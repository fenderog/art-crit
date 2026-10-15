"""Regenerate page.json / pages.json from runs/*/run.json, and GC unreferenced
engines. Also `rm` and `list`, which both end by calling rebuild()."""

import json
import re
import shutil
from datetime import datetime, timedelta, timezone

from .util import CritError, effort_sort_key, title_from_slug


def _ended_at(run):
    started = datetime.strptime(run["started_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    ms = (run.get("metrics") or {}).get("duration_ms") or 0
    return (started + timedelta(milliseconds=ms)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pick_thumb(runs):
    """The most recent run (by started_at, then effort order) that has a thumb."""
    for run in sorted(runs, key=effort_sort_key, reverse=True):
        if run.get("thumb"):
            return run
    return None


def apply_ranking(page_dir, runs):
    """Set each run's `rank` from data/<slug>/ranking.json (null when unranked), dropping entries
    for runs that no longer exist (e.g. after `art-crit rm`)."""
    path = page_dir / "ranking.json"
    ranking = json.loads(path.read_text()) if path.is_file() else {"ranks": {}}
    ids = {r["id"] for r in runs}
    kept = {k: v for k, v in ranking.get("ranks", {}).items() if k in ids}
    if path.is_file() and kept != ranking.get("ranks"):
        path.write_text(json.dumps({**ranking, "ranks": kept}, indent=2) + "\n")
    for run in runs:
        run["rank"] = kept.get(run["id"])


def rebuild(root):
    docs = root / "docs"
    data_dir = docs / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    referenced_engines = set()
    pages = []

    for page_dir in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        runs = []
        runs_dir = page_dir / "runs"
        if runs_dir.is_dir():
            for run_dir in sorted(runs_dir.iterdir()):
                rj = run_dir / "run.json"
                if rj.is_file():
                    runs.append(json.loads(rj.read_text()))
        if not runs:
            shutil.rmtree(page_dir)
            continue

        runs.sort(key=effort_sort_key)
        apply_ranking(page_dir, runs)
        (page_dir / "results.json").unlink(missing_ok=True)
        for run in runs:
            output = run.get("output")
            if output and output.get("engine"):
                referenced_engines.add(output["engine"])

        slug = page_dir.name
        page_json_path = page_dir / "page.json"
        existing = json.loads(page_json_path.read_text()) if page_json_path.is_file() else {}
        page = {
            "slug": slug,
            "title": existing.get("title") or title_from_slug(slug),
            "kind": existing.get("kind", "godot"),
            "prompt": existing.get("prompt", ""),
            "final_prompt": existing.get("final_prompt"),
            "created": existing.get("created") or min(r["started_at"] for r in runs),
            "updated": max(_ended_at(r) for r in runs),
            "runs": runs,
        }
        refs_dir = page_dir / "references"  # --ref files published by import; the viewer lists them by name
        if refs_dir.is_dir():
            page["references"] = sorted(p.name for p in refs_dir.iterdir() if p.is_file())
        page_json_path.write_text(json.dumps(page, indent=2) + "\n")

        thumb_run = _pick_thumb(runs)
        pages.append(
            {
                "slug": slug,
                "title": page["title"],
                "kind": page["kind"],
                "n_runs": len(runs),
                "models": sorted({r["model"] for r in runs}),
                "updated": page["updated"],
                "thumb": f"data/{slug}/runs/{thumb_run['id']}/{thumb_run['thumb']}" if thumb_run else None,
            }
        )

    pages.sort(key=lambda p: p["updated"], reverse=True)
    (data_dir / "pages.json").write_text(json.dumps(pages, indent=2) + "\n")

    engines_dir = docs / "engines"
    if engines_dir.is_dir():
        for d in engines_dir.iterdir():
            if d.is_dir() and d.name not in referenced_engines:
                shutil.rmtree(d)


def run_failed(run):
    """Whether a run is broken in any of the three senses (ADR-0018): the agent didn't finish it
    (`state` isn't complete), the kind step recorded nothing or failed (`output` / `output.ok`),
    or the check failed (`output.verified`). An unchecked run (`verified` null) isn't failed."""
    if run.get("state") != "complete":
        return True
    output = run.get("output")
    if not output:
        return True
    return output.get("ok") is False or output.get("verified") is False


def _failure_reason(run):
    if run.get("state") != "complete":
        return f"agent {run.get('state')}"
    if not run.get("output"):
        return "no output"
    if run["output"].get("ok") is False:
        return "kind step failed"
    return "not verified"


def cmd_rm(root, slug, run_id=None, failed=False, yes=False):
    page_dir = root / "docs" / "data" / slug
    if not page_dir.is_dir():
        raise CritError(f"no such page: {slug}")
    if failed:
        if run_id is not None:
            raise CritError("--failed takes no run id: it removes every failed run on the page")
        runs_dir = page_dir / "runs"
        doomed = []
        if runs_dir.is_dir():
            for run_dir in sorted(runs_dir.iterdir()):
                rj = run_dir / "run.json"
                if rj.is_file() and run_failed(json.loads(rj.read_text())):
                    doomed.append(run_dir.name)
        if not doomed:
            print(f"no failed runs on {slug}")
            return 0
        runs = {d: json.loads((runs_dir / d / "run.json").read_text()) for d in doomed}
        print(f"failed runs on {slug}:")
        for d in doomed:
            print(f"  {d}\t{runs[d]['model']}\t{runs[d]['effort']}\t{_failure_reason(runs[d])}")
        if not yes:
            answer = input(f"Remove {len(doomed)} run{'s' if len(doomed) != 1 else ''}? [y/N] ").strip().lower()
            if answer not in ("y", "yes"):
                print("aborted")
                return 1
        for d in doomed:
            shutil.rmtree(runs_dir / d)
            print(f"removed run {slug}/{d}")
        rebuild(root)
        return 0
    if run_id is None:
        shutil.rmtree(page_dir)
        print(f"removed page {slug}")
    else:
        run_dir = page_dir / "runs" / run_id
        if not run_dir.is_dir():
            raise CritError(f"no such run: {slug}/{run_id}")
        shutil.rmtree(run_dir)
        print(f"removed run {slug}/{run_id}")
    rebuild(root)
    return 0


def cmd_rename(root, old, new, title=None):
    """Move a page to a new slug. The slug is also each run.json's `page`; a title that was
    only derived from the old slug follows it, any other title stays unless `title` is given."""
    data_dir = root / "docs" / "data"
    old_dir, new_dir = data_dir / old, data_dir / new
    if not old_dir.is_dir():
        raise CritError(f"no such page: {old}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", new):
        raise CritError(f"bad slug {new!r}: use lowercase letters, digits and single hyphens")
    if new_dir.exists():
        raise CritError(f"page already exists: {new}")
    old_dir.rename(new_dir)
    for rj in new_dir.glob("runs/*/run.json"):
        run = json.loads(rj.read_text())
        run["page"] = new
        rj.write_text(json.dumps(run, indent=2) + "\n")
    page_path = new_dir / "page.json"
    page = json.loads(page_path.read_text()) if page_path.is_file() else {}
    if title or page.get("title") in (None, title_from_slug(old)):
        page["title"] = title or title_from_slug(new)
    page_path.write_text(json.dumps({**page, "slug": new}, indent=2) + "\n")
    rebuild(root)
    print(f"renamed page {old} -> {new}")
    return 0


def cmd_list(root):
    pages_json = root / "docs" / "data" / "pages.json"
    if not pages_json.is_file():
        print("no pages")
        return 0
    for p in json.loads(pages_json.read_text()):
        print(f"{p['slug']}\t{p['n_runs']} runs\tupdated {p['updated']}\t{', '.join(p['models'])}")
        results = json.loads((root / "docs" / "data" / p["slug"] / "page.json").read_text())["runs"]
        for r in results:
            verified = {True: "yes", False: "no", None: "?"}[(r.get("output") or {}).get("verified")]
            print(f"  {r['id']}\t{r['effort']}\t{r['model']}\tverified={verified}")
    return 0
