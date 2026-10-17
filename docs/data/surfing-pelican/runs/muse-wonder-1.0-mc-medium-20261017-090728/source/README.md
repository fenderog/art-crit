# The Surfing Pelican

An animated, non-interactive Three.js scene: a low-poly pelican — built entirely from primitives, with an S-curved tube neck, long orange beak and wobbling pouch — balances on a striped surfboard, carving back and forth along a big curling wave at golden hour.

Just open the page and watch. There are no controls: the camera drifts cinematically on its own, the pelican flaps its wings for balance, looks around, throws up a spray trail, and rides an endless break past drifting clouds, sailboats, and passing birds. Motion is slowed automatically if your system prefers reduced motion.

## Run it

```sh
npm install
npx serve .        # or any static file server, e.g. python3 -m http.server
```

Then open the served `index.html` in a browser. The entry point loads `main.js` as an ES module, which imports `three` by name from `node_modules` — no CDN or import map is used. All textures (surfboard stripes, wave stripes, sun glow, spray) are generated in code on canvases, so nothing is fetched at runtime.

## Check it packages

```sh
esbuild main.js --bundle --format=esm --outfile=/dev/null
```
