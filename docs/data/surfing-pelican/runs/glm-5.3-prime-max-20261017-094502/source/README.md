# Surfing Pelican 🌊

An animated, non-interactive three.js scene: a low-poly pelican in a sideways surf stance
carving an endless golden-hour wave on a little red surfboard. Everything is generated in
code — no textures, no network requests, no user input. Just watch.

## What's in the scene

- **Procedural ocean** — a large plane displaced every frame by four superposed travelling
  sine swells, with per-vertex coloring: deep teal in troughs, brighter on rises, white
  foam on the crests. Flat shading gives it a faceted, stylized look.
- **The pelican** — built entirely from primitives (ellipsoid body, tube neck, extruded
  wings with dark primary feathers, big blade beak with a gulping pouch, webbed feet in
  surf stance). It bobs, crouches into carves, leans with the board, glides with
  occasional wing-flap bursts, and periodically gulps.
- **The surfboard** — extruded plan-shape with nose/tail rocker, deck stripes and a tail
  fin. It pitches and rolls to match the wave face under it and banks into turns.
- **Effects** — instanced droplet spray off the nose and carving rail (more when turning
  hard), and an expanding foam wake trailing the tail, both tracking the moving wave
  surface.
- **Surroundings** — gradient sky dome with sun disc and glow, drifting low-poly clouds,
  distant hazy islands, and circling gull silhouettes.
- **Camera** — a slow drifting orbit around the pelican that never dips below the waves.

## Files

- `index.html` — entry point, minimal styling, vignette + caption overlay
- `main.js` — scene setup, board ride physics, spray/wake spawning, camera, loop
- `water.js`, `sky.js`, `surfboard.js`, `pelican.js`, `spray.js`, `wake.js`,
  `environment.js`, `birds.js` — scene modules

## Running

```
npm install
```

The page uses ES modules with a bare `three` import, so it needs a bundler or a dev
server that resolves `node_modules` (e.g. `npx vite`). For production the page is
packaged into a single self-contained `index.html` with esbuild:

```
esbuild main.js --bundle --format=esm
```

There are no controls — the scene animates itself.
