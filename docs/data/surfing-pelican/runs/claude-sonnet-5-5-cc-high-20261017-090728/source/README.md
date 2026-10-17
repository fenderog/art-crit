# Surfing Pelican

A non-interactive, endlessly looping three.js scene: a pelican on a coral surfboard carves back and forth across the face of a breaking wave at golden hour.

- `main.js` – scene, camera drift, surfer path, lights, render loop
- `waves.js` – wave maths shared by the CPU (board, wake, camera) and the GPU (ocean mesh)
- `ocean.js` / `sky.js` – procedural water (translucent face, foam, glitter) and sky shaders
- `pelican.js` / `board.js` – the pelican (feathered wings, IK legs, pouch, blinking) and surfboard, built from code
- `spray.js` / `trail.js` / `scenery.js` – spray particles, foam wake, headlands and gulls

Everything is generated in code (no external assets). `npm install`, then bundle `index.html` / `main.js` with esbuild.
