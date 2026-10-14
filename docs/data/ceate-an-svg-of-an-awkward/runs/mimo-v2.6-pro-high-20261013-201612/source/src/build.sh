#!/bin/bash
# Build the deliverables in ./output/ from src/robot-family-portrait.svg
#
# SVG -> PNG: macOS Quick Look (qlmanage) rasterises the SVG.  It applies plain
# SVG viewport rules only when the document's intrinsic size equals the size of
# the square thumbnail it produces, so the artwork is wrapped in a square
# document (viewBox unchanged) and the resulting letterbox bars are cropped
# away with ffmpeg.
set -euo pipefail
cd "$(dirname "$0")/.."

SRC=src/robot-family-portrait.svg
W=1600
H=1150
OFF=225          # (1600 - 1150) / 2 : vertical letterbox in the square render
NAME=robot-family-portrait
TMP=build_tmp

mkdir -p "$TMP" output
rm -f "$TMP"/*.png "$TMP"/*.svg

cp "$SRC" "output/$NAME.svg"

python3 - "$SRC" "$TMP/render.svg" "$W" "$((H + 2 * OFF))" <<'PYEOF'
import sys
src, dst, size = sys.argv[1], sys.argv[2], sys.argv[3]
svg = open(src).read()
svg = svg.replace('width="1600" height="1150"', f'width="1600" height="{size}"', 1)
open(dst, 'w').write(svg)
PYEOF

qlmanage -t -s "$W" -o "$TMP" "$TMP/render.svg" >/dev/null 2>&1
ffmpeg -y -loglevel error -i "$TMP/render.svg.png" -vf "crop=${W}:${H}:0:${OFF}" -frames:v 1 "output/$NAME.png"

# 8 s slow pan/zoom over the portrait
ffmpeg -y -loglevel error -i "output/$NAME.png" \
  -vf "zoompan=z='1.0+0.0011*on':x='(iw-iw/zoom)*(0.16+0.55*on/239)':y='(ih-ih/zoom)*0.32':d=240:s=1280x920:fps=30,format=yuv420p" \
  -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 22 -movflags +faststart "output/$NAME.mp4"

rm -rf "$TMP"
ls -la output
