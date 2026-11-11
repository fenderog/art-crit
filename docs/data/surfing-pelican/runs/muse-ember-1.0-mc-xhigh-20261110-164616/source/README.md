# Surfing Pelican — Animated 3D

A non-interactive, animated Three.js scene: *Peleyo the pelican* surfs a big curling wave on a teal board, with spray, foam, gulls and drifting clouds. The camera sways on its own in front of the wave — you just watch.

## Run

For a quick local preview (bundled, so the bare `three` import resolves in the browser without CDN or import maps):

```bash
npm install
npx esbuild main.js --bundle --format=esm --outfile=bundle.js
# serve the folder with any static server, e.g. `npx serve .`
# open view.html (same as index.html but loading bundle.js) or the served index.html after bundling
```

Or use the included screenshot helper, which bundles and serves automatically:

```bash
node screenshot.mjs
# writes shot-desktop.jpg, shot-desktop-2.jpg and leaves the server on :5173
```

The deliverable entry point is `index.html` + `main.js` (see below); `screenshot.mjs`, `shot*.jpg` and the generated `bundle.js`/`view.html` are for verification only.

## Files

- `index.html` — entry point, HUD overlay, loads `main.js` as an ES module (`<script type="module" src="main.js">`)
- `main.js` — all Three.js code, no CDN, no import maps. Imports `three` and `three/examples/jsm/environments/RoomEnvironment.js` by bare specifier.
- `package.json` — `three`, dev deps `esbuild`, `puppeteer-core`
- `screenshot.mjs` — bundles with esbuild, serves on `127.0.0.1:5173`, screenshots in headless Chrome as `.jpg`
- `shot-desktop.jpg`, `shot-desktop-2.jpg` — verified captures (1280×800, headless Chrome + SwiftShader)

## Bundle check

```bash
npx esbuild main.js --bundle --format=esm --outfile=/dev/null
# must succeed — the packaged page is a single self-contained index.html (esbuild inlines everything)
# runs offline in a sandboxed iframe: no network requests, no localStorage/cookies/storage
```

## What you see

- Pelican built entirely from code primitives (`SphereGeometry`, `TubeGeometry`, `ExtrudeGeometry` with beveled shapes for wings/beak/tail/feet/board) — white body, orange beak + pouch, black wingtips, crest, webbed feet on the deck.
- Curling wave wall (`PlaneGeometry` bent forward at the crest, 30×6, with taper along length) + animated ocean plane (vertex swell + canvas foam speckles), crest foam tube, spray `Points` with radial-gradient canvas sprite, drifting clouds (merged spheres), circling gulls (two-plane flappers), sun glow sprite, sky-dome gradient shader, soft shadows, `ACESFilmicToneMapping`.
- Animation loop only: rider carves up/down the face (`rideZ = sin(phase)*7.6`), wings flare for balance, head/neck bob, pouch bounce, board tilt/trim, ocean undulates, spray respawns, clouds/gulls drift, camera sways on a front arc (calmer under `prefers-reduced-motion`).

## Notes

- Non-interactive: no OrbitControls, no pointer/key input besides resize. Canvas is full-viewport and responsive.
- All textures are `CanvasTexture` generated in code; nothing is loaded by URL. Verified: no `localStorage`, no `fetch`/`XMLHttpRequest`, no `http*://` URLs in `main.js`/`index.html`.
- Verified in headless Chrome  (1280×800 and 390×844 desktop/phone viewports via `screenshot.mjs`): canvas present, `requestAnimationFrame` loop running, console only shows the `THREE.Clock` deprecation warning (no errors).
