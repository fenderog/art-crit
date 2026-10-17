# Surfing Pelican

An endless, non-interactive summer glide: a pelican on a surfboard, riding an
open-ocean swell into a low sunset sun, cut together like a little surf film.

No interaction, no controls — it just plays, forever.

Open `index.html` and it runs. Everything on screen is generated in code: the
swell, the sky, the sun, the clouds, the pelican, the surfboard, the spray.
There are no image, model or audio assets and no network requests.

```bash
npm install          # installs three
# then serve the folder however you like, e.g.
npx esbuild main.js --bundle --format=esm --outfile=bundle.js
```

## What you see

* **The ocean** is a "projected" polar grid that follows the surfer: rings are
  half a unit apart under the board and stretch out to 6 km at the horizon, so
  the sea never runs out but stays dense where the camera is. Displacement
  happens in the vertex shader; normals, whitecaps, sun glitter, sky reflection
  and haze are evaluated per pixel.
* **The swell** is five superimposed sine waves. The *same* table drives the
  GLSL that moves the water and the JavaScript that floats the board
  (`js/waves.js` emits the shader source), so the surfer really does ride the
  surface you see.
* **The pelican** is built from primitives and extruded shapes — no meshes are
  loaded. It pumps through the faces, banks into the turns, drags a wing in the
  foam now and then, and throws a rooster tail of spray.
* **The camera** cuts between six shots (chase, side, water-level, top, front,
  wide) on a loop, dipping to black across each cut.
* Around it: gulls wheeling overhead, low-poly islands on the haze line, and
  the sun sitting on the water.

## Files

| file | what it is |
| --- | --- |
| `index.html` | entry point: canvas, fade overlay, title |
| `main.js` | renderer, lights, scene graph, frame loop |
| `styles.css` | page chrome + title fade |
| `js/palette.js` | every colour in the scene, in one place |
| `js/waves.js` | the swell (JS + generated GLSL) |
| `js/ocean.js` | water grid + water shader |
| `js/sky.js` | sky dome, sun and clouds |
| `js/pelican.js` | the pelican, the surfboard and the riding animation |
| `js/spray.js` | particle spray |
| `js/flock.js` | gulls |
| `js/islands.js` | horizon islands (recycled as you travel) |
| `js/contact.js` | soft contact shadow on the water |
| `js/camera.js` | the self-editing shot list |
| `tools/` | dev-only helpers (see below) |

## Dev helpers

`tools/` contains optional helpers used to check the scene without a display:
they bundle `main.js` the way the shipped page is bundled, render it in
headless Chrome (software WebGL) and write screenshots. They are not needed by
the page and need two extra dev dependencies:

```bash
npm i -D puppeteer pngjs
node tools/shoot.mjs 5 15 23 31 38 47   # screenshot specific timeline points
node tools/sample.mjs 31                # print a grid of pixel values
node tools/playback.mjs                 # watch a live run for errors
```

`window.__pelican` in the console exposes `seek(seconds)` to jump to a point on
the timeline, plus the rider, camera rig and ocean uniforms for poking at.

## Notes

* Colours are authored as sRGB hex and converted to the linear working space;
  the custom shaders finish with `linearToOutputTexel()` so custom and built-in
  materials agree.
* Nothing is stored (no `localStorage`, cookies or storage APIs), no fonts,
  images or data are fetched — the page is happy in a sandboxed iframe with the
  network switched off.
