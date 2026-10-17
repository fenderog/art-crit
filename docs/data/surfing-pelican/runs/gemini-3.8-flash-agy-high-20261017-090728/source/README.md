# The Surfing Pelican 🏄‍♂️

An animated, non-interactive 3D web experience built with Three.js depicting a stylized pelican carving through a curling ocean barrel wave at sunset.

## Overview & Visual Design

- **The Pelican ("Pierre")**:
  - Anatomically styled character featuring an iconic hooked orange bill, flexible lower jaw, and an elastic gular (throat) pouch animated with harmonic spring-damper inertia.
  - Multi-jointed wings with splayed primary flight feathers that react dynamically to turns (dipping to skim the water during deep bottom turns, folding in the barrel, flapping on exits).
  - Webbed feet planted on the surfboard deck wax in an authentic goofy/regular crouch.
  - Wind-blown head crest plumage and retro 80s mirrored surf sunglasses.
  - Animated blinking eyelids and head horizon stabilization (vestibular-ocular reflex).

- **The Surfboard**:
  - Classic twin-fin fish surfboard with swallowtail outline, continuous rail bevels, and realistic nose/tail rocker.
  - Airbrush sunset graphic with dark wooden stringer, rail speed stripes, tail traction kickpad, and "Pelican Point" decal.
  - Coiled urethane surf leash connected to the pelican's rear ankle.

- **Dynamic Curling Barrel Wave**:
  - Parametric 3D water geometry forming an open peeling tube, steep concave wave face, cascading lip, and ocean flats.
  - Translucent water material with subsurface backlit glow (glowing turquoise emerald where sunlight pierces the thin lip).
  - Dynamic swell vertex displacement, scrolling normal maps, and foaming whitewater impact zones.

- **Particle Physics**:
  - High-performance GPU particle system emitting water spray and rooster tails off the board rails and fins, driven by carving G-forces.
  - Offshore wind blowing sea mist off the breaking wave crest.

- **Atmosphere & Cinematography**:
  - Golden hour tropical sunset sky dome, radiant sun corona, and distant volcanic islands.
  - Background flock of pelicans soaring in V-formation.
  - Automated Director camera smoothly switching between dynamic angles (Action Cam, Inside the Tube, Low Water Rail Cam, Aerial Drone, Hero Close-Up), with optional manual Orbit Controls.
  - Live maneuver telemetry HUD ("Bottom Turn", "In the Tube!", "Lip Snap", etc.).
  - 100% procedural Web Audio API ocean surf, wind, and carving hiss (starts muted per browser autoplay standards, toggleable via UI).

## Packaging & Compatibility

- Runs offline in a sandboxed iframe without network requests or storage APIs.
- All textures, normal maps, audio, and meshes are procedurally generated in code.
- Tested and verified with `esbuild main.js --bundle --format=esm --outfile=/dev/null`.
