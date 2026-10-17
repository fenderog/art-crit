# Surfing Pelican

An animated, non-interactive Three.js scene: a pelican in sunglasses (with a fish in its pouch) carves back and forth on a curling wave, balancing with flapping wings amid spray, foam, gulls, and drifting clouds. The camera drifts cinematically on its own — there are no controls.

## Run

```sh
npm install
npx serve .   # or any static server; open index.html
```

Entry point is `index.html`, which loads `main.js` as an ES module importing `three`. Everything is procedural — no external assets.
