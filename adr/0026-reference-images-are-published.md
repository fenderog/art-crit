# 0026. Reference images are published beside the page

- Status: Accepted
- Date: 2026-10-15

## Context

`--ref` files (a photo of a toy, a sketch) are part of what the agents were asked to make, but they used to stay
local: the rule was that reference files are the user's own files and are never published. That made pages with
references half-readable on the site — "Model the robbie the banker coin bank using the reference image" with no
way to see the image the models saw.

## Decision

Import publishes the batch's `references/` copies to `data/<slug>/references/` (a re-import replaces the set), and
`rebuild` lists the files' names in `page.json.references`. The page's details sidebar shows each image as a
thumbnail (a grid, so any number of references work); clicking a thumbnail expands it to the sidebar's width.
Images are shown through `<img>` only — the same rule as model-made SVGs (ADR-0004) — never inlined or framed.
A file over 8 MiB is re-encoded as a JPEG at most 2048 px wide (ffmpeg); anything still over ~20 MiB aborts the
import (Pages takes at most 25 MiB per file).

## Alternatives considered

- **Keep references local** (the old rule): the page can't be judged properly without seeing what the models saw,
  which is the whole point of a crit.
- **Re-encode every reference like transcript images**: references are looked at once by a human at full size, not
  stored as base64 in a transcript; byte-for-byte copies keep them faithful and cost nothing at today's sizes.
- **Show references in run.html too**: every run on a page got the same files, so the page sidebar is the right
  (single) home for them.
- **Non-image references in the viewer**: the brief may point at text files, but thumbnails are for images; other
  files are published (the agents used them) but not rendered.

## Consequences

Reference files become public — they were already the least sensitive thing in a run (the user chose them as the
task's subject), but a private photo can no longer be used as a reference on a published page. `references/` is
still skipped by `stage_source`: the per-run copies are never published, only the batch's originals.
