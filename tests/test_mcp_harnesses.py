"""MCP servers for agy, muse and grok-build: the stdio proxy that agy's and muse's permanent global entries point at,
the installer of those entries (a temp copy of the global configs, see conftest), the per-run Grok config, and the
MCP calls in their converted transcripts. No real harness or model runs here."""

import io
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from art_crit import mcp_proxy
from art_crit.harness import (Agy, GrokBuild, MuseCode, _muse_tool_call, convert_agy_stream, install_proxy_entries,
                              proxy_path)
from art_crit.util import CritError

SPEC = {"blender": {"command": "uvx", "args": ["--from", "src", "blender-mcp"], "env": {"BLENDER_MCP_PORT": "4242"},
                    "hidden": ["jump_to_tab_by_name"], "tools": ["execute_blender_code", "search_api_docs"]}}


def rpc_lines(*methods):
    return "".join(json.dumps({"jsonrpc": "2.0", "id": i, "method": m, "params": {}}) + "\n" for i, m in enumerate(methods, 1))


# --- the proxy -----------------------------------------------------------------------------------


def test_proxy_outside_a_run_is_an_empty_server():
    out = io.StringIO()
    mcp_proxy.serve_empty(io.StringIO(rpc_lines("initialize", "tools/list") + '{"jsonrpc": "2.0", "method": "notifications/initialized"}\n'), out)
    replies = [json.loads(line) for line in out.getvalue().splitlines()]
    assert [r["id"] for r in replies] == [1, 2]  # the notification gets no reply
    assert replies[0]["result"]["serverInfo"]["name"] == "art-crit-idle" and replies[1]["result"] == {"tools": []}


def test_proxy_finds_the_run_spec_beside_the_work_dir(tmp_path):
    (tmp_path / "harness").mkdir()
    (tmp_path / "work").mkdir()
    assert mcp_proxy.run_spec("blender", tmp_path / "work") is None
    (tmp_path / "harness" / mcp_proxy.SPEC_FILE).write_text(json.dumps(SPEC))
    assert mcp_proxy.run_spec("blender", tmp_path / "work") == SPEC["blender"]
    assert mcp_proxy.run_spec("other", tmp_path / "work") is None


def test_proxy_relays_and_drops_hidden_tools(tmp_path):
    server = tmp_path / "server.py"
    server.write_text(textwrap.dedent('''
        import json, sys
        for line in sys.stdin:
            msg = json.loads(line)
            tools = [{"name": "keep"}, {"name": "drop"}] if msg["method"] == "tools/list" else None
            result = {"tools": tools} if tools else {"echo": msg["method"]}
            print(json.dumps({"jsonrpc": "2.0", "id": msg["id"], "result": result}), flush=True)
    '''))
    out = io.StringIO()
    code = mcp_proxy.relay({"command": sys.executable, "args": [str(server)], "hidden": ["drop"]},
                           io.StringIO(rpc_lines("initialize", "tools/list")), out)
    replies = [json.loads(line) for line in out.getvalue().splitlines()]
    assert code == 0 and replies[0]["result"] == {"echo": "initialize"}
    assert replies[1]["result"]["tools"] == [{"name": "keep"}]


def test_installed_proxy_runs_on_its_own(tmp_path):
    """The global entries run the copied proxy with a bare python3: it must not import art_crit."""
    (tmp_path / "work").mkdir()
    install_proxy_entries(tmp_path / "config.json", SPEC, tmp_path)
    r = subprocess.run([sys.executable, "-I", str(proxy_path()), "blender"], input=rpc_lines("initialize", "tools/list"),
                       capture_output=True, text=True, cwd=tmp_path / "work", timeout=30)  # no harness/ here: idle server
    assert r.returncode == 0 and json.loads(r.stdout.splitlines()[1])["result"] == {"tools": []}


# --- the global entries --------------------------------------------------------------------------


def test_install_keeps_other_entries_and_writes_the_run_spec(tmp_path):
    config = tmp_path / "settings.json"
    config.write_text(json.dumps({"schema_version": 1, "model": "x", "mcpServers": {"mine": {"command": "a"}}}))
    install_proxy_entries(config, SPEC, tmp_path, lambda spec: {"mode": "optional"})
    data = json.loads(config.read_text())
    assert data["model"] == "x" and data["mcpServers"]["mine"] == {"command": "a"}
    assert data["mcpServers"]["art-crit-blender"] == {"command": "python3", "args": [str(proxy_path()), "blender"], "mode": "optional"}
    assert json.loads((tmp_path / "art-crit-mcp.json").read_text()) == SPEC
    assert proxy_path().read_text() == Path(mcp_proxy.__file__).read_text()
    before = config.stat().st_mtime_ns
    install_proxy_entries(config, SPEC, tmp_path, lambda spec: {"mode": "optional"})
    assert config.stat().st_mtime_ns == before  # unchanged: not rewritten


def test_install_accepts_an_empty_config_and_refuses_unreadable_ones(tmp_path):
    config = tmp_path / "mcp_config.json"
    config.write_text("")
    install_proxy_entries(config, SPEC, tmp_path)
    assert "art-crit-blender" in json.loads(config.read_text())["mcpServers"]
    config.write_text("// a comment\n{}")
    with pytest.raises(CritError, match="isn't plain JSON"):
        install_proxy_entries(config, SPEC, tmp_path)
    config.write_text(json.dumps({"mcp_servers": {}}))
    with pytest.raises(CritError, match="legacy mcp_servers"):
        install_proxy_entries(config, SPEC, tmp_path)


def test_agy_declares_the_visible_tools_eagerly(tmp_path):
    cmd = Agy().command("gemini-3.8-flash", "low", "brief", tmp_path, mcp=SPEC)
    assert cmd[0] == "agy"  # no env prefix: the proxy reads the run's spec file
    entry = json.loads(Agy.MCP_CONFIG.read_text())["mcpServers"]["art-crit-blender"]
    assert entry["timeoutSeconds"] == 600
    assert entry["tools"] == {"execute_blender_code": {"eager": True}, "search_api_docs": {"eager": True}}
    assert (tmp_path / "art-crit-mcp.json").is_file()


def test_muse_gets_a_settings_entry_and_no_trust(tmp_path):
    cmd = MuseCode().command("muse-spark-1.3", "low", "brief", tmp_path, mcp=SPEC)
    assert "--trust-workspace" not in cmd and "--yolo" not in cmd  # both would turn on sub-agents
    entry = json.loads(MuseCode.MCP_CONFIG.read_text())["mcpServers"]["art-crit-blender"]
    assert entry == {"command": "python3", "args": [str(proxy_path()), "blender"], "type": "stdio", "mode": "optional"}


def test_grok_gets_a_project_config_in_work_through_the_proxy(tmp_path):
    (tmp_path / "harness").mkdir()
    cmd = GrokBuild().command("grok-4.7", "low", "brief", tmp_path / "harness", mcp=SPEC)
    assert cmd[:2] == ["env", "GROK_FOLDER_TRUST=0"]  # project servers start only in a trusted folder; no --trust record
    import tomllib
    server = tomllib.loads((tmp_path / "work" / ".grok" / "config.toml").read_text())["mcp_servers"]["blender"]
    assert server == {"command": "python3", "args": [str(proxy_path()), "blender"], "tool_timeout_sec": 600,
                      "startup_timeout_sec": 60, "enabled": True}
    assert json.loads((tmp_path / "harness" / "art-crit-mcp.json").read_text()) == SPEC  # hidden tools: the proxy drops them


def test_harnesses_without_servers_write_nothing(tmp_path):
    for h in (Agy(), MuseCode(), GrokBuild()):
        h.command("m", "low", "brief", tmp_path / "harness")
    assert not Agy.MCP_CONFIG.exists() and not MuseCode.MCP_CONFIG.exists() and not (tmp_path / "work").exists()


# --- MCP calls in transcripts --------------------------------------------------------------------


def test_muse_mcp_call_gets_the_shared_name():
    call = _muse_tool_call({"call_id": "c1", "name": "mcp__art_crit_blender__execute_blender_code", "args": '{"code": "x"}'}, "/w")
    assert call == {"type": "toolCall", "id": "c1", "name": "mcp__blender__execute_blender_code", "arguments": {"code": "x"}}


def test_agy_mcp_call_gets_the_shared_name():
    events = [{"event": "init", "cwd": "/w", "model": "m"},
              {"event": "step_update", "step_update": {"step_type": "tool", "state": "DONE", "step_index": 3, "tool_info": {
                  "name": "call_mcp_tool", "parameters": {"ServerName": "art-crit-blender", "ToolName": "execute_blender_code",
                                                          "Arguments": {"code": "x"}}, "output": "ok"}}}]
    calls = [c for e in convert_agy_stream(events, "brief", "low") for c in (e.get("message") or {}).get("content", [])
             if isinstance(c, dict) and c.get("type") == "toolCall"]
    assert [(c["name"], c["arguments"]) for c in calls] == [("mcp__blender__execute_blender_code", {"code": "x"})]


def test_agy_eager_mcp_tool_gets_the_shared_name():
    """With `eager`, agy declares the tool itself as mcp_<entry>_<tool> instead of going through call_mcp_tool."""
    events = [{"event": "init", "cwd": "/w", "model": "m"},
              {"event": "step_update", "step_update": {"step_type": "tool", "state": "DONE", "step_index": 4, "tool_info": {
                  "name": "mcp_art-crit-blender_render_viewport_to_path", "parameters": {"filepath": "/w/a.png"}, "output": "ok"}}}]
    calls = [c for e in convert_agy_stream(events, "brief", "low") for c in (e.get("message") or {}).get("content", [])
             if isinstance(c, dict) and c.get("type") == "toolCall"]
    assert [(c["name"], c["arguments"]) for c in calls] == [("mcp__blender__render_viewport_to_path", {"filepath": "/w/a.png"})]
