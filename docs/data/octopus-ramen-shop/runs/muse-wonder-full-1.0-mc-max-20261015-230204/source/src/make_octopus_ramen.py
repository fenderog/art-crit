#!/usr/bin/env python3
"""Generate an SVG illustration: an octopus chef at a night ramen booth (yatai).

Run:  python3 src/make_octopus_ramen.py
Out:  output/octopus-ramen.svg
Pure standard library; the SVG is fully self-contained.
"""
import math
import random
from pathlib import Path

W, H = 1200, 900
OUT = Path(__file__).resolve().parent.parent / "output" / "octopus-ramen.svg"

P = []  # svg fragments, back-to-front


def add(s):
    P.append(s)


# ---------------------------------------------------------------- helpers
def steam(x, y, s=1.0, op=0.75, w=6):
    """One S-curve steam wisp rising from (x, y)."""
    d = (f"M {x} {y} C {x-14*s} {y-22*s}, {x+14*s} {y-38*s}, {x} {y-58*s} "
         f"C {x-12*s} {y-76*s}, {x+10*s} {y-86*s}, {x+2*s} {y-104*s}")
    return (f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="{w}" '
            f'stroke-linecap="round" opacity="{op}"/>')


def tentacle(d, suckers, width=36, color="#F26B7E"):
    """A stroked tentacle path plus pale sucker dots along it."""
    # darker underlay gives the arm an outline so it reads against the head
    out = [f'<path d="{d}" fill="none" stroke="#C23D57" stroke-width="{width+9}" '
           f'stroke-linecap="round" stroke-linejoin="round"/>',
           f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
           f'stroke-linecap="round" stroke-linejoin="round"/>']
    # soft top highlight, same path, thinner and lighter, slightly offset up
    out.append(f'<path d="{d}" fill="none" stroke="#FF93A2" stroke-width="{width*0.42:.0f}" '
               f'stroke-linecap="round" opacity="0.55" transform="translate(0 -7)"/>')
    for (sx, sy, r) in suckers:
        out.append(f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="#FFE0E4" opacity="0.95"/>')
        out.append(f'<circle cx="{sx}" cy="{sy}" r="{r*0.45:.1f}" fill="#F7A8B4" opacity="0.9"/>')
    return "".join(out)


def ramen_bowl(cx, cy, s=1.0, broth="#EFA03E"):
    """A front-view ramen bowl centred at rim (cx, cy)."""
    w, h = 150 * s, 62 * s
    g = [f'<g>']
    # shadow
    g.append(f'<ellipse cx="{cx}" cy="{cy+h+10*s}" rx="{w*0.52:.0f}" ry="{9*s:.0f}" fill="#3A2417" opacity="0.22"/>')
    # bowl body
    g.append(f'<path d="M {cx-w/2} {cy} A {w/2} {h} 0 0 0 {cx+w/2} {cy} Z" fill="#FFF6E8"/>')
    g.append(f'<path d="M {cx-w/2} {cy} A {w/2} {h} 0 0 0 {cx+w/2} {cy} Z" fill="none" stroke="#24406E" stroke-width="{3*s}"/>')
    # blue band + spiral motif at bowl centre
    g.append(f'<clipPath id="bc{cx:.0f}"><path d="M {cx-w/2} {cy} A {w/2} {h} 0 0 0 {cx+w/2} {cy} Z"/></clipPath>')
    g.append(f'<g clip-path="url(#bc{cx:.0f})"><rect x="{cx-w/2}" y="{cy+22*s}" width="{w}" height="{10*s}" fill="#24406E"/>'
             f'<circle cx="{cx}" cy="{cy+46*s}" r="{11*s}" fill="none" stroke="#E34A4A" stroke-width="{3*s}"/>'
             f'<path d="M {cx} {cy+46*s} m 0 {-6*s} a {6*s} {6*s} 0 1 1 {-6*s} {6*s} a {3.5*s} {3.5*s} 0 1 0 {3.5*s} {-3.5*s}" '
             f'fill="none" stroke="#E34A4A" stroke-width="{2.2*s}"/></g>')
    # foot
    g.append(f'<rect x="{cx-26*s}" y="{cy+h-2*s}" width="{52*s}" height="{10*s}" rx="{4*s}" fill="#24406E"/>')
    # rim + broth
    g.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{w/2}" ry="{15*s}" fill="#FFF6E8" stroke="#24406E" stroke-width="{3*s}"/>')
    g.append(f'<ellipse cx="{cx}" cy="{cy+1*s}" rx="{w/2-8*s}" ry="{11.5*s}" fill="{broth}"/>')
    # toppings: nori, chashu, narutomaki, half egg, scallions
    g.append(f'<rect x="{cx-58*s}" y="{cy-26*s}" width="{30*s}" height="{26*s}" rx="{3*s}" fill="#24382B" transform="rotate(-8 {cx-43*s} {cy-13*s})"/>')
    g.append(f'<ellipse cx="{cx+34*s}" cy="{cy-4*s}" rx="{24*s}" ry="{9*s}" fill="#C97B5A"/>')
    g.append(f'<ellipse cx="{cx+34*s}" cy="{cy-5*s}" rx="{16*s}" ry="{5.5*s}" fill="#E0A183"/>')
    g.append(f'<circle cx="{cx-22*s}" cy="{cy-5*s}" r="{11*s}" fill="#FFFDF6"/>')
    g.append(f'<path d="M {cx-22*s} {cy-5*s} m 0 {-7*s} a {7*s} {7*s} 0 1 1 {-7*s} {7*s} a {4*s} {4*s} 0 1 0 {4*s} {-4*s}" fill="none" stroke="#FF7FA5" stroke-width="{2.4*s}"/>')
    g.append(f'<ellipse cx="{cx+2*s}" cy="{cy-6*s}" rx="{13*s}" ry="{8*s}" fill="#FFFDF6"/>')
    g.append(f'<ellipse cx="{cx+2*s}" cy="{cy-6*s}" rx="{7*s}" ry="{4.6*s}" fill="#FFC93C"/>')
    for dx, dy in [(-38, -2), (-8, -9), (16, -2), (48, -7), (26, -10)]:
        g.append(f'<circle cx="{cx+dx*s}" cy="{cy+dy*s}" r="{2.6*s}" fill="#5FBF6A"/>')
    g.append('</g>')
    return "".join(g)


def lantern(cx, cy, label, s=1.0, body="#FFE9B8", ink="#D93A3A"):
    """Paper chochin lantern with vertical label."""
    g = [f'<circle cx="{cx}" cy="{cy}" r="{86*s}" fill="url(#glow)"/>']
    g.append(f'<line x1="{cx}" y1="{cy-96*s}" x2="{cx}" y2="{cy-52*s}" stroke="#2A3444" stroke-width="{4*s}"/>')
    g.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{47*s}" ry="{56*s}" fill="{body}"/>')
    for t in (-0.62, -0.31, 0.0, 0.31, 0.62):
        wid = 47 * s * math.sqrt(max(0.05, 1 - t * t))
        g.append(f'<path d="M {cx-wid} {cy+t*56*s} Q {cx} {cy+t*56*s+9*s} {cx+wid} {cy+t*56*s}" '
                 f'fill="none" stroke="#E5B96E" stroke-width="{2*s}" opacity="0.8"/>')
    g.append(f'<rect x="{cx-15*s}" y="{cy-63*s}" width="{30*s}" height="{11*s}" rx="{3*s}" fill="#2A3444"/>')
    g.append(f'<rect x="{cx-11*s}" y="{cy+52*s}" width="{22*s}" height="{10*s}" rx="{3*s}" fill="#2A3444"/>')
    g.append(f'<line x1="{cx}" y1="{cy+62*s}" x2="{cx}" y2="{cy+78*s}" stroke="{ink}" stroke-width="{3*s}"/>')
    chars = list(label)
    for i, ch in enumerate(chars):
        yy = cy + (i - (len(chars) - 1) / 2) * 30 * s + 10 * s
        g.append(f'<text x="{cx}" y="{yy:.0f}" font-size="{26*s}" text-anchor="middle" '
                 f'fill="{ink}" font-weight="700" font-family="\'Hiragino Sans\',\'Noto Sans JP\',sans-serif">{ch}</text>')
    return "".join(g)


def stool(cx, top=742):
    return (f'<ellipse cx="{cx}" cy="{top+86}" rx="58" ry="9" fill="#171E33" opacity="0.35"/>'
            f'<rect x="{cx-46}" y="{top+14}" width="12" height="70" rx="5" fill="#5E3A22"/>'
            f'<rect x="{cx+34}" y="{top+14}" width="12" height="70" rx="5" fill="#5E3A22"/>'
            f'<rect x="{cx-46}" y="{top+52}" width="92" height="9" rx="4" fill="#4A2E1B"/>'
            f'<ellipse cx="{cx}" cy="{top+8}" rx="60" ry="15" fill="#B33A3A"/>'
            f'<ellipse cx="{cx}" cy="{top}" rx="60" ry="15" fill="#D94A4A"/>'
            f'<ellipse cx="{cx-14}" cy="{top-3}" rx="30" ry="7" fill="#E87070" opacity="0.8"/>')


# ---------------------------------------------------------------- document
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">')
add('<title>Octopus chef at a ramen booth</title>')
add('<desc>A cheerful octopus chef wearing a toque, cooking ramen with all eight arms '
    'at a lantern-lit night-time yatai booth.</desc>')
add('''<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#141B36"/><stop offset="0.6" stop-color="#26315C"/><stop offset="1" stop-color="#39477A"/>
</linearGradient>
<radialGradient id="boothGlow" cx="0.5" cy="0.42" r="0.75">
 <stop offset="0" stop-color="#FFE3A1"/><stop offset="0.55" stop-color="#FFC87A"/><stop offset="1" stop-color="#E8935A"/>
</radialGradient>
<radialGradient id="glow"><stop offset="0" stop-color="#FFD97A" stop-opacity="0.55"/><stop offset="1" stop-color="#FFD97A" stop-opacity="0"/></radialGradient>
<linearGradient id="octo" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#FF8F9C"/><stop offset="0.55" stop-color="#F6677C"/><stop offset="1" stop-color="#E85268"/>
</linearGradient>
<linearGradient id="metal" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#C3CEDA"/><stop offset="0.5" stop-color="#8A97A5"/><stop offset="1" stop-color="#66727F"/>
</linearGradient>
<linearGradient id="woodTop" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#E8BC82"/><stop offset="1" stop-color="#C98D54"/>
</linearGradient>
</defs>''')

# ---- night sky, stars, moon ----
add(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
rng = random.Random(20261015)
stars = []
for _ in range(70):
    x, y = rng.uniform(10, W - 10), rng.uniform(8, 330)
    r = rng.uniform(1, 2.6)
    stars.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#FFFFFF" opacity="{rng.uniform(0.35,0.95):.2f}"/>')
add("".join(stars))
add('<circle cx="1052" cy="92" r="35" fill="#FFE9A8"/>'
    '<circle cx="1071" cy="83" r="30" fill="#171F3C"/>')

# distant rooftops
add('<path d="M0 300 L120 258 L250 300 L250 900 L0 900 Z" fill="#1D2749"/>'
    '<path d="M950 306 L1075 262 L1200 306 L1200 900 L950 900 Z" fill="#1D2749"/>')

# string of festoon bulbs across the top
wire = '<path d="M -10 118 Q 300 196 600 150 Q 910 106 1210 168" fill="none" stroke="#0F152B" stroke-width="4"/>'
bulbs = [wire]
for t in [i / 13 for i in range(1, 13)]:
    # point on the two quadratic halves (approx)
    if t <= 0.5:
        u = t * 2
        x = (1 - u) ** 2 * -10 + 2 * u * (1 - u) * 300 + u * u * 600
        y = (1 - u) ** 2 * 118 + 2 * u * (1 - u) * 196 + u * u * 150
    else:
        u = (t - 0.5) * 2
        x = (1 - u) ** 2 * 600 + 2 * u * (1 - u) * 910 + u * u * 1210
        y = (1 - u) ** 2 * 150 + 2 * u * (1 - u) * 106 + u * u * 168
    col = ["#FFD97A", "#FF9E7A", "#8FE3DC", "#FFB3C2"][int(t * 13) % 4]
    bulbs.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x:.0f}" y2="{y+10:.0f}" stroke="#0F152B" stroke-width="3"/>'
                 f'<circle cx="{x:.0f}" cy="{y+19:.0f}" r="9" fill="{col}"/>'
                 f'<circle cx="{x:.0f}" cy="{y+19:.0f}" r="17" fill="{col}" opacity="0.22"/>')
add("".join(bulbs))

# ---- ground / street ----
add('<rect x="0" y="772" width="1200" height="128" fill="#232C4E"/>'
    '<ellipse cx="600" cy="806" rx="560" ry="52" fill="#FFC87A" opacity="0.16"/>')
cobbles = []
for row, yy in enumerate((796, 828, 860)):
    for i in range(9):
        xx = 60 + i * 135 + (55 if row % 2 else 0)
        cobbles.append(f'<ellipse cx="{xx}" cy="{yy}" rx="52" ry="9" fill="none" stroke="#2C3760" stroke-width="2"/>')
add("".join(cobbles))

# ---- booth: posts, warm interior, shelves ----
add('<rect x="196" y="282" width="808" height="356" fill="url(#boothGlow)"/>')
# back shelves with jars & bottles (visible either side of the chef)
shelf = []
for sy in (398, 468):
    shelf.append(f'<rect x="214" y="{sy}" width="772" height="10" rx="4" fill="#A9713F"/>')
    shelf.append(f'<rect x="214" y="{sy+8}" width="772" height="5" fill="#7A4A2B" opacity="0.7"/>')
jars = [(246, 430, 22, 38, "#E8A13A"), (338, 426, 24, 42, "#3E7CB1"), (368, 434, 18, 34, "#E34A4A"),
        (812, 426, 24, 42, "#7FB069"), (842, 434, 18, 34, "#6B5CA5"), (900, 430, 22, 38, "#D96C4A")]
for (x, y, w, h, c) in jars:
    shelf.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{c}"/>'
                 f'<rect x="{x+3}" y="{y-6}" width="{w-6}" height="8" rx="3" fill="#5E3A22"/>'
                 f'<rect x="{x+4}" y="{y+8}" width="{w-8}" height="{h-16}" rx="3" fill="#FFFFFF" opacity="0.28"/>')
add("".join(shelf))

add('<rect x="168" y="238" width="34" height="472" rx="8" fill="#6B4226"/>'
    '<rect x="998" y="238" width="34" height="472" rx="8" fill="#6B4226"/>'
    '<rect x="176" y="238" width="7" height="472" fill="#8A5A34"/>'
    '<rect x="1006" y="238" width="7" height="472" fill="#8A5A34"/>')

# ---- noren curtain (behind the chef) ----
noren = ['<rect x="190" y="276" width="820" height="12" rx="6" fill="#3A2417"/>']
for i in range(5):
    x = 196 + i * 163
    wave = 10 if i % 2 == 0 else 2
    noren.append(f'<path d="M {x} 288 L {x+156} 288 L {x+156} {392+wave} Q {x+78} {404+wave} {x} {392+wave} Z" fill="#24406E"/>')
    noren.append(f'<circle cx="{x+78}" cy="336" r="21" fill="none" stroke="#FFF3D6" stroke-width="3.5" opacity="0.92"/>')
    noren.append(f'<path d="M {x+58} 336 Q {x+68} 326 {x+78} 336 Q {x+88} 346 {x+98} 336" fill="none" stroke="#FFF3D6" stroke-width="3" opacity="0.92"/>')
add("".join(noren))

# ---- roof + signboard ----
add('<polygon points="128,264 1072,264 956,142 244,142" fill="#3D4A5C"/>')
tile_rows = []
for r in range(4):
    yy = 168 + r * 26
    inset = (yy - 142) * (116 / 122)
    tile_rows.append(f'<line x1="{244-inset:.0f}" y1="{yy}" x2="{956+inset:.0f}" y2="{yy}" stroke="#55687F" stroke-width="5"/>')
for c in range(11):
    x_top = 300 + c * 60
    tile_rows.append(f'<line x1="{x_top}" y1="146" x2="{x_top-52}" y2="262" stroke="#2E3A4C" stroke-width="4" opacity="0.65"/>')
add("".join(tile_rows))
add('<rect x="110" y="258" width="980" height="24" rx="8" fill="#241A12"/>'
    '<rect x="110" y="258" width="980" height="7" rx="3" fill="#4A3626"/>')
# main signboard on the roof face
add('<rect x="382" y="162" width="436" height="84" rx="12" fill="#3A2417"/>'
    '<rect x="390" y="170" width="420" height="68" rx="9" fill="#FFEFC2"/>'
    '<circle cx="438" cy="204" r="23" fill="#F6677C"/>'
    '<circle cx="430" cy="200" r="3.4" fill="#2B1B22"/><circle cx="446" cy="200" r="3.4" fill="#2B1B22"/>'
    '<path d="M 430 210 Q 438 216 446 210" fill="none" stroke="#2B1B22" stroke-width="2.6" stroke-linecap="round"/>'
    '<path d="M 420 222 q 4 8 9 2 M 432 225 q 4 8 9 2 M 444 224 q 5 7 10 1" fill="none" stroke="#F6677C" stroke-width="4.5" stroke-linecap="round"/>'
    '<rect x="424" y="176" width="28" height="13" rx="6" fill="#FFFDF6" stroke="#D8D0BC" stroke-width="1.6"/>'
    '<text x="618" y="203" font-size="36" font-weight="800" letter-spacing="3" text-anchor="middle" fill="#7A2E1D" font-family="Georgia,\'Times New Roman\',serif">TAKO RAMEN</text>'
    '<text x="618" y="229" font-size="17" font-weight="700" letter-spacing="6" text-anchor="middle" fill="#24406E" font-family="\'Hiragino Sans\',\'Noto Sans JP\',sans-serif">タコラーメン</text>'
    '<rect x="776" y="204" width="25" height="25" rx="5" fill="#D93A3A"/>'
    '<text x="788" y="223" font-size="16" text-anchor="middle" fill="#FFFFFF" font-weight="700" font-family="\'Hiragino Sans\',\'Noto Sans JP\',sans-serif">旨</text>')

# ================================================================ THE CHEF
# -- back tentacles: 1 wave (L), 2 ladle (L), 7 pot-lid (R), 8 beckon (R) --
add(tentacle("M 478 612 C 392 592, 302 546, 264 480 C 252 458, 254 442, 270 436",
             [(306, 534, 6), (340, 562, 6.5), (378, 584, 7)]))                       # 1 wave
add(tentacle("M 470 622 C 398 594, 356 548, 339 480",
             [(350, 518, 6), (372, 560, 6.5), (402, 594, 7)]))                       # 2 ladle
add(tentacle("M 736 616 C 810 588, 886 540, 910 452",
             [(884, 510, 6), (840, 562, 6.5), (796, 594, 7)]))                       # 7 lid
add(tentacle("M 726 606 C 816 586, 906 536, 946 470 C 958 452, 956 438, 940 431",
             [(902, 520, 6), (868, 550, 6.5), (828, 576, 7)]))                       # 8 beckon

# -- head / mantle --
add('<path d="M 455 632 C 452 500, 490 366, 600 356 C 710 366, 748 500, 745 632 Z" fill="url(#octo)"/>'
    '<ellipse cx="528" cy="432" rx="46" ry="70" fill="#FFFFFF" opacity="0.18" transform="rotate(-12 528 432)"/>'
    '<circle cx="496" cy="462" r="9" fill="#FFB3BC" opacity="0.8"/>'
    '<circle cx="508" cy="498" r="6.5" fill="#FFB3BC" opacity="0.75"/>'
    '<circle cx="706" cy="462" r="9" fill="#FFB3BC" opacity="0.8"/>'
    '<circle cx="694" cy="498" r="6.5" fill="#FFB3BC" opacity="0.75"/>'
    '<circle cx="676" cy="416" r="7.5" fill="#FFB3BC" opacity="0.7"/>'
    '<circle cx="526" cy="416" r="7.5" fill="#FFB3BC" opacity="0.7"/>')
# face: brows, eyes, cheeks, smiling open mouth
add('<path d="M 512 452 Q 538 440 564 452" fill="none" stroke="#B23A50" stroke-width="6" stroke-linecap="round"/>'
    '<path d="M 636 452 Q 662 440 688 452" fill="none" stroke="#B23A50" stroke-width="6" stroke-linecap="round"/>'
    '<ellipse cx="538" cy="486" rx="17" ry="23" fill="#2B1B22"/>'
    '<ellipse cx="662" cy="486" rx="17" ry="23" fill="#2B1B22"/>'
    '<circle cx="532" cy="478" r="6" fill="#FFFFFF"/><circle cx="656" cy="478" r="6" fill="#FFFFFF"/>'
    '<circle cx="546" cy="496" r="3" fill="#FFFFFF" opacity="0.9"/><circle cx="670" cy="496" r="3" fill="#FFFFFF" opacity="0.9"/>'
    '<ellipse cx="492" cy="528" rx="24" ry="13" fill="#FF9DAE" opacity="0.95"/>'
    '<ellipse cx="708" cy="528" rx="24" ry="13" fill="#FF9DAE" opacity="0.95"/>'
    '<path d="M 566 524 Q 600 556 634 524 Q 632 560 600 562 Q 568 560 566 524 Z" fill="#7A2233"/>'
    '<ellipse cx="600" cy="552" rx="17" ry="8" fill="#FF8FA3"/>')
# chef's toque, tilted
add('<g transform="rotate(-7 600 330)">'
    '<circle cx="543" cy="310" r="35" fill="#FFFDF6"/><circle cx="600" cy="295" r="42" fill="#FFFDF6"/>'
    '<circle cx="657" cy="310" r="35" fill="#FFFDF6"/><rect x="508" y="298" width="184" height="46" fill="#FFFDF6"/>'
    '<circle cx="570" cy="282" r="12" fill="#FFFFFF" opacity="0.9"/>'
    '<rect x="498" y="334" width="204" height="40" rx="14" fill="#FFFDF6" stroke="#E3DCC8" stroke-width="3"/>'
    '<line x1="548" y1="340" x2="548" y2="368" stroke="#E3DCC8" stroke-width="3"/>'
    '<line x1="600" y1="340" x2="600" y2="368" stroke="#E3DCC8" stroke-width="3"/>'
    '<line x1="652" y1="340" x2="652" y2="368" stroke="#E3DCC8" stroke-width="3"/>'
    '<path d="M 512 334 Q 600 346 688 334" fill="none" stroke="#E3DCC8" stroke-width="3"/></g>')
# teal neckerchief
add('<path d="M 518 576 Q 600 602 682 576 L 666 610 Q 600 624 534 610 Z" fill="#1FA8A0"/>'
    '<path d="M 579 592 L 600 620 L 622 592 Q 600 602 579 592 Z" fill="#178F88"/>'
    '<circle cx="600" cy="591" r="9" fill="#146B66"/>')

# -- front tentacles: 3 chopsticks, 4 steady bowl, 5 sprinkle, 6 egg --
add(tentacle("M 500 648 C 455 602, 452 550, 478 502",
             [(460, 562, 6), (464, 598, 6.5)]))                                      # 3 chopsticks
add(tentacle("M 498 652 C 452 640, 420 618, 402 592",
             [(438, 630, 6)]))                                                       # 4 steady bowl
add(tentacle("M 700 648 C 735 606, 740 560, 716 518",
             [(734, 572, 6), (726, 608, 6.5)]))                                      # 5 sprinkle
add(tentacle("M 725 648 C 770 622, 800 592, 798 548",
             [(792, 586, 6), (766, 618, 6.5)]))                                      # 6 egg

# -- pots on the stoves (either side of the chef) --
add('<rect x="210" y="612" width="150" height="20" rx="6" fill="#3A3A44"/>'          # left stove
    '<rect x="198" y="532" width="174" height="84" rx="16" fill="url(#metal)"/>'
    '<rect x="198" y="566" width="174" height="9" fill="#5E6B7A"/>'
    '<path d="M 198 552 q -22 10 0 24 M 372 552 q 22 10 0 24" fill="none" stroke="#5E6B7A" stroke-width="7"/>'
    '<ellipse cx="285" cy="534" rx="87" ry="15" fill="#D8E0E8"/>'
    '<ellipse cx="285" cy="535" rx="74" ry="11" fill="#EFA03E"/>'
    '<circle cx="252" cy="533" r="4" fill="#FFD97A"/><circle cx="306" cy="537" r="3.4" fill="#FFD97A"/>'
    '<circle cx="280" cy="531" r="2.8" fill="#FFD97A"/>')
add('<rect x="846" y="612" width="138" height="20" rx="6" fill="#3A3A44"/>'          # right stove
    '<rect x="838" y="544" width="154" height="72" rx="15" fill="url(#metal)"/>'
    '<rect x="838" y="574" width="154" height="8" fill="#5E6B7A"/>'
    '<ellipse cx="915" cy="546" rx="77" ry="13" fill="#D8E0E8"/>'
    '<ellipse cx="915" cy="547" rx="64" ry="9.5" fill="#F3C96B"/>'
    '<path d="M 872 546 q 10 -6 22 0 q 12 6 24 0 q 12 -6 22 0" fill="none" stroke="#FFE6A7" stroke-width="4" stroke-linecap="round"/>')

# -- tools at the tentacle tips --
# ladle (arm 2), dripping broth back into the pot
add('<line x1="338" y1="477" x2="294" y2="512" stroke="#5E6B7A" stroke-width="8" stroke-linecap="round"/>'
    '<path d="M 242 516 A 30 16 0 0 0 302 516 Z" fill="#75828F" stroke="#4E5A68" stroke-width="3"/>'
    '<ellipse cx="272" cy="517" rx="27" ry="6" fill="#EFA03E"/>'
    '<path d="M 272 530 q 5 8 0 12 q -5 -4 0 -12" fill="#EFA03E"/>')
# lifted lid (arm 7): a tall domed lid gripped by its knob, tilted open
add('<g transform="rotate(-14 912 492)">'
    '<path d="M 848 498 A 64 40 0 0 1 976 498 Z" fill="url(#metal)" stroke="#4E5A68" stroke-width="3"/>'
    '<ellipse cx="912" cy="498" rx="64" ry="9" fill="#66727F"/>'
    '<rect x="899" y="444" width="26" height="15" rx="7" fill="#3A3A44"/></g>')
# chopsticks + lifted noodles (arm 3)
add('<line x1="474" y1="498" x2="469" y2="548" stroke="#7A4A2B" stroke-width="5.5" stroke-linecap="round"/>'
    '<line x1="487" y1="500" x2="492" y2="546" stroke="#7A4A2B" stroke-width="5.5" stroke-linecap="round"/>'
    '<path d="M 458 544 Q 481 556 504 544" fill="none" stroke="#FFE6A7" stroke-width="7" stroke-linecap="round"/>')
noodles = []
for dx in (-20, -11, -3, 5, 13, 21):
    noodles.append(f'<path d="M {481+dx} 548 q {-7 if dx%2 else 7} 12 0 24 q {7 if dx%2 else -7} 12 {-2} 26" '
                   f'fill="none" stroke="#FFE6A7" stroke-width="4.5" stroke-linecap="round"/>')
add("".join(noodles))
# falling scallions (arm 5) toward the right-hand bowl
flecks = [(718, 540), (706, 556), (726, 560), (714, 574), (732, 578), (708, 588)]
add("".join(f'<rect x="{x}" y="{y}" width="9" height="4.5" rx="2" fill="#4FAE5C" transform="rotate({(x*7)%50-25} {x} {y})"/>' for x, y in flecks)
    + '<circle cx="715" cy="522" r="7" fill="#4FAE5C"/>')
# halved egg being placed (arm 6)
add('<ellipse cx="792" cy="572" rx="21" ry="15" fill="#FFFDF6" stroke="#EAD9B0" stroke-width="2"/>'
    '<circle cx="792" cy="572" r="8.5" fill="#FFB92E"/><circle cx="789" cy="569" r="3" fill="#FFD97A"/>')

# ---- counter (covers the chef's lower body: he stands behind it) ----
add('<rect x="150" y="646" width="900" height="128" fill="#9A683C"/>')
planks = []
for i in range(13):
    x = 150 + i * 75
    planks.append(f'<line x1="{x}" y1="648" x2="{x}" y2="772" stroke="#7A4A2B" stroke-width="3" opacity="0.75"/>')
planks.append('<line x1="150" y1="710" x2="1050" y2="710" stroke="#7A4A2B" stroke-width="3" opacity="0.55"/>')
add("".join(planks))
add('<rect x="172" y="744" width="856" height="11" rx="5" fill="#4A3626"/>'          # foot rail
    '<rect x="130" y="610" width="940" height="42" rx="10" fill="url(#woodTop)"/>'
    '<rect x="130" y="610" width="940" height="9" rx="4" fill="#F2D3A0"/>'
    '<ellipse cx="600" cy="626" rx="380" ry="13" fill="#FFE3A1" opacity="0.35"/>')

# menu plaques hanging on the counter front
menu = [("醤", "¥800", 205), ("味", "¥850", 445), ("塩", "¥800", 700), ("辛", "¥900", 952)]
plaque = []
for ch, price, x in menu:
    plaque.append(f'<g><line x1="{x+12}" y1="652" x2="{x+12}" y2="682" stroke="#3A2417" stroke-width="3"/>'
                  f'<line x1="{x+56}" y1="652" x2="{x+56}" y2="682" stroke="#3A2417" stroke-width="3"/>'
                  f'<rect x="{x}" y="682" width="68" height="80" rx="7" fill="#FFEFC2" stroke="#7A4A2B" stroke-width="3"/>'
                  f'<text x="{x+34}" y="722" font-size="32" text-anchor="middle" fill="#7A2E1D" font-weight="700" font-family="\'Hiragino Sans\',\'Noto Sans JP\',sans-serif">{ch}</text>'
                  f'<text x="{x+34}" y="748" font-size="16" text-anchor="middle" fill="#24406E" font-weight="700" font-family="Georgia,serif">{price}</text></g>')
add("".join(plaque))

# ---- the two bowls being served, on the counter ----
add(ramen_bowl(475, 600, 1.05))
add(ramen_bowl(725, 600, 1.05))
# condiments + tea between the bowls; chopstick holder on the left
add('<rect x="584" y="612" width="17" height="34" rx="5" fill="#3A2A20"/>'
    '<rect x="587" y="602" width="11" height="12" rx="3" fill="#D93A3A"/>'
    '<rect x="586" y="622" width="13" height="14" rx="2" fill="#FFEFC2"/>'
    '<path d="M 612 618 L 644 618 L 639 646 L 617 646 Z" fill="#FFF6E8" stroke="#24406E" stroke-width="2.5"/>'
    '<ellipse cx="628" cy="619" rx="15" ry="4" fill="#C98D54"/>'
    '<rect x="176" y="606" width="34" height="42" rx="6" fill="#24406E"/>'
    '<line x1="186" y1="608" x2="178" y2="576" stroke="#7A4A2B" stroke-width="4" stroke-linecap="round"/>'
    '<line x1="196" y1="608" x2="196" y2="574" stroke="#7A4A2B" stroke-width="4" stroke-linecap="round"/>'
    '<line x1="204" y1="608" x2="212" y2="578" stroke="#7A4A2B" stroke-width="4" stroke-linecap="round"/>'
    '<rect x="960" y="618" width="62" height="28" rx="6" fill="#A9713F"/>'
    '<ellipse cx="976" cy="614" rx="11" ry="9" fill="#FFF3D6" stroke="#E3C896" stroke-width="1.8"/>'
    '<ellipse cx="999" cy="614" rx="11" ry="9" fill="#FFF3D6" stroke="#E3C896" stroke-width="1.8"/>'
    '<ellipse cx="988" cy="605" rx="11" ry="9" fill="#FFF3D6" stroke="#E3C896" stroke-width="1.8"/>')

# ---- foreground lanterns hanging from the eave ----
add(lantern(232, 376, "ラーメン", 0.92))
add(lantern(968, 376, "たこ", 0.92, body="#F6C6C6"))

# OPEN sign on the left post
add('<g transform="rotate(-6 124 486)"><rect x="86" y="458" width="78" height="56" rx="8" fill="#FFEFC2" stroke="#7A4A2B" stroke-width="3.5"/>'
    '<text x="125" y="484" font-size="19" font-weight="800" text-anchor="middle" fill="#D93A3A" font-family="Georgia,serif">OPEN</text>'
    '<text x="125" y="504" font-size="13" text-anchor="middle" fill="#24406E" font-weight="700" font-family="\'Hiragino Sans\',\'Noto Sans JP\',sans-serif">営業中</text></g>')

# ---- stools + a hopeful cat customer ----
add(stool(330) + stool(600) + stool(870))
add('<ellipse cx="1012" cy="858" rx="44" ry="8" fill="#171E33" opacity="0.4"/>'
    '<path d="M 1036 846 Q 1080 838 1074 806" fill="none" stroke="#4A445E" stroke-width="11" stroke-linecap="round"/>'
    '<ellipse cx="1012" cy="830" rx="31" ry="27" fill="#4A445E"/>'
    '<ellipse cx="1012" cy="838" rx="16" ry="18" fill="#EDE6DA"/>'
    '<polygon points="986,782 992,758 1006,776" fill="#4A445E"/><polygon points="1038,782 1032,758 1018,776" fill="#4A445E"/>'
    '<polygon points="991,778 995,766 1002,775" fill="#FFB3C2"/><polygon points="1033,778 1029,766 1022,775" fill="#FFB3C2"/>'
    '<circle cx="1012" cy="790" r="24" fill="#4A445E"/>'
    '<ellipse cx="1012" cy="799" rx="10" ry="8" fill="#EDE6DA"/>'
    '<circle cx="1003" cy="787" r="3.4" fill="#FFC93C"/><circle cx="1021" cy="787" r="3.4" fill="#FFC93C"/>'
    '<path d="M 1009 796 L 1015 796 L 1012 800 Z" fill="#FF8FA3"/>'
    '<path d="M 990 810 Q 1012 820 1034 810" fill="none" stroke="#D93A3A" stroke-width="5"/>'
    '<circle cx="1012" cy="819" r="5" fill="#FFC93C"/>')

# ---- steam, drifting in front of everything ----
add(steam(238, 526, 0.95, 0.8) + steam(332, 528, 0.75, 0.6)
    + steam(890, 540, 0.85, 0.75) + steam(940, 540, 0.65, 0.55)
    + steam(438, 592, 0.55, 0.55, 5) + steam(762, 592, 0.55, 0.55, 5))

add('</svg>')

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(P), encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size/1024:.1f} KB)")
