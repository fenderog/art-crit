# Surfing Pelican 🏄🐦

An animated, non-interactive 3D scene built with three.js: a pelican balances
on a surfboard, riding a procedurally animated swell.

## What's in the scene
- **Ocean**: a plane grid whose vertices are displaced each frame by layered
  sine waves, with flat shading for a stylized low-poly look.
- **Pelican**: built entirely from primitives — egg-shaped body, long spear
  beak with a swinging pouch, outstretched wings that make small balance
  corrections, and webbed orange legs planted on the board.
- **Surfboard**: extruded bezier outline with a red stripe and fin; it tilts
  to match the local wave slope and traces a lazy path across the swell.
- **Atmosphere**: drifting puff clouds, a warm sun, and a particle wake of
  spray behind the board.
- **Camera**: slowly orbits the surfer automatically (no interaction needed).

## Files
- `index.html` — entry point
- `main.js` — scene, models and animation loop (ES module)
- `style.css` — full-screen canvas + title overlay

## Run
Any static server works, e.g. `npx serve .`, then open the page.
Requires the `three` npm package (`npm install`).
