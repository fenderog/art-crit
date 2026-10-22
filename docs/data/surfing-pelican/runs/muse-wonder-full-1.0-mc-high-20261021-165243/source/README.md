# Surfing Pelican

An animated, non-interactive Three.js scene: a great white pelican with a long orange beak and swinging pouch balances on a striped surfboard, endlessly riding a turquoise swell in front of a big curling wave. Wings seesaw for balance, spray kicks up at the board, and clouds and gulls drift overhead. There are no controls — just open the page and watch.

## Run locally

```bash
npm install
npx serve .        # or any static file server
```

Then open `index.html` via the server URL in a browser. The entry point loads `main.js` as an ES module, which imports `three` from npm. Everything (models, textures) is generated in code; no external assets or network requests are needed at runtime beyond the bundled module.

## Files

- `index.html` — page shell and title overlay
- `main.js` — the whole scene: pelican, surfboard, ocean swell, curling wave, foam, spray, sky, and the animation loop
- `visual-plan/refs/hero.jpg` — art reference the model was built against
