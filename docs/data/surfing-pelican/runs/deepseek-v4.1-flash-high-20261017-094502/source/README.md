# Surfing Pelican

An animated, non-interactive Three.js scene of a pelican riding a surfboard
across an endless, procedurally generated ocean.

Open `index.html` and watch. There are no controls, no network requests and no
stored state — everything is generated in code at runtime.

## What's in the scene

- **Ocean** — a GPU-displaced plane. The vertex shader sums several travelling
  sine waves to build the swell, derives the surface normal from finite
  differences, and the fragment shader adds fresnel sky reflection, a sun
  glint, translucent crests and foam. The plane is panned in the shader so the
  water never runs out.
- **Pelican** — modelled entirely from primitives (sphere, cone, tube,
  extruded wing and board shapes). It samples the exact same wave function as
  the water, so it sits on the surface, tilts with the local slope, rolls as it
  carves, and its head, body and wings idle with small procedural motions.
- **Spray** — a GPU point system that throws droplets off the tail of the board.
- **Sky & life** — a painted equirectangular sky is used for the background and,
  via `PMREMGenerator`, for image-based lighting. Billboard clouds drift past
  and a handful of distant gulls circle overhead.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | Page shell, canvas and inline styles. |
| `main.js` | Renderer, camera, animation loop and scene assembly. |
| `waves.js` | Shared wave math (JS) and its GLSL twin. |
| `ocean.js` | Procedural water mesh and shaders. |
| `pelican.js` | The bird, surfboard and materials. |
| `spray.js` | Particle spray. |
| `environment.js` | Sky, lighting, clouds and birds. |

## Running

The source uses bare ESM imports, so serve the folder over HTTP (module
scripts do not load from `file://`):

```sh
npx serve .
# or
python3 -m http.server
```

The page is designed to be bundled into a single self-contained HTML file with
esbuild. The bundle entry is `main.js`:

```sh
esbuild main.js --bundle --format=esm --outfile=dist/main.js
```
