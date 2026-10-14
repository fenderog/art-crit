"""Tiny drawing toolkit: build a scene once, emit SVG and rasterize to PNG.

Pure standard library.  A scene is a flat, ordered list of drawing ops
(painter's algorithm).  `Canvas.to_svg()` writes the vector file and
`render()` rasterizes the very same ops into RGB bytes that `write_png()`
encodes.  The rasterizer is a supersampled even-odd scanline fill;
strokes are converted to round-capped/joined filled outlines.

Only what the artwork needs is implemented: rect (optional corner radii),
circle, ellipse, polygon/polyline, and paths made of M/L/C/Q/Z segments.
Fills/strokes are flat colours or a user-space linear gradient (gradient
fills are only used on axis aligned rects - the fast per-scanline path).
"""

import math
import struct
import zlib

IDENT = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


# ---------------------------------------------------------------- transforms

def mat_mul(m, n):
    a1, b1, c1, d1, e1, f1 = m
    a2, b2, c2, d2, e2, f2 = n
    return (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2,
            a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)


def mat_apply(m, x, y):
    a, b, c, d, e, f = m
    return (a * x + c * y + e, b * x + d * y + f)


def mat_scale_of(m):
    a, b, c, d, _, _ = m
    return math.sqrt(abs(a * d - b * c)) or 1.0


# -------------------------------------------------------------------- colour

_COLOR_CACHE = {}


def parse_color(c):
    v = _COLOR_CACHE.get(c)
    if v is None:
        s = c.lstrip('#')
        if len(s) == 3:
            s = ''.join(ch * 2 for ch in s)
        v = (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
        _COLOR_CACHE[c] = v
    return v


def mix(c1, c2, t):
    a = parse_color(c1) if isinstance(c1, str) else c1
    b = parse_color(c2) if isinstance(c2, str) else c2
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def hexcol(rgb):
    return '#%02X%02X%02X' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))


class LinGrad:
    """Linear gradient defined in absolute user space."""

    def __init__(self, gid, x1, y1, x2, y2, stops):
        self.gid = gid
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.stops = [(float(p), parse_color(c)) for p, c in stops]
        self.dx = x2 - x1
        self.dy = y2 - y1
        self.len2 = (self.dx * self.dx + self.dy * self.dy) or 1.0

    def color_at(self, x, y):
        t = ((x - self.x1) * self.dx + (y - self.y1) * self.dy) / self.len2
        if t <= self.stops[0][0]:
            return self.stops[0][1]
        if t >= self.stops[-1][0]:
            return self.stops[-1][1]
        for i in range(1, len(self.stops)):
            p0, c0 = self.stops[i - 1]
            p1, c1 = self.stops[i]
            if t <= p1:
                u = (t - p0) / (p1 - p0) if p1 > p0 else 0.0
                return (int(c0[0] + (c1[0] - c0[0]) * u),
                        int(c0[1] + (c1[1] - c0[1]) * u),
                        int(c0[2] + (c1[2] - c0[2]) * u))
        return self.stops[-1][1]


# ----------------------------------------------------------------------- path

class Path:
    """Path builder; segments are kept as tuples so both back-ends can read them."""

    def __init__(self, x=0.0, y=0.0):
        self.segs = []
        self.x, self.y = x, y
        self.sx, self.sy = x, y

    def move(self, x, y):
        self.segs.append(('M', x, y))
        self.x, self.y, self.sx, self.sy = x, y, x, y
        return self

    def line(self, x, y):
        self.segs.append(('L', x, y))
        self.x, self.y = x, y
        return self

    def curve(self, x1, y1, x2, y2, x, y):
        self.segs.append(('C', x1, y1, x2, y2, x, y))
        self.x, self.y = x, y
        return self

    def qcurve(self, x1, y1, x, y):
        self.segs.append(('Q', x1, y1, x, y))
        self.x, self.y = x, y
        return self

    def close(self):
        self.segs.append(('Z',))
        return self

    def d(self):
        out = []
        for s in self.segs:
            k = s[0]
            if k == 'Z':
                out.append('Z')
            else:
                out.append(k + ' ' + ' '.join(_n(v) for v in s[1:]))
        return ''.join(out)


def _n(v):
    s = '%.3f' % v
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s or '0'


def flatten_path(segs, steps=18):
    pts = []
    closed = False
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    for s in segs:
        k = s[0]
        if k == 'M':
            cur = (s[1], s[2])
            start = cur
            pts.append(cur)
        elif k == 'L':
            cur = (s[1], s[2])
            pts.append(cur)
        elif k == 'C':
            x0, y0 = cur
            x1, y1, x2, y2, x3, y3 = s[1:7]
            for i in range(1, steps + 1):
                t = i / steps
                u = 1.0 - t
                bx = (u * u * u * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t * t * t * x3)
                by = (u * u * u * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t * t * t * y3)
                pts.append((bx, by))
            cur = (x3, y3)
        elif k == 'Q':
            x0, y0 = cur
            x1, y1, x2, y2 = s[1:5]
            for i in range(1, steps + 1):
                t = i / steps
                u = 1.0 - t
                bx = u * u * x0 + 2 * u * t * x1 + t * t * x2
                by = u * u * y0 + 2 * u * t * y1 + t * t * y2
                pts.append((bx, by))
            cur = (x2, y2)
        elif k == 'Z':
            closed = True
            pts.append(start)
    return pts, closed


# -------------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.ops = []
        self.stack = [IDENT]
        self.grads = []

    # --- transforms
    def push(self, translate=(0.0, 0.0), rotate=0.0, scale=1.0):
        m = IDENT
        if scale != 1.0:
            m = mat_mul(m, (scale, 0.0, 0.0, scale, 0.0, 0.0))
        if rotate:
            r = math.radians(rotate)
            co, si = math.cos(r), math.sin(r)
            m = mat_mul(m, (co, si, -si, co, 0.0, 0.0))
        if translate != (0.0, 0.0):
            m = mat_mul(m, (1.0, 0.0, 0.0, 1.0, translate[0], translate[1]))
        self.stack.append(mat_mul(self.stack[-1], m))
        self.ops.append(('push', self.stack[-1]))
        return self

    def pop(self):
        self.stack.pop()
        self.ops.append(('pop',))
        return self

    # --- gradients
    def grad(self, gid, x1, y1, x2, y2, stops):
        g = LinGrad(gid, x1, y1, x2, y2, stops)
        self.grads.append(g)
        return g

    # --- primitives
    def rect(self, x, y, w, h, fill=None, rx=0.0, stroke=None, sw=0.0):
        self.ops.append(('rect', x, y, w, h, rx, fill, stroke, sw))
        return self

    def circle(self, cx, cy, r, fill=None, stroke=None, sw=0.0):
        self.ops.append(('circle', cx, cy, r, r, fill, stroke, sw))
        return self

    def ellipse(self, cx, cy, rx, ry, fill=None, stroke=None, sw=0.0):
        self.ops.append(('circle', cx, cy, rx, ry, fill, stroke, sw))
        return self

    def poly(self, pts, fill=None, stroke=None, sw=0.0):
        self.ops.append(('poly', list(pts), True, fill, stroke, sw))
        return self

    def polyline(self, pts, stroke, sw):
        self.ops.append(('poly', list(pts), False, None, stroke, sw))
        return self

    def line(self, x1, y1, x2, y2, stroke, sw):
        self.ops.append(('poly', [(x1, y1), (x2, y2)], False, None, stroke, sw))
        return self

    def path(self, p, fill=None, stroke=None, sw=0.0):
        segs = p.segs if isinstance(p, Path) else p
        self.ops.append(('path', segs, fill, stroke, sw))
        return self

    # --- svg
    def to_svg(self):
        out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
               'viewBox="0 0 %d %d">' % (self.w, self.h, self.w, self.h)]
        if self.grads:
            out.append('<defs>')
            for g in self.grads:
                stops = ''.join(
                    '<stop offset="%s" stop-color="%s"/>' % (_n(p), hexcol(c))
                    for p, c in g.stops)
                out.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" '
                           'x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>'
                           % (g.gid, _n(g.x1), _n(g.y1), _n(g.x2), _n(g.y2), stops))
            out.append('</defs>')
        for op in self.ops:
            k = op[0]
            if k == 'push':
                m = op[1]
                if m == IDENT:
                    out.append('<g>')
                else:
                    out.append('<g transform="matrix(%s)">' % ' '.join(_n(v) for v in m))
            elif k == 'pop':
                out.append('</g>')
            elif k == 'rect':
                _, x, y, w, h, rx, fill, stroke, sw = op
                out.append('<rect x="%s" y="%s" width="%s" height="%s"%s%s/>'
                           % (_n(x), _n(y), _n(w), _n(h),
                              (' rx="%s"' % _n(rx)) if rx else '',
                              _paint(fill, stroke, sw)))
            elif k == 'circle':
                _, cx, cy, rx, ry, fill, stroke, sw = op
                tag = 'circle' if abs(rx - ry) < 1e-9 else 'ellipse'
                if tag == 'circle':
                    out.append('<circle cx="%s" cy="%s" r="%s"%s/>'
                               % (_n(cx), _n(cy), _n(rx), _paint(fill, stroke, sw)))
                else:
                    out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s"%s/>'
                               % (_n(cx), _n(cy), _n(rx), _n(ry), _paint(fill, stroke, sw)))
            elif k == 'poly':
                _, pts, closed, fill, stroke, sw = op
                pts_s = ' '.join('%s,%s' % (_n(x), _n(y)) for x, y in pts)
                tag = 'polygon' if closed else 'polyline'
                out.append('<%s points="%s"%s/>' % (tag, pts_s, _paint(fill, stroke, sw)))
            elif k == 'path':
                _, segs, fill, stroke, sw = op
                out.append('<path d="%s"%s/>' % (Path().segs.__class__(segs).d()
                                                 if False else _segs_d(segs),
                                                 _paint(fill, stroke, sw)))
        out.append('</svg>')
        return '\n'.join(out) + '\n'


def _segs_d(segs):
    p = Path()
    p.segs = list(segs)
    return p.d()


def _paint(fill, stroke, sw):
    s = ' fill="%s"' % (_ref(fill) if fill is not None else 'none')
    if stroke is not None and sw > 0:
        s += ' stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"' % (
            _ref(stroke), _n(sw))
    return s


def _ref(col):
    return 'url(#%s)' % col.gid if isinstance(col, LinGrad) else col


# --------------------------------------------------------------- rasterizer

def circle_poly(cx, cy, rx, ry, n):
    return [(cx + rx * math.cos(2 * math.pi * i / n),
             cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def rect_poly(x, y, w, h, rx, ry=None):
    if ry is None:
        ry = rx
    rx = min(rx, w * 0.5)
    ry = min(ry, h * 0.5)
    if rx <= 0 or ry <= 0:
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    pts = []
    corners = [(x + w - rx, y + ry, -90.0), (x + w - rx, y + h - ry, 0.0),
               (x + rx, y + h - ry, 90.0), (x + rx, y + ry, 180.0)]
    steps = 8
    for cx, cy, a0 in corners:
        for i in range(steps + 1):
            a = math.radians(a0 + 90.0 * i / steps)
            pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return pts


def stroke_polys(pts, hw, seg=16):
    """Round-capped, round-joined stroke as an ordered list of filled polys."""
    polys = []
    n = len(pts)
    if n == 1:
        return [circle_poly(pts[0][0], pts[0][1], hw, hw, seg)]
    last = n - 1
    for i in range(last):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        if L < 1e-9:
            continue
        nx = -dy / L * hw
        ny = dx / L * hw
        polys.append([(x1 + nx, y1 + ny), (x2 + nx, y2 + ny),
                      (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)])
    for i in range(n):
        polys.append(circle_poly(pts[i][0], pts[i][1], hw, hw, seg))
    return polys


class Raster:
    def __init__(self, w, h, ss=2):
        self.ss = ss
        self.W = w * ss
        self.H = h * ss
        self.buf = bytearray(self.W * self.H * 3)

    # -- low level ------------------------------------------------------
    def fill_poly(self, pts, rgb):
        """pts: supersampled pixel coords (floats).  Even-odd scanline fill."""
        W, H, buf = self.W, self.H, self.buf
        ymin = min(p[1] for p in pts)
        ymax = max(p[1] for p in pts)
        y0 = max(0, int(math.floor(ymin)))
        y1 = min(H - 1, int(math.ceil(ymax)))
        if y1 < y0:
            return
        edges = []
        n = len(pts)
        for i in range(n):
            x1, ya = pts[i]
            x2, yb = pts[(i + 1) % n]
            if ya == yb:
                continue
            if ya < yb:
                edges.append((ya, yb, x1, (x2 - x1) / (yb - ya)))
            else:
                edges.append((yb, ya, x2, (x1 - x2) / (ya - yb)))
        if not edges:
            return
        r, g, b = rgb
        run_cache = {}
        for y in range(y0, y1 + 1):
            yc = y + 0.5
            xs = []
            for ya, yb, xa, sl in edges:
                if ya <= yc < yb:
                    xs.append(xa + (yc - ya) * sl)
            if not xs:
                continue
            xs.sort()
            row = y * W * 3
            for i in range(0, len(xs) - 1, 2):
                px0 = int(math.ceil(xs[i] - 0.5))
                px1 = int(math.ceil(xs[i + 1] - 0.5))
                if px0 < 0:
                    px0 = 0
                if px1 > W:
                    px1 = W
                if px1 <= px0:
                    continue
                cnt = px1 - px0
                run = run_cache.get(cnt)
                if run is None:
                    run = bytes((r, g, b)) * cnt
                    if len(run_cache) < 64:
                        run_cache[cnt] = run
                buf[row + px0 * 3:row + px1 * 3] = run

    def fill_rect_grad(self, x0, y0, x1, y1, grad):
        """Axis aligned rect filled with a linear gradient (one colour/row)."""
        W, buf = self.W, self.buf
        ya = max(0, int(math.floor(y0)))
        yb = min(self.H - 1, int(math.ceil(y1)))
        xa = max(0, int(math.floor(x0)))
        xb = min(W, int(math.ceil(x1)))
        if xb <= xa or yb < ya:
            return
        for y in range(ya, yb + 1):
            r, g, b = grad.color_at((xa + xb) * 0.5 / self.ss, (y + 0.5) / self.ss)
            row = y * W * 3
            buf[row + xa * 3:row + xb * 3] = bytes((r, g, b)) * (xb - xa)

    def fill_rect(self, x0, y0, x1, y1, rgb):
        W, buf = self.W, self.buf
        ya = max(0, int(math.floor(y0)))
        yb = min(self.H - 1, int(math.ceil(y1)))
        xa = max(0, int(math.floor(x0)))
        xb = min(W, int(math.ceil(x1)))
        if xb <= xa or yb < ya:
            return
        run = bytes(rgb) * (xb - xa)
        for y in range(ya, yb + 1):
            row = y * W * 3
            buf[row + xa * 3:row + xb * 3] = run

    # -- scene ----------------------------------------------------------
    def draw(self, canvas):
        ss = self.ss
        stack = [IDENT]
        for op in canvas.ops:
            k = op[0]
            if k == 'push':
                stack.append(op[1])
            elif k == 'pop':
                stack.pop()
            else:
                self._op(op, stack[-1])

    def _tx(self, m, pts):
        a, b, c, d, e, f = m
        ss = self.ss
        return [((a * x + c * y + e) * ss, (b * x + d * y + f) * ss) for x, y in pts]

    def _op(self, op, m):
        k = op[0]
        s = mat_scale_of(m)
        if k == 'rect':
            _, x, y, w, h, rx, fill, stroke, sw = op
            pts = self._tx(m, rect_poly(x, y, w, h, rx))
            self._paint_shape(pts, fill, stroke, sw, s, rect=(x, y, w, h, rx, m))
        elif k == 'circle':
            _, cx, cy, rx, ry, fill, stroke, sw = op
            rmax = max(rx, ry) * s
            n = max(12, min(160, int(rmax * math.pi / 1.2)))
            pts = self._tx(m, circle_poly(cx, cy, rx, ry, n))
            self._paint_shape(pts, fill, stroke, sw, s)
        elif k == 'poly':
            _, pts0, closed, fill, stroke, sw = op
            pts = self._tx(m, pts0)
            if not closed and len(pts) > 1:
                pts = pts[:]  # open path: fill is ignored
            self._paint_shape(pts, fill, stroke, sw, s, closed=closed)
        elif k == 'path':
            _, segs, fill, stroke, sw = op
            pts0, closed = flatten_path(segs)
            pts = self._tx(m, pts0)
            self._paint_shape(pts, fill, stroke, sw, s, closed=closed)

    def _paint_shape(self, pts, fill, stroke, sw, s, closed=True, rect=None):
        if fill is not None:
            if isinstance(fill, LinGrad) and rect is not None:
                x, y, w, h, rx, m = rect
                if rx <= 0 and _is_axis_aligned(m):
                    a, b, c, d, e, f = m
                    x0, y0 = mat_apply(m, x, y)
                    x1, y1 = mat_apply(m, x + w, y + h)
                    self.fill_rect_grad(min(x0, x1) * self.ss, min(y0, y1) * self.ss,
                                        max(x0, x1) * self.ss, max(y0, y1) * self.ss,
                                        _grad_in_pixel_space(fill, self.ss))
                    return
            self.fill_poly(pts, parse_color(fill) if isinstance(fill, str) else fill.color_at(0, 0))
        if stroke is not None and sw > 0:
            hw = sw * 0.5 * s * self.ss
            if hw < 0.4:
                hw = 0.4
            seg = max(8, min(20, int(hw * 1.2) + 8))
            sp = stroke_polys(pts, hw, seg)
            col = parse_color(stroke) if isinstance(stroke, str) else stroke.color_at(0, 0)
            for p in sp:
                self.fill_poly(p, col)

    def downsample(self, out_w, out_h):
        ss = self.ss
        W, H, buf = self.W, self.H, self.buf
        out = bytearray(out_w * out_h * 3)
        if ss == 2:
            stride = W * 3
            o = 0
            for y in range(out_h):
                r0 = y * 2 * stride
                r1 = r0 + stride
                for x in range(out_w):
                    p = x * 6
                    q0 = r0 + p
                    q1 = r1 + p
                    out[o] = (buf[q0] + buf[q0 + 3] + buf[q1] + buf[q1 + 3]) >> 2
                    out[o + 1] = (buf[q0 + 1] + buf[q0 + 4] + buf[q1 + 1] + buf[q1 + 4]) >> 2
                    out[o + 2] = (buf[q0 + 2] + buf[q0 + 5] + buf[q1 + 2] + buf[q1 + 5]) >> 2
                    o += 3
            return out
        n = ss * ss
        stride = W * 3
        o = 0
        for y in range(out_h):
            base = y * ss * stride
            for x in range(out_w):
                sx = base + x * ss * 3
                r = g = b = 0
                for dy in range(ss):
                    p = sx + dy * stride
                    for _ in range(ss):
                        r += buf[p]
                        g += buf[p + 1]
                        b += buf[p + 2]
                        p += 3
                out[o] = r // n
                out[o + 1] = g // n
                out[o + 2] = b // n
                o += 3
        return out


def _is_axis_aligned(m):
    a, b, c, d, _, _ = m
    return abs(b) < 1e-9 and abs(c) < 1e-9


def _grad_in_pixel_space(g, ss):
    lg = LinGrad(g.gid, g.x1 * ss, g.y1 * ss, g.x2 * ss, g.y2 * ss,
                 [(p, hexcol(c)) for p, c in g.stops])
    return lg


# ------------------------------------------------------------- post + output

def post_effects(out, w, h, vignette=0.34, warm=0.10):
    """Corner vignette + warm key light from the upper left."""
    cx, cy = (w - 1) * 0.5, (h - 1) * 0.5
    maxr2 = cx * cx + cy * cy
    for y in range(h):
        dy = y - cy
        for x in range(w):
            dx = x - cx
            r2 = (dx * dx + dy * dy) / maxr2
            v = 1.0 - vignette * (r2 ** 1.35)
            t = warm * (1.0 - (x * 0.62 + y * 0.38) / (w * 0.62 + h * 0.38))
            i = (y * w + x) * 3
            out[i] = min(255, int(out[i] * v * (1.0 + t * 1.15)))
            out[i + 1] = min(255, int(out[i + 1] * v * (1.0 + t * 0.55)))
            out[i + 2] = min(255, int(out[i + 2] * v * (1.0 - t * 0.35)))


def write_png(path, w, h, rgb):
    stride = w * 3
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data
                + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', comp) + chunk(b'IEND', b''))
    with open(path, 'wb') as fh:
        fh.write(png)
    return len(png)