# The Offshore Club

An animated, non-interactive Three.js vignette: a pelican riding a coral longboard beside a sculpted turquoise wave. Includes gently balancing wings, bobbing surf, airborne spray, and a responsive editorial layout.

- Entry point: `index.html`
- JavaScript: `main.js` (ES module)
- Styling: `style.css`
- Dependency: `three`

All geometry and materials are generated in code. No external assets, network requests, or browser storage are used. Serve through an ES-module-aware development server, or use the provided packaging pipeline.

Bundle validation: `esbuild main.js --bundle --format=esm --outfile=/dev/null`
