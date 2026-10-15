# 0028. A batch added to an existing page reuses the page's references

- Status: Accepted
- Date: 2026-10-15

## Context

References are staged per batch: `-R/--ref` copies files from `<root>/references/` into the batch and into every
run's `work/references/`, and only those copies appear in the brief (ADR-0026). `--page` reuses the existing
page's prompt and kind, but nothing carried the reference files over.

That bit a real batch: `art-crit run --page robbie-the-banker-with-reference -m openai-codex/gpt-6.1-sol:low..max`
was launched without `--ref`, so `work/references/` was empty and the brief had no reference list. The agent
(`gpt-6.1-sol-cx-low-20261015-151145`) listed the working directory, found no image, and answered "Please attach
the reference image—it wasn't included in the message, and there's no image in the working directory." It was
right, but the page's own prompt ("…using the reference image") and the page's published thumbnails made it look
like the image had been passed in. The run ended `complete` with `output.ok: false` ("no files in ./output/") and
nothing in the plan said the references were missing.

The page is the natural owner of these files: every run on it got the same ones, and a `--page` batch is the same
task with more models.

## Decision

`--page` on a page that has published references (`docs/data/<slug>/references/`) adopts them as the batch's refs,
unless the batch passes its own `-R/--ref` (which replaces the set rather than adding to it). They are staged,
listed in the brief and copied into each run's `work/references/` exactly like hand-passed refs, recorded in
`batch.json.request.refs`, and the plan prints which ones were reused:

```
references: robie.jpg (reused from the page)
```

`--ref` keeps its meaning: it looks under `<root>/references/`, and an explicit `--ref` always wins.

## Alternatives considered

- **Warn only** ("this prompt mentions a reference image but no --ref was given"): catches the honest case and
  nothing else — no warning fires for a prompt that says "the toy" or "the picture", and the run still costs money
  before anyone notices. Warnings in a plan that already prints 30 lines are also easy to miss.
- **Always reuse, even with `--ref`** (union of the two sets): lets a batch add one more reference to a page, but
  makes "which files did this run actually see?" depend on the page's state at launch — a run with two plausible
  reference sets is worse for a crit than one clear set.
- **Refuse to run without `--ref` when the page has references**: forces every `--page` batch to restate files the
  page already publishes, and `--ref` reads only `<root>/references/`, so the page's own copies would have to be
  copied back there first.
- **A `--no-refs` flag to opt out per batch**: no use case — a batch that doesn't want the page's references can
  pass `--ref` for the ones it does want, or make a new page.

## Consequences

`--page` is not quite a pure prompt/kind reuse any more: the page's reference set is an *input* to the next batch.
What the new agents get are the page's published copies, which for a file over 8 MiB is the re-encoded JPEG
(ADR-0026), not the original in `<root>/references/`. Re-importing such a batch publishes those same bytes back,
so the page's set is stable across batches. `--resume` replays the recorded `request.refs`, so it never re-reads
the page. Every `--page` batch still gets its own copies under its own batch dir, so deleting a batch or moving a
page can't change what an earlier run saw.
