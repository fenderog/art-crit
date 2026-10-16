"""Render the logo mark (organic blob cluster) to PNG using only stdlib."""
import struct, zlib, math

W = H = 1080
CX, CY = W / 2, H / 2 - 40  # leave room, matches SVG composition
S = W / 1200  # scale from SVG coords

def hx(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

PAPER = hx("#F1ECE2")
# (dx, dy, rx, ry, color) approx of the SVG wobble blobs, in SVG units
BLOBS = [
    (-150, -60, 215, 200, hx("#DCD2C1")),
    (140, -110, 190, 178, hx("#C2B6A3")),
    (170, 120, 175, 168, hx("#9AA092")),
    (-130, 140, 185, 172, hx("#A09A8D")),
    (10, 10, 150, 142, hx("#776F63")),
    (10, 5, 72, 68, hx("#33302B")),
]
DOTS = [(-235, -170, 10), (255, -195, 8), (285, 190, 9), (-240, 215, 7)]

buf = bytearray(H * W * 3)
# background
for y in range(H):
    o = y * W * 3
    buf[o:o + W * 3] = bytes(PAPER) * W

def blend_row(y, x0, x1, col):
    if y < 0 or y >= H:
        return
    x0 = max(0, x0); x1 = min(W - 1, x1)
    for x in range(x0, x1 + 1):
        o = (y * W + x) * 3
        buf[o] = col[0]; buf[o + 1] = col[1]; buf[o + 2] = col[2]

def fill_ellipse(cx, cy, rx, ry, col):
    for dy in range(-math.ceil(ry), math.ceil(ry) + 1):
        y = round(cy + dy)
        t = 1 - (dy / ry) ** 2
        if t < 0:
            continue
        hw = rx * math.sqrt(t)
        blend_row(y, round(cx - hw), round(cx + hw), col)

def fill_circle(cx, cy, r, col):
    fill_ellipse(cx, cy, r, r, col)

for dx, dy, rx, ry, col in BLOBS:
    fill_ellipse(CX + dx * S, CY + dy * S, rx * S, ry * S, col)
for dx, dy, r in DOTS:
    fill_circle(CX + dx * S, CY + dy * S, r * S, hx("#33302B"))

def chunk(tag, data):
    c = struct.pack(">I", len(data)) + tag + data
    return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

raw = b"".join(b"\x00" + bytes(buf[y * W * 3:(y + 1) * W * 3]) for y in range(H))
png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
       + chunk(b"IDAT", zlib.compress(bytes(raw), 6)) + chunk(b"IEND", b""))
with open("output/logo-mark.png", "wb") as f:
    f.write(png)
print("wrote output/logo-mark.png", len(png), "bytes")
