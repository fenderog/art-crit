#!/usr/bin/env python3
"""Pure-stdlib rasterizer for the forma mark (preview + PNG export).

Renders organic petal polygons with scanline fill, vertical gradients
and supersampled anti-aliasing. Also writes PNG (zlib/struct only).
"""
import math, struct, zlib

# ---------- palette (neutral, warm) ----------
PAPER = (243, 240, 233)
INK = (36, 34, 31)
STONE_DARK = (92, 88, 82)
TAUPE = (167, 158, 147)
SAND = (201, 185, 154)
LIGHT = (217, 210, 197)
CLAY = (184, 174, 160)

def cubic(p0, p1, p2, p3, n=28):
    pts = []
    for i in range(n):
        t = i / n
        mt = 1 - t
        x = mt**3*p0[0] + 3*mt*mt*t*p1[0] + 3*mt*t*t*p2[0] + t**3*p3[0]
        y = mt**3*p0[1] + 3*mt*mt*t*p1[1] + 3*mt*t*t*p2[1] + t**3*p3[1]
        pts.append((x, y))
    return pts

def petal_polygon(cx=320.0, cy=320.0, squash=1.0, lean=0.0):
    """Return sampled polygon for one petal pointing up."""
    b = (cx, cy + 16)
    # left side up to tip
    left = cubic(b, (cx - 74, cy - 30), (cx - 78, cy - 140), (cx - 18, cy - 214))
    # tip cap
    tip = cubic((cx - 18, cy - 214), (cx - 4, cy - 238), (cx + 30, cy - 236), (cx + 44, cy - 196))
    # right side down to base
    right = cubic((cx + 44, cy - 196), (cx + 62, cy - 120), (cx + 44, cy - 44), (cx + 4, cy + 10))
    # base cap back to start
    base = cubic((cx + 4, cy + 10), (cx - 2, cy + 20), (cx - 4, cy + 20), b)
    poly = left + tip + right + base
    # apply lean (shear x by y offset) + squash
    out = []
    for (x, y) in poly:
        dy = (cy - y)
        nx = cx + (x - cx) * squash + lean * dy * 0.12
        ny = cy - dy * (2 - squash) * 0.92 if False else y
        out.append((nx, ny))
    return out

def rotate(poly, cx, cy, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x-cx)*ca - (y-cy)*sa, cy + (x-cx)*sa + (y-cy)*ca) for (x, y) in poly]

def blob_polygon(cx, cy, r, wobble, phase=0.0, n=140):
    pts = []
    for i in range(n):
        t = i / n * math.tau
        rr = r * (1 + wobble[0]*math.sin(2*t+phase) + wobble[1]*math.sin(3*t+phase*1.7)
                  + wobble[2]*math.sin(5*t+phase*0.6))
        pts.append((cx + rr*math.cos(t), cy + rr*math.sin(t)*0.96))
    return pts

# ---------- scanline fill ----------
def fill_poly(img, W, H, poly, color_fn, alpha=1.0):
    """color_fn(x,y, coverage)->(r,g,b) or constant tuple; scanline with 1px AA via coverage."""
    ys = [p[1] for p in poly]
    y0 = max(0, int(math.floor(min(ys))))
    y1 = min(H - 1, int(math.ceil(max(ys))))
    n = len(poly)
    edges = [(poly[i], poly[(i + 1) % n]) for i in range(n)]
    for y in range(y0, y1 + 1):
        yc = y + 0.5
        xs = []
        for (x1, yy1), (x2, yy2) in edges:
            if (yy1 <= yc < yy2) or (yy2 <= yc < yy1):
                if yy2 == yy1:
                    continue
                xs.append(x1 + (yc - yy1) * (x2 - x1) / (yy2 - yy1))
        xs.sort()
        row = img[y]
        for k in range(0, len(xs) - 1, 2):
            xa, xb = xs[k], xs[k + 1]
            x_start = max(0, int(math.floor(xa)))
            x_end = min(W - 1, int(math.ceil(xb)))
            for x in range(x_start, x_end + 1):
                # coverage: fraction of pixel [x,x+1] inside [xa,xb]
                cov = min(x + 1.0, xb) - max(float(x), xa)
                if cov <= 0:
                    continue
                cov = min(1.0, cov) * alpha
                c = color_fn(x, y) if callable(color_fn) else color_fn
                px = row[x]
                row[x] = (px[0] + (c[0] - px[0]) * cov,
                          px[1] + (c[1] - px[1]) * cov,
                          px[2] + (c[2] - px[2]) * cov)

def fill_circle(img, W, H, cx, cy, r, color, alpha=1.0):
    x0, x1 = max(0, int(cx - r - 1)), min(W - 1, int(cx + r + 1))
    y0, y1 = max(0, int(cy - r - 1)), min(H - 1, int(cy + r + 1))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            # 2x2 subpixel coverage
            cov = 0
            for sy in (0.25, 0.75):
                for sx in (0.25, 0.75):
                    dx, dy = x + sx - cx, y + sy - cy
                    if dx*dx + dy*dy <= r*r:
                        cov += 1
            if cov == 0:
                continue
            a = cov / 4.0 * alpha
            px = img[y][x]
            img[y][x] = (px[0] + (color[0]-px[0])*a, px[1] + (color[1]-px[1])*a, px[2] + (color[2]-px[2])*a)

def lerp(c1, c2, t):
    return (c1[0] + (c2[0]-c1[0])*t, c1[1] + (c2[1]-c1[1])*t, c1[2] + (c2[2]-c1[2])*t)

def grad_fn(top, bottom, y_top, y_bot):
    def f(x, y):
        t = (y - y_top) / max(1.0, (y_bot - y_top))
        t = min(1.0, max(0.0, t))
        return lerp(top, bottom, t)
    return f

# ---------- PNG write ----------
def write_png(path, img, W, H):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        row = img[y]
        for x in range(W):
            r, g, b = row[x]
            raw += bytes((max(0, min(255, round(r))), max(0, min(255, round(g))), max(0, min(255, round(b)))))
    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff)
        return c
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 6)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

def downscale(img, W, H, SS):
    if SS == 1:
        return img, W, H
    ow, oh = W // SS, H // SS
    out = [[(0.0, 0.0, 0.0)] * ow for _ in range(oh)]
    inv = 1.0 / (SS * SS)
    for oy in range(oh):
        for ox in range(ow):
            r = g = b = 0.0
            for dy in range(SS):
                row = img[oy*SS+dy]
                for dx in range(SS):
                    p = row[ox*SS+dx]
                    r += p[0]; g += p[1]; b += p[2]
            out[oy][ox] = (r*inv, g*inv, b*inv)
    return out, ow, oh

def render_mark(size=960, SS=2, bg=PAPER, dark=False, morph=0.0):
    """morph in [0,1] subtly breathes petal angles for animation."""
    W = H = size * SS
    s = W / 640.0  # scale from 640 design space
    def S(poly):
        return [(x*s, y*s) for (x, y) in poly]
    bgc = (INK if dark else PAPER)
    img = [[(float(bgc[0]), float(bgc[1]), float(bgc[2]))] * W for _ in range(H)]
    cx = cy = 320.0
    breathe = math.sin(morph * math.tau) if morph else 0.0
    # overlapping amoeba lobes (cell cluster / bloom) — asymmetric sizes kill the propeller read
    lobes = [
        # (centre, radius, wobble, phase, top colour, bottom colour, alpha)
        ((318, 208), 104, (0.07, 0.045, 0.02), 0.4, (122, 116, 108), (178, 169, 155), 0.96),
        ((208, 340), 118, (0.06, 0.05, 0.018), 2.3, (146, 137, 124), (196, 186, 170), 0.96),
        ((392, 364), 94, (0.075, 0.04, 0.022), 4.2, (182, 171, 152), (222, 215, 201), 0.96),
        ((428, 246), 40, (0.06, 0.04, 0.02), 1.1, (140, 132, 120), (186, 177, 162), 0.95),
    ]
    for (lc, r, wob, ph, top, bottom, al) in lobes:
        rr = r * (1 + breathe * 0.02)
        poly = blob_polygon(lc[0], lc[1], rr, wob, phase=ph + morph * 1.5)
        t, b = (bottom, top) if dark else (top, bottom)
        fill_poly(img, W, H, S(poly), grad_fn(t, b, (lc[1]-r)*s, (lc[1]+r)*s), al)
    # single detached spore — what the form has generated
    fill_circle(img, W, H, 486*s, 176*s, 11*s, STONE_DARK if not dark else (216, 209, 196), 0.9)
    # centre seed — small paper fleck + ink nucleus where the lobes meet
    seed = blob_polygon(318, 308, 19, (0.05, 0.04, 0.02), phase=1.2)
    fill_poly(img, W, H, S(seed), PAPER if not dark else (30, 28, 26), 1.0)
    fill_circle(img, W, H, 321*s, 305*s, 7.5*s, INK if not dark else (234, 228, 216), 1.0)
    img, ow, oh = downscale(img, W, H, SS)
    return img, ow, oh

if __name__ == "__main__":
    import os
    os.makedirs("/tmp/preview", exist_ok=True)
    img, w, h = render_mark(900, SS=2)
    n = write_png("/tmp/preview/mark-light.png", img, w, h)
    print("light", w, h, n)
    img, w, h = render_mark(900, SS=2, dark=True)
    n = write_png("/tmp/preview/mark-dark.png", img, w, h)
    print("dark", w, h, n)
