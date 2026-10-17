# The Pelican Surf Club

A non-interactive animated Three.js postcard: a feathered pelican rides a striped longboard beneath a curling turquoise swell. Includes procedural geometry, foam spray, moving water, soft shadows, and a responsive editorial layout.

## Run

```sh
npm install
npm run dev
```

Open the local Vite address. `index.html` loads `main.js` as an ES module; `main.js` imports Three.js, and `index.html` references `style.css`. All artwork and grain are generated in code. No external assets, network services, or storage are used.

## Bundle check

```sh
esbuild main.js --bundle --format=esm --outfile=/dev/null
```

The animation starts automatically, has no controls, and slows down for reduced-motion preferences.
