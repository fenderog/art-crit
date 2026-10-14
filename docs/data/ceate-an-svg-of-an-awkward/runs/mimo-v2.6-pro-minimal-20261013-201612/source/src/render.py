"""Tiny dual-backend shape renderer.

A scene is described once with Canvas commands; the same command list can be
emitted as scalable SVG or rasterised to a PNG (supersampled scanline fill,
pure stdlib).  Supported primitives: rect (optionally rounded/rotated),
ellipse/circle, polygon, polyline, line, and paths built from M/L/C/Z ops.
Fills: solid, linear gradient, radial gradient (all with alpha).
"""

import math
import struct
import zlib


# ------------------------------------------------------------------ fills

def _norm_stops(stops):
    out = []
    for s in stops:
        t, rgb = s[0], s[1]
        a = s[2] if len(s) > 2 else 1.0
        out.append((float(t), (float(rgb[0]), float(rgb[1]), float(rgb[2])), float(a)))
    return tuple(out)


def solid(rgb, a=1.0):
    return {'k': 'solid', 'stops': _norm_stops([(0.0, rgb, a)]), 'p0': (0.0, 0.0), 'p1': (1.0, 0.0), 'c': (0.0, 0.0), 'r': 1.0}


def linear(stops, p0, p1):
    return {'k': 'lin', 'stops': _norm_stops(stops), 'p0': p0, 'p1': p1, 'c': (0.0, 0.0), 'r': 1.0}


def radial(stops, center, r):
    return {'k': 'rad', 'stops': _norm_stops(stops), 'p0': (0.0, 0.0), 'p1': (1.0, 0.0), 'c': center, 'r': float(r)}


def _stop_color(stops, t):
    n = len(stops)
    if n == 1 or t <= stops[0][0]:
        s = stops[0]
        return s[1], s[2]
    if t >= stops[-1][0]:
        s = stops[-1]
        return s[1], s[2]
    for i in range(1, n):
        b = stops[i]
        if t <= b[0]:
            a = stops[i - 1]
            span = b[0] - a[0]
            f = 0.0 if span <= 0 else (t - a[0]) / span
            c0, c1 = a[1], b[1]
            return ((c0[0] + (c1[0] - c0[0]) * f,
                     c0[1] + (c1[1] - c0[1]) * f,
                     c0[2] + (c1[2] - c0[2]) * f),
                    a[2] + (b[2] - a[2]) * f)
    s = stops[-1]
    return s[1], s[2]


# --------------------------------------------------------------- geometry

def _bez3(p0, p1, p2, p3, n):
    pts = []
    for i in range(1, n + 1):
        t = i / n
        mt = 1.0 - t
        x = mt * mt * mt * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t * t * t * p3[0]
        y = mt * mt * mt * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t * t * t * p3[1]
        pts.append((x, y))
    return pts


def _round_rect_pts(x, y, w, h, rx, seg=8):
    if rx <= 0.5:
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    rx = min(rx, w / 2.0, h / 2.0)
    pts = []
    arcs = [((x + w - rx, y + rx), -90, 0),
            ((x + w - rx, y + h - rx), 0, 90),
            ((x + rx, y + h - rx), 90, 180),
            ((x + rx, y + rx), 180, 270)]
    for (cx, cy), a0, a1 in arcs:
        for i in range(seg + 1):
            a = math.radians(a0 + (a1 - a0) * i / seg)
            pts.append((cx + rx * math.cos(a), cy + rx * math.sin(a)))
    return pts


def _ellipse_pts(cx, cy, rx, ry, seg=72):
    return [(cx + rx * math.cos(2 * math.pi * i / seg), cy + ry * math.sin(2 * math.pi * i / seg))
            for i in range(seg)]


def _path_subpaths(ops):
    subs, cur, start, last = [], [], None, None
    for op in ops:
        k = op[0]
        if k == 'M':
            if len(cur) > 1:
                subs.append(cur)
            cur = [(op[1], op[2])]
            start = cur[0]
            last = cur[0]
        elif k == 'L':
            cur.append((op[1], op[2]))
            last = cur[-1]
        elif k == 'C':
            p0, p1, p2, p3 = last, (op[1], op[2]), (op[3], op[4]), (op[5], op[6])
            d = math.hypot(p3[0] - p0[0], p3[1] - p0[1])
            n = max(6, min(64, int(d / 5) + 2))
            cur.extend(_bez3(p0, p1, p2, p3, n))
            last = p3
        elif k == 'Z':
            if start is not None and cur:
                if abs(cur[-1][0] - start[0]) > 1e-9 or abs(cur[-1][1] - start[1]) > 1e-9:
                    cur.append(start)
            last = start
    if len(cur) > 1:
        subs.append(cur)
    return subs


def _rot_pts(pts, rot):
    if not rot:
        return pts
    ang, cx, cy = math.radians(rot[0]), rot[1], rot[2]
    ca, sa = math.cos(ang), math.sin(ang)
    return [((x - cx) * ca - (y - cy) * sa + cx, (x - cx) * sa + (y - cy) * ca + cy) for x, y in pts]


def _fill_polys(cmd):
    k = cmd['kind']
    if k == 'rect':
        return [_rot_pts(_round_rect_pts(cmd['x'], cmd['y'], cmd['w'], cmd['h'], cmd.get('rx', 0)), cmd.get('rot'))]
    if k == 'ellipse':
        return [_rot_pts(_ellipse_pts(cmd['cx'], cmd['cy'], cmd['rx'], cmd['ry']), cmd.get('rot'))]
    if k == 'polygon':
        return [_rot_pts(list(cmd['pts']), cmd.get('rot'))]
    if k == 'path':
        return [_rot_pts(p, cmd.get('rot')) for p in _path_subpaths(cmd['ops'])]
    return []


def _stroke_polys(cmd):
    k = cmd['kind']
    if k == 'line':
        return [_rot_pts([(cmd['x1'], cmd['y1']), (cmd['x2'], cmd['y2'])], cmd.get('rot'))]
    if k == 'polyline':
        return [_rot_pts(list(cmd['pts']), cmd.get('rot'))]
    if k == 'path':
        return [_rot_pts(p, cmd.get('rot')) for p in _path_subpaths(cmd['ops'])]
    closed = _fill_polys(cmd)
    out = []
    for p in closed:
        q = list(p)
        if q[0] != q[-1]:
            q.append(q[0])
        out.append(q)
    return out


# ---------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.cmds = []

    def _add(self, **kw):
        self.cmds.append(kw)

    def rect(self, x, y, w, h, fill=None, stroke=None, sw=2.0, rx=0.0, rot=None):
        self._add(kind='rect', x=x, y=y, w=w, h=h, rx=rx, rot=rot, fill=fill, stroke=stroke, sw=sw)

    def circle(self, cx, cy, r, fill=None, stroke=None, sw=2.0):
        self._add(kind='ellipse', cx=cx, cy=cy, rx=r, ry=r, rot=None, fill=fill, stroke=stroke, sw=sw)

    def ellipse(self, cx, cy, rx, ry, fill=None, stroke=None, sw=2.0, rot=None):
        self._add(kind='ellipse', cx=cx, cy=cy, rx=rx, ry=ry, rot=rot, fill=fill, stroke=stroke, sw=sw)

    def polygon(self, pts, fill=None, stroke=None, sw=2.0, rot=None):
        self._add(kind='polygon', pts=list(pts), rot=rot, fill=fill, stroke=stroke, sw=sw)

    def polyline(self, pts, stroke, sw=2.0, rot=None):
        self._add(kind='polyline', pts=list(pts), rot=rot, fill=None, stroke=stroke, sw=sw)

    def line(self, x1, y1, x2, y2, stroke, sw=2.0, rot=None):
        self._add(kind='line', x1=x1, y1=y1, x2=x2, y2=y2, rot=rot, fill=None, stroke=stroke, sw=sw)

    def path(self, ops, fill=None, stroke=None, sw=2.0, rot=None):
        self._add(kind='path', ops=list(ops), rot=rot, fill=fill, stroke=stroke, sw=sw)

    # ------------------------------------------------------------- SVG

    def to_svg(self):
        defs, ids = [], {}

        def num(v):
            s = '%.2f' % v
            s = s.rstrip('0').rstrip('.')
            return s if s not in ('', '-0') else '0'

        def hexc(c):
            return '#%02x%02x%02x' % (max(0, min(255, int(round(c[0])))),
                                      max(0, min(255, int(round(c[1])))),
                                      max(0, min(255, int(round(c[2])))))

        def paint(f):
            if f is None:
                return 'none', None
            if f['k'] == 'solid':
                t, c, a = f['stops'][0]
                return hexc(c), a
            key = id(f)
            if key in ids:
                return 'url(#%s)' % ids[key], None
            name = 'g%d' % (len(ids) + 1)
            ids[key] = name
            stops = ''.join('<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (num(t), hexc(c), num(a))
                            for t, c, a in f['stops'])
            if f['k'] == 'lin':
                defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>'
                            % (name, num(f['p0'][0]), num(f['p0'][1]), num(f['p1'][0]), num(f['p1'][1]), stops))
            else:
                defs.append('<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="%s" cy="%s" r="%s">%s</radialGradient>'
                            % (name, num(f['c'][0]), num(f['c'][1]), num(f['r']), stops))
            return 'url(#%s)' % name, None

        body = []
        for cmd in self.cmds:
            fill_ref, fill_a = paint(cmd.get('fill'))
            stroke_ref, stroke_a = paint(cmd.get('stroke'))
            attrs = []
            if fill_ref == 'none':
                attrs.append('fill="none"')
            else:
                attrs.append('fill="%s"' % fill_ref)
                if fill_a is not None and fill_a < 1.0:
                    attrs.append('fill-opacity="%s"' % num(fill_a))
            if stroke_ref == 'none':
                attrs.append('stroke="none"')
            else:
                attrs.append('stroke="%s"' % stroke_ref)
                attrs.append('stroke-width="%s"' % num(cmd.get('sw', 2.0)))
                attrs.append('stroke-linecap="round" stroke-linejoin="round"')
                if stroke_a is not None and stroke_a < 1.0:
                    attrs.append('stroke-opacity="%s"' % num(stroke_a))
            rot = cmd.get('rot')
            if rot:
                attrs.append('transform="rotate(%s %s %s)"' % (num(rot[0]), num(rot[1]), num(rot[2])))
            k = cmd['kind']
            if k == 'rect':
                el = 'rect'
                attrs.insert(0, 'x="%s" y="%s" width="%s" height="%s"' % (num(cmd['x']), num(cmd['y']), num(cmd['w']), num(cmd['h'])))
                if cmd.get('rx'):
                    attrs.insert(1, 'rx="%s"' % num(cmd['rx']))
            elif k == 'ellipse':
                el = 'ellipse'
                attrs.insert(0, 'cx="%s" cy="%s" rx="%s" ry="%s"' % (num(cmd['cx']), num(cmd['cy']), num(cmd['rx']), num(cmd['ry'])))
            elif k == 'polygon':
                el = 'polygon'
                attrs.insert(0, 'points="%s"' % ' '.join('%s,%s' % (num(x), num(y)) for x, y in cmd['pts']))
            elif k == 'polyline':
                el = 'polyline'
                attrs.insert(0, 'points="%s"' % ' '.join('%s,%s' % (num(x), num(y)) for x, y in cmd['pts']))
            elif k == 'line':
                el = 'line'
                attrs.insert(0, 'x1="%s" y1="%s" x2="%s" y2="%s"' % (num(cmd['x1']), num(cmd['y1']), num(cmd['x2']), num(cmd['y2'])))
            else:
                el = 'path'
                d = []
                for op in cmd['ops']:
                    if op[0] == 'Z':
                        d.append('Z')
                    else:
                        d.append(op[0] + ' ' + ' '.join(num(v) for v in op[1:]))
                attrs.insert(0, 'd="%s"' % ' '.join(d))
            body.append('<%s %s/>' % (el, ' '.join(attrs)))

        head = ['<?xml version="1.0" encoding="UTF-8"?>',
                '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (self.w, self.h, self.w, self.h)]
        if defs:
            head.append('<defs>' + ''.join(defs) + '</defs>')
        return '\n'.join(head + body + ['</svg>', ''])

    # ------------------------------------------------------------- PNG

    def to_png(self, path, ss=2, bg=(0, 0, 0)):
        w2, h2 = self.w * ss, self.h * ss
        buf = bytearray(w2 * h2 * 3)
        # background
        br, bg_, bb = bg
        buf[:] = bytes([br, bg_, bb]) * (w2 * h2)

        raster = _Raster(buf, w2, h2)
        for cmd in self.cmds:
            if cmd.get('fill') is not None:
                polys = _fill_polys(cmd)
                if polys:
                    raster.fill(polys, cmd['fill'])
            if cmd.get('stroke') is not None:
                for poly in _stroke_polys(cmd):
                    raster.stroke(poly, cmd['stroke'], cmd.get('sw', 2.0) * ss)

        # downsample
        out = bytearray(self.w * self.h * 3)
        n = ss * ss
        for y in range(self.h):
            oy = y * ss
            for x in range(self.w):
                ox = x * ss
                r = g = b = 0
                for dy in range(ss):
                    base = ((oy + dy) * w2 + ox) * 3
                    for dx in range(ss):
                        i = base + dx * 3
                        r += buf[i]
                        g += buf[i + 1]
                        b += buf[i + 2]
                o = (y * self.w + x) * 3
                out[o] = r // n
                out[o + 1] = g // n
                out[o + 2] = b // n

        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw += out[y * stride:(y + 1) * stride]
        comp = zlib.compress(bytes(raw), 6)
        with open(path, 'wb') as fh:
            fh.write(b'\x89PNG\r\n\x1a\n')
            fh.write(_chunk(b'IHDR', struct.pack('>IIBBBBB', self.w, self.h, 8, 2, 0, 0, 0)))
            fh.write(_chunk(b'IDAT', comp))
            fh.write(_chunk(b'IEND', b''))


def _chunk(tag, data):
    return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)


class _Raster:
    def __init__(self, buf, w, h):
        self.buf = buf
        self.w = w
        self.h = h

    # -- polygon fill with non-zero winding, per-scanline
    def fill(self, polys, fill):
        ymin = self.h
        ymax = 0
        edges = []
        for pts in polys:
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if y0 < ymin:
                    ymin = y0
                if y1 < ymin:
                    ymin = y1
                if y0 > ymax:
                    ymax = y0
                if y1 > ymax:
                    ymax = y1
                if y0 < y1:
                    edges.append((y0, y1, x0, (x1 - x0) / (y1 - y0), 1))
                else:
                    edges.append((y1, y0, x1, (x0 - x1) / (y0 - y1), -1))
        if not edges:
            return
        y_a = max(0, int(math.floor(ymin)))
        y_b = min(self.h - 1, int(math.ceil(ymax)))

        kind = fill['k']
        stops = fill['stops']
        if kind == 'solid':
            col, alpha = stops[0][1], stops[0][2]
        p0 = fill['p0']
        gx = gy = 0.0
        if kind == 'lin':
            dx = fill['p1'][0] - p0[0]
            dy = fill['p1'][1] - p0[1]
            L = dx * dx + dy * dy
            inv = 1.0 / L if L > 0 else 0.0
            gx, gy = dx * inv, dy * inv
        elif kind == 'rad':
            cx, cy, rr = fill['c'][0], fill['c'][1], fill['r']
            invr = 1.0 / rr if rr > 0 else 0.0

        buf = self.buf
        w = self.w
        for y in range(y_a, y_b + 1):
            yc = y + 0.5
            xs = []
            for (ya, yb, xa, dxdy, dirn) in edges:
                if ya <= yc < yb:
                    xs.append((xa + (yc - ya) * dxdy, dirn))
            if not xs:
                continue
            xs.sort()
            wind = 0
            start = 0.0
            spans = []
            for x, d in xs:
                prev = wind
                wind += d
                if prev == 0 and wind != 0:
                    start = x
                elif prev != 0 and wind == 0:
                    spans.append((start, x))
            if not spans:
                continue
            row = y * w
            for (xa, xb) in spans:
                px0 = int(math.ceil(xa - 0.5))
                px1 = int(math.floor(xb - 0.5))
                if px0 < 0:
                    px0 = 0
                if px1 > w - 1:
                    px1 = w - 1
                if px1 < px0:
                    continue
                if kind == 'solid':
                    r, g, b = col
                    a255 = int(alpha * 255 + 0.5)
                    if a255 >= 255:
                        rowbytes = bytes((int(r), int(g), int(b))) * (px1 - px0 + 1)
                        buf[row * 3 + px0 * 3: row * 3 + (px1 + 1) * 3] = rowbytes
                    else:
                        ia = 255 - a255
                        base = row * 3 + px0 * 3
                        for i in range(base, base + (px1 - px0 + 1) * 3, 3):
                            buf[i] = (buf[i] * ia + int(r) * a255) // 255
                            buf[i + 1] = (buf[i + 1] * ia + int(g) * a255) // 255
                            buf[i + 2] = (buf[i + 2] * ia + int(b) * a255) // 255
                    continue
                if kind == 'lin':
                    t = (px0 + 0.5 - p0[0]) * gx + (yc - p0[1]) * gy
                    dt = gx
                else:
                    t = 0.0
                    dt = 0.0
                base = row * 3 + px0 * 3
                for i in range(px0, px1 + 1):
                    if kind == 'lin':
                        tt = t + (i - px0) * dt
                    else:
                        ddx = i + 0.5 - cx
                        ddy = yc - cy
                        tt = math.sqrt(ddx * ddx + ddy * ddy) * invr
                    (cr, cg, cb), a = _stop_color(stops, tt)
                    a255 = int(a * 255 + 0.5)
                    o = base + (i - px0) * 3
                    if a255 >= 255:
                        buf[o] = int(cr)
                        buf[o + 1] = int(cg)
                        buf[o + 2] = int(cb)
                    elif a255 > 0:
                        ia = 255 - a255
                        buf[o] = (buf[o] * ia + int(cr) * a255) // 255
                        buf[o + 1] = (buf[o + 1] * ia + int(cg) * a255) // 255
                        buf[o + 2] = (buf[o + 2] * ia + int(cb) * a255) // 255

    # -- stroke as chain of capsules (round caps/joins)
    def stroke(self, poly, fill, sw):
        if len(poly) < 2 or sw <= 0:
            return
        half = sw / 2.0
        for i in range(len(poly) - 1):
            x0, y0 = poly[i]
            x1, y1 = poly[i + 1]
            dx, dy = x1 - x0, y1 - y0
            L = math.hypot(dx, dy)
            if L < 1e-9:
                continue
            ux, uy = dx / L, dy / L
            px, py = -uy * half, ux * half
            self.fill([[(x0 + px, y0 + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (x0 - px, y0 - py)]], fill)
            self.fill([_ellipse_pts(x0, y0, half, half, 16)], fill)
            self.fill([_ellipse_pts(x1, y1, half, half, 16)], fill)