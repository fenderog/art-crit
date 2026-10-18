# Surfing Pelican

A non-interactive, continuously animated Three.js scene: a stylized pelican riding a long board across a golden-hour ocean.

## What's inside

- Procedural low-poly pelican with layered feather wings, a long mandible and hanging throat pouch
- Custom GLSL ocean with five directional waves, analytic normals, sun glints, whitecaps and a board wake
- Gradient sunset sky, canvas-generated clouds, distant birds and a GPU point-sprite spray system
- Slow cinematic camera that stays ahead of the rider, with no user controls
- CSS-only title treatment and subtle film texture

Everything is generated in code. There are no image, font or network assets.

## Run locally

```bash
npm install
python3 -m http.server 8000
```

Then open `http://localhost:8000/`. (Opening the file directly won't resolve the bare `three` import, so use a local server.)

## Build check

```bash
npx esbuild main.js --bundle --format=esm --outfile=/dev/null
```

The page is designed to be packaged into a single self-contained `index.html` with esbuild.
