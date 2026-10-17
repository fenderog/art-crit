# Surfing Pelican

An animated, non-interactive 3D scene built with Three.js: a pelican balances on a teal surfboard, carving across a rolling ocean in front of a curling wave, with drifting clouds, distant palm islands, and trailing spray. No input is needed — just watch it ride.

## Run locally

```bash
npm install
npx serve .        # or: python3 -m http.server 8000
```

Then open the printed local URL (for example `http://localhost:3000`) in a browser.

## Files

- `index.html` — page shell and caption overlay
- `main.js` — the whole Three.js scene and animation (pelican built from primitives, no external models or textures)

## Verify bundling

```bash
npx esbuild main.js --bundle --format=esm --outfile=/dev/null
```
