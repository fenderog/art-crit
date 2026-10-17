# 0032. Social videos are made locally with ffmpeg and headless Chrome, from the CLI or the local compare page

- Status: Accepted
- Date: 2026-10-17

## Context

The comparisons are best shown as moving pictures on social media (vertical for TikTok, Reels and Shorts, landscape for X and
YouTube). Doing that by hand means screen-recording the compare page and cutting it. The outputs are mixed: images, SVGs, the
model's own videos, games, web pages and 3D models. The ffmpeg on this machine has no `drawtext` and there is no image library,
so text can't be drawn by ffmpeg or the standard library alone.

## Decision

`art-crit video` (`video.py`) turns each selected run into one silent square clip (its video, a recording of its game or 3D
model, or its pictures with a slow zoom), then lays those clips over text cards for each layout (one at a time vertical, all at
once vertical, one at a time landscape) with ffmpeg. Cards are HTML screenshotted by Chrome, the same Playwright + Chrome the
verify step already needs. Games are recorded in `play.html`, so they run in the site's sandbox. It is available from the CLI
and, on `art-crit serve` only, from a panel on the compare page through `POST/GET api/video`, which follows the rules of the
other local APIs (loopback Host, same-origin, JSON; reads without CORS). Files go to `<root>/videos/<page>/`, outside `docs/`
and git-ignored, so nothing here is ever published.

## Alternatives considered

- **Recording the compare page itself**: the layout is built for a laptop, not a phone, the output varies with the viewer's
  state, and every video would need manual cutting.
- **Drawing text with ffmpeg `drawtext` or PIL**: not available here (and no new dependencies); Chrome renders text well and is already required.
- **A button on the published site**: it would need a server to run ffmpeg and Chrome; this is for the owner's machine.
- **Only the CLI, or only the button**: both are small once the work is one function, so both exist.

## Consequences

Making videos needs ffmpeg and Playwright with Chrome (a clear error says so otherwise). Recording a game or 3D model takes
seconds per run, a whole set of three layouts about half a minute. A game that needs a specific input won't show much beyond
its start. One job at a time runs in the server. The recorder depends on `play.html`'s `.play-frame iframe` and the run page's
`.model-view` / `.model-stage` markup, so changing those means rechecking it (the tests record a game).
