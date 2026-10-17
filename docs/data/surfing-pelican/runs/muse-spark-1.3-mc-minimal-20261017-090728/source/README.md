# Surfing Pelican

An animated, non-interactive 3D vignette: a low-poly pelican surfing a stylized
ocean wave, built with Three.js. Open `index.html` (entry point, loads
`main.js` as an ES module with `style.css`).

What you see:

- Procedurally modelled pelican (spheres/cones: body, head, crest, beak +
  pouch, flapping wings, tail, legs and feet) standing on a surfboard.
- Animated ocean swell, rippling wave face, shimmering foam, spray particles,
  drifting clouds, bobbing/carving surf motion, wing flaps and head bobs.
- Fixed camera, no controls — purely a looping animation.

Notes:

- Uses the `three` npm package, imported by name (`import * as THREE from "three"`).
- No CDN URLs, no import maps, no external assets, no storage APIs — everything
  is generated in code, so the esbuild-bundled page runs offline in a sandbox.
