# Surfing Pelican

An animated, non-interactive Three.js scene: a pelican wearing sunglasses rides a yellow surfboard on an endless golden-hour wave.

## Run

```bash
npm install
npx serve .        # or any static server, e.g. python3 -m http.server
```

Open the served `index.html` in a browser. No interaction is needed — the pelican carves, flaps for balance, and sprays foam on its own.

## Files

- `index.html` — page entry point
- `main.js` — Three.js scene (pelican built from primitives, animated ocean, wave, spray, clouds)
- `style.css` — overlay typography and layout

## Package check

```bash
npx esbuild main.js --bundle --format=esm --outfile=/dev/null
```
