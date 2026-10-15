"""A stdio MCP server for harnesses that only read a global MCP config (agy, muse): `python3 mcp_proxy.py NAME`.

art-crit installs one permanent `art-crit-NAME` entry pointing here (ADR-0025). The harness starts MCP servers in the
agent's working dir, which in an art-crit run is <run>/work/; the run's servers are in <run>/harness/art-crit-mcp.json
({NAME: {"command", "args", "env", "hidden"}}), next to it and outside what the agent works in. The proxy runs NAME's
server, relaying stdin/stdout line by line and dropping the `hidden` tools from tools/list results. (Not an env var:
muse starts stdio servers with only a fixed allowlist of the environment.) Anywhere else (the user's own sessions)
there is no such file and the proxy is an MCP server with no tools, so nothing changes there.
Standard library only: it runs with whatever python3 the harness finds on PATH."""

import json
import os
import subprocess
import sys
import threading
from pathlib import Path

EMPTY_RESULTS = {"tools/list": {"tools": []}, "resources/list": {"resources": []}, "prompts/list": {"prompts": []}}


SPEC_FILE = "art-crit-mcp.json"


def run_spec(name, cwd=None):
    """NAME's server in the art-crit run whose work dir is `cwd` (<run>/harness/art-crit-mcp.json), or None outside one."""
    path = Path(cwd or os.getcwd()).parent / "harness" / SPEC_FILE
    try:
        return json.loads(path.read_text()).get(name)
    except (OSError, ValueError, AttributeError):
        return None


def serve_empty(stdin=sys.stdin, stdout=sys.stdout):
    """An MCP server with no tools, resources or prompts."""
    for line in stdin:
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        if not isinstance(msg, dict) or "id" not in msg or "method" not in msg:
            continue  # notifications and responses need no reply
        method = msg["method"]
        if method == "initialize":
            version = (msg.get("params") or {}).get("protocolVersion", "2025-06-18")
            result = {"protocolVersion": version, "capabilities": {"tools": {}}, "serverInfo": {"name": "art-crit-idle", "version": "1"}}
        else:
            result = EMPTY_RESULTS.get(method, {})
        stdout.write(json.dumps({"jsonrpc": "2.0", "id": msg["id"], "result": result}) + "\n")
        stdout.flush()


def without_hidden(line, list_ids, hidden):
    """A server->client line with the hidden tools removed when it answers a tools/list request."""
    try:
        msg = json.loads(line)
    except ValueError:
        return line
    tools = (msg.get("result") or {}).get("tools") if isinstance(msg, dict) and msg.get("id") in list_ids else None
    if not isinstance(tools, list):
        return line
    list_ids.discard(msg["id"])
    msg["result"]["tools"] = [t for t in tools if t.get("name") not in hidden]
    return json.dumps(msg) + "\n"


def relay(spec, stdin=sys.stdin, stdout=sys.stdout):
    """Run spec's server and relay both ways, dropping its hidden tools. Returns the server's exit code."""
    hidden = set(spec.get("hidden") or ())
    proc = subprocess.Popen([spec["command"], *spec.get("args", [])], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            env={**os.environ, **spec.get("env", {})}, text=True, bufsize=1)
    list_ids = set()

    def to_server():
        for line in stdin:
            try:
                msg = json.loads(line)
                if isinstance(msg, dict) and msg.get("method") == "tools/list" and "id" in msg:
                    list_ids.add(msg["id"])
            except ValueError:
                pass
            proc.stdin.write(line)
            proc.stdin.flush()
        proc.stdin.close()

    threading.Thread(target=to_server, daemon=True).start()
    for line in proc.stdout:
        stdout.write(without_hidden(line, list_ids, hidden))
        stdout.flush()
    return proc.wait()


def main(argv=sys.argv[1:]):
    spec = run_spec(argv[0]) if argv else None
    if not spec:
        serve_empty()
        return 0
    return relay(spec)


if __name__ == "__main__":
    sys.exit(main())
