# Surfing Pelican 🐦‍⬛🌊

An animated, non-interactive 3D scene built with [three.js](https://threejs.org/) and plain ES modules.

## What you'll see

A stylized low-poly pelican carving lazy S-turns across an endlessly rolling
ocean, wings out for balance, pouch jiggling in the wind, with a spray of water
trailing off the tail of its surfboard. Clouds drift by, gulls circle overhead,
and the camera slowly orbits the action.

## How it's built

| File          | Purpose                                                                  |
| ------------- | ------------------------------------------------------------------------ |
| `index.html`  | Entry point, loads `main.js` as an ES module.                            |
| `main.js`     | Scene, camera, sky dome, sun, clouds, gulls, and the animation loop.     |
| `waves.js`    | Shared analytic wave function (height + slopes) so water, board and spray all agree. |
| `ocean.js`    | CPU-displaced low-poly ocean mesh with foam vertex colors on the crests. |
| `pelican.js`  | The pelican + surfboard, assembled entirely from primitive geometries.  |
| `spray.js`    | Pooled water-spray particle system behind the board.                     |

Everything is generated in code — no textures or models are loaded, so the page
runs fully offline.

## Run it

```bash
npm install
npx serve .        # or any static file server
```

Or bundle it with esbuild:

```bash
esbuild main.js --bundle --format=esm --outfile=bundle.js
```
