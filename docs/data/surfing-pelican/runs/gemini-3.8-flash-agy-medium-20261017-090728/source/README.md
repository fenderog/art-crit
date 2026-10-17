# The Surfing Pelican 3D

An animated, non-interactive 3D web experience of a California brown pelican riding a monster pipeline barrel wave, built with Three.js and HTML5.

## Features

- **Procedural Pelican Character**:
  - Detailed avian anatomy: aerodynamic plumage, articulated S-curved neck, hooked maxilla beak, and totipalmate webbed feet gripping the surfboard deck.
  - Signature expandable gular throat pouch with real-time vertex ripple and air-billow physics.
  - Stylish surfer accessories including retro tortoiseshell mirrored sunglasses and a tropical Hawaiian plumeria lei flower garland.
  - Biomechanical animation solver with dynamic stance crouch, wing aerodynamic balancing, tail trim, and vestibulo-ocular gaze tracking.

- **Sculpted Retro Surfboard**:
  - Classic 1970s longboard design with nose rocker, rail bevels, wood stringer, retro tropical racing stripes, thruster fin hydrofoils, and an ankle leash cord.
  - Dynamic carving physics simulating bottom turns, climbing the wave face, snapping off the lip, and trimming in the tube pocket.

- **Pipeline Barrel Wave System**:
  - Parametric curling cylinder wave with steep carving face, arching lip crest, hollow barrel tube, and ocean floor swells.
  - Physical water material with light transmission, subsurface green-amber glow, and scrolling foam wake textures.
  - Boiling impact zone whitewater and curling foam lip mesh.

- **Water Spray & Atmospheric Particles**:
  - High-velocity rail carve spray and tail fin fans with gravity and wind drift.
  - Wave lip offshore blowback mist sheets catching the sun.
  - Ambient golden sunlit bokeh droplets floating through the air.

- **Tropical Sunset Atmosphere**:
  - Golden-hour lighting with ACESFilmic tone mapping and soft shadow maps.
  - Panoramic sky dome with glowing sun corona.
  - Distant volcanic mountain silhouette islands with swaying palm trees.
  - Distant flock of soaring seabirds gliding in thermal updrafts.

- **Autonomous Cinematic Director**:
  - Automatic non-interactive camera transitions between 5 cinematographic surf angles: Action Chase, Inside the Tube, Water-Level Profile, Hero Low-Angle, and Sweeping Drone Arc.
  - Handheld camera breathing and G-force camera shake.

- **Procedural Web Audio Ambient Sound**:
  - 100% synthesized procedural ocean surf swell roar and rushing whitewater using Web Audio bandpass filters and LFO modulation (zero external audio files, offline friendly, toggleable).

## Development & Bundling

- Install dependencies: `npm install`
- Test bundle: `esbuild main.js --bundle --format=esm --outfile=/dev/null`
- No external assets, CDN dependencies, or storage APIs are used; 100% self-contained and sandboxed iframe compliant.
