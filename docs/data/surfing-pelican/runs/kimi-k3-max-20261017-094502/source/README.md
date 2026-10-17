# The Surfing Pelican

An animated, **non-interactive** three.js scene: a cartoon pelican rides a
striped surfboard on rolling ocean swells — knees bending, wings flapping for
balance, foam spraying off the tail — while the camera slowly orbits. Distant
birds, drifting clouds, sun glare and height-tinted water round out the scene.
Everything (geometry, textures, sky) is generated in code; there are no
external assets.

## Run locally

```sh
npm install
npx http-server .        # or: python3 -m http.server
# open http://localhost:8080
```

## Package check

```sh
esbuild main.js --bundle --format=esm --outfile=/dev/null
```

## Files

- `index.html` — entry point, loads `main.js` as an ES module
- `main.js` — the whole scene: ocean swell simulation, procedural pelican and
  surfboard, foam-particle trail, sky/clouds/birds, cinematic camera
