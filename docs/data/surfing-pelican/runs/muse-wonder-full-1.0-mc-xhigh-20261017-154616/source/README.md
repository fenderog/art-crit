# The Surfing Pelican

An animated, non-interactive Three.js scene: a procedurally modelled pelican
endlessly carves up and down the face of a curling wave on a striped longboard.
Wings balance, the throat pouch sways, spray kicks off the tail, gulls cross
the sky, and the camera sways gently — there are no controls, just watching.

## Files

- `index.html` — entry point, loads `main.js` as an ES module
- `main.js` — renderer, lighting, camera, animation loop
- `pelican.js` — the pelican, surfboard, spray, and surfing motion
- `ocean.js` — curling wave, water, sky, clouds, sun, and gulls

## Develop

```sh
npm install
npx esbuild main.js --bundle --format=esm --outfile=/dev/null  # bundle check
```

The page uses no network requests, storage, or external assets; every model
and texture is generated in code, so the bundled page runs fully offline.
