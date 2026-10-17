# Surfing Pelican

An animated (non-interactive) 3D scene built with [three.js]: a pelican
carving S-turns on a red surfboard across an endless ocean swell.

- `index.html` – entry point
- `main.js` – everything: procedural pelican, surfboard, vertex-displaced
  waves, foam and spray particles, gradient sky

## Run

Open `index.html` in a browser (e.g. `npx serve .`), or package it:

```
esbuild main.js --bundle --format=esm --outfile=/dev/null
```

No network requests, no storage – fully offline once bundled.

[three.js]: https://threejs.org/
