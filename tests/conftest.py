"""Synthetic batch fixture: a batch directory of run directories (two effort levels), each with the
shape `art-crit run` writes (run.json, work/, harness/, output/): tiny fake Godot engine files, a real
Godot index.html template, and small session files with the sensitive shapes the cleaning rules must
strip. Built at runtime (not committed) so nothing under a real home dir, or any real session content,
ends up in this public repo.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
GODOT_INDEX_HTML = (FIXTURES / "godot_index.html").read_text()

DEFAULT_LEVELS = ["low", "high"]


@pytest.fixture(autouse=True)
def no_muse_catalog(monkeypatch, tmp_path_factory):
    """Muse Code reads its model list from the user's cache; tests get the built-in table instead."""
    from art_crit.harness import MuseCode
    monkeypatch.setattr(MuseCode, "CATALOG_DIR", tmp_path_factory.getbasetemp() / "no-muse-catalog")


@pytest.fixture(autouse=True)
def no_global_mcp_config(monkeypatch, tmp_path):
    """agy and muse get MCP servers through entries in the user's global config: tests write a temp copy, never the
    real ~/.gemini or ~/.config/muse, and the proxy goes to a temp cache."""
    from art_crit.harness import Agy, MuseCode
    monkeypatch.setattr(Agy, "MCP_CONFIG", tmp_path / "global" / "agy-mcp_config.json")
    monkeypatch.setattr(MuseCode, "MCP_CONFIG", tmp_path / "global" / "muse-settings.json")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

ENGINE_BYTES = {
    "index.wasm": b"FAKE-WASM-BYTES-0001",
    "index.js": b"FAKE-JS-BYTES-0001",
    "index.audio.worklet.js": b"FAKE-AUDIO-WORKLET-0001",
    "index.audio.position.worklet.js": b"FAKE-AUDIO-POSITION-WORKLET-0001",
}


def _write_conversation(path, home, level, secret=None):
    thinking_sig = json.dumps({"id": "rs_1", "type": "reasoning", "encrypted_content": "gAAAAA-secret-blob-not-real"})
    text = f"Working in {home}/effort-runs/x now."
    if secret:
        text += f" token={secret}"
    convo = [
        {"type": "session", "id": "s1", "timestamp": "2026-09-26T07:12:42.000Z", "cwd": f"{home}/effort-runs/x"},
        {
            "type": "message",
            "id": "u1",
            "message": {
                "role": "user",
                "content": [{"type": "text", "text": f"Task: draw a running horse in {home}/effort-runs/x."}],
            },
        },
        {
            "type": "message",
            "id": "m1",
            "parentId": "s1",
            "pid": 4242,
            "sessionId": "sess-xyz",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "thinking": "plan", "thinkingSignature": thinking_sig},
                    {"type": "text", "text": text},
                ],
            },
        },
    ]
    path.write_text(json.dumps(convo, indent=2))


def make_batch(base, slug="voxel-horse", started=datetime(2026, 9, 26, 0, 11, 58), levels=None, threads=False, secret=None, refs=None):
    """A synthetic batch directory under `base`: prompt.md and one run directory per level. `refs` maps
    reference file names to bytes, copied into the batch's references/ (what --ref leaves behind)."""
    from art_crit.util import make_run_id

    levels = levels if levels is not None else DEFAULT_LEVELS
    home = str(Path.home())
    root = base / f"{started:%Y-%m-%d-%H%M%S}-{slug}"
    root.mkdir(parents=True)
    (root / "prompt.md").write_text("draw a running horse")
    for name, content in (refs or {}).items():
        refs_dir = root / "references"
        refs_dir.mkdir(exist_ok=True)
        (refs_dir / name).write_bytes(content)

    for i, level in enumerate(levels):
        model = "openai-codex/gpt-6-sol"
        run_id = make_run_id(model, level, started)
        run_dir = root / run_id
        work, harness_dir, output = run_dir / "work", run_dir / "harness", run_dir / "output"
        (work / "scenes").mkdir(parents=True)
        (work / "scripts").mkdir(parents=True)
        (work / "project.godot").write_text("config_version=5\n")
        (work / "README.md").write_text(f"# {level} run\nbuilt from {home}\n")
        (work / "export_presets.cfg").write_text("[preset.0]\nname=\"Web\"\n")
        (work / "scenes" / "main.tscn").write_text('[gd_scene load_steps=1 format=3]\n')
        (work / "scripts" / "main.gd").write_text("extends Node\nfunc _ready():\n\tpass\n")
        (work / "scripts" / "main.gd.uid").write_text("uid://abc123\n")
        (work / ".DS_Store").write_bytes(b"\x00\x00")
        cache_dir = work / ".godot" / "cache"
        cache_dir.mkdir(parents=True)
        (cache_dir / "whatever.tmp").write_text("editor cache junk, never copied")

        harness_dir.mkdir()
        _write_conversation(harness_dir / "conversation.json", home, level, secret=secret if level == levels[0] else None)
        (harness_dir / "events.jsonl").write_text('{"type": "agent_start"}\n')  # the raw stdout: never published
        (harness_dir / "brief.md").write_text("the brief")

        output.mkdir()
        for name, content in ENGINE_BYTES.items():
            (output / name).write_bytes(content)
        (output / "index.pck").write_bytes(b"PCK-DATA")
        (output / "index.png").write_bytes(b"PNG-DATA")
        (output / "index.icon.png").write_bytes(b"ICON-DATA")
        (output / "index.apple-touch-icon.png").write_bytes(b"TOUCH-DATA")
        html = GODOT_INDEX_HTML.replace(
            "const GODOT_THREADS_ENABLED = false;",
            f"const GODOT_THREADS_ENABLED = {'true' if threads else 'false'};",
        )
        (output / "index.html").write_text(html)
        (output / "export-manifest.json").write_text(
            json.dumps({"threads": threads, "godot": "4.7.2.stable.official.ed1daf0bf"})
        )
        verify_dir = output / "verification"
        verify_dir.mkdir()
        (verify_dir / "frame-1.png").write_bytes(b"FRAME-1-DATA")
        (verify_dir / "verify-report.json").write_text(json.dumps({"ok": True}))

        begun = started.replace(second=started.second + i)
        (run_dir / "run.json").write_text(json.dumps({
            "id": run_id,
            "page": slug,
            "model": model,
            "effort": level,
            "kind": "godot",
            "started_at": begun.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "batch": root.name,
            "harness": {"name": "pi", "version": "0.0.0-test"},
            "state": "complete",
            "error": None,
            "route": None,
            "metrics": {
                "duration_ms": 1000 + i * 500,
                "cost_usd": 0.01 * (i + 1),
                "tool_calls": 2 + i,
                "turns": 2 + i,
                "tokens_total": 140 * (i + 1),
                "tokens_input": 100 * (i + 1),
                "tokens_output": 40 * (i + 1),
                "tokens_reasoning": 5 * (i + 1),
                "tokens_cache_read": 10 * (i + 1),
            },
            "output": {"kind": "godot", "ok": True, "error": None, "verified": True},
        }, indent=2))
    return root


@pytest.fixture
def batch_factory(tmp_path):
    def factory(**kwargs):
        return make_batch(tmp_path, **kwargs)

    return factory


@pytest.fixture
def batch_dir(batch_factory):
    return batch_factory()


@pytest.fixture
def bench_root(tmp_path):
    root = tmp_path / "site"
    (root / "docs").mkdir(parents=True)
    (root / "docs" / ".nojekyll").touch()
    return root


@pytest.fixture
def git_repo(tmp_path):
    """Make `root` a git repo with an empty bare origin, so publish's add/commit/push succeed here:
    `art-crit run` publishes by default, and every full-run test goes through it. Idempotent, so a test can
    call it again to get the origin path."""

    def make(root):
        def run(*args, check=True):
            return subprocess.run(args, check=check, capture_output=True)

        origin = tmp_path / "origin.git"
        if not origin.exists():
            run("git", "init", "--bare", "-q", "-b", "main", str(origin))
        if subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "HEAD"], capture_output=True).returncode == 0:
            return origin  # already set up (run_root did it); don't add a second commit
        run("git", "-C", str(root), "init", "-q", "-b", "main")
        for key, value in (("user.email", "bench@test"), ("user.name", "bench"), ("commit.gpgsign", "false")):
            run("git", "-C", str(root), "config", key, value)
        remotes = subprocess.run(["git", "-C", str(root), "remote"], capture_output=True, text=True).stdout.split()
        if "origin" not in remotes:
            run("git", "-C", str(root), "remote", "add", "origin", str(origin))
        run("git", "-C", str(root), "add", "-A")
        run("git", "-C", str(root), "commit", "-q", "-m", "init")
        run("git", "-C", str(root), "push", "-q", "-u", "origin", "main")
        return origin

    return make
