#!/bin/sh
# usage: compare.sh TAG  -> renders/TAG_compare.png (reference quadrants vs renders)
T=$1
ffmpeg -y -loglevel error -i references/robie.jpg -i renders/${T}_front.png -i renders/${T}_side_r.png -i renders/${T}_back.png -i renders/${T}_side_l.png -filter_complex "\
[0:v]crop=640:620:0:30,scale=560:560[rf];[0:v]crop=600:600:680:30,scale=560:560[rs];\
[0:v]crop=640:620:0:650,scale=560:560[rb];[0:v]crop=620:620:660:660,scale=560:560[rs2];\
[1:v]scale=560:560[a];[2:v]scale=560:560[b];[3:v]scale=560:560[c];[4:v]scale=560:560[d];\
[rf][a][rs][b]hstack=4[top];[rb][c][rs2][d]hstack=4[bot];[top][bot]vstack=2" renders/${T}_compare.png
