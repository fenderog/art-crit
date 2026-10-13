#!/bin/sh
# Rasterise an SVG to PNG with headless Chrome: render.sh in.svg out.png [scale]
IN="$1"; OUTP="$2"; SC="${3:-1}"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --hide-scrollbars --force-device-scale-factor="$SC" --window-size="1600,1200" \
  --default-background-color=00000000 --screenshot="$OUTP" "file://$(cd "$(dirname "$IN")" && pwd)/$(basename "$IN")" 2>/dev/null
