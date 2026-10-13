#!/bin/bash
# Rebuild the vector artwork and a 1440 x 1280 PNG using the local browser.
set -euo pipefail
cd "$(dirname "$0")"
python3 make_portrait.py
profile="$PWD/.render-profile"
trap 'rm -rf "$profile"' EXIT
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --no-sandbox --disable-gpu --hide-scrollbars \
  --user-data-dir="$profile" \
  --window-size=1440,1280 --force-device-scale-factor=1 \
  --screenshot="$PWD/output/family_portrait.png" \
  "file://$PWD/output/family_portrait.svg"
