# Surfing Pelican

An animated, non-interactive Three.js scene: a pelican built from primitives
rides a curling wave on a striped surfboard, carving up and down the face with
wings out for balance, spray off the tail, and a jiggling beak pouch. The
camera is fixed (faint sway only) — there are no controls.

## Run

```sh
npm install
npx serve .
```

Then open the printed local URL in a browser. Entry point: `index.html`,
which loads `main.js` as an ES module (`import * as THREE from "three"`).

## Check packaging

```sh
npx esbuild main.js --bundle --format=esm --outfile=/dev/null
```

All textures are generated in code; the page makes no network requests and
uses no storage, so it runs offline once bundled.
