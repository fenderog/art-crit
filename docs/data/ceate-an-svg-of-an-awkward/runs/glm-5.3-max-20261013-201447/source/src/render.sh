#!/bin/bash
# Render family.svg via qlmanage (square canvas -> exact size) and print ASCII preview.
# usage: src/render.sh [size] [cols] [rows]
set -e
SIZE="${1:-1200}"
COLS="${2:-140}"
ROWS="${3:-70}"
D=$(mktemp -d)
qlmanage -t -s "$SIZE" -o "$D" family.svg >/dev/null 2>&1
cp "$D/family.svg.png" render_full.png
python3 src/pngview.py render_full.png "$COLS" "$ROWS"
rm -rf "$D"