# Surfing Pelican

A non-interactive Three.js scene. A brown pelican rides the face of a peeling wave while the camera follows. Nothing on the page is clickable.

## Run

```bash
npm install
```

`index.html` loads `main.js` as an ES module. That module imports `three` by package name. The page is meant to be bundled (`esbuild main.js --bundle --format=esm`) so the bare import resolves, including for offline viewing. It does not use the network or browser storage.
