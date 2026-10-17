# Surfing Pelican 🏄🐦

A fully automatic (non-interactive) animated 3D scene built with
[three.js](https://threejs.org/) and plain ES modules.

## What you'll see

- A stylized **pelican** standing on a striped **surfboard**, riding an
  animated ocean.
- The board tilts and carves following the **real wave-height field** used to
  displace the ocean mesh, so it stays glued to the surface.
- The pelican flaps its wings for balance, swivels its head, and its throat
  pouch wobbles with the motion.
- Water **spray** kicks off the tail of the board, **foam** streaks drift by,
  **clouds** glide overhead, and distant **gulls** circle and flap.
- A slow **cinematic camera orbit** shows the scene from every angle — no
  interaction required.

## Files

| File          | Purpose                                        |
| ------------- | ---------------------------------------------- |
| `index.html`  | Entry point; loads `main.js` as an ES module   |
| `main.js`     | All scene construction and animation logic     |
| `README.md`   | This file                                      |

## Running locally

```sh
npm install three
npx serve .   # or any static file server, then open index.html
```

## Packaging check

```sh
npx esbuild main.js --bundle --format=esm --outfile=/dev/null
```

No network requests, no storage APIs — safe for sandboxed offline iframes.
