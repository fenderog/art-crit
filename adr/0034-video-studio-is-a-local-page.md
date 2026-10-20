# 0034. The video studio is a local page that designs a video and renders it with the frame-by-frame scene

- Status: Accepted
- Date: 2026-10-19

## Context

`art-crit video` (ADR-0032, ADR-0033) makes three fixed layouts of runs of one page. The owner wanted to design videos
instead: a template, results from any prompt, their own text cards, music, a preview, from the browser. A design mockup
("Video studio" artboard, a Claude Design component with placeholder data) laid out the page: six templates, slots, a
preview with transport controls, a timeline of editable cards, settings and a list of renders. The compare page's quick
panel was the only other way to make a video from the browser.

## Decision

`docs/studio.html` is a local-only page (like the run monitor: published, but inert without `art-crit serve`'s API) built
on the site's own tokens, modules and CSP. Its whole state is a JSON spec. Python owns every rule: `studio.catalog()` is
what the page offers, `studio.check_spec` what a spec may hold, and `studio.timeline` the play order and lengths, which the
page asks for (`POST api/studio/plan`) instead of computing its own, so the preview and the render can't drift apart. The
render reuses video.py's recorder and frame-by-frame renderer with a second scene (`scene/studio.js`) that shares its
helpers with the layouts' scene (`scene/motion.js`): cards in the mockup's four looks, and the runs in the template's
layout, animated like the existing videos. The music styles are synthesized like the beat (ADR-0033). To make studio videos look like `art-crit video`'s,
its opening and closing are cards too (Hook, Finale) drawn by the same code (`scene/parts.js`), its three layouts are
templates (Reveal, Grid, Wide), and a new studio starts as a Reveal between a Hook and a Finale. The compare page's
panel is replaced by a link that opens the studio with the compared runs in its slots; `POST api/video` now takes a studio
spec only, and the CLI keeps the three layouts.

## Alternatives considered

- **Computing the timeline in the page as well**: instant, but two implementations of the same rules (cards between
  blocks, clamped places, lengths by type) would drift. A local round trip takes milliseconds.
- **Previewing real frames** (the scene in an iframe): the frames only exist after recording each run (seconds to a minute
  per game), so the preview shows thumbnails in the template's layout and the timing instead.
- **"Sound from" a result** (in the mockup): the browser recordings of games, pages and 3D models have no sound, and
  model-made videos mostly have none either; dropped, at the owner's choice.
- **Keeping the compare page's panel too**: two places to make videos from the browser; the studio covers it (a link
  pre-fills it with the compared runs).
- **A flat look like the mockup's preview**: the owner chose the animated look of the existing videos, with the cards in
  the mockup's colours.

## Consequences

Designing a video needs no command line. The page depends on `studio.catalog()`'s shape and the plan endpoint, the scene
on `runs.js` (through motion.js), and both scenes on motion.js, so a change there is checked by both scenes' tests. Renders
run one at a time; renders under way or failed live in the server's memory, while finished ones are the files in
`videos/studio/` (each with a `.json` of its details), so the list survives a restart and Delete removes the file. A spec saved in the browser can name runs that were later removed; the page then shows those slots empty.
