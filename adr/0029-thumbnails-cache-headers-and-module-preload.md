# 0029. Cards show import-time thumbnails; run files get cache headers; pages preload their modules

- Status: Accepted
- Date: 2026-10-16

## Context

Measured on the live site (cold cache, desktop) before this record: the home page downloaded 4.4 MB for nine
cards, a 20-run Godot page 4.2 MB, a 59-run media page 2.9 MB, and ~90% of it was images. The site's own code is
~70 KB of JS and 65 KB of CSS.

- A media run had no thumbnail: `run.thumb` was its first output image itself, so a home card could pull a 1.4 MB
  PNG. A card's hero and its strip of small thumbnails loaded every full-size output of the run.
- A Godot or web run's `thumb.png` was the 1280×720 verification screenshot (200–570 KB each) shown in ~300 px cards.
- Cloudflare Pages sends `Cache-Control: public, max-age=0, must-revalidate` for every file, so a return visit
  revalidated all ~40 requests, run directories included, although a published run never changes.
- Each page's module graph is three levels deep (`page.js` imports ten modules, which import others), and the
  browser only discovers it level by level: the page's data request started ~0.5 s after the HTML arrived, and the
  thumbnails only after that.

## Decision

1. **Every raster output gets an 800 px JPEG thumbnail at import** (`media.write_thumb`, ffmpeg; transparency is
   composited over white, since JPEG has no alpha). A media item carries it as `item.thumb`
   (`media/<stem>.thumb.jpg`); a Godot or web run's is `thumb.jpg`, made from the verification screenshot; `run.thumb`
   is the run's first thumbnail. SVGs keep no thumbnail (ffmpeg rasterizes them only with librsvg, and they are
   shown only through `<img>` anyway, ADR-0004); without ffmpeg the screenshot is copied as `thumb.png` as before.
   The viewer shows thumbnails everywhere a run is one of many (home cards, the runs table, the run grid, compare
   cards, the click-to-play overlay) and the file itself only on the run page. `art-crit rebuild` backfills thumbnails
   for runs published before this, from their published files, and rewrites their `run.json`.
2. **`docs/_headers` sets a cache policy per path**: run directories (`/data/:slug/runs/*`) one day plus a week of
   stale-while-revalidate, vendored assets and engines one year immutable. The viewer's own scripts and stylesheet stay
   at Pages' default (revalidate every time) because there is no cache-busting yet (ADR-0012): a long max-age could
   pair a new HTML page with an old script. Data JSON is unaffected: the viewer fetches it with `cache: "no-cache"`.
3. **Each HTML page lists `<link rel="modulepreload">` for its entry module's whole static import closure** (and, for
   run.html and monitor.html, the transcript modules they always import dynamically), so the graph loads in one round
   trip. A test derives the closure from the `import` statements and fails when the lists drift. The three.js bundle is
   never preloaded: it loads on a click.

## Alternatives considered

- **Serve resized images from the Worker (Cloudflare Images or a resize on the fly)**: a paid feature and a moving
  part on every image request; the repo-is-the-database model (ADR-0003) wants the bytes committed.
- **One thumbnail per run instead of per item**: a media card's strip and hero swap between the run's files, so a
  per-run thumbnail would still have loaded every other file at full size.
- **WebP or AVIF thumbnails**: smaller, but the user's ffmpeg has no WebP encoder (AGENTS.md) and JPEG at 800 px is
  already 25–40 KB.
- **`immutable` on run directories**: a run id can be re-imported (the Muse cost backfill does that), so a day with
  stale-while-revalidate instead; an `_headers` rule is easy to tighten later.
- **Bundling the viewer's modules**: ADR-0002 rules out a build step for the viewer; modulepreload gets the same
  single round trip without one.
- **Long cache headers on `assets/*.js` too**: the biggest remaining saving on repeat visits, but it needs
  cache-busting first (ADR-0012).

## Consequences

- Home and page loads drop from several MB to a few hundred KB; the data request and the thumbnails start one
  round trip after the HTML.
- `docs/data/` gains one ~30 KB file per raster output; the full-size `thumb.png` screenshots are gone.
- A new viewer import must be added to the page's modulepreload list; the test says which.
- A re-import of an existing run id can show its old images to a repeat visitor for up to a day.
- Changing how a thumbnail is made doesn't regenerate existing ones: `rebuild` only makes missing ones.
