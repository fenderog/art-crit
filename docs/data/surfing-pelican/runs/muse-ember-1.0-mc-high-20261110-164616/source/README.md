# Surfing Pelican

An animated, non-interactive 3D surfing pelican built with Three.js in plain JavaScript.

## Run

```bash
npm install
python3 -m http.server 8000
```

Then open http://127.0.0.1:8000/index.html in a browser.

## Controls

- Drag the canvas to orbit, scroll or pinch to zoom.
- Buttons (Hero / Side / Top / Follow) set camera angles.
- Arrow keys and `+` / `-` zoom while the canvas is focused.

The scene starts moving on load: ocean swell, spray, drifting
clouds, and a pelican balancing on a striped board. All geometry,
textures, and spray are generated in code. No network requests,
no storage, no build step required to view it locally.

## Bundle check

```bash
esbuild main.js --bundle --format=esm --outfile=/dev/null
```
