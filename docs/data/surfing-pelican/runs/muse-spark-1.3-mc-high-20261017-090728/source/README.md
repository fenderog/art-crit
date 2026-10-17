# Surf's Up, Pelican

An animated, **non-interactive** 3D vignette: a pelican surfing a breaking wave,
built with HTML and Three.js. Just open the page and watch — there are no
controls. The camera drifts slowly on its own and the loop runs forever.

## What's in the scene

- A procedural pelican (body, balancing wings, tail, legs, head with eyes,
  long beak and a wobbling throat pouch) riding a coral surfboard.
- Animated ocean swells, a breaking wave with a foam crest, spray particles,
  a stern wake, drifting clouds, distant gulls, sun and gradient sky.

## Run it

```sh
npm install
npx serve .        # or: python3 -m http.server
```

Then open `index.html` (entry point; code lives in `main.js` as ES modules).

## Notes

- Imports `three` by package name — no CDN URLs, no import maps.
- All visuals are generated in code (no external assets), so the packaged page
  runs offline with no network requests and uses no storage APIs.
- Packaging check: `esbuild main.js --bundle --format=esm --outfile=/dev/null`
  must succeed.
