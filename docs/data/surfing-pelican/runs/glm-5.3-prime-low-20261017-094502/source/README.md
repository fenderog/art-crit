# Surfing Pelican

An animated, non-interactive WebGL scene built with [three.js](https://threejs.org/):
a pelican carving gentle turns on a yellow surfboard across a rolling sunset ocean.

## What's in the scene

- **Ocean** — a large plane displaced in a custom shader by layered travelling
  sine waves, with foam on the crests, sun glitter, and fog toward the horizon.
- **Sunset sky** — a shader sky dome with a gradient and a glowing sun,
  plus drifting low clouds.
- **Pelican** — assembled from primitives (body, neck, head, big orange beak
  with a pouch, flapping wings with dark primary feathers, webbed feet).
- **Surfboard** — an extruded shape with a red racing stripe and a fin.
- **Motion** — the rider follows the exact same wave function as the shader,
  so the board sits on the water: it pitches with the wave face, banks into
  each carve, while the pelican counterbalances, bobs its head, kicks its
  tail, and lazily flaps its wings. The camera softly tracks the action.

No interaction is required (or possible) — just open the page and watch.

## Run locally

Serve the directory over HTTP (ES modules won't load from `file://`):

```bash
npx serve .        # or: python3 -m http.server
```

## Files

- `index.html` — entry point, canvas, and title
- `main.js` — all scene setup and animation (ES module)
