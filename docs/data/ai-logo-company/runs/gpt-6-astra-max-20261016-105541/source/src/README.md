# loam

A logo concept for a generative AI company. Three curling fronds form a growing whorl; a custom lowercase wordmark echoes their rounded bowls. Flat, warm-neutral colors keep the identity calm and reproducible.

## Finished assets

- `output/loam-logo.svg` — transparent horizontal lockup, with outlined descriptor.
- `output/loam-symbol.svg` — transparent standalone symbol, optically centered.
- `output/loam-preview.png` — 2400 × 1500 presentation on warm ivory.

Both SVGs are self-contained vectors: no fonts, embedded raster images, filters, or external resources. Use them on light backgrounds. For small placements, use the symbol rather than the descriptor-bearing lockup.

## Rebuild

From the project root, run:

```sh
python3 src/build.py
```

The generator uses Python's standard library. On macOS it uses the built-in `sips` tool for the PNG; otherwise it exports the presentation as SVG instead. Rendering intermediates are removed automatically.

The original symbol and wordmark paths are in `build.py`. `descriptor.json` stores the outlined small descriptor. The optional `outline_descriptor.swift` utility recreates those outlines from macOS Avenir Next Medium; it is not required to rebuild the final assets.

## Palette

| Role | Hex |
|---|---|
| Warm ivory | `#F3F0E8` |
| Charcoal wordmark | `#373A32` |
| Bark | `#494C41` |
| Taupe | `#B4AB99` |
| Stone | `#848575` |
| Secondary lettering | `#6B6E60` |
