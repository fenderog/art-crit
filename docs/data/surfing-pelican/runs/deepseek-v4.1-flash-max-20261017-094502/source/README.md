# Pelican on the Longboard

An animated, non-interactive WebGL scene: a procedurally modelled pelican
riding a longboard across a living ocean at golden hour. Built with
[three.js](https://threejs.org/) and bundled as a single self-contained page.

## What you see

- **Ocean** — a displaced plane driven by five summed swell waves in a custom
  shader (analytic normals, fresnel sky reflection, sun glints, crest foam and
  distance haze). The same wave train is evaluated on the CPU so the board rides
  the exact GPU surface.
- **Pelican** — modelled entirely from primitives and a handful of extruded
  shapes: egg-shaped body, S-curve neck with tapered tube, long bill with a
  hinged pouch that opens for a breath every few seconds, webbed feet, crest
  feathers and outspread wings that gently balance on the swell.
- **Longboard** — an extruded rounded outline with deck stripe, wax patch,
  skeg, and a leash from the bird's ankle to the tail.
- **Sky** — gradient dome shader with a sun disc and haze, drifting cloud
  sprites and a few distant birds circling the horizon.
- **Spray** — a CPU particle system throwing mist off the tail, wash off the
  rails, and a fan of spray whenever the nose digs into a wave face.
- **Camera** — a slow cinematic orbit with a subtle handheld roll; no user
  input is required or accepted, the scene performs on its own.

## Files

| file | purpose |
| --- | --- |
| `index.html` | entry point, page shell and caption styling |
| `main.js` | renderer, lights, camera choreography, animation loop |
| `ocean.js` | wave train (CPU + GLSL) and the ocean mesh |
| `sky.js` | sky dome, clouds and birds |
| `surfer.js` | surfboard, pelican model and its idle animation |
| `spray.js` | particle system for spray and foam |

## Run it

```bash
npm install
npx serve .        # or any static file server
```

Then open the served page. The scene is fully offline: all geometry, shaders
and textures (canvas-generated sprites) are produced in code, there are no
network requests, and no browser storage is used.

## Bundle check

```bash
esbuild main.js --bundle --format=esm --outfile=/dev/null
```

Everything the page needs — three.js and all local modules — is pulled in from
this one entry point.
