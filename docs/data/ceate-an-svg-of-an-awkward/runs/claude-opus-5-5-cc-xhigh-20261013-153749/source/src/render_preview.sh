#!/bin/sh
# Rasterize the 1600x1200 SVG with macOS Quick Look (WebKit).
# Quick Look renders into a square, so the root is padded to a square canvas
# first and the result cropped back to 4:3.
# usage: src/render_preview.sh in.svg out.(png|jpg) [width]
set -e
IN="$1"; OUT="$2"; WIDTH="${3:-1600}"
TMP=$(mktemp -d)
sed 's/width="1600" height="1200" viewBox="0 0 1600 1200"/width="1600" height="1600" viewBox="0 0 1600 1600"/' "$IN" > "$TMP/sq.svg"
qlmanage -t -s "$WIDTH" -o "$TMP" "$TMP/sq.svg" >/dev/null 2>&1
ffmpeg -loglevel error -y -i "$TMP/sq.svg.png" -vf "crop=$WIDTH:$((WIDTH*3/4)):0:0" -q:v 2 "$OUT"
rm -rf "$TMP"
