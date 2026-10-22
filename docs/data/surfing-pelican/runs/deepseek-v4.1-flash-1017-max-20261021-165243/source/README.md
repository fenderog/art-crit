# The Surfing Pelican

A small, fully procedural golden-hour scene: a sunglasses-wearing pelican rides a coral surfboard across a warm Pacific swell. Everything — the bird, board, water, sky, foam, flower, and textures — is generated in code with three.js. No external images, fonts, models, or network requests are used.

## Run / bundle

The page is authored as ES modules and imports `three` by package name. The delivery step bundles `main.js` (and `styles.css` referenced by `index.html`) into a single self-contained `index.html`.

To verify the JavaScript bundle:

```sh
npm install
npx esbuild main.js --bundle --format=esm --outfile=/dev/null
```

To preview the unbundled source locally, bundle it to a temporary module and point the page at that module, or use the packaged page supplied by the delivery step.

## Interaction

The pelican surfs on its own — no input is required. Move the pointer to subtly look around, or click / press Space to kick up a larger splash. A little flying fish occasionally leaps beside the board.

## Files

- `index.html` — page shell and editorial overlay
- `main.js` — three.js scene, character rig, ocean shader, animation, interactions
- `styles.css` — responsive poster typography and interface
