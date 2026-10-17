# Surfing Pelican

An animated, non-interactive 3D scene: a stylized pelican carving across a
GPU-displaced ocean at golden hour. Built with [three.js](https://threejs.org/)
and bundled as a single self-contained page.

## Running

Serve this folder with any static server and open `index.html`:

```bash
npx serve .
```

The page runs entirely offline — no network requests and no storage.

## What is in the scene

- **Ocean** — a 400×400 plane displaced in the vertex shader by a sum of four
  sine waves. The same wave definitions (`waves.js`) drive both the GPU
  displacement and the CPU buoyancy, so the surfer rides exactly on the
  visible surface. Normals are recomputed analytically for correct lighting.
- **Pelican** — modelled procedurally from three.js primitives: an ellipsoid
  body, a tube neck, a head with a long orange mandible and a wobbling throat
  pouch, flapping extruded wings, webbed feet and a tail fan.
- **Surfboard** — a bevelled extruded outline with a stripe and fin. The whole
  surfer group is oriented to the wave normal and banked into the turn.
- **Water spray** — a recycled pool of soft point particles thrown from the
  board's tail.
- **Sky** — a gradient dome with a sun glow shader and drifting cloud clusters,
  plus a foam disc on the water and a cinematic follow camera.

## Files

| File        | Purpose                                        |
| ----------- | ---------------------------------------------- |
| `index.html`| Entry point and page chrome                    |
| `main.js`   | Scene assembly, surfer path and render loop    |
| `waves.js`  | Shared wave model (CPU + generated GLSL)       |
| `ocean.js`  | Displaced water mesh                           |
| `pelican.js`| Procedural pelican and surfboard               |
| `sky.js`    | Sky dome, sun glow and clouds                  |
| `spray.js`  | Particle spray system                          |

## Build check

```bash
esbuild main.js --bundle --format=esm --outfile=/dev/null
```
