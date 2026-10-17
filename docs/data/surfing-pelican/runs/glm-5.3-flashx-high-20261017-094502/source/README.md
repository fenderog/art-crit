# Surfing Pelican 🌊🦩

An animated, non-interactive 3D scene built with [Three.js](https://threejs.org/).

A pelican in sunglasses rides a wave on a surfboard while the camera slowly
orbits the scene. Everything is generated procedurally in code — no external
assets.

## What's in the scene

- **Procedural ocean** — a displaced plane whose vertices follow an analytic
  sum-of-sines wave field, with flat shading for a stylized look.
- **Surfing pelican** — built entirely from primitives (spheres, cones,
  tubes). It bobs with the swell, carves the board left and right, flaps its
  wings in bursts, and occasionally squawks (the throat pouch stretches).
- **Board physics-lite** — the surfboard samples the same wave function and
  pitches/rolls to match the wave slope.
- **Splash particles** — spawned at the board's tail as it cuts through water.
- **Environment** — gradient sky dome, sun disc, drifting cloud billboards,
  warm directional light with soft shadows, and distance fog.
- **Camera** — a slow cinematic orbit that follows the pelican with a subtle
  hand-held sway.

## Running

Open `index.html` with any static server (the page uses ES modules):

```sh
npx serve .
# or
python3 -m http.server
```

The scene is non-interactive by design: just watch the pelican surf.

## Files

- `index.html` — entry point, loads the module script
- `main.js` — the whole scene: lighting, ocean, pelican, particles, animation
