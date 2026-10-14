#!/usr/bin/env python3
"""Pure-python PNG reader that prints an ASCII-art view of an image.

Usage: pngview.py FILE [COLS] [ROWS] [--hue]
"""
import sys
import zlib
import struct


def read_png(path):
    data = open(path, 'rb').read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', 'not a PNG'
    pos = 8
    idat = b''
    meta = {}
    while pos < len(data):
        ln = struct.unpack('>I', data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
        if typ == b'IHDR':
            w, h, bd, ct, cm, fm, il = struct.unpack('>IIBBBBB', chunk)
            meta = dict(w=w, h=h, bd=bd, ct=ct)
        elif typ == b'IDAT':
            idat += chunk
        elif typ == b'IEND':
            break
    w, h, bd, ct = meta['w'], meta['h'], meta['bd'], meta['ct']
    assert bd == 8 and ct in (0, 2, 4, 6), f'unsupported png bd={bd} ct={ct}'
    nch = {0: 1, 2: 3, 4: 2, 6: 4}[ct]
    raw = zlib.decompress(idat)
    stride = w * nch
    out = bytearray(h * stride)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        if f == 1:
            for i in range(nch, stride):
                line[i] = (line[i] + line[i - nch]) & 255
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i - nch] if i >= nch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - nch] if i >= nch else 0
                b = prev[i]
                c = prev[i - nch] if i >= nch else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                if pa <= pb and pa <= pc:
                    pr = a
                elif pb <= pc:
                    pr = b
                else:
                    pr = c
                line[i] = (line[i] + pr) & 255
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return w, h, nch, out


def sample(x, y):
    """mean color of cell at pixel coords (x0,y0)-(x1,y1)"""
    pass


def view(path, cols=100, rows=None, hue=False, box=None):
    w, h, nch, buf = read_png(path)
    if rows is None:
        rows = max(1, int(cols * h / w / 2))
    x0, y0, x1, y1 = box if box else (0, 0, w, h)
    bw = (x1 - x0) / cols
    bh = (y1 - y0) / rows
    ramp = ' .:-=+*#%@'
    lines = []
    for ry in range(rows):
        sy0 = y0 + ry * bh
        sy1 = min(y0 + (ry + 1) * bh, y1)
        row = []
        for rx in range(cols):
            sx0 = x0 + rx * bw
            sx1 = min(x0 + (rx + 1) * bw, x1)
            rs = gs = bs = n = 0
            # sample a few pixels inside the cell (subsample if big)
            stepx = max(1, int(bw / 4))
            stepy = max(1, int(bh / 4))
            for yy in range(int(sy0), int(sy1), stepy):
                for xx in range(int(sx0), int(sx1), stepx):
                    i = (yy * w + xx) * nch
                    if nch == 1:
                        r = g = b = buf[i]
                    else:
                        r, g, b = buf[i], buf[i + 1], buf[i + 2]
                    rs += r; gs += g; bs += b; n += 1
            if n == 0:
                row.append(' ')
                continue
            r, g, b = rs / n, gs / n, bs / n
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            if hue:
                mx, mn = max(r, g, b), min(r, g, b)
                sat = 0 if mx == 0 else (mx - mn) / mx
                if sat < 0.25:
                    row.append(ramp[min(9, int(lum / 256 * 10))])
                else:
                    if r >= g >= b or r >= b >= g:
                        c = 'R' if r > 140 else 'r'
                    elif g >= r >= b or g >= b >= r:
                        c = 'G' if g > 140 else 'g'
                    else:
                        c = 'B' if b > 140 else 'b'
                    row.append(c if lum > 60 else c.lower())
            else:
                row.append(ramp[min(9, int(lum / 256 * 10))])
        lines.append(''.join(row))
    return lines


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = [a for a in sys.argv[1:] if a.startswith('--')]
    path = args[0]
    cols = int(args[1]) if len(args) > 1 else 100
    rows = int(args[2]) if len(args) > 2 and args[2] else None
    hue = '--hue' in flags
    box = None
    if '--box' in flags:
        i = sys.argv.index('--box') + 1
        box = tuple(int(v) for v in sys.argv[i:i + 4])
    print(f'== {path} ==')
    for ln in view(path, cols, rows, hue, box):
        print(ln)