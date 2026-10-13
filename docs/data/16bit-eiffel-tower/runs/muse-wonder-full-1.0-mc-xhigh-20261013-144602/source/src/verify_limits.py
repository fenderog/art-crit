#!/usr/bin/env python3
"""Independently verify SNES limits from a decoded PPM of the PNG.

Usage:
  ffmpeg -y -v error -i output/eiffel_tower_snes.png src/_check.ppm
  python3 src/verify_limits.py src/_check.ppm
"""
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "src/_check.ppm"
data = open(path, "rb").read()
parts = data.split(b"\n", 3)
assert parts[0] == b"P6", parts[0]
w, h = map(int, parts[1].split())
maxv = int(parts[2]); raw = parts[3]
assert (w, h) == (256, 224), (w, h)
assert maxv == 255 and len(raw) == w * h * 3, (maxv, len(raw))

def pix(x, y):
    i = (y * w + x) * 3
    return (raw[i], raw[i+1], raw[i+2])

colours = {pix(x, y) for y in range(h) for x in range(w)}
max_tile = 0; worst = None
for ty in range(0, h, 8):
    for tx in range(0, w, 8):
        s = {pix(x, y) for y in range(ty, ty+8) for x in range(tx, tx+8)}
        if len(s) > max_tile:
            max_tile, worst = len(s), (tx, ty)
print(f"decoded {w}x{h}: {len(colours)} colours total (limit 128), "
      f"max {max_tile} colours in an 8x8 tile at {worst} (limit 16)")
assert len(colours) <= 128 and max_tile <= 16
print("PASS")
