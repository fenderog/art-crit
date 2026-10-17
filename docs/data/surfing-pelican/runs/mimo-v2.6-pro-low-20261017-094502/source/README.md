# Surfing Pelican

An animated, non-interactive three.js scene: a pelican rides a surfboard across an
endless Gerstner-wave ocean under a warm afternoon sun, with spray, foam, circling
gulls and a slow drifting camera. No input required — just watch.

## Run

```bash
npm install
# serve this directory with any static file server, e.g.
python3 -m http.server 8000
```

Then open `http://localhost:8000/` in a browser.

## Package

```bash
esbuild main.js --bundle --format=esm --outfile=bundle.js
```

Everything is generated in code (procedural geometry + canvas textures), so the
bundled page is fully self-contained and works offline.

## Files

| File        | Purpose                                                                    |
| ----------- | -------------------------------------------------------------------------- |
| `index.html`| Page shell, inline styles, loads `main.js` as an ES module                 |
| `main.js`   | Scene setup, lights, camera orbit, animation loop, surfer placement        |
| `waves.js`  | Shared Gerstner wave field — generates both the GLSL and the JS sampler    |
| `ocean.js`  | Sky dome, sun glow, wave-shaded ocean, spray particles, contact shadow     |
| `pelican.js`| Procedural pelican (body, swept neck, beak + pouch, wings, feet) and board || `birds.js`  | Distant flock of gulls circling on the horizon                             |

## Notes

- The ocean surface is displaced in the vertex shader from the wave list in
  `waves.js`; the same list is evaluated in JavaScript every frame so the
  pelican, board, spray and contact shadow ride the exact same water surface,
  including its slope.
- Shading is hand written GLSL (depth tint, fresnel sky reflection, sun glints,
  crest foam broken up with value noise) and uses three.js' fog chunks so the
  ocean dissolves into the sky at the horizon.
- The pelican is entirely procedural geometry: lathed/tapered boxes, a tube swept
  along a Catmull-Rom curve for the neck, and extruded bezier shapes for the
  wings, feathers and fin.