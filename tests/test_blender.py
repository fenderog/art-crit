"""The blender kind: the .glb check, the per-run Blender session, the MCP servers each harness gets, and a full
`art-crit run --kind blender` with the fake pi (tests/fixtures/fake_pi/pi) and a fake `blender` that only listens on
its port. Nothing here starts the real Blender or downloads the MCP server."""

import json
import os
import struct
from pathlib import Path

import pytest

from art_crit.cli import main
from art_crit.harness import ClaudeCode, Codex, Pi
from art_crit.kinds import KINDS
from art_crit.kinds.blender import HIDDEN_TOOLS, MCP_SOURCE, Blender, read_glb, triangles
from art_crit.util import CritError

FAKE_PI = Path(__file__).parent / "fixtures" / "fake_pi"
PNG_1X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c63f8cfc0f00f0004850180848c3221"
    "0000000049454e44ae426082"
)


def glb(gltf=None, positions=struct.pack("<9f", 0, 0, 0, 1, 0, 0, 0, 1, 0)):
    """A glTF binary: one triangle by default, or the given glTF JSON."""
    gltf = gltf or {
        "asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}],
        "accessors": [{"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3", "min": [0, 0, 0], "max": [1, 1, 0]}],
        "bufferViews": [{"buffer": 0, "byteLength": len(positions)}], "buffers": [{"byteLength": len(positions)}],
    }
    js = json.dumps(gltf).encode()
    js += b" " * (-len(js) % 4)
    body = struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(positions), 0x004E4942) + positions
    return struct.pack("<III", 0x46546C67, 2, 12 + len(body)) + body


@pytest.fixture(autouse=True)
def fakes_on_path(monkeypatch):
    monkeypatch.setenv("PATH", f"{FAKE_PI}{os.pathsep}{os.environ['PATH']}")
    for var in ("FAKE_PI_BLENDER_LIVE", "FAKE_BLENDER_FAIL", "FAKE_BLENDER_PID", "FAKE_PI_ARGV"):
        monkeypatch.delenv(var, raising=False)


# --- the .glb check ------------------------------------------------------------------------------


def test_read_glb_and_triangles():
    path = Path(__file__).parent / "x.glb"
    try:
        path.write_bytes(glb())
        gltf = read_glb(path)
    finally:
        path.unlink()
    assert gltf["asset"]["version"] == "2.0" and triangles(gltf) == 1


@pytest.mark.parametrize("data, error", [
    (b"not a model at all, just text", "not a glTF binary"),
    (glb()[:-4], "truncated"),
    (glb({"asset": {"version": "1.0"}}), "not glTF 2.0"),
    (glb({"asset": {"version": "2.0"}}), "without a scene"),
])
def test_bad_glb_is_an_error(tmp_path, data, error):
    (tmp_path / "output").mkdir()
    (tmp_path / "output" / "scene.glb").write_bytes(data)
    ok, err = Blender(home=tmp_path / "home").finalize(tmp_path, tmp_path / "out")
    assert not ok and error in err


def test_glb_needing_a_decoder_the_viewer_lacks_is_an_error(tmp_path):
    (tmp_path / "output").mkdir()
    (tmp_path / "output" / "scene.glb").write_bytes(glb({"asset": {"version": "2.0"}, "scenes": [{}], "extensionsRequired": ["KHR_draco_mesh_compression"]}))
    ok, err = Blender(home=tmp_path / "home").finalize(tmp_path, tmp_path / "out")
    assert not ok and "KHR_draco_mesh_compression" in err


def test_oversized_glb_is_an_error(tmp_path, monkeypatch):
    monkeypatch.setattr("art_crit.kinds.blender.MAX_MODEL_BYTES", 100)
    (tmp_path / "output").mkdir()
    (tmp_path / "output" / "scene.glb").write_bytes(glb() + b"\0" * 200)
    ok, err = Blender(home=tmp_path / "home").finalize(tmp_path, tmp_path / "out")
    assert not ok and "larger than" in err


def test_finalize_keeps_model_and_render(tmp_path):
    out = tmp_path / "output"
    out.mkdir()
    (out / "scene.glb").write_bytes(glb())
    (out / "render.png").write_bytes(PNG_1X1)
    (out / "notes.txt").write_text("not output")  # ignored, like the media kind
    kind = Blender(home=tmp_path / "home")
    assert kind.finalize(tmp_path, tmp_path / "out") == (True, None)
    assert kind.verify(tmp_path / "out") == {"ok": True}
    items = {i["file"]: i for i in json.loads((tmp_path / "out" / "manifest.json").read_text())["items"]}
    assert items["scene.glb"] == {"type": "model", "file": "scene.glb", "bytes": len(glb()), "meshes": 1, "triangles": 1, "animations": 0}
    assert items["render.png"]["type"] == "image"
    assert not kind.keep_source(Path("output/scene.glb"), out / "scene.glb")


def test_no_output_names_what_was_expected(tmp_path):
    (tmp_path / "output").mkdir()
    (tmp_path / "output" / "notes.txt").write_text("hi")
    assert Blender(home=tmp_path / "home").finalize(tmp_path, tmp_path / "out") == (False, "no render or .glb files in ./output/")


# --- the run's Blender ---------------------------------------------------------------------------


def test_agent_session_starts_blender_on_its_own_port_and_kills_it(tmp_path, monkeypatch):
    pids = tmp_path / "pids"
    monkeypatch.setenv("FAKE_BLENDER_PID", str(pids))
    (tmp_path / "work").mkdir()
    (tmp_path / "harness").mkdir()
    with Blender(home=tmp_path / "home").agent_session(tmp_path / "work", tmp_path / "harness") as mcp:
        spec = mcp["blender"]
        assert spec["command"] == "uvx" and spec["args"] == ["--from", MCP_SOURCE, "blender-mcp"]
        assert spec["hidden"] == list(HIDDEN_TOOLS)
        port = int(spec["env"]["BLENDER_MCP_PORT"])
        from art_crit.kinds.blender import port_open
        assert port_open(port)
    assert not port_open(port)
    pid = int(pids.read_text().split()[0])
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)
    assert "MCP server started" in (tmp_path / "harness" / "blender.log").read_text()


def test_agent_session_that_cannot_start_blender_raises(tmp_path, monkeypatch):
    monkeypatch.setenv("FAKE_BLENDER_FAIL", "1")
    (tmp_path / "harness").mkdir()
    with pytest.raises(CritError, match="Blender didn't start"):
        with Blender(home=tmp_path / "home").agent_session(tmp_path, tmp_path / "harness"):
            pass


# --- MCP servers per harness ---------------------------------------------------------------------

MCP = {"blender": {"command": "uvx", "args": ["--from", "src", "blender-mcp"], "env": {"BLENDER_MCP_PORT": "4242"},
                   "hidden": ["jump_to_tab_by_name"]}}


def test_pi_gets_a_project_mcp_config_in_work(tmp_path):
    (tmp_path / "harness").mkdir()
    cmd = Pi().command("openai-codex/gpt-6-sol", "low", "brief", tmp_path / "harness", mcp=MCP)
    assert cmd[-6:] == ["-e", "builtin:mcp", "--approve", "--exclude-tools", "mcp__blender__jump_to_tab_by_name", "brief"]
    config = json.loads((tmp_path / "work" / ".pi" / "mcp.json").read_text())["mcpServers"]["blender"]
    assert config["exposure"] == "direct" and config["env"] == {"BLENDER_MCP_PORT": "4242"} and "hidden" not in config


def test_claude_code_swaps_safe_mode_for_strict_mcp(tmp_path):
    plain = ClaudeCode().command("opus", "low", "brief", tmp_path)
    assert "--safe-mode" in plain and not any(a.startswith("--mcp-config") for a in plain)
    cmd = ClaudeCode().command("opus", "low", "brief", tmp_path, mcp=MCP)
    assert "--safe-mode" not in cmd and "--setting-sources=" in cmd and "--strict-mcp-config" in cmd
    assert f"--mcp-config={tmp_path / 'mcp.json'}" in cmd
    assert "--disallowed-tools=Agent,Task,mcp__blender__jump_to_tab_by_name" in cmd
    assert cmd[-2:] == ["--", "brief"]
    assert json.loads((tmp_path / "mcp.json").read_text())["mcpServers"]["blender"]["command"] == "uvx"
    assert ClaudeCode().env()["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] == "1"


def test_codex_gets_mcp_overrides(tmp_path):
    cmd = Codex().command("gpt-6-sol", "low", "brief", tmp_path, mcp=MCP)
    assert 'mcp_servers.blender.args=["--from", "src", "blender-mcp"]' in cmd
    assert 'mcp_servers.blender.env={BLENDER_MCP_PORT = "4242"}' in cmd
    assert 'mcp_servers.blender.disabled_tools=["jump_to_tab_by_name"]' in cmd
    assert cmd[-1] == "brief"


def test_blender_pages_refuse_harnesses_without_mcp(run_root, capsys):
    rc = main(["run", "--yes", "--dry-run", "--kind", "blender", "a fox", "-m", "agy:gemini-3.8-flash:low", "--root", str(run_root)])
    assert rc != 0 and "agy can't take here (use pi, claude-code, codex)" in capsys.readouterr().err


# --- a whole run ---------------------------------------------------------------------------------


@pytest.fixture
def run_root(bench_root, tmp_path, git_repo, monkeypatch):
    monkeypatch.setattr(Blender, "prepare", lambda self: None)  # no add-on download, no uvx
    monkeypatch.setattr(Blender, "tools", ("blender",))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    runs_dir = tmp_path / "art-crit-runs"
    (bench_root / "art-crit.toml").write_text(f'[run]\ndir = "{runs_dir}"\nparallel = 8\ntimeout = "30m"\n')
    git_repo(bench_root)
    return bench_root


def test_blender_run_publishes_model_and_render(run_root, tmp_path, monkeypatch):
    argv_file = tmp_path / "argv.json"
    monkeypatch.setenv("FAKE_PI_ARGV", str(argv_file))
    rc = main(["run", "--yes", "--kind", "blender", "a triangle", "-m", "openai-codex/gpt-6-sol:low", "--root", str(run_root)])
    assert rc == 0
    page = json.loads((run_root / "docs/data/a-triangle/page.json").read_text())
    assert page["kind"] == "blender" and "execute_blender_code" in page["final_prompt"]
    [run] = page["runs"]
    assert (run["output"]["ok"], run["output"]["verified"], run["output"]["error"]) == (True, True, None)
    by_path = {i["path"]: i for i in run["output"]["items"]}
    assert by_path["media/scene.glb"]["type"] == "model" and by_path["media/scene.glb"]["triangles"] == 1
    assert run["thumb"] == "media/render.png"
    run_dir = run_root / "docs/data/a-triangle/runs" / run["id"]
    assert (run_dir / "media/scene.glb").read_bytes()[:4] == b"glTF"
    # pi got the run's Blender as a project MCP server; that config is never published as source
    argv = json.loads(argv_file.read_text())["argv"]
    assert "--approve" in argv and "builtin:mcp" in argv
    seen = json.loads((run_dir / "source" / "mcp-seen.json").read_text())["mcpServers"]["blender"]
    assert seen["args"][-1] == "blender-mcp" and seen["env"]["BLENDER_MCP_PORT"].isdigit()
    assert not (run_dir / "source" / ".pi").exists()


def test_blender_that_cannot_start_fails_the_run_not_the_batch(run_root, monkeypatch):
    monkeypatch.setenv("FAKE_BLENDER_FAIL", "1")
    main(["run", "--yes", "--no-publish", "--kind", "blender", "a cone", "-m", "openai-codex/gpt-6-sol:low", "--root", str(run_root)])
    [run] = json.loads((run_root / "docs/data/a-cone/page.json").read_text())["runs"]
    assert run["state"] == "failed" and "Blender didn't start" in run["error"]


def test_blender_kind_is_registered():
    assert KINDS["blender"].needs_mcp and KINDS["blender"].name == "blender"
