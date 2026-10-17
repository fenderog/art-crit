# Surfing Pelican

An animated, non-interactive Three.js scene: a pelican balances on a yellow surfboard, carving across a curling wave at golden hour — flapping for balance, bobbing its head, trailing spray, with gulls, clouds, and a palm island in the distance. The camera drifts cinematically on its own; there are no controls.

## Run

```bash
npm install
npx serve .        # or any static server
```

Then open the served `index.html` in a browser. The entry point is [index.html](index.html), which loads [main.js](main.js) as an ES module importing `three` from npm.

## Check packaging

```bash
npx esbuild main.js --bundle --format=esm --outfile=/dev/null
```
