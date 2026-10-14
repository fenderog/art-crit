#!/usr/bin/env python3
"""Generate an awkward studio family portrait of robots as a single SVG.

No text anywhere in the artwork -- personality is expressed only through
pose, gaze, spacing and props.  Output: output/robots-family-portrait.svg
"""
import os

W, H = 1400, 1000
OUT = os.path.join(os.path.dirname(__file__), "..", "output",
                   "robots-family-portrait.svg")

S = []


def add(s):
    S.append(s)


def bolt(x, y, r=6, col="#2b2f38", hi="#8b95a6"):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/>'
            f'<circle cx="{x}" cy="{y}" r="{r*0.55:.1f}" fill="{hi}"/>')


def rivets(x0, y0, x1, y1, n=4, r=3):
    out = []
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" '
                   f'fill="#8b95a6" opacity="0.8"/>')
    return "".join(out)


# ----------------------------------------------------------------------------
# Defs
# ----------------------------------------------------------------------------
add(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     width="{W}" height="{H}">
<defs>
  <radialGradient id="wall" cx="50%" cy="38%" r="75%">
    <stop offset="0%" stop-color="#fdf3e0"/>
    <stop offset="62%" stop-color="#f0dcbc"/>
    <stop offset="100%" stop-color="#dcc39b"/>
  </radialGradient>
  <radialGradient id="spot" cx="50%" cy="30%" r="55%">
    <stop offset="0%" stop-color="#fff7e6" stop-opacity="0.95"/>
    <stop offset="100%" stop-color="#fff7e6" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#c08a55"/>
    <stop offset="100%" stop-color="#8a5c33"/>
  </linearGradient>
  <linearGradient id="curtain" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#1c3a39"/>
    <stop offset="50%" stop-color="#2e5553"/>
    <stop offset="100%" stop-color="#17302f"/>
  </linearGradient>
  <linearGradient id="dad" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#84a3d4"/>
    <stop offset="45%" stop-color="#4f76ad"/>
    <stop offset="100%" stop-color="#2c4772"/>
  </linearGradient>
  <linearGradient id="mom" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#f6c2c8"/>
    <stop offset="45%" stop-color="#dd92a4"/>
    <stop offset="100%" stop-color="#a75a72"/>
  </linearGradient>
  <linearGradient id="teen" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#7d9393"/>
    <stop offset="45%" stop-color="#3d5050"/>
    <stop offset="100%" stop-color="#212f2f"/>
  </linearGradient>
  <linearGradient id="kid" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#ffd489"/>
    <stop offset="45%" stop-color="#f4a63a"/>
    <stop offset="100%" stop-color="#c1711a"/>
  </linearGradient>
  <linearGradient id="baby" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#ded2f5"/>
    <stop offset="45%" stop-color="#bcaae6"/>
    <stop offset="100%" stop-color="#8b74bd"/>
  </linearGradient>
  <linearGradient id="grandpa" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#c2ccb1"/>
    <stop offset="45%" stop-color="#8d9c7b"/>
    <stop offset="100%" stop-color="#5d6b50"/>
  </linearGradient>
  <filter id="soft" x="-25%" y="-25%" width="150%" height="160%">
    <feDropShadow dx="6" dy="10" stdDeviation="10"
                  flood-color="#3a2a18" flood-opacity="0.30"/>
  </filter>
  <filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur stdDeviation="6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="blur18"><feGaussianBlur stdDeviation="18"/></filter>
</defs>
''')

# ----------------------------------------------------------------------------
# Background: studio wall, arched backdrop, curtains, floor
# ----------------------------------------------------------------------------
add(f'<rect width="{W}" height="{H}" fill="#efe0c6"/>')
add(f'<rect width="{W}" height="820" fill="url(#wall)"/>')
add(f'<ellipse cx="700" cy="470" rx="470" ry="440" fill="url(#spot)"/>')

# arched canvas backdrop
add('''<path d="M 250 800 L 250 340 Q 250 150 470 140 L 930 140
       Q 1150 150 1150 340 L 1150 800 Z" fill="#e9d4b2"
       stroke="#d3b98f" stroke-width="4"/>''')
add('''<path d="M 250 800 L 250 340 Q 250 150 470 140 L 930 140
       Q 1150 150 1150 340 L 1150 800" fill="none"
       stroke="#c9ad82" stroke-width="2" opacity="0.6"/>''')

# left curtain
add('''<path d="M 0 0 L 200 0 Q 150 260 190 520 Q 220 700 170 820 L 0 820 Z"
       fill="url(#curtain)"/>''')
add('''<path d="M 90 0 Q 70 300 110 820" stroke="#0f2322" stroke-width="10"
       fill="none" opacity="0.55"/>''')
add('''<path d="M 150 0 Q 135 300 165 820" stroke="#3c6b68" stroke-width="6"
       fill="none" opacity="0.5"/>''')
# right curtain
add('''<path d="M 1400 0 L 1200 0 Q 1250 260 1210 520 Q 1180 700 1230 820
       L 1400 820 Z" fill="url(#curtain)"/>''')
add('''<path d="M 1310 0 Q 1330 300 1290 820" stroke="#0f2322"
       stroke-width="10" fill="none" opacity="0.55"/>''')
add('''<path d="M 1250 0 Q 1265 300 1235 820" stroke="#3c6b68"
       stroke-width="6" fill="none" opacity="0.5"/>''')
# curtain rod
add('<rect x="0" y="0" width="1400" height="16" fill="#7a5a3a"/>')
add('<circle cx="70" cy="14" r="18" fill="#a9814f"/>'
    '<circle cx="1330" cy="14" r="18" fill="#a9814f"/>')

# floor
add('<rect x="0" y="800" width="1400" height="200" fill="url(#floor)"/>')
add('<rect x="0" y="788" width="1400" height="22" fill="#5f4127"/>')
add('<rect x="0" y="800" width="1400" height="6" fill="#d9b17f" opacity="0.35"/>')
for i in range(9):
    x = 40 + i * 165
    add(f'<line x1="{x}" y1="806" x2="{x-120}" y2="1000" '
        f'stroke="#6e4a2a" stroke-width="2" opacity="0.35"/>')

# a framed abstract portrait on the wall + wall clock
add('<rect x="1052" y="250" width="120" height="150" rx="6" fill="#7a5a3a"/>')
add('<rect x="1062" y="260" width="100" height="130" rx="4" fill="#efe4cd"/>')
add('<circle cx="1112" cy="305" r="26" fill="#dd92a4"/>')
add('<rect x="1082" y="335" width="60" height="40" rx="4" fill="#4f76ad"/>')
add('<g transform="translate(300,250)">'
    '<circle r="44" fill="#7a5a3a"/><circle r="36" fill="#f5ecd8"/>'
    '<line x1="0" y1="0" x2="0" y2="-22" stroke="#3a2f22" stroke-width="5" stroke-linecap="round"/>'
    '<line x1="0" y1="0" x2="16" y2="10" stroke="#3a2f22" stroke-width="5" stroke-linecap="round"/>'
    '<circle r="4" fill="#3a2f22"/></g>')

# ----------------------------------------------------------------------------
# Ground shadows
# ----------------------------------------------------------------------------
for cx, rx, ry in [(380, 150, 26), (720, 150, 26), (1030, 120, 24),
                   (560, 110, 22), (1185, 70, 16), (165, 120, 20)]:
    add(f'<ellipse cx="{cx}" cy="824" rx="{rx}" ry="{ry}" fill="#3a2410" '
        f'opacity="0.30"/>')

# ============================================================================
# GRANDPA ROBOT -- dozing in an armchair, far left, slightly behind
# ============================================================================
add('<g transform="translate(150,790) scale(0.72)" filter="url(#soft)" opacity="0.98">')
# armchair
add('<rect x="-110" y="-300" width="220" height="300" rx="40" fill="#5a3f6b"/>')
add('<rect x="-92" y="-278" width="184" height="210" rx="28" fill="#75538c"/>')
add('<rect x="-140" y="-120" width="70" height="130" rx="26" fill="#4a3358"/>')
add('<rect x="70" y="-120" width="70" height="130" rx="26" fill="#4a3358"/>')
add('<rect x="-118" y="-20" width="236" height="30" rx="12" fill="#4a3358"/>')
# seated robot
add('<rect x="-56" y="-150" width="112" height="150" rx="34" fill="url(#grandpa)"/>')
add('<rect x="-40" y="-128" width="80" height="70" rx="14" fill="#a7b394" opacity="0.8"/>')
# outstretched legs
add('<rect x="-58" y="-42" width="94" height="34" rx="16" fill="url(#grandpa)" transform="rotate(6 -11 -25)"/>')
add('<rect x="-6" y="-42" width="94" height="34" rx="16" fill="url(#grandpa)" transform="rotate(-8 41 -25)"/>')
add('<ellipse cx="78" cy="-16" rx="30" ry="18" fill="#4d5a42"/>')
add('<ellipse cx="24" cy="-14" rx="30" ry="18" fill="#4d5a42"/>')
# hands on lap
add('<circle cx="-6" cy="-112" r="20" fill="#a7b394"/><circle cx="34" cy="-108" r="20" fill="#a7b394"/>')
# neck + head tilted back
add('<rect x="-20" y="-186" width="40" height="34" rx="12" fill="#7b8a68"/>')
add(f'<g transform="rotate(-12 0 -232)">')
add('<rect x="-58" y="-306" width="116" height="126" rx="34" fill="url(#grandpa)"/>')
add('<rect x="-44" y="-288" width="88" height="92" rx="22" fill="#a7b394"/>')
# closed eyes (sleeping arcs)
add('<path d="M -30 -252 q 12 12 24 0" stroke="#3c4632" stroke-width="5" fill="none" stroke-linecap="round"/>')
add('<path d="M 8 -252 q 12 12 24 0" stroke="#3c4632" stroke-width="5" fill="none" stroke-linecap="round"/>')
# open relaxed mouth
add('<ellipse cx="1" cy="-212" rx="13" ry="8" fill="#3c4632" opacity="0.7"/>')
# glasses
add('<circle cx="-17" cy="-248" r="16" fill="none" stroke="#4a4a52" stroke-width="4"/>'
    '<circle cx="21" cy="-248" r="16" fill="none" stroke="#4a4a52" stroke-width="4"/>'
    '<line x1="-1" y1="-248" x2="5" y2="-248" stroke="#4a4a52" stroke-width="4"/>')
# hair tuft / antenna
add('<line x1="-14" y1="-306" x2="-30" y2="-352" stroke="#7b8a68" stroke-width="8" stroke-linecap="round"/>')
add(f'<circle cx="-30" cy="-354" r="9" fill="#c2ccb1"/>')
add('</g>')
# sleeping puffs
add('<g fill="none" stroke="#f5ecd8" stroke-width="6" opacity="0.85">'
    '<path d="M 60 -300 q 18 -14 0 -28"/>'
    '<path d="M 84 -336 q 24 -18 0 -38"/>'
    '<path d="M 112 -382 q 30 -22 0 -48"/></g>')
add('</g>')

# ============================================================================
# DAD ROBOT -- stiff, boxy, moustache, one hovering arm
# ============================================================================
add('<g transform="translate(380,820)" filter="url(#soft)">')
# legs & feet
add('<rect x="-58" y="-196" width="46" height="196" rx="18" fill="#3c5a86"/>')
add('<rect x="12" y="-196" width="46" height="196" rx="18" fill="#3c5a86"/>')
add('<rect x="-70" y="-28" width="64" height="32" rx="14" fill="#2c4772"/>')
add('<rect x="6" y="-28" width="64" height="32" rx="14" fill="#2c4772"/>')
add('<rect x="-74" y="-224" width="148" height="44" rx="20" fill="#3c5a86"/>')
# torso
add('<rect x="-82" y="-438" width="164" height="236" rx="28" fill="url(#dad)"/>')
add('<rect x="-50" y="-388" width="100" height="96" rx="16" fill="#7fa0d0" opacity="0.85"/>')
add('<circle cx="-24" cy="-352" r="10" fill="#f2d24b"/>'
    '<circle cx="6" cy="-352" r="10" fill="#e2574f"/>'
    '<circle cx="36" cy="-352" r="10" fill="#5ac37a"/>')
add('<rect x="-30" y="-320" width="60" height="10" rx="5" fill="#2c4772" opacity="0.5"/>')
add(rivets(-66, -414, 66, -414, 6))
# shoulders
add('<circle cx="-82" cy="-408" r="26" fill="#5f83bb"/>')
add('<circle cx="82" cy="-408" r="26" fill="#5f83bb"/>')
# left arm straight down, fist clenched
add('<rect x="-124" y="-402" width="38" height="160" rx="17" fill="#4f76ad"/>')
add('<circle cx="-105" cy="-238" r="25" fill="#84a3d4"/>')
add(rivets(-114, -380, -114, -270, 3, 2.5))
# right arm reaching toward mum but NOT touching (awkward gap)
add('<path d="M 82 -408 Q 168 -420 214 -374" stroke="#4f76ad" stroke-width="36" '
    'fill="none" stroke-linecap="round"/>')
add('<circle cx="232" cy="-360" r="26" fill="#84a3d4"/>')
add('<circle cx="232" cy="-360" r="12" fill="#5f83bb" opacity="0.6"/>')
# neck + bow tie
add('<rect x="-24" y="-470" width="48" height="40" rx="14" fill="#3c5a86"/>')
add('<path d="M -4 -458 L -40 -476 L -40 -440 Z" fill="#e2574f"/>'
    '<path d="M 4 -458 L 40 -476 L 40 -440 Z" fill="#e2574f"/>'
    '<circle cx="0" cy="-458" r="8" fill="#b83b34"/>')
# head
add('<rect x="-70" y="-604" width="140" height="146" rx="30" fill="url(#dad)"/>')
add('<rect x="-54" y="-582" width="108" height="104" rx="20" fill="#8fb0d8"/>')
# ears / bolts
add(bolt(-70, -530, 12))
add(bolt(70, -530, 12))
# antennae
add('<line x1="-30" y1="-604" x2="-52" y2="-676" stroke="#3c5a86" stroke-width="9" stroke-linecap="round"/>')
add('<circle cx="-52" cy="-680" r="12" fill="#f2d24b"/>')
add('<line x1="30" y1="-604" x2="56" y2="-670" stroke="#3c5a86" stroke-width="9" stroke-linecap="round"/>')
add('<circle cx="56" cy="-674" r="12" fill="#e2574f"/>')
# stern eyes (looking off to the left, away from mum)
add('<circle cx="-26" cy="-534" r="17" fill="#eef5ff"/>'
    '<circle cx="26" cy="-534" r="17" fill="#eef5ff"/>')
add('<circle cx="-33" cy="-532" r="7" fill="#1b2b44"/>'
    '<circle cx="19" cy="-532" r="7" fill="#1b2b44"/>')
add('<line x1="-46" y1="-560" x2="-8" y2="-568" stroke="#2c4772" stroke-width="7" stroke-linecap="round"/>')
add('<line x1="8" y1="-566" x2="46" y2="-560" stroke="#2c4772" stroke-width="7" stroke-linecap="round"/>')
# moustache
add('<path d="M -34 -504 Q -18 -520 0 -506 Q 18 -520 34 -504 '
    'Q 18 -494 0 -498 Q -18 -494 -34 -504 Z" fill="#42506b"/>')
add('<rect x="-12" y="-494" width="24" height="7" rx="3" fill="#2c4772"/>')
# a stiff medal / badge
add('<circle cx="56" cy="-300" r="14" fill="#f2d24b"/>'
    '<circle cx="56" cy="-300" r="7" fill="#c9a520"/>')
add('</g>')

# ============================================================================
# MUM ROBOT -- elegant, leaning away, cradling baby
# ============================================================================
add('<g transform="translate(735,820) rotate(4)" filter="url(#soft)">')
# skirt / lower body
add('<path d="M -88 -230 L 88 -230 L 66 0 Q 0 14 -66 0 Z" fill="url(#mom)"/>')
add('<path d="M -70 -80 Q 0 -66 70 -80" stroke="#a75a72" stroke-width="4" fill="none" opacity="0.6"/>')
# torso
add('<rect x="-66" y="-424" width="132" height="216" rx="28" fill="url(#mom)"/>')
add('<rect x="-38" y="-386" width="76" height="76" rx="14" fill="#f6c2c8" opacity="0.9"/>')
add('<circle cx="0" cy="-348" r="18" fill="#d98aa0"/>'
    '<circle cx="0" cy="-348" r="8" fill="#f7e3a1"/>')
add(rivets(-50, -404, 50, -404, 5))
# shoulders
add('<circle cx="-66" cy="-400" r="20" fill="#dd92a4"/>')
add('<circle cx="66" cy="-400" r="20" fill="#dd92a4"/>')
# left arm (toward dad) hangs defensively, hand on skirt
add('<path d="M -66 -400 Q -104 -340 -96 -250" stroke="#dd92a4" stroke-width="30" '
    'fill="none" stroke-linecap="round"/>')
add('<circle cx="-98" cy="-238" r="19" fill="#f6c2c8"/>')
# right arm cradling baby
add('<path d="M 66 -400 Q 118 -344 104 -250" stroke="#dd92a4" stroke-width="32" '
    'fill="none" stroke-linecap="round"/>')
# neck + head (tilted)
add('<rect x="-22" y="-458" width="44" height="42" rx="14" fill="#c07e92"/>')
add('<g transform="rotate(-8 0 -540)">')
add('<rect x="-58" y="-592" width="116" height="134" rx="34" fill="url(#mom)"/>')
add('<rect x="-44" y="-572" width="88" height="96" rx="26" fill="#f6c2c8"/>')
# swept hair plate
add('<path d="M -58 -560 Q -78 -606 -40 -608 Q 10 -620 52 -596 Q 66 -576 58 -552 '
    'Q 30 -578 -10 -574 Q -40 -572 -58 -560 Z" fill="#c07e92"/>')
# flower antenna
add('<line x1="-18" y1="-592" x2="-30" y2="-650" stroke="#4f7a52" stroke-width="7" stroke-linecap="round"/>')
for a in range(5):
    import math
    ang = a * 72
    px = -30 + 16 * math.cos(math.radians(ang))
    py = -656 + 16 * math.sin(math.radians(ang))
    add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="10" fill="#f2a0bb"/>')
add('<circle cx="-30" cy="-656" r="9" fill="#f7e3a1"/>')
# half-lidded eyes, gazing down at baby
add('<circle cx="-24" cy="-524" r="16" fill="#fdf3e0"/>'
    '<circle cx="24" cy="-524" r="16" fill="#fdf3e0"/>')
add('<circle cx="-30" cy="-516" r="7" fill="#3a2230"/>'
    '<circle cx="18" cy="-516" r="7" fill="#3a2230"/>')
add('<path d="M -40 -524 Q -24 -516 -8 -524 Z" fill="#dd92a4"/>'
    '<path d="M 8 -524 Q 24 -516 40 -524 Z" fill="#dd92a4"/>')
add('<path d="M -8 -500 Q 0 -492 8 -500" stroke="#a75a72" stroke-width="4" '
    'fill="none" stroke-linecap="round"/>')
add(bolt(-58, -528, 10))
add(bolt(58, -528, 10))
# little pearl earrings
add('<circle cx="-58" cy="-500" r="7" fill="#f7e3a1"/>'
    '<circle cx="58" cy="-500" r="7" fill="#f7e3a1"/>')
add('</g>')

# ---- BABY ROBOT nestled in mum's right arm ----
add('<g transform="translate(112,-258) rotate(-6)">')
# swaddle
add('<path d="M -46 34 Q -56 -10 -34 -34 L 34 -34 Q 56 -10 46 34 Z" fill="#f0b8bf"/>')
add('<path d="M -46 34 Q 0 46 46 34" stroke="#dd92a4" stroke-width="4" fill="none"/>')
# body
add('<rect x="-34" y="-36" width="68" height="80" rx="26" fill="url(#baby)"/>')
# head
add('<rect x="-40" y="-124" width="80" height="86" rx="32" fill="url(#baby)"/>')
add('<rect x="-30" y="-110" width="60" height="58" rx="22" fill="#ded2f5"/>')
# wide startled eyes
add('<circle cx="-14" cy="-84" r="12" fill="#ffffff"/>'
    '<circle cx="16" cy="-84" r="12" fill="#ffffff"/>')
add('<circle cx="-13" cy="-82" r="4.5" fill="#3a2f56"/>'
    '<circle cx="17" cy="-82" r="4.5" fill="#3a2f56"/>')
# o-mouth + pacifier
add('<ellipse cx="1" cy="-58" rx="6" ry="7" fill="#5a4a7a"/>')
add('<circle cx="1" cy="-52" r="9" fill="#f2a0bb"/><circle cx="1" cy="-52" r="4" fill="#d9789a"/>')
# reaching arm toward dad with door
add('<path d="M -30 -22 Q -62 -36 -74 -60" stroke="#bcaae6" stroke-width="16" '
    'fill="none" stroke-linecap="round"/>')
add('<circle cx="-76" cy="-64" r="10" fill="#ded2f5"/>')
# aerial curl
add('<path d="M 6 -124 q 10 -14 22 -8 q 12 6 4 16" stroke="#8b74bd" stroke-width="5" '
    'fill="none" stroke-linecap="round"/>')
add('</g>')
add('</g>')

# ============================================================================
# TEEN ROBOT -- slouched, cap askew, arms crossed, glaring away
# ============================================================================
add('<g transform="translate(1030,820) rotate(6)" filter="url(#soft)">')
# long legs
add('<rect x="-42" y="-320" width="30" height="320" rx="14" fill="#2b3a3a"/>')
add('<rect x="12" y="-320" width="30" height="320" rx="14" fill="#2b3a3a"/>')
# foot flat, foot tapping
add('<rect x="-58" y="-26" width="58" height="28" rx="12" fill="#182222"/>')
add('<g transform="rotate(-16 27 -12)"><rect x="6" y="-24" width="58" height="28" rx="12" fill="#182222"/></g>')
add('<path d="M 62 -30 q 22 -6 30 10" stroke="#7d9393" stroke-width="4" '
    'fill="none" stroke-linecap="round" opacity="0.7"/>')
# torso
add('<rect x="-58" y="-586" width="116" height="280" rx="30" fill="url(#teen)"/>')
# hoodie strings / pocket
add('<path d="M -30 -556 L -30 -486 M 30 -556 L 30 -486" stroke="#5a7070" stroke-width="5" stroke-linecap="round"/>')
add('<rect x="-40" y="-460" width="80" height="52" rx="12" fill="#2b3a3a" opacity="0.7"/>')
add(rivets(-36, -560, 36, -560, 5, 2.5))
# crossed arms
add('<path d="M -58 -520 Q 10 -492 60 -470" stroke="#334545" stroke-width="30" '
    'fill="none" stroke-linecap="round"/>')
add('<path d="M 58 -520 Q -10 -492 -60 -470" stroke="#3d5050" stroke-width="30" '
    'fill="none" stroke-linecap="round"/>')
# phone peeking out, glowing (no text)
add('<g transform="translate(34,-500) rotate(18)">'
    '<rect x="-16" y="-26" width="32" height="52" rx="6" fill="#101818"/>'
    '<rect x="-12" y="-22" width="24" height="44" rx="4" fill="#5ad0d8" filter="url(#glow)"/>'
    '<rect x="-12" y="-22" width="24" height="16" rx="4" fill="#bff6f8"/></g>')
# headphones
add('<path d="M -62 -624 Q 0 -704 62 -624" stroke="#1b2727" stroke-width="12" '
    'fill="none" stroke-linecap="round"/>')
add('<rect x="-74" y="-620" width="26" height="44" rx="10" fill="#e2574f"/>'
    '<rect x="48" y="-620" width="26" height="44" rx="10" fill="#e2574f"/>')
# neck + head
add('<rect x="-20" y="-618" width="40" height="40" rx="12" fill="#2b3a3a"/>')
add('<g transform="rotate(-6 0 -700)">')
add('<rect x="-52" y="-720" width="104" height="150" rx="28" fill="url(#teen)"/>')
add('<rect x="-40" y="-702" width="80" height="92" rx="20" fill="#5a7070"/>')
# annoyed eyes -- both cutting hard to the far left
add('<circle cx="-20" cy="-664" r="14" fill="#d9efef"/>'
    '<circle cx="20" cy="-664" r="14" fill="#d9efef"/>')
add('<circle cx="-31" cy="-664" r="6" fill="#12201f"/>'
    '<circle cx="9" cy="-664" r="6" fill="#12201f"/>')
add('<path d="M -34 -684 L -6 -678" stroke="#182222" stroke-width="6" stroke-linecap="round"/>')
add('<path d="M 6 -680 L 34 -688" stroke="#182222" stroke-width="6" stroke-linecap="round"/>')
add('<path d="M -8 -634 Q 0 -628 8 -636" stroke="#182222" stroke-width="4" '
    'fill="none" stroke-linecap="round"/>')
# baseball cap, brim to the side
add('<path d="M -54 -706 Q 0 -760 54 -706 Q 20 -722 -54 -706 Z" fill="#c2453e"/>')
add('<path d="M -58 -706 Q -110 -712 -128 -688 Q -84 -680 -40 -690 Z" fill="#e2574f"/>')
add('<circle cx="0" cy="-752" r="7" fill="#8f2f2a"/>')
# cheek pimple-like bolt for teen awkwardness
add(bolt(30, -636, 5, "#a94b45", "#e08a84"))
add('</g>')
add('</g>')

# ============================================================================
# ROBOT DOG -- oblivious, sitting by the teen, tail wagging
# ============================================================================
add('<g transform="translate(1215,822) rotate(-4)" filter="url(#soft)">')
# body
add('<rect x="-54" y="-96" width="108" height="70" rx="30" fill="#c98a4a"/>')
# legs
add('<rect x="-40" y="-40" width="20" height="42" rx="9" fill="#a86f38"/>'
    '<rect x="20" y="-40" width="20" height="42" rx="9" fill="#a86f38"/>')
add('<ellipse cx="-30" cy="0" rx="16" ry="9" fill="#7f5226"/>'
    '<ellipse cx="30" cy="0" rx="16" ry="9" fill="#7f5226"/>')
# tail wagging with motion arcs
add('<path d="M 50 -84 q 30 -6 34 -34" stroke="#c98a4a" stroke-width="14" '
    'fill="none" stroke-linecap="round"/>')
add('<path d="M 74 -92 q 22 -14 12 -34" stroke="#7f5226" stroke-width="3" '
    'fill="none" opacity="0.6"/>')
# head
add('<rect x="-24" y="-158" width="84" height="76" rx="30" fill="#c98a4a"/>')
add('<rect x="-14" y="-146" width="64" height="50" rx="20" fill="#e0ab6f"/>')
# snout + tongue
add('<ellipse cx="42" cy="-116" rx="22" ry="16" fill="#e0ab6f"/>')
add('<circle cx="42" cy="-124" r="7" fill="#3a2a1a"/>')
add('<path d="M 34 -106 q 8 16 18 6" fill="#e2574f"/>')
# eyes
add('<circle cx="-4" cy="-136" r="9" fill="#fff"/><circle cx="22" cy="-136" r="9" fill="#fff"/>')
add('<circle cx="-2" cy="-135" r="4" fill="#2a1c10"/><circle cx="24" cy="-135" r="4" fill="#2a1c10"/>')
# antenna ears
add('<line x1="0" y1="-156" x2="-12" y2="-190" stroke="#a86f38" stroke-width="6" stroke-linecap="round"/>'
    '<circle cx="-12" cy="-192" r="7" fill="#e2574f"/>')
add('<line x1="44" y1="-158" x2="56" y2="-192" stroke="#a86f38" stroke-width="6" stroke-linecap="round"/>'
    '<circle cx="56" cy="-194" r="7" fill="#e2574f"/>')
add('</g>')

# ============================================================================
# KID ROBOT -- sitting on the floor, waving wildly, huge grin
# ============================================================================
add('<g transform="translate(556,884) rotate(-7)" filter="url(#soft)">')
# splayed legs
add('<rect x="-72" y="-70" width="120" height="34" rx="17" fill="#d9891f" transform="rotate(18 -12 -53)"/>')
add('<rect x="-42" y="-66" width="120" height="34" rx="17" fill="#d9891f" transform="rotate(-16 18 -49)"/>')
add('<ellipse cx="-92" cy="-16" rx="26" ry="16" fill="#a85c15"/>')
add('<ellipse cx="76" cy="-4" rx="26" ry="16" fill="#a85c15"/>')
# body
add('<rect x="-62" y="-186" width="124" height="126" rx="34" fill="url(#kid)"/>')
add('<rect x="-38" y="-158" width="76" height="60" rx="16" fill="#ffd489"/>')
add('<circle cx="-18" cy="-128" r="7" fill="#f2d24b"/>'
    '<circle cx="18" cy="-128" r="7" fill="#e2574f"/>')
# left arm planted on floor
add('<path d="M -60 -150 Q -96 -110 -92 -56" stroke="#f4a63a" stroke-width="28" '
    'fill="none" stroke-linecap="round"/>')
add('<circle cx="-92" cy="-48" r="18" fill="#ffd489"/>')
# right arm waving high with motion lines
add('<path d="M 60 -162 Q 104 -206 96 -274" stroke="#f4a63a" stroke-width="28" '
    'fill="none" stroke-linecap="round"/>')
add('<circle cx="96" cy="-286" r="20" fill="#ffd489"/>')
for dx, dy in [(-26, -22), (-6, -34), (16, -24)]:
    add(f'<path d="M {96+dx} { -286+dy} q 54 -18 108 0" stroke="#e0a44a" '
        f'stroke-width="4" fill="none" opacity="0.7"/>')
# neck + big head
add('<rect x="-22" y="-216" width="44" height="36" rx="12" fill="#d9891f"/>')
add('<rect x="-70" y="-356" width="140" height="148" rx="44" fill="url(#kid)"/>')
add('<rect x="-56" y="-338" width="112" height="112" rx="36" fill="#ffd489"/>')
# big happy eyes looking up
add('<ellipse cx="-26" cy="-292" rx="18" ry="20" fill="#fff"/>'
    '<ellipse cx="26" cy="-292" rx="18" ry="20" fill="#fff"/>')
add('<circle cx="-24" cy="-298" r="8" fill="#2a1c10"/><circle cx="28" cy="-298" r="8" fill="#2a1c10"/>')
add('<circle cx="-22" cy="-302" r="3" fill="#fff"/><circle cx="30" cy="-302" r="3" fill="#fff"/>')
# huge open grin
add('<path d="M -34 -258 Q 0 -214 34 -258 Q 0 -244 -34 -258 Z" fill="#3a2418"/>')
add('<path d="M -22 -252 Q 0 -222 22 -252 Q 0 -244 -22 -252 Z" fill="#e2574f"/>')
# cheek rivets
add(bolt(-48, -278, 6, "#e0a44a", "#ffd489"))
add(bolt(48, -278, 6, "#e0a44a", "#ffd489"))
# spring antenna, bent
add('<path d="M -6 -356 q -10 -22 8 -30 q 18 -8 6 -30 q -12 -22 12 -32" '
    'stroke="#a85c15" stroke-width="6" fill="none" stroke-linecap="round"/>')
add('<circle cx="24" cy="-450" r="13" fill="#e2574f"/>')
add('</g>')

# ============================================================================
# Foreground vignette & dust motes for that forced studio-photo feel
# ============================================================================
add(f'<rect width="{W}" height="{H}" fill="none" stroke="#2a1c10" '
    f'stroke-width="60" opacity="0.10"/>')
for x, y, r in [(120,180,5),(240,420,4),(980,180,4),(1300,360,5),
                (640,120,4),(420,120,3),(1140,620,3),(60,640,4)]:
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff7e6" opacity="0.55"/>')

add('</svg>')

os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
with open(OUT, "w") as f:
    f.write("\n".join(S))
print("wrote", os.path.abspath(OUT), len("\n".join(S)), "bytes")
