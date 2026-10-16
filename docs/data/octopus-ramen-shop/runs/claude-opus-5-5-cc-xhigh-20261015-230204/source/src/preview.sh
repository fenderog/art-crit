#!/bin/sh
# Rasterise the SVG with Quick Look (WebKit). Quick Look renders square thumbnails, so a copy
# with a square canvas is rendered and the top 1600x1200 is cropped back out.
set -e
mkdir -p tmp
sed '1s/height="1200" viewBox="0 0 1600 1200"/height="1600" viewBox="0 0 1600 1600"/' \
  output/octopus_ramen_chef.svg > tmp/square.svg
qlmanage -t -s 1600 -o tmp tmp/square.svg >/dev/null 2>&1
ffmpeg -v error -y -i tmp/square.svg.png -vf crop=1600:1200:0:0 "${1:-tmp/preview.png}"
