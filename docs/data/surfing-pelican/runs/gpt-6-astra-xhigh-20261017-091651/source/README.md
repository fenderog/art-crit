# Pelican Bay

A non-interactive, animated Three.js seaside postcard: a feathered pelican balances on a coral longboard beside a curling turquoise wave. Includes drifting foam, spray, gentle wing movements, and the occasional blink.

## Run locally

```sh
npm install
npm run dev
```

Open the local address Vite prints. `index.html` is the entry point; `main.js` is its JavaScript ES module.

## Bundle check

```sh
esbuild main.js --bundle --format=esm --outfile=/dev/null
```

All geometry, textures, and illustrations are generated in code or inline SVG. No remote assets, network services, storage, or interaction required. Responsive layout and reduced-motion support included.
