# Surfing Pelican

A non-interactive Three.js animation of a pelican riding a rolling ocean swell on a surfboard.

- `index.html` – entry point, loads `main.js` as an ES module.
- `main.js` – the whole scene: a CPU-animated ocean mesh (peaked swell + chop, with foam coloured
  crests), a procedurally built pelican (S-curved neck, pouched beak, balancing wings), a surfboard
  that follows the wave face and carves up and down it, spray particles, sky dome, clouds, distant
  gulls and a slowly orbiting follow camera.

Everything is generated in code; no external assets. Run with any static server after `npm install`
(or bundle with esbuild: `esbuild main.js --bundle --format=esm`).
