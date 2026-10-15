"""art-crit serve: CORS, .wasm/.pck content types, and no COOP/COEP headers."""

import urllib.request

from art_crit.serve import serve_in_thread


def _get(url):
    with urllib.request.urlopen(url) as resp:
        return resp.status, resp.headers, resp.read()  # headers: case-insensitive email.message.Message


def test_serve_headers(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.html").write_text("<html></html>")
    (docs / "game.wasm").write_bytes(b"\x00wasm")
    (docs / "game.pck").write_bytes(b"pck-bytes")

    server = serve_in_thread(docs, 0)
    try:
        assert server.request_queue_size >= 32  # browser imports many ES modules at once
        port = server.server_address[1]
        base = f"http://127.0.0.1:{port}/"

        status, headers, body = _get(base + "game.wasm")
        assert status == 200
        assert headers["Content-Type"] == "application/wasm"
        assert headers["Access-Control-Allow-Origin"] == "*"
        assert "Cross-Origin-Opener-Policy" not in headers
        assert "Cross-Origin-Embedder-Policy" not in headers
        assert body == b"\x00wasm"

        status, headers, _ = _get(base + "game.pck")
        assert status == 200
        assert headers["Content-Type"] == "application/octet-stream"

        status, headers, _ = _get(base + "index.html")
        assert status == 200
        assert headers["Access-Control-Allow-Origin"] == "*"
    finally:
        server.shutdown()
        server.server_close()


# --- local ranking API ---------------------------------------------------------------------------

import json
import shutil
import urllib.error
from pathlib import Path

import pytest

from art_crit.cli import main

FIXTURE_DATA = Path(__file__).parent / "fixtures/site/data"
LOW, HIGH = "model-x-low-20260101-000000", "model-x-high-20260101-001000"


@pytest.fixture
def served(tmp_path):
    docs = tmp_path / "site" / "docs"
    shutil.copytree(FIXTURE_DATA, docs / "data")
    server = serve_in_thread(docs, 0)
    yield docs, f"http://127.0.0.1:{server.server_address[1]}/"
    server.shutdown()
    server.server_close()


def _post(url, body, headers=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def _get_with(url, headers):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as resp:
            return resp.status, resp.headers, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read()


def _put(url, body, headers=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="PUT",
                                 headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_api_local_says_ranking_is_available(served):
    _, base = served
    status, _, body = _get(base + "api/local")
    assert status == 200 and json.loads(body) == {"rank": True, "requests": True, "runs": True}


def test_saving_a_ranking_writes_it_and_rebuilds(served):
    docs, base = served
    status, body = _put(base + "api/rank?p=demo", {"ranks": {HIGH: 1, LOW: 2}})
    assert (status, body) == (200, {"ok": True})
    ranking = json.loads((docs / "data/demo/ranking.json").read_text())
    assert ranking["ranks"] == {HIGH: 1, LOW: 2}
    ranks = {r["id"]: r["rank"] for r in json.loads((docs / "data/demo/page.json").read_text())["runs"]}
    assert ranks == {HIGH: 1, LOW: 2, "model-x-medium-20260101-000500": None}

    _put(base + "api/rank?p=demo", {"ranks": {HIGH: 1, LOW: None}})  # null = unranked
    assert json.loads((docs / "data/demo/ranking.json").read_text())["ranks"] == {HIGH: 1}


@pytest.mark.parametrize("query, ranks, error", [
    ("p=../../etc", {}, "bad page slug"),
    ("p=nope", {}, "no such page"),
    ("p=demo", {"not-a-run": 1}, "no such run"),
    ("p=demo", {HIGH: 0}, "whole number from 1 to 3"),
    ("p=demo", {HIGH: 4}, "whole number from 1 to 3"),
    ("p=demo", {HIGH: "1"}, "whole number"),
])
def test_bad_rankings_are_refused(served, query, ranks, error):
    docs, base = served
    status, body = _put(base + f"api/rank?{query}", {"ranks": ranks})
    assert status == 400 and error in body["error"]
    assert not (docs / "data/demo/ranking.json").exists()


def test_cross_site_writes_are_refused(served):
    docs, base = served
    status, _ = _put(base + "api/rank?p=demo", {"ranks": {HIGH: 1}}, {"Origin": "https://evil.example"})
    assert status == 403
    req = urllib.request.Request(base + "api/rank?p=demo", data=b'{"ranks":{}}', method="PUT", headers={"Content-Type": "text/plain"})
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(req)
    assert e.value.code == 415
    assert not (docs / "data/demo/ranking.json").exists()


def test_writes_need_a_loopback_host(served):
    """DNS rebinding: a site that points its own name at 127.0.0.1 sends matching Host and Origin headers."""
    docs, base = served
    port = base.rsplit(":", 1)[1].rstrip("/")
    evil = {"Host": f"evil.example:{port}", "Origin": f"http://evil.example:{port}"}
    status, body = _put(base + "api/rank?p=demo", {"ranks": {HIGH: 1}}, evil)
    assert status == 403 and "loopback" in body["error"]
    assert not (docs / "data/demo/ranking.json").exists()
    status, _ = _put(base + "api/rank?p=demo", {"ranks": {HIGH: 1}}, {"Host": f"localhost:{port}", "Origin": f"http://localhost:{port}"})
    assert status == 200


def test_rm_drops_the_removed_run_from_the_ranking(served):
    docs, base = served
    _put(base + "api/rank?p=demo", {"ranks": {HIGH: 1, LOW: 2}})
    assert main(["rm", "demo", LOW, "--root", str(docs.parent)]) == 0
    assert json.loads((docs / "data/demo/ranking.json").read_text())["ranks"] == {HIGH: 1}


# --- local prompt requests -----------------------------------------------------------------------

def test_prompt_requests_are_added_listed_and_removed_outside_docs(served):
    docs, base = served
    (docs.parent / "art-crit.toml").write_text('[sets]\ncheap = ["openai-codex/gpt-6-luna:low"]\n')
    status, _, body = _get(base + "api/requests")
    assert status == 200 and json.loads(body) == {"requests": [], "sets": ["cheap"]}

    status, body = _put(base + "api/requests", {"add": {"prompt": "  a voxel lighthouse  ", "kind": "godot", "title": "", "set": "cheap"}})
    assert status == 200 and len(body["requests"]) == 1
    req = body["requests"][0]
    assert req["prompt"] == "a voxel lighthouse" and req["kind"] == "godot" and req["set"] == "cheap" and "title" not in req
    saved = json.loads((docs.parent / "requests.json").read_text())  # next to docs/, never inside it
    assert saved == body["requests"] and not list(docs.rglob("requests.json"))

    status, body = _put(base + "api/requests", {"remove": req["id"]})
    assert status == 200 and body["requests"] == []


@pytest.mark.parametrize("body,error", [
    ({"add": {"prompt": "", "kind": "media"}}, "a prompt is required"),
    ({"add": {"prompt": "x", "kind": "movie"}}, "kind must be one of"),
    ({"add": {"prompt": "x" * 4001, "kind": "media"}}, "at most 4000"),
    ({"add": {"prompt": "x", "kind": "media", "set": "nope"}}, "no such model set"),
    ({"remove": "missing"}, "no such request"),
    ({"edit": 1}, "expected add or remove"),
])
def test_bad_prompt_requests_are_refused(served, body, error):
    docs, base = served
    status, resp = _put(base + "api/requests", body)
    assert status == 400 and error in resp["error"]
    assert not (docs.parent / "requests.json").exists()


def test_cross_site_prompt_requests_are_refused(served):
    docs, base = served
    status, _ = _put(base + "api/requests", {"add": {"prompt": "x", "kind": "media"}}, {"Origin": "https://evil.example"})
    assert status == 403 and not (docs.parent / "requests.json").exists()


# --- run monitor (ADR-0027) ----------------------------------------------------------------------

LIVE, DONE, PUBLISHED = "model-y-low-20260101-010000", "model-y-high-20260101-010000", "model-x-medium-20260101-000500"


def _session_line(**message):
    return json.dumps({"type": "message", "message": message})


def _pi_session():
    """A pi session file as it looks mid-run: one assistant message with usage, one tool result with an image."""
    return "\n".join([
        json.dumps({"type": "session", "id": "live"}),
        json.dumps({"type": "model_change", "provider": "openai-codex", "modelId": "gpt-6-sol"}),
        _session_line(role="user", content=[{"type": "text", "text": "the brief"}]),
        _session_line(role="assistant", stopReason="toolUse", content=[{"type": "text", "text": "looking"}, {"type": "toolCall", "id": "t1", "name": "read"}],
                      usage={"input": 500, "output": 100, "cacheRead": 200, "cacheWrite": 0, "reasoning": 10, "totalTokens": 600, "cost": {"total": 0.0015}}),
        _session_line(role="toolResult", toolCallId="t1", content=[{"type": "image", "data": "A" * 9000}, {"type": "text", "text": "B" * 9000}]),
    ]) + "\n"


def _batch(runs_dir):
    """A batch with a running run (live metrics from its session), a finished run and one the site has."""
    batch = runs_dir / "2026-01-01-010000-demo"
    (batch / LIVE / "harness").mkdir(parents=True)
    (batch / LIVE / "harness" / "2026-01-01T01-00-00-000Z_live.jsonl").write_text(_pi_session())
    done = batch / DONE / "harness"
    done.mkdir(parents=True)
    (done / "conversation.json").write_text(json.dumps([{"type": "message", "message": {"role": "user", "content": [{"type": "text", "text": "the brief"}]}}]) + "\n")
    (batch / DONE / "run.json").write_text(json.dumps({"state": "complete", "started_at": "2026-01-01T01:00:00Z", "error": None,
                                                       "output": {"kind": "godot", "ok": True, "verified": True},
                                                       "metrics": {"duration_ms": 12000, "cost_usd": 0.02, "turns": 2, "tokens_total": 700}}) + "\n")
    (batch / PUBLISHED).mkdir()
    (batch / PUBLISHED / "run.json").write_text(json.dumps({"state": "failed", "error": "boom"}) + "\n")
    (batch / "batch.json").write_text(json.dumps({
        "prompt": "a demo prompt", "kind": "godot", "page": "demo", "title": "Demo", "brief": "BRIEF TEXT",
        "created": "2026-01-01T01:00:00Z",
        "runs": [{"id": LIVE, "harness": "pi", "model": "openai/gpt-6-sol", "model_arg": "gpt-6-sol", "level": "low", "state": "running"},
                 {"id": DONE, "harness": "pi", "model": "openai/gpt-6-sol", "model_arg": "gpt-6-sol", "level": "high", "state": "complete"},
                 {"id": PUBLISHED, "harness": "codex", "model": "openai/gpt-6.1-sol", "model_arg": "gpt-6.1-sol", "level": "low", "state": "failed"}]}) + "\n")
    return batch


@pytest.fixture
def monitor(tmp_path):
    """A site whose art-crit.toml points [run].dir at a batch built for the monitor tests."""
    repo = tmp_path / "site"
    docs = repo / "docs"
    shutil.copytree(FIXTURE_DATA, docs / "data")
    runs_dir = repo / "art-crit-runs"
    (repo / "art-crit.toml").write_text(f'[run]\ndir = "{runs_dir}"\n')
    batch = _batch(runs_dir)
    server = serve_in_thread(docs, 0)
    yield docs, f"http://127.0.0.1:{server.server_address[1]}/", batch
    server.shutdown()
    server.server_close()


def test_api_runs_lists_batches_with_live_and_finished_runs(monitor):
    docs, base, batch = monitor
    status, headers, body = _get(base + "api/runs")
    assert status == 200 and "Access-Control-Allow-Origin" not in headers
    data = json.loads(body)
    assert data["dir"].endswith("art-crit-runs") and [b["batch"] for b in data["batches"]] == [batch.name]
    [entry] = data["batches"]
    assert (entry["page"], entry["kind"], entry["prompt"]) == ("demo", "godot", "a demo prompt")
    runs = {r["id"]: r for r in entry["runs"]}
    live = runs[LIVE]
    assert live["state"] == "running" and live["published"] is False
    assert live["metrics"]["turns"] == 1 and live["metrics"]["tokens_total"] == 600
    assert live["metrics"]["tool_calls"] == 1 and live["metrics"]["cost_usd"] == 0.0015
    assert live["metrics"]["duration_ms"] >= 0 and live["activity_ms"] is not None
    assert runs[PUBLISHED]["published"] is True
    assert runs[PUBLISHED]["error"] == "boom"


def test_api_run_serves_a_live_transcript(monitor):
    _, base, batch = monitor
    d = json.loads(_get(base + "api/run?b=" + batch.name + "&r=" + LIVE)[2])
    assert d["live"] and d["brief"] == "BRIEF TEXT" and not d["truncated"]
    t = json.dumps(d["transcript"])
    assert "looking" in t and "[image omitted here]" in t
    assert "A" * 4001 not in t and "B" * 4001 not in t and "more characters" in t


def test_api_run_reads_a_finished_run(monitor):
    _, base, batch = monitor
    (batch / DONE / "work").mkdir()
    (batch / DONE / "work" / "scene.tscn").write_text("x")
    d = json.loads(_get(base + "api/run?b=" + batch.name + "&r=" + DONE)[2])
    assert not d["live"] and d["transcript"][0]["message"]["role"] == "user"
    assert [f["name"] for f in d["files"]["work"]] == ["scene.tscn"]


def test_api_run_refuses_unknown_batches(monitor):
    _, base, batch = monitor
    st, _, body = _get_with(base + "api/run?b=..%2Fbad&r=x", {})
    assert st == 400 and "no such batch" in json.loads(body)["error"]
    st, _, body = _get_with(base + "api/run?b=" + batch.name + "&r=nope", {})
    assert st == 400 and "no such run" in json.loads(body)["error"]


def test_monitor_reads_are_refused_off_loopback(monitor):
    _, base, _ = monitor
    st, _, body = _get_with(base + "api/runs", {"Host": "evil.example"})
    assert st == 403 and "loopback" in json.loads(body)["error"]


def test_stopping_a_running_run_writes_the_stop_file(monitor):
    _, base, batch = monitor
    st, body = _post(base + "api/stop", {"batch": batch.name, "run": LIVE})
    assert (st, body) == (200, {"ok": True})
    marker = json.loads((batch / LIVE / "harness" / "stop").read_text())
    assert marker["by"] == "local monitor"


def test_stop_refuses_a_run_that_is_not_running(monitor):
    _, base, batch = monitor
    st, body = _post(base + "api/stop", {"batch": batch.name, "run": DONE})
    assert st == 400 and "isn't running" in body["error"]
    st, body = _post(base + "api/stop", {"batch": batch.name, "run": "nope"})
    assert st == 400 and "no such run" in body["error"]
    st, body = _post(base + "api/stop", {"batch": "a/../b", "run": LIVE})
    assert st == 400 and "no such batch" in body["error"]


def test_cross_site_stop_is_refused(monitor):
    _, base, batch = monitor
    st, _ = _post(base + "api/stop", {"batch": batch.name, "run": LIVE}, {"Origin": "https://e.x"})
    assert st == 403 and not (batch / LIVE / "harness" / "stop").exists()
