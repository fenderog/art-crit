# Drift — Swell days.

A non-interactive, animated Three.js coastal escape: one happy pelican, a golden longboard, and an endless turquoise wave.

## Run locally

```sh
npm install
npm run dev
```

Open the local address printed by Vite. `index.html` loads `main.js` as an ES module and `style.css` separately.

All geometry, textures, lighting, and decorations are generated locally. No external assets, network APIs, or browser storage are used. The responsive scene includes gentle surfing motion, moving feathers, a fluttering scarf, blinking, foam, and spray. Reduced-motion preferences produce a still scene.

## Packaging check

```sh
esbuild main.js --bundle --format=esm --outfile=/dev/null
```

Requires a browser with WebGL 2. No interaction is needed—just drift.
