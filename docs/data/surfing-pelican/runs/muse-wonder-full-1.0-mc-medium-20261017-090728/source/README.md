# Surfing Pelican

An animated, non-interactive Three.js scene: a pelican in a sideways surf
stance endlessly carving across animated ocean swell, with a curling barrel
wave, spray off the board's tail, drifting clouds and foam, distant gulls,
and a palm island. The camera moves on its own slow arc — there are no
controls, buttons, or pointer/keyboard input.

The pelican (S-neck, long orange beak with a wobbling pouch, outstretched
wings, webbed feet) and its striped surfboard are built entirely from
Three.js geometry in code; the board deck and spray sprite use canvas
textures generated at runtime. No external assets are loaded.

## Files

- `index.html` — entry point
- `main.js` — scene, lighting, camera choreography, animation loop
- `pelican.js` — pelican and surfboard construction
- `ocean.js` — shared wave-height field, ocean mesh, barrel wave

## Check bundling

```sh
npm install
esbuild main.js --bundle --format=esm --outfile=/dev/null
```

The page is packaged afterwards into one self-contained `index.html`
with esbuild, so the bare `three` import is resolved at packaging time
rather than in the browser.

Motion is reduced automatically when the browser reports
`prefers-reduced-motion`.
