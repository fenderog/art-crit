# 🏄 Surfing Pelican

An animated, non-interactive 3D scene of a pelican surfing an endless swell,
built with plain [three.js](https://threejs.org/) — no assets, everything is
generated in code.

## What's in the scene

- **Shader ocean** — a vertex-displaced plane driven by a table of sine waves.
  The exact same wave table is used in JavaScript to compute the water height
  and analytic surface normal, so the surfboard truly rides the swell, banking
  into slopes and weaving across the water.
- **Procedural pelican** — built from primitives: plump body, long curved neck,
  big yellow beak with a wobbling orange throat pouch, spread wings that flap
  for balance (with feathered tips), crouched orange legs on webbed feet, and a
  head that looks around.
- **Surfboard** — extruded bezier outline with a red stripe and fin.
- **Spray** — point-sprite water spray kicked up around the tail of the board.
- **Atmosphere** — gradient sky dome, sun disc with specular glint on the water,
  drifting flat-shaded clouds, distant banking seagulls, and a slow cinematic
  orbiting camera.

## Files

- `index.html` — entry point (title overlay + canvas)
- `main.js` — the whole scene (ES module, imports `three` from npm)

## Run locally

```bash
npm install
npx serve .   # or any static server, then open index.html
```

The page is fully offline-capable and uses no storage or network requests.
