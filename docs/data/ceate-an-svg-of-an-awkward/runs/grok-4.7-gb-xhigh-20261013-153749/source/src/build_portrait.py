#!/usr/bin/env python3
"""Awkward robot family portrait.

Five robots and a pet in a studio cyclorama. Relationships are pose and
spacing only: nobody was built as a set, and nobody quite held still.
"""

from pathlib import Path
import math
import xml.etree.ElementTree as ET

INK = "#1b2126"
OUT = Path(__file__).resolve().parent.parent / "output" / "awkward-family-portrait.svg"

# Floor line where soles and chair feet land.
FLOOR = 878


def limb(x1, y1, x2, y2, fill, width=26):
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" '
        f'stroke-width="{width + 7}" stroke-linecap="round"/>'
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{fill}" '
        f'stroke-width="{width}" stroke-linecap="round"/>'
    )


def tube(d, fill, width=16):
    return (
        f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{width + 7}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{width}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
    )


def joint(cx, cy, r, outer, inner="#e4e8ec"):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r + 2.2}" fill="{INK}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{outer}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r * 0.4:.1f}" fill="{inner}"/>'
        f'<circle cx="{cx - r * 0.18:.1f}" cy="{cy - r * 0.22:.1f}" '
        f'r="{r * 0.13:.1f}" fill="#fff" opacity="0.85"/>'
    )


def rivet(x, y, dark="#5a3c18", light="#f6e2b8"):
    return (
        f'<circle cx="{x}" cy="{y}" r="3.7" fill="{dark}"/>'
        f'<circle cx="{x - 0.9:.1f}" cy="{y - 1:.1f}" r="1.35" fill="{light}"/>'
    )


def rivets(points, dark="#5a3c18", light="#f6e2b8"):
    return "".join(rivet(x, y, dark, light) for x, y in points)


def spec(cx, cy, rx, ry, op=0.5, rot=-28):
    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#fff8ee" '
        f'opacity="{op}" transform="rotate({rot} {cx} {cy})"/>'
    )


def lamp(cx, cy, r, core, ring="#2a3036"):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r + 4}" fill="{INK}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r + 1.6}" fill="{ring}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{core}" filter="url(#glow)"/>'
        f'<circle cx="{cx - r * 0.28:.1f}" cy="{cy - r * 0.32:.1f}" '
        f'r="{max(1.4, r * 0.28):.1f}" fill="#fff" opacity="0.75"/>'
    )


def eye(cx, cy, r, iris, dx=0, dy=0, cloudy=False, lid=None, clip=None):
    """Round glass eye. dx/dy shift the pupil. Catchlight stays upper-left."""
    sclera = "#aebabc" if cloudy else "#f5fafb"
    iris_r = r * (0.62 if cloudy else 0.5)
    pupil_r = r * (0.28 if cloudy else 0.24)
    parts = [
        f'<circle cx="{cx}" cy="{cy}" r="{r + 2}" fill="{INK}"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{sclera}"/>',
        f'<circle cx="{cx + dx}" cy="{cy + dy}" r="{iris_r:.1f}" fill="{iris}"/>',
        f'<circle cx="{cx + dx}" cy="{cy + dy}" r="{pupil_r:.1f}" fill="#12161c"/>',
        f'<circle cx="{cx - r * 0.32:.1f}" cy="{cy - r * 0.36:.1f}" '
        f'r="{r * 0.16:.1f}" fill="#fff"/>',
        f'<circle cx="{cx + r * 0.18:.1f}" cy="{cy - r * 0.46:.1f}" '
        f'r="{r * 0.07:.1f}" fill="#fff" opacity="0.85"/>',
    ]
    if lid and clip:
        # Lid grows down from the top of the eye. Resting height is 0.
        parts.append(
            f'<g clip-path="url(#{clip})">'
            f'<rect x="{cx - r - 1}" y="{cy - r - 1}" width="{2 * r + 2}" height="0" '
            f'fill="{lid}">'
            f'<animate attributeName="height" '
            f'values="0;0;{2 * r + 2};0;0" '
            f'keyTimes="0;0.9;0.935;0.97;1" dur="7.5s" '
            f'repeatCount="indefinite"/>'
            f'</rect></g>'
        )
    return "".join(parts)


def clip_circle(cid, cx, cy, r):
    return (
        f'<clipPath id="{cid}">'
        f'<circle cx="{cx}" cy="{cy}" r="{r}"/>'
        f'</clipPath>'
    )


def hex_points(cx, cy, r, start=30):
    pts = []
    for i in range(6):
        a = math.radians(start + 60 * i)
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return " ".join(pts)


def shadow(cx, cy, rx, ry, op=0.38):
    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
        f'fill="#1a1612" opacity="{op}" filter="url(#blur)"/>'
    )


def defs():
    clips = "".join(
        [
            clip_circle("clipGeye", 236, 404, 11),
            clip_circle("clipMeyeL", 598, 492, 16),
            clip_circle("clipMeyeR", 666, 496, 16),
            clip_circle("clipTeye", 1368, 318, 13),
        ]
    )
    return f'''
<defs>
  <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#b7c3cb"/>
    <stop offset="0.42" stop-color="#8b99a3"/>
    <stop offset="1" stop-color="#73818b"/>
  </linearGradient>
  <linearGradient id="floorG" x1="0" y1="0" x2="0.2" y2="1">
    <stop offset="0" stop-color="#8d9aa3"/>
    <stop offset="1" stop-color="#4e5a63"/>
  </linearGradient>
  <radialGradient id="pool" cx="40%" cy="36%" r="52%">
    <stop offset="0" stop-color="#f4eadc" stop-opacity="0.55"/>
    <stop offset="0.45" stop-color="#d5e0e6" stop-opacity="0.18"/>
    <stop offset="1" stop-color="#d5e0e6" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="vig" cx="50%" cy="44%" r="72%">
    <stop offset="52%" stop-color="#1a2128" stop-opacity="0"/>
    <stop offset="100%" stop-color="#12181e" stop-opacity="0.62"/>
  </radialGradient>
  <radialGradient id="warm" cx="28%" cy="18%" r="70%">
    <stop offset="0" stop-color="#ffd9a8" stop-opacity="0.45"/>
    <stop offset="55%" stop-color="#ffd9a8" stop-opacity="0"/>
    <stop offset="100%" stop-color="#8aa0b4" stop-opacity="0.25"/>
  </radialGradient>
  <radialGradient id="silver" cx="32%" cy="30%" r="70%">
    <stop offset="0" stop-color="#ffffff"/>
    <stop offset="38%" stop-color="#d5dce2"/>
    <stop offset="100%" stop-color="#7e888f"/>
  </radialGradient>
  <linearGradient id="brass" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#f6e2b4"/>
    <stop offset="0.38" stop-color="#d4a44c"/>
    <stop offset="0.72" stop-color="#a67532"/>
    <stop offset="1" stop-color="#6e4c20"/>
  </linearGradient>
  <linearGradient id="brassNew" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#fff1cc"/>
    <stop offset="0.5" stop-color="#e8c56a"/>
    <stop offset="1" stop-color="#b8883a"/>
  </linearGradient>
  <linearGradient id="slate" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#7d8b96"/>
    <stop offset="0.35" stop-color="#4a5660"/>
    <stop offset="1" stop-color="#2a3238"/>
  </linearGradient>
  <linearGradient id="slateDark" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3e4952"/>
    <stop offset="1" stop-color="#232a30"/>
  </linearGradient>
  <linearGradient id="cream" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#fffaf4"/>
    <stop offset="0.45" stop-color="#f3e4d4"/>
    <stop offset="1" stop-color="#e2cbb8"/>
  </linearGradient>
  <linearGradient id="apron" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#f8e4dc"/>
    <stop offset="1" stop-color="#e7c8bc"/>
  </linearGradient>
  <linearGradient id="coral" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#f09088"/>
    <stop offset="1" stop-color="#c45450"/>
  </linearGradient>
  <linearGradient id="wood" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#c4845a"/>
    <stop offset="0.45" stop-color="#8d5434"/>
    <stop offset="1" stop-color="#5c321c"/>
  </linearGradient>
  <linearGradient id="woodDark" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#7a4630"/>
    <stop offset="1" stop-color="#3e2418"/>
  </linearGradient>
  <linearGradient id="hoodie" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#61789a"/>
    <stop offset="0.4" stop-color="#3d516c"/>
    <stop offset="1" stop-color="#283646"/>
  </linearGradient>
  <linearGradient id="kidBlue" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#8fd0f8"/>
    <stop offset="0.4" stop-color="#3d9ae0"/>
    <stop offset="1" stop-color="#2468a4"/>
  </linearGradient>
  <linearGradient id="kidYellow" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffe38a"/>
    <stop offset="0.5" stop-color="#f0c14e"/>
    <stop offset="1" stop-color="#d09a28"/>
  </linearGradient>
  <linearGradient id="kidYellowOld" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#f0d090"/>
    <stop offset="1" stop-color="#c48428"/>
  </linearGradient>
  <linearGradient id="teal" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#7ed9cc"/>
    <stop offset="0.45" stop-color="#2f9d90"/>
    <stop offset="1" stop-color="#1a655c"/>
  </linearGradient>
  <linearGradient id="caseA" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#a84868"/>
    <stop offset="1" stop-color="#6a2438"/>
  </linearGradient>
  <linearGradient id="caseB" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#8a9a58"/>
    <stop offset="1" stop-color="#4e5c30"/>
  </linearGradient>
  <filter id="blur" x="-60%" y="-80%" width="220%" height="260%">
    <feGaussianBlur stdDeviation="7"/>
  </filter>
  <filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur stdDeviation="3.2" result="b"/>
    <feMerge>
      <feMergeNode in="b"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2"
      stitchTiles="stitch" result="n"/>
    <feColorMatrix type="matrix" in="n" result="t"
      values="0 0 0 0 0.35
              0 0 0 0 0.3
              0 0 0 0 0.26
              0 0 0 0.55 0"/>
  </filter>
  {clips}
</defs>
'''


def backdrop():
    return f'''
<g id="studio">
  <rect width="1600" height="1000" fill="url(#wall)"/>
  <ellipse cx="820" cy="1120" rx="1380" ry="390" fill="url(#floorG)"/>
  <ellipse cx="740" cy="792" rx="820" ry="34" fill="#d5e0e6" opacity="0.22"/>
  <rect width="1600" height="1000" fill="url(#pool)"/>

  <!-- paper never quite got steamed on the left -->
  <path d="M150,0 C190,160 96,300 148,520 C186,690 120,790 156,980"
    stroke="#5a676f" stroke-width="26" fill="none" opacity="0.28" stroke-linecap="round"/>
  <path d="M168,0 C206,160 114,300 164,520 C200,690 136,790 170,940"
    stroke="#e4eef3" stroke-width="6" fill="none" opacity="0.28" stroke-linecap="round"/>
  <path d="M78,40 C110,220 60,420 96,640"
    stroke="#55636b" stroke-width="14" fill="none" opacity="0.22" stroke-linecap="round"/>
  <path d="M250,-10 C230,180 286,340 246,560 C220,700 250,760 236,860"
    stroke="#66747c" stroke-width="10" fill="none" opacity="0.18" stroke-linecap="round"/>

  <!-- backdrop seam falls in the gap the teenager left -->
  <path d="M1124,0 C1136,180 1104,380 1128,600 C1144,760 1112,830 1130,980"
    stroke="#46535b" stroke-width="4" fill="none" opacity="0.55" stroke-linecap="round"/>
  <path d="M1130,0 C1142,180 1110,380 1134,600"
    stroke="#d0dbe1" stroke-width="1.6" fill="none" opacity="0.4"/>

  <!-- reflector disc intruding from the corner -->
  <circle cx="-36" cy="-28" r="214" fill="url(#silver)" stroke="#5c666d" stroke-width="7"/>
  <circle cx="-70" cy="-70" r="70" fill="#fff" opacity="0.18"/>
  <rect x="92" y="78" width="34" height="16" rx="3" fill="#1b2126"/>
  <rect x="104" y="90" width="10" height="46" rx="2" fill="#2c343c"/>

  <!-- gaffer marks the photographer put down, and nobody used -->
  <g transform="rotate(18 992 846)">
    <rect x="970" y="838" width="52" height="14" rx="2" fill="#d2c09a" stroke="#6a5c40" stroke-width="1"/>
    <rect x="974" y="842" width="44" height="3" fill="#e6d7b4" opacity="0.7"/>
  </g>
  <g transform="rotate(-8 1248 852)">
    <rect x="1222" y="844" width="52" height="13" rx="2" fill="#d2c09a" stroke="#6a5c40" stroke-width="1"/>
    <rect x="1226" y="848" width="44" height="3" fill="#e6d7b4" opacity="0.65"/>
  </g>

  <ellipse cx="430" cy="860" rx="34" ry="6" fill="#2a3138" opacity="0.08"/>
  <ellipse cx="1480" cy="900" rx="50" ry="8" fill="#2a3138" opacity="0.1"/>
</g>
'''


def shadows():
    return f'''
<g id="shadows">
  {shadow(300, 884, 150, 16, 0.32)}
  {shadow(640, 886, 150, 15, 0.30)}
  {shadow(860, 884, 78, 13, 0.28)}
  {shadow(1040, 900, 70, 12, 0.26)}
  {shadow(1288, 886, 160, 16, 0.34)}
  {shadow(1060, 968, 180, 20, 0.40)}
</g>
'''


def grandpa():
    """Original model. He has been ready since he sat down.
    His good eye is on his son. His near hand never quite arrives.
    """
    riv = rivets(
        [(236, 548), (268, 548), (300, 548), (332, 548), (364, 548),
         (214, 612), (250, 600), (214, 636), (250, 636)]
    )
    return f'''
<g id="grandpa">
  <!-- chair he insisted on bringing -->
  <g id="chair">
    {tube("M168,500 Q300,430 432,512", "#8d5434", 20)}
    <rect x="160" y="490" width="18" height="388" rx="5" fill="url(#woodDark)" stroke="{INK}" stroke-width="2"/>
    <rect x="412" y="500" width="18" height="358" rx="5" fill="url(#wood)" stroke="{INK}" stroke-width="2"/>
    <rect x="230" y="530" width="14" height="130" rx="4" fill="url(#wood)" stroke="{INK}" stroke-width="1.6"/>
    <rect x="346" y="538" width="14" height="122" rx="4" fill="url(#woodDark)" stroke="{INK}" stroke-width="1.6"/>
    <!-- short leg on a coaster -->
    <ellipse cx="422" cy="872" rx="28" ry="9" fill="#e6d3ae" stroke="{INK}" stroke-width="1.5"/>
    <ellipse cx="422" cy="870" rx="18" ry="5" fill="#f3e6c8" opacity="0.6"/>
    <rect x="188" y="655" width="15" height="223" rx="4" fill="url(#woodDark)" stroke="{INK}" stroke-width="1.8"/>
    <rect x="392" y="658" width="15" height="210" rx="4" fill="url(#wood)" stroke="{INK}" stroke-width="1.8"/>
    <ellipse cx="300" cy="662" rx="128" ry="30" fill="url(#woodDark)" stroke="{INK}" stroke-width="2.2"/>
    <ellipse cx="286" cy="656" rx="78" ry="18" fill="#7a3040" stroke="{INK}" stroke-width="1.8"/>
    <circle cx="278" cy="656" r="5" fill="#5a2030" stroke="{INK}" stroke-width="1"/>
    <circle cx="276" cy="654.5" r="1.4" fill="#f0c0c0" opacity="0.7"/>
  </g>

  <!-- boots and legs, planted apart -->
  {limb(250, 700, 228, 820, "#8a6230", 30)}
  {limb(350, 705, 372, 825, "#a67532", 30)}
  {joint(250, 700, 12, "#a67532", "#f0d7a0")}
  {joint(228, 818, 10, "#6e4c20", "#d4a44c")}
  {joint(350, 705, 12, "#a67532", "#f0d7a0")}
  {joint(372, 822, 10, "#6e4c20", "#d4a44c")}
  <!-- mismatched boots -->
  <g id="bootL">
    <path d="M196,812 h62 v30 q0,18 -16,22 h-62 q-14,-4 -14,-20 v-14 q0,-18 14,-18 z"
      fill="#5c4030" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>
    <path d="M196,824 h70" stroke="#c4a070" stroke-width="4" stroke-linecap="round"/>
    <rect x="214" y="806" width="16" height="12" rx="2" fill="#d4a44c" stroke="{INK}" stroke-width="1.4"/>
  </g>
  <g id="bootR">
    <path d="M346,818 h70 v26 q0,20 -18,24 h-64 q-16,-2 -16,-20 v-12 q0,-18 16,-18 z"
      fill="#4a3428" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>
    <path d="M352,834 h62" stroke="#8a7058" stroke-width="5" stroke-linecap="round"/>
    <circle cx="400" cy="828" r="4" fill="#1b2126"/>
  </g>

  <!-- barrel torso -->
  <path d="M196,500
           C186,460 230,438 300,434
           C378,430 424,458 414,512
           L400,640
           C392,688 340,710 300,708
           C250,706 206,684 198,640 Z"
    fill="url(#brass)" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>
  {spec(250, 490, 36, 16, 0.42)}
  <!-- patina -->
  <ellipse cx="360" cy="470" rx="16" ry="9" fill="#6f8f78" opacity="0.35"/>
  <ellipse cx="230" cy="560" rx="12" ry="7" fill="#6f8f78" opacity="0.28"/>
  <!-- dent -->
  <path d="M372,520 q14,8 6,20" stroke="#6e4c20" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M370,518 q16,8 8,22" stroke="#f6e2b4" stroke-width="1.4" fill="none" opacity="0.7"/>
  <!-- chest band and lamp -->
  <path d="M210,542 H392" stroke="#6e4c20" stroke-width="8" stroke-linecap="round"/>
  <path d="M214,538 H388" stroke="#f0d29a" stroke-width="2" stroke-linecap="round" opacity="0.45"/>
  {riv}
  {lamp(300, 592, 13, "#e8a84a", "#6e4c20")}
  <!-- newer patch plate -->
  <g transform="rotate(2 236 618)">
    <rect x="212" y="598" width="50" height="40" rx="4" fill="url(#brassNew)" stroke="{INK}" stroke-width="1.8"/>
    {rivet(222, 608)}{rivet(252, 608)}{rivet(222, 628)}{rivet(252, 628)}
  </g>

  <!-- outer arm, both hands meant for the cane, one stayed -->
  {limb(214, 520, 196, 648, "#c99640", 28)}
  {limb(196, 648, 230, 742, "#b88838", 24)}
  {joint(214, 520, 13, "#a67532", "#f6e2b4")}
  {joint(196, 648, 11, "#8a6230", "#f0d7a0")}
  <!-- cane -->
  {tube("M236,700 C250,760 228,820 214,874", "#b88838", 8)}
  <circle cx="238" cy="692" r="12" fill="url(#brass)" stroke="{INK}" stroke-width="2"/>
  {spec(234, 688, 5, 3, 0.7)}
  <rect x="200" y="866" width="26" height="12" rx="3" fill="#2a241e" stroke="{INK}" stroke-width="1.5"/>
  <!-- hand stacked wrong on the knob -->
  <g id="caneHand">
    <rect x="214" y="676" width="22" height="18" rx="5" fill="#d4a44c" stroke="{INK}" stroke-width="1.8"/>
    <rect x="210" y="668" width="9" height="16" rx="3" fill="#c99640" stroke="{INK}" stroke-width="1.5" transform="rotate(-8 214 684)"/>
    <rect x="222" y="664" width="9" height="18" rx="3" fill="#d4a44c" stroke="{INK}" stroke-width="1.5"/>
    <rect x="234" y="668" width="9" height="15" rx="3" fill="#b88838" stroke="{INK}" stroke-width="1.5" transform="rotate(10 238 682)"/>
    <rect x="198" y="686" width="14" height="10" rx="3" fill="#a67532" stroke="{INK}" stroke-width="1.5" transform="rotate(-30 205 691)"/>
  </g>

  <!-- the hand that almost reaches her, and stops in the gray -->
  {limb(372, 518, 424, 588, "#c99640", 26)}
  {limb(424, 588, 458, 642, "#d4a44c", 22)}
  {joint(372, 518, 13, "#a67532", "#f6e2b4")}
  {joint(424, 588, 11, "#a67532", "#f6e2b4")}
  <g id="almost">
    <ellipse cx="468" cy="652" rx="15" ry="13" fill="#d4a44c" stroke="{INK}" stroke-width="1.8"/>
    <rect x="472" y="626" width="10" height="22" rx="4" fill="#e0b45a" stroke="{INK}" stroke-width="1.5" transform="rotate(-18 477 648)"/>
    <rect x="484" y="624" width="10" height="24" rx="4" fill="#d4a44c" stroke="{INK}" stroke-width="1.5" transform="rotate(-4 489 648)"/>
    <rect x="496" y="628" width="10" height="20" rx="4" fill="#c99640" stroke="{INK}" stroke-width="1.5" transform="rotate(14 501 648)"/>
    <rect x="456" y="662" width="15" height="11" rx="4" fill="#b88838" stroke="{INK}" stroke-width="1.5" transform="rotate(70 464 668)"/>
  </g>

  <!-- neck, dome, face -->
  <ellipse cx="300" cy="448" rx="36" ry="14" fill="#6e4c20" stroke="{INK}" stroke-width="2"/>
  <ellipse cx="300" cy="386" rx="80" ry="72" fill="url(#brass)" stroke="{INK}" stroke-width="2.4"/>
  {spec(262, 346, 30, 14, 0.55)}
  <ellipse cx="348" cy="348" rx="14" ry="8" fill="#6f8f78" opacity="0.32"/>
  <ellipse cx="300" cy="404" rx="52" ry="46" fill="#5a3d22" stroke="#3a2814" stroke-width="2"/>
  <!-- heavy brow over the old eye, lighter over the new one -->
  <path d="M220,382 Q244,358 268,380" stroke="#3a2814" stroke-width="10" fill="none" stroke-linecap="round"/>
  <path d="M274,372 Q310,358 366,384" stroke="#3a2814" stroke-width="6" fill="none" stroke-linecap="round"/>
  {eye(236, 404, 11, "#3d555c", dx=-1, dy=1, cloudy=True, lid="#5a3d22", clip="clipGeye")}
  {eye(308, 396, 16, "#1c4e5c", dx=6, dy=1)}
  <!-- hex nose -->
  <polygon points="{hex_points(304, 424, 8)}" fill="#efe0b8" stroke="{INK}" stroke-width="1.4"/>
  <circle cx="304" cy="424" r="2.2" fill="#6e4c20"/>
  <!-- aftermarket wire mustache, screwed on, longer on the family side -->
  <path d="M248,430
           C260,416 278,418 290,432
           C300,418 318,414 332,430
           C348,416 372,422 392,442
           C368,454 340,450 318,444
           C296,456 268,452 246,438 Z"
    fill="#b86432" stroke="#6a3418" stroke-width="1.6" stroke-linejoin="round"/>
  <path d="M252,434 C290,448 330,442 388,446" stroke="#6a3418" stroke-width="1.1" fill="none" opacity="0.7"/>
  <path d="M256,426 C300,440 350,436 384,440" stroke="#e0a070" stroke-width="1" fill="none" opacity="0.45"/>
  <circle cx="262" cy="422" r="3.2" fill="#d9dee3" stroke="{INK}" stroke-width="1"/>
  <circle cx="352" cy="424" r="3.2" fill="#d9dee3" stroke="{INK}" stroke-width="1"/>
  <path d="M258,422 v-6 M266,422 v-6 M348,424 v-6 M356,424 v-6" stroke="#8a9096" stroke-width="1"/>
  <!-- mouth vent, mostly a rumor under the mustache -->
  <rect x="292" y="448" width="28" height="6" rx="2" fill="#2a1c10"/>

  <!-- ear trumpet aimed at the family, not the camera -->
  <g id="trumpet">
    <path d="M352,392 L438,366 L470,338 L496,396 L468,422 L436,406 L356,428 Z"
      fill="url(#brass)" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>
    <path d="M390,384 L452,368" stroke="#6e4c20" stroke-width="3" fill="none"/>
    <path d="M378,400 L444,386" stroke="#f6e2b4" stroke-width="1.5" fill="none" opacity="0.55"/>
    <ellipse cx="480" cy="380" rx="16" ry="30" fill="#3a2818" stroke="{INK}" stroke-width="2.2"/>
    <ellipse cx="480" cy="380" rx="8" ry="18" fill="#140e0a"/>
    <ellipse cx="474" cy="370" rx="4" ry="7" fill="#fff" opacity="0.25"/>
  </g>
</g>
'''


def dad_body():
    """Middle-management chassis. Everything he added to look formal is crooked.
    The smile booted halfway. The free hand has nowhere to go.
    """
    return f'''
<g id="dad">
  <!-- the one visible shoe, missing the tape -->
  {limb(900, 620, 1010, 820, "#2c343c", 28)}
  {joint(900, 620, 11, "#3e4952", "#c5ced6")}
  <path d="M974,812 h78 v22 q0,16 -14,20 h-78 q-12,-2 -12,-16 v-10 q0,-16 14,-16 z"
    fill="#1c2228" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>
  <path d="M980,828 h70" stroke="#3a4048" stroke-width="5" stroke-linecap="round"/>
  <path d="M986,820 h18" stroke="#5a6268" stroke-width="3" stroke-linecap="round"/>

  <!-- torso / jacket -->
  <path d="M648,318
           h330
           q28,8 24,40
           l-16,250
           h-346
           l-16,-250
           q-4,-32 24,-40 z"
    fill="url(#slate)" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>
  {spec(720, 345, 50, 16, 0.18)}
  <!-- shirt panel -->
  <path d="M760,330 L724,520 h150 L850,330 Z" fill="#5c6c78"/>
  <!-- lapels -->
  <path d="M748,324 L690,470 L724,490 L778,340 Z" fill="#3a4650" stroke="{INK}" stroke-width="1.6"/>
  <path d="M868,324 L940,490 L908,500 L836,340 Z" fill="#334048" stroke="{INK}" stroke-width="1.6"/>
  <!-- tie, a thumb's width off center -->
  <path d="M792,336 h46 l16,150 -28,22 -26,-22 z" fill="#163e4c" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>
  <path d="M806,360 h16 l6,90 h-28 z" fill="#1e5c70" opacity="0.85"/>
  <circle cx="814" cy="342" r="6" fill="#0e2c36" stroke="{INK}" stroke-width="1.2"/>
  <!-- sash he leveled by eye, sitting high so it misses everyone else -->
  <g transform="rotate(-3.2 890 358)">
    <rect x="790" y="350" width="200" height="15" rx="3" fill="#f0c043" stroke="{INK}" stroke-width="1.6"/>
    <rect x="790" y="350" width="200" height="5" rx="2" fill="#ffe9a0" opacity="0.5"/>
  </g>
  <!-- blank badge, tilted the other way -->
  <g transform="rotate(8 900 378)">
    <rect x="878" y="360" width="44" height="30" rx="4" fill="#e7e1d6" stroke="{INK}" stroke-width="1.6"/>
    <rect x="878" y="360" width="44" height="8" rx="3" fill="#3a6ea5"/>
    <circle cx="888" cy="380" r="2" fill="#b0a898"/>
  </g>
  {lamp(962, 400, 8, "#3ddc84", "#1e3a28")}
  <!-- stylus -->
  <rect x="948" y="448" width="7" height="34" rx="2" fill="#c5ccd2" stroke="{INK}" stroke-width="1.2" transform="rotate(7 951 465)"/>
  <rect x="944" y="444" width="16" height="6" rx="1" fill="#2a3238"/>

  <!-- side seams -->
  <path d="M670,360 V560" stroke="#232a30" stroke-width="2" opacity="0.7"/>
  <path d="M960,370 V540" stroke="#232a30" stroke-width="2" opacity="0.55"/>

  <!-- collar -->
  <rect x="760" y="300" width="100" height="28" rx="8" fill="#232a30" stroke="{INK}" stroke-width="2"/>

  <!-- head: a screen with no neck to speak of -->
  <rect x="706" y="168" width="176" height="140" rx="28" fill="url(#slate)" stroke="{INK}" stroke-width="2.4"/>
  {spec(760, 196, 40, 14, 0.28)}
  <rect x="724" y="186" width="140" height="104" rx="16" fill="#12181e" stroke="#0c1014" stroke-width="2"/>
  <!-- glass reflection -->
  <path d="M734,196 h70 l-40,70 h-30 z" fill="#fff" opacity="0.05"/>
  <!-- eyes, dead level -->
  <rect x="748" y="224" width="40" height="16" rx="8" fill="#67e8ef" filter="url(#glow)"/>
  <rect x="818" y="224" width="40" height="16" rx="8" fill="#67e8ef" filter="url(#glow)"/>
  <rect x="750" y="226" width="22" height="4" rx="2" fill="#fff" opacity="0.55"/>
  <rect x="820" y="226" width="22" height="4" rx="2" fill="#fff" opacity="0.55"/>
  <rect x="762" y="227" width="4" height="10" rx="1" fill="#12383c"/>
  <rect x="832" y="227" width="4" height="10" rx="1" fill="#12383c"/>
  <!-- smile that booted halfway. The sixth cell keeps trying. -->
  <g id="dadMouth">
    <rect x="756" y="270" width="11" height="11" rx="2" fill="#1a2228"/>
    <rect x="772" y="270" width="11" height="11" rx="2" fill="#1a2228"/>
    <rect x="788" y="270" width="11" height="11" rx="2" fill="#5a8e92"/>
    <rect x="804" y="270" width="11" height="11" rx="2" fill="#6aa8ac"/>
    <rect x="820" y="270" width="11" height="11" rx="2" fill="#5a8e92"/>
    <rect x="836" y="270" width="11" height="11" rx="2" fill="#1a2228">
      <animate attributeName="fill" values="#1a2228;#1a2228;#6aa8ac;#1a2228;#1a2228"
        keyTimes="0;0.72;0.78;0.86;1" dur="4.8s" repeatCount="indefinite"/>
    </rect>
    <rect x="852" y="270" width="11" height="11" rx="2" fill="#1a2228"/>
  </g>
  <!-- vents -->
  <path d="M716,210 h16 M716,222 h16 M716,234 h16" stroke="#1a2026" stroke-width="2" stroke-linecap="round"/>
  <path d="M856,210 h16 M856,222 h16 M856,234 h16" stroke="#1a2026" stroke-width="2" stroke-linecap="round"/>

  <!-- antennas: a matched pair and a stump -->
  {tube("M770,168 L770,118", "#4a5660", 6)}
  <circle cx="770" cy="112" r="9" fill="#5c6c78" stroke="{INK}" stroke-width="2"/>
  {spec(767, 109, 3, 2, 0.8)}
  {tube("M830,168 L830,116", "#4a5660", 6)}
  <circle cx="830" cy="110" r="9" fill="#5c6c78" stroke="{INK}" stroke-width="2"/>
  {tube("M724,186 L708,158", "#4a5660", 6)}
  <ellipse cx="706" cy="154" rx="7" ry="5" fill="#c47a4a" stroke="{INK}" stroke-width="1.5"/>
  <path d="M702,152 h8" stroke="#6a3a22" stroke-width="1.4"/>

  <!-- free arm, held slightly off the body, fingers not committed -->
  {limb(960, 360, 990, 490, "#3e4952", 26)}
  {limb(990, 490, 1004, 590, "#354048", 22)}
  {joint(960, 360, 12, "#2e3840", "#b7c2cc")}
  {joint(990, 490, 10, "#2e3840", "#b7c2cc")}
  <g id="freeHand" transform="translate(1004,600) rotate(8)">
    <rect x="-16" y="-8" width="30" height="22" rx="6" fill="#4a5660" stroke="{INK}" stroke-width="1.8"/>
    <rect x="-12" y="-26" width="9" height="20" rx="3" fill="#3e4952" stroke="{INK}" stroke-width="1.4"/>
    <rect x="0" y="-28" width="9" height="22" rx="3" fill="#4a5660" stroke="{INK}" stroke-width="1.4"/>
    <rect x="12" y="-22" width="9" height="16" rx="3" fill="#3e4952" stroke="{INK}" stroke-width="1.4" transform="rotate(16 16 -14)"/>
    <rect x="-24" y="2" width="12" height="14" rx="3" fill="#2e3840" stroke="{INK}" stroke-width="1.4" transform="rotate(-40 -18 8)"/>
  </g>

  <!-- arm leaves his shoulder and disappears behind her head -->
  {limb(724, 358, 600, 470, "#3e4952", 24)}
  {joint(724, 358, 12, "#2e3840", "#b7c2cc")}
</g>
'''


def dad_hand():
    """The hand reappears on her shoulder. One finger never got the memo."""
    return f'''
<g id="dadHand">
  {limb(528, 588, 575, 648, "#3e4952", 20)}
  {joint(528, 588, 10, "#2e3840", "#b7c2cc")}
  <g transform="translate(568,642)">
    <rect x="-6" y="-4" width="32" height="22" rx="6" fill="#4a5660" stroke="{INK}" stroke-width="1.8"/>
    <rect x="0" y="12" width="10" height="18" rx="3" fill="#3e4952" stroke="{INK}" stroke-width="1.5"/>
    <rect x="12" y="14" width="10" height="16" rx="3" fill="#4a5660" stroke="{INK}" stroke-width="1.5"/>
    <rect x="22" y="12" width="9" height="14" rx="3" fill="#3e4952" stroke="{INK}" stroke-width="1.5"/>
    <rect x="-18" y="2" width="14" height="10" rx="3" fill="#2e3840" stroke="{INK}" stroke-width="1.5" transform="rotate(-55 -12 8)"/>
    <!-- index finger, up in the empty backdrop beside her cheek -->
    <rect x="-8" y="-62" width="12" height="62" rx="5" fill="#5c6a74" stroke="{INK}" stroke-width="1.8" transform="rotate(-18 -2 -30)"/>
  </g>
</g>
'''


def mom_body():
    """Hospitality chassis. She is holding the portrait together, and the smile."""
    return f'''
<g id="mom">
  <!-- studio stool, one cap replaced -->
  <ellipse cx="640" cy="866" rx="62" ry="12" fill="#8e99a1" stroke="{INK}" stroke-width="1.8"/>
  <rect x="632" y="800" width="16" height="66" rx="4" fill="#c5ced4" stroke="{INK}" stroke-width="1.6"/>
  <circle cx="592" cy="872" r="6" fill="#1b2126"/>
  <circle cx="640" cy="874" r="6" fill="#d0d6dc" stroke="{INK}" stroke-width="1.2"/>
  <circle cx="688" cy="872" r="6" fill="#d0d6dc" stroke="{INK}" stroke-width="1.2"/>

  <!-- little feet, one turned in -->
  <path d="M575,820 l28,8 6,28 -40,6 -8,-26 z" fill="#f4e7da" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M578,844 h30" stroke="#e07068" stroke-width="4" stroke-linecap="round"/>
  <path d="M688,828 l34,-2 10,26 -42,8 z" fill="#f4e7da" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M692,848 h32" stroke="#e07068" stroke-width="4" stroke-linecap="round"/>

  <!-- skirt flare -->
  <path d="M520,700
           C490,760 500,830 560,842
           H730
           C800,834 812,760 778,700
           Q650,730 520,700 Z"
    fill="url(#cream)" stroke="{INK}" stroke-width="2.3"/>
  {spec(590, 760, 40, 12, 0.28)}

  <!-- lap arm, the quiet one, on the side grandpa almost reaches -->
  {limb(545, 615, 512, 730, "#f6ecdf", 24)}
  {limb(512, 730, 575, 800, "#f3e4d4", 20)}
  {joint(545, 615, 11, "#e7d5c4", "#fff")}
  {joint(512, 730, 9, "#e7d5c4", "#fff")}
  <g id="lapHand" transform="translate(590,792)">
    <ellipse cx="0" cy="8" rx="16" ry="12" fill="#f6ecdf" stroke="{INK}" stroke-width="1.6"/>
    <rect x="-14" y="12" width="8" height="16" rx="3" fill="#f3e4d4" stroke="{INK}" stroke-width="1.3"/>
    <rect x="-4" y="14" width="8" height="17" rx="3" fill="#fffaf4" stroke="{INK}" stroke-width="1.3"/>
    <rect x="6" y="13" width="8" height="16" rx="3" fill="#f3e4d4" stroke="{INK}" stroke-width="1.3"/>
    <rect x="16" y="12" width="8" height="14" rx="3" fill="#e7d3c2" stroke="{INK}" stroke-width="1.3"/>
  </g>
  <!-- washer bracelet the small one made, spacing already going -->
  <g stroke="#d5dbe2" fill="none" stroke-width="2.4">
    <circle cx="560" cy="786" r="5.5"/>
    <circle cx="572" cy="792" r="5.5"/>
    <circle cx="584" cy="796" r="7"/>
    <circle cx="598" cy="792" r="5"/>
    <circle cx="608" cy="786" r="5.5"/>
  </g>

  <!-- torso -->
  <path d="M545,575
           C520,600 516,680 530,720
           H750
           C770,680 768,600 738,572
           Q640,548 545,575 Z"
    fill="url(#cream)" stroke="{INK}" stroke-width="2.3"/>
  <path d="M575,590 Q640,570 715,592" stroke="#e07068" stroke-width="10" fill="none" stroke-linecap="round"/>
  {spec(600, 620, 36, 14, 0.4)}
  {lamp(668, 655, 12, "#ee8b9a", "#a84850")}

  <!-- apron -->
  <path d="M590,600 h100 l8,40 H582 Z" fill="url(#apron)" stroke="{INK}" stroke-width="1.6"/>
  <path d="M600,612 Q640,598 700,614" stroke="#f8e4dc" stroke-width="4" fill="none"/>
  <path d="M575,700 h150 v108 q-75,16 -150,0 z" fill="url(#apron)" stroke="{INK}" stroke-width="1.8"/>
  <path d="M612,588 q-6,-30 28,-36" stroke="#e7c8bc" stroke-width="5" fill="none" stroke-linecap="round"/>
  <path d="M700,590 q10,-34 36,-28" stroke="#e7c8bc" stroke-width="5" fill="none" stroke-linecap="round"/>
  <!-- pocket with the screwdriver she didn't put down -->
  <path d="M640,742 h52 v40 q-26,8 -52,0 z" fill="#f8e4dc" stroke="{INK}" stroke-width="1.5"/>
  <path d="M648,742 q26,-8 44,0" stroke="#c9a89c" stroke-width="2" fill="none"/>
  <rect x="658" y="724" width="9" height="22" rx="2" fill="#c4884a" stroke="{INK}" stroke-width="1.2" transform="rotate(12 662 735)"/>
  <rect x="666" y="712" width="3" height="16" rx="1" fill="#c5ccd2" transform="rotate(12 667 720)"/>

  <!-- corsage at the collar: two blooms up, one already nodding -->
  <g id="flowers">
    <path d="M624,648 C618,632 612,622 606,612" stroke="#5f7d52" stroke-width="3" fill="none" stroke-linecap="round"/>
    <path d="M636,650 C644,636 652,626 660,616" stroke="#5f7d52" stroke-width="3" fill="none" stroke-linecap="round"/>
    <path d="M630,652 C634,670 626,688 638,702" stroke="#5f7d52" stroke-width="3" fill="none" stroke-linecap="round"/>
    <g transform="translate(602,606)">
      <ellipse cx="0" cy="-8" rx="5" ry="7" fill="#e36b62" stroke="{INK}" stroke-width="1"/>
      <ellipse cx="7" cy="-2" rx="7" ry="5" fill="#e36b62" stroke="{INK}" stroke-width="1"/>
      <ellipse cx="4" cy="7" rx="5" ry="7" fill="#c45450" stroke="{INK}" stroke-width="1"/>
      <ellipse cx="-6" cy="3" rx="7" ry="5" fill="#e36b62" stroke="{INK}" stroke-width="1"/>
      <circle r="4" fill="#f4d35e" stroke="{INK}" stroke-width="1"/>
    </g>
    <g transform="translate(664,610)">
      <ellipse cx="0" cy="-7" rx="4.5" ry="6" fill="#f0c043" stroke="{INK}" stroke-width="1"/>
      <ellipse cx="6" cy="-1" rx="6" ry="4.5" fill="#f0c043" stroke="{INK}" stroke-width="1"/>
      <ellipse cx="2" cy="6" rx="4.5" ry="6" fill="#d09a28" stroke="{INK}" stroke-width="1"/>
      <ellipse cx="-6" cy="2" rx="6" ry="4.5" fill="#f0c043" stroke="{INK}" stroke-width="1"/>
      <circle r="3.4" fill="#fff6d0" stroke="{INK}" stroke-width="1"/>
    </g>
    <g transform="translate(642,706) rotate(28)">
      <ellipse cx="0" cy="-6" rx="4" ry="6" fill="#e36b62" stroke="{INK}" stroke-width="1"/>
      <ellipse cx="6" cy="0" rx="6" ry="4" fill="#c45450" stroke="{INK}" stroke-width="1"/>
      <ellipse cx="0" cy="6" rx="4" ry="6" fill="#e36b62" stroke="{INK}" stroke-width="1"/>
      <ellipse cx="-6" cy="0" rx="6" ry="4" fill="#e36b62" stroke="{INK}" stroke-width="1"/>
      <circle r="3" fill="#f4d35e" stroke="{INK}" stroke-width="1"/>
    </g>
    <circle cx="628" cy="652" r="4.5" fill="#b7c0c6" stroke="{INK}" stroke-width="1.2"/>
  </g>

  <!-- uneven bow -->
  <ellipse cx="508" cy="708" rx="20" ry="13" fill="#f0d2c8" stroke="{INK}" stroke-width="1.6" transform="rotate(-24 508 708)"/>
  <ellipse cx="534" cy="716" rx="13" ry="10" fill="#e7c4b8" stroke="{INK}" stroke-width="1.6" transform="rotate(18 534 716)"/>
  <path d="M516,718 C500,748 486,770 478,798" stroke="#f0d2c8" stroke-width="7" fill="none" stroke-linecap="round"/>
  <path d="M516,718 C500,748 486,770 478,798" stroke="{INK}" stroke-width="1.2" fill="none"/>
  <path d="M524,722 C540,760 548,792 556,812" stroke="#e2b8ac" stroke-width="6" fill="none" stroke-linecap="round"/>

  <!-- neck and head -->
  <rect x="612" y="548" width="52" height="36" rx="12" fill="#f3e4d4" stroke="{INK}" stroke-width="2"/>
  <path d="M608,570 h60" stroke="#e07068" stroke-width="8" stroke-linecap="round"/>
  <ellipse cx="640" cy="492" rx="82" ry="78" fill="url(#cream)" stroke="{INK}" stroke-width="2.4"/>
  {spec(598, 446, 28, 12, 0.55)}
  <!-- escaped wire from the bun -->
  <path d="M640,414
           m-22,0
           a22,22 0 1 1 44,0
           a22,22 0 1 1 -44,0"
    fill="none" stroke="#c4923e" stroke-width="8"/>
  <path d="M640,414
           m-22,0
           a22,22 0 1 1 44,0
           a22,22 0 1 1 -44,0"
    fill="none" stroke="{INK}" stroke-width="1.5"/>
  <path d="M662,402 C688,392 700,408 692,424" stroke="#c4923e" stroke-width="4" fill="none" stroke-linecap="round"/>
  <circle cx="692" cy="426" r="3.5" fill="#e8c56a" stroke="{INK}" stroke-width="1"/>

  <!-- brows, one working harder -->
  <path d="M576,468 Q598,452 622,470" stroke="#a84850" stroke-width="4.5" fill="none" stroke-linecap="round"/>
  <path d="M650,476 Q670,470 692,482" stroke="#a84850" stroke-width="3.5" fill="none" stroke-linecap="round"/>
  {eye(598, 492, 16, "#e39a3c", dx=3, dy=2, lid="#f3e4d4", clip="clipMeyeL")}
  {eye(666, 496, 16, "#e39a3c", dx=3, dy=1, lid="#f3e4d4", clip="clipMeyeR")}
  <!-- lashes -->
  <path d="M580,480 l-8,-6 M586,476 l-2,-8 M674,482 l8,-5 M682,478 l4,-7"
    stroke="#a84850" stroke-width="1.6" stroke-linecap="round"/>
  <ellipse cx="586" cy="522" rx="12" ry="7" fill="#f0a090" opacity="0.45"/>
  <ellipse cx="690" cy="524" rx="11" ry="7" fill="#f0a090" opacity="0.4"/>
  <!-- the smile that is doing too much -->
  <path d="M572,524 Q640,590 710,522 Q640,556 572,524 Z" fill="#3a2422" stroke="{INK}" stroke-width="1.6"/>
  <path d="M566,518 Q640,500 716,516" stroke="#e07068" stroke-width="5" fill="none" stroke-linecap="round"/>
  <rect x="588" y="530" width="14" height="16" rx="2" fill="#fffaf6"/>
  <rect x="604" y="534" width="14" height="16" rx="2" fill="#fffaf6"/>
  <rect x="620" y="536" width="14" height="16" rx="2" fill="#fffaf6"/>
  <rect x="636" y="536" width="14" height="16" rx="2" fill="#fffaf6"/>
  <rect x="652" y="534" width="14" height="16" rx="2" fill="#d9d0c6"/>
  <rect x="668" y="528" width="14" height="16" rx="2" fill="#fffaf6"/>
  <rect x="684" y="524" width="13" height="15" rx="2" fill="#fffaf6"/>
</g>
'''


def teen():
    """Warranty void. Present, and leaned as far out of the group as the frame allows.
    The shoe toward the family is where the pet is allowed to sit.
    """
    return f'''
<g id="teen">
  <!-- turned-out sneaker -->
  <path d="M1368,788 C1410,800 1460,820 1468,846 L1452,872 L1348,868 L1336,830 Z"
    fill="#f3f0ea" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>
  <path d="M1352,846 H1460" stroke="#e23d8a" stroke-width="6" stroke-linecap="round"/>
  <path d="M1360,860 H1450" stroke="#1b2126" stroke-width="7" stroke-linecap="round"/>
  <!-- planted sneaker, lace undone -->
  <path d="M1136,800 C1160,792 1224,804 1236,834 L1230,872 L1128,870 L1116,836 Z"
    fill="#f4f1eb" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>
  <path d="M1144,848 H1224" stroke="#e23d8a" stroke-width="6" stroke-linecap="round"/>
  <path d="M1148,862 H1222" stroke="#1b2126" stroke-width="7" stroke-linecap="round"/>
  <!-- dangling lace -->
  <path d="M1168,834 C1162,860 1178,878 1164,896" stroke="#f4f1eb" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M1184,836 C1196,862 1174,888 1192,900" stroke="#dedad2" stroke-width="3.5" fill="none" stroke-linecap="round"/>
  <path d="M1168,834 C1162,860 1178,878 1164,896" stroke="{INK}" stroke-width="1" fill="none"/>

  <!-- legs, tucked up under the hem so they belong to the hoodie -->
  {limb(1210, 630, 1184, 812, "#1a1c22", 28)}
  {limb(1324, 640, 1376, 804, "#1a1c22", 26)}
  {joint(1210, 630, 10, "#2a2c34", "#8a9098")}
  {joint(1324, 640, 10, "#2a2c34", "#8a9098")}

  <!-- hoodie body, right shoulder dropped -->
  <path d="M1148,455
           C1124,520 1136,620 1168,678
           Q1260,742 1388,700
           C1436,640 1452,530 1410,470
           Q1280,400 1148,455 Z"
    fill="url(#hoodie)" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>
  {spec(1220, 490, 46, 16, 0.16)}
  <!-- rib -->
  <path d="M1176,662 Q1270,706 1376,676" stroke="#243244" stroke-width="3" fill="none" opacity="0.7"/>
  <path d="M1182,674 Q1272,716 1370,686" stroke="#243244" stroke-width="2" fill="none" opacity="0.5"/>
  <!-- pocket -->
  <path d="M1204,590 h150 q8,40 -6,62 h-140 q-16,-22 -4,-62 z" fill="#314256" stroke="{INK}" stroke-width="1.6"/>
  <path d="M1216,598 H1344" stroke="#1b2836" stroke-width="3" stroke-linecap="round"/>
  <!-- hood pile -->
  <ellipse cx="1305" cy="430" rx="78" ry="36" fill="#2a3a4e" stroke="{INK}" stroke-width="2"/>
  <path d="M1254,424 Q1305,452 1360,420" stroke="#1b2836" stroke-width="6" fill="none" stroke-linecap="round"/>

  <!-- crossed sleeves. Top sleeve is pushed up. -->
  {limb(1168, 490, 1310, 575, "#3d516c", 34)}
  {limb(1400, 500, 1260, 545, "#4a6284", 32)}
  <!-- exposed forearm, primer showing -->
  {limb(1260, 545, 1188, 610, "#1a1c22", 18)}
  <path d="M1224,566 C1236,558 1244,574 1232,584 C1220,590 1212,576 1224,566 Z" fill="#e8843c" stroke="#9a4e1c" stroke-width="1"/>
  <path d="M1216,572 l22,8" stroke="#c46828" stroke-width="1.5"/>
  {joint(1188, 610, 8, "#2a2c34", "#9aa0a8")}
  <!-- thumb with a hex nut, the only soft tell besides the shoe -->
  <g transform="translate(1192,618) rotate(-20)">
    <rect x="-6" y="-4" width="16" height="22" rx="5" fill="#2a2c34" stroke="{INK}" stroke-width="1.5"/>
    <polygon points="{hex_points(2, 16, 8)}" fill="#d5dbe2" stroke="{INK}" stroke-width="1.2"/>
    <circle cx="2" cy="16" r="2.4" fill="#2a2c34"/>
  </g>

  <!-- drawstrings, unequal -->
  <path d="M1284,448 C1276,490 1288,530 1272,562" stroke="#f4f1eb" stroke-width="3.2" fill="none" stroke-linecap="round"/>
  <path d="M1316,446 C1324,510 1306,570 1330,624" stroke="#f4f1eb" stroke-width="3.2" fill="none" stroke-linecap="round"/>
  <path d="M1324,624 l6,10 M1330,624 l8,8 M1336,618 l4,12" stroke="#f4f1eb" stroke-width="1.4" stroke-linecap="round"/>
  <circle cx="1272" cy="562" r="3" fill="#c5cad0"/>

  <!-- head, tilted off the group -->
  <g transform="rotate(11 1338 330)">
    <rect x="1284" y="262" width="108" height="132" rx="36" fill="#2a2d36" stroke="{INK}" stroke-width="2.3"/>
    {spec(1310, 286, 24, 10, 0.18)}
    <!-- headphone band -->
    <path d="M1296,286 Q1338,232 1392,292" stroke="#1a1c22" stroke-width="9" fill="none" stroke-linecap="round"/>
    <path d="M1296,286 Q1338,232 1392,292" stroke="#3a3e48" stroke-width="3" fill="none"/>
    <ellipse cx="1394" cy="308" rx="14" ry="18" fill="#1a1c22" stroke="{INK}" stroke-width="1.6"/>
    <ellipse cx="1390" cy="304" rx="5" ry="7" fill="#3a3e48"/>
    <!-- whip antenna, bent -->
    <path d="M1310,262 C1300,220 1340,200 1330,168" stroke="#3a3e48" stroke-width="4" fill="none" stroke-linecap="round"/>
    <circle cx="1330" cy="164" r="5" fill="#e23d8a" stroke="{INK}" stroke-width="1.2"/>
    <!-- bangs hide the eye that would have to look at the family -->
    <path d="M1296,280
             C1284,330 1272,370 1278,410
             C1298,385 1304,340 1318,300
             C1324,250 1348,246 1364,278
             C1340,268 1316,250 1296,280 Z"
      fill="#14161c" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>
    <path d="M1310,270 C1304,320 1316,360 1304,400" stroke="#0c0e12" stroke-width="6" fill="none" stroke-linecap="round"/>
    <path d="M1336,258 C1348,300 1330,350 1344,392" stroke="#101218" stroke-width="7" fill="none" stroke-linecap="round"/>
    <!-- a little glow where the covered eye still is -->
    <ellipse cx="1304" cy="332" rx="8" ry="4" fill="#e23d8a" opacity="0.35" filter="url(#glow)"/>
    <!-- the eye that got away -->
    {eye(1368, 318, 13, "#e23d8a", dx=4, dy=1, lid="#2a2d36", clip="clipTeye")}
    <path d="M1352,304 Q1368,296 1384,306" stroke="#1a1c22" stroke-width="5" fill="none" stroke-linecap="round"/>
    <!-- ghost of a cheek decal, scraped off -->
    <circle cx="1312" cy="348" r="8" fill="none" stroke="#e23d8a" stroke-width="1.5" opacity="0.35"/>
    <!-- mouth -->
    <path d="M1354,362 q12,4 24,-2" stroke="#3a2030" stroke-width="3" fill="none" stroke-linecap="round"/>
    <!-- washer earring under the bangs -->
    <circle cx="1292" cy="360" r="6" fill="none" stroke="#d5dbe2" stroke-width="2.4"/>
    <circle cx="1292" cy="360" r="1.6" fill="#d5dbe2"/>
  </g>
  <!-- faint lamp leak at the collar -->
  <ellipse cx="1310" cy="455" rx="10" ry="5" fill="#e23d8a" opacity="0.45" filter="url(#glow)"/>
</g>
'''


def kid_and_cases():
    """Early-learning unit on two tool cases. The wave was not in the instructions.
    One arm was finished in a hurry. The cheek paint did not survive the car.
    """
    return f'''
<g id="cases">
  <rect x="790" y="824" width="196" height="54" rx="6" fill="url(#caseA)" stroke="{INK}" stroke-width="2"/>
  <rect x="802" y="834" width="172" height="28" rx="3" fill="#8a3050" opacity="0.45"/>
  <rect x="776" y="838" width="16" height="22" rx="4" fill="#5a2030" stroke="{INK}" stroke-width="1.4"/>
  <rect x="868" y="842" width="16" height="10" rx="2" fill="#c5ccd2" stroke="{INK}" stroke-width="1"/>
  <rect x="908" y="842" width="16" height="10" rx="2" fill="#c5ccd2" stroke="{INK}" stroke-width="1"/>
  <path d="M812,860 l18,8" stroke="#f0c8d0" stroke-width="2" opacity="0.4"/>
  <g transform="rotate(-5.5 900 802)">
    <rect x="812" y="778" width="168" height="48" rx="6" fill="url(#caseB)" stroke="{INK}" stroke-width="2"/>
    <rect x="824" y="788" width="144" height="22" rx="3" fill="#6a7a40" opacity="0.4"/>
    <rect x="900" y="792" width="14" height="9" rx="2" fill="#c5ccd2" stroke="{INK}" stroke-width="1"/>
    <!-- latch that didn't catch -->
    <g transform="rotate(58 968 800)">
      <rect x="960" y="792" width="22" height="9" rx="2" fill="#d0d6dc" stroke="{INK}" stroke-width="1.2"/>
      <circle cx="962" cy="796" r="2" fill="#1b2126"/>
    </g>
  </g>
</g>
<g id="kid">
  <!-- shoes on the case, one sole awake -->
  <path d="M832,752 h36 v18 q0,8 -8,8 h-28 q-8,0 -8,-8 z" fill="url(#kidYellow)" stroke="{INK}" stroke-width="1.6"/>
  <path d="M834,770 h32" stroke="#9fd8f8" stroke-width="4" stroke-linecap="round" opacity="0.35"/>
  <path d="M900,748 h38 v18 q0,8 -8,8 h-30 q-8,0 -8,-8 z" fill="url(#kidYellow)" stroke="{INK}" stroke-width="1.6"/>
  <path d="M904,766 h30" stroke="#7ee8ef" stroke-width="5" stroke-linecap="round" filter="url(#glow)">
    <animate attributeName="opacity" values="1;1;0.25;1;1" keyTimes="0;0.4;0.55;0.7;1" dur="1.6s" repeatCount="indefinite"/>
  </path>
  {limb(846, 700, 846, 760, "#f0c14e", 18)}
  {limb(912, 700, 918, 756, "#f0c14e", 18)}
  <!-- bandage on the near knee -->
  <g transform="rotate(-8 846 742)">
    <rect x="834" y="732" width="24" height="16" rx="3" fill="#f4e6d0" stroke="{INK}" stroke-width="1.2"/>
    <rect x="841" y="735" width="10" height="10" rx="1" fill="#f8f4ea"/>
    <path d="M834,746 l6,-4" stroke="#e6d2b8" stroke-width="2"/>
  </g>

  <!-- body -->
  <rect x="824" y="630" width="130" height="84" rx="28" fill="url(#kidBlue)" stroke="{INK}" stroke-width="2.2"/>
  {spec(860, 652, 28, 10, 0.4)}
  <!-- mold line, drifted -->
  <path d="M892,636 v72" stroke="#d6f0ff" stroke-width="2" opacity="0.55"/>
  {lamp(888, 672, 8, "#7ee8ef")}
  <circle cx="888" cy="672" r="8" fill="#7ee8ef" opacity="0.001">
    <animate attributeName="fill" values="#7ee8ef;#f0c14e;#e07068;#7ee8ef" dur="3.2s" repeatCount="indefinite"/>
  </circle>

  <!-- holding arm, the original yellow, reaching back to mom -->
  {limb(840, 660, 780, 724, "#f0c14e", 18)}
  {joint(840, 660, 9, "#d09a28", "#fff3c4")}

  <!-- head -->
  <circle cx="900" cy="560" r="70" fill="url(#kidBlue)" stroke="{INK}" stroke-width="2.4"/>
  {spec(868, 524, 26, 12, 0.5)}
  <path d="M900,492 v130" stroke="#d6f0ff" stroke-width="2" opacity="0.4"/>
  <!-- ears -->
  <circle cx="832" cy="566" r="12" fill="url(#kidYellow)" stroke="{INK}" stroke-width="1.6"/>
  <circle cx="968" cy="562" r="12" fill="url(#kidYellowOld)" stroke="{INK}" stroke-width="1.6"/>
  <!-- spring, listing toward mom -->
  <g>
    <g>
      <animateTransform attributeName="transform" type="rotate"
        values="-4 888 498;7 888 498;-4 888 498" dur="1.8s" repeatCount="indefinite"/>
      <path d="M888,498 C876,484 868,476 856,468"
        stroke="#f0c14e" stroke-width="5" fill="none" stroke-linecap="round"/>
      <circle cx="850" cy="462" r="8" fill="#e07068" stroke="{INK}" stroke-width="1.4"/>
      <circle cx="847" cy="459" r="2.4" fill="#fff" opacity="0.8"/>
    </g>
  </g>
  <!-- brows up -->
  <path d="M848,528 Q870,512 892,526" stroke="#1a3a58" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M912,524 Q934,510 956,524" stroke="#1a3a58" stroke-width="4" fill="none" stroke-linecap="round"/>
  {eye(868, 552, 20, "#1c3a5c", dx=1, dy=-1)}
  {eye(934, 550, 20, "#1c3a5c", dx=1, dy=-1)}
  <!-- cheeks, one smeared -->
  <circle cx="846" cy="586" r="11" fill="#ff5d4a" opacity="0.9"/>
  <circle cx="952" cy="584" r="12" fill="#ff5d4a" opacity="0.9"/>
  <path d="M960,592 q10,14 4,26 q-8,2 -12,-6 z" fill="#ff5d4a" opacity="0.75"/>
  <!-- open beep, one tooth dark -->
  <rect x="872" y="586" width="52" height="32" rx="10" fill="#1a2430" stroke="{INK}" stroke-width="1.6"/>
  <rect x="878" y="590" width="10" height="10" rx="2" fill="#fffaf6"/>
  <rect x="892" y="590" width="10" height="10" rx="2" fill="#1a2430"/>
  <rect x="906" y="590" width="10" height="10" rx="2" fill="#fffaf6"/>
  <rect x="884" y="604" width="10" height="9" rx="2" fill="#fffaf6"/>
  <rect x="900" y="604" width="10" height="9" rx="2" fill="#fffaf6"/>
</g>
'''


def kid_wave():
    """The arm that was replaced this morning, already in motion."""
    # Shoulder at (958, 668). Arm drawn in that frame, +x to the right, +y down.
    arm = f'''
    {limb(0, 0, 78, -78, "#e0a82e", 18)}
    {joint(0, 0, 10, "#c48428", "#fff3c4")}
    {joint(78, -78, 8, "#c48428", "#fff3c4")}
    {limb(78, -78, 148, -150, "#e8b040", 16)}
    <g transform="translate(156,-158)">
      <circle cx="0" cy="0" r="14" fill="#f0c14e" stroke="{INK}" stroke-width="1.6"/>
      <circle cx="-16" cy="-12" r="6" fill="#f0c14e" stroke="{INK}" stroke-width="1.3"/>
      <circle cx="-6" cy="-20" r="6.5" fill="#ffe38a" stroke="{INK}" stroke-width="1.3"/>
      <circle cx="8" cy="-20" r="6.5" fill="#f0c14e" stroke="{INK}" stroke-width="1.3"/>
      <circle cx="18" cy="-10" r="6" fill="#e0a82e" stroke="{INK}" stroke-width="1.3"/>
      <circle cx="-8" cy="8" r="3" fill="#fff" opacity="0.6"/>
    </g>
    '''
    return f'''
<g id="wave">
  <g opacity="0.16" transform="translate(958,668) rotate(-30)">{arm}</g>
  <g transform="translate(958,668)">
    <g transform="rotate(-6)">
      <animateTransform attributeName="transform" type="rotate"
        values="-6;12;-6" dur="0.85s" repeatCount="indefinite"
        calcMode="spline" keySplines="0.45 0 0.2 1;0.45 0 0.2 1"/>
      {arm}
    </g>
  </g>
</g>
'''


def clasp():
    """Mom's hand and the kid's hand, sharing two fingers and surprising the other two."""
    return f'''
<g id="clasp">
  {limb(730, 608, 790, 690, "#f6ecdf", 22)}
  {limb(790, 690, 820, 736, "#f3e4d4", 18)}
  {joint(730, 608, 11, "#e7d5c4", "#fff")}
  {joint(790, 690, 9, "#e7d5c4", "#fff")}
  <!-- kid fist around the middle fingers -->
  <ellipse cx="812" cy="748" rx="18" ry="14" fill="#f0c14e" stroke="{INK}" stroke-width="1.7"/>
  <circle cx="800" cy="744" r="5" fill="#ffe38a" stroke="{INK}" stroke-width="1"/>
  <circle cx="812" cy="738" r="5" fill="#f0c14e" stroke="{INK}" stroke-width="1"/>
  <circle cx="824" cy="742" r="5" fill="#e0a82e" stroke="{INK}" stroke-width="1"/>
  <!-- mom fingers that escaped -->
  <rect x="828" y="724" width="9" height="22" rx="4" fill="#fffaf4" stroke="{INK}" stroke-width="1.4" transform="rotate(18 832 746)"/>
  <rect x="786" y="728" width="9" height="20" rx="4" fill="#f3e4d4" stroke="{INK}" stroke-width="1.4" transform="rotate(-28 790 748)"/>
  <ellipse cx="808" cy="756" rx="8" ry="6" fill="#e7d3c2" stroke="{INK}" stroke-width="1.2"/>
</g>
'''


def pet():
    """Links the case to the untied shoe. Looks at the teen, who is not looking back."""
    return f'''
<g id="pet" transform="translate(-58,-36)">
  <!-- tail plug sits on the tool case -->
  <g>
    <animateTransform attributeName="transform" type="rotate"
      values="-7 990 950;9 990 950;-7 990 950" dur="1.3s" repeatCount="indefinite"
      calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
    <path d="M990,955 C1005,910 1008,880 992,858" stroke="{INK}" stroke-width="16" fill="none" stroke-linecap="round"/>
    <path d="M990,955 C1005,910 1008,880 992,858" stroke="#248f84" stroke-width="10" fill="none" stroke-linecap="round"/>
    <path d="M990,955 C1005,910 1008,880 992,858" stroke="#b8ebe4" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <rect x="972" y="844" width="24" height="16" rx="3" fill="#2a3036" stroke="{INK}" stroke-width="1.5"/>
    <rect x="960" y="847" width="14" height="3.5" rx="1" fill="#c5ccd2"/>
    <rect x="960" y="854" width="14" height="3.5" rx="1" fill="#c5ccd2"/>
  </g>

  <!-- wheels: the rear one was replaced -->
  <g id="wheels">
    <circle cx="980" cy="962" r="16" fill="#1a3e3a" stroke="{INK}" stroke-width="2"/>
    <circle cx="980" cy="962" r="6" fill="#8e99a1"/>
    <circle cx="1055" cy="970" r="16" fill="#1a3e3a" stroke="{INK}" stroke-width="2"/>
    <circle cx="1055" cy="970" r="6" fill="#8e99a1"/>
    <circle cx="1128" cy="966" r="15" fill="#1a3e3a" stroke="{INK}" stroke-width="2"/>
    <circle cx="1128" cy="966" r="6" fill="#8e99a1"/>
    <circle cx="1196" cy="958" r="16" fill="#a67532" stroke="{INK}" stroke-width="2"/>
    <circle cx="1196" cy="958" r="6" fill="#f0d7a0"/>
  </g>
  {limb(980, 930, 980, 954, "#1d6e62", 12)}
  {limb(1055, 938, 1055, 960, "#1d6e62", 12)}
  {limb(1128, 934, 1128, 956, "#1d6e62", 12)}
  {limb(1190, 924, 1196, 948, "#1d6e62", 12)}

  <!-- long body -->
  <path d="M950,900
           C940,860 980,842 1060,844
           H1160
           C1220,844 1230,890 1210,930
           C1180,972 1000,980 960,960
           C930,948 934,920 950,900 Z"
    fill="url(#teal)" stroke="{INK}" stroke-width="2.3"/>
  <ellipse cx="1040" cy="940" rx="70" ry="22" fill="#e7f7f3" opacity="0.85"/>
  {spec(1020, 870, 40, 12, 0.35)}
  {lamp(1088, 900, 6, "#3ddc84", "#14584c")}
  <!-- scratch -->
  <path d="M990,910 l16,6" stroke="#14584c" stroke-width="2" stroke-linecap="round"/>

  <!-- collar in mom's coral -->
  <path d="M1148,888 q30,8 28,36" stroke="#e07068" stroke-width="10" fill="none" stroke-linecap="round"/>
  <path d="M1148,888 q30,8 28,36" stroke="{INK}" stroke-width="1.4" fill="none"/>
  <circle cx="1164" cy="932" r="8" fill="#f0d2c8" stroke="{INK}" stroke-width="1.3"/>
  <circle cx="1164" cy="932" r="3.5" fill="none" stroke="#a84850" stroke-width="1.4"/>
  <path d="M1160,929 l3,5" stroke="#c48a80" stroke-width="1"/>

  <!-- head lifted toward the teen -->
  <ellipse cx="1210" cy="868" rx="48" ry="40" fill="url(#teal)" stroke="{INK}" stroke-width="2.2"/>
  {spec(1188, 850, 16, 8, 0.45)}
  <!-- one ear down, one ear arguing -->
  <ellipse cx="1172" cy="900" rx="14" ry="22" fill="#21786c" stroke="{INK}" stroke-width="1.6" transform="rotate(18 1172 900)"/>
  <ellipse cx="1236" cy="830" rx="12" ry="20" fill="#3dbaaa" stroke="{INK}" stroke-width="1.6" transform="rotate(-12 1236 830)"/>
  <ellipse cx="1234" cy="826" rx="4" ry="8" fill="#e7f7f3" opacity="0.6"/>
  <!-- snout -->
  <ellipse cx="1254" cy="886" rx="30" ry="18" fill="#7ed9cc" stroke="{INK}" stroke-width="1.8"/>
  <ellipse cx="1276" cy="884" rx="7" ry="5.5" fill="#1b2126"/>
  <ellipse cx="1274" cy="882" rx="2" ry="1.4" fill="#fff" opacity="0.5"/>
  <!-- eyes up, a little crossed, full of the person not looking at them -->
  {eye(1194, 862, 11, "#14342e", dx=-1, dy=-4)}
  {eye(1224, 856, 12, "#14342e", dx=2, dy=-5)}
  <!-- ribbon-cable tongue -->
  <g>
    <animateTransform attributeName="transform" type="rotate"
      values="-4 1258 900;6 1258 900;-4 1258 900" dur="1.1s" repeatCount="indefinite"/>
    <rect x="1248" y="896" width="16" height="28" rx="6" fill="#f099aa" stroke="{INK}" stroke-width="1.3"/>
    <path d="M1252,902 v16 M1256,900 v18 M1260,902 v16" stroke="#d07088" stroke-width="1"/>
  </g>
</g>
'''


def grade():
    return '''
<g id="grade" pointer-events="none">
  <rect width="1600" height="1000" fill="url(#warm)" opacity="0.28" style="mix-blend-mode:soft-light"/>
  <rect width="1600" height="1000" fill="url(#vig)"/>
  <rect width="1600" height="1000" filter="url(#grain)" opacity="0.22"/>
</g>
'''


def build():
    body = "\n".join(
        [
            defs(),
            backdrop(),
            shadows(),
            grandpa(),
            dad_body(),
            teen(),
            mom_body(),
            dad_hand(),
            kid_and_cases(),
            clasp(),
            kid_wave(),
            pet(),
            grade(),
        ]
    )
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000" width="1600" height="1000">
{body}
</svg>
'''


def main():
    svg = build()
    if "<text" in svg or "<tspan" in svg:
        raise SystemExit("visible text slipped in")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    ET.fromstring(svg)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
