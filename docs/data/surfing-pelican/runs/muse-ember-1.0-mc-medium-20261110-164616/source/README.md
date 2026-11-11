# Surfing Pelican

An animated, non-interactive 3D scene of a pelican surfing a curling ocean wave, built with HTML + Three.js.

## Files

- `index.html` — entry point, loads `main.js` as an ES module
- `main.js` — all scene code (pelican, surfboard, ocean, wave, foam, spray, clouds, camera)

## Run

`index.html` imports `three` by package name, so it must be bundled before it can run in a browser:

```sh
npm install
npx esbuild main.js --bundle --format=esm --outfile=bundle.js
```

Point any static server at a page that loads `bundle.js` as a module (or use your bundler), then open it in a browser. There are no controls — the pelican carves, flaps, and the water moves on its own. Best viewed full-screen.

## Package check

```sh
npx esbuild main.js --bundle --format=esm --outfile=/dev/null
```

The page needs no network requests and uses no storage (localStorage/cookies), so it runs offline in a sandboxed iframe.
