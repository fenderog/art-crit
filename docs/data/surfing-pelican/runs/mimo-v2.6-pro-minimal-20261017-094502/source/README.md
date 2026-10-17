# Pelican Surf

An animated, non-interactive WebGL scene: a pelican riding a surfboard across a
rolling ocean at golden hour. Everything plays automatically — no controls, no
input required.

Built with [three](https://threejs.org) (WebGL) and plain ES modules.

## What's in the scene

- **The pelican** — modelled entirely from primitives (spheres, cylinders, tubes
  and extruded shapes): long beak with a sagging orange pouch, S-curved neck,
  flapping wings with fanned primary feathers, webbed feet planted on the deck.
- **The surfboard** — extruded outline with a rocker bend, deck stripe, stringer
  and three fins; it banks and pitches with the wave face.
- **The ocean** — a custom GLSL shader driven by a sum of sharpened sine waves.
  The very same wave field is evaluated in JavaScript, so the board always sits
  exactly on the moving water surface. Per-pixel normals give sun sparkle;
  noise-driven foam forms on crests and steep faces.
- **Sky, sun and clouds** — gradient dome, glowing sun disc and procedural
  cumulus sprites that drift slowly.
- **Life** — spray droplets kick off the board's tail and bow, and distant gulls
  circle overhead.
- A slow, automatic camera drift keeps the framing alive.

All textures (noise, cloud, glow, droplet) are generated in code at runtime —
the page has no external assets and runs fully offline.

## Running locally

```sh
npm install
npx esbuild main.js --bundle --format=esm --outfile=dist/bundle.js
# or just serve the folder with any static server and open index.html
python3 -m http.server
```

## Packaging

The page is a plain `index.html` that loads `main.js` as an ES module. It is
bundled with esbuild:

```sh
esbuild main.js --bundle --format=esm --outfile=/dev/null   # sanity check
```

## Files

| File          | Purpose                                              |
| ------------- | ---------------------------------------------------- |
| `index.html`  | Entry point: canvas, vignette, title card            |
| `main.js`     | Renderer, lighting, camera choreography, main loop   |
| `waves.js`    | Shared wave field (JS + generated GLSL twin)         |
| `ocean.js`    | Ocean mesh and water shader                          |
| `sky.js`      | Sky dome, sun, clouds, distant gulls                 |
| `pelican.js`  | Surfboard + pelican rig and its animation            |
| `spray.js`    | Foam/spray particle system                           |
| `textures.js` | Procedural canvas textures                           |