#!/usr/bin/env python3
"""Generate an SVG illustration: an octopus chef multitasking at a ramen booth (yatai)."""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "output" / "octopus-ramen-chef.svg"
INK = "#33222A"
FONT = "Hiragino Sans, 'Noto Sans JP', sans-serif"
P = []  # svg parts


def add(s):
    P.append(s)


def steam(x, y, s=1.0, op=0.55, n=3):
    out = []
    for i in range(n):
        dx = (i - (n - 1) / 2) * 22 * s
        h = (52 - abs(i - (n - 1) / 2) * 9) * s
        out.append(
            f'<path d="M {x+dx:.0f},{y:.0f} c {-9*s:.0f},{-h*0.35:.0f} {9*s:.0f},{-h*0.6:.0f} 0,{-h:.0f}" '
            f'fill="none" stroke="#FFFFFF" stroke-width="{5.5*s:.1f}" stroke-linecap="round" opacity="{op}"/>'
        )
    return "".join(out)


def bowl(cx, cy, w=110, color="#2A7F7F", toppings=True, empty=False, steam_on=False):
    """Ramen bowl; cy is rim centre, base sits at cy + w*0.42."""
    h = w * 0.42
    hw = w / 2
    g = [f'<g>']
    if steam_on:
        g.append(steam(cx, cy - 12, s=w / 120, op=0.6))
    # foot + body
    g.append(f'<path d="M {cx-hw*0.32:.0f},{cy+h:.0f} h {w*0.64:.0f} l {-w*0.05:.0f},{-h*0.16:.0f} h {-w*0.54:.0f} Z" fill="{color}" stroke="{INK}" stroke-width="3"/>')
    g.append(f'<path d="M {cx-hw:.0f},{cy:.0f} C {cx-hw:.0f},{cy+h*0.72:.0f} {cx-hw*0.55:.0f},{cy+h*0.92:.0f} {cx:.0f},{cy+h*0.92:.0f} '
             f'C {cx+hw*0.55:.0f},{cy+h*0.92:.0f} {cx+hw:.0f},{cy+h*0.72:.0f} {cx+hw:.0f},{cy:.0f} Z" fill="{color}" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')
    # decorative stripe + dot pattern on body
    g.append(f'<path d="M {cx-hw*0.86:.0f},{cy+h*0.34:.0f} C {cx-hw*0.4:.0f},{cy+h*0.5:.0f} {cx+hw*0.4:.0f},{cy+h*0.5:.0f} {cx+hw*0.86:.0f},{cy+h*0.34:.0f}" fill="none" stroke="#FFF3D6" stroke-width="{w*0.045:.1f}" opacity="0.85"/>')
    for i in range(-2, 3):
        g.append(f'<circle cx="{cx+i*w*0.16:.0f}" cy="{cy+h*0.58:.0f}" r="{w*0.028:.1f}" fill="#FFF3D6" opacity="0.9"/>')
    # rim / broth
    broth = "#F3E9D2" if empty else "url(#broth)"
    g.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{hw:.0f}" ry="{w*0.13:.0f}" fill="{broth}" stroke="{INK}" stroke-width="3.5"/>')
    if not empty:
        # noodle swirl
        g.append(f'<path d="M {cx-hw*0.62:.0f},{cy+1:.0f} q {w*0.12:.0f},{-w*0.09:.0f} {w*0.24:.0f},0 q {w*0.12:.0f},{w*0.09:.0f} {w*0.24:.0f},0 q {w*0.12:.0f},{-w*0.09:.0f} {w*0.2:.0f},{-w*0.01:.0f}" fill="none" stroke="#FFE3A1" stroke-width="{w*0.05:.1f}" stroke-linecap="round"/>')
    if toppings and not empty:
        # nori sheet (back right)
        g.append(f'<rect x="{cx+hw*0.34:.0f}" y="{cy-w*0.3:.0f}" width="{w*0.3:.0f}" height="{w*0.3:.0f}" rx="3" fill="#26352B" stroke="{INK}" stroke-width="2.5" transform="rotate(9 {cx+hw*0.49:.0f} {cy-w*0.15:.0f})"/>')
        # chashu slice
        g.append(f'<circle cx="{cx-hw*0.42:.0f}" cy="{cy-w*0.015:.0f}" r="{w*0.13:.0f}" fill="#C97B52" stroke="{INK}" stroke-width="2.5"/>')
        g.append(f'<path d="M {cx-hw*0.5:.0f},{cy-w*0.01:.0f} a {w*0.07:.0f},{w*0.07:.0f} 0 1,1 {w*0.1:.0f},{w*0.045:.0f} a {w*0.035:.0f},{w*0.035:.0f} 0 1,0 {-w*0.06:.0f},{-w*0.02:.0f}" fill="none" stroke="#F3C39A" stroke-width="2.2"/>')
        # halved egg
        g.append(f'<ellipse cx="{cx+hw*0.08:.0f}" cy="{cy+w*0.012:.0f}" rx="{w*0.15:.0f}" ry="{w*0.095:.0f}" fill="#FFFFFF" stroke="{INK}" stroke-width="2.5"/>')
        g.append(f'<ellipse cx="{cx+hw*0.08:.0f}" cy="{cy+w*0.012:.0f}" rx="{w*0.075:.0f}" ry="{w*0.05:.0f}" fill="#FFB020"/>')
        # narutomaki
        nx, ny = cx + hw * 0.52, cy + w * 0.02
        g.append(f'<circle cx="{nx:.0f}" cy="{ny:.0f}" r="{w*0.085:.0f}" fill="#FFFFFF" stroke="{INK}" stroke-width="2.2"/>')
        g.append(f'<path d="M {nx-w*0.04:.0f},{ny:.0f} a {w*0.04:.0f},{w*0.04:.0f} 0 1,1 {w*0.05:.0f},{w*0.03:.0f} a {w*0.018:.0f},{w*0.018:.0f} 0 1,0 {-w*0.03:.0f},{-w*0.012:.0f}" fill="none" stroke="#FF7A9E" stroke-width="2.2"/>')
        # scallions
        rng = random.Random(int(cx))
        for _ in range(7):
            gx = cx + rng.uniform(-hw * 0.55, hw * 0.55)
            gy = cy + rng.uniform(-w * 0.05, w * 0.06)
            g.append(f'<circle cx="{gx:.0f}" cy="{gy:.0f}" r="{w*0.026:.1f}" fill="none" stroke="#3FA34D" stroke-width="2"/>')
    g.append("</g>")
    return "".join(g)


def tentacle(d, suckers=(), w=32):
    g = [f'<path d="{d}" fill="none" stroke="#F45564" stroke-width="{w}" stroke-linecap="round"/>']
    g.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w+7}" stroke-linecap="round" opacity="0"/>')
    for (x, y, r) in suckers:
        g.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFC4C9" stroke="#E8848F" stroke-width="1.4"/>')
    return "".join(g)


def lantern(x, cy, label, big=True):
    rx, ry = (44, 54) if big else (34, 42)
    g = [f'<ellipse cx="{x}" cy="{cy}" rx="{rx*2.1:.0f}" ry="{ry*1.9:.0f}" fill="url(#glow)"/>']
    g.append(f'<line x1="{x}" y1="{cy-ry-34}" x2="{x}" y2="{cy-ry-8}" stroke="{INK}" stroke-width="3"/>')
    g.append(f'<rect x="{x-15}" y="{cy-ry-10}" width="30" height="13" rx="3" fill="#2B2B33" stroke="{INK}" stroke-width="2.5"/>')
    g.append(f'<ellipse cx="{x}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#lantern)" stroke="{INK}" stroke-width="3.5"/>')
    for k in (-0.62, -0.3, 0.3, 0.62):
        g.append(f'<path d="M {x+k*rx:.0f},{cy-ry*0.92:.0f} C {x+k*rx*1.25:.0f},{cy-ry*0.3:.0f} {x+k*rx*1.25:.0f},{cy+ry*0.3:.0f} {x+k*rx:.0f},{cy+ry*0.92:.0f}" fill="none" stroke="#B5392F" stroke-width="2" opacity="0.55"/>')
    g.append(f'<ellipse cx="{x-rx*0.38:.0f}" cy="{cy-ry*0.42:.0f}" rx="{rx*0.2:.0f}" ry="{ry*0.3:.0f}" fill="#FFFFFF" opacity="0.35"/>')
    if len(label) == 1:
        g.append(f'<text x="{x}" y="{cy+13}" font-family="{FONT}" font-size="36" font-weight="700" fill="#FFF7E0" text-anchor="middle">{label}</text>')
    else:
        for i, ch in enumerate(label):
            g.append(f'<text x="{x}" y="{cy-6+i*30}" font-family="{FONT}" font-size="24" font-weight="700" fill="#FFF7E0" text-anchor="middle">{ch}</text>')
    g.append(f'<rect x="{x-15}" y="{cy+ry-3}" width="30" height="13" rx="3" fill="#2B2B33" stroke="{INK}" stroke-width="2.5"/>')
    g.append(f'<path d="M {x},{cy+ry+10} v 16 M {x-7},{cy+ry+12} v 13 M {x+7},{cy+ry+12} v 13" stroke="#E8B33C" stroke-width="3" stroke-linecap="round"/>')
    return "".join(g)


def stool(x, y=752):
    return (
        f'<g stroke="{INK}" stroke-width="3">'
        f'<line x1="{x-34}" y1="{y+6}" x2="{x-44}" y2="{y+74}" stroke="#5A3A22" stroke-width="7" stroke-linecap="round"/>'
        f'<line x1="{x+34}" y1="{y+6}" x2="{x+44}" y2="{y+74}" stroke="#5A3A22" stroke-width="7" stroke-linecap="round"/>'
        f'<line x1="{x-40}" y1="{y+48}" x2="{x+40}" y2="{y+48}" stroke="#5A3A22" stroke-width="5"/>'
        f'<ellipse cx="{x}" cy="{y}" rx="54" ry="15" fill="#C93B31"/>'
        f'<ellipse cx="{x}" cy="{y-4}" rx="54" ry="14" fill="#DE5348"/>'
        f'</g>'
    )


# ---------------------------------------------------------------- defs
add('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="1200" height="900" role="img" aria-labelledby="t d">
<title id="t">Octopus chef at a ramen booth</title>
<desc id="d">A cheerful octopus chef in a toque runs a night-market ramen stall, using all eight tentacles at once: lifting noodles, ladling broth, garnishing and serving bowls, while a cat customer waits at the counter.</desc>
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#131C3C"/><stop offset="0.55" stop-color="#27335E"/><stop offset="1" stop-color="#5A4059"/>
</linearGradient>
<linearGradient id="interior" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#FFE7AC"/><stop offset="1" stop-color="#FFB26B"/>
</linearGradient>
<radialGradient id="octo" cx="0.42" cy="0.3" r="0.95">
<stop offset="0" stop-color="#FFA3AB"/><stop offset="0.55" stop-color="#FF6B78"/><stop offset="1" stop-color="#EE4759"/>
</radialGradient>
<linearGradient id="wood" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#C08A4E"/><stop offset="1" stop-color="#8F5C2B"/>
</linearGradient>
<linearGradient id="counterFront" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#A66C38"/><stop offset="1" stop-color="#71441F"/>
</linearGradient>
<linearGradient id="metal" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#9AA5B5"/><stop offset="0.35" stop-color="#E3E9F1"/><stop offset="0.7" stop-color="#A7B1C0"/><stop offset="1" stop-color="#7E8A9C"/>
</linearGradient>
<radialGradient id="broth" cx="0.5" cy="0.5" r="0.6">
<stop offset="0" stop-color="#FFCE66"/><stop offset="1" stop-color="#F1942B"/>
</radialGradient>
<radialGradient id="lantern" cx="0.42" cy="0.38" r="0.85">
<stop offset="0" stop-color="#FFE3A1"/><stop offset="0.55" stop-color="#FF8A50"/><stop offset="1" stop-color="#E83E2E"/>
</radialGradient>
<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
<stop offset="0" stop-color="#FFD98A" stop-opacity="0.5"/><stop offset="1" stop-color="#FFD98A" stop-opacity="0"/>
</radialGradient>
<linearGradient id="roof" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#D14A3E"/><stop offset="1" stop-color="#9C2A22"/>
</linearGradient>
<radialGradient id="vign" cx="0.5" cy="0.46" r="0.85">
<stop offset="0.62" stop-color="#000000" stop-opacity="0"/><stop offset="1" stop-color="#0B0F22" stop-opacity="0.38"/>
</radialGradient>
<filter id="blur14" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="14"/></filter>
</defs>''')

# ---------------------------------------------------------------- background
add('<rect x="0" y="0" width="1200" height="900" fill="url(#sky)"/>')
rng = random.Random(7)
stars = []
for _ in range(70):
    x, y = rng.uniform(8, 1192), rng.uniform(8, 330)
    r = rng.uniform(1, 2.6)
    stars.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#FFF6D8" opacity="{rng.uniform(0.35,0.95):.2f}"/>')
add("".join(stars))
# crescent moon, top right
add('<circle cx="1092" cy="74" r="34" fill="#FFF3C4"/><circle cx="1078" cy="64" r="29" fill="#1B2549"/>')
# distant skyline silhouettes at the edges
add(f'<g fill="#1A2342"><rect x="-10" y="300" width="90" height="470"/><rect x="70" y="380" width="80" height="390"/>'
    f'<rect x="1050" y="350" width="85" height="420"/><rect x="1125" y="270" width="90" height="500"/></g>')
wins = []
for bx, by, bw, bh in [(0, 320, 70, 420), (78, 400, 62, 340), (1058, 370, 66, 370), (1135, 290, 60, 450)]:
    for _ in range(9):
        wins.append(f'<rect x="{bx+rng.uniform(4,bw-14):.0f}" y="{by+rng.uniform(4,bh-70):.0f}" width="9" height="12" fill="#FFD98A" opacity="{rng.uniform(0.25,0.8):.2f}"/>')
add("".join(wins))
# ground + pool of warm light
add('<rect x="0" y="762" width="1200" height="138" fill="#222A45"/>')
add('<ellipse cx="600" cy="812" rx="580" ry="72" fill="#FFB26B" opacity="0.16" filter="url(#blur14)"/>')
add('<path d="M 0,762 H 1200" stroke="#39436B" stroke-width="3"/>')
for gx in range(80, 1200, 150):
    add(f'<path d="M {gx},900 L {gx+60},764" stroke="#2C3557" stroke-width="3"/>')

# ---------------------------------------------------------------- booth interior
add(f'<rect x="225" y="205" width="750" height="388" fill="url(#interior)" stroke="{INK}" stroke-width="3.5"/>')
# warm glow inside
add('<ellipse cx="600" cy="400" rx="360" ry="200" fill="url(#glow)"/>')
# left shelf: stacked bowls + bottles
add(f'<rect x="242" y="312" width="150" height="10" rx="3" fill="#8F5C2B" stroke="{INK}" stroke-width="2.5"/>')
for i, yy in enumerate([312, 300, 288]):
    add(f'<path d="M 252,{yy} a 26,12 0 0,0 52,0 Z" fill="{"#2A7F7F" if i%2==0 else "#EFE6D0"}" stroke="{INK}" stroke-width="2.2"/>')
for bx, col, bh in [(322, "#7A3B2E", 44), (346, "#2E6B4F", 54), (370, "#B5392F", 38)]:
    add(f'<g stroke="{INK}" stroke-width="2.2"><rect x="{bx}" y="{312-bh}" width="18" height="{bh}" rx="5" fill="{col}"/>'
        f'<rect x="{bx+5}" y="{312-bh-10}" width="8" height="12" rx="2" fill="{col}"/>'
        f'<rect x="{bx+3}" y="{312-bh+12}" width="12" height="14" fill="#FFF3D6" stroke="none"/></g>')
# right shelf: bottles + menu plaques
add(f'<rect x="805" y="312" width="150" height="10" rx="3" fill="#8F5C2B" stroke="{INK}" stroke-width="2.5"/>')
for bx, col, bh in [(818, "#B5892E", 40), (844, "#7A3B2E", 52), (870, "#2A7F7F", 36), (896, "#4A3A6B", 48), (922, "#B5392F", 42)]:
    add(f'<g stroke="{INK}" stroke-width="2.2"><rect x="{bx}" y="{312-bh}" width="18" height="{bh}" rx="5" fill="{col}"/>'
        f'<rect x="{bx+5}" y="{312-bh-10}" width="8" height="12" rx="2" fill="{col}"/>'
        f'<rect x="{bx+3}" y="{312-bh+12}" width="12" height="14" fill="#FFF3D6" stroke="none"/></g>')
# (the menu board hangs on the counter front, added with the counter below)

# noren curtains (behind the chef's hat)
noren_chars = ["た", "こ", "ラ", "麺"]
for i in range(4):
    nx = 229 + i * 187
    add(f'<rect x="{nx}" y="205" width="180" height="86" fill="#2E4A7A" stroke="{INK}" stroke-width="3"/>')
    add(f'<circle cx="{nx+90}" cy="262" r="23" fill="none" stroke="#FFF3D6" stroke-width="3"/>')
    add(f'<text x="{nx+90}" y="273" font-family="{FONT}" font-size="26" font-weight="700" fill="#FFF3D6" text-anchor="middle">{noren_chars[i]}</text>')

# ---------------------------------------------------------------- noodle pot (left)
add(steam(325, 468, s=1.25, op=0.5))
add(f'<rect x="278" y="572" width="96" height="14" rx="4" fill="#3A3A44" stroke="{INK}" stroke-width="2.5"/>')
add('<path d="M 296,572 q 8,-12 16,0 q 8,-14 16,0 q 8,-12 16,0 q 8,-13 14,0" fill="#5EA8E8" opacity="0.85"/>')
add(f'<path d="M 254,486 L 398,486 L 388,574 Q 326,586 264,574 Z" fill="url(#metal)" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')
add(f'<path d="M 254,486 a 18,10 0 0,0 -4,20 M 398,486 a 18,10 0 0,1 4,20" fill="none" stroke="{INK}" stroke-width="4"/>')
add(f'<rect x="282" y="500" width="16" height="58" rx="8" fill="#FFFFFF" opacity="0.4"/>')
add(f'<ellipse cx="326" cy="486" rx="72" ry="16" fill="#C9D2DE" stroke="{INK}" stroke-width="3.5"/>')
add('<ellipse cx="326" cy="486" rx="59" ry="11.5" fill="url(#broth)"/>')
add('<path d="M 282,486 q 10,-7 20,0 q 10,7 20,0 q 10,-7 20,0 q 10,6 18,1" fill="none" stroke="#FFE3A1" stroke-width="4.5" stroke-linecap="round"/>')
for bx, by, br in [(296, 482, 4), (340, 490, 3), (362, 483, 3.5), (315, 491, 2.6)]:
    add(f'<circle cx="{bx}" cy="{by}" r="{br}" fill="#FFE9B8" stroke="#E8A33C" stroke-width="1.2"/>')

# ---------------------------------------------------------------- back tentacles (6 of 8)
# L1: holds the "open" nobori flag pole
add(tentacle("M 480,515 C 392,505 302,470 252,410 C 237,391 227,371 218,352",
             suckers=[(262, 425, 5), (242, 398, 5), (228, 370, 4.5)]))
# L2: chopsticks lifting noodles from the pot
add(tentacle("M 475,545 C 422,500 384,448 368,388 C 362,366 359,353 357,341",
             suckers=[(383, 440, 5), (369, 395, 5), (361, 360, 4.5)]))
# L3: ladle scooping broth
add(tentacle("M 465,562 C 400,566 340,541 300,501 C 285,486 277,472 271,458",
             suckers=[(322, 532, 5), (294, 496, 5), (278, 470, 4.5)]))
# R1: holding an order ticket
add(tentacle("M 722,515 C 808,500 888,441 923,377 C 936,352 943,336 946,321",
             suckers=[(900, 418, 5), (928, 372, 5), (941, 338, 4.5)]))
# R2: serving a finished bowl
add(tentacle("M 733,545 C 799,536 844,507 851,467 C 853,456 852,449 850,443",
             suckers=[(822, 518, 5), (846, 486, 5)]))
# R3: sprinkling scallions
add(tentacle("M 728,565 C 774,559 809,540 827,511 C 837,496 841,485 843,473",
             suckers=[(806, 541, 5), (829, 507, 5), (840, 483, 4.5)]))

# (nobori flag is drawn later, in front of the booth post)

# chopsticks + lifted noodle bundle
add(f'<g stroke="#7A4A22" stroke-width="5.5" stroke-linecap="round"><line x1="357" y1="338" x2="324" y2="428"/><line x1="370" y1="341" x2="344" y2="430"/></g>')
noodles = []
for i, nx0 in enumerate([322, 330, 338, 346]):
    noodles.append(f'<path d="M {nx0},424 c -7,14 5,22 -1,34 c -5,10 2,18 0,26" fill="none" stroke="#FFD98A" stroke-width="5" stroke-linecap="round"/>')
noodles.append('<path d="M 318,424 q 16,-13 34,-3 q 12,7 4,14 q -20,8 -38,-2 q -9,-6 0,-9" fill="none" stroke="#FFD98A" stroke-width="5" stroke-linecap="round"/>')
noodles.append('<path d="M 326,416 q 12,-9 24,-2" fill="none" stroke="#FFE9B8" stroke-width="4" stroke-linecap="round"/>')
add("".join(noodles))

# ladle
add(f'<line x1="270" y1="455" x2="293" y2="478" stroke="#7E8A9C" stroke-width="6" stroke-linecap="round"/>')
add(f'<ellipse cx="300" cy="484" rx="17" ry="8.5" fill="url(#metal)" stroke="{INK}" stroke-width="2.5"/>')
add('<ellipse cx="300" cy="483" rx="12" ry="5" fill="url(#broth)"/>')

# order ticket
add(f'<g transform="rotate(11 948 285)"><rect x="925" y="250" width="48" height="74" rx="4" fill="#FFF7E6" stroke="{INK}" stroke-width="2.8"/>'
    f'<rect x="925" y="250" width="48" height="14" fill="#C93B31"/>'
    f'<circle cx="949" cy="274" r="3.5" fill="none" stroke="#9AA5B5" stroke-width="2"/>'
    f'<path d="M 933,288 h 32 M 933,299 h 24 M 933,310 h 29" stroke="#9AA5B5" stroke-width="3" stroke-linecap="round"/></g>')

# scallions falling from R3 toward the garnish bowl
rng2 = random.Random(11)
bits = []
for _ in range(11):
    t = rng2.random()
    gx = 843 + (835 - 843) * t + rng2.uniform(-13, 13)
    gy = 484 + (528 - 484) * t
    bits.append(f'<circle cx="{gx:.0f}" cy="{gy:.0f}" r="3.4" fill="none" stroke="#3FA34D" stroke-width="2.2"/>')
add("".join(bits))

# ---------------------------------------------------------------- octopus head
add(f'<path d="M 437,478 C 437,356 506,274 600,274 C 694,274 763,356 763,478 '
    f'C 763,558 698,602 600,602 C 502,602 437,558 437,478 Z" fill="url(#octo)" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
# mantle spots
for sx, sy, sr, so in [(478, 340, 13, 0.5), (505, 312, 8, 0.45), (715, 338, 11, 0.5), (692, 310, 7, 0.4), (468, 395, 8, 0.35), (732, 400, 8, 0.35)]:
    add(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="#FF9AA3" opacity="{so}"/>')
# face: brows, eyes, blush, mouth
add(f'<path d="M 514,398 Q 540,384 566,398 M 634,398 Q 660,384 686,398" fill="none" stroke="{INK}" stroke-width="5.5" stroke-linecap="round"/>')
for ex in (540, 660):
    add(f'<ellipse cx="{ex}" cy="432" rx="16" ry="23" fill="#26202B"/>')
    add(f'<circle cx="{ex-5}" cy="423" r="6" fill="#FFFFFF"/><circle cx="{ex+6}" cy="441" r="3.2" fill="#FFFFFF" opacity="0.85"/>')
add('<ellipse cx="488" cy="476" rx="24" ry="13" fill="#FF8FA3" opacity="0.75"/>')
add('<ellipse cx="712" cy="476" rx="24" ry="13" fill="#FF8FA3" opacity="0.75"/>')
add(f'<path d="M 576,474 C 588,494 612,494 624,474 C 612,483 588,483 576,474 Z" fill="#7E2434" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
add('<path d="M 590,488 q 10,5 20,0 q -4,7 -10,7 q -6,0 -10,-7" fill="#FF8FA3"/>')
add(f'<circle cx="600" cy="458" r="2.6" fill="#D63E50"/><circle cx="596" cy="510" r="2.2" fill="#D63E50" opacity="0.6"/>')
# neckerchief
add(f'<path d="M 510,544 Q 600,572 690,544 L 680,580 Q 600,602 520,580 Z" fill="#2A9D8F" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')
add(f'<path d="M 588,570 L 600,596 L 614,570 Q 600,578 588,570 Z" fill="#2A9D8F" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
add(f'<circle cx="600" cy="568" r="11" fill="#21867A" stroke="{INK}" stroke-width="3"/>')
# (the toque is drawn later, after the roof, so it pops in front of the booth frame)

# served bowl (held out by R2) + sparkles
add(bowl(850, 396, w=124, color="#C93B31", steam_on=True))
for sx, sy, sr in [(762, 348, 13), (940, 372, 10), (912, 312, 8)]:
    add(f'<path d="M {sx},{sy-sr} L {sx+sr*0.28:.0f},{sy-sr*0.28:.0f} L {sx+sr},{sy} L {sx+sr*0.28:.0f},{sy+sr*0.28:.0f} '
        f'L {sx},{sy+sr} L {sx-sr*0.28:.0f},{sy+sr*0.28:.0f} L {sx-sr},{sy} L {sx-sr*0.28:.0f},{sy-sr*0.28:.0f} Z" fill="#FFD166" stroke="{INK}" stroke-width="1.6"/>')

# ---------------------------------------------------------------- counter
add(f'<rect x="170" y="618" width="860" height="152" fill="url(#counterFront)" stroke="{INK}" stroke-width="3.5"/>')
for px in range(256, 1030, 86):
    add(f'<line x1="{px}" y1="624" x2="{px}" y2="766" stroke="#5E3A1E" stroke-width="3" opacity="0.55"/>')
add(f'<rect x="148" y="576" width="904" height="44" rx="9" fill="url(#wood)" stroke="{INK}" stroke-width="4"/>')
add('<path d="M 160,586 H 1040" stroke="#FFFFFF" stroke-width="3" opacity="0.3"/>')
# counter-front plaque
add(f'<rect x="506" y="652" width="188" height="54" rx="8" fill="#FFF3D6" stroke="{INK}" stroke-width="3"/>')
add(f'<text x="600" y="688" font-family="{FONT}" font-size="27" font-weight="700" fill="#B5392F" text-anchor="middle">ラーメン</text>')
for cxp, cyp in [(518, 664), (682, 664), (518, 694), (682, 694)]:
    add(f'<circle cx="{cxp}" cy="{cyp}" r="2.6" fill="#8F5C2B"/>')
# menu board on the counter front (left)
add(f'<rect x="246" y="644" width="200" height="100" rx="7" fill="#3E2A1C" stroke="{INK}" stroke-width="3.5"/>')
add(f'<rect x="256" y="654" width="180" height="80" rx="5" fill="none" stroke="#C08A4E" stroke-width="2"/>')
add(f'<text x="346" y="674" font-family="{FONT}" font-size="16" font-weight="700" fill="#FFD166" text-anchor="middle">〜 メニュー 〜</text>')
for i, (label, price) in enumerate([("しょうゆ", "¥800"), ("みそ", "¥850"), ("たこ特製", "¥980")]):
    yy = 696 + i * 17
    add(f'<text x="270" y="{yy}" font-family="{FONT}" font-size="14" font-weight="700" fill="#FFF3D6">{label}</text>')
    add(f'<text x="424" y="{yy}" font-family="{FONT}" font-size="13.5" font-weight="700" fill="#FF8FA3" text-anchor="end">{price}</text>')

# front tentacles (7 & 8) draped over the counter
add(f'<g transform="rotate(-7 800 606)"><rect x="766" y="596" width="68" height="21" rx="8" fill="#7AC5CD" stroke="{INK}" stroke-width="2.8"/>'
    f'<path d="M 782,597 v 19 M 800,597 v 19 M 818,597 v 19" stroke="#4E9AA6" stroke-width="2.4"/></g>')
add(tentacle("M 548,584 C 500,594 455,592 425,575 C 408,565 398,556 393,547",
             suckers=[(470, 590, 4.6), (428, 576, 4.6), (402, 559, 4.2)], w=28))
add(tentacle("M 655,584 C 700,595 748,600 782,601 C 794,601 802,603 807,608",
             suckers=[(712, 593, 4.6), (758, 599, 4.6)], w=28))

# bowls + condiments on the counter
add(bowl(438, 538, w=104, color="#EFE6D0", empty=True, toppings=False))
add(f'<g stroke="#7A4A22" stroke-width="4.5" stroke-linecap="round"><line x1="398" y1="528" x2="478" y2="516"/><line x1="400" y1="536" x2="476" y2="526"/></g>')
add(bowl(835, 532, w=112, color="#2A7F7F", steam_on=True))
add(f'<g stroke="{INK}" stroke-width="2.5"><rect x="714" y="538" width="34" height="40" rx="5" fill="#8F5C2B"/>'
    f'<path d="M 722,538 L 716,504 M 731,538 L 731,500 M 740,538 L 748,506" stroke="#7A4A22" stroke-width="4" stroke-linecap="round"/>'
    f'<rect x="672" y="544" width="20" height="34" rx="6" fill="#C93B31"/><rect x="677" y="534" width="10" height="11" rx="2" fill="#7E2019"/>'
    f'<rect x="646" y="552" width="17" height="26" rx="5" fill="#E8EDF3"/><rect x="649" y="543" width="11" height="10" rx="2" fill="#9AA5B5"/></g>')

# ---------------------------------------------------------------- booth frame front
for postx in (188, 976):
    add(f'<rect x="{postx}" y="198" width="36" height="584" fill="#6B3F23" stroke="{INK}" stroke-width="3.5"/>')
    add(f'<path d="M {postx+11},210 v 560 M {postx+25},210 v 560" stroke="#8F5C2B" stroke-width="2.5" opacity="0.7"/>')

# nobori flag in front of the left post, with a tentacle-tip grip on the pole
add(f'<line x1="208" y1="238" x2="208" y2="374" stroke="#5A3A22" stroke-width="5" stroke-linecap="round"/>')
add(f'<rect x="208" y="244" width="44" height="108" rx="3" fill="#FFF3D6" stroke="{INK}" stroke-width="3"/>')
add('<rect x="208" y="244" width="44" height="18" fill="#C93B31"/>')
for i, ch in enumerate("営業中"):
    add(f'<text x="230" y="{290+i*27}" font-family="{FONT}" font-size="21" font-weight="700" fill="#33222A" text-anchor="middle">{ch}</text>')
add(f'<circle cx="211" cy="354" r="13" fill="#F45564" stroke="{INK}" stroke-width="2.5"/>')
add('<circle cx="208" cy="351" r="4" fill="#FFC4C9"/>')

# roof, fascia, rooftop sign
add(f'<polygon points="150,200 1050,200 988,110 212,110" fill="url(#roof)" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
for ty in (138, 167):
    lx = 212 - (ty - 110) * 62 / 90
    rxp = 988 + (ty - 110) * 62 / 90
    add(f'<path d="M {lx:.0f},{ty} H {rxp:.0f}" stroke="#7E2019" stroke-width="3" opacity="0.5" stroke-dasharray="26 14"/>')
add(f'<rect x="206" y="90" width="788" height="23" rx="7" fill="#5A3A22" stroke="{INK}" stroke-width="3"/>')
add(f'<rect x="138" y="196" width="924" height="30" fill="#5A3A22" stroke="{INK}" stroke-width="3.5"/>')
add(f'<g stroke="{INK}" stroke-width="5" stroke-linecap="round"><line x1="455" y1="98" x2="440" y2="114"/><line x1="745" y1="98" x2="760" y2="114"/></g>')
add(f'<rect x="382" y="36" width="436" height="64" rx="10" fill="#FFF3D6" stroke="{INK}" stroke-width="4"/>')
add(f'<rect x="394" y="46" width="412" height="44" rx="7" fill="none" stroke="#C93B31" stroke-width="2"/>')
add(f'<g><circle cx="433" cy="66" r="15" fill="#FF6B78" stroke="{INK}" stroke-width="2.5"/>'
    f'<circle cx="422" cy="79" r="5" fill="#FF6B78" stroke="{INK}" stroke-width="2"/>'
    f'<circle cx="433" cy="81" r="5" fill="#FF6B78" stroke="{INK}" stroke-width="2"/>'
    f'<circle cx="444" cy="79" r="5" fill="#FF6B78" stroke="{INK}" stroke-width="2"/>'
    f'<rect x="422" y="48" width="22" height="9" rx="3" fill="#FFFFFF" stroke="{INK}" stroke-width="2"/>'
    f'<circle cx="428" cy="65" r="2" fill="#26202B"/><circle cx="438" cy="65" r="2" fill="#26202B"/></g>')
add(f'<text x="628" y="81" font-family="{FONT}" font-size="36" font-weight="700" fill="#B5392F" text-anchor="middle" letter-spacing="2">TAKO RAMEN</text>')

# string lights along the fascia
bulb_colors = ["#FFD166", "#FF8FA3", "#7AE0C3", "#FFF3D6"]
lights = []
for span in range(4):
    x0 = 155 + span * 222.5
    x1 = x0 + 222.5
    lights.append(f'<path d="M {x0:.0f},228 Q {(x0+x1)/2:.0f},244 {x1:.0f},228" fill="none" stroke="#2B2B33" stroke-width="2.5"/>')
    for j, t in enumerate((0.25, 0.5, 0.75)):
        bx = x0 + (x1 - x0) * t
        by = (1 - t) ** 2 * 228 + 2 * t * (1 - t) * 244 + t ** 2 * 228
        col = bulb_colors[(span * 3 + j) % 4]
        lights.append(f'<circle cx="{bx:.0f}" cy="{by+8:.0f}" r="13" fill="{col}" opacity="0.28"/>')
        lights.append(f'<line x1="{bx:.0f}" y1="{by:.0f}" x2="{bx:.0f}" y2="{by+5:.0f}" stroke="#2B2B33" stroke-width="2"/>')
        lights.append(f'<circle cx="{bx:.0f}" cy="{by+11:.0f}" r="6.5" fill="{col}" stroke="{INK}" stroke-width="1.8"/>')
add("".join(lights))

# chef's toque, popping in front of the roof beam
add(f'<g transform="rotate(-4 600 245)">'
    f'<ellipse cx="545" cy="214" rx="50" ry="40" fill="#FFFFFF" stroke="{INK}" stroke-width="3.5"/>'
    f'<ellipse cx="655" cy="214" rx="50" ry="40" fill="#FFFFFF" stroke="{INK}" stroke-width="3.5"/>'
    f'<ellipse cx="600" cy="196" rx="60" ry="48" fill="#FFFFFF" stroke="{INK}" stroke-width="3.5"/>'
    f'<path d="M 552,202 q 9,14 4,30 M 600,192 q 4,20 -2,38 M 648,202 q -9,14 -4,30" fill="none" stroke="#D8E0EA" stroke-width="4"/>'
    f'<rect x="508" y="232" width="184" height="48" rx="12" fill="#F4F7FB" stroke="{INK}" stroke-width="3.5"/>'
    f'<path d="M 516,256 h 168" stroke="#D8E0EA" stroke-width="4"/>'
    f'<circle cx="600" cy="256" r="12.5" fill="#C93B31" stroke="{INK}" stroke-width="2.5"/>'
    f'<text x="600" y="261.5" font-family="{FONT}" font-size="14" font-weight="700" fill="#FFF3D6" text-anchor="middle">た</text>'
    f'</g>')

# hanging lanterns
add(lantern(168, 318, "麺"))
add(lantern(1032, 318, "たこ"))

# ---------------------------------------------------------------- stools + cat customer
for sx in (290, 520, 885):
    add(f'<ellipse cx="{sx}" cy="842" rx="72" ry="12" fill="#141B33" opacity="0.5"/>')
add(stool(290))
add(stool(520))
# the cat stands on the ground, paws up on the counter (no stool)
add(f'<path d="M 938,802 C 984,796 1001,762 986,736" fill="none" stroke="#F59A3C" stroke-width="17" stroke-linecap="round"/>')
add(f'<path d="M 991,752 C 994,746 990,739 986,736" fill="none" stroke="#D97925" stroke-width="17" stroke-linecap="round"/>')
add(f'<path d="M 848,758 C 838,712 838,676 844,646 M 922,758 C 932,712 932,676 926,646" fill="none" stroke="#F59A3C" stroke-width="20" stroke-linecap="round"/>')
add(f'<ellipse cx="885" cy="796" rx="64" ry="56" fill="#F59A3C" stroke="{INK}" stroke-width="3.5"/>')
add('<path d="M 828,772 q 14,6 26,2 M 826,796 q 14,5 26,1 M 916,773 q 13,3 26,-2 M 918,797 q 13,3 26,-1" fill="none" stroke="#D97925" stroke-width="5" stroke-linecap="round"/>')
add(f'<polygon points="848,674 835,631 878,653" fill="#F59A3C" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')
add(f'<polygon points="922,674 935,631 892,653" fill="#F59A3C" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')
add('<polygon points="850,663 844,643 866,655" fill="#FFB8C4"/><polygon points="920,663 926,643 904,655" fill="#FFB8C4"/>')
add(f'<circle cx="885" cy="707" r="51" fill="#F59A3C" stroke="{INK}" stroke-width="3.5"/>')
add('<path d="M 863,667 q 4,11 2,19 M 885,661 v 21 M 907,667 q -4,11 -2,19" fill="none" stroke="#D97925" stroke-width="5" stroke-linecap="round"/>')
add('<path d="M 834,712 l -12,5 l 12,5 M 936,712 l 12,5 l -12,5" fill="none" stroke="#D97925" stroke-width="3.5" stroke-linecap="round"/>')
for pxp in (845, 925):
    add(f'<ellipse cx="{pxp}" cy="638" rx="15" ry="11" fill="#FFB066" stroke="{INK}" stroke-width="3"/>')
    add(f'<path d="M {pxp-5},631 v 7 M {pxp+5},631 v 7" stroke="{INK}" stroke-width="2"/>')

add('<rect x="0" y="0" width="1200" height="900" fill="url(#vign)"/>')
add('</svg>')

OUT.parent.mkdir(parents=True, exist_ok=True)
svg = "\n".join(P)
OUT.write_text(svg, encoding="utf-8")
print(f"wrote {OUT} ({len(svg.encode('utf-8'))} bytes)")
