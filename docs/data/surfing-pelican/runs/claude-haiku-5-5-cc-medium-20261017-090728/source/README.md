# Surfing Pelican

A non-interactive, animated three.js scene: a pelican riding a surfboard down a
procedurally animated ocean swell.

## What's in it

- **Pelican** built from primitives (ellipsoid body, tube neck, bill with pouch,
  legs, tail) with wings that flap for balance.
- **Board** that follows the slope of the wave under it, with the pelican
  counter-leaning to stay upright.
- **Ocean** as a displaced plane, with vertex colours shifting from deep blue to
  turquoise to white foam on the crests.
- **Spray** thrown off the tail fin, plus a sky gradient, painted sun and drifting clouds.

## Running

```sh
npm install
```

Open `index.html` in a browser. The page has no controls and no network needs.

Check that it packages:

```sh
esbuild main.js --bundle --format=esm --outfile=/dev/null
```

## Files

- `index.html`: entry page, loads `main.js` as an ES module.
- `main.js`: the whole scene (geometry, wave function, animation loop).
- `package.json`: dependencies are `three` and `esbuild` (dev).
