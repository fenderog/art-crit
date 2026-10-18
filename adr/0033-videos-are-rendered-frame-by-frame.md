# 0033. Social videos are drawn frame by frame by an animated page in Chrome

- Status: Accepted
- Date: 2026-10-17

## Context

The first `art-crit video` (ADR-0032) laid each run's clip over a still text card and faded between cards. The result was
correct but static: nothing moved except the runs' own clips, the first seconds were a wall of text, and nothing asked the
viewer to do anything. Short-form feeds reward a strong first frame, constant motion, fast cuts, readable stats, a reason
to comment and a sound track. ffmpeg here has no `drawtext`, the CLI adds no dependencies (ADR-0002), and Chrome is
already required.

## Decision

Each layout is one animated page (`src/art_crit/scene/`) that headless Chrome draws one frame at a time: `renderFrame(f)` sets
every element's pose as a pure function of the frame number (no CSS transitions, timers or clocks), waits for the frame
images it needs to decode, and video.py screenshots it over CDP and pipes the JPEG straight into ffmpeg. Python owns the
plan: the timeline, the timings (`TIMING`), the tile geometry, the stickers and the owner's pick. The same plan gives the
sound cues, so `video_sound.py` (standard library synthesis into a WAV) hits on the cuts. Each run's source clip is cut
into JPEG frames once and shared by every layout. The scene imports the site's `runs.js`, so models are named, coloured
and iconned the way the site shows them; it is served from the job's temp folder with `assets/` linked to `docs/assets/`.
The renderer is a second Chrome without the SwiftShader flags (the recorder keeps them), which draws a frame in about
16 ms instead of 75 ms on this machine.

## Alternatives considered

- **ffmpeg filters for the motion** (overlay expressions, zoompan, PNG text cards): no text without `drawtext`, every animated
  word would be another PNG, and springs, masks and count-ups get unreadable fast.
- **Recording the page in real time** (Playwright's screen recording or a CSS-animated page): frame timing depends on load,
  the codec is low quality, and a slow frame becomes a stutter. Drawing frame by frame is deterministic.
- **`<video>` elements seeked per frame**: seeking H.264 is slow and inexact; JPEG frames decode quickly and exactly.
- **Remotion or another motion library**: a Node toolchain and a dependency tree for something a few hundred lines do.
- **Licensed or stock music**: can't be shipped in a public repo. The synthesized beat is plain on purpose, and `--no-sound`
  leaves room for a platform's own sounds.

## Consequences

The videos have a hook, motion throughout, counting stats, superlative stickers and a "Place your vote on art-crit"
ending, with sound. A layout takes about 15 to 40 seconds to draw (30 fps, so about 1 to 1.5 s of frames per second of
video), on top of the recording. The scene depends on `runs.js` exports (`prettyModelName`, `vendorName`, `vendorIcon`,
`vendorOptions`, `EFFORTS`), so renaming those means updating it. Timings live in one place (`TIMING`); changing a beat in
scene.js without it puts the sounds out of step.
