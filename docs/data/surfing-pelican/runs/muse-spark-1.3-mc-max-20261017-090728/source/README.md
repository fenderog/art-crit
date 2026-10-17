# Surfing Pelican

An animated, non-interactive 3D vignette: a stylized pelican riding a surfboard
on a rolling swell in front of a curling breaker. Built with Three.js, all
geometry generated procedurally in code (no downloaded assets).

## Files

- `index.html` — entry point, loads `main.js` as an ES module
- `main.js` — renderer, camera, lights, animation loop
- `pelican.js` — pelican + surfboard model and its animation
- `ocean.js` — swell, breaker wave, foam, wake, shared wave function
- `sky.js` — gradient sky shader, clouds, gulls

## Run

Install dependencies first (`npm install`), then open the packaged single-file
build (produced from these sources with esbuild) in any browser. No server,
network, or storage is used.

## Packaging check

`esbuild main.js --bundle --format=esm --outfile=/dev/null` must succeed.
