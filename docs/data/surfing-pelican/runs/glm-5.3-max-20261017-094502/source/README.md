# Surf's up, pelican 🌊

An animated, deliberately **non-interactive** three.js scene: a big-billed
pelican surfing a rolling swell at dawn. Sit back and watch — there is nothing
to click, and that's the point.

## What you'll see

- A pelican riding the **face of a traveling swell** (it holds a fixed phase on
  the wave, so it moves with the wave like a real surfer), carving lazy S-turns
  across it, pumping up and down the face, and heeling into each turn.
- Balance behavior: half-open wings with a constant shimmy and occasional
  takeoff-style **flap bursts**, tail wag, crouch pumping, a bobbing head.
- The famous beak: the jaw hinges open now and then and the **pouch stretches**.
- A leash line from the tail plug to its ankle, spray off the nose and rails,
  whitecap foam on the crests, a glittering sun path, drifting clouds, three
  circling gulls — and a fish that leaps out of the sea now and then (the
  pelican turns its head to watch it).
- A low, cinematic chase camera that never asks you for input.

## How it works

- `waves.js` defines the wave field **once** and shares it bit-for-bit between
  JavaScript (so the board, camera and droplets sit exactly on the surface) and
  GLSL (so the ocean mesh is displaced by the same math, generated from the
  same constants via `glslWaveChunk()`).
- The ocean is one large displaced plane with analytic normals, fragment-level
  ripple normals, crest/face foam, fresnel sky reflection, sun glitter and warm
  distance haze matching the sky shader's horizon.
- The pelican and board are built entirely from primitives (lathe, spheres,
  capsules, boxes, a tube neck, a bezier curve) — no model files.
- Everything is procedural: textures (sun glow, clouds) are drawn to canvases
  in code, so the page makes **zero network requests** and uses no storage —
  safe for offline, sandboxed iframes.
- The "scenery rig" (sky dome, sun, clouds, gulls) follows the rider, so the
  horizon behaves like a truly distant backdrop while the pelican travels.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | Entry point; loads `main.js` as an ES module, overlay titles |
| `main.js` | Renderer, scene, kinematics (riding the swell), camera, loop |
| `waves.js` | Shared wave math (JS + GLSL code generation) |
| `ocean.js` | Ocean shader (displacement, foam, glitter, haze) |
| `sky.js` | Sky dome shader + sun glow sprite |
| `pelican.js` | Procedural pelican + surfboard rig and all pose animation |
| `effects.js` | Spray particles, gulls, clouds, jumping fish |
| `theme.js` | Dawn color palette |
| `textures.js` | Canvas-generated textures |

## Run / verify

```sh
npm install

# the packaging check the harness runs — must succeed:
npx esbuild main.js --bundle --format=esm --outfile=/dev/null
```

To preview locally, bundle once and point the `<script>` tag at the output
(browsers can't resolve the bare `three` import without a bundler):

```sh
npx esbuild main.js --bundle --format=esm --outfile=dev.js
# then temporarily change src="main.js" to src="dev.js" in index.html
```

The final self-contained `index.html` is produced by the packaging step that
runs after this; nothing here needs to be built by hand.
