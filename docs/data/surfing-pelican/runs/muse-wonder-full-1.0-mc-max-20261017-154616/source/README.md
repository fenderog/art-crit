# Pelican Break — a surfing pelican diorama

An animated, non-interactive 3D scene built with Three.js: a pelican rides
an endless curling wave at sunset, carving back and forth across the face
with spray sheeting off its board. There are no controls — the camera drifts
on its own, so you just sit back and watch the session.

Everything is procedural. The pelican (S-curved neck, orange beak, wobbly
throat pouch, black-tipped wings spread for balance), its coral surfboard,
the curling wave with a foamy lip, the faceted ocean, gulls, a leaping fish,
a bobbing buoy and a palm island are all generated in code — no model or
image files, no network requests, no storage.

Highlights of the loop:

- The pelican pumps down the face for speed, climbs into each turn, and
  throws in a little hop with a wing-flap and spray burst at every cutback.
- Wings counter-flap for balance, the head looks into each turn, the pouch
  wobbles a beat behind the body and squashes on landing, and the eyes blink.
- Wake foam trails across the wave face while droplets drizzle off the lip.
- `prefers-reduced-motion` is respected: the camera holds still and the
  motion calms down.

## Run locally

```sh
npm install
npm run dev
```

Then open http://127.0.0.1:5173/ in a browser.

## Check that it bundles

```sh
npx esbuild main.js --bundle --format=esm --outfile=/dev/null
```

The page entry point is `index.html`, which loads `main.js` as an ES module;
`main.js` imports `three` by package name. When packaged, the module and its
imports are bundled into a single self-contained `index.html` that runs
offline.
