#!/bin/zsh
# usage: render.sh in.svg out.png width height [scale]
# Rasterises an SVG through headless Chrome (used for the PNG preview and for design checks).
profile="$(dirname "$0")/.chrome-profile"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor="${5:-1}" --user-data-dir="$profile" \
  --screenshot="$2" --window-size="$3,$4" "file://$1" >/dev/null 2>&1
rm -rf "$profile"
