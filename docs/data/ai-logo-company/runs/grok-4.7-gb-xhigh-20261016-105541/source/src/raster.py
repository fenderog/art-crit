"""Supersampled rasterizer for the Loam logo paths.

Quick Look clips this logo, and ffmpeg has no SVG decoder. The stills and the
motion piece are painted from the same polygons the SVG paths describe.
"""

from __future__ import annotations

import math
import subprocess


def _flat(p0, p1, p2, p3, tol):
    dx = p3[0] - p0[0]
    dy = p3[1] - p0[1]
    length = math.hypot(dx, dy)

    def dist(p):
        if length < 1e-9:
            return math.hypot(p[0] - p0[0], p[1] - p0[1])
        return abs((p[0] - p0[0]) * dy - (p[1] - p0[1]) * dx) / length

    return dist(p1) <= tol and dist(p2) <= tol


def _split(p0, p1, p2, p3):
    def mid(a, b):
        return ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5)

    m01 = mid(p0, p1)
    m12 = mid(p1, p2)
    m23 = mid(p2, p3)
    m012 = mid(m01, m12)
    m123 = mid(m12, m23)
    m = mid(m012, m123)
    return (p0, m01, m012, m), (m, m123, m23, p3)


def _flatten_one(p0, p1, p2, p3, tol, depth=0):
    if depth > 12 or _flat(p0, p1, p2, p3, tol):
        return [p0, p3]
    left, right = _split(p0, p1, p2, p3)
    a = _flatten_one(*left, tol, depth + 1)
    b = _flatten_one(*right, tol, depth + 1)
    return a[:-1] + b


def flatten_cubics(cubics, tol):
    out = []
    for cubic in cubics:
        flat = _flatten_one(*cubic, tol)
        if out and flat:
            flat = flat[1:]
        out.extend(flat)
    if len(out) >= 2:
        if abs(out[0][0] - out[-1][0]) < 1e-6 and abs(out[0][1] - out[-1][1]) < 1e-6:
            out.pop()
    return out


def flatten_catmull(pts, tol=0.2):
    """Closed Catmull–Rom, matching mark_geometry.catmull_rom_path."""
    n = len(pts)
    cubics = []
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        cubics.append((p1, c1, c2, p2))
    return flatten_cubics(cubics, tol)


def flatten_ellipse(cx, cy, rx, ry, tol=0.15):
    """4-cubic ellipse, matching mark_geometry.ellipse_beziers."""
    k = 0.5522847498
    kx, ky = k * rx, k * ry
    right = (cx + rx, cy)
    bottom = (cx, cy + ry)
    left = (cx - rx, cy)
    top = (cx, cy - ry)
    cubics = [
        (right, (cx + rx, cy + ky), (cx + kx, cy + ry), bottom),
        (bottom, (cx - kx, cy + ry), (cx - rx, cy + ky), left),
        (left, (cx - rx, cy - ky), (cx - kx, cy - ry), top),
        (top, (cx + kx, cy - ry), (cx + rx, cy - ky), right),
    ]
    return flatten_cubics(cubics, tol)


def hex_rgb(color):
    h = color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _blend(buf, start, end, rgb, alpha):
    inv = 1.0 - alpha
    br, bg, bb = rgb
    for i in range(start, end, 3):
        buf[i] = int(buf[i] * inv + br * alpha + 0.5)
        buf[i + 1] = int(buf[i + 1] * inv + bg * alpha + 0.5)
        buf[i + 2] = int(buf[i + 2] * inv + bb * alpha + 0.5)


def _edges(polys, sx, sy):
    edges = []
    for poly in polys:
        n = len(poly)
        if n < 3:
            continue
        for i in range(n):
            x0 = poly[i][0] * sx
            y0 = poly[i][1] * sy
            j = (i + 1) % n
            x1 = poly[j][0] * sx
            y1 = poly[j][1] * sy
            if abs(y1 - y0) < 1e-6:
                continue
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            edges.append((y0, y1, x0, (x1 - x0) / (y1 - y0)))
    edges.sort()
    return edges


def paint(buf, pix_w, pix_h, polys, rgb, alpha, sx, sy):
    """Even-odd fill of polygon subpaths into an RGB buffer."""
    edges = _edges(polys, sx, sy)
    if not edges:
        return
    y_start = max(0, int(math.floor(edges[0][0] - 0.5)))
    y_last = max(e[1] for e in edges)
    y_end = min(pix_h - 1, int(math.ceil(y_last + 0.5)))
    active = []
    ei = 0
    nedges = len(edges)
    solid = alpha >= 0.999
    color = bytes(rgb)
    for y in range(y_start, y_end + 1):
        ys = y + 0.5
        while ei < nedges and edges[ei][0] <= ys:
            active.append(edges[ei])
            ei += 1
        if active:
            active = [e for e in active if e[1] > ys]
        if len(active) < 2:
            continue
        xs = [e[2] + e[3] * (ys - e[0]) for e in active]
        xs.sort()
        row = y * pix_w
        for i in range(0, len(xs) - 1, 2):
            x0 = max(0, math.ceil(xs[i] - 0.5))
            x1 = min(pix_w, math.floor(xs[i + 1] - 0.5) + 1)
            if x1 <= x0:
                continue
            start = (row + x0) * 3
            end = (row + x1) * 3
            if solid:
                buf[start:end] = color * (x1 - x0)
            else:
                _blend(buf, start, end, rgb, alpha)


def paint_union(buf, pix_w, pix_h, items, rgb, alpha, sx, sy):
    """Fill a group once, so overlapping parts don't darken at partial alpha."""
    if alpha >= 0.999:
        for item in items:
            paint(buf, pix_w, pix_h, item.polys, rgb, 1.0, sx, sy)
        return
    minx = min(x for item in items for poly in item.polys for x, _y in poly)
    miny = min(y for item in items for poly in item.polys for _x, y in poly)
    maxx = max(x for item in items for poly in item.polys for x, _y in poly)
    maxy = max(y for item in items for poly in item.polys for _x, y in poly)
    x0 = max(0, int(math.floor(minx * sx)) - 2)
    y0 = max(0, int(math.floor(miny * sy)) - 2)
    x1 = min(pix_w, int(math.ceil(maxx * sx)) + 2)
    y1 = min(pix_h, int(math.ceil(maxy * sy)) + 2)
    mw, mh = x1 - x0, y1 - y0
    if mw <= 0 or mh <= 0:
        return
    mask = bytearray(mw * mh)
    solid = b"\x01"
    for item in items:
        edges = _edges(item.polys, sx, sy)
        if not edges:
            continue
        y_start = max(y0, int(math.floor(edges[0][0] - 0.5)))
        y_last = max(e[1] for e in edges)
        y_end = min(y1 - 1, int(math.ceil(y_last + 0.5)))
        active = []
        ei = 0
        nedges = len(edges)
        for y in range(y_start, y_end + 1):
            ys = y + 0.5
            while ei < nedges and edges[ei][0] <= ys:
                active.append(edges[ei])
                ei += 1
            if active:
                active = [e for e in active if e[1] > ys]
            if len(active) < 2:
                continue
            xs = [e[2] + e[3] * (ys - e[0]) for e in active]
            xs.sort()
            row = (y - y0) * mw
            for i in range(0, len(xs) - 1, 2):
                a = max(x0, math.ceil(xs[i] - 0.5))
                b = min(x1, math.floor(xs[i + 1] - 0.5) + 1)
                if b > a:
                    mask[row + (a - x0) : row + (b - x0)] = solid * (b - a)
    br, bg, bb = rgb
    inv = 1.0 - alpha
    for yy in range(mh):
        mrow = yy * mw
        brow = (y0 + yy) * pix_w + x0
        xx = 0
        while xx < mw:
            if not mask[mrow + xx]:
                xx += 1
                continue
            end = xx + 1
            while end < mw and mask[mrow + end]:
                end += 1
            for k in range(xx, end):
                i = (brow + k) * 3
                buf[i] = int(buf[i] * inv + br * alpha + 0.5)
                buf[i + 1] = int(buf[i + 1] * inv + bg * alpha + 0.5)
                buf[i + 2] = int(buf[i + 2] * inv + bb * alpha + 0.5)
            xx = end


def render(items, user_w, user_h, pix_w, pix_h, background):
    bg = hex_rgb(background)
    buf = bytearray(bytes(bg) * (pix_w * pix_h))
    sx = pix_w / user_w
    sy = pix_h / user_h
    i = 0
    n = len(items)
    while i < n:
        item = items[i]
        alpha = getattr(item, "alpha", 1.0)
        if alpha <= 0.001:
            i += 1
            continue
        group = getattr(item, "group", None)
        if not group:
            paint(buf, pix_w, pix_h, item.polys, hex_rgb(item.fill), alpha, sx, sy)
            i += 1
            continue
        j = i + 1
        while (
            j < n
            and getattr(items[j], "group", None) == group
            and items[j].fill == item.fill
            and abs(getattr(items[j], "alpha", 1.0) - alpha) < 1e-6
        ):
            j += 1
        paint_union(buf, pix_w, pix_h, items[i:j], hex_rgb(item.fill), alpha, sx, sy)
        i = j
    return buf


def write_png(buf, src_w, src_h, path, out_w, out_h):
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{src_w}x{src_h}", "-i", "pipe:0", "-frames:v", "1",
    ]
    if (src_w, src_h) != (out_w, out_h):
        cmd += ["-vf", f"scale={out_w}:{out_h}:flags=lanczos"]
    cmd += ["-an", str(path)]
    proc = subprocess.run(cmd, input=bytes(buf), capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode()[-2000:])


def rasterize(items, viewbox, png_path, long_edge, background, ss=4):
    _x, _y, user_w, user_h = viewbox
    scale = long_edge / max(user_w, user_h)
    out_w = max(1, int(round(user_w * scale)))
    out_h = max(1, int(round(user_h * scale)))
    hi_w, hi_h = out_w * ss, out_h * ss
    buf = render(items, user_w, user_h, hi_w, hi_h, background)
    write_png(buf, hi_w, hi_h, png_path, out_w, out_h)
    return out_w, out_h


def content_box(path, tol=18):
    """Bounding box of pixels that differ from the top-left corner."""
    info = subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path),
        ],
        text=True,
    ).strip()
    w, h = (int(float(v)) for v in info.split(","))
    raw = subprocess.check_output(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"]
    )
    if len(raw) != w * h * 3:
        raise RuntimeError(f"raw size {len(raw)} != {w * h * 3}")
    br, bg, bb = raw[0], raw[1], raw[2]
    minx, miny, maxx, maxy = w, h, -1, -1
    for y in range(h):
        row = y * w * 3
        for x in range(w):
            i = row + x * 3
            if abs(raw[i] - br) + abs(raw[i + 1] - bg) + abs(raw[i + 2] - bb) > tol:
                if x < minx:
                    minx = x
                if x > maxx:
                    maxx = x
                if y < miny:
                    miny = y
                if y > maxy:
                    maxy = y
    return w, h, (minx, miny, maxx, maxy), raw
