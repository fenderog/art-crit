"""Organic blob geometry: smooth closed shapes from a handful of perturbed radii."""
import math
import random


def _fmt(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def blob_points(cx, cy, rx, ry, rot=0.0, n=7, amp=0.12, seed=0, phase=0.0):
    """Points around an ellipse with a smooth, seeded radial wobble."""
    rng = random.Random(seed)
    wob = [rng.uniform(-1, 1) for _ in range(n)]
    pts = []
    cr, sr = math.cos(rot), math.sin(rot)
    for i in range(n):
        t = 2 * math.pi * i / n + phase
        k = 1 + amp * wob[i]
        x, y = rx * k * math.cos(t), ry * k * math.sin(t)
        pts.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return pts


def lerp_points(a, b, t):
    return [(ax + (bx - ax) * t, ay + (by - ay) * t) for (ax, ay), (bx, by) in zip(a, b)]


def smooth_path(pts, tension=1.0):
    """Closed Catmull-Rom spline converted to cubic Beziers."""
    n = len(pts)
    d = [f"M{_fmt(pts[0][0])} {_fmt(pts[0][1])}"]
    for i in range(n):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6 * tension, p1[1] + (p2[1] - p0[1]) / 6 * tension)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6 * tension, p2[1] - (p3[1] - p1[1]) / 6 * tension)
        d.append(
            f"C{_fmt(c1[0])} {_fmt(c1[1])} {_fmt(c2[0])} {_fmt(c2[1])} {_fmt(p2[0])} {_fmt(p2[1])}"
        )
    d.append("Z")
    return "".join(d)


def spline_samples(pts, per_seg=24, tension=1.0):
    """Dense samples along the same closed spline (for exact bounding boxes)."""
    n = len(pts)
    out = []
    for i in range(n):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6 * tension, p1[1] + (p2[1] - p0[1]) / 6 * tension)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6 * tension, p2[1] - (p3[1] - p1[1]) / 6 * tension)
        for k in range(per_seg):
            t = k / per_seg
            u = 1 - t
            out.append((
                u**3 * p1[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t**3 * p2[0],
                u**3 * p1[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t**3 * p2[1],
            ))
    return out
