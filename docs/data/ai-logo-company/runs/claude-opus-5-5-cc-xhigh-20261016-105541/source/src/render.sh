#!/bin/zsh
# Builds every Flint deliverable into ./output.  Requires node, ffmpeg and macOS `sips`
# (used only to rasterise SVG -> PNG).  Intermediate files live in ./build and are removed.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=output BUILD=build
mkdir -p $OUT $BUILD

# 1. vector logos
node src/build.mjs $OUT

# rasterise an SVG at a scale, optionally on a background colour
rasterize() { # in.svg out.png scale bg|none
  python3 - "$1" "$3" "$4" > $BUILD/_r.svg <<'PY'
import sys, re
s = open(sys.argv[1]).read(); k = float(sys.argv[2]); bg = sys.argv[3]
w, h = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', s).groups())
s = re.sub(r'width="[\d.]+" height="[\d.]+"', f'width="{w*k:.0f}" height="{h*k:.0f}"', s, count=1)
if bg != 'none': s = s.replace('<title>', f'<rect width="{w}" height="{h}" fill="{bg}"/><title>', 1)
print(s)
PY
  sips -s format png $BUILD/_r.svg --out "$2" >/dev/null
}

# 2. primary logo, high resolution on chalk
rasterize $OUT/flint-logo.svg $OUT/flint-logo.png 6 '#F4F0EA'

# 3. brand sheet
node src/sheet.mjs $BUILD/sheet.svg
sips -s format png $BUILD/sheet.svg --out $OUT/flint-brand-sheet.png >/dev/null

# 4. reveal animation (tagline text set with the system's Avenir Next, overlaid by ffmpeg)
cat > $BUILD/tagline.svg <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="60" viewBox="0 0 900 60"><text x="450" y="38" text-anchor="middle" font-family="Avenir Next Demi Bold, AvenirNext-DemiBold, Avenir Next" font-size="20" letter-spacing="6" fill="#857566">GENERATIVE INTELLIGENCE, GROUNDED</text></svg>
SVG
sips -s format png $BUILD/tagline.svg --out $BUILD/tagline.png >/dev/null
node src/reveal.mjs $OUT/flint-reveal.mp4 $BUILD/tagline.png

rm -rf $BUILD
ls -la $OUT
