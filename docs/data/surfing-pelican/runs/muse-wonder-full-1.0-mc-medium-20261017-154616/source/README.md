# Surfing Pelican

An animated, non-interactive Three.js scene: a pelican built from primitives
surfs a curling breaker — carving up and down the wave face, balancing with its
wings, kicking up spray, with drifting clouds, gulls, and cascading foam.

## Run

```bash
npm install
npx vite
```

Then open the URL Vite prints in a browser (Vite resolves the bare `three`
import for local development; the packaged single-file build needs no server). There are no controls; the camera
tracks the pelican automatically and `prefers-reduced-motion` slows the scene.

## Files

- `index.html` — page and styles
- `main.js` — the whole Three.js scene (ES module, imports `three` by name)
