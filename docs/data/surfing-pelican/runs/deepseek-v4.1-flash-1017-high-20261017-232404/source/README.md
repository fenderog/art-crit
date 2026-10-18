# Pelican Surf

A short, non-interactive 3D vignette: a pelican riding a surfboard through a
golden-hour sea. Built with three.js.

## Run

```bash
npm install
python3 -m http.server 8080
```

Open <http://localhost:8080>. A local server is needed for the ES modules and
the bare `three` import during development.

## What's inside

- `index.html` — canvas, cinematic overlay, and the module entry point.
- `main.js` — renderer, lighting, camera drift, and the animation loop.
- `ocean.js` — analytic swell + a custom water shader (reflections, glitter,
  foam, aerial haze). The same wave functions drive the board's motion.
- `sky.js` — gradient sky shader, sun glow, drifting clouds, distant birds.
- `pelican.js` — the procedural pelican, surfboard, and their balancing
  animation.
- `particles.js` — bow spray, trail foam, and waterline bubbles.
- `textures.js` — all textures are drawn onto canvases at runtime, so the page
  needs no external image assets.

There are no controls: the camera, bird, board, water, and spray are all
animated by a single clock. The page performs no network requests and uses no
storage, so the packaged build works offline in a sandboxed iframe.
