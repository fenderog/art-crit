# Offshore

A non-interactive, animated Three.js surfing pelican, presented as a quiet editorial seaside escape.

## Preview

```sh
npm install
npm run dev
```

Open the local address printed by Vite.

## Files

- `index.html` — accessible page structure and inline illustrations
- `style.css` — responsive editorial layout
- `main.js` — procedural pelican, surfboard, curling wave, foam, lighting, and animation

All artwork is generated in code. No network assets, external fonts, or browser storage are used. The animation automatically slows for reduced-motion preferences.

Bundle check (verified):

```sh
esbuild main.js --bundle --format=esm --outfile=/dev/null
```
