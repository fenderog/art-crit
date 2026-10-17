# Surfing Pelican

An animated, non-interactive 3D scene of a pelican surfing an ocean wave, built with [Three.js](https://threejs.org/).

## Features

- A pelican modeled from primitives (body, neck, head, beak with pouch, flapping wings, tail, webbed feet) riding an orange surfboard.
- A rolling, curling wave crest the rider carves back and forth across, plus a large open ocean plane with animated swells.
- White foam particles spraying from the wave lip, drifting clouds, sun disc, soft shadows, fog, and a gently swaying camera.
- Fully procedural: no external assets, no network requests, no storage — runs offline.

## Run

```
npm install
npx serve .   # or any static file server
```

Open `index.html` via the server (ES modules require HTTP).

## Package

```
esbuild main.js --bundle --format=esm --outfile=/dev/null
```
