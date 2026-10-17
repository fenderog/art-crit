# Surfing Pelican

A non-interactive Three.js scene. A pelican carves along a swell: the board sits on the same waves that move the ocean, and the camera rides along from the shoulder.

## Develop

```bash
npm install
npx serve .
```

Open the local URL. The page is an ES module, so it needs a local server.

## Bundle check

```bash
esbuild main.js --bundle --format=esm --outfile=/dev/null
```
