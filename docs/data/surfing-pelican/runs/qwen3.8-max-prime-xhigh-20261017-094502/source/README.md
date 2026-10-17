# Dawn Patrol — a surfing pelican

An animated, non-interactive WebGL short film: a brown pelican trim-surfs a
longboard across a slow-motion dawn swell while a virtual camera flies a
never-repeating orbit around it. There are no controls — the page is a film.

## Run

```sh
npm install          # three.js
# dev: serve the folder and open index.html, or bundle once:
npx esbuild main.js --bundle --format=esm --outfile=bundle.js
```

`index.html` loads `main.js` as an ES module; everything (geometry, textures,
foam, sky) is generated in code — no external assets, no network, no storage.

## What's in the frame

- **The sea** is one analytic height field (six directional gravity-wave
  components in slow motion). The *same* parameter list is evaluated on the CPU
  — so the board, wake and camera sit exactly on the rendered surface — and
  code-generated into GLSL for displacement, analytic normals, capillary chop,
  fresnel sky reflection, backlit translucency, sun glitter and gated
  whitecaps. The mesh is a polar disc: 0.4-unit rings under the surfer widening
  to 50-unit rings at a 1.4 km horizon, so one seamless mesh covers everything.
- **The pelican** is built from lathes, tapered tubes and vertex-coloured wing
  grids (white coverts → grey → black primaries), with a gular pouch that gapes
  and jiggles, stabilised head gaze, balance-correcting wings with flap bursts,
  webbed feet planted in a surf stance, and a generated feather bump map.
- **The board** is an extruded outline with rocker, foil taper, vertex-painted
  livery, three fins, a traction pad and a leash cuffed to the back ankle. It
  rides a plane fitted to four wave probes, banks into carves and pumps with
  the swell.
- **Foam**: a GPU point-spray system (tail wash, rail fans through carves,
  nose-slam bursts), a trail ribbon that re-lies on the moving surface each
  frame, and a contact shadow that conforms to the local wave normal.
- **Sky & light**: procedural gradient dome with two masked cloud decks and a
  low sun; ACES tone mapping; gulls wheeling in the distance; a cinematic
  camera driven by layered incommensurate sines plus handheld drift.

## Files

| file | role |
| --- | --- |
| `main.js` | bootstrap: renderer, lights, world assembly, frame loop |
| `src/waves.js` | the shared wave field (CPU + generated GLSL) |
| `src/ocean.js` | polar sea mesh + water shader |
| `src/sky.js` | sky dome, sun, clouds |
| `src/pelican.js` | bird rig, plumage, animation |
| `src/board.js` | surfboard, fins, pad, leash |
| `src/surfer.js` | ride physics: path, wave-plane fit, carve bank, foam cues |
| `src/foam.js` | spray particles, wake ribbon, contact shadow, mist |
| `src/camera.js` | cinematic orbit rig |
| `src/gulls.js` | background flock |
| `src/textures.js` | canvas-generated bump/dot/shadow/speckle textures |
| `src/util.js`, `src/glsl-common.js` | math + shared GLSL noise |
