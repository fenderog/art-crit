# Surfing Pelican

Animated, non-interactive 3D scene built with three.js.

- `index.html` — entry point, loads `main.js` as an ES module.
- `main.js` — whole scene: procedural low-poly pelican on a surfboard,
  animated ocean swell, curling wave with foam crest, wake, spray,
  drifting clouds, and circling gulls. No user input; camera is fixed
  and everything animates from the render clock.

Run locally with any static server, e.g. `npx serve .`, then open the page.
