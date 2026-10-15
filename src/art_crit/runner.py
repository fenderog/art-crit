"""`art-crit run`: plan, launch, collect, finalize, verify and import a batch of agent runs.
See SPEC.md "Running benchmarks (art-crit run)". A fresh batch and a `--resume`d one both end in
`execute()`: for each run, either run its agent (if unfinished) or reuse its run.json, then the kind's
output step if it hasn't succeeded yet, then import — each run is imported and pushed as soon as its own
output step is done (the default; `--no-publish` imports the whole batch at the end instead), so the live
site fills up while the batch still runs.

A run's state (batch.json and run.json) says only what the agent did: queued | running | complete | failed
| timeout. What the kind made of its work is `output` in run.json: {kind, ok, error, verified}. The progress
table's other labels (exporting, verifying...) are transient and never written.

A running agent is stopped by writing `harness/stop` (the local monitor's Stop button, ADR-0027); this process
owns the child, so it is the one that kills the agent's process group."""

import contextlib
import difflib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from . import clean
from .config import RunRequest
from .harness import HARNESSES, add_tool_durations, split_harness
from .importer import cmd_import
from .kinds import KINDS
from .picker import pick_models
from .util import CritError, expand_levels, iso_from_ms, make_run_id, parse_duration, title_from_slug

# batch.json run states that mean "this agent hasn't produced a finished result yet".
UNFINISHED = ("queued", "running")

STOP_FILE = "stop"  # <run>/harness/stop: written by `art-crit serve`'s monitor to stop a running agent
STOP_POLL_S = 1.0  # how often a running agent is checked for a stop request (and for its timeout)


def tool_version(name):
    """First version-looking token of `name --version` (or `-version`, for ffmpeg), or None."""
    for flag in ("--version", "-version"):
        try:
            r = subprocess.run([name, flag], capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            return None
        m = re.search(r"v?(\d+(?:\.\d+)+)", r.stdout + r.stderr) if r.returncode == 0 else None
        if m:
            return m.group(1)
    return None


def describe_tools(entries):
    """art-crit.toml [run].tools entries ("python3 (standard library only)") -> the text listed in the
    brief, e.g. "python3 3.14.7 (standard library only), ffmpeg 9.0.2". Tools not on PATH are left
    out (with a note), so the brief never promises something the agent can't run."""
    listed = []
    for entry in entries:
        name, _, note = entry.partition(" ")
        if not shutil.which(name):
            print(f"note: tool {name!r} from [run].tools is not on PATH; leaving it out of the brief")
            continue
        version = tool_version(name)
        listed.append(" ".join(part for part in (name, version, note.strip()) if part))
    return ", ".join(listed) or "none beyond the shell"


def expand_sets(config, set_args):
    """--set NAME (from art-crit.toml [sets]) or --set FILE (one model[:levels] per line, # comments)
    -> the model specs, in order, exactly as if each had been given with -m."""
    sets = config.sets if set_args else {}
    specs = []
    for arg in set_args:
        if arg in sets:
            specs += sets[arg]
        elif Path(arg).is_file():
            lines = (line.split("#", 1)[0].strip() for line in Path(arg).read_text().splitlines())
            specs += [line for line in lines if line]
        else:
            known = ", ".join(sorted(sets)) or "none defined"
            raise CritError(f"unknown model set {arg!r}: not in art-crit.toml [sets] ({known}) and not a file")
    return specs


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40].rstrip("-") or "run"


def slug_from_prompt(prompt):
    return slugify(" ".join(prompt.strip().split()[:6]))


def page_slug(page, title, prompt):
    """--page/--slug wins, else the --title, else the prompt's first words."""
    return page or (slugify(title) if title and title.strip() else slug_from_prompt(prompt))


def parse_model_spec(spec, known):
    """'model[:levels]' -> (model, levels_text_or_None), resolved against the harness's model list.
    Model ids can contain ':' themselves (e.g. 'openrouter/x/y:batch'), so a full-spec match wins;
    otherwise the levels are what follows the last ':'. Unknown models are an error with suggestions."""
    if spec in known:
        return spec, None
    model, sep, levels = spec.rpartition(":")
    if sep and model in known:
        return model, levels
    name = spec if spec in known or not sep else model
    close = difflib.get_close_matches(name, known, n=3, cutoff=0.6)
    hint = f" (did you mean: {', '.join(close)}?)" if close else ""
    raise CritError(f"unknown model {name!r}{hint}; see `art-crit models`")


class Harnesses(dict):
    """Harness instances by name, created on first use (so pi isn't needed for a Claude-Code-only
    batch). Tests pass pre-built ones."""

    def __missing__(self, name):
        if name not in HARNESSES:
            raise CritError(f"unknown harness {name!r} (known: {', '.join(HARNESSES)})")
        self[name] = HARNESSES[name]()
        return self[name]


def plan_runs(config, request, harnesses=None):
    """Resolve every -m [HARNESS:]MODEL[@UPSTREAMS][:LEVELS] (and --set entry) against its harness
    (pi when there's no prefix) before anything starts. Returns [(harness name, model_arg, level), ...]
    with the harness's own model id (`model_arg` keeps the `@slugs` suffix; the base id is what pi gets).
    The same model+upstream given twice has its levels merged."""
    harnesses = harnesses if harnesses is not None else Harnesses()
    model_specs = [*expand_sets(config, request.model_sets), *request.model_specs]
    if not model_specs:
        raise CritError("at least one -m MODEL or --set is required")
    effort_default = request.effort
    known, levels_by_model = {}, {}
    for spec in model_specs:
        name, rest = split_harness(spec)
        harness = harnesses[name]
        rest, upstreams = harness.split_spec(rest)
        if name not in known:
            known[name] = set(harness.models())
        model, levels_text = parse_model_spec(rest, known[name])
        model = harness.resolve(model)
        supported = harness.levels(model)
        levels = expand_levels(levels_text or effort_default or "all", supported, model)
        model_arg = harness.pinned(model, upstreams)
        levels_by_model.setdefault((name, model_arg), {}).update(dict.fromkeys(levels))

    return [(name, model, level) for (name, model), levels in levels_by_model.items() for level in levels]


def assign_run_ids(plan, harnesses, started):
    """The plan -> batch.json's runs, each with its id (the run directory's name, which is also its
    id on the site). Two runs that resolve to one id (models whose names differ only before the last
    "/") are an error before anything starts."""
    runs, owner = [], {}
    for name, model_arg, level in plan:
        harness = harnesses[name]
        display = harness.display_model(model_arg)
        run_id = make_run_id(display, level, started, harness.tag)
        if run_id in owner:
            raise CritError(f"{owner[run_id]!r} and {model_arg!r} both resolve to the run id {run_id!r}; run them in separate batches")
        owner[run_id] = model_arg
        runs.append({"id": run_id, "harness": name, "model": display, "model_arg": model_arg, "level": level, "state": "queued"})
    return runs


def run_label(run):
    return run["model"] if run["harness"] == "pi" else f"{run['model']} [{run['harness']}]"


def page_json(root, slug):
    path = root / "docs" / "data" / slug / "page.json"
    return json.loads(path.read_text()) if path.is_file() else None


def clean_prompt(config, prompt):
    """The prompt as import stores it on the page (path rewrites applied), for comparing."""
    return clean.rewrite_text(prompt.strip(), config.rewrites)[0]


REF_DIR = "references"  # <root>/references/ is where --ref looks; work/references/ holds a run's copies (the importer never publishes it)


def resolve_ref(root, name):
    """A --ref name (a path under <root>/references/) as an absolute path to an existing file inside it."""
    folder = (Path(root) / REF_DIR).resolve()
    ref = (folder / name).resolve()
    if folder not in ref.parents or not ref.is_file():
        raise CritError(f"--ref {name}: no such file in {folder}")
    return str(ref)


def page_refs(root, slug):
    """A page's published reference files (data/<slug>/references/), reused when --page adds runs to it."""
    folder = root / "docs" / "data" / slug / REF_DIR
    if not folder.is_dir():
        return []
    return sorted(str(p) for p in folder.iterdir() if p.is_file() and not p.name.startswith("."))


def render_brief(brief_text, prompt, kind="godot", tool_entries=(), refs=()):
    template = brief_text if brief_text else KINDS[kind]().brief()
    if refs:  # in the brief only: the page's prompt stays the task itself
        prompt += f"\n\nReference files (read them, don't modify them), in ./{REF_DIR}/:\n" + "\n".join(f"- ./{REF_DIR}/{Path(r).name}" for r in refs)
    tools = describe_tools(tool_entries) if "{tools}" in template else ""
    return template.format(prompt=prompt, tools=tools)


def last_line(path):
    if not path.is_file():
        return None
    lines = [line for line in path.read_text(errors="replace").splitlines() if line.strip()]
    return lines[-1][:200] if lines else None


def fmt_elapsed(seconds):
    if seconds is None:
        return "-"
    return f"{int(seconds) // 60}:{int(seconds) % 60:02d}"


class Progress:
    """tty: a table redrawn every 2s, re-parsing each running row's growing session file for
    live turns/tokens/cost. non-tty: one line per state change."""

    def __init__(self, harnesses, runs):
        self.harnesses = harnesses
        self.rows = {}
        for r in runs:
            state = "done" if r["state"] == "complete" else r["state"]
            self.rows[r["id"]] = {
                "model": run_label(r), "harness": r["harness"], "level": r["level"], "state": state,
                "turns": 0, "tokens": 0, "cost": 0.0, "started": None, "elapsed": None, "harness_dir": None,
            }
        self.lock = threading.Lock()
        self.tty = sys.stdout.isatty()
        self._stop = threading.Event()
        self._printed_lines = 0
        self._thread = threading.Thread(target=self._loop, daemon=True) if self.tty else None

    def start(self):
        if self._thread:
            self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)
        if self.tty:
            self._render()

    def track(self, key, harness_dir):
        """Point a row at its harness dir, so the tty loop can find the growing session file."""
        with self.lock:
            self.rows[key]["harness_dir"] = harness_dir

    def update(self, key, **fields):
        with self.lock:
            row = self.rows[key]
            if fields.get("state") == "running" and row["started"] is None:
                row["started"] = time.monotonic()
            row.update(fields)
            if fields.get("state") in ("done", "no output", "failed", "timeout") and row["started"] is not None:
                row["elapsed"] = time.monotonic() - row["started"]
            state = fields.get("state")
        if not self.tty and state:
            print(f"{row['model']} {row['level']}: {state}")

    def _loop(self):
        while not self._stop.wait(2):
            self._refresh_running()
            self._render()

    def _refresh_running(self):
        with self.lock:
            running = [r for r in self.rows.values() if r["state"] == "running" and r["harness_dir"]]
        for row in running:
            try:
                metrics = self.harnesses[row["harness"]].metrics(row["harness_dir"], row["level"])
            except OSError:
                continue
            if not metrics:
                continue
            with self.lock:
                row["turns"] = metrics["turns"]
                row["tokens"] = metrics["tokens"]["total"]
                row["cost"] = metrics["cost_usd"]

    def _render(self):
        with self.lock:
            rows = list(self.rows.values())
        header = f"{'model':<44} {'effort':<8} {'state':<10} {'elapsed':>7} {'turns':>6} {'tokens':>8} {'cost':>8}"
        lines = [header]
        for r in rows:
            elapsed = r["elapsed"] if r["elapsed"] is not None else (time.monotonic() - r["started"] if r["started"] else None)
            lines.append(
                f"{r['model']:<44} {r['level']:<8} {r['state']:<10} {fmt_elapsed(elapsed):>7} "
                f"{r['turns']:>6} {r['tokens']:>8} {r['cost']:>8.3f}"
            )
        if self._printed_lines:
            sys.stdout.write(f"\x1b[{self._printed_lines}A")
        for line in lines:
            sys.stdout.write("\x1b[2K" + line + "\n")
        sys.stdout.flush()
        self._printed_lines = len(lines)


def _kill_group(proc):
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def wait_agent(proc, timeout_s, stop_path):
    """Wait for an agent process, watching for a stop request. Returns (exit_code, outcome), outcome
    "timeout" | "stopped" | None. The process is this process's child (start_new_session=True), so killing
    its group here is the only safe way to stop it — a monitor can only ask, by writing `stop_path`."""
    deadline = time.monotonic() + timeout_s
    while True:
        try:
            return proc.wait(timeout=min(STOP_POLL_S, max(0.05, deadline - time.monotonic()))), None
        except subprocess.TimeoutExpired:
            if stop_path.is_file():
                _kill_group(proc)
                return proc.wait(), "stopped"
            if time.monotonic() >= deadline:
                _kill_group(proc)
                return proc.wait(), "timeout"


class RunDir:
    """<batch>/<run id>/: run.json (the run's record), work/ (the agent's working dir, nothing else is
    written there), harness/ (the agent's session, stdout, stderr, brief, route log), output/ (what the kind made)."""

    def __init__(self, batch_dir, run_id):
        self.path = Path(batch_dir) / run_id
        self.work, self.harness, self.output = (self.path / name for name in ("work", "harness", "output"))
        self.record_path = self.path / "run.json"

    def reset(self):
        """Empty directories for a (re)run."""
        shutil.rmtree(self.path, ignore_errors=True)
        for d in (self.work, self.harness):
            d.mkdir(parents=True)

    def read(self):
        return json.loads(self.record_path.read_text()) if self.record_path.is_file() else None

    def write(self, record):
        self.record_path.write_text(json.dumps(record, indent=2) + "\n")


def run_agent(harness, run, rd, batch, version, timeout_s, progress, live, live_lock, interrupted, kind=None):
    """Run one agent to completion (or until killed by a timeout or Ctrl-C). Returns the run's record
    (written to its run.json), or None if it was killed for a Ctrl-C (the caller leaves its batch.json
    state as "queued" so --resume reruns it; nothing is collected for a run that never really finished).
    The kind's `agent_session` (blender: the run's own Blender) is up for exactly as long as the agent."""
    rd.reset()
    brief = batch["brief"]
    refs = rd.path.parent / REF_DIR  # the batch's own copies, so --resume doesn't depend on the originals
    if refs.is_dir():
        shutil.copytree(refs, rd.work / REF_DIR)
    (rd.harness / "brief.md").write_text(brief)  # kept out of work/: never seen/edited by the agent
    stdout_path, stderr_path = rd.harness / "events.jsonl", rd.harness / "stderr.txt"
    started = datetime.now(timezone.utc)
    key = run["id"]
    progress.track(key, rd.harness)
    progress.update(key, state="running")

    exit_code, outcome = None, None
    try:
        with (kind.agent_session(rd.work, rd.harness) if kind else contextlib.nullcontext()) as mcp, \
                open(stdout_path, "wb") as out, open(stderr_path, "wb") as err:
            cmd = harness.command(run["model_arg"], run["level"], brief, rd.harness, **({"mcp": mcp} if mcp else {}))
            proc = subprocess.Popen(cmd, cwd=rd.work, stdin=subprocess.DEVNULL, stdout=out, stderr=err, start_new_session=True, env=harness.env(run["model_arg"], rd.harness))
            with live_lock:
                live[key] = proc
                if interrupted.is_set():  # Ctrl-C landed between Popen and registering: kill it here
                    _kill_group(proc)
            exit_code, outcome = wait_agent(proc, timeout_s, rd.harness / STOP_FILE)
    except OSError as e:
        return collect(rd, batch, run, harness, version, started, datetime.now(timezone.utc), "failed", f"cannot run harness: {e}", None)
    except CritError as e:  # the kind's session didn't start (e.g. Blender's MCP server)
        return collect(rd, batch, run, harness, version, started, datetime.now(timezone.utc), "failed", str(e), None)
    finally:
        with live_lock:
            live.pop(key, None)

    if interrupted.is_set():
        return None

    ended = datetime.now(timezone.utc)
    session_path = harness.session_file(rd.harness)
    metrics = harness.metrics(rd.harness, run["level"]) if session_path else None

    if outcome == "timeout":
        state, error = "timeout", f"timed out after {int(timeout_s)}s"
    elif outcome == "stopped":  # the monitor asked to stop: killed above, so the exit code is meaningless
        state, error = "failed", "stopped from the local monitor"
    elif exit_code != 0:
        state, error = "failed", last_line(stderr_path) or f"harness exited {exit_code}"
    elif session_path is None:
        state, error = "failed", "no session file written"
    elif metrics["ended_in_error"]:
        state, error = "failed", (metrics["error_message"] or last_line(stderr_path) or "assistant ended in error")[:200]
    else:
        state, error = "complete", None

    record = collect(rd, batch, run, harness, version, started, ended, state, error, metrics)
    progress.update(key, state=state, turns=record["metrics"]["turns"], tokens=record["metrics"]["tokens_total"], cost=record["metrics"]["cost_usd"])
    return record


def collect(rd, batch, run, harness, version, started, ended, state, error, metrics):
    """Write harness/conversation.json (the session in pi's format, which the viewer renders, with
    each tool's duration) and run.json (the run's record, `output` still null). Returns the record."""
    if harness.session_file(rd.harness):
        entries = add_tool_durations(harness.session_entries(rd.harness, batch["brief"], run["level"]))
        (rd.harness / "conversation.json").write_text(json.dumps(entries, indent=2) + "\n")

    metrics = harness.finish(rd.harness, run["model"], dict(metrics or {}))
    for note in metrics.get("notes", ()):
        error = f"{error}; {note}" if error else note
    tokens = metrics.get("tokens") or {}
    record = {
        "id": run["id"],
        "page": batch["page"],
        "model": run["model"],
        "effort": run["level"],
        "kind": batch["kind"],
        "started_at": iso_from_ms(int(started.timestamp() * 1000)),
        "batch": rd.path.parent.name,
        "harness": {"name": harness.name, "version": version},
        "state": state,
        "error": error,
        "route": None,
        **metrics.get("extra", {}),  # whatever the harness adds to the run (pi: the OpenRouter route)
        "metrics": {
            "duration_ms": int((ended - started).total_seconds() * 1000),
            "cost_usd": metrics.get("cost_usd", 0.0),
            **({"cost_estimated": True} if metrics.get("cost_estimated") else {}),
            **({"cost_estimate_proxy": metrics["cost_estimate_proxy"]} if metrics.get("cost_estimate_proxy") else {}),
            "tool_calls": metrics.get("tool_calls", 0),
            "turns": metrics.get("turns", 0),
            "tokens_total": tokens.get("total", 0),
            "tokens_input": tokens.get("input", 0),
            "tokens_output": tokens.get("output", 0),
            "tokens_reasoning": tokens.get("reasoning", 0),
            "tokens_cache_read": tokens.get("cacheRead", 0),
        },
        "output": None,
    }
    rd.write(record)
    return record


def finish_output(kind, rd, record, lock, verify, progress):
    """The kind's step on a completed run: finalize its work into output/, then verify it. Sets
    record["output"] = {kind, ok, error, verified}; a step that fails leaves the agent's state alone."""
    key = record["id"]
    progress.update(key, state=kind.activity)
    shutil.rmtree(rd.output, ignore_errors=True)
    with lock if kind.serial else contextlib.nullcontext():
        ok, error = kind.finalize(rd.work, rd.output)
    output = {"kind": kind.name, "ok": ok, "error": error, "verified": None}
    if ok and verify:
        progress.update(key, state="verifying")
        try:
            report = kind.verify(rd.output)
            output["verified"] = report["ok"] if report else None
        except Exception as e:  # verification must never fail the run
            report = {"ok": None, "error": f"could not run verification: {e}"}
            print(f"note: verification of {record['id']} failed to run: {e}", file=sys.stderr)
        if report is not None:
            report_path = rd.output / "verification" / "verify-report.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, indent=2) + "\n")
    record["output"] = output
    rd.write(record)
    progress.update(key, state="done" if ok else "no output")


def write_batch_json(batch_dir, batch):
    (batch_dir / "batch.json").write_text(json.dumps(batch, indent=2) + "\n")


def batch_versions(batch):
    """{harness name: version} from batch.json."""
    return batch["harnesses"]


def read_batch(batch_dir):
    batch = json.loads((Path(batch_dir) / "batch.json").read_text())
    if any("id" not in r for r in batch["runs"]):
        raise CritError(f"{batch_dir} was made by an older art-crit (one directory per model); it can't be resumed")
    return batch


def verification_reason(rd):
    """Use the kind's saved diagnostics, without branching on kind names. Old batches may have none."""
    path = rd.output / "verification" / "verify-report.json"
    try:
        report = json.loads(path.read_text())
    except (OSError, ValueError):
        return ""
    reasons = []
    for key, label in (("error", ""), ("errors", ""), ("pageErrors", "page error"),
                       ("consoleErrors", "console error"), ("blockedRequests", "blocked request")):
        values = report.get(key) or []
        if isinstance(values, str):
            values = [values]
        reasons.extend(f"{label}: {value}" if label else str(value) for value in values[:3])
    if report.get("booted") is False:
        reasons.append("page did not become ready")
    if not reasons and report.get("framesDiffer") is False:
        reasons.append("captured frames did not change")
    return "; ".join(reasons)


def print_failure_summary(batch_dir, runs, publish_errors=None):
    """Report final problems in plan order, once progress/publishing is finished. Never changes state."""
    failures = []
    for run in runs:
        rd = RunDir(batch_dir, run["id"])
        record = rd.read()
        reasons = []
        if record is None:
            if run["state"] not in UNFINISHED:
                reasons.append("run record missing")
        elif record["state"] in ("failed", "timeout"):
            reasons.append(f"agent {record['state']}: {record.get('error') or 'no reason recorded'}")
        elif record["state"] == "complete":
            output = record.get("output")
            if not output:
                reasons.append("output: no output recorded")
            else:
                if output.get("ok") is False or output.get("error"):
                    reasons.append(f"output: {output.get('error') or 'output step failed without a reason'}")
                if output.get("verified") is False:
                    reasons.append(f"verification: {verification_reason(rd) or output.get('error') or 'check failed without a recorded reason'}")
                elif output.get("verified") is None and output.get("ok"):
                    diagnostic = verification_reason(rd)
                    if diagnostic:
                        reasons.append(f"verification: {diagnostic}")
        if error := (publish_errors or {}).get(run["id"]):
            reasons.append(f"publish: {error}")
        if reasons:
            label = f"{run['id']} ({run['harness']} / {run['model']}:{run['level']})"
            failures.append((label, reasons))
    if not failures:
        return
    print(f"\nFailure summary: {len(failures)} of {len(runs)} runs had problems", file=sys.stderr)
    for label, reasons in failures:
        print(f"  {label}", file=sys.stderr)
        for reason in reasons:
            print(f"    - {' '.join(reason.split())[:500]}", file=sys.stderr)
    print(f"Full records and logs: {batch_dir}", file=sys.stderr)


class Publisher:
    """`art-crit run` (the default): import and push each run as it finishes, so the live site fills up while
    the batch is still running (nothing is left for the batch's own import at the end; see `execute`).
    `--no-publish` turns this off.
    One run at a time: importing rewrites page.json, git needs the index to itself, and a push must never
    see a half-written run directory. A run that can't be published — a secret hit, a failed push — is
    reported and left to the batch's import at the end, which retries it and exits non-zero."""

    def __init__(self, config, batch_dir, slug, title):
        self.config, self.batch_dir, self.slug, self.title = config, batch_dir, slug, title
        self.lock = threading.Lock()
        self.published = set()
        self.errors = {}

    def publish(self, run_id):
        from .cli import cmd_publish  # cli imports runner

        with self.lock:
            try:
                cmd_import(self.config, self.batch_dir / run_id, page=self.slug, title=self.title)
                cmd_publish(self.config.root, f"art-crit run: {self.slug} ({run_id})")
            except CritError as e:
                self.errors[run_id] = str(e)
                print(f"note: {run_id} not published: {e}", file=sys.stderr)
                return
            self.errors.pop(run_id, None)
            self.published.add(run_id)

    def missed(self, runs):
        return [r["id"] for r in runs if r["id"] not in self.published]


def execute(config, request, batch_dir, harnesses, verify=True):
    """Run every unfinished agent, finalize + verify what needs it, then import.
    Drives both a fresh batch and a `--resume`d one (see module docstring)."""
    batch = read_batch(batch_dir)
    parallel = request.parallel or config.run.parallel
    timeout_s = parse_duration(request.timeout or config.run.timeout)
    runs = batch["runs"]
    versions = batch_versions(batch)
    kind = KINDS[batch["kind"]]()
    slug, title = batch["page"], batch["title"]

    if any(r["state"] in UNFINISHED for r in runs):
        kind.prepare()
    progress = Progress(harnesses, runs)
    progress.start()
    finalize_lock = threading.Lock()
    live, live_lock, interrupted = {}, threading.Lock(), threading.Event()
    page_exists = (config.root / "docs" / "data" / slug / "page.json").is_file()
    import_title = title if (batch["title_is_explicit"] or not page_exists) else None
    publisher = Publisher(config, batch_dir, slug, import_title) if request.publish else None

    def save():
        write_batch_json(batch_dir, batch)

    def work(run):
        if interrupted.is_set():
            return
        rd = RunDir(batch_dir, run["id"])
        harness = harnesses[run["harness"]]
        if run["state"] in UNFINISHED:
            run["state"] = "running"
            save()
            record = run_agent(harness, run, rd, batch, versions.get(run["harness"]), timeout_s, progress, live, live_lock, interrupted, kind)
            if record is None:
                return  # Ctrl-C: left "running" here; the handler below resets it to "queued"
            run["state"] = record["state"]
            save()
        else:
            record = rd.read()
            if record is None:
                return
        if interrupted.is_set():
            return
        if record["state"] == "complete" and not (record["output"] and record["output"]["ok"]):
            finish_output(kind, rd, record, finalize_lock, verify, progress)
        if publisher and not interrupted.is_set():  # publishing: this run is live from here on
            publisher.publish(run["id"])

    pool = ThreadPoolExecutor(max_workers=parallel)
    futures = [pool.submit(work, r) for r in runs]
    try:
        for f in futures:
            f.result()
    except KeyboardInterrupt:
        with live_lock:  # set under the lock so run_agent can't register a process we then miss
            interrupted.set()
            for proc in live.values():
                _kill_group(proc)
        pool.shutdown(wait=True, cancel_futures=True)
        for r in runs:
            if r["state"] == "running":
                r["state"] = "queued"
        save()
        progress.stop()
        print(f"interrupted; resume with: art-crit run --resume {batch_dir}")
        print_failure_summary(batch_dir, runs, publisher.errors if publisher else None)
        sys.exit(130)
    pool.shutdown(wait=True)
    progress.stop()
    try:
        if publisher and not publisher.missed(runs):  # every run is already imported and pushed
            print(f"published {len(publisher.published)} runs to {slug!r} as they finished")
            return 0
        result = _import_and_publish(config, batch_dir, slug, import_title, request.publish)
        if publisher and result == 0:
            publisher.errors.clear()  # the final import/push recovered the per-run failures
        return result
    finally:
        print_failure_summary(batch_dir, runs, publisher.errors if publisher else None)


def cmd_run(config, request, *, yes=False, dry_run=False, resume=None, verify=True, harnesses=None, pick=False):
    harnesses = harnesses if harnesses is not None else Harnesses()
    root = config.root

    if resume and pick:
        raise CritError("--pick can't be combined with --resume: the batch already chose its models")
    if resume:
        batch_dir = Path(resume)
        stored = read_batch(batch_dir).get("request")
        if stored:  # replay what the batch recorded; explicit CLI flags override it
            merged = RunRequest.from_dict(stored)
            merged.parallel = request.parallel or merged.parallel
            merged.timeout = request.timeout or merged.timeout
            merged.publish = merged.publish and request.publish  # --no-publish always wins
            request = merged
        return execute(config, request, batch_dir, harnesses, verify)

    prompt, kind, page, title = request.prompt, request.kind, request.page, request.title
    # Adding runs to an existing page: --page alone reuses its prompt and kind.
    existing = page_json(root, page) if page else None
    if not prompt and existing:
        prompt = existing.get("prompt") or ""
    if not prompt:
        raise CritError("PROMPT or --prompt-file is required (or --page with an existing page, to reuse its prompt)")
    # No -m/--set (or -i/--pick): ask which harnesses, models and levels to run. The picks become
    # ordinary -m specs, so planning below validates them exactly like a hand-typed spec.
    if pick or not (request.model_specs or request.model_sets):
        if not sys.stdin.isatty():
            raise CritError("--pick needs an interactive stdin" if pick
                            else "at least one -m MODEL or --set is required")
        request.model_specs += pick_models(harnesses)
        if not request.model_specs:
            raise CritError("no models were picked (or pass -m MODEL / --set)")
    slug = page_slug(page, title, prompt)
    existing = page_json(root, slug)
    page_exists = existing is not None
    page_kind = existing.get("kind", "godot") if page_exists else None
    kind = kind or page_kind or "godot"
    if page_exists and page_kind != kind:
        raise CritError(f"page {slug!r} holds {page_kind} runs; use --kind {page_kind} or another --page")
    # Every import replaces the page's prompt, so a different one would silently relabel the existing runs.
    if page_exists and not request.change_prompt and existing.get("prompt") and clean_prompt(config, prompt) != existing["prompt"]:
        raise CritError(
            f"page {slug!r} was run with a different prompt:\n  {existing['prompt']}\n"
            "Leave the prompt out to reuse it, use another --page, or pass --change-prompt to replace it for the whole page."
        )
    # Adding runs to an existing page reuses the page's published references, unless this batch names its own
    # with --ref: a "use the reference image" prompt must not silently run with no image staged. (ADR-0026)
    reused_refs = []
    if page_exists and not request.refs:
        reused_refs = page_refs(root, slug)
        request.refs = reused_refs
    if kind not in KINDS:
        raise CritError(f"unknown kind {kind!r} (expected one of: {', '.join(KINDS)})")
    missing = KINDS[kind]().missing_tools()
    if missing:
        hint = KINDS[kind].tools_hint
        raise CritError(f"--kind {kind} needs {' and '.join(missing)} on PATH" + (f" ({hint})" if hint else ""))

    plan = plan_runs(config, request, harnesses)
    if KINDS[kind].needs_mcp:
        no_mcp = sorted({name for name, _, _ in plan if not harnesses[name].supports_mcp})
        if no_mcp:
            raise CritError(f"--kind {kind} gives agents MCP tools, which {', '.join(no_mcp)} can't take here "
                            f"(use {', '.join(n for n in HARNESSES if HARNESSES[n].supports_mcp)})")
    versions = {name: harnesses[name].version() for name in dict.fromkeys(name for name, _, _ in plan)}
    title_is_explicit = bool(title)
    if not title:
        title = (existing.get("title") if page_exists else None) or title_from_slug(slug)

    started = datetime.now()
    while (config.run.dir / f"{started:%Y-%m-%d-%H%M%S}-{slug}").exists():  # two batches for one page in the same second
        time.sleep(0.2)
        started = datetime.now()
    batch_dir = config.run.dir / f"{started:%Y-%m-%d-%H%M%S}-{slug}"
    runs = assign_run_ids(plan, harnesses, started)

    print("harness: " + ", ".join(f"{name} {version}" for name, version in versions.items()))
    print(f"kind: {kind}")
    print(f"page: {slug} ({'existing' if page_exists else 'new'}, title: {title!r})")
    print(f"prompt: {prompt}")
    if request.refs:
        refs = ", ".join(Path(r).name for r in request.refs)
        print(f"references: {refs}" + (" (reused from the page)" if reused_refs else ""))
    for i, (name, model, level) in enumerate(plan, 1):
        print(f"  {i}. {'' if name == 'pi' else name + ':'}{model}:{level}")
    print(f"batch dir: {batch_dir}")

    if dry_run:
        return 0

    if not yes:
        if not sys.stdin.isatty():
            raise CritError("refusing to prompt for confirmation on a non-tty stdin; pass --yes")
        answer = input("Start? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("aborted")
            return 1

    batch_dir.mkdir(parents=True)
    (batch_dir / "prompt.md").write_text(prompt)
    for ref in request.refs:
        (batch_dir / REF_DIR).mkdir(exist_ok=True)
        shutil.copy2(ref, batch_dir / REF_DIR / Path(ref).name)
    batch = {
        "prompt": prompt, "kind": kind, "page": slug, "title": title, "title_is_explicit": title_is_explicit,
        "harnesses": versions, "brief": render_brief(request.brief, prompt, kind, config.run.tools, request.refs),
        "request": request.to_dict(), "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "runs": runs,
    }
    write_batch_json(batch_dir, batch)

    return execute(config, request, batch_dir, harnesses, verify)


def _import_and_publish(config, batch_dir, slug, title, publish):
    cmd_import(config, batch_dir, page=slug, title=title)
    print(f"imported into page {slug!r}. Preview with: art-crit serve")
    if publish:
        from .cli import cmd_publish

        return cmd_publish(config.root, f"art-crit run: {slug}")
    print("publish with: art-crit publish")
    return 0


def cmd_models(harness, search=None):
    models = harness.models()
    if search:
        models = [m for m in models if search.lower() in m.lower()]
    for model in sorted(models):
        if search:
            try:
                levels = harness.levels(model)
            except CritError as e:
                print(f"{model}: {e}")
                continue
            print(f"{model}: {', '.join(levels)}")
        else:
            print(model)
    return 0
