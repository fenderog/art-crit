# Big Kahuna Pete - Surfing Pelican

An animated, non-interactive 3D web experience built with Three.js showcasing a stylish pelican named Big Kahuna Pete gracefully carving a giant ocean barrel wave at golden hour.

## Features

- **Stylized Procedural Pelican**:
  - Detailed hierarchical procedural geometry: articulated body, feathered wings, S-curved neck, knobby legs, and webbed feet gripping the surfboard.
  - Iconic pelican characteristics: long upper bill with hook tip and a flexible, inertial throat pouch that wobbles with wave momentum.
  - Beach vibe accessories: Mirrored neon-teal surfer shades with strap and a colorful tropical Hawaiian flower lei garland.
  - Surfing kinematics: Bent-knee compression/extension absorbing wave bumps, body counter-banking, and fluttering wing feathers for aerodynamic balance.

- **Curling Ocean Barrel**:
  - Parametric 3D curling wave tube with animated vertex displacement simulating ocean swells rushing by.
  - Translucent water material with physical clearcoat, specular shine, and procedural canvas sea-foam texturing.
  - Foaming wave lip strip and sweeping water wake.

- **Dynamic Particle Systems**:
  - Wave lip spray: Mist particles thrown forward from the curling wave crest.
  - Board wake spray: Trailing rooster tails generated dynamically behind the surfboard rail and fins.

- **Atmosphere & Cinematic Camera**:
  - Golden hour tropical sky dome, glowing sun with corona halo, and distant volcanic islands.
  - Automated cinematic camera that orbits smoothly between dramatic barrel shots, hero tracking angles, and coastal vistas without requiring user interaction.

## Technical Details

- **Built with**: Three.js (ES Modules)
- **Zero External Assets**: All textures (foam, sky gradient, surfboard livery, particle sprites) are generated procedurally in code via Canvas API.
- **Offline & Sandbox Compatible**: No network calls, storage APIs, or external CDN dependencies.
- **Packaging Verified**: Cleanly bundles via `esbuild main.js --bundle --format=esm --outfile=/dev/null`.
