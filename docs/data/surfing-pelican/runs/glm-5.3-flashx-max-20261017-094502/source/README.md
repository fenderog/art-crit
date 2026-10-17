# Surfing Pelican 🦩🏄 (well, pelican)

An animated, non-interactive scene built with Three.js: a pelican riding a surfboard
on a stylized low-poly ocean.

## What you'll see

- A procedurally modeled pelican (body, curved neck, beak with pouch, flapping wings,
  wagging tail, orange legs) standing on a red surfboard with a fin and deck stripe.
- A CPU-displaced wave field — the board bobs, pitches, and rolls to follow the local
  wave slope, and the pelican shifts its wings for balance.
- Foam ring, wake, and spray droplets around the board.
- Gradient sky dome, sun with canvas-generated glow, drifting clouds, a palm island,
  warm directional light with soft shadows, and distance fog.

The camera slowly sways on its own — there are no controls; the scene just plays.

## Files

- `index.html` — entry point (loads `main.js` as an ES module)
- `main.js` — renderer, scene, lights, camera, animation loop
- `ocean.js` — wave function, slope, animated ocean mesh
- `rider.js` — surfboard + pelican + foam, with its own animation update
- `sky.js` — sky dome, sun/glow, clouds, palm island

## Notes

- Three.js is installed from npm and imported by name; no CDN, no import maps.
- All assets are generated in code (geometry + a canvas-generated glow texture), so the
  page bundles into a single self-contained `index.html` via esbuild and runs fully offline.
