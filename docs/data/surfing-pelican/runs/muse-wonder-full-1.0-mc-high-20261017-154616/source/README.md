# The Surfing Pelican

An animated, non-interactive Three.js scene: a pelican carves back and forth
across a curling wave on a striped surfboard, wings out for balance, spray
flying from the rail. Gulls circle, a dolphin leaps in the distance, clouds
drift past a palm-topped island. There is nothing to click — just watch.

## Run locally

```sh
npm install
npx vite --port 5173
```

Then open http://127.0.0.1:5173/ in a browser. The entry point loads
`main.js` as an ES module; `three` is imported by package name (Vite
resolves it in dev, and esbuild bundles it for the packaged page).

## Notes

- Fully procedural: the pelican, board, wave, island and wildlife are all
  built from Three.js geometry in code — no external assets or network calls.
- The camera drifts on its own; the scene deliberately has no controls.
- Motion eases down automatically when the OS requests reduced motion.
