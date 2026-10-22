"""`art-crit retry`: run a page's failed runs again (same harness, model and effort, the page's own prompt, kind and
references) and replace each failed run that now has a good one."""

import shutil
import sys
from pathlib import Path

from .config import RunRequest
from .harness import split_model_route
from .runner import Harnesses, cmd_run, page_json
from .site import rebuild, run_failed
from .util import CritError


def retry_spec(harnesses, run, listed=None):
    """The `-m` spec that starts `run` again. run.json keeps the harness's display name (`anthropic/claude-opus-5-5`),
    so the model id is the one the harness lists under that display name; a pinned OpenRouter upstream is the
    `@slugs` suffix pi puts on the display name. `listed` caches each harness's model list (pi and agy ask a program)."""
    name = run["harness"]["name"]
    harness = harnesses[name]
    display, upstreams = split_model_route(run["model"])
    listed = {} if listed is None else listed
    if name not in listed:
        listed[name] = harness.models()
    models = listed[name]
    model = next((m for m in models if harness.display_model(m) == display), None)
    if model is None:
        raise CritError(f"{run['id']}: {name} no longer offers {display}")
    return f"{name}:{harness.pinned(model, upstreams)}:{run['effort']}"


def _key(run):
    return run["harness"]["name"], run["model"], run["effort"]


def _fixed(run, runs):
    """Whether a newer run of the same harness, model and effort is good (so `run`, a failed one, is replaced)."""
    return any(_key(r) == _key(run) and r["started_at"] > run["started_at"] and not run_failed(r) for r in runs)


def _replace_fixed(root, slug, targets, publish):
    """Delete the target runs that have a good newer run, rebuild and publish once. Returns the ids that stay."""
    runs = (page_json(root, slug) or {"runs": []})["runs"]
    replaced = [t["id"] for t in targets if _fixed(t, runs)]
    for run_id in replaced:
        shutil.rmtree(root / "docs" / "data" / slug / "runs" / run_id)
        print(f"removed run {slug}/{run_id}")
    if replaced:
        rebuild(root)
        if publish:
            from .cli import cmd_publish  # cli imports this module

            cmd_publish(root, f"art-crit retry: {slug} (replaced {len(replaced)} failed run{'s' if len(replaced) != 1 else ''})",
                        [Path("docs/data") / slug, Path("docs/data/pages.json")])
    return [t["id"] for t in targets if t["id"] not in replaced]


def cmd_retry(config, slug, run_ids=(), *, yes=False, dry_run=False, parallel=None, timeout=None, publish=True,
              verify=True, harnesses=None):
    root = config.root
    page = page_json(root, slug)
    if page is None:
        raise CritError(f"no such page: {slug}")
    by_id = {r["id"]: r for r in page["runs"]}
    for run_id in run_ids:
        if run_id not in by_id:
            raise CritError(f"no such run: {slug}/{run_id}")
        if not run_failed(by_id[run_id]):
            raise CritError(f"{run_id} didn't fail; add runs with `art-crit run --page {slug}`")
    targets = [by_id[i] for i in run_ids] or [r for r in page["runs"] if run_failed(r)]
    if not targets:
        print(f"no failed runs on {slug}")
        return 0

    # A failed run that already has a good newer run (a manual re-run, or an interrupted retry) isn't run again.
    todo = [t for t in targets if not _fixed(t, page["runs"])]
    harnesses = harnesses if harnesses is not None else Harnesses()
    listed, specs = {}, {}
    for run in todo:
        try:
            specs[retry_spec(harnesses, run, listed)] = None
        except CritError as e:
            if run_ids:
                raise
            print(f"skipping {e}", file=sys.stderr)  # one retired model doesn't stop the others
    if not specs and dry_run:
        print("nothing to run again")
        return 0
    if specs:
        print(f"retrying {len(todo)} failed run{'s' if len(todo) != 1 else ''} on {slug}")
        request = RunRequest(prompt="", page=slug, model_specs=list(specs), parallel=parallel, timeout=timeout, publish=publish)
        try:
            rc = cmd_run(config, request, yes=yes, dry_run=dry_run, verify=verify, harnesses=harnesses)
        except (SystemExit, KeyboardInterrupt):  # Ctrl-C: what finished is already published, so replace what it fixed
            _replace_fixed(root, slug, targets, publish)
            raise
        if dry_run or (rc and len(page_json(root, slug)["runs"]) == len(page["runs"])):
            return rc  # nothing was run (a dry run, or the confirmation was declined)
    else:
        rc = 0
    kept = _replace_fixed(root, slug, targets, publish)
    if kept:
        print(f"still failed: {', '.join(kept)}", file=sys.stderr)
    return rc or (1 if kept else 0)
