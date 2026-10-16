"""Organic logo geometry: smooth contours, unions, and stroked letterforms.

Coordinates are in a y-up math space unless a function says otherwise.
SVG export flips Y.
"""

from __future__ import annotations

import math
from collections import defaultdict


def hypot(x, y):
    return math.hypot(x, y)


def signed_area(pts):
    a = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a * 0.5


def centroid(pts):
    a = signed_area(pts)
    if abs(a) < 1e-9:
        sx = sum(p[0] for p in pts) / len(pts)
        sy = sum(p[1] for p in pts) / len(pts)
        return sx, sy
    cx = cy = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        c = x1 * y2 - x2 * y1
        cx += (x1 + x2) * c
        cy += (y1 + y2) * c
    cx /= 6.0 * a
    cy /= 6.0 * a
    return cx, cy


def bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def point_in_poly(x, y, pts):
    inside = False
    n = len(pts)
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / (yj - yi + 1e-15) + xi
        ):
            inside = not inside
        j = i
    return inside


def resample_closed(pts, n):
    if len(pts) < 3:
        return list(pts)
    segs = []
    total = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        L = hypot(x2 - x1, y2 - y1)
        segs.append((x1, y1, x2, y2, L))
        total += L
    if total < 1e-9:
        return list(pts)
    step = total / n
    out = []
    target = 0.0
    seg_i = 0
    acc = 0.0
    for k in range(n):
        while seg_i < len(segs) - 1 and acc + segs[seg_i][4] < target - 1e-9:
            acc += segs[seg_i][4]
            seg_i += 1
        x1, y1, x2, y2, L = segs[seg_i]
        t = 0.0 if L < 1e-9 else (target - acc) / L
        t = max(0.0, min(1.0, t))
        out.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t))
        target += step
    return out


def laplacian_closed(pts, iters=4, amount=0.35):
    pts = list(pts)
    n = len(pts)
    for _ in range(iters):
        nxt = []
        for i in range(n):
            px, py = pts[i]
            ax, ay = pts[(i - 1) % n]
            bx, by = pts[(i + 1) % n]
            mx, my = (ax + bx) * 0.5, (ay + by) * 0.5
            nxt.append((px * (1 - amount) + mx * amount, py * (1 - amount) + my * amount))
        pts = nxt
    return pts


def rdp_closed(pts, eps):
    """Ramer–Douglas–Peucker on a closed ring. Keeps the shape closed."""
    if len(pts) < 5:
        return list(pts)
    # Split at the farthest point from the first so the ring has two chains.
    x0, y0 = pts[0]
    far = max(range(1, len(pts)), key=lambda i: hypot(pts[i][0] - x0, pts[i][1] - y0))
    a = _rdp_open(pts[: far + 1], eps)
    b = _rdp_open(pts[far:] + pts[:1], eps)
    # b includes the closing duplicate of pts[0]
    return a[:-1] + b[:-1]


def _rdp_open(pts, eps):
    if len(pts) < 3:
        return list(pts)
    x1, y1 = pts[0]
    x2, y2 = pts[-1]
    dx, dy = x2 - x1, y2 - y1
    den = hypot(dx, dy)
    worst = 0.0
    idx = 0
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        if den < 1e-12:
            d = hypot(x - x1, y - y1)
        else:
            d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / den
        if d > worst:
            worst = d
            idx = i
    if worst > eps:
        left = _rdp_open(pts[: idx + 1], eps)
        right = _rdp_open(pts[idx:], eps)
        return left[:-1] + right
    return [pts[0], pts[-1]]


def catmull_rom_path(pts, decimals=2):
    """Closed Catmull–Rom spline as an SVG path string. Y is left as given."""
    n = len(pts)
    if n < 3:
        return ""

    def fmt(v):
        return f"{v:.{decimals}f}"

    cmds = [f"M{fmt(pts[0][0])} {fmt(pts[0][1])}"]
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        c1x = p1[0] + (p2[0] - p0[0]) / 6.0
        c1y = p1[1] + (p2[1] - p0[1]) / 6.0
        c2x = p2[0] - (p3[0] - p1[0]) / 6.0
        c2y = p2[1] - (p3[1] - p1[1]) / 6.0
        cmds.append(
            f"C{fmt(c1x)} {fmt(c1y)} {fmt(c2x)} {fmt(c2y)} {fmt(p2[0])} {fmt(p2[1])}"
        )
    cmds.append("Z")
    return "".join(cmds)


def translate(pts, dx, dy):
    return [(x + dx, y + dy) for x, y in pts]


def scale_about(pts, cx, cy, s):
    return [(cx + (x - cx) * s, cy + (y - cy) * s) for x, y in pts]


def rotate_about(pts, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * c - dy * s, cy + dx * s + dy * c))
    return out


def fourier_radius(theta, harmonics, cleft=None):
    """harmonics: list of (freq, amp, phase). r = 1 + sum amp*cos(freq*th+phase)."""
    r = 1.0
    for freq, amp, phase in harmonics:
        r += amp * math.cos(freq * theta + phase)
    if cleft:
        center, depth, width = cleft
        d = (theta - center + math.pi) % (2 * math.pi) - math.pi
        r -= depth * math.exp(-0.5 * (d / width) ** 2)
    return max(0.08, r)


def fourier_ring(harmonics, cleft=None, n=96, scale_x=1.0, scale_y=1.0, rotation=0.0):
    pts = []
    for i in range(n):
        th = (i / n) * math.tau
        r = fourier_radius(th, harmonics, cleft)
        x = r * math.cos(th) * scale_x
        y = r * math.sin(th) * scale_y
        pts.append((x, y))
    if rotation:
        pts = rotate_about(pts, 0.0, 0.0, rotation)
    return pts


def wyvill(r2):
    if r2 >= 1.0:
        return 0.0
    t = 1.0 - r2
    return t * t * t


def ellipse_field(x, y, blobs):
    total = 0.0
    for cx, cy, rx, ry, rot, weight in blobs:
        dx, dy = x - cx, y - cy
        c, s = math.cos(rot), math.sin(rot)
        lx = (dx * c + dy * s) / rx
        ly = (-dx * s + dy * c) / ry
        total += weight * wyvill(lx * lx + ly * ly)
    return total


def circle_softmax(x, y, circles, sharpness=10.0):
    """circles: (cx, cy, r). Positive inside the soft union. Threshold at 0."""
    vals = [r - hypot(x - cx, y - cy) for cx, cy, r in circles]
    m = max(vals)
    s = 0.0
    for v in vals:
        s += math.exp(sharpness * (v - m))
    return m + math.log(s) / sharpness


def marching_squares(field_fn, x0, y0, x1, y1, nx, ny, thresh):
    """Return closed loops as lists of (x, y) in math space (y up)."""
    xs = [x0 + (x1 - x0) * i / (nx - 1) for i in range(nx)]
    ys = [y0 + (y1 - y0) * j / (ny - 1) for j in range(ny)]
    val = [[field_fn(xs[i], ys[j]) for i in range(nx)] for j in range(ny)]

    def interp(pa, va, pb, vb):
        if abs(vb - va) < 1e-12:
            t = 0.5
        else:
            t = (thresh - va) / (vb - va)
        t = max(0.0, min(1.0, t))
        return (pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t)

    segments = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            corners = [
                ((xs[i], ys[j]), val[j][i]),
                ((xs[i + 1], ys[j]), val[j][i + 1]),
                ((xs[i + 1], ys[j + 1]), val[j + 1][i + 1]),
                ((xs[i], ys[j + 1]), val[j + 1][i]),
            ]
            mask = 0
            for bit, (_, v) in enumerate(corners):
                if v >= thresh:
                    mask |= 1 << bit
            if mask == 0 or mask == 15:
                continue
            edges = {}
            pairs = (
                (0, 1, 0),
                (1, 2, 1),
                (2, 3, 2),
                (3, 0, 3),
            )
            crossed = []
            for a, b, eid in pairs:
                va = corners[a][1]
                vb = corners[b][1]
                if (va >= thresh) != (vb >= thresh):
                    edges[eid] = interp(corners[a][0], va, corners[b][0], vb)
                    crossed.append(eid)
            if len(crossed) == 2:
                segments.append((edges[crossed[0]], edges[crossed[1]]))
            elif len(crossed) == 4:
                cx = (xs[i] + xs[i + 1]) * 0.5
                cy = (ys[j] + ys[j + 1]) * 0.5
                center_in = field_fn(cx, cy) >= thresh
                # Disjoint pockets when the center is outside; a channel when inside.
                if center_in:
                    segments.append((edges[0], edges[1]))
                    segments.append((edges[2], edges[3]))
                else:
                    segments.append((edges[0], edges[3]))
                    segments.append((edges[1], edges[2]))
    return _link_segments(segments)


def _link_segments(segments):
    def key(p):
        return (round(p[0], 4), round(p[1], 4))

    nbrs = defaultdict(list)
    pts = {}
    for a, b in segments:
        ka, kb = key(a), key(b)
        if ka == kb:
            continue
        pts[ka] = a
        pts[kb] = b
        nbrs[ka].append(kb)
        nbrs[kb].append(ka)

    used = set()
    loops = []
    for start in nbrs:
        for nb in nbrs[start]:
            if (start, nb) in used:
                continue
            loop_k = [start]
            cur = nb
            prev = start
            used.add((prev, cur))
            used.add((cur, prev))
            guard = 0
            while cur != start and guard < 100000:
                guard += 1
                loop_k.append(cur)
                nxts = [c for c in nbrs[cur] if (cur, c) not in used]
                if not nxts:
                    break
                # Prefer the neighbor that isn't a tiny reverse step.
                nxt = nxts[0]
                if len(nxts) > 1:
                    # Choose the one closest to a straight continuation.
                    px, py = pts[prev]
                    cx, cy = pts[cur]
                    vx, vy = cx - px, cy - py
                    best = None
                    best_dot = -1e18
                    for cand in nxts:
                        qx, qy = pts[cand]
                        wx, wy = qx - cx, qy - cy
                        dot = vx * wx + vy * wy
                        if dot > best_dot:
                            best_dot = dot
                            best = cand
                    nxt = best
                used.add((cur, nxt))
                used.add((nxt, cur))
                prev, cur = cur, nxt
            if cur == start and len(loop_k) >= 6:
                loops.append([pts[k] for k in loop_k])
    return loops


def classify_loops(loops, min_area=1e-4):
    """Return (outer, holes) for the largest outer loop and loops inside it."""
    loops = [lp for lp in loops if abs(signed_area(lp)) > min_area]
    if not loops:
        return None, []
    loops.sort(key=lambda lp: abs(signed_area(lp)), reverse=True)
    outer = loops[0]
    holes = []
    for lp in loops[1:]:
        cx, cy = centroid(lp)
        if point_in_poly(cx, cy, outer):
            holes.append(lp)
    return outer, holes


def orient(pts, ccw=True):
    area = signed_area(pts)
    # Math y-up: positive area is CCW.
    is_ccw = area > 0
    if is_ccw != ccw:
        return list(reversed(pts))
    return list(pts)


def fit_in_box(pts_groups, size, pad):
    """Uniform-scale a list of rings into a square [pad, size-pad], y still up."""
    allpts = [p for g in pts_groups for p in g]
    minx, miny, maxx, maxy = bbox(allpts)
    bw = max(maxx - minx, 1e-9)
    bh = max(maxy - miny, 1e-9)
    s = (size - 2 * pad) / max(bw, bh)
    cx = (minx + maxx) * 0.5
    cy = (miny + maxy) * 0.5
    ox = size * 0.5
    oy = size * 0.5

    def map_pt(x, y):
        return ((x - cx) * s + ox, (y - cy) * s + oy)

    return [[map_pt(x, y) for x, y in g] for g in pts_groups]


def to_svg_y(pts, height):
    return [(x, height - y) for x, y in pts]


# --- letter strokes -------------------------------------------------------

def _norm(x, y):
    L = hypot(x, y)
    if L < 1e-12:
        return 0.0, 0.0
    return x / L, y / L


def _intersect(p, r, q, s):
    """Intersect point+dir rays. Returns None if parallel."""
    rx, ry = r
    sx, sy = s
    den = rx * sy - ry * sx
    if abs(den) < 1e-12:
        return None
    qpx, qpy = q[0] - p[0], q[1] - p[1]
    t = (qpx * sy - qpy * sx) / den
    return (p[0] + t * rx, p[1] + t * ry)


def stroke_polyline(pts, width, miter_limit=2.4, closed=False):
    """Return an outline polygon for a constant-width stroke. Y-up or Y-down, consistent."""
    hw = width * 0.5
    n = len(pts)
    if n < 2:
        return []
    dirs = []
    normals = []
    for i in range(n - 1):
        dx = pts[i + 1][0] - pts[i][0]
        dy = pts[i + 1][1] - pts[i][1]
        ux, uy = _norm(dx, dy)
        dirs.append((ux, uy))
        normals.append((-uy, ux))  # left

    def offset_point(i, side):
        """side +1 left, -1 right, at vertex i, mitered."""
        if i == 0:
            nx, ny = normals[0]
            return (pts[0][0] + side * nx * hw, pts[0][1] + side * ny * hw)
        if i == n - 1:
            nx, ny = normals[-1]
            return (pts[-1][0] + side * nx * hw, pts[-1][1] + side * ny * hw)
        n0 = normals[i - 1]
        n1 = normals[i]
        p0 = (pts[i][0] + side * n0[0] * hw, pts[i][1] + side * n0[1] * hw)
        d0 = dirs[i - 1]
        p1 = (pts[i][0] + side * n1[0] * hw, pts[i][1] + side * n1[1] * hw)
        d1 = dirs[i]
        hit = _intersect(p0, d0, p1, d1)
        if hit is None:
            return p0
        # Miter length measured from the vertex.
        mx, my = hit[0] - pts[i][0], hit[1] - pts[i][1]
        mlen = hypot(mx, my)
        # Turn direction: if this side is the inner corner, intersection is close.
        cross = dirs[i - 1][0] * dirs[i][1] - dirs[i - 1][1] * dirs[i][0]
        inner = (side > 0 and cross < 0) or (side < 0 and cross > 0)
        if inner:
            # Bevel the inner corner if the intersection ran backwards.
            return hit if mlen < hw * 4 else p0
        if mlen > hw * miter_limit:
            # Bevel: two points. Caller handles single return; we clamp along bisector.
            bx, by = _norm(n0[0] + n1[0], n0[1] + n1[1])
            if bx == 0 and by == 0:
                bx, by = n0
            return (pts[i][0] + side * bx * hw * miter_limit, pts[i][1] + side * by * hw * miter_limit)
        return hit

    left = [offset_point(i, 1) for i in range(n)]
    right = [offset_point(i, -1) for i in range(n)]
    if closed:
        # Not needed for these letters.
        return left + list(reversed(right))
    return left + list(reversed(right))


def clip_polygon_horizontal(pts, y_limit, keep_above):
    """Sutherland–Hodgman against a horizontal line. keep_above=True keeps y >= limit if y-up.

    Here `keep` is a predicate on the point.
    """
    if keep_above:
        inside = lambda y: y >= y_limit - 1e-9
    else:
        inside = lambda y: y <= y_limit + 1e-9

    def intersect(a, b):
        x1, y1 = a
        x2, y2 = b
        if abs(y2 - y1) < 1e-12:
            return (x2, y_limit)
        t = (y_limit - y1) / (y2 - y1)
        return (x1 + t * (x2 - x1), y_limit)

    out = []
    if not pts:
        return out
    prev = pts[-1]
    prev_in = inside(prev[1])
    for cur in pts:
        cur_in = inside(cur[1])
        if cur_in:
            if not prev_in:
                out.append(intersect(prev, cur))
            out.append(cur)
        elif prev_in:
            out.append(intersect(prev, cur))
        prev, prev_in = cur, cur_in
    return out


def polygon_path(pts, decimals=2):
    if not pts:
        return ""

    def fmt(v):
        return f"{v:.{decimals}f}"

    cmds = [f"M{fmt(pts[0][0])} {fmt(pts[0][1])}"]
    for x, y in pts[1:]:
        cmds.append(f"L{fmt(x)} {fmt(y)}")
    cmds.append("Z")
    return "".join(cmds)


def ellipse_beziers(cx, cy, rx, ry):
    """4-cubic ellipse as an SVG subpath, current user y orientation."""
    k = 0.5522847498
    pts = [
        (cx + rx, cy),
        (cx + rx, cy + k * ry),
        (cx + k * rx, cy + ry),
        (cx, cy + ry),
        (cx - k * rx, cy + ry),
        (cx - rx, cy + k * ry),
        (cx - rx, cy),
        (cx - rx, cy - k * ry),
        (cx - k * rx, cy - ry),
        (cx, cy - ry),
        (cx + k * rx, cy - ry),
        (cx + rx, cy - k * ry),
        (cx + rx, cy),
    ]
    # pts layout: move, then groups of (c1, c2, end) but I stored anchors interleaved.
    # Rebuild cleanly.
    kx, ky = k * rx, k * ry
    d = [
        f"M{cx + rx:.2f} {cy:.2f}",
        f"C{cx + rx:.2f} {cy + ky:.2f} {cx + kx:.2f} {cy + ry:.2f} {cx:.2f} {cy + ry:.2f}",
        f"C{cx - kx:.2f} {cy + ry:.2f} {cx - rx:.2f} {cy + ky:.2f} {cx - rx:.2f} {cy:.2f}",
        f"C{cx - rx:.2f} {cy - ky:.2f} {cx - kx:.2f} {cy - ry:.2f} {cx:.2f} {cy - ry:.2f}",
        f"C{cx + kx:.2f} {cy - ry:.2f} {cx + rx:.2f} {cy - ky:.2f} {cx + rx:.2f} {cy:.2f}",
        "Z",
    ]
    return "".join(d)
