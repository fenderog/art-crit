#!/usr/bin/env python3
"""
Generator for 'Awkward Robot Family Portrait' SVG.
Produces ./output/awkward_robot_family_portrait.svg (strictly no text/letters/numbers).
"""

import math
import os


def create_defs():
    return """
  <defs>
    <!-- Drop Shadows & Glow Filters -->
    <filter id="dropShadow" x="-15%" y="-15%" width="135%" height="135%">
      <feDropShadow dx="0" dy="10" stdDeviation="8" flood-color="#070510" flood-opacity="0.6"/>
    </filter>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="5" stdDeviation="4" flood-color="#070510" flood-opacity="0.48"/>
    </filter>
    <filter id="tightShadow" x="-15%" y="-15%" width="130%" height="130%">
      <feDropShadow dx="2" dy="4" stdDeviation="2.5" flood-color="#05040a" flood-opacity="0.65"/>
    </filter>
    <filter id="glowCyan" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="glowWarm" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="blurSoft" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="24"/>
    </filter>
    <filter id="blurMed" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="9"/>
    </filter>

    <!-- Studio Wall & Floor Gradients -->
    <linearGradient id="studioWall" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#12101b"/>
      <stop offset="70%" stop-color="#1c1829"/>
      <stop offset="100%" stop-color="#100d19"/>
    </linearGradient>
    <radialGradient id="studioFloor" cx="50%" cy="20%" r="75%">
      <stop offset="0%" stop-color="#3a2d44"/>
      <stop offset="50%" stop-color="#21192b"/>
      <stop offset="100%" stop-color="#0b0812"/>
    </radialGradient>

    <!-- 1980s Sears / Olan Mills Backdrop Gradients -->
    <radialGradient id="backdropBase" cx="52%" cy="40%" r="68%">
      <stop offset="0%" stop-color="#215573"/>
      <stop offset="38%" stop-color="#1e315c"/>
      <stop offset="72%" stop-color="#271740"/>
      <stop offset="100%" stop-color="#130b24"/>
    </radialGradient>
    <radialGradient id="backdropWarmCloud" cx="62%" cy="34%" r="46%">
      <stop offset="0%" stop-color="#a83b6f" stop-opacity="0.58"/>
      <stop offset="50%" stop-color="#612361" stop-opacity="0.32"/>
      <stop offset="100%" stop-color="#1d1135" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="backdropTealCloud" cx="30%" cy="46%" r="48%">
      <stop offset="0%" stop-color="#28a4a9" stop-opacity="0.48"/>
      <stop offset="55%" stop-color="#18516e" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#121c38" stop-opacity="0"/>
    </radialGradient>

    <!-- Retro Laser Gradients -->
    <linearGradient id="laserCyan" x1="0" y1="1" x2="1" y2="0">
      <stop offset="0%" stop-color="#00f2fe" stop-opacity="0.05"/>
      <stop offset="50%" stop-color="#4facfe" stop-opacity="0.78"/>
      <stop offset="85%" stop-color="#b8f9ff" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.2"/>
    </linearGradient>
    <linearGradient id="laserMagenta" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ff0844" stop-opacity="0.1"/>
      <stop offset="50%" stop-color="#ff4e9b" stop-opacity="0.82"/>
      <stop offset="90%" stop-color="#ffb8d9" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.1"/>
    </linearGradient>
    <linearGradient id="laserGold" x1="0" y1="1" x2="1" y2="0">
      <stop offset="0%" stop-color="#f6d365" stop-opacity="0.05"/>
      <stop offset="55%" stop-color="#fda085" stop-opacity="0.72"/>
      <stop offset="90%" stop-color="#fff3b0" stop-opacity="0.92"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.1"/>
    </linearGradient>

    <!-- Velvet Settee Gradients -->
    <linearGradient id="velvetCrimson" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#a61f3d"/>
      <stop offset="40%" stop-color="#7d122b"/>
      <stop offset="85%" stop-color="#4a0717"/>
      <stop offset="100%" stop-color="#2b030c"/>
    </linearGradient>
    <radialGradient id="velvetTuft" cx="40%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#c43152"/>
      <stop offset="60%" stop-color="#80132c"/>
      <stop offset="100%" stop-color="#3c0512"/>
    </radialGradient>
    <linearGradient id="giltWood" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f5ca6e"/>
      <stop offset="35%" stop-color="#c98e2e"/>
      <stop offset="70%" stop-color="#805210"/>
      <stop offset="100%" stop-color="#4a2c04"/>
    </linearGradient>

    <!-- DAD BOT: 1970s Walnut & Brass Console Gradients -->
    <linearGradient id="dadBrass" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#fce5a2"/>
      <stop offset="28%" stop-color="#dba84a"/>
      <stop offset="65%" stop-color="#9c6c1f"/>
      <stop offset="90%" stop-color="#613f0a"/>
      <stop offset="100%" stop-color="#b8852e"/>
    </linearGradient>
    <linearGradient id="dadCreamSteel" x1="0" y1="0" x2="1" y2="0.8">
      <stop offset="0%" stop-color="#f7efe0"/>
      <stop offset="35%" stop-color="#e0d2b8"/>
      <stop offset="75%" stop-color="#ab9a7e"/>
      <stop offset="100%" stop-color="#756750"/>
    </linearGradient>
    <linearGradient id="dadWalnut" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#824b2b"/>
      <stop offset="30%" stop-color="#63351b"/>
      <stop offset="65%" stop-color="#4a2510"/>
      <stop offset="100%" stop-color="#2e1406"/>
    </linearGradient>
    <linearGradient id="chromeGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="22%" stop-color="#dfe7f0"/>
      <stop offset="48%" stop-color="#8d9ba8"/>
      <stop offset="55%" stop-color="#525e6b"/>
      <stop offset="78%" stop-color="#bac6d2"/>
      <stop offset="100%" stop-color="#6b7885"/>
    </linearGradient>
    <linearGradient id="darkPipe" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#727d8a"/>
      <stop offset="30%" stop-color="#9eaab8"/>
      <stop offset="65%" stop-color="#48515c"/>
      <stop offset="100%" stop-color="#262c33"/>
    </linearGradient>

    <!-- MOM BOT: 1950s Atomic Mint-Turquoise Enamel & Copper Coils -->
    <linearGradient id="momMint" x1="0.1" y1="0" x2="0.9" y2="1">
      <stop offset="0%" stop-color="#c2fff6"/>
      <stop offset="25%" stop-color="#64ded0"/>
      <stop offset="62%" stop-color="#29a195"/>
      <stop offset="90%" stop-color="#11635d"/>
      <stop offset="100%" stop-color="#40b8a9"/>
    </linearGradient>
    <linearGradient id="momCopperCoil" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#783416"/>
      <stop offset="25%" stop-color="#e68653"/>
      <stop offset="45%" stop-color="#ffd4b5"/>
      <stop offset="70%" stop-color="#ba5625"/>
      <stop offset="100%" stop-color="#521d07"/>
    </linearGradient>
    <radialGradient id="pearlBearing" cx="35%" cy="30%" r="65%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="35%" stop-color="#e3f6ff"/>
      <stop offset="75%" stop-color="#7da0b8"/>
      <stop offset="100%" stop-color="#324759"/>
    </radialGradient>

    <!-- TEEN BOT: 1990s Matte Charcoal & Translucent Cyber-Purple -->
    <linearGradient id="teenCharcoal" x1="0" y1="0" x2="1" y2="0.5">
      <stop offset="0%" stop-color="#555a70"/>
      <stop offset="32%" stop-color="#373a4d"/>
      <stop offset="72%" stop-color="#20222e"/>
      <stop offset="100%" stop-color="#12131c"/>
    </linearGradient>
    <linearGradient id="teenTransPurple" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#bf55ff" stop-opacity="0.82"/>
      <stop offset="50%" stop-color="#731cc2" stop-opacity="0.76"/>
      <stop offset="100%" stop-color="#300759" stop-opacity="0.88"/>
    </linearGradient>
    <linearGradient id="teenVisor" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#29083d"/>
      <stop offset="50%" stop-color="#140321"/>
      <stop offset="100%" stop-color="#3b0c59"/>
    </linearGradient>

    <!-- MIDDLE-CHILD NERD BOT: 1980s Canary Yellow & Cobalt Blue -->
    <linearGradient id="nerdYellow" x1="0.1" y1="0" x2="0.9" y2="1">
      <stop offset="0%" stop-color="#fff6a1"/>
      <stop offset="30%" stop-color="#ffd629"/>
      <stop offset="72%" stop-color="#d99800"/>
      <stop offset="100%" stop-color="#8f5a00"/>
    </linearGradient>
    <linearGradient id="nerdBlue" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#63afff"/>
      <stop offset="35%" stop-color="#246ee3"/>
      <stop offset="75%" stop-color="#0f429c"/>
      <stop offset="100%" stop-color="#072159"/>
    </linearGradient>

    <!-- TODDLER BOT: Coral-Orange & Brushed Steel -->
    <linearGradient id="toddlerCoral" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ffb091"/>
      <stop offset="30%" stop-color="#ff6138"/>
      <stop offset="75%" stop-color="#cc2c0c"/>
      <stop offset="100%" stop-color="#781200"/>
    </linearGradient>
    <linearGradient id="toddlerDiaper" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f7fbff"/>
      <stop offset="40%" stop-color="#cbd8e6"/>
      <stop offset="80%" stop-color="#8596a8"/>
      <stop offset="100%" stop-color="#526070"/>
    </linearGradient>

    <!-- GRANDPA BOT: Antique Cast-Iron & Tarnished Copper Boiler -->
    <linearGradient id="grandpaIron" x1="0.1" y1="0" x2="0.9" y2="1">
      <stop offset="0%" stop-color="#706d6a"/>
      <stop offset="32%" stop-color="#4a4745"/>
      <stop offset="70%" stop-color="#2c2928"/>
      <stop offset="100%" stop-color="#171514"/>
    </linearGradient>
    <linearGradient id="grandpaCopper" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#de9164"/>
      <stop offset="35%" stop-color="#a35830"/>
      <stop offset="70%" stop-color="#663216"/>
      <stop offset="90%" stop-color="#3e5c4b"/>
      <stop offset="100%" stop-color="#2e1508"/>
    </linearGradient>

    <!-- PET BOT: Brushed Silver & Warm Pewter -->
    <linearGradient id="petSilver" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f5f8fc"/>
      <stop offset="30%" stop-color="#bcc8d6"/>
      <stop offset="68%" stop-color="#738291"/>
      <stop offset="100%" stop-color="#3c4652"/>
    </linearGradient>

    <!-- Optics & Glass Gradients -->
    <radialGradient id="cyanLens" cx="38%" cy="35%" r="62%">
      <stop offset="0%" stop-color="#e6ffff"/>
      <stop offset="28%" stop-color="#38f2ff"/>
      <stop offset="65%" stop-color="#0077a8"/>
      <stop offset="92%" stop-color="#002b47"/>
      <stop offset="100%" stop-color="#001221"/>
    </radialGradient>
    <radialGradient id="amberLens" cx="38%" cy="35%" r="62%">
      <stop offset="0%" stop-color="#fff8d6"/>
      <stop offset="28%" stop-color="#ffbe2e"/>
      <stop offset="68%" stop-color="#c95b00"/>
      <stop offset="92%" stop-color="#591c00"/>
      <stop offset="100%" stop-color="#290a00"/>
    </radialGradient>
    <radialGradient id="redNose" cx="35%" cy="30%" r="65%">
      <stop offset="0%" stop-color="#ffd6d6"/>
      <stop offset="30%" stop-color="#ff2a2a"/>
      <stop offset="75%" stop-color="#9e0000"/>
      <stop offset="100%" stop-color="#420000"/>
    </radialGradient>
    <radialGradient id="oilSlick" cx="45%" cy="40%" r="60%">
      <stop offset="0%" stop-color="#2c2040"/>
      <stop offset="45%" stop-color="#162630"/>
      <stop offset="75%" stop-color="#120d1c"/>
      <stop offset="100%" stop-color="#07050a"/>
    </radialGradient>
    <radialGradient id="vignetteGrad" cx="50%" cy="48%" r="68%">
      <stop offset="66%" stop-color="#000000" stop-opacity="0"/>
      <stop offset="91%" stop-color="#06030d" stop-opacity="0.36"/>
      <stop offset="100%" stop-color="#020105" stop-opacity="0.76"/>
    </radialGradient>
  </defs>
"""


def bezier_point(t, p0, p1, p2):
    u = 1.0 - t
    x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
    y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
    return x, y


def bezier_tangent(t, p0, p1, p2):
    dx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
    dy = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
    return math.degrees(math.atan2(dy, dx))


def draw_segmented_limb(p0, p1, p2, num_segs, width, seg_thick=20, grad="url(#chromeGrad)", dark_ring="#1b1c26"):
    """Draws a tightly packed curved accordion/segmented robotic limb along a quadratic Bezier curve."""
    parts = []
    parts.append(
        f'<path d="M {p0[0]:.1f} {p0[1]:.1f} Q {p1[0]:.1f} {p1[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}" '
        f'fill="none" stroke="{dark_ring}" stroke-width="{width * 0.82:.1f}" stroke-linecap="round"/>'
    )
    for i in range(num_segs):
        t = (i + 0.5) / num_segs
        cx, cy = bezier_point(t, p0, p1, p2)
        ang = bezier_tangent(t, p0, p1, p2)
        rx = seg_thick / 2.0
        ry = width / 2.0
        parts.append(
            f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({ang:.1f})">'
            f'<rect x="{-rx:.1f}" y="{-ry:.1f}" width="{seg_thick:.1f}" height="{width:.1f}" rx="{rx * 0.85:.1f}" '
            f'fill="{grad}" stroke="#16151f" stroke-width="2.2"/>'
            f'<line x1="{-rx * 0.3:.1f}" y1="{-ry + 4:.1f}" x2="{-rx * 0.3:.1f}" y2="{ry - 4:.1f}" '
            f'stroke="#ffffff" stroke-opacity="0.48" stroke-width="2.2" stroke-linecap="round"/>'
            f'</g>'
        )
    return "\n".join(parts)


def draw_hydraulic_cylinder(p0, p1, w1, w2, grad="url(#teenCharcoal)", collar_grad="url(#chromeGrad)", accent_col=None):
    """Draws a solid 3D tapered armored/hydraulic limb segment between p0 and p1 with end collars and specular highlight."""
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    length = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(dy, dx))
    r1 = w1 / 2.0
    r2 = w2 / 2.0
    accent_svg = ""
    if accent_col:
        accent_svg = f'<line x1="{length*0.15:.1f}" y1="0" x2="{length*0.85:.1f}" y2="0" stroke="{accent_col}" stroke-width="3.5" stroke-linecap="round"/>'
    return f"""
    <g transform="translate({p0[0]:.1f},{p0[1]:.1f}) rotate({ang:.1f})">
      <path d="M 0 {-r1:.1f} L {length:.1f} {-r2:.1f} L {length:.1f} {r2:.1f} L 0 {r1:.1f} Z"
            fill="{grad}" stroke="#101118" stroke-width="2.8" stroke-linejoin="round"/>
      <line x1="6" y1="{-r1*0.52:.1f}" x2="{length-6:.1f}" y2="{-r2*0.52:.1f}"
            stroke="#ffffff" stroke-opacity="0.35" stroke-width="3" stroke-linecap="round"/>
      {accent_svg}
      <rect x="-4" y="{-r1*1.12:.1f}" width="14" height="{w1*1.12:.1f}" rx="4" fill="{collar_grad}" stroke="#101118" stroke-width="2"/>
      <rect x="{length-10:.1f}" y="{-r2*1.12:.1f}" width="14" height="{w2*1.12:.1f}" rx="4" fill="{collar_grad}" stroke="#101118" stroke-width="2"/>
    </g>
    """


def draw_rivets(pts, r=4.5, fill="url(#chromeGrad)"):
    out = []
    for x, y in pts:
        out.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="#181520" stroke-width="1.6"/>'
            f'<circle cx="{x - r*0.28:.1f}" cy="{y - r*0.28:.1f}" r="{r*0.32:.1f}" fill="#ffffff" fill-opacity="0.75"/>'
        )
    return "\n".join(out)


def draw_gauge(cx, cy, r, needle_deg=-35, rim_grad="url(#dadBrass)", face_color="#f7eed7"):
    """Draws an analog pressure/voltage dial gauge with tick marks ONLY (strictly no numbers/text)."""
    ticks = []
    for deg in range(-135, 136, 27):
        rad = math.radians(deg - 90)
        r_in = r * 0.62 if deg % 54 == 0 else r * 0.70
        r_out = r * 0.82
        x1 = cx + r_in * math.cos(rad)
        y1 = cy + r_in * math.sin(rad)
        x2 = cx + r_out * math.cos(rad)
        y2 = cy + r_out * math.sin(rad)
        sw = 2.6 if deg % 54 == 0 else 1.5
        col = "#c92a2a" if deg > 50 else "#2b241d"
        ticks.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{sw}"/>')

    a1 = math.radians(54 - 90)
    a2 = math.radians(135 - 90)
    ar = r * 0.76
    ax1, ay1 = cx + ar * math.cos(a1), cy + ar * math.sin(a1)
    ax2, ay2 = cx + ar * math.cos(a2), cy + ar * math.sin(a2)

    nrad = math.radians(needle_deg - 90)
    nx = cx + r * 0.74 * math.cos(nrad)
    ny = cy + r * 0.74 * math.sin(nrad)

    return f"""
    <g>
      <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{rim_grad}" stroke="#1a140e" stroke-width="2.5"/>
      <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r*0.86:.1f}" fill="{face_color}" stroke="#3b2d1d" stroke-width="1.8"/>
      <path d="M {ax1:.1f} {ay1:.1f} A {ar:.1f} {ar:.1f} 0 0 1 {ax2:.1f} {ay2:.1f}" fill="none" stroke="#e03131" stroke-width="{r*0.11:.1f}" stroke-opacity="0.75"/>
      {''.join(ticks)}
      <line x1="{cx:.1f}" y1="{cy:.1f}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="#d92b2b" stroke-width="2.8" stroke-linecap="round"/>
      <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r*0.13:.1f}" fill="#2b241d"/>
      <path d="M {cx - r*0.65:.1f} {cy - r*0.25:.1f} A {r*0.7:.1f} {r*0.7:.1f} 0 0 1 {cx + r*0.45:.1f} {cy - r*0.62:.1f}" fill="none" stroke="#ffffff" stroke-width="{r*0.09:.1f}" stroke-linecap="round" stroke-opacity="0.65"/>
    </g>
    """


def draw_vacuum_tube(cx, cy, w, h, angle=0):
    return f"""
    <g transform="translate({cx:.1f},{cy:.1f}) rotate({angle:.1f})">
      <rect x="{-w*0.55:.1f}" y="{-h*0.18:.1f}" width="{w*1.1:.1f}" height="{h*0.22:.1f}" rx="3" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2"/>
      <path d="M {-w*0.46:.1f} {-h*0.18:.1f} L {-w*0.46:.1f} {-h*0.75:.1f} A {w*0.46:.1f} {w*0.46:.1f} 0 0 1 {w*0.46:.1f} {-h*0.75:.1f} L {w*0.46:.1f} {-h*0.18:.1f} Z"
            fill="#ff9e2c" fill-opacity="0.28" stroke="#ffd899" stroke-width="2"/>
      <ellipse cx="0" cy="{-h*0.55:.1f}" rx="{w*0.35:.1f}" ry="{h*0.32:.1f}" fill="#ff7b00" fill-opacity="0.45" filter="url(#glowWarm)"/>
      <rect x="{-w*0.22:.1f}" y="{-h*0.68:.1f}" width="{w*0.44:.1f}" height="{h*0.38:.1f}" rx="2" fill="#4a3525" stroke="#ffbe5c" stroke-width="1.5"/>
      <path d="M {-w*0.14:.1f} {-h*0.28:.1f} L 0 {-h*0.62:.1f} L {w*0.14:.1f} {-h*0.28:.1f}" fill="none" stroke="#fff3b0" stroke-width="2.2" filter="url(#glowWarm)"/>
      <path d="M {-w*0.32:.1f} {-h*0.26:.1f} L {-w*0.32:.1f} {-h*0.72:.1f}" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-opacity="0.75"/>
    </g>
    """


def draw_spark(pts, outer_col="#00f2fe", core_col="#ffffff", width=5.0):
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return (
        f'<path d="{d}" fill="none" stroke="{outer_col}" stroke-width="{width:.1f}" '
        f'stroke-linecap="round" stroke-linejoin="round" filter="url(#glowCyan)"/>'
        f'<path d="{d}" fill="none" stroke="{core_col}" stroke-width="{width*0.42:.1f}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
    )


def create_studio_and_backdrop():
    """Creates the photography studio room, the 1980s pull-down laser backdrop, and Dad Bot's legs behind the settee."""
    return f"""
  <!-- ================= 1. STUDIO ROOM & 1980s LASER BACKDROP ================= -->
  <g id="studio-environment">
    <!-- Studio Back Wall -->
    <rect x="0" y="0" width="1600" height="1340" fill="url(#studioWall)"/>
    <!-- Studio Floor -->
    <rect x="0" y="1280" width="1600" height="520" fill="url(#studioFloor)"/>
    <line x1="0" y1="1285" x2="1600" y2="1285" stroke="#09070f" stroke-width="4"/>

    <!-- Hanging Chains for Pull-Down Backdrop -->
    <g stroke="#555d6b" stroke-width="5" stroke-linecap="round">
      <line x1="210" y1="0" x2="210" y2="62"/>
      <line x1="1390" y1="0" x2="1390" y2="48"/>
      <line x1="202" y1="24" x2="218" y2="24" stroke="#8994a6" stroke-width="3"/>
      <line x1="202" y1="44" x2="218" y2="44" stroke="#8994a6" stroke-width="3"/>
      <line x1="1382" y1="18" x2="1398" y2="18" stroke="#8994a6" stroke-width="3"/>
      <line x1="1382" y1="36" x2="1398" y2="36" stroke="#8994a6" stroke-width="3"/>
    </g>

    <!-- Pull-Down Seamless Studio Backdrop Canvas (extending down to y=1735) -->
    <g filter="url(#dropShadow)">
      <path d="M 115 58 L 1485 44 L 1485 1290 C 1485 1420 1525 1545 1565 1735 L 45 1735 C 85 1545 115 1420 115 1290 Z"
            fill="url(#backdropBase)" stroke="#29233d" stroke-width="3"/>
      <!-- Soft Airbrushed 1980s Nebula Clouds -->
      <ellipse cx="980" cy="480" rx="560" ry="390" fill="url(#backdropWarmCloud)"/>
      <ellipse cx="480" cy="620" rx="530" ry="420" fill="url(#backdropTealCloud)"/>
      <ellipse cx="800" cy="680" rx="470" ry="350" fill="#ff9e68" fill-opacity="0.13" filter="url(#blurSoft)"/>

      <!-- Iconic 1980s Sears / Olan Mills Geometric Laser Grid Beams -->
      <g clip-path="url(#backdropClip)">
        <polygon points="180,520 1475,85 1475,155 180,610" fill="url(#laserCyan)" opacity="0.58"/>
        <polygon points="240,680 1475,205 1475,250 240,740" fill="url(#laserCyan)" opacity="0.42"/>
        <polygon points="130,180 1410,720 1410,785 130,240" fill="url(#laserMagenta)" opacity="0.52"/>
        <polygon points="360,80 1475,540 1475,575 360,120" fill="url(#laserGold)" opacity="0.48"/>

        <!-- Crisp Neon Laser Core Lines -->
        <g filter="url(#glowCyan)">
          <line x1="140" y1="560" x2="1475" y2="112" stroke="#7df9ff" stroke-width="5" stroke-opacity="0.88"/>
          <line x1="205" y1="715" x2="1475" y2="228" stroke="#38f2ff" stroke-width="3.5" stroke-opacity="0.78"/>
          <line x1="420" y1="420" x2="1475" y2="66" stroke="#b8f9ff" stroke-width="2.5" stroke-opacity="0.72"/>
          <line x1="135" y1="210" x2="1430" y2="755" stroke="#ff5ca8" stroke-width="4.5" stroke-opacity="0.88"/>
          <line x1="280" y1="118" x2="1470" y2="610" stroke="#ff85c0" stroke-width="2.5" stroke-opacity="0.72"/>
          <line x1="370" y1="100" x2="1470" y2="555" stroke="#ffe066" stroke-width="3.5" stroke-opacity="0.82"/>
        </g>

        <!-- Retro Laser Perspective Grid Hint in Upper Right -->
        <g stroke="#4facfe" stroke-opacity="0.24" stroke-width="1.8">
          <line x1="880" y1="50" x2="1480" y2="390"/>
          <line x1="1020" y1="48" x2="1480" y2="310"/>
          <line x1="1160" y1="46" x2="1480" y2="230"/>
          <line x1="780" y1="310" x2="1480" y2="78"/>
          <line x1="850" y1="380" x2="1480" y2="162"/>
        </g>

        <!-- Soft Out-of-Focus Studio Bokeh Orbs -->
        <circle cx="1180" cy="210" r="36" fill="#7df9ff" fill-opacity="0.18" filter="url(#blurMed)"/>
        <circle cx="1090" cy="145" r="22" fill="#ffb8d9" fill-opacity="0.24" filter="url(#blurMed)"/>
        <circle cx="430" cy="240" r="42" fill="#ff7eb3" fill-opacity="0.16" filter="url(#blurMed)"/>
        <circle cx="520" cy="180" r="24" fill="#7df9ff" fill-opacity="0.20" filter="url(#blurMed)"/>
      </g>

      <!-- Subtle crease lines on the backdrop sweep floor -->
      <path d="M 155 1320 Q 780 1355 1445 1305" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="3"/>
      <path d="M 115 1455 Q 810 1495 1495 1440" fill="none" stroke="#080412" stroke-opacity="0.35" stroke-width="4"/>
      <path d="M 75 1665 Q 800 1705 1535 1655" fill="none" stroke="#ffffff" stroke-opacity="0.06" stroke-width="2.5"/>
    </g>

    <!-- Backdrop Top Metal Roller Bar (slightly crooked!) -->
    <g transform="rotate(-0.6, 800, 51)" filter="url(#tightShadow)">
      <rect x="85" y="40" width="1430" height="22" rx="10" fill="url(#chromeGrad)" stroke="#1a1c24" stroke-width="2.5"/>
      <rect x="72" y="34" width="28" height="34" rx="5" fill="url(#dadBrass)" stroke="#1a1c24" stroke-width="2"/>
      <rect x="1500" y="34" width="28" height="34" rx="5" fill="url(#dadBrass)" stroke="#1a1c24" stroke-width="2"/>
      <!-- Pull cord & brass acorn weight -->
      <line x1="800" y1="62" x2="800" y2="112" stroke="#d9cbb8" stroke-width="3" stroke-dasharray="4,3"/>
      <circle cx="800" cy="119" r="8" fill="url(#dadBrass)" stroke="#1c160d" stroke-width="2"/>
    </g>

    <!-- Floor Cast Shadows Under Settee and Family -->
    <ellipse cx="835" cy="1515" rx="690" ry="105" fill="#06040c" fill-opacity="0.76" filter="url(#blurMed)"/>
    <ellipse cx="315" cy="1520" rx="195" ry="46" fill="#040208" fill-opacity="0.78" filter="url(#blurMed)"/>
    <ellipse cx="965" cy="1585" rx="260" ry="56" fill="#040208" fill-opacity="0.82" filter="url(#blurMed)"/>

    <!--DAD BOT'S PILLAR LEGS (Placed BEHIND the Velvet Settee so the backrest occludes his upper legs!) -->
    <g id="dad-legs-behind-settee" filter="url(#dropShadow)">
      {draw_hydraulic_cylinder((625, 1180), (620, 1425), 54, 48, "url(#darkPipe)", "url(#dadBrass)")}
      {draw_hydraulic_cylinder((765, 1180), (770, 1425), 54, 48, "url(#darkPipe)", "url(#dadBrass)")}
      <!-- Heavy Brass & Walnut Console Feet Peeking Under Settee -->
      <path d="M 565 1415 C 565 1385 665 1385 665 1415 L 675 1452 L 552 1452 Z" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="3"/>
      <rect x="548" y="1445" width="130" height="16" rx="6" fill="url(#dadWalnut)" stroke="#1c150c" stroke-width="2.5"/>
      <path d="M 718 1415 C 718 1385 818 1385 818 1415 L 828 1452 L 705 1452 Z" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="3"/>
      <rect x="702" y="1445" width="130" height="16" rx="6" fill="url(#dadWalnut)" stroke="#1c150c" stroke-width="2.5"/>
    </g>
  </g>
"""


def create_settee_back():
    """Creates the ornate tufted burgundy velvet studio posing bench (backrest & frame)."""
    tufts = []
    for row_idx, y in enumerate([885, 955, 1025]):
        x_start = 520 if row_idx % 2 == 0 else 560
        for x in range(x_start, 1330, 80):
            droop = max(0, (x - 1000) * 0.06)
            ty = y + droop
            tufts.append(
                f'<path d="M {x-38} {ty} Q {x} {ty-26} {x+38} {ty} Q {x} {ty+26} {x-38} {ty} Z" '
                f'fill="url(#velvetTuft)" stroke="#2b030c" stroke-width="2" opacity="0.88"/>'
                f'<circle cx="{x}" cy="{ty:.1f}" r="5.5" fill="url(#giltWood)" stroke="#241202" stroke-width="1.5"/>'
            )

    return f"""
  <!-- ================= 2. STUDIO VELVET SETTEE (BACKREST) ================= -->
  <g id="settee-back" filter="url(#dropShadow)">
    <!-- Carved Gilt Wood Crest Rail -->
    <path d="M 435 840 Q 680 775 910 815 Q 1140 770 1385 865 L 1365 1130 L 455 1110 Z"
          fill="url(#giltWood)" stroke="#2b1702" stroke-width="3.5"/>
    <circle cx="445" cy="845" r="18" fill="url(#giltWood)" stroke="#2b1702" stroke-width="2.5"/>
    <circle cx="910" cy="805" r="22" fill="url(#giltWood)" stroke="#2b1702" stroke-width="2.5"/>
    <circle cx="1378" cy="868" r="18" fill="url(#giltWood)" stroke="#2b1702" stroke-width="2.5"/>

    <!-- Tufted Burgundy Velvet Backrest Cushion -->
    <path d="M 462 858 Q 680 802 910 838 Q 1140 798 1358 882 L 1345 1125 L 470 1105 Z"
          fill="url(#velvetCrimson)" stroke="#33040f" stroke-width="3"/>
    {''.join(tufts)}
  </g>
"""


def create_dad_bot():
    """Creates Dad Bot (1970s Walnut & Brass Console Patriarch) standing proudly behind the settee."""
    # Right arm reaching to Teen Bot's shoulder (from 525,535 to 412,510)
    right_arm = draw_segmented_limb((525, 535), (465, 495), (412, 510), 9, 44, 20, "url(#dadBrass)")
    # Left arm reaching behind Mom Bot toward her outer shoulder (from 865,535 to 1085,515)
    left_arm_upper = draw_segmented_limb((865, 535), (975, 495), (1085, 515), 11, 42, 20, "url(#dadBrass)")

    dad_rivets = draw_rivets([
        (542, 488), (848, 488), (542, 875), (848, 875),
        (615, 488), (775, 488), (542, 680), (848, 680)
    ], r=5, fill="url(#dadBrass)")

    tubes = (
        draw_vacuum_tube(555, 468, 28, 58, -8) +
        draw_vacuum_tube(592, 468, 24, 48, -3) +
        draw_vacuum_tube(802, 468, 24, 48, 4) +
        draw_vacuum_tube(838, 468, 28, 58, 9)
    )

    gauges = (
        draw_gauge(615, 595, 36, needle_deg=45) +
        draw_gauge(775, 595, 36, needle_deg=82)
    )

    return f"""
  <!-- ================= 3. DAD BOT (1970s Walnut & Brass Console Patriarch) ================= -->
  <g id="dad-bot" filter="url(#dropShadow)">
    <!-- Dad's Arms (behind torso) -->
    {right_arm}
    {left_arm_upper}

    <!-- Shoulder Vacuum Tubes -->
    {tubes}

    <!-- Dad's Wide Barrel-Chested Hi-Fi Console Torso -->
    <g id="dad-torso">
      <rect x="500" y="490" width="52" height="88" rx="18" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="3"/>
      <rect x="838" y="490" width="52" height="88" rx="18" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="3"/>

      <!-- Outer Brushed Brass & Cream-Steel Chassis Box -->
      <rect x="522" y="468" width="346" height="432" rx="24" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="3.5"/>
      <!-- Walnut Woodgrain Side Panels -->
      <rect x="536" y="482" width="318" height="404" rx="16" fill="url(#dadWalnut)" stroke="#241205" stroke-width="3"/>
      <!-- Woodgrain Texture Lines -->
      <g stroke="#291205" stroke-width="2" stroke-opacity="0.45" fill="none">
        <path d="M 552 485 Q 560 680 548 882"/>
        <path d="M 568 485 Q 555 690 572 882"/>
        <path d="M 822 485 Q 832 670 818 882"/>
        <path d="M 838 485 Q 825 690 840 882"/>
      </g>

      <!-- Center Brushed Cream-Steel Instrument Faceplate -->
      <rect x="568" y="498" width="254" height="372" rx="12" fill="url(#dadCreamSteel)" stroke="#382c1e" stroke-width="3"/>

      <!-- Analog Dial Gauges -->
      {gauges}

      <!-- Center Oscilloscope / Green Sine-Wave Window -->
      <rect x="662" y="558" width="66" height="74" rx="8" fill="#0c2618" stroke="#382c1e" stroke-width="3"/>
      <line x1="666" y1="595" x2="724" y2="595" stroke="#1f5c39" stroke-width="1.5"/>
      <line x1="695" y1="562" x2="695" y2="628" stroke="#1f5c39" stroke-width="1.5"/>
      <path d="M 666 595 Q 675 568 684 595 T 702 595 T 722 595" fill="none" stroke="#4dff88" stroke-width="3" filter="url(#glowWarm)"/>

      <!-- Mid-Torso Warm Walnut Speaker Louvers & Brass Trim -->
      <rect x="588" y="652" width="214" height="115" rx="8" fill="url(#dadWalnut)" stroke="#2b190b" stroke-width="2.5"/>
      <g stroke="url(#dadBrass)" stroke-width="4" stroke-linecap="round">
        <line x1="602" y1="672" x2="788" y2="672"/>
        <line x1="602" y1="692" x2="788" y2="692"/>
        <line x1="602" y1="712" x2="788" y2="712"/>
        <line x1="602" y1="732" x2="788" y2="732"/>
        <line x1="602" y1="752" x2="788" y2="752"/>
      </g>

      <!-- Lower Control Panel: Toggle Switches & Reel-to-Reel Tape Spools -->
      <rect x="588" y="782" width="214" height="72" rx="8" fill="#2b2520" stroke="#4a3b2a" stroke-width="2"/>
      <circle cx="628" cy="818" r="22" fill="url(#chromeGrad)" stroke="#141210" stroke-width="2"/>
      <circle cx="628" cy="818" r="7" fill="#2b2520"/>
      <circle cx="692" cy="818" r="22" fill="url(#chromeGrad)" stroke="#141210" stroke-width="2"/>
      <circle cx="692" cy="818" r="7" fill="#2b2520"/>
      <circle cx="742" cy="804" r="6" fill="#ff3b30" filter="url(#glowWarm)"/>
      <circle cx="768" cy="804" r="6" fill="#34c759" filter="url(#glowWarm)"/>
      <rect x="736" y="822" width="12" height="20" rx="3" fill="url(#chromeGrad)" stroke="#141210" stroke-width="1.5"/>
      <rect x="762" y="822" width="12" height="20" rx="3" fill="url(#chromeGrad)" stroke="#141210" stroke-width="1.5"/>

      {dad_rivets}
    </g>

    <!-- Dad's Neck & Crooked Geometric Metal Clip-On Bowtie -->
    <g id="dad-neck">
      {draw_segmented_limb((695, 475), (695, 455), (695, 435), 4, 74, 16, "url(#darkPipe)")}
      <g transform="translate(695, 482) rotate(-11)" filter="url(#tightShadow)">
        <polygon points="-58,-24 -8,-5 -8,5 -58,24" fill="#c92a2a" stroke="#f5d076" stroke-width="3" stroke-linejoin="round"/>
        <polygon points="58,-24 8,-5 8,5 58,24" fill="#a61e1e" stroke="#f5d076" stroke-width="3" stroke-linejoin="round"/>
        <polygon points="-46,-14 -14,-3 -14,3 -46,14" fill="#e03131"/>
        <polygon points="46,-14 14,-3 14,3 46,14" fill="#c92a2a"/>
        <rect x="-12" y="-12" width="24" height="24" rx="5" fill="url(#dadBrass)" stroke="#241808" stroke-width="2.5"/>
      </g>
    </g>

    <!-- Dad's Proudly Tilted Head (+3.5 deg) -->
    <g id="dad-head" transform="translate(695, 345) rotate(3.5)">
      <!-- Rabbit-Ear Dipole Antennas -->
      <line x1="-25" y1="-98" x2="-95" y2="-185" stroke="url(#chromeGrad)" stroke-width="5" stroke-linecap="round"/>
      <circle cx="-95" cy="-185" r="8" fill="#ff3b30" stroke="#1c150c" stroke-width="2"/>
      <line x1="25" y1="-98" x2="105" y2="-172" stroke="url(#chromeGrad)" stroke-width="5" stroke-linecap="round"/>
      <circle cx="105" cy="-172" r="8" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2"/>
      <path d="M -38 -95 C -38 -115 38 -115 38 -95 Z" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2.5"/>

      <!-- Side Ear-Pods -->
      <rect x="-138" y="-28" width="22" height="56" rx="8" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2.5"/>
      <rect x="116" y="-28" width="22" height="56" rx="8" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2.5"/>

      <!-- Outer Walnut & Brass Head Cabinet -->
      <rect x="-122" y="-96" width="244" height="192" rx="26" fill="url(#dadWalnut)" stroke="#1c1208" stroke-width="3.5"/>
      <rect x="-108" y="-82" width="216" height="164" rx="18" fill="url(#dadCreamSteel)" stroke="#3b2c1a" stroke-width="3"/>
      <!-- Dark Recessed Optic Faceplate -->
      <rect x="-94" y="-68" width="188" height="92" rx="12" fill="#211d1a" stroke="#5c472c" stroke-width="2.5"/>

      <!-- Left Eye: Giant Wide-Open Protruding Brass Telephoto Lens -->
      <g transform="translate(-44, -22)">
        <circle cx="0" cy="0" r="44" fill="url(#dadBrass)" stroke="#171108" stroke-width="3"/>
        <circle cx="0" cy="0" r="35" fill="#121820" stroke="#4a381d" stroke-width="2"/>
        <circle cx="0" cy="0" r="29" fill="url(#cyanLens)"/>
        <circle cx="0" cy="0" r="19" fill="none" stroke="#002b47" stroke-width="3" stroke-dasharray="10,5"/>
        <circle cx="0" cy="0" r="10" fill="#001829"/>
        <circle cx="-11" cy="-11" r="8" fill="#ffffff" fill-opacity="0.9"/>
        <circle cx="9" cy="10" r="4" fill="#b8f9ff" fill-opacity="0.75"/>
        <path d="M -42 -44 Q -5 -58 38 -38" fill="none" stroke="url(#dadBrass)" stroke-width="9" stroke-linecap="round"/>
        <path d="M -42 -44 Q -5 -58 38 -38" fill="none" stroke="#1c150c" stroke-width="2" stroke-linecap="round"/>
      </g>

      <!-- Right Eye: Smaller Lens with Strained, Twitching Half-Closed Shutter Eyelid -->
      <g transform="translate(48, -18)">
        <circle cx="0" cy="0" r="34" fill="url(#dadBrass)" stroke="#171108" stroke-width="3"/>
        <circle cx="0" cy="0" r="25" fill="url(#cyanLens)"/>
        <circle cx="0" cy="0" r="9" fill="#001829"/>
        <path d="M -27 -6 A 26 26 0 0 1 27 -2 L 26 -14 A 26 26 0 0 0 -27 -6 Z" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2"/>
        <line x1="-26" y1="-3" x2="26" y2="3" stroke="url(#dadBrass)" stroke-width="7" stroke-linecap="round"/>
        <circle cx="-7" cy="4" r="5.5" fill="#ffffff" fill-opacity="0.88"/>
        <path d="M -30 -36 Q 5 -28 34 -42" fill="none" stroke="url(#dadBrass)" stroke-width="8" stroke-linecap="round"/>
      </g>

      <!-- Sculpted Chrome "Handlebar Mustache" Bumper Grille -->
      <path d="M -88 32 Q -45 10 0 24 Q 45 10 88 32 Q 68 46 38 40 Q 0 32 -38 40 Q -68 46 -88 32 Z"
            fill="url(#chromeGrad)" stroke="#171a21" stroke-width="2.8" filter="url(#tightShadow)"/>

      <!-- Forced, Overly Wide Clenched Radiator-Grille Smile -->
      <path d="M -74 44 Q 0 58 74 44 L 66 72 Q 0 86 -66 72 Z" fill="#ffffff" stroke="#1c150c" stroke-width="3"/>
      <g stroke="#1c150c" stroke-width="2.8">
        <line x1="-48" y1="47" x2="-45" y2="74"/>
        <line x1="-24" y1="50" x2="-22" y2="77"/>
        <line x1="0" y1="51" x2="0" y2="78"/>
        <line x1="24" y1="50" x2="22" y2="77"/>
        <line x1="48" y1="47" x2="45" y2="74"/>
        <path d="M -70 58 Q 0 72 70 58" fill="none" stroke="#1c150c" stroke-width="2.5"/>
      </g>
    </g>
  </g>
"""


def create_teen_bot():
    """Creates the Angsty 1990s/2000s Cyber-Goth Teenager Bot on the far left, slouching away from Dad."""
    return f"""
  <!-- ================= 4. TEENAGER BOT (Angsty Slouching Cyber-Goth Unit, Far Left) ================= -->
  <g id="teen-bot" filter="url(#dropShadow)">
    <!-- Studio Floor Bullseye Standing-Mark Stencil (Teen Bot is deliberately stepping off his mark!) -->
    <g transform="translate(335, 1485) scale(1, 0.34)" opacity="0.65">
      <circle cx="0" cy="0" r="68" fill="none" stroke="#ffe066" stroke-width="8" stroke-dasharray="22,12"/>
      <circle cx="0" cy="0" r="38" fill="none" stroke="#38f2ff" stroke-width="6"/>
      <circle cx="0" cy="0" r="12" fill="#ffe066"/>
    </g>

    <!-- Long Gangly Solid Hydraulic Legs -->
    <g id="teen-legs">
      <!-- Left Thigh & Shin (stepped way out to the left off the standing mark!) -->
      {draw_hydraulic_cylinder((268, 925), (218, 1180), 40, 32, "url(#teenCharcoal)", "url(#chromeGrad)", "#b544ff")}
      {draw_hydraulic_cylinder((218, 1180), (195, 1440), 32, 28, "url(#teenCharcoal)", "url(#chromeGrad)", "#38f2ff")}
      <!-- Right Thigh & Shin -->
      {draw_hydraulic_cylinder((352, 928), (335, 1185), 40, 32, "url(#teenCharcoal)", "url(#chromeGrad)", "#b544ff")}
      {draw_hydraulic_cylinder((335, 1185), (345, 1450), 32, 28, "url(#teenCharcoal)", "url(#chromeGrad)", "#38f2ff")}

      <!-- Knee Ball Joints with Neon Purple Rings -->
      <circle cx="218" cy="1180" r="24" fill="url(#teenCharcoal)" stroke="#101118" stroke-width="3"/>
      <circle cx="218" cy="1180" r="12" fill="#b544ff" stroke="#101118" stroke-width="2"/>
      <circle cx="335" cy="1185" r="24" fill="url(#teenCharcoal)" stroke="#101118" stroke-width="3"/>
      <circle cx="335" cy="1185" r="12" fill="#b544ff" stroke="#101118" stroke-width="2"/>

      <!-- Chunky Cyber-Skater Platform Boots (Left boot tilted up on heel!) -->
      <g transform="translate(190, 1448) rotate(-14)">
        <path d="M -55 -20 C -55 -50 38 -50 45 -15 L 50 22 L -68 22 Z" fill="url(#teenCharcoal)" stroke="#0d0e14" stroke-width="3"/>
        <rect x="-72" y="12" width="126" height="22" rx="8" fill="#b544ff" stroke="#0d0e14" stroke-width="2.5"/>
        <line x1="-60" y1="23" x2="44" y2="23" stroke="#38f2ff" stroke-width="3"/>
      </g>
      <g transform="translate(348, 1455) rotate(3)">
        <path d="M -45 -22 C -45 -52 45 -52 52 -15 L 58 22 L -52 22 Z" fill="url(#teenCharcoal)" stroke="#0d0e14" stroke-width="3"/>
        <rect x="-56" y="12" width="118" height="22" rx="8" fill="#b544ff" stroke="#0d0e14" stroke-width="2.5"/>
        <line x1="-46" y1="23" x2="50" y2="23" stroke="#38f2ff" stroke-width="3"/>
      </g>
    </g>

    <!-- Teen Bot's Slouched Torso & Pelvis (tilted -10 deg away from Dad!) -->
    <g id="teen-body" transform="translate(315, 720) rotate(-10)">
      <!-- Pelvis Pod -->
      <path d="M -74 155 L 74 155 L 54 218 L -54 218 Z" fill="url(#teenCharcoal)" stroke="#0d0e14" stroke-width="3"/>
      <rect x="-66" y="145" width="132" height="18" rx="6" fill="#b544ff" stroke="#0d0e14" stroke-width="2.5"/>
      <!-- Flexible Spine Bellows -->
      {draw_segmented_limb((0, 75), (-8, 115), (0, 150), 5, 60, 18, "url(#darkPipe)")}

      <!-- Upper Hooded/Angled Charcoal & Translucent Purple Chest -->
      <path d="M -98 -195 L 98 -185 L 78 85 L -76 85 Z" fill="url(#teenCharcoal)" stroke="#0d0e14" stroke-width="3.5" stroke-linejoin="round"/>
      <!-- High Hunched Shoulder Cowls -->
      <path d="M -114 -205 C -85 -232 -45 -222 -38 -185 L -88 -145 Z" fill="url(#teenCharcoal)" stroke="#0d0e14" stroke-width="3"/>
      <path d="M 114 -195 C 85 -222 45 -212 38 -175 L 88 -135 Z" fill="url(#teenCharcoal)" stroke="#0d0e14" stroke-width="3"/>

      <!-- Translucent Purple Polycarbonate Chest Window -->
      <path d="M -68 -155 L 68 -148 L 54 45 L -54 45 Z" fill="url(#teenTransPurple)" stroke="#d98aff" stroke-width="2.5"/>
      <!-- Internal Glowing Circuit Traces (strictly geometric) -->
      <g stroke="#39ff14" stroke-width="2.5" fill="none" opacity="0.85">
        <path d="M -45 -120 L -15 -120 L 0 -95 L 35 -95"/>
        <path d="M -40 -65 L -10 -65 L 12 -40 L 42 -40"/>
        <path d="M -32 10 L 0 10 L 18 -15 L 38 -15"/>
        <circle cx="-45" cy="-120" r="4" fill="#39ff14"/>
        <circle cx="35" cy="-95" r="4" fill="#39ff14"/>
        <circle cx="42" cy="-40" r="4" fill="#39ff14"/>
      </g>
      <circle cx="0" cy="-65" r="22" fill="#ff2a85" fill-opacity="0.5" filter="url(#glowCyan)"/>
      <circle cx="0" cy="-65" r="12" fill="#ff9ec7" stroke="#ffffff" stroke-width="2"/>
    </g>

    <!-- Teen Bot's Solid Hydraulic Arms (Left arm crossed sullenly; Right arm holding up Prank "Bunny Ears" behind Little Brother's Head!) -->
    <g id="teen-arms">
      <!-- Left Upper Arm & Forearm crossed over chest -->
      {draw_hydraulic_cylinder((208, 535), (178, 665), 34, 28, "url(#teenCharcoal)", "url(#chromeGrad)", "#b544ff")}
      <circle cx="178" cy="665" r="18" fill="url(#teenCharcoal)" stroke="#b544ff" stroke-width="2.5"/>
      {draw_hydraulic_cylinder((178, 665), (345, 682), 28, 26, "url(#teenCharcoal)", "url(#chromeGrad)", "#38f2ff")}
      <path d="M 345 668 C 372 666 372 698 345 696" fill="none" stroke="#b544ff" stroke-width="8.5" stroke-linecap="round"/>

      <!-- Right Upper Arm extending from right shoulder (402, 518) to elbow (442, 628) and forearm up to (502, 662) -->
      {draw_hydraulic_cylinder((402, 518), (442, 628), 34, 28, "url(#teenCharcoal)", "url(#chromeGrad)", "#b544ff")}
      <circle cx="442" cy="628" r="18" fill="url(#teenCharcoal)" stroke="#b544ff" stroke-width="2.5"/>
      {draw_hydraulic_cylinder((442, 628), (502, 662), 28, 24, "url(#teenCharcoal)", "url(#chromeGrad)", "#38f2ff")}
      <!-- Teen Bot's Prank "Bunny Ears" Mechanical Hand Behind Middle-Child Bot's Head! -->
      <g transform="translate(506, 658) rotate(12)" filter="url(#tightShadow)">
        <rect x="-18" y="-14" width="36" height="26" rx="8" fill="url(#teenCharcoal)" stroke="#b544ff" stroke-width="2.5"/>
        <!-- Two tall V-shaped robotic bunny-ear fingers held up behind little brother's head -->
        <line x1="-8" y1="-14" x2="-22" y2="-66" stroke="url(#chromeGrad)" stroke-width="10" stroke-linecap="round"/>
        <line x1="-8" y1="-14" x2="-22" y2="-66" stroke="#b544ff" stroke-width="4" stroke-linecap="round"/>
        <circle cx="-22" cy="-66" r="6" fill="#38f2ff"/>
        <line x1="8" y1="-14" x2="18" y2="-68" stroke="url(#chromeGrad)" stroke-width="10" stroke-linecap="round"/>
        <line x1="8" y1="-14" x2="18" y2="-68" stroke="#b544ff" stroke-width="4" stroke-linecap="round"/>
        <circle cx="18" cy="-68" r="6" fill="#38f2ff"/>
      </g>
    </g>

    <!-- DAD'S HEAVY BRASS CLAMP-HAND GRIPPING TEEN BOT'S RIGHT SHOULDER! -->
    <g id="dad-clamp-on-teen" transform="translate(405, 506) rotate(-16)" filter="url(#tightShadow)">
      <rect x="-26" y="-22" width="52" height="32" rx="10" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="3"/>
      <path d="M -22 6 C -32 28 -18 48 -8 42" fill="none" stroke="url(#dadBrass)" stroke-width="12" stroke-linecap="round"/>
      <path d="M -22 6 C -32 28 -18 48 -8 42" fill="none" stroke="#1c150c" stroke-width="2.5" stroke-linecap="round"/>
      <path d="M 0 8 C -4 34 8 52 16 44" fill="none" stroke="url(#dadBrass)" stroke-width="12" stroke-linecap="round"/>
      <path d="M 0 8 C -4 34 8 52 16 44" fill="none" stroke="#1c150c" stroke-width="2.5" stroke-linecap="round"/>
      <path d="M 20 4 C 24 28 34 42 40 34" fill="none" stroke="url(#dadBrass)" stroke-width="11" stroke-linecap="round"/>
      <path d="M 20 4 C 24 28 34 42 40 34" fill="none" stroke="#1c150c" stroke-width="2.5" stroke-linecap="round"/>
    </g>

    <!-- Teen Bot's Neck & Head (tilted -16 deg down & away, wearing Oversized Headphones) -->
    {draw_segmented_limb((295, 520), (285, 480), (280, 445), 4, 40, 14, "url(#darkPipe)")}
    <g id="teen-head" transform="translate(275, 395) rotate(-16)">
      <!-- Headphone Overhead Arch Band -->
      <path d="M -105 10 C -115 -115 115 -115 105 10" fill="none" stroke="url(#chromeGrad)" stroke-width="14" stroke-linecap="round"/>
      <path d="M -85 -48 C -45 -92 45 -92 85 -48" fill="none" stroke="#b544ff" stroke-width="8" stroke-linecap="round"/>

      <!-- Sleek Angled Trapezoidal Cyber Head -->
      <path d="M -82 -58 L 82 -58 L 68 64 L -68 64 Z" fill="url(#teenCharcoal)" stroke="#0d0e14" stroke-width="3.5" stroke-linejoin="round"/>
      <!-- Glossy Dark Visor Faceplate -->
      <path d="M -68 -42 L 68 -42 L 56 48 L -56 48 Z" fill="url(#teenVisor)" stroke="#b544ff" stroke-width="2.5" stroke-linejoin="round"/>

      <!-- Expressive Eye-Roll Visor Graphics (Looking hard to the upper-left!) -->
      <g filter="url(#glowCyan)">
        <circle cx="-36" cy="-12" r="14" fill="#38f2ff"/>
        <path d="M -54 -14 L -16 -8 L -16 -28 L -54 -28 Z" fill="#180428"/>
        <line x1="-52" y1="-12" x2="-16" y2="-6" stroke="#ff4e9b" stroke-width="4" stroke-linecap="round"/>

        <circle cx="20" cy="-12" r="14" fill="#38f2ff"/>
        <path d="M 2 -14 L 40 -8 L 40 -28 L 2 -28 Z" fill="#180428"/>
        <line x1="4" y1="-12" x2="38" y2="-6" stroke="#ff4e9b" stroke-width="4" stroke-linecap="round"/>

        <!-- Flat Unimpressed Diagonal Mouth Line -->
        <line x1="-22" y1="26" x2="18" y2="20" stroke="#ff4e9b" stroke-width="4.5" stroke-linecap="round"/>
      </g>

      <polygon points="-58,-38 -25,-38 -42,42 -52,42" fill="#ffffff" fill-opacity="0.12"/>

      <!-- Giant Chunky Ear-Cups of the Headphones -->
      <g transform="translate(-92, 4)">
        <rect x="-22" y="-38" width="32" height="76" rx="14" fill="#b544ff" stroke="#0d0e14" stroke-width="3"/>
        <rect x="-8" y="-32" width="14" height="64" rx="6" fill="#232533" stroke="#0d0e14" stroke-width="2"/>
        <circle cx="-9" cy="0" r="10" fill="#38f2ff" fill-opacity="0.8"/>
      </g>
      <g transform="translate(92, 4)">
        <rect x="-10" y="-38" width="32" height="76" rx="14" fill="#b544ff" stroke="#0d0e14" stroke-width="3"/>
        <rect x="-6" y="-32" width="14" height="64" rx="6" fill="#232533" stroke="#0d0e14" stroke-width="2"/>
        <circle cx="9" cy="0" r="10" fill="#38f2ff" fill-opacity="0.8"/>
      </g>
    </g>

    <!-- Coiled Headphone Cable Dangling from Teen's Left Ear-Cup -->
    <path d="M 175 415 C 145 460 195 475 160 510 C 135 540 185 555 158 590 C 138 620 190 640 235 670"
          fill="none" stroke="#ff4e9b" stroke-width="4.5" stroke-linecap="round"/>
  </g>
"""


def create_settee_seat_and_grandpa_and_mom():
    """Creates the Settee Seat Cushion, Grandpa Bot (asleep on right), Mom Bot (center-right), and Dad's Hover-Hand."""
    gp_rivets = draw_rivets([
        (1195, 720), (1225, 695), (1265, 682), (1305, 680), (1345, 685), (1385, 702), (1410, 730),
        (1185, 920), (1225, 945), (1270, 958), (1315, 960), (1360, 952), (1400, 935)
    ], r=5.5, fill="url(#grandpaCopper)")

    # Crisp static electricity arcs jumping from Mom's beehive coils & hairpin to Dad's Hover-Hand!
    hover_sparks = (
        draw_spark([(1048, 398), (1082, 432), (1072, 468), (1118, 505)], "#38f2ff", "#ffffff", 4.8) +
        draw_spark([(1052, 442), (1085, 472), (1078, 495), (1112, 522)], "#38f2ff", "#ffffff", 4.0)
    )

    return f"""
  <!-- ================= 5. SETTEE SEAT, GRANDPA BOT, MOM BOT & DAD'S HOVER-HAND ================= -->
  <g id="settee-seat-and-legs" filter="url(#dropShadow)">
    <!-- Carved Gilt Wood Armrests -->
    <path d="M 430 965 C 400 965 395 1020 425 1035 L 475 1135 L 505 1125 L 468 985 Z" fill="url(#giltWood)" stroke="#2b1702" stroke-width="3"/>
    <path d="M 1380 990 C 1415 990 1425 1045 1392 1060 L 1355 1165 L 1325 1155 L 1350 1005 Z" fill="url(#giltWood)" stroke="#2b1702" stroke-width="3"/>

    <!-- Plush Burgundy Velvet Seat Cushion (deeply squished on the right under Grandpa Bot!) -->
    <path d="M 445 1085 Q 720 1060 980 1085 Q 1230 1145 1375 1125 C 1400 1155 1395 1215 1365 1225 Q 910 1245 450 1205 C 425 1190 422 1115 445 1085 Z"
          fill="url(#velvetCrimson)" stroke="#2b030c" stroke-width="3.5"/>
    <!-- Gold Seat Apron & Trim -->
    <path d="M 448 1195 Q 910 1235 1368 1218 L 1360 1262 Q 910 1282 455 1240 Z"
          fill="url(#giltWood)" stroke="#2b1702" stroke-width="3"/>

    <!-- Settee Wooden Legs (Front-Right Leg at x=1345 is buckling & cracked under Grandpa's weight!) -->
    <path d="M 465 1235 L 495 1238 L 482 1465 L 452 1465 Z" fill="url(#giltWood)" stroke="#2b1702" stroke-width="3"/>
    <circle cx="467" cy="1465" r="14" fill="url(#dadBrass)" stroke="#2b1702" stroke-width="2.5"/>
    <path d="M 535 1235 L 560 1238 L 552 1430 L 528 1430 Z" fill="#593506" stroke="#241202" stroke-width="2.5"/>
    <path d="M 1255 1255 L 1280 1255 L 1290 1435 L 1265 1435 Z" fill="#593506" stroke="#241202" stroke-width="2.5"/>
    <!-- Buckling Front Right Leg -->
    <path d="M 1325 1255 L 1358 1252 Q 1405 1355 1365 1470 L 1332 1470 Q 1368 1355 1325 1255 Z"
          fill="url(#giltWood)" stroke="#2b1702" stroke-width="3"/>
    <path d="M 1378 1355 L 1355 1362 L 1368 1372 L 1348 1378" fill="none" stroke="#1f0f01" stroke-width="3" stroke-linecap="round"/>
    <polygon points="1392,1348 1408,1342 1398,1356" fill="#d89c3e" stroke="#2b1702" stroke-width="1.5"/>
    <polygon points="1396,1368 1414,1372 1400,1379" fill="#d89c3e" stroke="#2b1702" stroke-width="1.5"/>
    <circle cx="1348" cy="1472" r="14" fill="url(#dadBrass)" stroke="#2b1702" stroke-width="2.5"/>
  </g>

  <!-- ================= 6. GRANDPA BOT (Antique 1920s Cast-Iron Boiler Automaton, Fast Asleep!) ================= -->
  <g id="grandpa-bot" filter="url(#dropShadow)">
    <!-- Grandpa's Stubby Riveted Cast-Iron Legs (tightly packed segments) -->
    <g id="grandpa-legs">
      {draw_segmented_limb((1235, 1045), (1220, 1245), (1215, 1435), 14, 50, 24, "url(#grandpaIron)")}
      {draw_segmented_limb((1345, 1045), (1345, 1245), (1315, 1440), 14, 50, 24, "url(#grandpaIron)")}
      <path d="M 1160 1430 C 1160 1395 1255 1395 1255 1430 L 1265 1468 L 1148 1468 Z" fill="url(#grandpaCopper)" stroke="#17120e" stroke-width="3"/>
      <path d="M 1270 1435 C 1270 1400 1365 1400 1365 1435 L 1375 1472 L 1260 1472 Z" fill="url(#grandpaCopper)" stroke="#17120e" stroke-width="3"/>
    </g>

    <!-- Grandpa's Rotund Cast-Iron & Tarnished Copper Boiler Belly -->
    <g id="grandpa-torso">
      <!-- Brass Steam Whistle Mounted Snugly on Grandpa's Upper-Left Shoulder -->
      <g transform="translate(1382, 708) rotate(24)">
        <rect x="-12" y="-8" width="24" height="14" rx="3" fill="url(#grandpaCopper)" stroke="#1c120b" stroke-width="2"/>
        <rect x="-8" y="-42" width="16" height="36" rx="4" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2"/>
        <path d="M -12 -42 L 12 -42 L 8 -56 L -8 -56 Z" fill="url(#grandpaCopper)" stroke="#1c150c" stroke-width="2"/>
      </g>

      <ellipse cx="1298" cy="845" rx="135" ry="185" fill="url(#grandpaIron)" stroke="#171514" stroke-width="4"/>
      <path d="M 1168 740 Q 1298 695 1428 745 L 1422 935 Q 1298 985 1172 930 Z"
            fill="url(#grandpaCopper)" stroke="#1c120b" stroke-width="3.5"/>
      {gp_rivets}

      <!-- Glowing Coal Firebox Grate Window in Lower Belly -->
      <rect x="1238" y="835" width="115" height="72" rx="14" fill="#290c02" stroke="#17120e" stroke-width="3.5"/>
      <ellipse cx="1295" cy="878" rx="46" ry="22" fill="#ff5500" fill-opacity="0.65" filter="url(#glowWarm)"/>
      <circle cx="1275" cy="882" r="12" fill="#ffaa00" fill-opacity="0.8"/>
      <circle cx="1312" cy="880" r="14" fill="#ff7700" fill-opacity="0.8"/>
      <g stroke="#241c18" stroke-width="5" stroke-linecap="round">
        <line x1="1262" y1="840" x2="1262" y2="902"/>
        <line x1="1284" y1="840" x2="1284" y2="902"/>
        <line x1="1306" y1="840" x2="1306" y2="902"/>
        <line x1="1328" y1="840" x2="1328" y2="902"/>
      </g>

      <!-- Grandpa's Chest Pressure Gauge (Needle resting down in Sleep Mode) -->
      {draw_gauge(1298, 772, 38, needle_deg=-125, rim_grad="url(#grandpaCopper)")}
    </g>

    <!-- Grandpa's Limp Left Arm Resting Asleep on His Lap Holding a Dripping Antique Brass Oil-Can! -->
    <g id="grandpa-left-arm">
      {draw_segmented_limb((1175, 765), (1152, 865), (1205, 955), 9, 36, 18, "url(#grandpaIron)")}
      <!-- Tilted Antique Brass Oil-Can Held in Limp Claw -->
      <g transform="translate(1208, 975) rotate(135)" filter="url(#tightShadow)">
        <path d="M -24 -12 L 24 -12 L 18 18 L -18 18 Z" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2.5"/>
        <path d="M -18 -12 A 18 12 0 0 1 18 -12 Z" fill="url(#grandpaCopper)" stroke="#1c150c" stroke-width="2.5"/>
        <!-- Long conical oil-can spout -->
        <polygon points="-4,-24 4,-24 2,-68 -2,-68" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2"/>
        <!-- Handle loop -->
        <path d="M 20 -4 C 34 -4 34 16 18 14" fill="none" stroke="url(#dadBrass)" stroke-width="4"/>
      </g>
      <!-- Droplet of dark motor oil falling from oil-can spout tip toward the floor puddle! -->
      <circle cx="1165" cy="1028" r="5" fill="#18242e" stroke="#38f2ff" stroke-width="1"/>
      <circle cx="1212" cy="962" r="18" fill="url(#grandpaCopper)" stroke="#1c120b" stroke-width="2.5"/>
    </g>

    <!-- Grandpa's Right Arm & Brass Walking Cane -->
    <g id="grandpa-arm-and-cane">
      {draw_segmented_limb((1415, 765), (1455, 865), (1425, 975), 10, 38, 19, "url(#grandpaIron)")}
      <path d="M 1392 985 C 1392 940 1448 940 1448 985 L 1422 1478" fill="none" stroke="url(#dadBrass)" stroke-width="14" stroke-linecap="round"/>
      <path d="M 1392 985 C 1392 940 1448 940 1448 985 L 1422 1478" fill="none" stroke="#241606" stroke-width="2.5" stroke-linecap="round"/>
      <rect x="1412" y="1465" width="20" height="22" rx="5" fill="#1f1d24" stroke="#0a090d" stroke-width="2"/>
      <circle cx="1422" cy="972" r="20" fill="url(#grandpaCopper)" stroke="#1c120b" stroke-width="2.5"/>
    </g>

    <!-- Grandpa's Tilted-Back Sleeping Tin-Can Head (+20 deg tilt!) -->
    {draw_segmented_limb((1298, 665), (1308, 630), (1318, 595), 4, 56, 16, "url(#darkPipe)")}
    <g id="grandpa-head" transform="translate(1325, 525) rotate(20)">
      <!-- Giant Brass Ear-Horn Hearing Trumpet sticking out left side toward Mom -->
      <g transform="translate(-85, 8) rotate(-12)">
        <path d="M 0 -10 L -75 -42 C -92 -48 -95 36 -75 28 L 0 10 Z" fill="url(#dadBrass)" stroke="#211607" stroke-width="3"/>
        <ellipse cx="-80" cy="-7" rx="12" ry="35" fill="#3b2308" stroke="url(#dadBrass)" stroke-width="4"/>
      </g>

      <rect x="-82" y="-78" width="164" height="152" rx="34" fill="url(#grandpaIron)" stroke="#141211" stroke-width="3.5"/>
      <path d="M -88 -58 Q 0 -88 88 -58 L 82 -42 Q 0 -68 -82 -42 Z" fill="url(#grandpaCopper)" stroke="#141211" stroke-width="2.5"/>
      <rect x="-16" y="-92" width="32" height="16" rx="4" fill="url(#grandpaCopper)" stroke="#141211" stroke-width="2"/>
      <path d="M -12 -92 A 12 16 0 0 1 12 -92 Z" fill="#38f2ff" fill-opacity="0.65" stroke="#b8f9ff" stroke-width="2"/>

      <!-- Unruly Bushy Silver Steel-Wool Eyebrows -->
      <path d="M -68 -28 Q -48 -48 -28 -32 Q -18 -45 -8 -26" fill="none" stroke="#d8e0e8" stroke-width="8" stroke-linecap="round"/>
      <path d="M -64 -24 Q -38 -40 -12 -24" fill="none" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round"/>
      <path d="M 8 -26 Q 28 -45 42 -32 Q 55 -48 68 -28" fill="none" stroke="#d8e0e8" stroke-width="8" stroke-linecap="round"/>
      <path d="M 12 -24 Q 38 -40 64 -24" fill="none" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round"/>

      <!-- Peacefully Closed Brass Shutter-Eyelids -->
      <circle cx="-38" cy="-4" r="24" fill="url(#grandpaCopper)" stroke="#141211" stroke-width="2.5"/>
      <path d="M -58 -4 Q -38 16 -18 -4" fill="none" stroke="#141211" stroke-width="4" stroke-linecap="round"/>
      <circle cx="38" cy="-4" r="24" fill="url(#grandpaCopper)" stroke="#141211" stroke-width="2.5"/>
      <path d="M 18 -4 Q 38 16 58 -4" fill="none" stroke="#141211" stroke-width="4" stroke-linecap="round"/>

      <!-- Whisker-like Copper Mustache & Slack Unhinged Snoring Jaw -->
      <path d="M -62 34 Q 0 16 62 34" fill="none" stroke="url(#grandpaCopper)" stroke-width="10" stroke-linecap="round"/>
      <rect x="-46" y="38" width="92" height="44" rx="10" fill="#120d0a" stroke="url(#grandpaCopper)" stroke-width="3"/>
      <g transform="rotate(6, -40, 62)">
        <rect x="-50" y="58" width="100" height="28" rx="8" fill="url(#grandpaIron)" stroke="#141211" stroke-width="3"/>
        <g stroke="#9e9a95" stroke-width="3">
          <line x1="-28" y1="58" x2="-28" y2="70"/>
          <line x1="-10" y1="58" x2="-10" y2="70"/>
          <line x1="10" y1="58" x2="10" y2="70"/>
          <line x1="28" y1="58" x2="28" y2="70"/>
        </g>
        <!-- Glossy Droplet of Dark Motor Oil Dribbling from Corner of Slack Jaw -->
        <path d="M 38 78 C 34 95 48 95 44 78 Z" fill="#18242e" stroke="#38f2ff" stroke-width="1" stroke-opacity="0.6"/>
        <circle cx="41" cy="102" r="4.5" fill="#18242e" stroke="#38f2ff" stroke-width="1" stroke-opacity="0.6"/>
      </g>
    </g>

    <!-- Floating Translucent Standby Sleep Bubbles Rising Above Grandpa's Head -->
    <g filter="url(#glowCyan)" opacity="0.78">
      <circle cx="1368" cy="422" r="8" fill="none" stroke="#7df9ff" stroke-width="2.5"/>
      <circle cx="1365" cy="419" r="2.5" fill="#ffffff"/>
      <circle cx="1392" cy="388" r="14" fill="none" stroke="#7df9ff" stroke-width="2.5"/>
      <circle cx="1387" cy="383" r="4" fill="#ffffff"/>
      <circle cx="1425" cy="342" r="21" fill="none" stroke="#7df9ff" stroke-width="2.5" stroke-dasharray="18,6"/>
      <circle cx="1418" cy="335" r="5.5" fill="#ffffff"/>
    </g>
  </g>

  <!-- ================= 7. MOM BOT (1950s Atomic-Age Mint Enamel & Chrome Matriarch) ================= -->
  <g id="mom-bot" filter="url(#dropShadow)">
    <!-- Mom's Graceful Tapered Chrome & Mint Legs -->
    <g id="mom-legs">
      <path d="M 920 1050 Q 905 1235 885 1435 L 918 1435 Q 942 1235 958 1050 Z"
            fill="url(#momMint)" stroke="#0e3b37" stroke-width="3"/>
      <circle cx="918" cy="1220" r="18" fill="url(#chromeGrad)" stroke="#16242b" stroke-width="2.5"/>
      <path d="M 985 1050 Q 972 1235 952 1445 L 985 1445 Q 1012 1235 1025 1050 Z"
            fill="url(#momMint)" stroke="#0e3b37" stroke-width="3"/>
      <circle cx="985" cy="1225" r="18" fill="url(#chromeGrad)" stroke="#16242b" stroke-width="2.5"/>

      <g transform="translate(895, 1445)">
        <path d="M -38 -12 C -32 -36 22 -36 28 -8 L 32 14 L -44 14 Z" fill="url(#chromeGrad)" stroke="#16242b" stroke-width="2.5"/>
        <circle cx="-12" cy="14" r="14" fill="#f7f9fc" stroke="#16242b" stroke-width="3"/>
        <circle cx="-12" cy="14" r="6" fill="url(#momMint)"/>
      </g>
      <g transform="translate(965, 1455)">
        <path d="M -35 -12 C -28 -36 25 -36 32 -8 L 36 14 L -40 14 Z" fill="url(#chromeGrad)" stroke="#16242b" stroke-width="2.5"/>
        <circle cx="-8" cy="14" r="14" fill="#f7f9fc" stroke="#16242b" stroke-width="3"/>
        <circle cx="-8" cy="14" r="6" fill="url(#momMint)"/>
      </g>
    </g>

    <!-- Mom's Sleek Mint-Enamel Left Arm Reaching Gently to Steady Sleeping Grandpa Bot's Shoulder -->
    {draw_hydraulic_cylinder((1075, 622), (1132, 655), 28, 24, "url(#momMint)", "url(#chromeGrad)")}
    <circle cx="1132" cy="655" r="15" fill="url(#chromeGrad)" stroke="#16242b" stroke-width="2.5"/>
    {draw_hydraulic_cylinder((1132, 655), (1188, 675), 24, 20, "url(#momMint)", "url(#chromeGrad)")}
    <g transform="translate(1196, 678) rotate(12)" filter="url(#tightShadow)">
      <ellipse cx="0" cy="0" rx="22" ry="14" fill="url(#momMint)" stroke="#0e3b37" stroke-width="2.5"/>
      <path d="M 14 -8 C 32 -4 34 12 18 14" fill="none" stroke="url(#chromeGrad)" stroke-width="7" stroke-linecap="round"/>
      <path d="M 10 4 C 28 12 26 24 12 22" fill="none" stroke="url(#chromeGrad)" stroke-width="6.5" stroke-linecap="round"/>
    </g>

    <!-- Mom's Curvy Hourglass 1950s Mint-Turquoise Enamel Torso & Chrome Peplum Skirt -->
    <g id="mom-torso">
      <path d="M 885 875 Q 975 855 1065 875 C 1105 945 1110 1025 1085 1065 Q 975 1088 865 1065 C 845 1025 850 945 885 875 Z"
            fill="url(#momMint)" stroke="#0e3b37" stroke-width="3.5"/>
      <path d="M 862 1045 Q 975 1072 1088 1045 L 1084 1065 Q 975 1092 866 1065 Z"
            fill="url(#chromeGrad)" stroke="#16242b" stroke-width="2.5"/>
      <ellipse cx="975" cy="875" rx="82" ry="18" fill="url(#chromeGrad)" stroke="#16242b" stroke-width="2.5"/>

      <path d="M 858 595 Q 975 572 1092 595 C 1082 695 1048 775 1045 865 Q 975 882 905 865 C 902 775 868 695 858 595 Z"
            fill="url(#momMint)" stroke="#0e3b37" stroke-width="3.5"/>
      <path d="M 865 605 C 820 570 812 625 858 655 Z" fill="url(#chromeGrad)" stroke="#16242b" stroke-width="2.5"/>
      <path d="M 1085 605 C 1130 570 1138 625 1092 655 Z" fill="url(#chromeGrad)" stroke="#16242b" stroke-width="2.5"/>

      <!-- Heart-Shaped Glowing Radar / Oscilloscope Locket Window on Chest -->
      <path d="M 975 725 C 975 725 928 690 928 662 C 928 642 952 635 975 656 C 998 635 1022 642 1022 662 C 1022 690 975 725 975 725 Z"
            fill="#09292c" stroke="url(#chromeGrad)" stroke-width="5"/>
      <path d="M 942 670 L 960 670 L 968 652 L 978 688 L 986 664 L 1008 664"
            fill="none" stroke="#7df9ff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" filter="url(#glowCyan)"/>
    </g>

    <!-- DAD BOT'S AWKWARD "HOVER-HAND" FLOATING IN CLEAR SPACE ABOVE MOM'S OUTER SHOULDER! -->
    <g id="dad-hover-hand" filter="url(#tightShadow)">
      {draw_segmented_limb((1065, 515), (1105, 502), (1135, 522), 5, 36, 17, "url(#dadBrass)")}
      <g transform="translate(1142, 530) rotate(22)">
        <rect x="-22" y="-18" width="44" height="28" rx="8" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2.5"/>
        <path d="M -18 8 C -34 26 -28 48 -12 52" fill="none" stroke="url(#dadBrass)" stroke-width="9.5" stroke-linecap="round"/>
        <path d="M 0 10 C -2 32 4 50 14 52" fill="none" stroke="url(#dadBrass)" stroke-width="9.5" stroke-linecap="round"/>
        <path d="M 16 6 C 28 22 36 38 28 48" fill="none" stroke="url(#dadBrass)" stroke-width="9" stroke-linecap="round"/>
      </g>
      {hover_sparks}
    </g>

    <!-- Mom's Graceful Neck & Frantic Steam-Relief Puff Valve (on LEFT side of neck for crisp silhouette!) -->
    <g id="mom-neck">
      {draw_segmented_limb((975, 590), (975, 565), (975, 540), 4, 44, 15, "url(#chromeGrad)")}
      <rect x="940" y="550" width="16" height="10" rx="3" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="1.8"/>
      <!-- Pressurized White Steam Puff Shooting Out Leftward! -->
      <g fill="#f0f8ff" fill-opacity="0.88" stroke="#9ad4eb" stroke-width="1.8">
        <path d="M 938 554 L 912 538 L 916 560 Z"/>
        <circle cx="904" cy="540" r="11"/>
        <circle cx="886" cy="532" r="15"/>
        <circle cx="892" cy="552" r="12"/>
        <circle cx="868" cy="526" r="18"/>
        <circle cx="872" cy="546" r="13"/>
      </g>
    </g>

    <!-- Mom's Head (Tilted -10 deg in a Forced Sweet Studio Portrait Pose!) -->
    <g id="mom-head" transform="translate(975, 475) rotate(-10)">
      <g id="mom-beehive-hair">
        <!-- Side Satellite-Dish Hair Buns -->
        <ellipse cx="-82" cy="-48" rx="22" ry="34" fill="url(#momCopperCoil)" stroke="#2b1104" stroke-width="2.5"/>
        <ellipse cx="82" cy="-48" rx="22" ry="34" fill="url(#momCopperCoil)" stroke="#2b1104" stroke-width="2.5"/>
        <line x1="-104" y1="-48" x2="-122" y2="-56" stroke="url(#chromeGrad)" stroke-width="4" stroke-linecap="round"/>
        <circle cx="-122" cy="-56" r="6" fill="#7df9ff" filter="url(#glowCyan)"/>

        <!-- Stacked Toroidal Copper Coils (Beehive Tiers) -->
        <ellipse cx="0" cy="-148" rx="34" ry="14" fill="url(#momCopperCoil)" stroke="#2b1104" stroke-width="2.5"/>
        <ellipse cx="0" cy="-130" rx="48" ry="16" fill="url(#momCopperCoil)" stroke="#2b1104" stroke-width="2.5"/>
        <ellipse cx="0" cy="-110" rx="62" ry="18" fill="url(#momCopperCoil)" stroke="#2b1104" stroke-width="2.5"/>
        <ellipse cx="0" cy="-88" rx="74" ry="20" fill="url(#momCopperCoil)" stroke="#2b1104" stroke-width="2.5"/>
        <ellipse cx="0" cy="-64" rx="82" ry="22" fill="url(#momCopperCoil)" stroke="#2b1104" stroke-width="2.5"/>
        <path d="M -82 -56 Q 0 -76 82 -56" fill="none" stroke="url(#chromeGrad)" stroke-width="8" stroke-linecap="round"/>

        <!-- Frazzled Capacitor Hairpin sticking out on right (drawn ON TOP of coils so stem is continuous!) -->
        <g transform="translate(52, -108) rotate(36)">
          <line x1="0" y1="18" x2="0" y2="-44" stroke="url(#chromeGrad)" stroke-width="5" stroke-linecap="round"/>
          <rect x="-9" y="-34" width="18" height="24" rx="5" fill="#ff4e9b" stroke="#1c0d18" stroke-width="2.2"/>
          <circle cx="0" cy="-46" r="7" fill="#38f2ff" stroke="#0e3b37" stroke-width="1.5" filter="url(#glowCyan)"/>
        </g>
      </g>

      <!-- Sleek Mid-Century Mint Enamel Head Shape -->
      <path d="M -78 -52 Q 0 -72 78 -52 C 88 12 68 68 0 74 C -68 68 -88 12 -78 -52 Z"
            fill="url(#momMint)" stroke="#0e3b37" stroke-width="3.5"/>
      <path d="M -78 -12 L -102 -22 L -92 14 L -74 18 Z" fill="url(#chromeGrad)" stroke="#16242b" stroke-width="2"/>
      <path d="M 78 -12 L 102 -22 L 92 14 L 74 18 Z" fill="url(#chromeGrad)" stroke="#16242b" stroke-width="2"/>

      <!-- Exhausted Half-Lidded Almond Eyes with Sweeping Chrome Eyelashes -->
      <g transform="translate(-34, -8)">
        <ellipse cx="0" cy="0" rx="25" ry="18" fill="url(#cyanLens)" stroke="#0e3b37" stroke-width="2.5"/>
        <circle cx="0" cy="2" r="8" fill="#001b2e"/>
        <circle cx="-5" cy="-1" r="4" fill="#ffffff"/>
        <path d="M -26 -2 A 25 18 0 0 1 26 -2 L 22 4 Q 0 -2 -26 -2 Z" fill="url(#momMint)" stroke="#0e3b37" stroke-width="2.5"/>
        <path d="M -25 -2 L -34 -10 M -18 -5 L -24 -14 M -8 -7 L -10 -16" stroke="#0e3b37" stroke-width="2.8" stroke-linecap="round"/>
        <path d="M -26 -22 Q -4 -32 20 -20" fill="none" stroke="#0e3b37" stroke-width="3.5" stroke-linecap="round"/>
      </g>
      <g transform="translate(34, -8)">
        <ellipse cx="0" cy="0" rx="25" ry="18" fill="url(#cyanLens)" stroke="#0e3b37" stroke-width="2.5"/>
        <circle cx="0" cy="2" r="8" fill="#001b2e"/>
        <circle cx="-5" cy="-1" r="4" fill="#ffffff"/>
        <path d="M -26 0 A 25 18 0 0 1 26 2 L 26 6 Q 0 0 -26 0 Z" fill="url(#momMint)" stroke="#0e3b37" stroke-width="2.5"/>
        <path d="M 25 0 L 34 -8 M 18 -4 L 24 -13 M 8 -6 L 10 -15" stroke="#0e3b37" stroke-width="2.8" stroke-linecap="round"/>
        <path d="M -20 -20 Q 4 -34 26 -18" fill="none" stroke="#0e3b37" stroke-width="3.5" stroke-linecap="round"/>
      </g>

      <ellipse cx="-48" cy="18" rx="14" ry="8" fill="#ff6b9d" fill-opacity="0.45" filter="url(#blurMed)"/>
      <ellipse cx="48" cy="18" rx="14" ry="8" fill="#ff6b9d" fill-opacity="0.45" filter="url(#blurMed)"/>

      <!-- Tight, Strained, Slightly Crooked Smile -->
      <path d="M -42 32 Q -5 48 44 26 Q 28 54 -4 52 Q -32 50 -42 32 Z" fill="#ffffff" stroke="url(#chromeGrad)" stroke-width="3"/>
      <path d="M -38 39 Q 0 48 39 33" fill="none" stroke="#0e3b37" stroke-width="2"/>
      <path d="M 46 20 Q 54 26 48 34" fill="none" stroke="#0e3b37" stroke-width="2.5" stroke-linecap="round"/>
    </g>
  </g>
"""


def create_toddler_and_mom_right_arm():
    """Creates Mom's pulled pearl necklace, the chaotic Toddler Bot on her lap, and Mom's right mint-enamel arm holding it."""
    necklace_pts = [
        (930, 578), (925, 602), (921, 626), (917, 650), (913, 675), (910, 700), (908, 725), (908, 748),
        (926, 732), (945, 710), (964, 686), (982, 662), (998, 636), (1012, 608), (1022, 582)
    ]
    pearls = ['<path d="M 930 575 L 908 752 L 1024 578" fill="none" stroke="#d8f0ff" stroke-width="3"/>']
    for px, py in necklace_pts:
        pearls.append(f'<circle cx="{px}" cy="{py}" r="10.5" fill="url(#pearlBearing)" stroke="#16242b" stroke-width="2"/>')

    toddler_spark = draw_spark([(992, 988), (976, 1006), (958, 995), (940, 1008)], "#ffe066", "#ffffff", 4.5)

    return f"""
  <!-- ================= 8. TODDLER BOT (Chaotic Upside-Down Gremlin on Mom's Lap) ================= -->
  <g id="toddler-bot-and-mom-arm" filter="url(#dropShadow)">
    <!-- Mom's Ball-Bearing Pearl Necklace (Pulled Taut into a V!) -->
    <g id="mom-necklace">
      {''.join(pearls)}
    </g>

    <!-- Mom's Right Upper Arm & Forearm (drawn behind Toddler's diaper so diaper & legs are 100% unobstructed!) -->
    <g id="mom-right-arm-segments">
      {draw_hydraulic_cylinder((862, 622), (822, 725), 28, 24, "url(#momMint)", "url(#chromeGrad)")}
      <circle cx="822" cy="725" r="16" fill="url(#chromeGrad)" stroke="#16242b" stroke-width="2.5"/>
      {draw_hydraulic_cylinder((822, 725), (892, 835), 24, 22, "url(#momMint)", "url(#chromeGrad)")}
    </g>

    <!-- Toddler's Lower Leg Kicking Downward/Left Out of Diaper Pelvis -->
    {draw_segmented_limb((832, 882), (806, 928), (788, 975), 6, 24, 15, "url(#chromeGrad)")}
    <g transform="translate(784, 982) rotate(155)">
      <path d="M -24 0 A 24 18 0 0 1 24 0 Z" fill="#289c90" stroke="#0e3b37" stroke-width="2.5"/>
      <rect x="-11" y="0" width="22" height="9" rx="3" fill="url(#toddlerCoral)" stroke="#2b0c04" stroke-width="2"/>
    </g>

    <!-- Toddler's Upper Leg Planted with a Suction-Cup Foot Directly onto Dad Bot's Lower Console! -->
    {draw_segmented_limb((825, 840), (788, 825), (755, 818), 6, 24, 15, "url(#chromeGrad)")}
    <g transform="translate(746, 816) rotate(-90)">
      <ellipse cx="0" cy="8" rx="30" ry="9" fill="#00f2fe" fill-opacity="0.28"/>
      <path d="M -26 6 C -22 -16 22 -16 26 6 Z" fill="#289c90" stroke="#0e3b37" stroke-width="2.5"/>
      <line x1="-28" y1="6" x2="28" y2="6" stroke="#7df9ff" stroke-width="3.5" stroke-linecap="round"/>
      <rect x="-11" y="-16" width="22" height="10" rx="3" fill="url(#toddlerCoral)" stroke="#2b0c04" stroke-width="2"/>
    </g>

    <!-- Toddler's Tilted / Half-Upside-Down Coral & Steel Diaper Chassis -->
    <g id="toddler-body" transform="translate(876, 872) rotate(125)">
      <!-- Riveted Steel "Diaper" Pelvis (Now 100% visible in foreground!) -->
      <path d="M -54 12 C -58 70 58 70 54 12 L 44 -12 L -44 -12 Z"
            fill="url(#toddlerDiaper)" stroke="#1e242b" stroke-width="3"/>
      <!-- Giant Oversized Chrome Safety-Pin on Diaper -->
      <rect x="-28" y="20" width="56" height="14" rx="7" fill="none" stroke="url(#chromeGrad)" stroke-width="4"/>
      <ellipse cx="-24" cy="27" rx="10" ry="8" fill="url(#dadBrass)" stroke="#1e242b" stroke-width="2"/>

      <!-- Round Coral-Orange Belly -->
      <ellipse cx="0" cy="-26" rx="56" ry="48" fill="url(#toddlerCoral)" stroke="#2b0c04" stroke-width="3"/>
      <!-- Winding Key sticking out of Toddler's back/side -->
      <g transform="translate(-56, -26)">
        <rect x="-18" y="-5" width="18" height="10" rx="3" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2"/>
        <circle cx="-26" cy="-14" r="12" fill="none" stroke="url(#dadBrass)" stroke-width="5"/>
        <circle cx="-26" cy="14" r="12" fill="none" stroke="url(#dadBrass)" stroke-width="5"/>
      </g>
      <circle cx="0" cy="-28" r="5" fill="#2b0c04"/>
      <circle cx="-16" cy="-24" r="4.5" fill="#2b0c04"/>
      <circle cx="16" cy="-24" r="4.5" fill="#2b0c04"/>
      <circle cx="-8" cy="-38" r="4.5" fill="#2b0c04"/>
      <circle cx="8" cy="-38" r="4.5" fill="#2b0c04"/>
    </g>

    <!-- Mom's Mint & Chrome Hand Clasping Toddler Bot's Coral Belly -->
    <g transform="translate(896, 845) rotate(22)" filter="url(#tightShadow)">
      <ellipse cx="0" cy="0" rx="24" ry="15" fill="url(#momMint)" stroke="#0e3b37" stroke-width="2.5"/>
      <path d="M 12 -10 C 34 -12 38 6 20 12" fill="none" stroke="url(#chromeGrad)" stroke-width="7" stroke-linecap="round"/>
      <path d="M 10 4 C 30 8 30 22 14 22" fill="none" stroke="url(#chromeGrad)" stroke-width="6.5" stroke-linecap="round"/>
    </g>

    <!-- Toddler's Left Arm Yanking Taut on Mom's Pearl Necklace at (908, 752)! -->
    {draw_segmented_limb((898, 835), (906, 795), (908, 758), 6, 22, 13, "url(#toddlerCoral)")}
    <g transform="translate(908, 752) rotate(-15)">
      <circle cx="0" cy="0" r="13" fill="url(#chromeGrad)" stroke="#1e242b" stroke-width="2.5"/>
      <path d="M -10 -4 C -16 -20 16 -20 10 -4" fill="none" stroke="url(#chromeGrad)" stroke-width="5.5" stroke-linecap="round"/>
    </g>

    <!-- Toddler's Right Arm Flailing Outward Holding a Magnetic Pacifier Plug -->
    {draw_segmented_limb((922, 898), (962, 925), (1005, 905), 6, 22, 13, "url(#toddlerCoral)")}
    <g transform="translate(1015, 902) rotate(25)">
      <circle cx="0" cy="0" r="14" fill="#38f2ff" stroke="#0e3b37" stroke-width="2.5"/>
      <circle cx="12" cy="0" r="11" fill="none" stroke="url(#dadBrass)" stroke-width="4"/>
      <rect x="-18" y="-6" width="12" height="12" rx="2" fill="url(#chromeGrad)" stroke="#1e242b" stroke-width="2"/>
    </g>

    <!-- Toddler's Upside-Down Googly-Eyed Head at (942, 938) -->
    <g id="toddler-head" transform="translate(942, 938) rotate(148)">
      <line x1="-22" y1="-50" x2="-35" y2="-78" stroke="url(#chromeGrad)" stroke-width="4.5" stroke-linecap="round"/>
      <circle cx="-35" cy="-78" r="7" fill="#ffe066" stroke="#2b0c04" stroke-width="2"/>
      <line x1="22" y1="-50" x2="35" y2="-78" stroke="url(#chromeGrad)" stroke-width="4.5" stroke-linecap="round"/>
      <circle cx="35" cy="-78" r="7" fill="#ffe066" stroke="#2b0c04" stroke-width="2"/>

      <rect x="-56" y="-52" width="112" height="96" rx="42" fill="url(#toddlerCoral)" stroke="#2b0c04" stroke-width="3"/>
      <rect x="-44" y="-38" width="88" height="68" rx="28" fill="#261310" stroke="url(#chromeGrad)" stroke-width="2.5"/>

      <!-- Wildly Mismatched Googly Camera Eyes -->
      <circle cx="-18" cy="-12" r="21" fill="url(#amberLens)" stroke="url(#chromeGrad)" stroke-width="3"/>
      <circle cx="-24" cy="-18" r="8" fill="#1a0900"/>
      <circle cx="-27" cy="-21" r="4" fill="#ffffff"/>
      <circle cx="22" cy="-10" r="15" fill="url(#cyanLens)" stroke="url(#chromeGrad)" stroke-width="3"/>
      <circle cx="27" cy="-5" r="6" fill="#001829"/>
      <circle cx="25" cy="-7" r="3" fill="#ffffff"/>

      <path d="M -28 12 Q 0 38 28 12 Q 0 18 -28 12 Z" fill="#38f2ff" stroke="#ffffff" stroke-width="2" filter="url(#glowCyan)"/>
      <rect x="-14" y="14" width="8" height="7" rx="1" fill="#ffffff"/>
      <rect x="4" y="14" width="8" height="7" rx="1" fill="#ffffff"/>
    </g>
    {toddler_spark}
  </g>
"""


def create_middle_child_nerd_bot():
    """Creates the Over-Eager 1980s Middle-Child Nerd Bot standing on a studio apple-box in a cheesy Chin-on-Hands pose."""
    return f"""
  <!-- ================= 9. MIDDLE-CHILD NERD BOT (Over-Eager 1980s Camera-Nerd Bot, Front-Left) ================= -->
  <g id="middle-child-nerd-bot" filter="url(#dropShadow)">
    <!-- Studio Wooden "Apple Box" Posing Crate on Floor -->
    <g id="studio-apple-box">
      <polygon points="435,1385 675,1385 695,1415 415,1415" fill="#8c5828" stroke="#241304" stroke-width="3"/>
      <rect x="415" y="1415" width="280" height="78" rx="4" fill="url(#dadWalnut)" stroke="#241304" stroke-width="3"/>
      <rect x="515" y="1438" width="80" height="24" rx="12" fill="#1f0e03" stroke="#593512" stroke-width="2"/>
      <line x1="425" y1="1432" x2="685" y2="1432" stroke="#3b1e08" stroke-width="2"/>
      <line x1="425" y1="1472" x2="685" y2="1472" stroke="#3b1e08" stroke-width="2"/>
    </g>

    <!-- Middle-Child's Short Springy Legs Standing on Tiptoes on the Apple Box -->
    <g id="nerd-legs">
      {draw_segmented_limb((510, 1145), (502, 1265), (505, 1380), 11, 34, 18, "url(#nerdBlue)")}
      {draw_segmented_limb((600, 1145), (608, 1265), (605, 1380), 11, 34, 18, "url(#nerdBlue)")}
      <path d="M 462 1380 C 462 1352 542 1352 542 1380 L 548 1404 L 455 1404 Z" fill="url(#nerdYellow)" stroke="#1c1604" stroke-width="3"/>
      <rect x="452" y="1396" width="98" height="12" rx="5" fill="url(#nerdBlue)" stroke="#091936" stroke-width="2"/>
      <path d="M 568 1380 C 568 1352 648 1352 648 1380 L 655 1404 L 562 1404 Z" fill="url(#nerdYellow)" stroke="#1c1604" stroke-width="3"/>
      <rect x="560" y="1396" width="98" height="12" rx="5" fill="url(#nerdBlue)" stroke="#091936" stroke-width="2"/>
    </g>

    <!-- Middle-Child's Compact Cylindrical Yellow & Cobalt-Blue Torso -->
    <g id="nerd-torso">
      <path d="M 468 1085 L 642 1085 L 622 1158 L 488 1158 Z" fill="url(#nerdBlue)" stroke="#091936" stroke-width="3"/>
      <rect x="458" y="882" width="194" height="215" rx="32" fill="url(#nerdYellow)" stroke="#291d02" stroke-width="3.5"/>
      <!-- Cobalt Blue Overalls-Style Chest Bib & Straps -->
      <path d="M 485 885 L 512 885 L 512 945 L 598 945 L 598 885 L 625 885 L 625 1075 L 485 1075 Z"
            fill="url(#nerdBlue)" stroke="#091936" stroke-width="3" stroke-linejoin="round"/>
      <circle cx="498" cy="925" r="8" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2"/>
      <circle cx="612" cy="925" r="8" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2"/>

      <!-- Nerdy Plastic Pocket-Protector with Mini Screwdrivers & Glowing Logic Probe -->
      <g transform="translate(575, 995)">
        <rect x="-24" y="-36" width="7" height="24" rx="2" fill="#ff3b30" stroke="#141414" stroke-width="1.5"/>
        <rect x="-12" y="-42" width="7" height="30" rx="2" fill="#34c759" stroke="#141414" stroke-width="1.5"/>
        <line x1="4" y1="-12" x2="8" y2="-45" stroke="url(#chromeGrad)" stroke-width="4" stroke-linecap="round"/>
        <circle cx="8" cy="-46" r="5" fill="#38f2ff" filter="url(#glowCyan)"/>
        <path d="M -32 -16 L 24 -16 L 24 28 C 24 38 -32 38 -32 28 Z" fill="#e8f4fc" stroke="#1c2d42" stroke-width="2.5"/>
        <path d="M -32 -16 L 24 -16 L 24 -4 L -32 -4 Z" fill="#b8d4e8" stroke="#1c2d42" stroke-width="2"/>
      </g>

      <!-- Glowing Equalizer / Floppy-Drive Slot on Left Chest -->
      <rect x="500" y="975" width="34" height="58" rx="6" fill="#0c192e" stroke="#5ca9ff" stroke-width="2"/>
      <rect x="506" y="984" width="22" height="8" rx="2" fill="#39ff14"/>
      <rect x="506" y="998" width="22" height="8" rx="2" fill="#ffe066"/>
      <rect x="506" y="1012" width="22" height="8" rx="2" fill="#ff3b30"/>
    </g>

    <!-- Middle-Child's Accordion Neck -->
    {draw_segmented_limb((555, 888), (555, 862), (555, 838), 4, 52, 15, "url(#darkPipe)")}

    <!-- Middle-Child's Eagerly Tilted Dome Head (+5 deg) with Taped Square Binocular Glasses! -->
    <g id="nerd-head" transform="translate(555, 775) rotate(5)">
      <!-- Cute Spring Propeller Beanie on Top-Right of Dome Head (right beside Teen Bot's Prank Bunny-Ears!) -->
      <path d="M -22 -84 C -22 -98 22 -98 22 -84 Z" fill="url(#nerdBlue)" stroke="#091936" stroke-width="2.5"/>
      <line x1="0" y1="-92" x2="10" y2="-122" stroke="url(#chromeGrad)" stroke-width="6" stroke-linecap="round"/>
      <g transform="translate(12, -124) rotate(8)">
        <ellipse cx="-26" cy="0" rx="26" ry="7" fill="#ff3b30" stroke="#1c0d0b" stroke-width="2"/>
        <ellipse cx="26" cy="0" rx="26" ry="7" fill="#38f2ff" stroke="#0b1c24" stroke-width="2"/>
        <circle cx="0" cy="0" r="9" fill="url(#nerdYellow)" stroke="#1c1604" stroke-width="2"/>
      </g>

      <!-- Canary Yellow Dome Head -->
      <path d="M -86 -25 C -86 -108 86 -108 86 -25 L 86 58 C 86 84 -86 84 -86 58 Z"
            fill="url(#nerdYellow)" stroke="#291d02" stroke-width="3.5"/>
      <!-- Side Ear-Bolts -->
      <rect x="-102" y="-12" width="16" height="36" rx="6" fill="url(#nerdBlue)" stroke="#091936" stroke-width="2.5"/>
      <rect x="86" y="-12" width="16" height="36" rx="6" fill="url(#nerdBlue)" stroke="#091936" stroke-width="2.5"/>

      <!-- Oversized Thick-Framed Square "Nerd Glasses" with Silver Duct Tape on the Bridge! -->
      <g id="nerd-glasses" filter="url(#tightShadow)">
        <rect x="-82" y="-48" width="72" height="66" rx="10" fill="#181c24" stroke="#0a0c10" stroke-width="3"/>
        <rect x="-74" y="-40" width="56" height="50" rx="6" fill="url(#amberLens)"/>
        <rect x="10" y="-48" width="72" height="66" rx="10" fill="#181c24" stroke="#0a0c10" stroke-width="3"/>
        <rect x="18" y="-40" width="56" height="50" rx="6" fill="url(#amberLens)"/>
        <rect x="-14" y="-26" width="28" height="14" rx="2" fill="#181c24"/>
        <!-- Crinkled Silver Duct-Tape Wrapped Around the Bridge -->
        <polygon points="-9,-30 9,-28 11,-8 -7,-10" fill="#d8e0e8" stroke="#5c6670" stroke-width="2"/>
        <line x1="-6" y1="-25" x2="7" y2="-13" stroke="#8b96a3" stroke-width="1.5"/>

        <!-- Giant Starry-Eyed Over-Eager Camera Apertures Inside the Glasses -->
        <circle cx="-44" cy="-15" r="16" fill="#240b00"/>
        <circle cx="-50" cy="-22" r="7.5" fill="#ffffff"/>
        <circle cx="-36" cy="-8" r="4" fill="#fff3b0"/>

        <circle cx="44" cy="-15" r="16" fill="#240b00"/>
        <circle cx="38" cy="-22" r="7.5" fill="#ffffff"/>
        <circle cx="52" cy="-8" r="4" fill="#fff3b0"/>

        <polygon points="-70,-38 -52,-38 -64,6 -70,6" fill="#ffffff" fill-opacity="0.25"/>
        <polygon points="22,-38 40,-38 28,6 22,6" fill="#ffffff" fill-opacity="0.25"/>
      </g>

      <!-- Joyful Wide LED Mouth Screen with Glowing Green Zigzag Smile! -->
      <path d="M -56 26 L 56 26 L 46 64 L -46 64 Z" fill="#072112" stroke="#181c24" stroke-width="3" stroke-linejoin="round"/>
      <path d="M -44 40 L -28 54 L -14 38 L 0 54 L 14 38 L 28 54 L 44 40"
            fill="none" stroke="#39ff14" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#glowWarm)"/>
    </g>

    <!-- THE CHEESY OLAN MILLS "CHIN-ON-HANDS" POSE! -->
    {draw_segmented_limb((462, 915), (412, 995), (512, 858), 11, 28, 16, "url(#nerdBlue)")}
    {draw_segmented_limb((648, 915), (698, 995), (598, 862), 11, 28, 16, "url(#nerdBlue)")}
    <!-- Cupped Yellow Pincer Hands Propping Up His Chin -->
    <g transform="translate(514, 852) rotate(-20)" filter="url(#tightShadow)">
      <path d="M -24 6 C -26 -18 18 -18 20 6 Z" fill="url(#nerdYellow)" stroke="#291d02" stroke-width="2.5"/>
      <path d="M -22 -2 C -32 -18 -8 -26 4 -12" fill="none" stroke="url(#nerdYellow)" stroke-width="8" stroke-linecap="round"/>
    </g>
    <g transform="translate(596, 856) rotate(20)" filter="url(#tightShadow)">
      <path d="M -20 6 C -18 -18 26 -18 24 6 Z" fill="url(#nerdYellow)" stroke="#291d02" stroke-width="2.5"/>
      <path d="M 22 -2 C 32 -18 8 -26 -4 -12" fill="none" stroke="url(#nerdYellow)" stroke-width="8" stroke-linecap="round"/>
    </g>
  </g>
"""


def create_pet_bot_and_floor_chaos():
    """Creates the Robotic Toaster-Pug Family Pet, the Oil Puddle, Tangled Power Cords, and Sparking Power Strip."""
    strip_sparks = (
        draw_spark([(295, 1582), (282, 1548), (302, 1528), (288, 1502)], "#ffe066", "#ffffff", 4.2) +
        draw_spark([(328, 1585), (348, 1554), (336, 1536), (358, 1512)], "#38f2ff", "#ffffff", 4.0)
    )

    return f"""
  <!-- ================= 10. FOREGROUND PET BOT, OIL PUDDLE & TANGLED POWER CORDS ================= -->
  <g id="foreground-pet-and-cords">
    <!-- Glossy Dark Iridescent Motor-Oil Puddle Under Grandpa & Pet Bot -->
    <g id="oil-puddle">
      <path d="M 885 1555 C 865 1528 965 1515 1065 1525 C 1175 1515 1265 1535 1245 1568 C 1225 1595 1105 1605 1015 1592 C 935 1602 895 1582 885 1555 Z"
            fill="url(#oilSlick)" stroke="#2b394a" stroke-width="2"/>
      <path d="M 935 1552 Q 1025 1538 1125 1552" fill="none" stroke="#4facfe" stroke-opacity="0.38" stroke-width="5" stroke-linecap="round"/>
      <path d="M 1045 1570 Q 1125 1562 1195 1572" fill="none" stroke="#ff4e9b" stroke-opacity="0.32" stroke-width="4" stroke-linecap="round"/>

      <!-- Loose Hardware Dropped on the Studio Floor (Hex Nut, Washer & Coil Spring) -->
      <polygon points="1165,1562 1179,1555 1193,1562 1193,1576 1179,1583 1165,1576" fill="url(#dadBrass)" stroke="#1a140b" stroke-width="2"/>
      <circle cx="1179" cy="1569" r="5.5" fill="#120d1c"/>
      <path d="M 1218 1545 C 1225 1530 1235 1558 1242 1545 C 1249 1530 1259 1558 1266 1545" fill="none" stroke="url(#chromeGrad)" stroke-width="4.5" stroke-linecap="round"/>
    </g>

    <!-- Heavy Black Power Cords Snaking from Dad & Mom's Feet Across the Floor -->
    <g id="power-cords-back" fill="none" stroke-linecap="round">
      <path d="M 615 1448 C 655 1525 405 1535 390 1490 C 375 1445 660 1565 875 1515"
            stroke="#14131a" stroke-width="14"/>
      <path d="M 615 1448 C 655 1525 405 1535 390 1490 C 375 1445 660 1565 875 1515"
            stroke="#454354" stroke-width="3" stroke-dasharray="18,12"/>
    </g>

    <!-- THE FAMILY PET: Robotic Toaster-Pug / Cyber-Terrier (Front Center) -->
    <g id="pet-bot" filter="url(#dropShadow)">
      <!-- Wagging Coiled Spring Tail with Glowing Bulb Tip -->
      <path d="M 1062 1415 C 1095 1395 1075 1365 1108 1355 C 1135 1348 1110 1320 1138 1308"
            fill="none" stroke="url(#chromeGrad)" stroke-width="7" stroke-linecap="round"/>
      <circle cx="1142" cy="1304" r="12" fill="#ffe066" stroke="#2b1e04" stroke-width="2.5" filter="url(#glowWarm)"/>

      <!-- Squat Rounded Chrome Toaster Body -->
      <rect x="855" y="1375" width="215" height="122" rx="42" fill="url(#petSilver)" stroke="#1c2229" stroke-width="3.5"/>
      <rect x="915" y="1380" width="95" height="12" rx="5" fill="#ff5500" stroke="#2b1204" stroke-width="2" filter="url(#glowWarm)"/>
      <rect x="925" y="1398" width="85" height="8" rx="4" fill="#ff9900" stroke="#2b1204" stroke-width="1.5"/>
      <line x1="1045" y1="1425" x2="1045" y2="1475" stroke="#1c2229" stroke-width="6" stroke-linecap="round"/>
      <rect x="1042" y="1430" width="26" height="14" rx="5" fill="#c92a2a" stroke="#1c2229" stroke-width="2"/>

      <!-- Pet's Hind Leg & Paw -->
      <path d="M 1015 1465 L 1055 1465 L 1068 1538 L 1005 1538 Z" fill="url(#chromeGrad)" stroke="#1c2229" stroke-width="3" stroke-linejoin="round"/>
      <ellipse cx="1038" cy="1542" rx="34" ry="14" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2.5"/>

      <!-- Pet's Front Legs -->
      <path d="M 868 1465 L 906 1465 L 898 1548 L 855 1548 Z" fill="url(#chromeGrad)" stroke="#1c2229" stroke-width="3" stroke-linejoin="round"/>
      <ellipse cx="876" cy="1552" rx="32" ry="14" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2.5"/>

      <path d="M 948 1465 L 986 1465 L 995 1548 L 952 1548 Z" fill="url(#chromeGrad)" stroke="#1c2229" stroke-width="3" stroke-linejoin="round"/>
      <ellipse cx="974" cy="1552" rx="32" ry="14" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2.5"/>

      <!-- TANGLED POWER CORD WRAPPED AROUND PET BOT'S FRONT LEGS! -->
      <path d="M 852 1505 C 915 1535 998 1485 1002 1515 C 1006 1545 845 1535 848 1518 C 852 1500 620 1635 365 1598"
            fill="none" stroke="#14131a" stroke-width="14" stroke-linecap="round"/>
      <path d="M 852 1505 C 915 1535 998 1485 1002 1515 C 1006 1545 845 1535 848 1518 C 852 1500 620 1635 365 1598"
            fill="none" stroke="#4e4b61" stroke-width="3" stroke-dasharray="16,12" stroke-linecap="round"/>

      <!-- Pet's Red Collar with Gold Gear Tag -->
      <path d="M 862 1398 Q 925 1435 985 1398" fill="none" stroke="#e03131" stroke-width="14" stroke-linecap="round"/>
      <circle cx="925" cy="1428" r="14" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2.5"/>
      <circle cx="925" cy="1428" r="5" fill="#1c150c"/>

      <!-- Pet's Tilted Pug Head (+7 deg) Clamping a Shiny Chrome Wrench in Its Jaws! -->
      <g id="pet-head" transform="translate(922, 1345) rotate(7)">
        <path d="M -68 -42 L -108 -18 L -92 32 L -62 8 Z" fill="url(#grandpaIron)" stroke="#141211" stroke-width="3" stroke-linejoin="round"/>
        <path d="M 68 -42 L 108 -24 L 98 26 L 62 4 Z" fill="url(#grandpaIron)" stroke="#141211" stroke-width="3" stroke-linejoin="round"/>
        <circle cx="-68" cy="-35" r="5" fill="url(#dadBrass)"/>
        <circle cx="68" cy="-35" r="5" fill="url(#dadBrass)"/>

        <rect x="-72" y="-58" width="144" height="114" rx="36" fill="url(#petSilver)" stroke="#1c2229" stroke-width="3.5"/>
        <path d="M -28 -42 Q 0 -32 28 -42" fill="none" stroke="#3c4652" stroke-width="3" stroke-linecap="round"/>
        <path d="M -18 -32 Q 0 -24 18 -32" fill="none" stroke="#3c4652" stroke-width="2.5" stroke-linecap="round"/>

        <!-- Shiny Chrome Box-Wrench Clamped Horizontally in Pet's Jaws -->
        <g transform="translate(8, 38) rotate(-8)" filter="url(#tightShadow)">
          <rect x="-95" y="-8" width="190" height="16" rx="5" fill="url(#chromeGrad)" stroke="#161920" stroke-width="2.5"/>
          <path d="M -92 -18 C -122 -22 -122 22 -92 18 L -92 8 L -106 8 L -106 -8 L -92 -8 Z" fill="url(#chromeGrad)" stroke="#161920" stroke-width="2.5"/>
          <path d="M 92 -18 C 122 -22 122 22 92 18 L 92 8 L 106 8 L 106 -8 L 92 -8 Z" fill="url(#chromeGrad)" stroke="#161920" stroke-width="2.5"/>
        </g>

        <rect x="-48" y="4" width="96" height="46" rx="20" fill="url(#grandpaIron)" stroke="#141211" stroke-width="3"/>
        <rect x="-32" y="34" width="12" height="10" rx="2" fill="#ffffff" stroke="#1c2229" stroke-width="2"/>
        <rect x="-14" y="34" width="12" height="10" rx="2" fill="#ffffff" stroke="#1c2229" stroke-width="2"/>
        <rect x="4" y="34" width="12" height="10" rx="2" fill="#ffffff" stroke="#1c2229" stroke-width="2"/>
        <rect x="22" y="34" width="12" height="10" rx="2" fill="#ffffff" stroke="#1c2229" stroke-width="2"/>
        <!-- Pink Sheet-Metal Tongue -->
        <path d="M -38 42 C -46 68 -16 72 -18 44 Z" fill="#ff5ca8" stroke="#590d2e" stroke-width="2.5"/>
        <line x1="-29" y1="45" x2="-31" y2="58" stroke="#b81d62" stroke-width="2" stroke-linecap="round"/>

        <ellipse cx="0" cy="10" rx="16" ry="12" fill="url(#redNose)" stroke="#2b0000" stroke-width="2.5"/>
        <ellipse cx="-5" cy="6" rx="5" ry="3" fill="#ffffff" fill-opacity="0.8"/>

        <!-- Huge Bulging Glass-Dome Eyes Looking Cross-Eyed at Nose -->
        <g transform="translate(-38, -12)">
          <circle cx="0" cy="0" r="24" fill="url(#cyanLens)" stroke="url(#chromeGrad)" stroke-width="3.5"/>
          <circle cx="8" cy="5" r="9" fill="#001829"/>
          <circle cx="4" cy="1" r="4.5" fill="#ffffff"/>
        </g>
        <g transform="translate(38, -12)">
          <circle cx="0" cy="0" r="24" fill="url(#cyanLens)" stroke="url(#chromeGrad)" stroke-width="3.5"/>
          <circle cx="-8" cy="5" r="9" fill="#001829"/>
          <circle cx="-11" cy="1" r="4.5" fill="#ffffff"/>
        </g>
      </g>
    </g>

    <!-- Overloaded Sparking Studio Power Strip on Bottom-Left Floor -->
    <g id="floor-power-strip" filter="url(#tightShadow)">
      <polygon points="225,1585 378,1575 392,1609 212,1619" fill="url(#nerdYellow)" stroke="#1c1504" stroke-width="3" stroke-linejoin="round"/>
      <polygon points="212,1619 392,1609 392,1627 212,1637" fill="#8c5800" stroke="#1c1504" stroke-width="2.5" stroke-linejoin="round"/>
      <rect x="232" y="1592" width="18" height="12" rx="2" fill="#ff2a2a" stroke="#2b0000" stroke-width="1.5" filter="url(#glowWarm)"/>
      <rect x="268" y="1569" width="24" height="28" rx="5" fill="#1e202b" stroke="#0a0b10" stroke-width="2.5"/>
      <rect x="304" y="1565" width="24" height="28" rx="5" fill="#2b2d3c" stroke="#0a0b10" stroke-width="2.5"/>
      <rect x="342" y="1567" width="24" height="26" rx="5" fill="#1e202b" stroke="#0a0b10" stroke-width="2.5"/>
      <path d="M 212 1622 Q 110 1642 0 1612" fill="none" stroke="#14131a" stroke-width="14"/>
      {strip_sparks}
    </g>
  </g>
"""


def create_studio_foreground_and_vignette():
    """Adds a studio flash umbrella edge in the upper-right corner, lighting bloom, and portrait vignette."""
    return """
  <!-- ================= 11. STUDIO FLASH UMBRELLA & PORTRAIT VIGNETTE ================= -->
  <g id="studio-foreground">
    <!-- Studio Strobe Reflector Umbrella Peeking in at Top-Right Corner -->
    <g id="studio-strobe-umbrella" filter="url(#dropShadow)">
      <line x1="1600" y1="260" x2="1445" y2="115" stroke="url(#chromeGrad)" stroke-width="10" stroke-linecap="round"/>
      <circle cx="1445" cy="115" r="12" fill="url(#dadBrass)" stroke="#1c150c" stroke-width="2.5"/>
      <path d="M 1455 -20 C 1495 45 1555 135 1620 185 L 1620 -20 Z" fill="#161821" stroke="#383e4d" stroke-width="3"/>
      <path d="M 1455 -20 C 1475 55 1525 135 1620 185 C 1565 165 1485 95 1455 -20 Z" fill="url(#chromeGrad)" stroke="#282d38" stroke-width="2.5"/>
      <circle cx="1475" cy="85" r="35" fill="#ffffff" fill-opacity="0.65" filter="url(#blurMed)"/>
      <circle cx="1475" cy="85" r="12" fill="#ffffff"/>
    </g>

    <!-- Subtle Warm Key-Light Bloom on Upper Left -->
    <circle cx="180" cy="180" r="260" fill="#fff5d6" fill-opacity="0.08" filter="url(#blurSoft)"/>

    <!-- Full-Canvas Studio Portrait Vignette -->
    <rect x="0" y="0" width="1600" height="1800" fill="url(#vignetteGrad)" pointer-events="none"/>
  </g>
"""


def generate_svg():
    svg_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1800" width="1600" height="1800">',
        create_defs(),
        '  <clipPath id="backdropClip">',
        '    <path d="M 115 58 L 1485 44 L 1485 1290 L 115 1290 Z"/>',
        '  </clipPath>',
        create_studio_and_backdrop(),
        create_settee_back(),
        create_dad_bot(),
        create_teen_bot(),
        create_settee_seat_and_grandpa_and_mom(),
        create_toddler_and_mom_right_arm(),
        create_middle_child_nerd_bot(),
        create_pet_bot_and_floor_chaos(),
        create_studio_foreground_and_vignette(),
        '</svg>'
    ]
    return "\n".join(svg_parts)


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", "awkward_robot_family_portrait.svg")
    svg_content = generate_svg()
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Wrote {len(svg_content)} bytes to {out_path}")
