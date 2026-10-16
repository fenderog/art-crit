#!/usr/bin/env python3
"""Rasterize LOAM lockups to transparent PNG and a six-second ident.

Pure Python (no third-party packages). Frames go to preview/frames and are
deleted after ffmpeg encodes the mp4.
"""

from __future__ import annotations

import math
import os
import struct
import subprocess
import zlib

from build_logo import (
    CAP,
    DARK,
    INK,
    PAPER,
    bounds,
    horizontal,
    loam_mark,
    normalize,
    scale_about,
    translate,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")
FRAMES = os.path.join(ROOT, "preview", "frames")


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def write_png(path, w, h, rgba):
    def chunk(tag, data):
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    raw = bytearray()
    stride = w * 4
    for y in range(h):
        raw.append(0)
        raw.extend(rgba[y * stride : (y + 1) * stride])
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )
    with open(path, "wb") as f:
        f.write(png)


def flatten(loops, samples=8):
    """Smooth loops become polygons. Sharp loops stay as drawn."""
    polys = []
    for lp in loops:
        if lp.smooth and len(lp.pts) >= 4:
            pts = lp.pts
            n = len(pts)
            poly = []
            for i in range(n):
                p0, p1 = pts[(i - 1) % n], pts[i]
                p2, p3 = pts[(i + 1) % n], pts[(i + 2) % n]
                b1 = (
                    p1[0] + (p2[0] - p0[0]) / 6,
                    p1[1] + (p2[1] - p0[1]) / 6,
                )
                b2 = (
                    p2[0] - (p3[0] - p1[0]) / 6,
                    p2[1] - (p3[1] - p1[1]) / 6,
                )
                # sample the cubic, skip t=1 (next segment starts there)
                for s in range(samples):
                    t = s / samples
                    u = 1 - t
                    x = (
                        u ** 3 * p1[0]
                        + 3 * u * u * t * b1[0]
                        + 3 * u * t * t * b2[0]
                        + t ** 3 * p2[0]
                    )
                    y = (
                        u ** 3 * p1[1]
                        + 3 * u * u * t * b1[1]
                        + 3 * u * t * t * b2[1]
                        + t ** 3 * p2[1]
                    )
                    poly.append((x, y))
            polys.append(poly)
        else:
            polys.append(list(lp.pts))
    return polys


def paint(buf, W, H, polys, color):
    """Even-odd fill. `color` is an RGBA tuple. Replaces covered pixels."""
    edges = []
    for poly in polys:
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            if y1 == y2:
                continue
            if y1 > y2:
                x1, y1, x2, y2 = x2, y2, x1, y1
            edges.append((y1, y2, x1, (x2 - x1) / (y2 - y1)))
    cr, cg, cb, ca = color
    pix = bytes((cr, cg, cb, ca))
    for y in range(H):
        ymid = y + 0.5
        xs = [x + dx * (ymid - y0) for y0, y1, x, dx in edges if y0 <= ymid < y1]
        if not xs:
            continue
        xs.sort()
        row = y * W * 4
        for x0, x1 in zip(xs[0::2], xs[1::2]):
            a = 0 if x0 < 0 else int(x0)
            b = W if x1 > W else int(math.ceil(x1))
            if b > a:
                buf[row + a * 4 : row + b * 4] = pix * (b - a)


def downsample(src, W, H, ss):
    w, h = W // ss, H // ss
    out = bytearray(w * h * 4)
    n = ss * ss
    for y in range(h):
        for x in range(w):
            ar = ag = ab = aa = 0
            for sy in range(ss):
                base = ((y * ss + sy) * W + x * ss) * 4
                for sx in range(ss):
                    i = base + sx * 4
                    a = src[i + 3]
                    ar += src[i] * a
                    ag += src[i + 1] * a
                    ab += src[i + 2] * a
                    aa += a
            o = (y * w + x) * 4
            if aa:
                out[o] = ar // aa
                out[o + 1] = ag // aa
                out[o + 2] = ab // aa
                out[o + 3] = aa // n
    return out


def map_polys(polys, scale, ox, oy, maxy, ss):
    """y-up design → supersampled screen pixels (y down)."""
    out = []
    for poly in polys:
        out.append(
            [
                ((x * scale + ox) * ss, (oy + (maxy - y) * scale) * ss)
                for x, y in poly
            ]
        )
    return out


def render_lockup_png(path, loops, width_px, ss=3):
    norm, w, h = normalize(loops, 0)
    height_px = max(1, round(width_px * h / w))
    # keep even
    if width_px % 2:
        width_px += 1
    if height_px % 2:
        height_px += 1
    W, H = width_px * ss, height_px * ss
    buf = bytearray(W * H * 4)
    polys = flatten(norm)
    # norm is y-up with origin at min corner. Screen: y flips within H.
    mapped = []
    for poly in polys:
        mapped.append([((x / w) * W, (1 - y / h) * H) for x, y in poly])
    paint(buf, W, H, mapped, (*hex_rgb(INK), 255))
    write_png(path, width_px, height_px, downsample(buf, W, H, ss))
    print(path, os.path.getsize(path))


def ease_out(t):
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return 1 - (1 - t) ** 3


def window(t, a, b):
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    return ease_out((t - a) / (b - a))


def centroid(pts):
    return (
        sum(p[0] for p in pts) / len(pts),
        sum(p[1] for p in pts) / len(pts),
    )


def render_ident():
    os.makedirs(FRAMES, exist_ok=True)
    mark, words = horizontal()
    # Shared design bounds of the final lockup, used for the whole animation
    # so the mark never slides when the word appears.
    minx, miny, maxx, maxy = bounds(mark + words)
    frame_w, frame_h = 1280, 720
    ss = 2
    W, H = frame_w * ss, frame_h * ss
    dw = maxx - minx
    scale = (frame_w * 0.60) / dw
    pw = dw * scale
    ph = (maxy - miny) * scale
    ox = (frame_w - pw) / 2 - minx * scale
    oy = (frame_h - ph) / 2  # screen y of design maxy

    mark_poly = flatten(mark, samples=6)
    word_poly = flatten(words, samples=6)
    hole_pts = mark[1].pts
    hole_c = centroid(hole_pts)
    outer_only = flatten(mark[:1], samples=6)
    hole_flat = flatten([mark[1]], samples=6)[0]

    ink = hex_rgb(INK)
    paper = hex_rgb(PAPER)
    bg = bytes((*paper, 255))
    paper_px = (*paper, 255)
    fps = 24
    duration = 6.0
    nframes = int(fps * duration)

    def blit_color(alpha):
        a = alpha
        return (
            int(ink[0] * a + paper[0] * (1 - a)),
            int(ink[1] * a + paper[1] * (1 - a)),
            int(ink[2] * a + paper[2] * (1 - a)),
            255,
        )

    for i in range(nframes):
        t = i / fps
        buf = bytearray(bg * (W * H))

        mark_a = window(t, 0.25, 1.15)
        hole_k = window(t, 1.15, 1.95)
        word_a = window(t, 2.05, 3.25)
        word_rise = (1 - word_a) * -28.0  # design units, y-up; settles to 0

        if mark_a > 0.001:
            s = 0.97 + 0.03 * mark_a
            c = centroid(mark[0].pts)
            scaled_outer = []
            for poly in outer_only:
                scaled_outer.append(
                    [
                        ((x - c[0]) * s + c[0], (y - c[1]) * s + c[1])
                        for x, y in poly
                    ]
                )
            paint(
                buf,
                W,
                H,
                map_polys(scaled_outer, scale, ox, oy, maxy, ss),
                blit_color(mark_a),
            )
            if hole_k > 0.004 and mark_a > 0.98:
                hk = hole_k
                hole_scaled = [
                    ((x - hole_c[0]) * hk + hole_c[0], (y - hole_c[1]) * hk + hole_c[1])
                    for x, y in hole_flat
                ]
                paint(
                    buf,
                    W,
                    H,
                    map_polys([hole_scaled], scale, ox, oy, maxy, ss),
                    paper_px,
                )

        if word_a > 0.001:
            moved = []
            for poly in word_poly:
                moved.append([(x, y + word_rise) for x, y in poly])
            paint(buf, W, H, map_polys(moved, scale, ox, oy, maxy, ss), blit_color(word_a))

        small = downsample(buf, W, H, ss)
        write_png(os.path.join(FRAMES, f"{i:04d}.png"), frame_w, frame_h, small)
        if i % 12 == 0:
            print(f"frame {i}/{nframes}")

    mp4 = os.path.join(OUT, "loam-ident.mp4")
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(fps),
            "-i",
            os.path.join(FRAMES, "%04d.png"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "18",
            "-movflags",
            "+faststart",
            mp4,
        ]
    )
    print(mp4, os.path.getsize(mp4))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    mark = loam_mark()
    hm, hw = horizontal()
    render_lockup_png(os.path.join(OUT, "loam-mark.png"), mark, 1400, ss=3)
    render_lockup_png(os.path.join(OUT, "loam-lockup.png"), hm + hw, 2200, ss=2)
    render_ident()
