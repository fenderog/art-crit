#!/usr/bin/env python3
"""Generate an organic-shape generative-AI logo (LOAM) in neutral tones.

Outputs (vector masters):
  ../output/loam-logo.svg       light lockup
  ../output/loam-logo-dark.svg  dark lockup
Intermediate (deleted after mp4 render):
  /tmp/loam-mark.png            raster mark for video source

Vector blobs and raster blobs share one parametric definition so the
PNG/MP4 mark matches the SVG mark.
Standard library only.
"""
import math
import os
import struct
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")
TMP_PNG = "/tmp/loam-mark.png"

W, H = 1200, 1200
CX, CY = 600, 500  # optical centre of the mark (wordmark sits below)

# Neutral palette (warm paper / stone / taupe / umber / ink)
PAPER = (243, 238, 230)
SAND = (220, 207, 182)
STONE = (183, 169, 146)
TAUPE = (140, 128, 113)
UMBER = (74, 66, 59)
INK = (45, 41, 38)
DARK_BG = (38, 34, 31)
CREAM = (233, 224, 208)

# Blob definition: centre offset from (CX,CY), base radius, two sine lobes,
# rotation (radians). Shared by SVG path + PNG raster.
BLOBS = [
    # back petal (up)
    {"dx": 0, "dy": -135, "base": 238, "k1": 3, "a1": 0.10, "p1": 0.5,
     "k2": 5, "a2": 0.055, "p2": 1.7, "rot": 0.0, "fill": SAND},
    # left petal
    {"dx": -128, "dy": 95, "base": 218, "k1": 2, "a1": 0.12, "p1": 2.0,
     "k2": 4, "a2": 0.05, "p2": 0.3, "rot": 0.6, "fill": STONE},
    # right petal
    {"dx": 130, "dy": 100, "base": 208, "k1": 3, "a1": 0.11, "p1": 4.0,
     "k2": 2, "a2": 0.07, "p2": 1.0, "rot": -0.5, "fill": TAUPE},
]
CORE = {"dx": 0, "dy": 8, "base": 112, "k1": 3, "a1": 0.07, "p1": 1.2,
        "k2": 4, "a2": 0.04, "p2": 3.0, "rot": 0.3}

# Small generative "spore" nodes (mark only): offsets + radius
NODES = [
    {"dx": -238, "dy": -38, "r": 13},
    {"dx": 244, "dy": -52, "r": 10},
    {"dx": 176, "dy": 268, "r": 12},
    {"dx": -182, "dy": 262, "r": 8},
]


def radius_at(b, theta):
    t = theta - b["rot"]
    return b["base"] * (1.0 + b["a1"] * math.sin(b["k1"] * t + b["p1"])
                        + b["a2"] * math.sin(b["k2"] * t + b["p2"]))


def blob_points(b, n=40):
    cx, cy = CX + b["dx"], CY + b["dy"]
    pts = []
    for i in range(n):
        th = 2 * math.pi * i / n
        r = radius_at(b, th)
        pts.append((cx + r * math.cos(th), cy + r * math.sin(th)))
    return pts


def smooth_closed_path(pts):
    """Closed Catmull-Rom -> cubic Bezier path."""
    n = len(pts)
    p = f"M {pts[0][0]:.1f},{pts[0][1]:.1f} "
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        p += (f"C {c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} "
              f"{p2[0]:.1f},{p2[1]:.1f} ")
    return p + "Z"


def hex_of(rgb):
    return "#%02X%02X%02X" % rgb


def mark_group(core_fill):
    """SVG inner markup for the mark (blobs + nodes + connectors)."""
    s = ""
    for b in BLOBS:
        s += (f'<path d="{smooth_closed_path(blob_points(b))}" '
              f'fill="{hex_of(b["fill"])}" fill-opacity="0.94"/>\n      ')
    # hairline connectors from core to nodes (generative network hint)
    for nd in NODES:
        x2, y2 = CX + nd["dx"], CY + nd["dy"]
        s += (f'<line x1="{CX}" y1="{CY}" x2="{x2:.0f}" y2="{y2:.0f}" '
              f'stroke="{hex_of(TAUPE)}" stroke-width="2" opacity="0.55"/>\n      ')
    for nd in NODES:
        x2, y2 = CX + nd["dx"], CY + nd["dy"]
        s += (f'<circle cx="{x2:.0f}" cy="{y2:.0f}" r="{nd["r"]}" '
              f'fill="{hex_of(UMBER)}"/>\n      ')
    s += (f'<path d="{smooth_closed_path(blob_points(CORE, n=36))}" '
          f'fill="{hex_of(core_fill)}"/>\n      ')
    # tiny highlight spore inside core
    s += (f'<circle cx="{CX - 30}" cy="{CY - 28}" r="14" '
          f'fill="{hex_of(CREAM)}" opacity="0.85"/>\n      ')
    return s


def lockup_svg(bg, core_fill, word_fill, sub_fill, title):
    mark = mark_group(core_fill)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}">
  <title>{title}</title>
  <desc>Organic overlapping stone-tone blobs forming a bloom-like mark for Loam, a generative intelligence company.</desc>
  <rect width="{W}" height="{H}" fill="{hex_of(bg)}"/>
  <g>
      {mark}
  </g>
  <text x="{CX + 15}" y="948" text-anchor="middle" font-family="Avenir, Futura, 'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="104" font-weight="500" letter-spacing="30" fill="{hex_of(word_fill)}">LOAM</text>
  <text x="{CX + 4}" y="1002" text-anchor="middle" font-family="Avenir, Futura, 'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="27" font-weight="400" letter-spacing="8" fill="{hex_of(sub_fill)}">GENERATIVE INTELLIGENCE</text>
</svg>
'''


# ---------- PNG raster (mark on paper, no type) ----------

def over(dst, src, alpha):
    return src * alpha + dst * (1.0 - alpha)


def render_mark_png(path, size=1000):
    """Software rasterise the mark (bg + 3 blobs + nodes + core) to PNG."""
    sc = size / W
    cx, cy = CX * sc, CY * sc

    # scale blob defs
    def scaled(b):
        c = dict(b)
        c["dx"] *= sc
        c["dy"] *= sc
        c["base"] *= sc
        return c
    blobs = [scaled(b) for b in BLOBS]
    core = scaled(CORE)
    nodes = [{"dx": n["dx"] * sc, "dy": n["dy"] * sc, "r": n["r"] * sc}
             for n in NODES]

    bg = PAPER
    px = bytearray(size * size * 3)
    aa = 1.6 * sc
    for y in range(size):
        yw = y * size * 3
        for x in range(size):
            r, g, bl = bg
            for b in blobs:
                dx = x - (cx + b["dx"])
                dy = y - (cy + b["dy"])
                dist = math.hypot(dx, dy)
                th = math.atan2(dy, dx)
                rr = (b["base"] * (1.0 + b["a1"] * math.sin(b["k1"] * (th - b["rot"]) + b["p1"])
                                  + b["a2"] * math.sin(b["k2"] * (th - b["rot"]) + b["p2"])))
                a = max(0.0, min(1.0, (rr - dist) / aa + 0.5))
                a *= 0.94
                if a > 0.003:
                    fr, fg, fb = b["fill"]
                    r, g, bl = over(r, fr, a), over(g, fg, a), over(bl, fb, a)
            # hairline connectors core -> nodes (under core, like SVG)
            for nd in nodes:
                x1, y1 = cx, cy
                x2, y2 = cx + nd["dx"], cy + nd["dy"]
                vx, vy = x2 - x1, y2 - y1
                L2 = vx * vx + vy * vy
                t = ((x - x1) * vx + (y - y1) * vy) / L2 if L2 else 0.0
                t = max(0.0, min(1.0, t))
                d = math.hypot(x - (x1 + t * vx), y - (y1 + t * vy))
                a = max(0.0, min(1.0, (1.1 * sc - d) / aa + 0.5)) * 0.55
                if a > 0.003:
                    r, g, bl = over(r, TAUPE[0], a), over(g, TAUPE[1], a), over(bl, TAUPE[2], a)
            # core (opaque)
            dx = x - (cx + core["dx"])
            dy = y - (cy + core["dy"])
            dist = math.hypot(dx, dy)
            th = math.atan2(dy, dx)
            rr = (core["base"] * (1.0 + core["a1"] * math.sin(core["k1"] * (th - core["rot"]) + core["p1"])
                                 + core["a2"] * math.sin(core["k2"] * (th - core["rot"]) + core["p2"])))
            a = max(0.0, min(1.0, (rr - dist) / aa + 0.5))
            if a > 0.003:
                r, g, bl = over(r, UMBER[0], a), over(g, UMBER[1], a), over(bl, UMBER[2], a)
            # nodes
            for nd in nodes:
                dx = x - (cx + nd["dx"])
                dy = y - (cy + nd["dy"])
                d = math.hypot(dx, dy)
                a = max(0.0, min(1.0, (nd["r"] - d) / aa + 0.5))
                if a > 0.003:
                    r, g, bl = over(r, UMBER[0], a), over(g, UMBER[1], a), over(bl, UMBER[2], a)
            # highlight spore inside core
            dx = x - (cx + core["dx"] - 30 * sc)
            dy = y - (cy + core["dy"] - 36 * sc)
            d = math.hypot(dx, dy)
            a = max(0.0, min(1.0, (14 * sc - d) / aa + 0.5)) * 0.85
            if a > 0.003:
                r, g, bl = over(r, CREAM[0], a), over(g, CREAM[1], a), over(bl, CREAM[2], a)
            o = yw + x * 3
            px[o] = int(r + 0.5)
            px[o + 1] = int(g + 0.5)
            px[o + 2] = int(bl + 0.5)
        if y % 250 == 0:
            print(f"row {y}/{size}", flush=True)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + bytes(px[y * size * 3:(y + 1) * size * 3])
                   for y in range(size))
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 6)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    print(f"wrote {path} ({len(png) / 1e6:.2f} MB)", flush=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    light = lockup_svg(PAPER, UMBER, INK, TAUPE, "Loam — generative intelligence logo")
    dark = lockup_svg(DARK_BG, CREAM, CREAM, SAND, "Loam — generative intelligence logo (dark)")
    with open(os.path.join(OUT, "loam-logo.svg"), "w") as f:
        f.write(light)
    with open(os.path.join(OUT, "loam-logo-dark.svg"), "w") as f:
        f.write(dark)
    print("wrote SVGs", flush=True)
    render_mark_png(TMP_PNG, size=1000)


if __name__ == "__main__":
    main()
