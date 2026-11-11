# The Surfing Pelican

An animated, non-interactive 3D scene built with [Three.js](https://threejs.org/).
A white pelican with a long orange beak, throat pouch and surfer sunglasses carves
the swell on a coral surfboard, flapping its wings for balance while foam and spray
trail behind it. The camera orbits slowly on its own — sit back and watch.

## Run locally

Serve the folder and open the page in a browser, e.g.:

```sh
npx serve .
# or
python3 -m http.server 8000
```

Then open `http://localhost:8000` (or the printed URL).

## Bundle check

```sh
npx esbuild main.js --bundle --format=esm --outfile=/dev/null
```

## Files

- `index.html` — entry point, loads the scene as an ES module
- `main.js` — Three.js scene: ocean waves, pelican + surfboard, foam, spray, clouds, animation loop

No network requests at runtime beyond the local files; everything is generated in code.
