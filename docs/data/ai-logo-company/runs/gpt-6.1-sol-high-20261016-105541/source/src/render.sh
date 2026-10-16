#!/bin/bash
# Rebuild vector assets and the PNG presentation using the installed Chrome.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/src/create_logo.py"
TEMP="$(mktemp -d "$ROOT/.render.XXXXXX")"
trap 'rm -rf "$TEMP"' EXIT
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-first-run --no-default-browser-check \
  --user-data-dir="$TEMP/chrome" --hide-scrollbars \
  --window-size=1600,1000 --screenshot="$ROOT/output/loam-logo.png" \
  "file://$ROOT/output/loam-logo.svg" >/dev/null 2>&1
