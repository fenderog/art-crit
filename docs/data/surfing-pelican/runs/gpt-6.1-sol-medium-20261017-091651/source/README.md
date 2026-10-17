# Pelican Surf Club

A non-interactive, animated Three.js postcard: a pelican balances on a coral longboard beside a rolling turquoise wave, under a warm coastal sun.

All models, water, foam, and scenery are generated in JavaScript. No external assets, network calls, or browser storage are used. The layout adapts to desktop and mobile screens.

## Packaging check

```sh
npm install
esbuild main.js --bundle --format=esm --outfile=/dev/null
```

Entry point: `index.html`. Scene: `main.js`. Layout: `style.css`.
