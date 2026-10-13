#!/bin/sh
# Rasterise the SVG via macOS Quick Look (square thumbnails), then crop back to 4:3.
set -e
cd "$(dirname "$0")/.."
tmp=$(mktemp -d)
sed 's/viewBox="0 0 1200 900" width="1200" height="900"/viewBox="0 -150 1200 1200" width="1200" height="1200"/' \
  src/robot_family_portrait.svg > "$tmp/sq.svg"
qlmanage -t -s 1200 -o "$tmp" "$tmp/sq.svg" >/dev/null 2>&1
ffmpeg -loglevel error -y -i "$tmp/sq.svg.png" -vf crop=1200:900:0:150 output/robot_family_portrait.png
cp src/robot_family_portrait.svg output/
rm -rf "$tmp"
