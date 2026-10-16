#!/bin/sh
# Rasterise the SVG with headless Chrome: render.sh in.svg out.png [scale]
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=${3:-1} \
  --default-background-color=00000000 --virtual-time-budget=1000 \
  --window-size=1200,900 --screenshot="$2" "file://$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" 2>/dev/null
