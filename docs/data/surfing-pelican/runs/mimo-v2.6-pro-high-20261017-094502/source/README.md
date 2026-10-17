# Surfing Pelican

An animated, non-interactive 3D vignette: a pelican riding the swell on a
surfboard, built entirely with [three.js](https://threejs.org) and procedural
geometry — no models, no image assets, no network access.

Open `index.html` (served over any static server, or packaged) and watch.

## What's on screen

- **The ocean** — a large plane displaced in the vertex shader by a sum of five
  directional sine waves. The same wave field is evaluated on the CPU, so the
  surf rig floats and tilts exactly on the moving surface. The water is shaded
  with a stylised model: fresnel sky reflection, sun glitter, foam on the
  crests and a haze fade into the horizon.
- **The pelican** — assembled from primitives (sphere body, tube neck, tapered
  mandible with a hanging pouch, two-segment flapping wings, webbed feet,
  crest feathers). It flaps, sways, looks around, blinks and breathes.
- **The board** — an extruded surfboard outline with bevelled rails, a deck
  stripe, a tail pad and a fin, plus a soft contact shadow and a foamy collar
  on the water.
- **Spray & wake** — a GPU point system of foam particles thrown from the board
  nose and a scrolling foam trail behind it.
- **The world** — a gradient sky dome with a sun glow, drifting stylised clouds
  and distant flapping seabirds, lit by a warm sun with a cool fill light.

The camera drifts slowly around the scene on its own; the page needs no input.

## Project layout

| File            | Purpose                                                     |
| --------------- | ----------------------------------------------------------- |
| `index.html`    | Entry point, page chrome and the module script tag           |
| `main.js`       | Renderer, lights, camera choreography and the animation loop |
| `src/waves.js`  | Shared wave field (CPU + generated GLSL)                     |
| `src/ocean.js`  | Displaced, shaded ocean mesh                                 |
| `src/sky.js`    | Sky dome, sun glow, clouds and distant birds                 |
| `src/pelican.js`| Surfboard + pelican rig, driven by the wave field            |
| `src/effects.js` | Foam spray particles and wake trail                         |
| `src/textures.js`| Canvas-generated soft sprites and foam patches              |

## Running

```bash
npm install
npx esbuild main.js --bundle --format=esm --outfile=dist/bundle.js
```

Then serve the directory and open `index.html`. The page has no interactive
controls and no state; it simply animates.

## Packaging

Everything the page uses is imported from ES modules, so it bundles to a single
self-contained file:

```bash
esbuild main.js --bundle --format=esm --outfile=index.packaged.html
```

All textures are generated on a canvas at runtime, so the bundle works fully
offline (no network, no storage).