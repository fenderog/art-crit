#!/usr/bin/env python3
"""Build an organic, neutral-toned logo mark.

The mark is a set of nested iso-contours of a metaball field. Each contour
level is filled with one tone of a stone/sand palette: the outer bands read as
a pebble, the inner bands as a generated core.

Writes output/logo.svg (vector master) and output/logo.png (a preview rendered
from the same geometry with the standard library only).

Usage: python3 make_logo.py
"""

import math
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "output")

SIZE = 1024            # canvas edge in px
CENTER = SIZE / 2
SCALE = 400.0          # px per field unit
GRID_N = 520           # marching-squares samples per axis
EXTENT = 1.2           # field sampled over [-EXTENT, EXTENT]^2
SIMPLIFY_PX = 0.35     # Ramer-Douglas-Peucker tolerance in px
SUPERSAMPLE = 4        # sub-scanlines per pixel row in the PNG preview

# Metaball sources as (x, y, radius) in field units (y points up).
BLOBS = [
    (-0.10, -0.02, 0.55),
    (0.38, 0.30, 0.30),
    (-0.42, 0.42, 0.18),
    (0.22, -0.42, 0.22),
]

# Nested levels, outermost first: (iso threshold, fill colour).
LEVELS = [
    (0.40, "#E4DBCB"),  # bone
    (0.80, "#BFB4A3"),  # stone
    (1.40, "#8C7F70"),  # taupe
    (2.90, "#4A433C"),  # umber
]

# Marching-squares case table. Cell corners: c0 bottom-left, c1 bottom-right,
# c2 top-right, c3 top-left (bit k set = corner k is inside the level).
# Edges: 0 bottom, 1 right, 2 top, 3 left. Saddles (5, 10) are in the code below.
CASE_EDGES = {
    1: [(3, 0)], 2: [(0, 1)], 3: [(3, 1)], 4: [(1, 2)], 6: [(0, 2)],
    7: [(2, 3)], 8: [(2, 3)], 9: [(0, 2)], 11: [(1, 2)], 12: [(3, 1)],
    13: [(0, 1)], 14: [(3, 0)],
}


def field(x, y):
    total = 0.0
    for bx, by, r in BLOBS:
        dx = x - bx
        dy = y - by
        total += r * r / (dx * dx + dy * dy + 1e-9)
    return total


def sample_field():
    h = 2 * EXTENT / (GRID_N - 1)
    xs = [-EXTENT + i * h for i in range(GRID_N)]
    ys = [-EXTENT + j * h for j in range(GRID_N)]
    vals = [[field(x, y) for x in xs] for y in ys]  # vals[row j][col i]
    return xs, ys, h, vals


def contour_loops(xs, ys, h, vals, t):
    """Closed boundary loops of {field >= t}, in field units."""
    adj = {}

    def link(a, b):
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)

    def point(key):
        kind, i, j = key
        if kind == "h":
            a, b = vals[j][i], vals[j][i + 1]
            return (xs[i] + (t - a) / (b - a) * h, ys[j])
        a, b = vals[j][i], vals[j + 1][i]
        return (xs[i], ys[j] + (t - a) / (b - a) * h)

    for j in range(GRID_N - 1):
        r0, r1 = vals[j], vals[j + 1]
        for i in range(GRID_N - 1):
            c0, c1, c2, c3 = r0[i], r0[i + 1], r1[i + 1], r1[i]
            code = (int(c0 >= t) | int(c1 >= t) << 1
                    | int(c2 >= t) << 2 | int(c3 >= t) << 3)
            if code in (0, 15):
                continue
            e = (("h", i, j), ("v", i + 1, j), ("h", i, j + 1), ("v", i, j))
            if code == 5:
                inside = (c0 + c1 + c2 + c3) / 4 >= t
                pairs = [(0, 1), (2, 3)] if inside else [(3, 0), (1, 2)]
            elif code == 10:
                inside = (c0 + c1 + c2 + c3) / 4 >= t
                pairs = [(3, 0), (1, 2)] if inside else [(0, 1), (2, 3)]
            else:
                pairs = CASE_EDGES[code]
            for a, b in pairs:
                link(e[a], e[b])

    loops = []
    visited = set()
    for start in adj:
        if start in visited:
            continue
        keys = [start]
        visited.add(start)
        prev, cur = None, start
        while True:
            nb = adj[cur]
            if len(nb) != 2:
                raise RuntimeError("open contour: enlarge EXTENT")
            nxt = nb[0] if nb[0] != prev else nb[1]
            if nxt == start:
                break
            keys.append(nxt)
            visited.add(nxt)
            prev, cur = cur, nxt
        loops.append([point(k) for k in keys])
    return loops


def _rdp(points, eps):
    """Ramer-Douglas-Peucker on an open polyline (endpoints kept)."""
    n = len(points)
    if n < 3:
        return list(points)
    keep = [False] * n
    keep[0] = keep[-1] = True
    stack = [(0, n - 1)]
    while stack:
        s, e = stack.pop()
        ax, ay = points[s]
        bx, by = points[e]
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy)
        best, idx = 0.0, -1
        for k in range(s + 1, e):
            px, py = points[k]
            if length == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                d = abs(dy * (px - ax) - dx * (py - ay)) / length
            if d > best:
                best, idx = d, k
        if idx != -1 and best > eps:
            keep[idx] = True
            stack.append((s, idx))
            stack.append((idx, e))
    return [p for p, k in zip(points, keep) if k]


def simplify_closed(pts, eps):
    """Simplify a closed loop by splitting it at the point farthest from pts[0]."""
    if len(pts) < 4:
        return pts
    p0 = pts[0]
    far = max(range(len(pts)), key=lambda k: math.hypot(pts[k][0] - p0[0], pts[k][1] - p0[1]))
    run_a = _rdp(pts[: far + 1], eps)[:-1]
    run_b = _rdp(pts[far:] + [p0], eps)[:-1]
    return run_a + run_b


def _fmt(v):
    return f"{v:.1f}"


def write_svg(path, layers):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<!-- Generated by make_logo.py -->",
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" '
        f'viewBox="0 0 {SIZE} {SIZE}" role="img" aria-label="Organic generative mark">',
    ]
    for colour, loops in layers:
        d = []
        for loop in loops:
            seg = [("M" if k == 0 else "L") + _fmt(x) + " " + _fmt(y)
                   for k, (x, y) in enumerate(loop)]
            d.append("".join(seg) + "Z")
        lines.append(f'  <path fill="{colour}" fill-rule="evenodd" d="{"".join(d)}"/>')
    lines.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _add_span(cov, a, b, weight):
    if a < 0.0:
        a = 0.0
    if b > SIZE:
        b = float(SIZE)
    if b <= a:
        return
    p0, p1 = int(a), int(b)
    if p0 == p1:
        cov[p0] += (b - a) * weight
        return
    cov[p0] += (p0 + 1 - a) * weight
    for p in range(p0 + 1, p1):
        cov[p] += weight
    if p1 < SIZE:
        cov[p1] += (b - p1) * weight


def rasterize_rows(layers):
    """Yield RGBA rows (non-premultiplied) of the even-odd filled layers."""
    colours = [tuple(int(c[k:k + 2], 16) / 255 for k in (1, 3, 5)) for c, _ in layers]
    buckets = []
    for _, loops in layers:
        rows = [[] for _ in range(SIZE)]
        for loop in loops:
            n = len(loop)
            for k in range(n):
                x0, y0 = loop[k]
                x1, y1 = loop[(k + 1) % n]
                if y0 == y1:
                    continue
                if y0 > y1:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                slope = (x1 - x0) / (y1 - y0)
                for r in range(max(0, int(y0)), min(SIZE - 1, int(y1)) + 1):
                    rows[r].append((x0, y0, y1, slope))
        buckets.append(rows)

    inv = 1.0 / SUPERSAMPLE
    for r in range(SIZE):
        pr = [0.0] * SIZE
        pg = [0.0] * SIZE
        pb = [0.0] * SIZE
        pa = [0.0] * SIZE
        for (R, G, B), rows in zip(colours, buckets):
            cov = [0.0] * SIZE
            for s in range(SUPERSAMPLE):
                y = r + (s + 0.5) * inv
                hits = sorted(x0 + (y - y0) * slope
                              for x0, y0, y1, slope in rows[r] if y0 <= y < y1)
                for k in range(0, len(hits) - 1, 2):
                    _add_span(cov, hits[k], hits[k + 1], inv)
            for px in range(SIZE):
                a = cov[px]
                if a <= 0.0:
                    continue
                if a > 1.0:
                    a = 1.0
                keep = 1.0 - a
                pr[px] = R * a + pr[px] * keep
                pg[px] = G * a + pg[px] * keep
                pb[px] = B * a + pb[px] * keep
                pa[px] = a + pa[px] * keep
        row = bytearray(4 * SIZE)
        for px in range(SIZE):
            A = pa[px]
            if A <= 0.0:
                continue
            o = 4 * px
            row[o] = min(255, round(pr[px] / A * 255))
            row[o + 1] = min(255, round(pg[px] / A * 255))
            row[o + 2] = min(255, round(pb[px] / A * 255))
            row[o + 3] = round(A * 255)
        yield row


def write_png(path, rows):
    def chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    raw = b"".join(b"\x00" + bytes(row) for row in rows)
    ihdr = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0)  # 8-bit RGBA
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    xs, ys, h, vals = sample_field()
    layers = []
    for threshold, colour in LEVELS:
        loops = []
        for loop in contour_loops(xs, ys, h, vals, threshold):
            pts = [(CENTER + x * SCALE, CENTER - y * SCALE) for x, y in loop]
            loops.append(simplify_closed(pts, SIMPLIFY_PX))
        layers.append((colour, loops))
        print(f"level {threshold:.2f} {colour}: {len(loops)} loop(s), "
              f"{sum(len(l) for l in loops)} points")

    write_svg(os.path.join(OUT_DIR, "logo.svg"), layers)
    write_png(os.path.join(OUT_DIR, "logo.png"), rasterize_rows(layers))
    print("wrote output/logo.svg and output/logo.png")


if __name__ == "__main__":
    main()
