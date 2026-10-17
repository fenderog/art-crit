# Surfing Pelican

An animated, non-interactive surfing pelican built with Three.js. A procedural
pelican — long orange beak and pouch, flapping wings, fluttering scarf — rides
a coral surfboard on an endless low-poly swell, carving side to side while
spray, foam rings, drifting clouds, palm islands, and wheeling gulls complete
the scene. There are no controls: open the page and watch the loop.

## Run

```sh
npm install
npm start        # python3 -m http.server 5319
```

Then open http://localhost:5319/ in a browser.

## Check the bundle

```sh
npm run check    # esbuild main.js --bundle --format=esm --outfile=/dev/null
```

## Notes

- Entry point is `index.html`, which loads `main.js` as an ES module;
  Three.js is imported by package name (`three`) with no CDN or import map.
- Everything is generated in code — ocean, pelican, board, sky, and particles —
  so the packed page needs no network access and uses no web storage.
- `prefers-reduced-motion` slows the loop down automatically.
