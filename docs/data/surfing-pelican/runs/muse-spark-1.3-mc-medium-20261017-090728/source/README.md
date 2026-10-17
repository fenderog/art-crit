# Surfing Pelican

An animated, **non-interactive** surfing pelican built with HTML + Three.js.

- Entry point: [`index.html`](index.html) loads [`main.js`](main.js) as a JavaScript ES module.
- `main.js` imports `three` by name (installed via `npm install three`). No CDN URLs, no import maps.
- Everything is procedural: the pelican (body, head, beak + pouch, wings, tail, feet),
  surfboard, ocean waves, breaking swell, sea spray, sun, clouds, and islands are all
  generated in code. No external assets, so the page runs offline in a sandboxed iframe
  (no network requests, no localStorage/cookies).
- Animation (automatic, no user input): the pelican carves across the wave, bobs,
  flaps its wings for balance, wobbles its beak pouch, and kicks up spray while the
  camera drifts slowly.

## Run

Use any static server from this directory, e.g. `npx serve .`, then open the page.

## Package check

`esbuild main.js --bundle --format=esm --outfile=/dev/null` must succeed.
