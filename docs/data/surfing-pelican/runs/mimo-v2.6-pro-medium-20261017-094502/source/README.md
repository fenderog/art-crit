# Surfing Pelican

An animated, non-interactive three.js scene: a stylised pelican rides a surfboard
down an endless ocean swell — flapping, bobbing and kicking up spray while the
camera drifts along with it.

Open `index.html` (served over HTTP, e.g. `python3 -m http.server`) and just watch.

## What's inside

| File       | Contents                                                                 |
| ---------- | ------------------------------------------------------------------------ |
| `index.html` | Page shell, canvas, CSS caption/vignette, loads `main.js` as an ES module |
| `main.js`    | The whole scene: ocean, sky, clouds, birds, pelican + board, spray, camera |

## How it works

- **Ocean** — a high-resolution plane whose vertices are displaced in the vertex
  shader by a six-component wave field (deep-water dispersion phase speeds).
  The exact same wave sum is compiled into both GLSL and JS, so the pelican and
  its spray sit *on* the moving surface. Foam is generated procedurally from the
  wave crest height plus value noise, and the surface receives shadows.
- **Pelican** — built entirely from primitives (spheres, cones, boxes, a tube
  neck), with pivot groups on the wings for flapping, a bobbing head and a
  gently inflating throat pouch. The board is oriented to the local wave slope.
- **Spray** — a pooled particle system (`THREE.Points` + a tiny shader) thrown
  off the tail of the board, with gravity, drag and fading alpha.
- **Sky / clouds / birds** — gradient + sun-glow sky dome shader, canvas-drawn
  cloud sprites, and a few distant two-wing birds circling the horizon.
- **Camera** — a slow cinematic sway around the rider; no user input anywhere.

Everything (textures included) is generated in code — no external assets, no
network access, no storage.

## Build

```sh
npm install        # pulls in `three`
esbuild main.js --bundle --format=esm --outfile=/dev/null   # packaging check
```