# Surfing Pelican

A non-interactive, animated scene of a pelican riding a surfboard down a travelling swell, built with three.js.

## Files

- `index.html` – page shell and styles; loads `main.js` as an ES module.
- `main.js` – renderer, camera, lighting, sky and the animation loop.
- `ocean.js` – the swell: a sum of travelling sine waves that displaces the water mesh.
- `surfer.js` – the surfboard, and the logic that pitches and rolls it to match the wave under it.
- `pelican.js` – the pelican, built from primitives, with flapping wings and a gentle sway.

## Running

```sh
npm install
```

The scene starts on load and runs until the page is closed. There is no input handling.

To check that the modules bundle:

```sh
npx esbuild main.js --bundle --format=esm --outfile=/dev/null
```

The page uses no network requests and no browser storage, so it can be packaged into a single `index.html` and run offline.
