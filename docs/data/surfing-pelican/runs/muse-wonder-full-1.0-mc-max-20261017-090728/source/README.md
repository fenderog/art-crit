# The Surfing Pelican

A non-interactive Three.js loop: a pelican surfs an endless, peeling wave
forever. There are no controls to learn — open the page and watch. The bird
carves from a low bottom turn to a high cutback and back, balances with its
wings (with a quick flurry at each top turn), wobbles its throat pouch, and
throws spray off the board, while the camera drifts slowly on its own.

Everything is procedural — no model, texture or font files. The pelican is
built from spheres, tubes and extrusions; the wave is a curl profile swept
along its length with vertex-colour shading; the board stripes, spray
sprites and sky are generated in code at runtime.

## Files

- `index.html` — entry point; loads `main.js` as an ES module
- `main.js` — the whole scene and animation (Three.js)
- `style.css` — fullscreen stage and overlay captions (pointer-events: none)
- `package.json` — declares the `three` dependency

## Run locally

```sh
npm install
npx vite            # any dev server that resolves the "three" import works
```

Or preview the bundled build exactly as it will be packaged:

```sh
npm install
mkdir -p dist
npx esbuild main.js --bundle --format=esm --outfile=dist/main.js
cp index.html style.css dist/
python3 -m http.server -d dist 8000   # then open http://localhost:8000
```

## Verify it bundles

```sh
npm run check-bundle
# equivalent to: esbuild main.js --bundle --format=esm --outfile=/dev/null
```

## Notes

- Non-interactive by design: no orbit controls, buttons, pointer or
  keyboard handling. Resizing is handled, and `prefers-reduced-motion`
  softens the camera drift and bobbing.
- After packaging it runs fully offline: no network requests, and no
  localStorage, cookies or other storage are used.
