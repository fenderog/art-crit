# Surfing Pelican

An animated, non-interactive 3D scene of a pelican surfing a curling ocean
wave, built with [Three.js](https://threejs.org/).

## Run it

Open `index.html` in a browser (the scene loads `main.js` as an ES module, so
serve the folder over HTTP if your browser blocks module loading from
`file://`, e.g. `npx serve .`).

## What you'll see

- A stylized pelican built entirely from Three.js primitives (spheres, cones,
  capsules), balancing on a coral-red surfboard with flapping wings, a
  wobbling throat pouch, and a bobbing head.
- A big curling breaker (an extruded wave silhouette) with animated foam
  blobs along its lip and a foamy wash at its base.
- A procedurally animated ocean — vertex-displaced plane with rolling swells
  and a ridge that swells up into the breaking wave.
- Board spray particles, drifting clouds, circling gulls, a low sun, and a
  slow cinematic camera orbit.

## Development

```
npm install   # installs three
```

The page is packaged into a single self-contained `index.html` with esbuild;
all assets are generated in code (no external URLs, no storage APIs).
