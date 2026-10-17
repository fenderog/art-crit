# Surfing Pelican

A looping, non-interactive Three.js scene of a brown pelican crouched on a longboard, riding the face of a wave.

`index.html` loads `main.js`, which imports `three` by package name. Shapes, the wave, and the sky are built in code. Nothing is loaded from the network, and the scene does not use storage or controls. A static server alone cannot resolve the bare `three` import; the page is meant to be bundled (esbuild) first.

```bash
npm install
npx serve .
```
