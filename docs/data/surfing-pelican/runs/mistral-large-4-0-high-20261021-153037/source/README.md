# Surfing Pelican

An animated, **non-interactive** WebGL scene: a pelican built entirely
from Three.js primitives rides a surfboard across a procedurally
displaced ocean. There are no controls and no input handling — the
pelican flaps, bobs, and carves on its own while the camera drifts.

## Files

- `index.html` — entry point; loads `main.js` as an ES module.
- `main.js` — the whole scene:
  - gradient sky sphere, sun with glow sprite, drifting clouds, distant birds
  - ocean: high-segment plane displaced by a custom shader (wave height,
    analytic normals, sun glint, crest foam, horizon haze)
  - surfboard: extruded outline with a deck stripe
  - pelican: body, neck, head, long beak + pouch, eyes, flapping wings
    with dark tips, tail and webbed feet
  - the rig follows the same wave function in JS that drives the shader,
    so the board sits on the surface and tilts with the slope
  - additive spray particles off the board's nose
- `package.json` / `node_modules` — only dependency is `three`.

## Develop

```sh
npm install
npx serve .        # or: python3 -m http.server
```

ES modules need to be served over HTTP (opening `index.html` via
`file://` won't work in the dev setup).

## Bundle check

```sh
npx esbuild main.js --bundle --format=esm --outfile=/dev/null
```

The scene is fully self-contained: all textures are generated on
canvases in code, and there are no network requests or storage usage,
so the packaged page runs offline in a sandboxed iframe.
