# Surfing Pelican

An animated, non-interactive 3D scene of a pelican surfing at golden hour, built with Three.js. There are no controls — the pelican carves back and forth on its own, flapping for balance while its pouch swings, spray kicks up behind the board, and the camera sways gently.

## Run locally

```bash
npm install
npm start
```

Then open http://localhost:8891 in a browser.

## What's in the scene

- A pelican built entirely from Three.js primitives: white body and S-curved neck, long orange beak with a swinging pouch, dark-tipped wings and tail, and webbed feet planted on the board.
- A striped surfboard whose top texture (including the "PELI" logo) is generated on a canvas in code — no external assets.
- A large curling wave with a bumpy foam crest, an animated ocean surface, a foam trail and spray particles behind the board, plus drifting clouds, distant flapping birds, and a low sun.

## Files

- `index.html` — page entry point and overlay text
- `style.css` — full-screen layout and overlay styling
- `main.js` — all Three.js scene, pelican construction, and animation

## Packaging note

The page uses ES modules imported by package name (`three`), with no CDN links or import maps, so `esbuild main.js --bundle --format=esm --outfile=/dev/null` succeeds and the result can be inlined into a single self-contained HTML file that runs offline.
