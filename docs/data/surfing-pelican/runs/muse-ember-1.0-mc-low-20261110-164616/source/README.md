# Surfing Pelican

An animated, non-interactive Three.js scene: a pelican carving a turquoise
wave on a coral surfboard, with spray, foam, gulls, clouds and a palm island.

## Files

- `index.html` — entry point, loads `main.js` as an ES module.
- `main.js` — everything: ocean, board, pelican, sky, particles, animation.

Run: serve the folder (`npx vite` or `python3 -m http.server`) and open
`index.html`. No CDN, no build step required for viewing; `three` is resolved
from `node_modules` via esbuild for packaging (`esbuild main.js --bundle
--format=esm --outfile=/dev/null`).

## Motion

The camera slowly orbits the surfer. The ocean heaves, the pelican bobs,
leans into his carve and flaps; spray trails the board. Animation eases
automatically for `prefers-reduced-motion`.
