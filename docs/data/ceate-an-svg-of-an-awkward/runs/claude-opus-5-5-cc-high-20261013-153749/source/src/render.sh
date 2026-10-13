#!/bin/sh
# Render src/portrait.svg to output/ (SVG copy + JPG via headless Chrome + ffmpeg)
cd "$(dirname "$0")/.."
cp src/portrait.svg output/robot-family-portrait.svg
TMP="$PWD/src/_frame.png"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --hide-scrollbars \
  --window-size=1600,1200 --screenshot="$TMP" "file://$PWD/src/portrait.svg" 2>/dev/null
ffmpeg -v error -y -i "$TMP" -q:v 2 output/robot-family-portrait.jpg
rm -f "$TMP"
