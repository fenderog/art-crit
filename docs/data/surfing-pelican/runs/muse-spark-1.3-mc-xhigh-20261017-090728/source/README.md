# Surfing Pelican

An animated, **non-interactive** surfing pelican built with HTML and three.js.
A cartoon pelican stands in a tandem stance on a coral surfboard and rides a
procedural ocean swell: wings flap and counter-balance against the board's
roll, the head looks around, the throat pouch wobbles, and spray + a foamy
wake trail behind the board. Gradient sky, drifting clouds, circling distant
birds, and a tiny palm island complete the scene. The camera drifts slowly on
its own; there are no controls.

## Files

- `index.html` — entry point, loads `main.js` as an ES module
- `main.js` — renderer, scene assembly, and the animation loop
- `pelican.js` — procedural pelican + surfboard model and its animation
- `ocean.js` — animated swell mesh and the shared `waveHeight` function
- `world.js` — sky, lights, clouds, birds, spray, foam, wake, island

## Run

```sh
npm install
npx serve .        # or: python3 -m http.server 8000
# open http://localhost:3000 (or :8000)
```

Imports use the bare `three` package (no CDN, no import maps). All textures
are generated in code on a canvas; the page makes no network requests and
uses no storage, so the esbuild-packaged single file runs offline in a
sandboxed iframe.

## Packaging check

```sh
esbuild main.js --bundle --format=esm --outfile=/dev/null
```
