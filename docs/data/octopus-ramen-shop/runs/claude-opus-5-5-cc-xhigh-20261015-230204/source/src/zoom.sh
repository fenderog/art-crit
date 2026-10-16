#!/bin/sh
# Zoomed render of a region: zoom.sh X Y W OUT  (region W x 0.75W at X,Y)
set -e
mkdir -p tmp
H=$(python3 -c "print($3*0.75)")
sed "1s/height=\"1200\" viewBox=\"0 0 1600 1200\"/height=\"1600\" viewBox=\"$1 $2 $3 $3\"/" \
  output/octopus_ramen_chef.svg > tmp/zoom.svg
qlmanage -t -s 1200 -o tmp tmp/zoom.svg >/dev/null 2>&1
ffmpeg -v error -y -i tmp/zoom.svg.png -vf crop=1200:900:0:0 "$4"
