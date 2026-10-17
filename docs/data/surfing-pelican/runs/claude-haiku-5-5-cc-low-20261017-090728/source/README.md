# Surfing Pelican

A non-interactive, animated 3D scene of a pelican riding a surfboard over rolling waves, built with Three.js.

- The ocean is a grid whose vertices are displaced by summed sine waves each frame.
- The board follows a slow S-curve across the swell, tilting and yawing with the wave slope.
- The pelican bobs on the board and flaps its wings to keep balance.
- The camera slowly orbits the surfer.

## Running

Open `index.html` in a browser, or run the dev/build check:

    npm install
    npm run build

`npm run build` runs `esbuild main.js --bundle --format=esm --outfile=/dev/null` to confirm the modules bundle.
