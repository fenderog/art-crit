# The Morning Break — A Surfing Pelican

An animated, **non-interactive** Three.js diorama: a white pelican with a
long orange beak and wobbling pouch carves an endless golden-hour wave on a
coral surfboard. There are no controls to learn — open the page and watch.

## What's in the scene

- **Procedural pelican** — plump body, S-curved neck, crested head turned
  into the ride, flattened beak with hooked tip and pouch, black-tipped
  wings spread for balance, webbed feet, and a board leash.
- **Endless ride** — she pumps up and down the wave face, traverses along
  it, crouches to absorb each turn, counter-balances with her wings, and
  pops a small hop roughly every twelve seconds.
- **Curling hero wave** — a bent-plane wave face with a sunlit gradient,
  pulsing foam lip, churning whitewater, falling lip mist, and spray kicked
  up behind the board.
- **Golden-hour world** — gradient sky dome, low sun, animated ocean swells,
  drifting clouds, and flapping distant seabirds.
- **Cinematic camera** — a slow drift that keeps the rider framed. The page
  is deliberately non-interactive: no mouse, touch, or keyboard controls.
- Respects `prefers-reduced-motion` by calming the animation.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | Entry point; loads `style.css` and `main.js` |
| `main.js` | All Three.js scene, model-building, and animation code |
| `style.css` | Page layout, caption card, and vignette |
| `package.json` | Declares the `three` dependency |

## Develop

```sh
npm install
npm run check   # verify the bundle: esbuild main.js --bundle --format=esm
```

The page imports `three` by package name and is packaged afterwards into a
single self-contained `index.html` with esbuild, so it runs fully offline
with no network requests and no browser storage.
