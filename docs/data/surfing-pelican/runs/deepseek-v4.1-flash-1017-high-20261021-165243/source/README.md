# Surfing Pelican

An animated, non-interactive WebGL scene made with [three.js](https://threejs.org/): a sunglass-wearing pelican riding a surfboard on a golden-hour sea.

Everything is generated in code — the Gerstner-style ocean shader, the pelican and board geometry, spray, wake and cloud textures. There are no external images, fonts or network requests at runtime.

## Run locally

```bash
npm install
python3 -m http.server 8000
# open http://localhost:8000
```

The page imports `three` by package name, so it is intended to be bundled before viewing as a single file:

```bash
npx esbuild main.js --bundle --format=esm --outfile=/dev/null
```

## Files

- `index.html` — entry point and title overlay
- `style.css` — typography, frame and grain overlay
- `main.js` — renderer, sky, lighting, clouds, camera, spray, wake and animation loop
- `ocean.js` — ocean shader plus matching CPU wave functions
- `pelican.js` — procedural surfboard, pelican and distant-bird geometry
