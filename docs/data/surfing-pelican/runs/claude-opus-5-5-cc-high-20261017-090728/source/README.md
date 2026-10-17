# Surfing Pelican

An animated, non-interactive three.js scene. A brown pelican in breeding plumage rides a longboard along a peeling wave in late-afternoon light.

Open `index.html` (through a bundler or dev server that resolves the bare `three` import). It needs no input and loads no external assets.

## What's in it

- **`ocean.js`**: a custom water shader on a grid that is denser near the rider. The hero wave's lip pitches forward, and a broken whitewater section churns behind the rider. On top of that are travelling swells, procedural ripples, Fresnel sky reflections, sun glints, light glowing through the thin lip, foam (lip, whitewater, drifting lacy streaks, and the board's wake) and haze toward the horizon. The same height function is mirrored on the CPU so the board sits on the surface.
- **`pelican.js`**: the pelican, built from lofted shapes: streaky silver back, chestnut hind-neck, yellow crown, hooked orange bill and sagging pouch, layered flight feathers. It has two-bone IK legs with feet planted on the deck. It crouches and banks through turns and trims its wings for balance. It also flaps now and then, blinks, claps its bill and glances at the camera.
- **`board.js`**: a longboard with rocker, painted stripes and a fin.
- **`spray.js`**: CPU particles for rail spray in hard turns, mist blown off the lip by the offshore wind, and whitewater mist and droplets.
- **`sky.js`**: a gradient sky dome with a sun, hazy islands and clouds drawn on a canvas.
- **`main.js`**: the carving path, banking and compression, foam trail, a slowly drifting cinematic camera, a distant line of pelicans, shadows, bloom and ACES tone mapping.
- **`loft.js`**: a helper that sweeps a cross-section along a curve to build the pelican and board shapes.

Everything is generated in code. The only dependency is `three`.
