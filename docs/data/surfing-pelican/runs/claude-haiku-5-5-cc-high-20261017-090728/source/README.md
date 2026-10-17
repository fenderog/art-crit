# Surfing Pelican

A non-interactive three.js scene: a pelican rides a rolling swell on a coral surfboard. Everything is generated in code (no models, textures or files are loaded), and the page only plays; there is no input handling.

## Files

- `index.html`: entry point. Loads `main.js` as an ES module.
- `main.js`: renderer, sky, lighting, camera and the animation loop.
- `ocean.js`: the static swell the board rides, the moving ripples, and the animated water mesh.
- `surfboard.js`: the board geometry and the code that lays it on the wave.
- `pelican.js`: the procedural pelican, with a swaying upper body and flapping wings.
- `spray.js`: droplets thrown off the tail and rails.

## Running

Install dependencies with `npm install`. `index.html` is the entry point. esbuild bundles its script, and everything that script imports (including `three`), into one self-contained page that runs offline.

To check that the JavaScript bundles:

```sh
esbuild main.js --bundle --format=esm --outfile=/dev/null
```
