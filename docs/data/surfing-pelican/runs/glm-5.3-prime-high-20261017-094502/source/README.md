# Surfing Pelican

An animated, non-interactive 3D scene built with [Three.js](https://threejs.org/):
a low-poly pelican carving rolling ocean swells on a coral surfboard.

## Run

Open `index.html` (or serve the directory) in a browser — everything is
generated in code, there are no external assets.

## What's in the scene

- **Stylized ocean** — a large displaced plane driven by a sum of travelling
  sine swells; vertex colors tint the wave crests with foam.
- **Pelican** — built from primitives (S-curved neck tube, pouch, extruded
  flapping wings with dark tips) doing a little body-language dance: bobbing,
  wing balance, jiggling pouch, turning head.
- **Surfboard** — extruded ellipse deck with stripe and back fin.
- **Ride** — the surfer carves a sinusoidal path across the wave face; the
  board pitches with the wave slope, banks into turns, and slices spray
  particles (an instanced-mesh particle system) off the nose and tail.
- **Ambience** — gradient sky, sun, drifting clouds, and circling gulls.
- **Camera** — smoothly follows the action; fully automatic, no interaction.

## Files

- `index.html` — entry point, loads the module.
- `main.js` — all scene code (ES module).
