#!/bin/sh
# Rasterise an SVG via Quick Look (WebKit) and crop to its aspect: preview.sh in.svg out.png size w h
set -e
tmp=$(mktemp -d)
qlmanage -t -s "$3" -o "$tmp" "$1" >/dev/null 2>&1
ffmpeg -v error -y -i "$tmp/$(basename "$1").png" -vf "crop=$4:$5:0:0" "$2"
rm -rf "$tmp"
