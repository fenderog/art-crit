#!/bin/bash
# usage: src/zoom.sh x0 y0 x1 y1 cols rows [hue]
set -e
X0=$1; Y0=$1; X0=$1; Y0=$2; X1=$3; Y1=$4; COLS=$5; ROWS=$6; HUE=${7:-}
D=$(mktemp -d)
qlmanage -t -s 2400 -o "$D" family.svg >/dev/null 2>&1
ffmpeg -y -loglevel error -i "$D/family.svg.png" -vf "crop=$(( (X1-X0)*2 )):$(( (Y1-Y0)*2 )):$(( X0*2 )):$(( Y0*2 ))" "$D/z.png"
python3 src/pngview.py "$D/z.png" $COLS $ROWS $HUE
rm -rf "$D"
