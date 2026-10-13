#!/usr/bin/env python3
"""Awkward robot family portrait.

Writes output/robot_family_portrait.svg (hand-built vector art, no text).

Cast, left to right:
  Grandpa  - wind-up tin robot, asleep in the avocado wing chair, oil drool.
  Dad      - boxy mainframe in a clip-on tie, wire comb-over, manic LED grin,
             one stiff hand on the chair and one on Mom's shoulder.
  Dog      - the only one who nailed the pose (flash eye-shine, wagging tail).
  Mom      - chrome beehive, polite smile, leaning slightly away from Dad,
             holding the baby.
  Baby     - egg pod in a knit hat whose pom-pom is a siren. Screaming.
  Kid      - hovering on a rotor, winking, thumbs-up, and stretching a
             telescoping arm to give the teen bunny ears.
  Teen     - standing apart in a black hoodie, headphones on, arms crossed,
             side-eye; the matching sweater is knotted around the waist.
"""
import math
import os
import random
import xml.dom.minidom

W, H = 1600, 1200
INK = '#241d29'
OL = f'stroke="{INK}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"'

MAROON, MAROON_D, CREAM, MUSTARD = '#8f2f3b', '#5e1c27', '#f0e2c4', '#d9a441'

defs = []
_n = [0]


def uid(p):
    _n[0] += 1
    return f'{p}{_n[0]}'


def f(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.')


def rot(p, ang, c):
    a = math.radians(ang)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a),
            c[1] + x * math.sin(a) + y * math.cos(a))


# ---------------------------------------------------------------- primitives

def _ol(ol, extra):
    """Outline attributes, minus any that `extra` overrides."""
    if not ol:
        return ''
    keep = [a for a in OL.split(' ') if a.split('=')[0] + '=' not in extra]
    return ' '.join(keep)


def path(d, fill, ol=True, extra=''):
    return f'<path d="{d}" fill="{fill}" {_ol(ol, extra)} {extra}/>'


def circ(cx, cy, r, fill, ol=True, extra=''):
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}" {_ol(ol, extra)} {extra}/>'


def ell(cx, cy, rx, ry, fill, ol=True, extra=''):
    return (f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{fill}" '
            f'{_ol(ol, extra)} {extra}/>')


def rect(x, y, w, h, fill, rx=0, ol=True, extra=''):
    return (f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}" '
            f'fill="{fill}" {_ol(ol, extra)} {extra}/>')


def stroke(d, color, w, extra=''):
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{f(w)}" '
            f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def tube(d, w, color, hl=None, cap='round'):
    """A limb: outlined thick stroke with an optional highlight streak."""
    s = (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{f(w + 8)}" '
         f'stroke-linecap="{cap}" stroke-linejoin="round"/>'
         f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{f(w)}" '
         f'stroke-linecap="{cap}" stroke-linejoin="round"/>')
    if hl:
        s += (f'<path d="{d}" fill="none" stroke="{hl}" stroke-width="{f(w * 0.28)}" '
              f'stroke-linecap="round" stroke-linejoin="round" opacity="0.55" '
              f'transform="translate({f(-w * 0.22)},{f(-w * 0.08)})"/>')
    return s


def pts(*p):
    return 'M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in p)


def g(content, transform=''):
    t = f' transform="{transform}"' if transform else ''
    return f'<g{t}>{"".join(content) if isinstance(content, list) else content}</g>'


# ---------------------------------------------------------------- materials

def lin(gid, stops, x1=0, y1=0, x2=1, y2=0.3):
    s = ''
    for st in stops:
        o, c = st[0], st[1]
        op = f' stop-opacity="{st[2]}"' if len(st) > 2 else ''
        s += f'<stop offset="{o}" stop-color="{c}"{op}/>'
    defs.append(f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>')


def mat(gid, light, mid, dark):
    lin(gid, [(0, light), (0.42, mid), (1, dark)])


mat('steel', '#dfe7ee', '#a3b3c3', '#66717f')
mat('mint', '#f6fcf8', '#c7e3d8', '#86ad9f')
mat('lilac', '#f7efff', '#bba5dc', '#6f5b98')
mat('tin', '#e6e0cf', '#b0a994', '#736b58')
mat('yellow', '#ffe995', '#f4c23a', '#c0850f')
mat('black', '#66627a', '#3b3849', '#1f1d27')
mat('copper', '#f5bb86', '#cf8146', '#87471d')
mat('maroon', '#ad4552', MAROON, '#5c1d27')
mat('avocado', '#a2ab64', '#76803f', '#4a5225')
mat('rose', '#e3adb6', '#bd7f8b', '#80505b')
mat('teal', '#77abb0', '#4f8188', '#30565c')
mat('plaster', '#fbf7ec', '#e0d8c5', '#ada38d')
mat('khaki', '#c8b68f', '#a08c64', '#6e5e40')
mat('denim', '#4b4d5e', '#2e3040', '#1b1c26')
mat('wood', '#a8723f', '#7d4f27', '#4f3017')
mat('white', '#ffffff', '#ecebe6', '#b9b8b2')
mat('brass', '#f3d77e', '#c9a03e', '#86651c')
lin('shade', [(0, '#ffffff', 0.10), (0.42, '#000000', 0), (1, '#000000', 0.34)])
lin('floorfade', [(0, '#0e1222', 0), (0.3, '#0e1222', 0.22), (1, '#0e1222', 0.5)], 0, 0, 0, 1)

defs.append('''
<radialGradient id="backdrop" cx="0.44" cy="0.38" r="0.78">
  <stop offset="0" stop-color="#b3c4d4"/><stop offset="0.38" stop-color="#7d93ad"/>
  <stop offset="0.75" stop-color="#46587a"/><stop offset="1" stop-color="#252d47"/>
</radialGradient>
<radialGradient id="vignette" cx="0.5" cy="0.46" r="0.74">
  <stop offset="0.55" stop-color="#0b0d18" stop-opacity="0"/>
  <stop offset="1" stop-color="#0b0d18" stop-opacity="0.6"/>
</radialGradient>
<radialGradient id="eyeshine">
  <stop offset="0" stop-color="#ffffff"/><stop offset="0.35" stop-color="#d8fff0"/>
  <stop offset="0.7" stop-color="#5fe8b8"/><stop offset="1" stop-color="#127a62"/>
</radialGradient>
<radialGradient id="glowG"><stop offset="0" stop-color="#8fffd8" stop-opacity="0.55"/>
  <stop offset="1" stop-color="#8fffd8" stop-opacity="0"/></radialGradient>
<radialGradient id="sirenG" cx="0.4" cy="0.35"><stop offset="0" stop-color="#fff2ec"/>
  <stop offset="0.35" stop-color="#ff5a4a"/><stop offset="1" stop-color="#a3101c"/></radialGradient>
<radialGradient id="sirenGlow"><stop offset="0" stop-color="#ff3b3b" stop-opacity="0.5"/>
  <stop offset="1" stop-color="#ff3b3b" stop-opacity="0"/></radialGradient>
<radialGradient id="magentaGlow"><stop offset="0" stop-color="#ff4fc0" stop-opacity="0.6"/>
  <stop offset="1" stop-color="#ff4fc0" stop-opacity="0"/></radialGradient>
<radialGradient id="rotorG"><stop offset="0" stop-color="#ffffff" stop-opacity="0.05"/>
  <stop offset="0.7" stop-color="#ffffff" stop-opacity="0.38"/>
  <stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
<radialGradient id="tubeGlow"><stop offset="0" stop-color="#ffb347" stop-opacity="0.9"/>
  <stop offset="1" stop-color="#ffb347" stop-opacity="0"/></radialGradient>
<radialGradient id="pearl" cx="0.35" cy="0.3"><stop offset="0" stop-color="#ffffff"/>
  <stop offset="1" stop-color="#cfc6bf"/></radialGradient>
<pattern id="knit" width="9" height="8" patternUnits="userSpaceOnUse">
  <path d="M0.5 0 L4.5 6 L8.5 0" fill="none" stroke="#000" stroke-opacity="0.17" stroke-width="1.6"/>
  <path d="M0.5 2 L4.5 8 L8.5 2" fill="none" stroke="#fff" stroke-opacity="0.08" stroke-width="1"/>
</pattern>
<filter id="mottleL" x="0" y="0" width="1" height="1">
  <feTurbulence type="fractalNoise" baseFrequency="0.0032 0.0045" numOctaves="4" seed="11"/>
  <feColorMatrix values="0 0 0 0 0.88  0 0 0 0 0.92  0 0 0 0 1  2.4 0 0 0 -1.22"/>
</filter>
<filter id="mottleD" x="0" y="0" width="1" height="1">
  <feTurbulence type="fractalNoise" baseFrequency="0.005 0.004" numOctaves="4" seed="4"/>
  <feColorMatrix values="0 0 0 0 0.12  0 0 0 0 0.12  0 0 0 0 0.24  0 2.6 0 0 -1.36"/>
</filter>
<filter id="grain" x="0" y="0" width="1" height="1">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="5"/>
  <feColorMatrix type="saturate" values="0"/>
  <feComponentTransfer><feFuncA type="linear" slope="0" intercept="1"/></feComponentTransfer>
</filter>
<filter id="flashShadow" x="-10%" y="-10%" width="130%" height="130%">
  <feGaussianBlur in="SourceAlpha" stdDeviation="5"/>
  <feOffset dx="30" dy="14"/>
  <feComponentTransfer><feFuncA type="linear" slope="0.4"/></feComponentTransfer>
</filter>
<filter id="blur4" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="blur8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="blur2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2"/></filter>
''')


# ---------------------------------------------------------------- sweaters

def knit_band(x0, x1, y, h=36):
    s = [rect(x0, y, x1 - x0, h, CREAM, ol=False),
         rect(x0, y + 3, x1 - x0, 4, MAROON_D, ol=False),
         rect(x0, y + h - 7, x1 - x0, 4, MAROON_D, ol=False)]
    zig, dots = [], []
    x, k = x0 - (x0 % 24), 0
    while x <= x1 + 24:
        low = k % 2 == 0
        zig.append((x, y + h - 12 if low else y + 12))
        if low:
            dots.append(circ(x, y + 14, 2.8, MUSTARD, ol=False))
        else:
            dots.append(circ(x, y + h - 14, 2.8, MUSTARD, ol=False))
        x += 12
        k += 1
    s.append(f'<path d="{pts(*zig)}" fill="none" stroke="{MAROON_D}" stroke-width="4.5" '
             f'stroke-linejoin="miter"/>')
    s += dots
    return ''.join(s)


def sweater(d, bx0, bx1, band_y, band_h=36, fill='url(#maroon)', extra=''):
    cid = uid('clip')
    defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
    return (f'<path d="{d}" fill="{fill}"/>'
            f'<g clip-path="url(#{cid})">'
            + (knit_band(bx0, bx1, band_y, band_h) if band_y else '') +
            f'<rect x="{bx0}" y="{band_y - 500 if band_y else 0}" width="{bx1 - bx0}" '
            f'height="{1000 if band_y else H}" fill="url(#knit)"/>'
            + extra +
            f'<path d="{d}" fill="url(#shade)"/></g>'
            f'<path d="{d}" fill="none" {OL}/>')


def sleeve(d, w, cuff_d=None):
    s = tube(d, w, MAROON, hl='#c4606c')
    if cuff_d:
        s += tube(cuff_d, w + 2, MAROON_D, cap='butt')
    return s


# ---------------------------------------------------------------- backdrop

def backdrop():
    s = [rect(0, 0, W, H, 'url(#backdrop)', ol=False),
         rect(0, 0, W, H, '#000', ol=False, extra='filter="url(#mottleL)" opacity="0.55"'),
         rect(0, 0, W, H, '#000', ol=False, extra='filter="url(#mottleD)" opacity="0.7"'),
         rect(0, 860, W, 340, 'url(#floorfade)', ol=False),
         ell(760, 1060, 620, 70, '#d8e2ee', ol=False, extra='opacity="0.10" filter="url(#blur8)"')]
    return ''.join(s)


def tape_mark(cx, cy):
    tape = 'stroke="#efe6c4" stroke-width="9" stroke-linecap="butt" opacity="0.85"'
    return (f'<path d="M{cx - 30} {cy - 9} L{cx + 30} {cy + 9} M{cx - 30} {cy + 9} L{cx + 30} {cy - 9}" '
            f'fill="none" {tape}/>')


def contact_shadows():
    sh = [(135, 1046, 92, 10, 0.45), (396, 1044, 170, 14, 0.5), (650, 1070, 132, 14, 0.55),
          (890, 1016, 120, 14, 0.5), (942, 1030, 40, 7, 0.4), (1330, 1052, 88, 11, 0.5),
          (1112, 1046, 46, 7, 0.22), (590, 1052, 60, 8, 0.4)]
    return ''.join(ell(x, y, rx, ry, '#0b0d18', ol=False,
                       extra=f'opacity="{o}" filter="url(#blur4)"') for x, y, rx, ry, o in sh)


# ---------------------------------------------------------------- props

def frond(rng, x0, y0, ang, length, droop, color):
    a = math.radians(ang)
    p0 = (x0, y0)
    p1 = (x0 + math.cos(a) * length * 0.62, y0 + math.sin(a) * length * 0.62)
    p2 = (p1[0] + math.cos(a) * length * 0.38, p1[1] + math.sin(a) * length * 0.38 + droop)
    out = [stroke(f'M{f(p0[0])} {f(p0[1])} Q{f(p1[0])} {f(p1[1])} {f(p2[0])} {f(p2[1])}',
                  '#2f5a23', 4)]
    n = 14
    for i in range(2, n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * t * (1 - t) * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * t * (1 - t) * p1[1] + t * t * p2[1]
        dx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
        dy = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
        base = math.degrees(math.atan2(dy, dx))
        ln = 26 * (1 - t * 0.75) + rng.uniform(-2, 2)
        for side in (-1, 1):
            la = math.radians(base + side * 58)
            cx, cy = x + math.cos(la) * ln / 2, y + math.sin(la) * ln / 2
            out.append(ell(cx, cy, ln / 2, ln * 0.2, color, ol=False,
                           extra=f'transform="rotate({f(base + side * 58)} {f(cx)} {f(cy)})" '
                                 f'stroke="#2f5a23" stroke-width="1.2"'))
    return ''.join(out)


def column_and_fern():
    s = []
    # fern behind the urn first (back fronds)
    rng = random.Random(3)
    back = [(-150, 150, 40), (-120, 130, 20), (-60, 130, 20), (-30, 150, 45), (-95, 120, 10)]
    for ang, ln, dr in back:
        s.append(frond(rng, 135, 488, ang, ln, dr, '#4b8434'))
    # column
    s.append(path('M90 600 L180 600 L176 990 L94 990 Z', 'url(#plaster)'))
    for i in range(7):
        x = 101 + i * 11.5
        s.append(stroke(f'M{f(x)} 614 L{f(x + (135 - x) * 0.04)} 978', '#8a8069', 4,
                        'stroke-opacity="0.35"'))
        s.append(stroke(f'M{f(x - 3)} 616 L{f(x - 3 + (135 - x) * 0.04)} 976', '#ffffff', 1.5,
                        'stroke-opacity="0.5"'))
    s.append(rect(76, 574, 118, 30, 'url(#plaster)', rx=8))
    s.append(rect(64, 560, 142, 18, 'url(#plaster)', rx=3))
    for cx, sgn in ((80, 1), (190, -1)):
        s.append(circ(cx, 592, 15, 'url(#plaster)'))
        s.append(stroke(f'M{cx} 592 m-6 0 a6 6 0 1 1 6 6 a3 3 0 1 1 -3 -3', '#8a8069', 2.5))
    s.append(rect(82, 984, 106, 18, 'url(#plaster)', rx=9))
    s.append(rect(68, 1000, 134, 44, 'url(#plaster)', rx=3))
    # urn
    s.append(path('M92 494 L178 494 Q176 536 146 547 L124 547 Q94 536 92 494 Z', 'url(#plaster)'))
    s.append(path('M122 546 L148 546 L158 561 L112 561 Z', 'url(#plaster)'))
    s.append(rect(84, 482, 102, 14, 'url(#plaster)', rx=6))
    s.append(stroke('M104 515 Q135 524 166 515', '#8a8069', 2.5, 'stroke-opacity="0.5"'))
    # front fronds, drooping over the urn
    front = [(-175, 170, 120), (-150, 120, 70), (-105, 140, 30), (-75, 150, 30),
             (-20, 150, 90), (5, 160, 140), (-128, 110, 60), (-45, 115, 50), (-90, 90, 10)]
    for ang, ln, dr in front:
        s.append(frond(rng, 135 + rng.uniform(-8, 8), 486, ang, ln, dr,
                       rng.choice(['#5fa23f', '#6cb349', '#4f9136'])))
    return ''.join(s)


# ---------------------------------------------------------------- grandpa

def chair_back():
    s = [path('M300 600 Q258 598 254 650 L256 800 L304 800 Z', 'url(#avocado)'),
         path('M490 600 Q532 598 536 650 L534 800 L486 800 Z', 'url(#avocado)'),
         path('M290 840 L286 600 Q288 548 395 540 Q502 548 504 600 L500 840 Z', 'url(#avocado)')]
    for x, y in ((318, 600), (472, 600), (330, 660), (460, 660), (318, 720), (472, 720)):
        s.append(circ(x, y, 4.5, '#4a5225', ol=False))
        s.append(stroke(f'M{x} {y} l-14 -10 M{x} {y} l14 -10', '#4a5225', 1.5, 'opacity="0.5"'))
    return ''.join(s)


def chair_front():
    s = []
    for x0 in (252, 468):
        s.append(path(f'M{x0} 772 Q{x0} 748 {x0 + 35} 748 Q{x0 + 70} 748 {x0 + 70} 772 '
                      f'L{x0 + 70} 906 L{x0} 906 Z', 'url(#avocado)'))
        s.append(ell(x0 + 35, 776, 29, 24, '#8a9450'))
        s.append(stroke(f'M{x0 + 35} 776 m-12 0 a12 12 0 1 1 12 12 a7 7 0 1 1 -7 -7',
                        '#4a5225', 2.5))
    s.append(path('M318 800 L472 800 Q482 800 482 812 L482 852 L308 852 L308 812 Q308 800 318 800 Z',
                  '#8a9450'))
    s.append(path('M254 852 L536 852 L536 1004 L254 1004 Z', 'url(#avocado)'))
    for x in range(262, 532, 9):
        s.append(stroke(f'M{x} 996 L{x + 1} 1014', '#5b6430', 3))
    s.append(stroke('M256 994 L534 994', '#5b6430', 6))
    for x in (276, 514):
        s.append(path(f'M{x - 8} 1012 L{x + 8} 1012 L{x + 4} 1042 L{x - 4} 1042 Z', 'url(#wood)'))
    return ''.join(s)


def grandpa_torso():
    s = []
    # wind-up key poking out of his back
    s.append(tube('M344 700 L304 704', 9, '#c9a03e'))
    s.append(path('M300 704 Q288 680 276 690 Q268 704 276 718 Q288 728 300 704 Z', 'url(#brass)'))
    s.append(circ(284, 704, 5, '#86651c', ol=False))
    torso = 'M342 652 Q328 742 346 832 L446 832 Q464 742 450 652 Q396 632 342 652 Z'
    s.append(sweater(torso, 320, 470, 716))
    # rust spot peeking under the collar
    s.append(rect(378, 628, 36, 30, 'url(#tin)', rx=6))
    for y in (634, 642, 650):
        s.append(stroke(f'M380 {y} L412 {y}', '#5b5444', 2.5))
    return ''.join(s)


def grandpa_head():
    s = []
    # vacuum-tube hair
    for i, x in enumerate((372, 395, 418)):
        s.append(rect(x - 10, 496, 20, 14, '#4a4538', rx=3))
        glass = (f'M{x - 8} 499 L{x - 8} {474 + abs(i - 1) * 6} Q{x - 8} {464 + abs(i - 1) * 6} '
                 f'{x} {464 + abs(i - 1) * 6} Q{x + 8} {464 + abs(i - 1) * 6} {x + 8} '
                 f'{474 + abs(i - 1) * 6} L{x + 8} 499 Z')
        if i == 1:
            s.append(circ(x, 484, 16, 'url(#tubeGlow)', ol=False))
        s.append(path(glass, '#cfe6f2', extra='fill-opacity="0.5"'))
        s.append(stroke(f'M{x - 3} 496 L{x - 3} 482 L{x + 3} 482 L{x + 3} 496',
                        '#ffb347' if i == 1 else '#6a6a6a', 2))
        s.append(stroke(f'M{x - 4} {478 + abs(i - 1) * 6} L{x - 4} 494', '#ffffff', 2,
                        'opacity="0.7"'))
    # wilted antenna from the ear
    s.append(stroke('M462 572 Q486 548 500 566 Q510 582 504 604', INK, 7))
    s.append(stroke('M462 572 Q486 548 500 566 Q510 582 504 604', '#8f8a7a', 3))
    s.append(circ(504, 610, 7, '#d8c58a'))
    # ears
    for x in (332, 458):
        s.append(circ(x, 578, 16, 'url(#tin)'))
        s.append(circ(x, 578, 6, '#736b58', ol=False))
    head = 'M340 548 Q340 508 395 508 Q450 508 450 548 L450 612 Q450 628 434 628 L356 628 Q340 628 340 612 Z'
    s.append(path(head, 'url(#tin)'))
    s.append(rect(341, 538, 108, 12, '#b0392e', ol=False))
    s.append(stroke('M341 538 L449 538 M341 550 L449 550', INK, 2.5))
    for x in (350, 372, 395, 418, 440):
        s.append(circ(x, 544, 2.5, '#f0c96a', ol=False))
    # rust
    s.append(path('M426 516 q10 -3 14 6 q-2 9 -11 7 q-8 -4 -3 -13 Z', '#8a4b2a', ol=False,
                  extra='opacity="0.5"'))
    s.append(path('M348 598 q8 -2 9 7 q-3 8 -9 5 Z', '#8a4b2a', ol=False, extra='opacity="0.45"'))
    s.append(path('M346 520 Q360 512 378 512', 'none', ol=False,
                  extra='stroke="#fff" stroke-width="4" stroke-linecap="round" opacity="0.6"'))
    # heavy droopy brows, closed eyes
    s.append(path('M352 558 L388 562 L386 571 L350 566 Z', '#6d685c'))
    s.append(path('M402 562 L438 558 L440 566 L404 571 Z', '#6d685c'))
    s.append(stroke('M356 580 Q370 590 384 580', INK, 4))
    s.append(stroke('M406 580 Q420 590 434 580', INK, 4))
    s.append(stroke('M362 586 l-3 5 M370 588 l0 5 M378 586 l3 5', INK, 2))
    s.append(stroke('M412 586 l-3 5 M420 588 l0 5 M428 586 l3 5', INK, 2))
    s.append(circ(395, 597, 6, '#cfc8b4'))
    # slack mouth + oil drool
    s.append(ell(396, 614, 13, 7, '#3a2a2a'))
    s.append(stroke('M405 618 Q408 630 405 640', '#3b2a1c', 3.5))
    s.append(path('M405 638 q-5 7 0 11 q5 -4 0 -11 Z', '#3b2a1c', ol=False))
    # neck
    s.append(rect(380, 626, 32, 18, '#8d8672', rx=4))
    return ''.join(s)


def grandpa_front():
    s = []
    # arms: sleeves to the elbows, hose forearms meeting on the cane
    s.append(sleeve('M348 670 Q330 712 334 748', 32, 'M334 742 L334 754'))
    s.append(sleeve('M444 670 Q462 712 458 748', 32, 'M458 742 L458 754'))
    # legs
    for x in (348, 410):
        s.append(rect(x, 852, 34, 166, 'url(#tin)', rx=8))
        for y in range(872, 1010, 14):
            s.append(stroke(f'M{x + 3} {y} L{x + 31} {y}', '#736b58', 2, 'opacity="0.6"'))
        s.append(circ(x + 17, 856, 20, 'url(#tin)'))
        s.append(circ(x + 17, 856, 6, '#736b58', ol=False))
    for x0 in (328, 400):
        s.append(path(f'M{x0 + 2} 1018 Q{x0 + 2} 1000 {x0 + 24} 1000 L{x0 + 46} 1000 '
                      f'Q{x0 + 62} 1000 {x0 + 64} 1018 L{x0 + 64} 1044 L{x0} 1044 Z', '#6b4a3a'))
        s.append(path(f'M{x0 + 4} 1030 L{x0 + 60} 1030', 'none', ol=False,
                      extra='stroke="#c9a77a" stroke-width="4"'))
    # cane
    s.append(tube('M396 1040 L396 802 Q396 776 420 776 Q444 776 444 800', 11, '#7d4f27',
                  hl='#b78452'))
    s.append(rect(390, 1030, 12, 14, '#2a2228', rx=3))
    # corrugated hose forearms
    for d in ('M334 752 Q348 790 384 790', 'M458 752 Q448 784 412 784'):
        s.append(tube(d, 16, '#a39c88'))
        s.append(f'<path d="{d}" fill="none" stroke="#6d6655" stroke-width="16" '
                 f'stroke-dasharray="2.5 5"/>')
    # pincer hands stacked on the crook
    for cx, cy, a in ((392, 786, 15), (414, 780, -20)):
        s.append(g([path('M-14 -2 Q-14 -16 0 -16 Q14 -16 14 -2 L10 10 L2 2 L-2 2 L-10 10 Z',
                         'url(#tin)')], f'translate({cx} {cy}) rotate({a})'))
    return ''.join(s)


def grandpa_steam():
    return (stroke('M398 456 C384 440 412 428 400 410 C390 394 414 386 406 368', '#ffffff', 7,
                   'opacity="0.35" filter="url(#blur2)"')
            + stroke('M410 420 C424 410 418 398 430 390', '#ffffff', 5,
                     'opacity="0.25" filter="url(#blur2)"'))


# ---------------------------------------------------------------- dad

def dad_body():
    s = []
    # khaki slacks
    s.append(path('M558 640 L634 640 L628 1032 L566 1032 Z', 'url(#khaki)'))
    s.append(path('M646 640 L722 640 L716 1032 L654 1032 Z', 'url(#khaki)'))
    s.append(stroke('M596 660 L597 1020 M684 660 L685 1020', '#6e5e40', 2.5, 'opacity="0.6"'))
    for x0 in (548, 650):
        s.append(path(f'M{x0 + 6} 1028 L{x0 + 80} 1028 Q{x0 + 90} 1050 {x0 + 72} 1052 '
                      f'L{x0 + 6} 1052 Q{x0 - 6} 1048 {x0 + 6} 1028 Z', '#1d1b22'))
    s.append(rect(536, 626, 208, 24, '#4a2f22', rx=4))
    s.append(rect(626, 624, 30, 28, 'url(#brass)', rx=4))
    # torso in the sweater, V-neck with shirt and clip-on tie
    torso = 'M522 374 Q524 350 554 348 L726 348 Q756 350 758 374 L748 640 L532 640 Z'
    s.append(sweater(torso, 510, 770, 516, 40))
    s.append(path('M606 350 L640 428 L674 350 Z', '#f3efe6'))
    s.append(path('M632 364 L648 364 L654 414 L640 428 L626 414 Z', '#2c3a66'))
    for y in (376, 392, 408):
        s.append(stroke(f'M630 {y} L652 {y - 8}', MUSTARD, 3, 'opacity="0.9"'))
    s.append(path('M630 350 L650 350 L646 366 L634 366 Z', '#2c3a66'))
    s.append(path('M612 344 L636 352 L620 374 Z', '#ffffff'))
    s.append(path('M668 344 L644 352 L660 374 Z', '#ffffff'))
    s.append(stroke('M602 350 L640 434 L678 350', MAROON_D, 9))
    s.append(stroke('M602 350 L640 434 L678 350', INK, 2, 'opacity="0.6"'))
    # left arm: hand planted on Grandpa's chair
    s.append(sleeve('M538 380 Q506 418 496 468', 40, 'M496 458 L494 476'))
    s.append(tube('M494 474 L480 540', 22, '#a3b3c3', hl='#e6eef4'))
    s.append(circ(494, 474, 13, 'url(#steel)'))
    s.append(path('M462 546 Q462 530 480 530 Q498 530 498 546 L498 560 L462 560 Z', 'url(#steel)'))
    for x in (466, 478, 490):
        s.append(rect(x - 4, 554, 9, 22, 'url(#steel)', rx=4))
    # right upper arm (forearm is drawn after Mom)
    s.append(sleeve('M744 380 Q776 412 792 462', 40, 'M788 452 L794 470'))
    return ''.join(s)


def dad_head():
    s = []
    s.append(rect(614, 320, 52, 34, '#7d8a98', rx=4))
    for y in (326, 334, 342):
        s.append(stroke(f'M616 {y} L664 {y}', '#4e5966', 3))
    for x in (530, 732):
        s.append(rect(x, 226, 18, 60, 'url(#steel)', rx=6))
        s.append(circ(x + 9, 256, 5, '#c8413a', ol=False))
    s.append(rect(548, 178, 184, 146, 'url(#steel)', rx=26))
    s.append(ell(594, 198, 26, 9, '#ffffff', ol=False,
                 extra='opacity="0.75" transform="rotate(-14 594 198)"'))
    for x in (562, 718):
        for y in (196, 306):
            s.append(circ(x, y, 3.5, '#6b7685', ol=False))
    # comb-over: three wires swept across the dome
    for i, dd in enumerate(('M558 222 C548 166 640 156 718 186',
                            'M558 232 C552 172 652 164 724 198',
                            'M560 242 C556 180 662 174 728 212')):
        s.append(stroke(dd, '#2b2630', 5))
        s.append(stroke(dd, '#6a6070', 1.5, 'opacity="0.8"'))
    # eager brows
    s.append(rect(578, 198, 46, 9, '#3d4652', rx=4, extra='transform="rotate(-7 601 202)"'))
    s.append(rect(656, 198, 46, 9, '#3d4652', rx=4, extra='transform="rotate(7 679 202)"'))
    # lens eyes, fully open
    for x in (603, 677):
        s.append(circ(x, 240, 25, '#e9eff3'))
        s.append(circ(x, 240, 18, '#1b232c', ol=False))
        s.append(circ(x, 241, 11, '#4b86a8', ol=False))
        s.append(circ(x, 241, 5.5, '#0b0f14', ol=False))
        s.append(circ(x - 6, 234, 4, '#ffffff', ol=False))
    # vent mustache
    s.append(rect(598, 266, 84, 18, '#3a3440', rx=8))
    for x in range(604, 680, 6):
        s.append(stroke(f'M{x} 269 L{x} 281', '#8a8494', 2))
    # LED grin, much too wide
    s.append(rect(580, 288, 120, 28, '#152027', rx=10))
    cells = []
    for i in range(16):
        x = 585 + i * 7
        u = (x + 3 - 640) / 56
        top = 292 - 4 * u * u
        cells.append(rect(x, top, 5.5, 5.5, '#a8ffd9', ol=False))
        bot = 292 + 13 * (1 - u * u)
        if bot - top > 8:
            cells.append(rect(x, bot - 1, 5.5, 5.5, '#a8ffd9', ol=False))
        if bot - top > 15:
            cells.append(rect(x, (top + bot) / 2 - 1, 5.5, 5.5, '#ffffff', ol=False,
                              extra='opacity="0.85"'))
    s.append(f'<g filter="url(#blur2)" opacity="0.8">{"".join(cells)}</g>')
    s += cells
    return ''.join(s)


def dad_forearm(target):
    ex, ey = 792, 466
    tx, ty = target
    s = [tube(f'M{ex} {ey} L{f(tx - 4)} {f(ty - 10)}', 22, '#a3b3c3', hl='#e6eef4'),
         circ(ex, ey, 13, 'url(#steel)')]
    ang = math.degrees(math.atan2(ty - ey, tx - ex))
    hand = [path('M-16 -14 Q4 -18 12 -12 L12 14 Q4 18 -16 14 Z', 'url(#steel)')]
    for yy in (-10, 0, 10):
        hand.append(rect(8, yy - 4.5, 26, 9, 'url(#steel)', rx=4.5))
    s.append(g(hand, f'translate({f(tx)} {f(ty)}) rotate(84)'))
    return ''.join(s)


# ---------------------------------------------------------------- mom & baby

MOM_PIVOT = (890, 716)
MOM_LEAN = 5


def bench_and_legs():
    s = []
    s.append(path('M786 840 L786 990 Q890 1008 994 990 L994 840 Z', 'url(#rose)'))
    for x in range(800, 990, 16):
        s.append(stroke(f'M{x} 852 L{x} 992', '#80505b', 2, 'opacity="0.45"'))
    sc = 'M788 984 ' + ' '.join('q8.6 15 17.25 0' for _ in range(12))
    s.append(stroke(sc, '#80505b', 4))
    s.append(ell(890, 840, 104, 20, '#d9a2ac'))
    for x in (806, 974):
        s.append(circ(x, 1012, 10, 'url(#brass)'))
    # pleated skirt over the knees
    skirt = 'M846 716 L934 716 Q976 790 980 860 Q890 884 800 860 Q804 790 846 716 Z'
    s.append(path(skirt, 'url(#teal)'))
    for x0, x1 in ((866, 836), (890, 890), (914, 944), (878, 862), (902, 918)):
        s.append(stroke(f'M{x0} 726 L{x1} 868', '#30565c', 2.5, 'opacity="0.6"'))
    # legs angled demurely to the side, crossed at the ankle
    s.append(tube('M904 866 L936 1008', 15, '#c7e3d8', hl='#ffffff'))
    s.append(tube('M872 866 L952 1004', 15, '#c7e3d8', hl='#ffffff'))
    s.append(path('M922 1004 Q930 998 946 1006 L962 1018 Q956 1028 940 1026 L922 1024 Z',
                  'url(#lilac)'))
    s.append(path('M940 998 Q950 992 966 1002 L980 1014 Q974 1024 958 1022 L942 1018 Z',
                  'url(#lilac)'))
    s.append(stroke('M926 1024 L924 1036 M944 1018 L942 1030', INK, 4))
    return ''.join(s)


def baby_arms(cx, cy):
    """Flailing arms, drawn over Mom's sleeves."""
    return (tube(f'M{cx - 30} {cy - 6} Q{cx - 46} {cy - 18} {cx - 46} {cy - 42}', 9, '#ecebe6')
            + tube(f'M{cx + 30} {cy - 6} Q{cx + 46} {cy - 20} {cx + 48} {cy - 44}', 9, '#ecebe6')
            + circ(cx - 46, cy - 46, 8, 'url(#white)') + circ(cx + 48, cy - 48, 8, 'url(#white)')
            + stroke(f'M{cx - 62} {cy - 58} q-6 8 0 16 M{cx + 64} {cy - 60} q6 8 0 16', '#ffffff',
                     2.5, 'opacity="0.8"'))


def baby(cx, cy):
    s = []
    s.append(circ(cx, cy - 72, 40, 'url(#sirenGlow)', ol=False))
    for i in range(10):
        a = math.radians(i * 36 + 8)
        r0, r1 = 19, 28 + (i % 2) * 6
        s.append(stroke(f'M{f(cx + math.cos(a) * r0)} {f(cy - 72 + math.sin(a) * r0)} '
                        f'L{f(cx + math.cos(a) * r1)} {f(cy - 72 + math.sin(a) * r1)}',
                        '#ff5b4d', 3, 'opacity="0.8"'))
    # egg pod
    s.append(ell(cx, cy, 38, 36, 'url(#white)'))
    s.append(rect(cx - 26, cy - 18, 52, 36, '#1d2b3c', rx=12))
    blue = '#8fe3ff'
    s.append(stroke(f'M{cx - 18} {cy - 10} L{cx - 9} {cy - 5} L{cx - 18} {cy}', blue, 3))
    s.append(stroke(f'M{cx + 18} {cy - 10} L{cx + 9} {cy - 5} L{cx + 18} {cy}', blue, 3))
    s.append(path(f'M{cx - 10} {cy + 4} Q{cx} {cy + 2} {cx + 10} {cy + 4} L{cx + 7} {cy + 15} '
                  f'Q{cx} {cy + 18} {cx - 7} {cy + 15} Z', '#ff6b7a', ol=False,
                  extra=f'stroke="{blue}" stroke-width="2.5"'))
    for dx, dy, sx in ((-40, -10, -1), (40, -12, 1), (-48, 4, -1)):
        s.append(path(f'M{cx + dx} {cy + dy} q{sx * 4} 6 0 9 q{-sx * 4} -3 0 -9 Z', blue,
                      ol=False))
    # knit hat with a siren for a pom-pom
    hat = f'M{cx - 36} {cy - 20} Q{cx - 36} {cy - 62} {cx} {cy - 62} Q{cx + 36} {cy - 62} {cx + 36} {cy - 20} Z'
    s.append(sweater(hat, cx - 40, cx + 40, cy - 34, 16))
    s.append(rect(cx - 39, cy - 26, 78, 12, MAROON_D, rx=6))
    s.append(stroke(f'M{cx - 34} {cy - 20} L{cx + 34} {cy - 20}', '#3e1219', 2, 'opacity="0.4"'))
    s.append(circ(cx, cy - 70, 13, 'url(#sirenG)'))
    s.append(ell(cx - 4, cy - 75, 4, 3, '#ffffff', ol=False))
    return ''.join(s)


def mom_upper():
    s = []
    cx = 890
    # torso in a cardigan
    torso = 'M842 588 Q836 652 852 720 L928 720 Q944 652 938 588 Q890 570 842 588 Z'
    s.append(sweater(torso, 830, 950, 640, 34))
    # neck, pearls
    s.append(rect(879, 540, 22, 46, 'url(#mint)', rx=6))
    for i in range(9):
        t = i / 8
        x = 864 + 52 * t
        y = 578 + 22 * math.sin(math.pi * t)
        s.append(circ(x, y, 4.6, 'url(#pearl)', ol=False, extra=f'stroke="{INK}" stroke-width="1.2"'))
    s.append(sleeve('M848 600 Q834 640 838 688', 30))
    s.append(sleeve('M932 600 Q952 632 952 670', 30))
    # baby, cradled
    s.append(baby(888, 700))
    # forearms in front of the baby
    s.append(tube('M838 688 Q846 744 910 744', 15, '#c7e3d8', hl='#ffffff'))
    s.append(ell(918, 742, 13, 9, 'url(#mint)'))
    s.append(tube('M952 670 Q954 696 938 702', 15, '#c7e3d8', hl='#ffffff'))
    s.append(ell(932, 703, 11, 8, 'url(#mint)'))
    # sleeve ends redrawn over the forearm joints
    s.append(tube('M837 678 L838 688', 30, MAROON))
    s.append(tube('M952 660 L952 670', 30, MAROON))
    s.append(baby_arms(888, 700))
    return ''.join(s)


def mom_head():
    s = []
    cx, cy = 890, 490
    for x in (838, 942):
        s.append(circ(x, 500, 6, 'url(#pearl)'))
        s.append(stroke(f'M{x} 506 L{x} 516', INK, 1.5))
        s.append(circ(x, 521, 5.5, 'url(#pearl)'))
    s.append(ell(cx, cy, 54, 58, 'url(#mint)'))
    s.append(ell(cx - 22, cy + 18, 10, 7, '#ff8fb0', ol=False, extra='opacity="0.0"'))
    # chrome beehive
    hive = 'M838 472 C824 410 848 342 890 340 C932 342 956 410 942 472 Q890 452 838 472 Z'
    s.append(path(hive, 'url(#lilac)'))
    for d in ('M845 452 Q890 436 935 452', 'M842 428 Q890 410 938 428', 'M846 404 Q890 388 934 404',
              'M856 380 Q890 366 924 380', 'M868 358 Q890 350 912 358'):
        s.append(stroke(d, '#6f5b98', 2.5, 'opacity="0.7"'))
    s.append(stroke('M858 450 C850 410 860 372 878 356', '#ffffff', 6, 'opacity="0.55"'))
    # brows, lashes, eyes
    s.append(stroke('M856 478 Q868 472 880 477', INK, 2.5))
    s.append(stroke('M900 477 Q912 472 924 478', INK, 2.5))
    for ex in (868, 912):
        s.append(ell(ex, 494, 13, 10, '#ffffff'))
        s.append(circ(ex - 5, 497, 7, '#3f7fb5', ol=False))
        s.append(circ(ex - 6, 497, 3.2, '#0d1520', ol=False))
        s.append(circ(ex - 8, 494, 1.8, '#ffffff', ol=False))
        # polite, slightly lowered lids
        s.append(path(f'M{ex - 14} 492 Q{ex} 480 {ex + 14} 492 Q{ex} 487 {ex - 14} 492 Z',
                      '#a9cbbd', extra='stroke-width="3"'))
        side = -1 if ex < cx else 1
        s.append(stroke(f'M{ex + side * 12} 489 l{side * 7} -5 M{ex + side * 7} 485 l{side * 5} -6',
                        INK, 2.2))
    for x in (858, 922):
        s.append(circ(x, 514, 9, '#ff8fb0', ol=False, extra='opacity="0.55"'))
    s.append(path('M876 523 Q890 531 904 523 Q890 527 876 523 Z', '#c8327a',
                  extra='stroke="#8e1f55" stroke-width="2.5"'))
    return ''.join(s)


# ---------------------------------------------------------------- kid

KID = (1112, 392)


def kid_body(palm, fingers_ang):
    s = []
    cx = 1112
    # dangling legs, mismatched sneakers
    s.append(tube('M1096 498 L1090 556', 12, '#c9cfd6'))
    s.append(tube('M1128 498 Q1140 528 1156 544', 12, '#c9cfd6'))
    s.append(f'<path d="M1092 536 L1090 556" stroke="#e84a5f" stroke-width="12" '
             f'stroke-dasharray="4 4"/>')
    s.append(path('M1072 556 Q1072 546 1084 546 L1098 546 Q1110 548 1112 566 L1074 568 Q1068 564 1072 556 Z',
                  '#e2453b'))
    s.append(g(path('M-14 -8 Q-14 -16 -2 -16 L10 -16 Q22 -12 22 4 L-14 6 Q-20 2 -14 -8 Z',
                    '#3c6fd0'), 'translate(1160 552) rotate(-30)'))
    # oversized sweater
    torso = 'M1070 400 Q1048 452 1058 508 Q1112 524 1166 508 Q1176 452 1154 400 Q1112 386 1070 400 Z'
    s.append(sweater(torso, 1040, 1180, 438, 34))
    s.append(stroke('M1062 500 Q1112 514 1162 500', MAROON_D, 7))
    # thumbs-up arm
    s.append(sleeve('M1070 420 Q1040 444 1030 418', 22))
    s.append(rect(1016, 378, 28, 26, 'url(#yellow)', rx=9))
    s.append(rect(1020, 352, 12, 30, 'url(#yellow)', rx=6))
    s.append(stroke('M1030 388 L1040 388 M1030 396 L1040 396', INK, 2))
    # telescoping arm toward the teen
    sx, sy = 1160, 414
    s.append(sleeve(f'M1152 416 L{sx} {sy}', 24))
    tx, ty = palm
    L = math.hypot(tx - sx, ty - sy)
    ang = math.degrees(math.atan2(ty - sy, tx - sx))
    segs = []
    n = 5
    for i in range(n):
        w = 17 - i * 2
        x0 = i * L / n - 4
        segs.append(rect(x0, -w / 2, L / n + 8, w, 'url(#yellow)', rx=3))
        segs.append(rect(x0 - 2, -w / 2 - 3, 8, w + 6, '#8e959e', rx=2))
    s.append(g(segs, f'translate({sx} {sy}) rotate({f(ang)})'))
    # V fingers (mostly hidden behind the teen's hood)
    hand = [rect(-17, -16, 34, 30, 'url(#yellow)', rx=10)]
    for a in (-17, 15):
        hand.append(g(rect(-7, -92, 14, 86, 'url(#yellow)', rx=7), f'rotate({a})'))
        hand.append(g(rect(-3, -88, 4, 30, '#ffffff', rx=2, ol=False, extra='opacity="0.5"'),
                      f'rotate({a})'))
    s.append(g(hand, f'translate({f(tx)} {f(ty)}) rotate({f(fingers_ang)})'))
    return ''.join(s)


def kid_head():
    s = []
    cx, cy = 1112, 340
    # rotor
    s.append(rect(cx - 5, 268, 10, 26, '#8e959e', rx=3))
    s.append(ell(cx, 266, 82, 13, 'url(#rotorG)', ol=False))
    s.append(ell(cx - 30, 266, 46, 5, '#e84a5f', ol=False, extra='opacity="0.35"'))
    s.append(ell(cx + 34, 265, 42, 4, '#e84a5f', ol=False, extra='opacity="0.25"'))
    s.append(stroke(f'M{cx - 90} 252 q-10 12 0 24 M{cx + 92} 250 q10 12 0 24', '#ffffff', 2.5,
                    'opacity="0.7"'))
    s.append(ell(cx, 265, 10, 6, '#e84a5f'))
    for x in (cx - 60, cx + 60):
        s.append(circ(x, cy + 4, 11, '#e88b2e'))
    s.append(ell(cx, cy, 60, 52, 'url(#yellow)'))
    s.append(ell(cx - 26, cy - 34, 16, 7, '#ffffff', ol=False,
                 extra=f'opacity="0.7" transform="rotate(-20 {cx - 26} {cy - 34})"'))
    s.append(rect(cx - 41, cy - 26, 82, 58, '#1d2833', rx=18))
    led = '#c4f5ff'
    s.append(stroke(f'M{cx - 30} {cy - 2} Q{cx - 20} {cy - 12} {cx - 10} {cy - 2}', led, 4))
    s.append(stroke(f'M{cx - 31} {cy - 15} L{cx - 13} {cy - 13}', led, 3))
    s.append(circ(cx + 18, cy - 4, 10, led, ol=False))
    s.append(circ(cx + 20, cy - 2, 4.5, '#1d2833', ol=False))
    s.append(stroke(f'M{cx + 6} {cy - 21} L{cx + 30} {cy - 25}', led, 3))
    s.append(path(f'M{cx - 26} {cy + 12} Q{cx + 2} {cy + 32} {cx + 32} {cy + 6} '
                  f'Q{cx + 2} {cy + 20} {cx - 26} {cy + 12} Z', led, ol=False,
                  extra=f'stroke="{led}" stroke-width="2"'))
    s.append(rect(cx + 2, cy + 18, 6, 6, '#1d2833', ol=False))
    return ''.join(s)


# ---------------------------------------------------------------- teen

TEEN_BODY = (4, (1325, 736))
TEEN_HEAD = (6, (1325, 422))


def teen_flap():
    return path('M1272 712 L1378 712 Q1384 752 1388 792 Q1325 802 1262 792 Q1266 752 1272 712 Z',
                'url(#maroon)')


def teen_legs():
    s = []
    s.append(tube('M1306 730 L1296 872 L1306 1020', 32, '#2e3040', hl='#5a5d73'))
    s.append(tube('M1346 730 L1352 1022', 32, '#2e3040', hl='#5a5d73'))
    for x0, a in ((1270, -4), (1324, 3)):
        sh = [path('M2 0 L54 0 Q66 0 66 14 L66 28 L-2 28 Q-6 12 2 0 Z', 'url(#white)'),
              rect(-4, 22, 72, 10, '#9a98a6', rx=4),
              stroke('M10 14 L30 6 L50 14', '#ff3fb4', 4)]
        s.append(g(sh, f'translate({x0} 1016) rotate({a} 32 16)'))
    return ''.join(s)


def teen_upper():
    s = []
    hoodie = 'M1270 426 Q1254 566 1264 738 L1386 738 Q1396 566 1380 426 Q1325 406 1270 426 Z'
    s.append(path(hoodie, 'url(#black)'))
    s.append(stroke('M1276 440 Q1262 560 1270 700', '#9d98b3', 4, 'opacity="0.45"'))
    s.append(path('M1282 606 L1368 606 L1382 690 L1268 690 Z', '#34313f'))
    s.append(stroke('M1290 616 L1278 684 M1360 616 L1372 684', '#24222c', 2.5))
    s.append(rect(1262, 714, 126, 26, '#2b2935', rx=6))
    # sweater knotted around the waist
    tie = 'M1258 700 Q1325 720 1392 700 L1394 732 Q1325 752 1256 732 Z'
    s.append(sweater(tie, 1250, 1400, 708, 18))
    s.append(sleeve('M1318 736 Q1308 780 1304 818', 22, 'M1304 806 L1303 822'))
    s.append(sleeve('M1334 736 Q1346 778 1344 812', 22, 'M1344 800 L1344 816'))
    s.append(ell(1326, 734, 17, 14, 'url(#maroon)'))
    # drawstrings
    s.append(stroke('M1308 432 Q1304 470 1306 500', '#d6d3df', 3))
    s.append(stroke('M1342 432 Q1346 470 1344 504', '#d6d3df', 3))
    # crossed arms
    s.append(tube('M1278 444 Q1256 500 1266 550', 34, '#3d3a4b', hl='#77728c'))
    s.append(tube('M1372 444 Q1396 500 1388 550', 34, '#3d3a4b', hl='#77728c'))
    s.append(tube('M1388 552 L1300 524', 34, '#353243', hl='#6a6680'))
    for x, y in ((1286, 512), (1278, 524), (1284, 536)):
        s.append(rect(x - 12, y - 4, 22, 9, '#8e959e', rx=4.5))
    s.append(tube('M1264 550 L1356 522', 34, '#433f52', hl='#837e99'))
    s.append(tube('M1352 523 L1364 519', 36, '#2b2935', cap='butt'))
    for x, y in ((1374, 506), (1382, 518), (1378, 530)):
        s.append(rect(x - 6, y - 4, 20, 9, '#8e959e', rx=4.5))
    # headphone cord to pocket
    s.append(stroke('M1388 360 Q1414 430 1404 500 Q1396 580 1352 640', '#f2f0f5', 2.5))
    return ''.join(s)


def teen_head():
    s = []
    s.append(path('M1266 428 C1250 330 1280 260 1325 258 C1370 260 1400 330 1384 428 Z',
                  'url(#black)'))
    s.append(path('M1284 424 C1276 352 1292 298 1325 296 C1358 298 1374 352 1366 424 Z',
                  '#121118', extra='stroke-width="5"'))
    s.append(stroke('M1270 420 C1256 336 1284 266 1325 262', '#b9b3d6', 4, 'opacity="0.5"'))
    s.append(rect(1290, 316, 70, 82, '#2d2b3a', rx=20))
    s.append(ell(1312, 326, 14, 5, '#ffffff', ol=False, extra='opacity="0.25"'))
    # side-eye visor: pupil shoved to the side, lids at half-mast
    s.append(circ(1308, 350, 30, 'url(#magentaGlow)', ol=False))
    s.append(rect(1295, 336, 60, 28, '#0a090e', rx=12, ol=False))
    s.append(rect(1297, 340, 22, 20, '#ff3fb4', rx=7, ol=False))
    s.append(rect(1300, 350, 6, 5, '#ffd0ee', rx=2, ol=False))
    s.append(rect(1293, 334, 64, 14, '#2d2b3a', ol=False))
    s.append(stroke('M1295 348 L1355 348', '#ff8fd6', 3))
    s.append(stroke('M1314 382 L1336 385', '#ff3fb4', 3.5, 'opacity="0.85"'))
    # headphones over the hood
    band = 'M1268 352 C1258 226 1392 226 1382 352'
    s.append(tube(band, 10, '#f2f0f5'))
    for x in (1252, 1372):
        s.append(rect(x, 324, 26, 54, '#f2f0f5', rx=11))
        s.append(rect(x + 7, 334, 12, 34, '#ff3fb4', rx=6, ol=False))
    return ''.join(s)


# ---------------------------------------------------------------- dog

def dog():
    s = []
    # wagging tail (ghosts first)
    for d, op in (('M712 1010 Q768 1016 792 966', 0.25), ('M712 1010 Q750 984 744 926', 0.25)):
        s.append(f'<g opacity="{op}">{tube(d, 8, "#cf8146")}{circ(*_end(d), 9, "#ffd166")}</g>')
    s.append(tube('M712 1010 Q762 1002 772 944', 8, '#cf8146'))
    s.append(circ(772, 936, 9, '#ffd166'))
    s.append(stroke('M800 930 Q812 950 806 976 M814 920 Q830 948 822 984', '#ffffff', 3,
                    'opacity="0.7"'))
    # haunches and hind paws
    for x in (598, 702):
        s.append(ell(x, 1016, 44, 38, 'url(#copper)'))
    s.append(ell(570, 1056, 24, 10, 'url(#copper)'))
    s.append(ell(730, 1056, 24, 10, 'url(#copper)'))
    # chest in the matching sweater
    chest = 'M600 898 Q586 962 604 1036 L696 1036 Q714 962 700 898 Q650 880 600 898 Z'
    s.append(sweater(chest, 580, 720, 946, 34))
    # front legs
    for x in (628, 672):
        s.append(tube(f'M{x} 1004 L{x} 1050', 22, '#cf8146', hl='#f5bb86'))
        s.append(ell(x + (x - 650) * 0.1, 1058, 21, 11, 'url(#copper)'))
    # head, tilted
    h = []
    h.append(path('M598 806 Q570 810 560 850 Q556 874 576 872 Q592 852 604 828 Z', '#9a5a2a'))
    h.append(path('M698 806 Q712 768 736 750 Q744 792 712 832 Z', '#9a5a2a'))
    h.append(rect(604, 876, 92, 16, '#c8413a', rx=8))
    h.append(circ(650, 904, 10, 'url(#brass)'))
    h.append(rect(592, 790, 116, 92, 'url(#copper)', rx=32))
    h.append(ell(620, 802, 18, 6, '#ffffff', ol=False, extra='opacity="0.6"'))
    h.append(rect(604, 812, 92, 36, '#20262b', rx=17))
    for x in (628, 672):
        h.append(circ(x, 830, 22, 'url(#glowG)', ol=False))
        h.append(circ(x, 830, 12, 'url(#eyeshine)', ol=False))
    h.append(rect(620, 846, 60, 42, '#f2d2ad', rx=17))
    h.append(path('M640 851 L660 851 Q662 862 650 866 Q638 862 640 851 Z', '#18141a'))
    h.append(ell(645, 854, 3, 1.6, '#ffffff', ol=False, extra='opacity="0.8"'))
    h.append(path('M652 878 Q652 904 663 904 Q675 904 673 878 Z', '#e8758a'))
    h.append(stroke('M662 882 L662 896', '#b54a60', 2))
    h.append(stroke('M650 866 L650 874 M634 872 Q650 884 668 872', INK, 3))
    s.append(g(h, 'rotate(-9 650 886)'))
    return g(s, 'translate(650 1062) scale(1.2) translate(-650 -1062)')


def _end(d):
    nums = d.replace('M', ' ').replace('Q', ' ').split()
    return float(nums[-2]), float(nums[-1])


# ---------------------------------------------------------------- assembly

def main():
    # world positions needed across characters
    shoulder = rot((846, 590), MOM_LEAN, MOM_PIVOT)
    hood_top = rot(rot((1320, 294), *TEEN_HEAD), *TEEN_BODY)
    palm = (hood_top[0], hood_top[1])
    fingers_ang = TEEN_BODY[0] + TEEN_HEAD[0] - 4

    fam = []
    fam.append(column_and_fern())
    fam.append(g(teen_flap(), f'rotate({TEEN_BODY[0]} {TEEN_BODY[1][0]} {TEEN_BODY[1][1]})'))
    fam.append(teen_legs())
    fam.append(kid_body(palm, fingers_ang))
    fam.append(g(kid_head(), f'rotate(-7 {KID[0]} {KID[1]})'))
    fam.append(g([teen_upper(), g(teen_head(), f'rotate({TEEN_HEAD[0]} {TEEN_HEAD[1][0]} {TEEN_HEAD[1][1]})')],
                 f'rotate({TEEN_BODY[0]} {TEEN_BODY[1][0]} {TEEN_BODY[1][1]})'))
    fam.append(dad_body())
    fam.append(dad_head())
    fam.append(chair_back())
    fam.append(grandpa_torso())
    fam.append(g(grandpa_head(), 'rotate(-13 395 640)'))
    fam.append(chair_front())
    fam.append(grandpa_front())
    fam.append(bench_and_legs())
    fam.append(g([mom_upper(), g(mom_head(), 'rotate(4 890 548)')],
                 f'rotate({MOM_LEAN} {MOM_PIVOT[0]} {MOM_PIVOT[1]})'))
    fam.append(dad_forearm(shoulder))
    fam.append(dog())

    defs.append(f'<g id="family">{"".join(fam)}</g>')

    m = 34
    frame = (f'<path d="M0 0 H{W} V{H} H0 Z M{m} {m} V{H - m} H{W - m} V{m} Z" '
             f'fill="#f1ead9" fill-rule="evenodd"/>'
             f'<rect x="{m}" y="{m}" width="{W - 2 * m}" height="{H - 2 * m}" fill="none" '
             f'stroke="#000" stroke-opacity="0.25" stroke-width="2"/>')

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{"".join(defs)}</defs>'
           + backdrop() + tape_mark(1160, 1066) + contact_shadows() +
           '<use href="#family" filter="url(#flashShadow)"/>'
           '<use href="#family"/>'
           + grandpa_steam() +
           f'<rect width="{W}" height="{H}" fill="#ffb066" opacity="0.22" style="mix-blend-mode:soft-light"/>'
           f'<rect width="{W}" height="{H}" fill="url(#vignette)"/>'
           f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.05"/>'
           + frame + '</svg>')

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output',
                       'robot_family_portrait.svg')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    xml.dom.minidom.parseString(svg)  # fail loudly on malformed markup
    with open(out, 'w') as fh:
        fh.write(svg)
    print(os.path.normpath(out), len(svg), 'bytes')


if __name__ == '__main__':
    main()
