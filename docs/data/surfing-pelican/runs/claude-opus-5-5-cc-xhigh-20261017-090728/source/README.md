# Surfing Pelican

A non-interactive three.js animation: a brown pelican rides the barrel of a
breaking wave at sunset, wings out for balance.

Open `index.html` through any bundler or dev server that resolves bare imports
(for example `npx esbuild main.js --bundle --format=esm --servedir=. --outdir=.
--serve`). The only dependency is `three`. Everything else, including textures,
is generated in code, so the page needs no network access and no storage.

## What's on screen

- **Breaking wave** (`src/wave.js`, `src/ocean.js`): one continuous ocean mesh.
  Near the break, its rows follow a Catmull-Rom wave profile that morphs along the
  line from an unbroken shoulder, through the pocket and a full overhanging tube,
  into collapsing whitewater. The scene sits in the frame that travels with the
  surfer, so the wave holds still while the water, foam and chop stream past.
  The shader handles ripple normals, Fresnel sky reflection, light glowing
  through the thin lip, the wave hiding the sky in reflections of the water in
  front of it, procedural foam (lip, whitewater, marbled face lines, scum lines)
  and haze towards the horizon.
- **Pelican** (`src/pelican.js`): lofted body, neck and bill with a sagging gular
  pouch. Wings are bone chains covered in about 60 individual feathers each. The
  pelican balances with its wings, flaps now and then, keeps its head steady in
  world space, glances back at the tube, blinks, and its pouch jiggles. Its legs
  use two-bone IK down to webbed feet planted on the board.
- **Surfing** (`src/surfer.js`): the board follows the wave face, carves up and
  down, and banks into turns. The pelican leans out with the board whenever the
  tube wall gets close to its head.
- **Effects** (`src/spray.js`, `src/trail.js`): rail spray, mist blown off the
  crest by the offshore wind, drops falling from the lip, whitewater bursts, and
  a foamy carve line.
- **Sky** (`src/sky.js`, `src/shaders.js`): a procedural sunset with clouds. The
  same function lights the scene via PMREM and feeds the water's reflections.
  There is also a hazy headland, and a line of pelicans gliding past
  (`src/flock.js`).
- **Camera** (`src/camera.js`): a loop of four shots (front three-quarter, down
  the line into the tube, low and close, wide) with slow glides between them.

Post-processing is bloom, ACES tone mapping and a light vignette. The render
resolution adapts automatically to keep the frame rate smooth.
