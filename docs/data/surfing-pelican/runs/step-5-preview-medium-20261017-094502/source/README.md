# Surfing Pelican 🏄‍♂️🌊

An animated, **non-interactive** scene: a pelican in full surfing stance carving a
golden-hour swell, built with [three.js](https://threejs.org) and ES modules.

Just open `index.html` (or serve the folder) — there is nothing to click, the
pelican rides the whole loop by itself.

## Run it

```bash
npm install   # installs three
npx serve .   # or: python3 -m http.server 8000
```

Open `index.html` from that server. (`src`-form pages import `three` by name, so a
server is needed here; the packaged, bundled version of the page runs from
`file://` just fine.)

## How it is put together

| file        | what lives there                                                     |
| ----------- | -------------------------------------------------------------------- |
| `index.html`| markup, the vignette/caption styling, and the module entry           |
| `main.js`   | the whole scene (see below)                                          |
| `README.md` | this file                                                            |

No import maps, no CDN, no external assets — every texture is drawn on a
`<canvas>` in code.

### The wave field

`main.js` defines one wave field (a sum of three directional sine waves) and
reuses it in two places:

* **JavaScript** — `waveHeight()` / `waveNormal()` place the pelican, its board,
  the spray emitters and the sailboat exactly on the moving surface.
* **GLSL** — `waveGLSL()` emits the very same constants as shader code, so the
  ocean mesh and the physics agree to the millimetre.

The ocean is a 760 × 760 grid whose vertices are displaced in the vertex shader
(normals come from central differences of the same field). It stays centred on
the camera and slides in grid-sized steps, which keeps the surface continuous
while the geometry never has to be rebuilt.

The water shader mixes a depth gradient, a fresnel sky reflection (the shared
`skyColor()` function is also used by the sky dome), sun glitter, animated foam
on the crests and whitecaps on steep faces, then fades into exponential-squared
fog that matches the horizon haze.

### The pelican

Assembled from primitives (spheres, tubes, cones and two extruded plan-forms —
one for the surfboard outline, one for the wings) into a small hierarchy:

```
ride        — world placement: wave height, board orientation, bank into turns
 └ body     — surf stance, bob, crouch, lean
    ├ torso / belly / tail
    ├ neck (S-curve) → head → beak, pouch, eyes
    ├ wingL / wingR — pivots that flap and adjust while carving
    └ legs + webbed feet on the deck
```

The board orientation is built from an orthonormal frame (forward, wave normal,
side) each frame, tilted toward the inside of the turn by a bank angle derived
from the closed-form curvature of the oval circuit — so it leans into the corners
instead of sliding around them.

Around it: a camera that swings in from a wide establishing shot and then
follows with damping and a gentle handheld float, a point-sprite spray system
(rooster tail off the tail, rail spray while carving), seagulls orbiting on
their own schedules and a small sailboat bobbing far out on the swell.

## Packaging

The page is bundled into a single self-contained `index.html` with esbuild:

```bash
esbuild main.js --bundle --format=esm --outfile=bundle.js
```

Everything is either bundled or generated in code, so the result runs offline in
a sandboxed iframe with no network, storage or cookies.
