#!/usr/bin/env python3
"""
generate.py - Produces an intricate, expressive SVG of an awkward family portrait of robots.
Strictly adheres to:
- No text elements or letterforms anywhere.
- Output saved in ./output/awkward_robot_family_portrait.svg.
- Clean standard W3C SVG.
"""

import math
import os
import sys

def build_svg():
    width = 1400
    height = 1050

    svg = []
    def emit(s):
        svg.append(s)

    emit(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    
    # =========================================================================
    # DEFS SECTION: Gradients, Patterns, Shadows (Universally supported)
    # =========================================================================
    emit('<defs>')
    
    # Universal Drop Shadows & Blur
    emit('''
    <filter id="soft-shadow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="10"/>
      <feOffset dx="0" dy="12"/>
      <feComponentTransfer><feFuncA type="linear" slope="0.55"/></feComponentTransfer>
      <feMerge>
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="floor-blur" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="8"/>
    </filter>
    ''')

    # Studio Backdrop & Floor Gradients
    emit('''
    <!-- Studio Backdrop Vignette -->
    <radialGradient id="studio-backdrop" cx="50%" cy="42%" r="62%">
      <stop offset="0%" stop-color="#3a4b63"/>
      <stop offset="35%" stop-color="#243244"/>
      <stop offset="70%" stop-color="#121822"/>
      <stop offset="100%" stop-color="#080c12"/>
    </radialGradient>

    <!-- Studio Floor Warm Hardwood -->
    <linearGradient id="floor-gradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2c1a12"/>
      <stop offset="15%" stop-color="#3d2419"/>
      <stop offset="50%" stop-color="#28160e"/>
      <stop offset="100%" stop-color="#0f0704"/>
    </linearGradient>

    <linearGradient id="floor-reflection" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#4a688a" stop-opacity="0.16"/>
      <stop offset="60%" stop-color="#203042" stop-opacity="0.04"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </linearGradient>

    <!-- Ornate Picture Frame Gradients -->
    <linearGradient id="gold-frame-outer" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#4d3612"/>
      <stop offset="20%" stop-color="#916c2c"/>
      <stop offset="42%" stop-color="#e0be6c"/>
      <stop offset="54%" stop-color="#fff4c2"/>
      <stop offset="75%" stop-color="#b58a3a"/>
      <stop offset="100%" stop-color="#4d3612"/>
    </linearGradient>

    <linearGradient id="gold-frame-inner" x1="1" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#fff2ad"/>
      <stop offset="30%" stop-color="#cca041"/>
      <stop offset="70%" stop-color="#80571b"/>
      <stop offset="100%" stop-color="#452a0a"/>
    </linearGradient>

    <linearGradient id="mat-velvet" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#141720"/>
      <stop offset="100%" stop-color="#1e222e"/>
    </linearGradient>
    ''')

    # Character Materials & Glows
    emit('''
    <!-- Grandpa Materials -->
    <radialGradient id="copper-boiler" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#f5a86c"/>
      <stop offset="25%" stop-color="#d47c3f"/>
      <stop offset="65%" stop-color="#8f4419"/>
      <stop offset="90%" stop-color="#5a2406"/>
      <stop offset="100%" stop-color="#361302"/>
    </radialGradient>

    <linearGradient id="brass-sheen" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#fff2be"/>
      <stop offset="30%" stop-color="#deb454"/>
      <stop offset="70%" stop-color="#996e20"/>
      <stop offset="100%" stop-color="#523808"/>
    </linearGradient>

    <linearGradient id="bakelite-dark" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#4d2719"/>
      <stop offset="40%" stop-color="#36180e"/>
      <stop offset="85%" stop-color="#210d06"/>
      <stop offset="100%" stop-color="#120502"/>
    </linearGradient>

    <linearGradient id="vacuum-glass" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.45"/>
      <stop offset="30%" stop-color="#ffffff" stop-opacity="0.1"/>
      <stop offset="70%" stop-color="#ff9900" stop-opacity="0.2"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.35"/>
    </linearGradient>

    <radialGradient id="filament-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="20%" stop-color="#ffe873"/>
      <stop offset="55%" stop-color="#ff7300"/>
      <stop offset="85%" stop-color="#b82a00" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#b82a00" stop-opacity="0"/>
    </radialGradient>

    <radialGradient id="velvet-seat" cx="40%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#d63145"/>
      <stop offset="45%" stop-color="#941423"/>
      <stop offset="85%" stop-color="#540711"/>
      <stop offset="100%" stop-color="#2b0207"/>
    </radialGradient>

    <!-- Dad Materials (80s Beige Desktop) -->
    <linearGradient id="beige-plastic-v" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#f2e9d7"/>
      <stop offset="20%" stop-color="#e3d6bd"/>
      <stop offset="70%" stop-color="#ccbea0"/>
      <stop offset="100%" stop-color="#94866c"/>
    </linearGradient>

    <linearGradient id="beige-plastic-h" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#f0e6d2"/>
      <stop offset="25%" stop-color="#decfae"/>
      <stop offset="75%" stop-color="#c4b595"/>
      <stop offset="100%" stop-color="#99896c"/>
    </linearGradient>

    <radialGradient id="crt-phosphor" cx="50%" cy="45%" r="65%">
      <stop offset="0%" stop-color="#163820"/>
      <stop offset="55%" stop-color="#0a1f12"/>
      <stop offset="88%" stop-color="#040d07"/>
      <stop offset="100%" stop-color="#010503"/>
    </radialGradient>

    <linearGradient id="tie-stripes" x1="0" y1="0" x2="0.3" y2="1">
      <stop offset="0%" stop-color="#c91a2b"/>
      <stop offset="44%" stop-color="#c91a2b"/>
      <stop offset="46%" stop-color="#1f3f96"/>
      <stop offset="88%" stop-color="#1f3f96"/>
      <stop offset="90%" stop-color="#e6b82e"/>
      <stop offset="100%" stop-color="#e6b82e"/>
    </linearGradient>

    <!-- Mom Materials (Retro Mint Streamline & Chrome) -->
    <radialGradient id="mint-enamel" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#c7faf1"/>
      <stop offset="25%" stop-color="#7ee0d1"/>
      <stop offset="65%" stop-color="#3aa697"/>
      <stop offset="90%" stop-color="#1b665c"/>
      <stop offset="100%" stop-color="#0d3d37"/>
    </radialGradient>

    <linearGradient id="chrome-mirror" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="18%" stop-color="#d6e8f2"/>
      <stop offset="38%" stop-color="#8baec2"/>
      <stop offset="48%" stop-color="#516d80"/>
      <stop offset="56%" stop-color="#ffffff"/>
      <stop offset="78%" stop-color="#a4bfcf"/>
      <stop offset="100%" stop-color="#455e6e"/>
    </linearGradient>

    <radialGradient id="cyan-lens-glow" cx="40%" cy="40%" r="60%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="30%" stop-color="#6affff"/>
      <stop offset="70%" stop-color="#0fa4ab"/>
      <stop offset="100%" stop-color="#04383c"/>
    </radialGradient>

    <radialGradient id="pink-pearl-ball" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#ffebf2"/>
      <stop offset="40%" stop-color="#ff6699"/>
      <stop offset="85%" stop-color="#b81d50"/>
      <stop offset="100%" stop-color="#5e0523"/>
    </radialGradient>

    <!-- Teen Materials (Cyberpunk Gunmetal & Neon Magenta) -->
    <linearGradient id="gunmetal-matte" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#3b3e4a"/>
      <stop offset="30%" stop-color="#242730"/>
      <stop offset="75%" stop-color="#15171c"/>
      <stop offset="100%" stop-color="#0b0c0f"/>
    </linearGradient>

    <radialGradient id="teen-visor-glow" cx="50%" cy="45%" r="65%">
      <stop offset="0%" stop-color="#380d38"/>
      <stop offset="65%" stop-color="#1a041c"/>
      <stop offset="100%" stop-color="#08010a"/>
    </radialGradient>

    <!-- Kid Materials (Canary Yellow) -->
    <radialGradient id="kid-yellow" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#fff885"/>
      <stop offset="30%" stop-color="#ffcc24"/>
      <stop offset="70%" stop-color="#ed8300"/>
      <stop offset="100%" stop-color="#944500"/>
    </radialGradient>

    <radialGradient id="kid-optic" cx="45%" cy="40%" r="55%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="28%" stop-color="#7ae0ff"/>
      <stop offset="65%" stop-color="#157ed4"/>
      <stop offset="100%" stop-color="#073359"/>
    </radialGradient>

    <!-- Robo-Pup Materials -->
    <linearGradient id="toaster-silver" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="18%" stop-color="#deecf5"/>
      <stop offset="48%" stop-color="#89adbf"/>
      <stop offset="55%" stop-color="#557382"/>
      <stop offset="85%" stop-color="#c1d9e6"/>
      <stop offset="100%" stop-color="#698391"/>
    </linearGradient>

    <!-- Patterns -->
    <pattern id="scanlines" width="100" height="4" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="100" y2="0" stroke="#00ff66" stroke-opacity="0.1" stroke-width="1.5"/>
    </pattern>

    <pattern id="circuit-traces" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 0,10 H 20 M 10,0 V 20 M 6,6 h 2 v 2 h -2 z M 14,14 h 2 v 2 h -2 z" stroke="#36c459" stroke-width="0.9" fill="none" opacity="0.7"/>
    </pattern>
    ''')
    
    emit('</defs>')

    # =========================================================================
    # BACKGROUND LAYER: Studio Backdrop & Parquet Floor
    # =========================================================================
    emit('<!-- Studio Backdrop -->')
    emit('<rect x="0" y="0" width="1400" height="1050" fill="url(#studio-backdrop)"/>')

    # Studio mottled cloud texture
    emit('''
    <g opacity="0.22">
      <ellipse cx="450" cy="380" rx="360" ry="240" fill="#6a87ad" filter="url(#floor-blur)"/>
      <ellipse cx="900" cy="420" rx="420" ry="260" fill="#526d8c" filter="url(#floor-blur)"/>
      <ellipse cx="690" cy="270" rx="280" ry="180" fill="#8da9cb" filter="url(#floor-blur)"/>
      <ellipse cx="250" cy="520" rx="200" ry="300" fill="#304157" filter="url(#floor-blur)"/>
    </g>
    ''')

    # Studio Floor: Hardwood Planks
    emit('<!-- Studio Floor -->')
    emit('<polygon points="0,750 1400,750 1400,1050 0,1050" fill="url(#floor-gradient)"/>')
    plank_xs = [0, 110, 240, 390, 560, 740, 930, 1120, 1290, 1400]
    for px in plank_xs:
        top_x = 700 + (px - 700) * 0.72
        emit(f'<line x1="{top_x:.1f}" y1="750" x2="{px}" y2="1050" stroke="#100704" stroke-width="2.5" opacity="0.75"/>')
        emit(f'<line x1="{top_x + 1:.1f}" y1="750" x2="{px + 1}" y2="1050" stroke="#543725" stroke-width="0.8" opacity="0.4"/>')
    emit('<line x1="0" y1="750" x2="1400" y2="750" stroke="#0a0503" stroke-width="4"/>')
    emit('<line x1="0" y1="752" x2="1400" y2="752" stroke="#593b29" stroke-width="1.8" opacity="0.6"/>')
    emit('<polygon points="200,752 1200,752 1360,1050 40,1050" fill="url(#floor-reflection)"/>')

    # Backdrop stand clamps
    emit('''
    <g opacity="0.2">
      <line x1="85" y1="110" x2="85" y2="820" stroke="#1d2633" stroke-width="6"/>
      <line x1="85" y1="110" x2="1315" y2="110" stroke="#1d2633" stroke-width="8"/>
      <line x1="1315" y1="110" x2="1315" y2="820" stroke="#1d2633" stroke-width="6"/>
      <rect x="240" y="104" width="16" height="22" rx="3" fill="#2d3748"/>
      <rect x="580" y="104" width="16" height="22" rx="3" fill="#2d3748"/>
      <rect x="920" y="104" width="16" height="22" rx="3" fill="#2d3748"/>
      <rect x="1180" y="104" width="16" height="22" rx="3" fill="#2d3748"/>
    </g>
    ''')

    # FLOOR CAST SHADOWS
    emit('<!-- Floor Cast Shadows -->')
    emit('<g opacity="0.75" filter="url(#floor-blur)">')
    emit('<ellipse cx="270" cy="855" rx="135" ry="28" fill="#000000"/>') # Grandpa
    emit('<ellipse cx="360" cy="850" rx="75" ry="20" fill="#000000"/>')  # Pup
    emit('<ellipse cx="510" cy="852" rx="55" ry="18" fill="#000000"/>')  # Dad L
    emit('<ellipse cx="585" cy="850" rx="55" ry="18" fill="#000000"/>')  # Dad R
    emit('<ellipse cx="645" cy="845" rx="50" ry="16" fill="#000000"/>')  # Kid
    emit('<ellipse cx="715" cy="848" rx="40" ry="14" fill="#000000"/>')  # Mom L
    emit('<ellipse cx="765" cy="846" rx="40" ry="14" fill="#000000"/>')  # Mom R
    emit('<ellipse cx="945" cy="852" rx="60" ry="20" fill="#000000"/>')  # Teen L
    emit('<ellipse cx="1025" cy="846" rx="60" ry="18" fill="#000000"/>') # Teen R
    emit('</g>')

    # =========================================================================
    # CHARACTER 1: GRANDPA ROBOT (Left: Seated Antique Boiler & Tubes)
    # =========================================================================
    emit('<!-- ================= GRANDPA ROBOT ================= -->')
    emit('<g id="grandpa-robot">')

    # Stool
    emit('<g id="grandpa-stool">')
    stool_legs = [(210, 730, 195, 850), (270, 740, 270, 860), (330, 730, 345, 850)]
    for lx1, ly1, lx2, ly2 in stool_legs:
        emit(f'<line x1="{lx1}" y1="{ly1}" x2="{lx2}" y2="{ly2}" stroke="#2b150c" stroke-width="15" stroke-linecap="round"/>')
        emit(f'<line x1="{lx1}" y1="{ly1}" x2="{lx2}" y2="{ly2}" stroke="#522d1b" stroke-width="9" stroke-linecap="round"/>')
        emit(f'<circle cx="{lx2}" cy="{ly2}" r="10" fill="url(#brass-sheen)"/>')
    emit('<ellipse cx="270" cy="800" rx="66" ry="15" fill="none" stroke="#3d2113" stroke-width="8"/>')
    emit('<ellipse cx="270" cy="800" rx="66" ry="15" fill="none" stroke="#8a532d" stroke-width="2.5"/>')
    emit('<ellipse cx="270" cy="725" rx="88" ry="32" fill="#3b0308"/>')
    emit('<ellipse cx="270" cy="720" rx="88" ry="30" fill="url(#velvet-seat)"/>')
    for angle in range(0, 360, 24):
        rad = math.radians(angle)
        sx = 270 + 84 * math.cos(rad)
        sy = 720 + 26 * math.sin(rad)
        emit(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="3" fill="url(#brass-sheen)"/>')
    emit('</g>')

    # Slumped Body (tilted ~7 deg left)
    emit('<g id="grandpa-slumped" transform="rotate(-7, 270, 700)">')

    # Boiler Body
    emit('<ellipse cx="270" cy="680" rx="100" ry="36" fill="#241004"/>')
    emit('<ellipse cx="270" cy="565" rx="108" ry="120" fill="url(#copper-boiler)"/>')
    emit('<ellipse cx="255" cy="540" rx="88" ry="96" fill="none" stroke="#f0a871" stroke-width="3.5" opacity="0.4"/>')
    # Seams & Rivets
    for ry in [490, 565, 635]:
        emit(f'<ellipse cx="270" cy="{ry}" rx="104" ry="23" fill="none" stroke="#5e2d10" stroke-width="5.5"/>')
        emit(f'<ellipse cx="270" cy="{ry}" rx="104" ry="23" fill="none" stroke="#d48a52" stroke-width="1.8"/>')
        for deg in range(15, 175, 20):
            rad = math.radians(deg)
            rx = 270 + 104 * math.cos(rad)
            r_y = ry + 23 * math.sin(rad)
            emit(f'<circle cx="{rx:.1f}" cy="{r_y:.1f}" r="3" fill="url(#brass-sheen)"/>')
            emit(f'<circle cx="{rx-0.8:.1f}" cy="{r_y-0.8:.1f}" r="1" fill="#ffffff"/>')

    # Chest Pressure Gauge (Completely unblocked and prominent!)
    emit('<!-- Grandpa Pressure Gauge -->')
    emit('<g id="grandpa-gauge" transform="translate(270, 565)">')
    emit('<circle cx="0" cy="0" r="46" fill="#381d05"/>')
    emit('<circle cx="0" cy="0" r="44" fill="url(#brass-sheen)"/>')
    emit('<circle cx="0" cy="0" r="38" fill="#241303"/>')
    emit('<circle cx="0" cy="0" r="36" fill="#f4ebd0"/>')
    def arc_d(r, s_deg, e_deg):
        s_r = math.radians(s_deg)
        e_r = math.radians(e_deg)
        x1 = r * math.cos(s_r)
        y1 = r * math.sin(s_r)
        x2 = r * math.cos(e_r)
        y2 = r * math.sin(e_r)
        large = 1 if (e_deg - s_deg) > 180 else 0
        return f"M {x1:.2f},{y1:.2f} A {r},{r} 0 {large},1 {x2:.2f},{y2:.2f}"
    emit(f'<path d="{arc_d(29, 140, 240)}" fill="none" stroke="#2d8c46" stroke-width="4"/>')
    emit(f'<path d="{arc_d(29, 240, 300)}" fill="none" stroke="#d69e1e" stroke-width="4"/>')
    emit(f'<path d="{arc_d(29, 300, 395)}" fill="none" stroke="#c92424" stroke-width="5"/>')
    for deg in range(140, 400, 15):
        rad = math.radians(deg)
        emit(f'<line x1="{31*math.cos(rad):.1f}" y1="{31*math.sin(rad):.1f}" x2="{25*math.cos(rad):.1f}" y2="{25*math.sin(rad):.1f}" stroke="#423018" stroke-width="1.6"/>')
    # Needle pegged in red!
    emit('<line x1="0" y1="0" x2="26" y2="11" stroke="#b31212" stroke-width="3" stroke-linecap="round"/>')
    emit('<polygon points="26,11 19,7 21,14" fill="#b31212"/>')
    emit('<circle cx="0" cy="0" r="5" fill="#3a2208"/>')
    emit('<circle cx="0" cy="0" r="2.5" fill="url(#brass-sheen)"/>')
    emit('<path d="M -28,-14 A 36,36 0 0,1 28,-14 Q 0,-4 -28,-14 Z" fill="#ffffff" fill-opacity="0.32"/>')
    emit('</g>')

    # Steam Pipes and Valves on side
    emit('<path d="M 170,540 C 140,550 130,620 160,650 C 190,680 210,670 220,690" fill="none" stroke="#8c471a" stroke-width="12" stroke-linecap="round"/>')
    emit('<path d="M 170,540 C 140,550 130,620 160,650 C 190,680 210,670 220,690" fill="none" stroke="#d97d41" stroke-width="7" stroke-linecap="round"/>')
    emit('<circle cx="135" cy="580" r="13" fill="none" stroke="url(#brass-sheen)" stroke-width="4.5"/>')
    emit('<line x1="122" y1="580" x2="148" y2="580" stroke="url(#brass-sheen)" stroke-width="3"/>')
    emit('<line x1="135" y1="567" x2="135" y2="593" stroke="url(#brass-sheen)" stroke-width="3"/>')

    # Shoulder Chimney & Steam Puffs
    emit('<rect x="180" y="445" width="22" height="34" rx="4" fill="#4a2610"/>')
    emit('<ellipse cx="191" cy="445" rx="13" ry="5" fill="url(#brass-sheen)"/>')
    emit('<g opacity="0.45">')
    emit('<circle cx="187" cy="425" r="9" fill="#e0e8f0"/>')
    emit('<circle cx="178" cy="402" r="14" fill="#d0dce8"/>')
    emit('<circle cx="166" cy="374" r="20" fill="#c4d5e8"/>')
    emit('<circle cx="150" cy="340" r="27" fill="#b9cde3" opacity="0.6"/>')
    emit('</g>')

    # Head: Cathedral Bakelite Radio
    emit('<!-- Grandpa Radio Head -->')
    emit('<g id="grandpa-head">')
    emit('<path d="M 200,440 L 200,355 Q 200,300 270,300 Q 340,300 340,355 L 340,440 Z" fill="url(#bakelite-dark)"/>')
    emit('<path d="M 210,435 L 210,360 Q 210,315 270,315 Q 330,315 330,360 L 330,435 Z" fill="#1f0c05" stroke="url(#brass-sheen)" stroke-width="2.5"/>')

    # Vacuum Tubes on Top
    for vtx in [235, 270, 305]:
        emit(f'<rect x="{vtx-12}" y="292" width="24" height="12" rx="2" fill="url(#brass-sheen)"/>')
        emit(f'<path d="M {vtx-10},292 C {vtx-12},275 {vtx-14},240 {vtx},240 C {vtx+14},240 {vtx+12},275 {vtx+10},292 Z" fill="url(#vacuum-glass)" stroke="#ffd79e" stroke-width="0.8"/>')
        emit(f'<ellipse cx="{vtx}" cy="265" rx="16" ry="22" fill="url(#filament-glow)"/>')
        emit(f'<path d="M {vtx-5},285 L {vtx-3},255 L {vtx},262 L {vtx+3},255 L {vtx+5},285" fill="none" stroke="#ffffff" stroke-width="1.8"/>')
        emit(f'<path d="M {vtx-7},288 C {vtx-9},270 {vtx-6},246 {vtx-1},244" fill="none" stroke="#ffffff" stroke-width="1.4" opacity="0.6"/>')

    # Antenna
    emit('<path d="M 330,310 Q 360,270 350,230 Q 345,215 357,210 Q 370,205 365,225" fill="none" stroke="url(#brass-sheen)" stroke-width="3" stroke-linecap="round"/>')

    # Nixie Eyes
    for ey_x, pupil_dx, pupil_dy in [(240, -4, -2), (300, -5, 4)]:
        emit(f'<circle cx="{ey_x}" cy="360" r="22" fill="url(#brass-sheen)"/>')
        emit(f'<circle cx="{ey_x}" cy="360" r="18" fill="#1c0a02"/>')
        emit(f'<circle cx="{ey_x}" cy="360" r="16" fill="url(#filament-glow)"/>')
        emit(f'<circle cx="{ey_x}" cy="360" r="13" fill="none" stroke="#8a4400" stroke-width="1.2" stroke-dasharray="2,2"/>')
        emit(f'<g transform="translate({ey_x + pupil_dx}, {360 + pupil_dy})">')
        emit('<circle cx="0" cy="0" r="5.5" fill="#ffffff"/>')
        emit('<circle cx="0" cy="0" r="3" fill="#ffeeaa"/>')
        emit('<path d="M -5,0 H 5 M 0,-5 V 5" stroke="#ffaa00" stroke-width="1.4"/>')
        emit('</g>')
        emit(f'<path d="M {ey_x-18},353 Q {ey_x},346 {ey_x+18},353 L {ey_x+18},342 L {ey_x-18},342 Z" fill="#522a1b"/>')

    # Speaker Grille Mouth & Drooling Oil Drip
    emit('<path d="M 230,405 C 250,395 290,395 310,405 C 300,430 240,430 230,405 Z" fill="#2b1509" stroke="#63391d" stroke-width="2"/>')
    for my in [404, 411, 418, 424]:
        emit(f'<path d="M {227 + (my-400)*0.8:.1f},{my} Q 270,{my - 4} {313 - (my-400)*0.8:.1f},{my}" fill="none" stroke="url(#brass-sheen)" stroke-width="3" stroke-linecap="round"/>')
    emit('<path d="M 234,424 C 232,434 238,434 234,424 Z" fill="#120c02"/>')
    emit('<circle cx="234" cy="437" r="1.5" fill="#120c02"/>')
    emit('</g>') # End grandpa-head

    # Grandpa Arms
    # Right arm (dangling limply)
    emit('<circle cx="170" cy="495" r="17" fill="url(#brass-sheen)"/>')
    emit('<path d="M 170,495 C 150,550 145,630 160,700" fill="none" stroke="#7a3d16" stroke-width="20" stroke-linecap="round"/>')
    emit('<path d="M 170,495 C 150,550 145,630 160,700" fill="none" stroke="#d47d40" stroke-width="11" stroke-linecap="round"/>')
    emit('<rect x="148" y="695" width="26" height="16" rx="4" fill="url(#brass-sheen)"/>')
    emit('<path d="M 150,711 C 145,730 156,745 166,750 C 176,745 172,730 169,711" fill="none" stroke="#522e15" stroke-width="8" stroke-linecap="round"/>')

    # Left arm: Resting down on knee, holding oil can pointed DOWN-LEFT towards stool!
    emit('<circle cx="365" cy="495" r="17" fill="url(#brass-sheen)"/>')
    emit('<path d="M 365,495 C 385,550 380,620 355,670" fill="none" stroke="#7a3d16" stroke-width="20" stroke-linecap="round"/>')
    emit('<path d="M 365,495 C 385,550 380,620 355,670" fill="none" stroke="#d47d40" stroke-width="11" stroke-linecap="round"/>')
    emit('<circle cx="355" cy="670" r="13" fill="url(#brass-sheen)"/>')
    
    # Oil can pointing DOWN-LEFT towards stool seat & puddle
    emit('<g id="grandpa-oil-can" transform="translate(355, 670) rotate(-130)">')
    emit('<polygon points="-12,-5 14,-5 8,-28 -6,-28" fill="url(#copper-boiler)"/>')
    emit('<line x1="1" y1="-28" x2="1" y2="-75" stroke="url(#brass-sheen)" stroke-width="4" stroke-linecap="round"/>')
    emit('<path d="M 1,-75 Q 1,-98 12,-108" fill="none" stroke="url(#brass-sheen)" stroke-width="3" stroke-linecap="round"/>')
    emit('<path d="M 12,-107 C 15,-114 9,-114 12,-107 Z" fill="#1f1505"/>')
    emit('</g>')

    # Grandpa Legs on Stool
    emit('<path d="M 235,685 C 225,725 215,750 220,820" fill="none" stroke="#4a2610" stroke-width="24" stroke-linecap="round"/>')
    emit('<path d="M 235,685 C 225,725 215,750 220,820" fill="none" stroke="#8a471f" stroke-width="14" stroke-linecap="round"/>')
    emit('<path d="M 220,820 L 200,835 L 240,835 Z" fill="#301809"/>')
    
    emit('<path d="M 305,685 C 315,725 325,750 320,820" fill="none" stroke="#4a2610" stroke-width="24" stroke-linecap="round"/>')
    emit('<path d="M 305,685 C 315,725 325,750 320,820" fill="none" stroke="#8a471f" stroke-width="14" stroke-linecap="round"/>')
    emit('<path d="M 320,820 L 300,835 L 340,835 Z" fill="#301809"/>')

    # Oil puddle on floor
    emit('<ellipse cx="210" cy="852" rx="14" ry="4" fill="#0d0803" opacity="0.8"/>')
    emit('<ellipse cx="208" cy="851" rx="6" ry="1.5" fill="#f5c26b" opacity="0.4"/>')

    emit('</g>') # End grandpa-slumped

    # Power Cable Connection & Sparks (Directly into Robo-Pup\'s mouth!)
    emit('<!-- Grandpa Power Socket & Loose Plug -->')
    emit('<rect x="330" y="675" width="22" height="28" rx="4" fill="#1c0f05" stroke="url(#brass-sheen)" stroke-width="2"/>')
    emit('<g id="loose-plug" transform="translate(344, 688) rotate(26)">')
    emit('<rect x="-8" y="-5" width="6" height="3" fill="#e6c86e"/>')
    emit('<rect x="-8" y="2" width="6" height="3" fill="#e6c86e"/>')
    emit('<rect x="-2" y="-8" width="15" height="16" rx="3" fill="#2b2d33"/>')
    emit('</g>')
    # Cable pulled taut straight to Pup\'s jaws at (318, 762)!
    emit('<path d="M 354,694 C 362,715 335,740 318,762" fill="none" stroke="#121317" stroke-width="10" stroke-linecap="round"/>')
    emit('<path d="M 354,694 C 362,715 335,740 318,762" fill="none" stroke="#2e323b" stroke-width="5" stroke-linecap="round"/>')
    
    # Electric Sparks at socket
    def spark(sx, sy, size, color="#fff275"):
        return f'<polygon points="{sx},{sy-size} {sx+size*0.3},{sy-size*0.3} {sx+size},{sy} {sx+size*0.3},{sy+size*0.3} {sx},{sy+size} {sx-size*0.3},{sy+size*0.3} {sx-size},{sy} {sx-size*0.3},{sy-size*0.3}" fill="{color}"/>'
    emit('<g id="socket-sparks">')
    emit(spark(340, 680, 8, "#ffffff"))
    emit(spark(346, 674, 12, "#ffe600"))
    emit(spark(334, 690, 6, "#ff9900"))
    emit(spark(354, 683, 7, "#66ffff"))
    emit('<circle cx="342" cy="682" r="3" fill="#ffffff"/>')
    emit('</g>')
    emit('</g>') # End grandpa-robot

    # =========================================================================
    # CHARACTER 2: ROBO-PUP (Foreground: Toaster Hound Tugging the Cable!)
    # =========================================================================
    emit('<!-- ================= ROBO-PUP ================= -->')
    emit('<g id="robo-pup">')
    pup_legs = [(340, 785, 325, 842), (365, 785, 352, 842), (400, 785, 390, 840), (425, 785, 420, 840)]
    for lx1, ly1, lx2, ly2 in pup_legs:
        emit(f'<line x1="{lx1}" y1="{ly1}" x2="{lx2}" y2="{ly2}" stroke="#2a333d" stroke-width="7"/>')
        emit(f'<path d="M {lx1-5},{ly1+10} Q {lx1+5},{ly1+15} {lx1-5},{ly1+20} Q {lx1+5},{ly1+25} {lx1-5},{ly1+30} Q {lx1+5},{ly1+35} {lx1-5},{ly1+40}" fill="none" stroke="url(#chrome-mirror)" stroke-width="2.5"/>')
        emit(f'<ellipse cx="{lx2}" cy="{ly2}" rx="9" ry="4" fill="#14171a"/>')

    # Toaster Body
    emit('<rect x="335" y="730" width="95" height="58" rx="15" fill="url(#toaster-silver)"/>')
    emit('<rect x="339" y="733" width="87" height="18" rx="9" fill="#ffffff" fill-opacity="0.35"/>')
    emit('<rect x="350" y="726" width="65" height="8" rx="4" fill="#1f2429"/>')
    
    # Circuit Board Toast Slice
    emit('<rect x="357" y="690" width="50" height="40" rx="4" fill="#1b5e2a" stroke="#2ebb4f" stroke-width="1.5"/>')
    emit('<rect x="357" y="690" width="50" height="40" fill="url(#circuit-traces)"/>')
    for cx in range(361, 403, 6):
        emit(f'<rect x="{cx}" y="687" width="4" height="6" fill="#ffd700"/>')

    # Toast lever
    emit('<rect x="423" y="745" width="12" height="24" rx="2" fill="#2d333b"/>')
    emit('<circle cx="433" cy="755" r="6" fill="#cc2222"/>')

    # Tail with glowing bulb & wag lines
    emit('<path d="M 430,745 Q 460,730 455,700 Q 450,685 465,675" fill="none" stroke="#d97d41" stroke-width="5" stroke-linecap="round"/>')
    emit('<circle cx="465" cy="675" r="12" fill="#ff2222" opacity="0.8"/>')
    emit('<circle cx="465" cy="675" r="7" fill="#ffffff"/>')
    emit('<path d="M 450,660 A 25,25 0 0,1 480,660" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" opacity="0.6"/>')
    emit('<path d="M 445,652 A 35,35 0 0,1 485,652" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>')

    # Head clamped directly onto cord!
    emit('<circle cx="335" cy="755" r="11" fill="#3a444f"/>')
    emit('<g transform="rotate(-15, 330, 755)">')
    emit('<rect x="280" y="738" width="55" height="34" rx="10" fill="url(#toaster-silver)"/>')
    emit('<rect x="275" y="744" width="8" height="12" rx="3" fill="#1b1f24"/>')
    # Happy eyes (^ ^)
    emit('<path d="M 300,748 Q 305,742 310,748" fill="none" stroke="#00ff66" stroke-width="3.5" stroke-linecap="round"/>')
    emit('<path d="M 317,748 Q 322,742 327,748" fill="none" stroke="#00ff66" stroke-width="3.5" stroke-linecap="round"/>')
    emit('<path d="M 320,738 C 315,715 300,715 295,730" fill="url(#toaster-silver)" stroke="#526370" stroke-width="1.5"/>')
    emit('<path d="M 327,735 L 337,720" stroke="#7b93a4" stroke-width="3"/>')
    emit('<path d="M 331,716 A 12,12 0 0,1 343,724" fill="none" stroke="url(#chrome-mirror)" stroke-width="4"/>')
    emit('<rect x="285" y="764" width="28" height="10" rx="3" fill="#2d333b"/>') # jaw clamp
    emit('</g>')
    emit('</g>') # End robo-pup

    # =========================================================================
    # CHARACTER 3: DAD ROBOT (Center-Left: 1980s PC Tower, CRT & Hover Hand)
    # =========================================================================
    emit('<!-- ================= DAD ROBOT ================= -->')
    emit('<g id="dad-robot">')

    # Legs
    # Left Leg
    emit('<rect x="495" y="700" width="30" height="70" rx="6" fill="url(#beige-plastic-v)"/>')
    emit('<rect x="503" y="725" width="14" height="40" fill="url(#chrome-mirror)"/>')
    emit('<circle cx="510" cy="770" r="16" fill="#4a4235"/>')
    emit('<circle cx="510" cy="770" r="10" fill="url(#chrome-mirror)"/>')
    emit('<rect x="492" y="775" width="36" height="60" rx="4" fill="url(#beige-plastic-v)"/>')
    emit('<rect x="480" y="830" width="58" height="20" rx="4" fill="#363127"/>')
    emit('<rect x="482" y="832" width="54" height="12" rx="2" fill="url(#beige-plastic-h)"/>')
    emit('<line x1="480" y1="846" x2="538" y2="846" stroke="#110f0c" stroke-width="4"/>')

    # Right Leg
    emit('<rect x="565" y="700" width="30" height="70" rx="6" fill="url(#beige-plastic-v)"/>')
    emit('<rect x="573" y="725" width="14" height="40" fill="url(#chrome-mirror)"/>')
    emit('<circle cx="580" cy="770" r="16" fill="#4a4235"/>')
    emit('<circle cx="580" cy="770" r="10" fill="url(#chrome-mirror)"/>')
    emit('<rect x="562" y="775" width="36" height="60" rx="4" fill="url(#beige-plastic-v)"/>')
    emit('<rect x="552" y="830" width="58" height="20" rx="4" fill="#363127"/>')
    emit('<rect x="554" y="832" width="54" height="12" rx="2" fill="url(#beige-plastic-h)"/>')
    emit('<line x1="552" y1="846" x2="610" y2="846" stroke="#110f0c" stroke-width="4"/>')

    # Torso Tower
    emit('<!-- Dad Tower Torso -->')
    emit('<rect x="470" y="475" width="150" height="235" rx="10" fill="url(#beige-plastic-v)"/>')
    emit('<rect x="473" y="478" width="144" height="6" rx="3" fill="#ffffff" fill-opacity="0.45"/>')
    emit('<line x1="472" y1="480" x2="472" y2="705" stroke="#ffffff" stroke-width="2" opacity="0.3"/>')
    emit('<line x1="618" y1="480" x2="618" y2="705" stroke="#6e624e" stroke-width="3"/>')

    # Floppy Bays
    for by in [505, 545]:
        emit(f'<rect x="488" y="{by}" width="114" height="32" rx="4" fill="#292620"/>')
        emit(f'<rect x="496" y="{by+13}" width="80" height="4" rx="2" fill="#0d0c0a"/>')
        emit(f'<rect x="582" y="{by+8}" width="14" height="15" rx="2" fill="#a89a80"/>')
        emit(f'<line x1="589" y1="{by+8}" x2="589" y2="{by+23}" stroke="#474033" stroke-width="2"/>')
        l_col = "#ff2222" if by == 505 else "#00ff44"
        emit(f'<circle cx="493" cy="{by+15}" r="2.5" fill="{l_col}"/>')

    # Vent slats
    for vy in range(605, 680, 8):
        emit(f'<line x1="492" y1="{vy}" x2="598" y2="{vy}" stroke="#786c57" stroke-width="3.5" stroke-linecap="round"/>')
        emit(f'<line x1="492" y1="{vy+1}" x2="598" y2="{vy+1}" stroke="#ffffff" stroke-width="1" stroke-linecap="round" opacity="0.3"/>')

    emit('<circle cx="585" cy="592" r="6" fill="#302b23"/>')
    emit('<circle cx="585" cy="592" r="3" fill="#d9b84a"/>')
    emit('<circle cx="505" cy="592" r="5" fill="#cc1818"/>')

    # Striped Clip-on Power Tie
    emit('<!-- Dad Tie -->')
    emit('<rect x="532" y="468" width="26" height="8" rx="2" fill="url(#chrome-mirror)"/>')
    emit('<polygon points="535,476 555,476 550,496 540,496" fill="url(#tie-stripes)"/>')
    emit('<polygon points="540,496 550,496 558,630 545,648 532,630" fill="url(#tie-stripes)"/>')
    emit('<polygon points="540,496 550,496 558,630 545,648 532,630" fill="none" stroke="#211812" stroke-width="1.8"/>')

    # Neck
    for ny in range(436, 475, 8):
        emit(f'<ellipse cx="545" cy="{ny}" rx="28" ry="7" fill="#1f1e1c"/>')
        emit(f'<ellipse cx="545" cy="{ny}" rx="28" ry="7" fill="none" stroke="#54514a" stroke-width="2"/>')

    # CRT Monitor Head
    emit('<!-- Dad CRT Monitor Head -->')
    emit('<g id="dad-head">')
    emit('<rect x="460" y="305" width="170" height="140" rx="18" fill="url(#beige-plastic-v)"/>')
    emit('<rect x="465" y="308" width="160" height="12" rx="4" fill="#ffffff" fill-opacity="0.35"/>')
    for tx in range(485, 615, 12):
        emit(f'<line x1="{tx}" y1="312" x2="{tx+6}" y2="312" stroke="#695f4c" stroke-width="2.5"/>')

    emit('<rect x="474" y="322" width="142" height="110" rx="12" fill="#a89a80"/>')
    emit('<rect x="477" y="325" width="136" height="104" rx="10" fill="#141311"/>')
    emit('<rect x="482" y="330" width="126" height="94" rx="14" fill="url(#crt-phosphor)"/>')
    emit('<rect x="482" y="330" width="126" height="94" rx="14" fill="url(#scanlines)"/>')

    # Phosphor Green Face (Smiling tensely)
    emit('<rect x="508" y="350" width="14" height="14" rx="2" fill="#00ff66"/>')
    emit('<rect x="511" y="353" width="8" height="8" rx="1" fill="#ffffff"/>')
    emit('<rect x="568" y="350" width="14" height="14" rx="2" fill="#00ff66"/>')
    emit('<rect x="571" y="353" width="8" height="8" rx="1" fill="#ffffff"/>')
    emit('<path d="M 512,388 Q 545,410 578,388" fill="none" stroke="#00ff66" stroke-width="4.5" stroke-linecap="round"/>')
    emit('<path d="M 590,344 C 588,350 594,350 590,344 Z" fill="#00ff66"/>') # Sweat drop

    emit('<path d="M 484,334 C 530,332 580,350 600,380 C 590,350 540,336 484,334 Z" fill="#ffffff" fill-opacity="0.18"/>')

    # LEDs
    emit('<circle cx="598" cy="420" r="3.5" fill="#00ff44"/>')
    emit('<circle cx="606" cy="420" r="3.5" fill="#ffaa00"/>')
    emit('<circle cx="500" cy="420" r="4" fill="#383227"/>')
    emit('<circle cx="512" cy="420" r="4" fill="#383227"/>')

    # Rabbit Ear Antenna
    emit('<circle cx="545" cy="305" r="9" fill="url(#chrome-mirror)"/>')
    emit('<line x1="540" y1="300" x2="495" y2="230" stroke="url(#chrome-mirror)" stroke-width="4" stroke-linecap="round"/>')
    emit('<circle cx="495" cy="230" r="5" fill="#c41616"/>')
    emit('<path d="M 550,300 L 595,255 L 615,268" fill="none" stroke="url(#chrome-mirror)" stroke-width="4" stroke-linecap="round"/>')
    emit('<circle cx="615" cy="268" r="5" fill="#c41616"/>')
    emit('</g>')

    # DAD'S AWKWARD ARMS:
    # 1. Right Arm: THE INFAMOUS HOVER-HAND over Grandpa!
    emit('<!-- Dad Hover-Hand -->')
    emit('<g id="dad-hover-arm">')
    emit('<circle cx="468" cy="495" r="22" fill="#544c3c"/>')
    emit('<circle cx="468" cy="495" r="14" fill="url(#chrome-mirror)"/>')
    emit('<line x1="468" y1="495" x2="395" y2="475" stroke="#363127" stroke-width="20" stroke-linecap="round"/>')
    emit('<line x1="468" y1="495" x2="395" y2="475" stroke="url(#beige-plastic-h)" stroke-width="12" stroke-linecap="round"/>')
    emit('<circle cx="395" cy="475" r="15" fill="#544c3c"/>')
    emit('<circle cx="395" cy="475" r="9" fill="url(#chrome-mirror)"/>')
    emit('<line x1="395" y1="475" x2="335" y2="465" stroke="#363127" stroke-width="16" stroke-linecap="round"/>')
    emit('<line x1="395" y1="475" x2="335" y2="465" stroke="url(#beige-plastic-h)" stroke-width="10" stroke-linecap="round"/>')
    emit('<rect x="325" y="456" width="14" height="18" rx="3" fill="#544c3c"/>')
    # Pincer hovering awkwardly above Grandpa with visible gap!
    emit('<g id="hover-pincer" transform="rotate(-15, 325, 465)">')
    emit('<path d="M 325,458 C 313,445 298,448 288,456" fill="none" stroke="url(#chrome-mirror)" stroke-width="5" stroke-linecap="round"/>')
    emit('<path d="M 325,465 C 311,460 295,463 285,470" fill="none" stroke="url(#chrome-mirror)" stroke-width="5" stroke-linecap="round"/>')
    emit('<path d="M 325,472 C 315,478 301,478 291,482" fill="none" stroke="url(#chrome-mirror)" stroke-width="5" stroke-linecap="round"/>')
    emit('</g>')
    emit('<path d="M 288,485 Q 295,498 300,508" fill="none" stroke="#ffffff" stroke-width="1.2" stroke-dasharray="2,3" opacity="0.45"/>')
    emit('</g>')

    # 2. Left Arm: Wrapping stiffly around Mom's shoulder
    emit('<!-- Dad Arm Around Mom -->')
    emit('<g id="dad-arm-around-mom">')
    emit('<circle cx="622" cy="495" r="22" fill="#544c3c"/>')
    emit('<circle cx="622" cy="495" r="14" fill="url(#chrome-mirror)"/>')
    emit('<path d="M 622,495 C 655,505 680,510 705,520" fill="none" stroke="#363127" stroke-width="18" stroke-linecap="round"/>')
    emit('<path d="M 622,495 C 655,505 680,510 705,520" fill="none" stroke="url(#beige-plastic-h)" stroke-width="10" stroke-linecap="round"/>')
    emit('<circle cx="705" cy="520" r="11" fill="url(#chrome-mirror)"/>')
    emit('<path d="M 705,514 C 715,512 725,516 730,525" fill="none" stroke="url(#chrome-mirror)" stroke-width="5" stroke-linecap="round"/>')
    emit('<path d="M 705,526 C 715,528 725,526 730,532" fill="none" stroke="url(#chrome-mirror)" stroke-width="5" stroke-linecap="round"/>')
    emit('</g>')
    emit('</g>') # End dad-robot

    # =========================================================================
    # CHARACTER 4: MOM ROBOT (Center-Right: 1950s Mint Streamline Appliance Mom)
    # =========================================================================
    emit('<!-- ================= MOM ROBOT ================= -->')
    emit('<g id="mom-robot">')

    # Stiletto Legs
    emit('<!-- Mom Legs -->')
    emit('<path d="M 725,705 C 721,745 718,790 715,842" fill="none" stroke="#256b60" stroke-width="13" stroke-linecap="round"/>')
    emit('<path d="M 725,705 C 721,745 718,790 715,842" fill="none" stroke="url(#mint-enamel)" stroke-width="8" stroke-linecap="round"/>')
    emit('<circle cx="720" cy="765" r="8" fill="url(#chrome-mirror)"/>')
    emit('<ellipse cx="715" cy="842" rx="13" ry="5" fill="url(#chrome-mirror)"/>')

    emit('<path d="M 765,705 C 765,745 765,790 765,842" fill="none" stroke="#256b60" stroke-width="13" stroke-linecap="round"/>')
    emit('<path d="M 765,705 C 765,745 765,790 765,842" fill="none" stroke="url(#mint-enamel)" stroke-width="8" stroke-linecap="round"/>')
    emit('<circle cx="765" cy="765" r="8" fill="url(#chrome-mirror)"/>')
    emit('<ellipse cx="765" cy="842" rx="13" ry="5" fill="url(#chrome-mirror)"/>')

    # Hourglass Torso
    emit('<!-- Mom Torso -->')
    emit('<path d="M 700,480 C 690,540 715,595 725,630 C 710,650 695,675 705,710 C 735,720 760,720 790,710 C 800,675 785,650 770,630 C 780,595 805,540 795,480 Z" fill="url(#mint-enamel)"/>')
    emit('<path d="M 700,480 C 690,540 715,595 725,630" fill="none" stroke="url(#chrome-mirror)" stroke-width="4"/>')
    emit('<path d="M 795,480 C 805,540 780,595 770,630" fill="none" stroke="url(#chrome-mirror)" stroke-width="4"/>')

    # Chrome Wasp-Waist Belt
    emit('<ellipse cx="747" cy="628" rx="27" ry="9" fill="url(#chrome-mirror)"/>')
    emit('<circle cx="747" cy="628" r="6" fill="#e8c448"/>')

    # Apron
    emit('<path d="M 722,634 C 720,665 725,690 747,698 C 769,690 774,665 772,634 Z" fill="#ffffff" fill-opacity="0.92" stroke="url(#chrome-mirror)" stroke-width="2"/>')
    emit('<path d="M 726,655 C 732,662 740,662 747,655 C 754,662 762,662 768,655" fill="none" stroke="#a6d4cb" stroke-width="2"/>')
    emit('<path d="M 730,675 C 738,682 747,682 755,675" fill="none" stroke="#a6d4cb" stroke-width="2"/>')

    # Atomic Starburst on Chest
    emit('<g transform="translate(747, 535)">')
    emit('<circle cx="0" cy="0" r="13" fill="none" stroke="url(#chrome-mirror)" stroke-width="2"/>')
    emit('<path d="M 0,-17 Q 0,0 17,0 Q 0,0 0,17 Q 0,0 -17,0 Q 0,0 0,-17 Z" fill="url(#chrome-mirror)"/>')
    emit('<circle cx="0" cy="0" r="4" fill="#ff739d"/>')
    emit('</g>')

    for rad_val in [22, 30]:
        for ang in range(20, 160, 25):
            rad_ang = math.radians(ang)
            emit(f'<circle cx="{747 + rad_val*math.cos(rad_ang):.1f}" cy="{550 + rad_val*math.sin(rad_ang)*0.5:.1f}" r="1.5" fill="#1b5249"/>')

    # Neck
    emit('<path d="M 732,482 C 732,465 762,465 762,482 Z" fill="url(#chrome-mirror)"/>')
    emit('<ellipse cx="747" cy="482" rx="15" ry="5" fill="#4d6575"/>')

    # Beehive / Dome Head
    emit('<!-- Mom Head -->')
    emit('<g id="mom-head">')
    emit('<path d="M 700,440 C 690,380 705,320 747,315 C 790,320 805,380 795,440 C 780,458 715,458 700,440 Z" fill="url(#mint-enamel)"/>')
    emit('<path d="M 688,390 C 692,370 702,350 702,350 L 700,410 Z" fill="url(#chrome-mirror)"/>')
    emit('<path d="M 806,390 C 802,370 792,350 792,350 L 794,410 Z" fill="url(#chrome-mirror)"/>')
    emit('<path d="M 720,328 C 747,322 775,335 782,360 C 770,340 745,332 720,328 Z" fill="#ffffff" fill-opacity="0.6"/>')

    # Cat-Eye Visor
    emit('<path d="M 706,380 C 718,368 776,368 788,380 C 790,405 704,405 706,380 Z" fill="#081c19" stroke="url(#chrome-mirror)" stroke-width="2"/>')

    # Eyes
    for my_x in [728, 766]:
        emit(f'<circle cx="{my_x}" cy="388" r="13" fill="url(#cyan-lens-glow)"/>')
        emit(f'<circle cx="{my_x}" cy="388" r="9" fill="#0d524a"/>')
        emit(f'<circle cx="{my_x}" cy="388" r="4.5" fill="#ffffff"/>')
        for deg in range(0, 360, 60):
            rad = math.radians(deg)
            emit(f'<line x1="{my_x}" y1="388" x2="{my_x + 9*math.cos(rad):.1f}" y2="{388 + 9*math.sin(rad):.1f}" stroke="#09302b" stroke-width="1.2"/>')

    # Strained Polite Eyebrows
    emit('<path d="M 714,366 Q 728,354 740,364" fill="none" stroke="url(#chrome-mirror)" stroke-width="3.5" stroke-linecap="round"/>')
    emit('<path d="M 754,364 Q 766,354 780,366" fill="none" stroke="url(#chrome-mirror)" stroke-width="3.5" stroke-linecap="round"/>')

    # Polite smile
    emit('<path d="M 728,426 Q 747,440 766,426" fill="none" stroke="url(#chrome-mirror)" stroke-width="3.5" stroke-linecap="round"/>')
    emit('<ellipse cx="726" cy="426" rx="2.5" ry="2.5" fill="#e66e85"/>')
    emit('<ellipse cx="768" cy="426" rx="2.5" ry="2.5" fill="#e66e85"/>')

    # Antenna
    emit('<path d="M 747,315 L 747,255" stroke="url(#chrome-mirror)" stroke-width="4.5" stroke-linecap="round"/>')
    emit('<circle cx="747" cy="250" r="11" fill="url(#pink-pearl-ball)"/>')
    emit('<circle cx="745" cy="247" r="4" fill="#ffffff"/>')
    emit('</g>') # End mom-head

    # Mom Arms:
    # Left Arm: Resting politely against Dad's arm
    emit('<!-- Mom Left Arm -->')
    emit('<circle cx="704" cy="495" r="15" fill="url(#chrome-mirror)"/>')
    emit('<path d="M 704,495 C 675,510 655,540 640,560" fill="none" stroke="url(#mint-enamel)" stroke-width="12" stroke-linecap="round"/>')
    emit('<circle cx="640" cy="560" r="8" fill="url(#chrome-mirror)"/>')
    emit('<path d="M 640,560 C 630,562 622,558 618,552" fill="none" stroke="url(#chrome-mirror)" stroke-width="4" stroke-linecap="round"/>')
    emit('<path d="M 640,563 C 630,567 622,565 616,558" fill="none" stroke="url(#chrome-mirror)" stroke-width="4" stroke-linecap="round"/>')

    # RIGHT ARM: THE TELESCOPING VICE-GRIP FIRMLY CLAMPED ONTO TEEN'S ROTATED SHOULDER!
    # Mom reaches from shoulder (790, 495) all the way to Teen's arm at (965, 480)!
    emit('<!-- Mom Vice-Grip on Teen -->')
    emit('<g id="mom-vice-grip">')
    emit('<circle cx="790" cy="495" r="16" fill="url(#chrome-mirror)"/>')
    # Telescoping chrome cylinders stretched taut all the way to Teen's arm!
    emit('<line x1="790" y1="495" x2="880" y2="488" stroke="url(#mint-enamel)" stroke-width="14" stroke-linecap="round"/>')
    emit('<line x1="880" y1="488" x2="965" y2="480" stroke="url(#chrome-mirror)" stroke-width="9" stroke-linecap="round"/>')
    
    # Locking vice-clamp FIRMLY CLAMPED around Teen's upper arm at (965, 480)!
    emit('<g transform="translate(965, 480) rotate(15)">')
    emit('<rect x="-8" y="-18" width="16" height="36" rx="4" fill="#303b42" stroke="url(#chrome-mirror)" stroke-width="2.5"/>')
    emit('<circle cx="0" cy="-22" r="7" fill="url(#chrome-mirror)"/>') # screw knob
    emit('<line x1="-10" y1="-22" x2="10" y2="-22" stroke="#1c2429" stroke-width="3"/>')
    # Clamp jaws wrapped tightly around Teen's armor plate!
    emit('<path d="M 8,-14 C 26,-16 38,-4 34,14" fill="none" stroke="url(#chrome-mirror)" stroke-width="7" stroke-linecap="round"/>')
    emit('<path d="M 8,14 C 26,16 38,4 34,-14" fill="none" stroke="url(#chrome-mirror)" stroke-width="7" stroke-linecap="round"/>')
    emit('</g>')
    # Tension stress lines
    emit('<line x1="945" y1="460" x2="938" y2="453" stroke="#ffffff" stroke-width="1.8" opacity="0.6"/>')
    emit('<line x1="956" y1="457" x2="952" y2="449" stroke="#ffffff" stroke-width="1.8" opacity="0.6"/>')
    emit('</g>')
    emit('</g>') # End mom-robot

    # =========================================================================
    # CHARACTER 5: TEEN ROBOT (Right: Cyberpunk Sloucher, Held by Mom's Grip!)
    # =========================================================================
    emit('<!-- ================= TEEN ROBOT ================= -->')
    emit('<g id="teen-robot">')
    # Teen center X = 970 (leaning away by 11 degrees)
    emit('<g transform="rotate(11, 970, 840)">')

    # Heavy Magnetic Combat Boots & Legs
    # Left Leg
    emit('<line x1="945" y1="710" x2="930" y2="780" stroke="#1f2026" stroke-width="24" stroke-linecap="round"/>')
    emit('<line x1="945" y1="710" x2="930" y2="780" stroke="#333742" stroke-width="14" stroke-linecap="round"/>')
    emit('<polygon points="920,770 945,765 940,790 915,795" fill="url(#gunmetal-matte)"/>')
    emit('<path d="M 910,795 L 945,790 L 950,830 L 890,835 Z" fill="#14151a"/>')
    emit('<rect x="885" y="830" width="70" height="15" rx="3" fill="#242630"/>')
    emit('<line x1="890" y1="840" x2="950" y2="840" stroke="#ff0077" stroke-width="2.5"/>')

    # Right Leg (Planted stubborn and wide)
    emit('<line x1="1005" y1="710" x2="1020" y2="780" stroke="#1f2026" stroke-width="24" stroke-linecap="round"/>')
    emit('<line x1="1005" y1="710" x2="1020" y2="780" stroke="#333742" stroke-width="14" stroke-linecap="round"/>')
    emit('<polygon points="1010,765 1035,770 1030,795 1005,790" fill="url(#gunmetal-matte)"/>')
    emit('<path d="M 1005,790 L 1040,795 L 1055,835 L 995,830 Z" fill="#14151a"/>')
    emit('<rect x="995" y="830" width="65" height="15" rx="3" fill="#242630"/>')
    emit('<line x1="1000" y1="840" x2="1055" y2="840" stroke="#ff0077" stroke-width="2.5"/>')

    # Faceted Stealth Armor Torso
    emit('<!-- Teen Torso -->')
    emit('<polygon points="920,490 1020,480 1040,695 930,705" fill="url(#gunmetal-matte)"/>')
    emit('<polygon points="930,500 1010,492 995,620 925,615" fill="#292c36"/>')
    emit('<line x1="970" y1="490" x2="965" y2="695" stroke="#111217" stroke-width="3"/>')
    emit('<path d="M 1005,495 L 1015,540 L 1005,580 L 1020,640" fill="none" stroke="#00ffff" stroke-width="2"/>')

    # Angular Helmet & Headphones
    emit('<!-- Teen Helmet -->')
    emit('<path d="M 925,455 L 920,380 L 960,335 L 1025,345 L 1035,450 Z" fill="url(#gunmetal-matte)"/>')
    emit('<polygon points="955,335 1025,345 1005,375 945,365" fill="#3f4452"/>')

    # Massive Over-Ear Monitor Headphones
    emit('<path d="M 920,390 C 915,325 1030,325 1040,390" fill="none" stroke="#18191f" stroke-width="14" stroke-linecap="round"/>')
    emit('<path d="M 920,390 C 915,325 1030,325 1040,390" fill="none" stroke="#ff0077" stroke-width="2" stroke-linecap="round"/>')
    emit('<rect x="905" y="380" width="22" height="48" rx="8" fill="#18191f" stroke="#ff0077" stroke-width="2"/>')
    emit('<circle cx="916" cy="404" r="7" fill="#ff0077"/>')
    emit('<rect x="1028" y="380" width="22" height="48" rx="8" fill="#18191f" stroke="#ff0077" stroke-width="2"/>')
    emit('<circle cx="1039" cy="404" r="7" fill="#ff0077"/>')

    # Dark Visor & Bored Flat Slit Eyes (—  —)
    emit('<polygon points="935,385 1020,385 1015,435 932,430" fill="url(#teen-visor-glow)"/>')
    emit('<line x1="948" y1="408" x2="972" y2="408" stroke="#ff0077" stroke-width="4.5" stroke-linecap="round"/>')
    emit('<line x1="988" y1="408" x2="1012" y2="408" stroke="#ff0077" stroke-width="4.5" stroke-linecap="round"/>')
    emit('<path d="M 946,403 L 974,405" stroke="#ff66cc" stroke-width="1.8"/>')
    emit('<path d="M 986,405 L 1014,403" stroke="#ff66cc" stroke-width="1.8"/>')

    # Emo Fringe Antenna
    emit('<path d="M 960,335 C 950,360 930,395 920,410 C 935,395 955,380 965,355 Z" fill="#111217" stroke="#00ffff" stroke-width="1.2"/>')
    emit('<path d="M 975,340 C 965,370 945,410 938,425 C 952,410 970,385 980,355 Z" fill="#181921"/>')
    emit('<path d="M 985,345 C 980,375 960,415 955,430 C 968,415 982,390 990,360 Z" fill="#242633"/>')

    # Folded / Crossed Arms (Defiant posture)
    emit('<!-- Teen Crossed Arms -->')
    emit('<circle cx="915" cy="485" r="24" fill="#242630"/>')
    emit('<polygon points="898,470 932,465 938,495 902,500" fill="url(#gunmetal-matte)"/>')
    emit('<circle cx="1025" cy="480" r="24" fill="#242630"/>')

    # Forearms crossed
    emit('<path d="M 915,490 C 940,535 995,545 1015,530" fill="none" stroke="#181921" stroke-width="26" stroke-linecap="round"/>')
    emit('<path d="M 915,490 C 940,535 995,545 1015,530" fill="none" stroke="url(#gunmetal-matte)" stroke-width="18" stroke-linecap="round"/>')
    emit('<path d="M 1020,490 C 1000,545 945,555 925,545" fill="none" stroke="#14151a" stroke-width="26" stroke-linecap="round"/>')
    emit('<path d="M 1020,490 C 1000,545 945,555 925,545" fill="none" stroke="url(#gunmetal-matte)" stroke-width="18" stroke-linecap="round"/>')

    # Gauntlets
    emit('<rect x="930" y="522" width="22" height="28" rx="4" fill="#14151a" transform="rotate(15, 940, 536)"/>')
    emit('<line x1="932" y1="536" x2="950" y2="540" stroke="#00ffff" stroke-width="2"/>')
    emit('<rect x="990" y="515" width="22" height="28" rx="4" fill="#14151a" transform="rotate(-15, 1000, 529)"/>')
    emit('<line x1="992" y1="528" x2="1010" y2="524" stroke="#ff0077" stroke-width="2"/>')

    emit('</g>') # End teen rotate
    emit('</g>') # End teen-robot

    # =========================================================================
    # CHARACTER 6: LITTLE KID ROBOT (Front Center: Hyperactive Toddler Bot)
    # =========================================================================
    emit('<!-- ================= LITTLE KID ROBOT ================= -->')
    emit('<g id="kid-robot">')
    # Kid center X = 650, down in front, tilted ~16 degrees
    emit('<g transform="rotate(16, 650, 835)">')

    # Wheel & Training Casters
    emit('<circle cx="650" cy="820" r="32" fill="#1c1f24"/>')
    emit('<circle cx="650" cy="820" r="26" fill="#363d47"/>')
    emit('<circle cx="650" cy="820" r="18" fill="url(#kid-yellow)"/>')
    emit('<circle cx="650" cy="820" r="8" fill="url(#chrome-mirror)"/>')
    for deg in range(0, 360, 30):
        rad = math.radians(deg)
        emit(f'<circle cx="{650 + 31*math.cos(rad):.1f}" cy="{820 + 31*math.sin(rad):.1f}" r="3" fill="#0d0e10"/>')

    # Training struts
    emit('<path d="M 625,800 Q 605,810 610,835" fill="none" stroke="url(#chrome-mirror)" stroke-width="5" stroke-linecap="round"/>')
    emit('<circle cx="610" cy="835" r="9" fill="#1c1f24"/>')
    emit('<circle cx="610" cy="835" r="4" fill="url(#kid-yellow)"/>')
    emit('<path d="M 675,800 Q 695,805 700,822" fill="none" stroke="url(#chrome-mirror)" stroke-width="5" stroke-linecap="round"/>')
    emit('<circle cx="700" cy="822" r="9" fill="#1c1f24"/>')
    emit('<circle cx="700" cy="822" r="4" fill="url(#kid-yellow)"/>')

    # Ball Chassis
    emit('<!-- Kid Chassis -->')
    emit('<circle cx="650" cy="735" r="54" fill="url(#kid-yellow)"/>')
    emit('<ellipse cx="633" cy="710" rx="32" ry="20" fill="#ffffff" fill-opacity="0.45" transform="rotate(-25, 633, 710)"/>')
    emit('<path d="M 597,740 C 597,765 703,765 703,740 C 703,725 597,725 597,740 Z" fill="#24262b"/>')
    for bx in range(607, 693, 14):
        emit(f'<polygon points="{bx},730 {bx+8},730 {bx+4},748 {bx-4},748" fill="#ffcc00"/>')

    # Spring Neck
    neck_coils = [
        (650, 685, 637, 680), (637, 680, 660, 672), (660, 672, 643, 664),
        (643, 664, 667, 656), (667, 656, 650, 646), (650, 646, 673, 638),
    ]
    for x1, y1, x2, y2 in neck_coils:
        emit(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="url(#chrome-mirror)" stroke-width="8" stroke-linecap="round"/>')
        emit(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#ffffff" stroke-width="2" stroke-linecap="round" opacity="0.6"/>')

    # Head with Cyclops Optic
    emit('<!-- Kid Head -->')
    emit('<g transform="translate(18, -48)">')
    emit('<circle cx="650" cy="650" r="42" fill="url(#kid-yellow)"/>')
    emit('<ellipse cx="637" cy="630" rx="22" ry="14" fill="#ffffff" fill-opacity="0.5" transform="rotate(-20, 637, 630)"/>')

    # Propeller Beanie
    emit('<ellipse cx="650" cy="608" rx="14" ry="5" fill="#2e7d32"/>')
    emit('<line x1="650" y1="608" x2="650" y2="590" stroke="url(#chrome-mirror)" stroke-width="4"/>')
    emit('<circle cx="650" cy="590" r="5" fill="#d32f2f"/>')
    emit('<ellipse cx="650" cy="590" rx="34" ry="8" fill="#ffffff" fill-opacity="0.25"/>')
    emit('<ellipse cx="625" cy="590" rx="16" ry="4" fill="#fbc02d"/>')
    emit('<ellipse cx="675" cy="590" rx="16" ry="4" fill="#1976d2"/>')

    # Cyclops Eye
    emit('<circle cx="650" cy="650" r="28" fill="#262a30" stroke="url(#chrome-mirror)" stroke-width="4"/>')
    emit('<circle cx="650" cy="650" r="23" fill="url(#kid-optic)"/>')
    emit('<circle cx="655" cy="644" r="11" fill="#051c2e"/>')
    emit('<circle cx="651" cy="640" r="5" fill="#ffffff"/>')
    emit('<circle cx="659" cy="648" r="2.5" fill="#ffffff"/>')
    emit('</g>')

    # Waving Arm
    emit('<!-- Kid Arms -->')
    emit('<g id="kid-waving-arm">')
    emit('<path d="M 605,725 C 565,710 555,650 575,605 C 585,580 605,570 610,550" fill="none" stroke="#2d3238" stroke-width="12" stroke-linecap="round"/>')
    emit('<path d="M 605,725 C 565,710 555,650 575,605 C 585,580 605,570 610,550" fill="none" stroke="url(#chrome-mirror)" stroke-width="6" stroke-linecap="round"/>')
    emit('<circle cx="610" cy="550" r="8" fill="url(#kid-yellow)"/>')
    emit('<path d="M 610,546 L 597,530" stroke="url(#chrome-mirror)" stroke-width="3.5" stroke-linecap="round"/>')
    emit('<path d="M 612,544 L 615,524" stroke="url(#chrome-mirror)" stroke-width="3.5" stroke-linecap="round"/>')
    emit('<path d="M 615,548 L 629,534" stroke="url(#chrome-mirror)" stroke-width="3.5" stroke-linecap="round"/>')
    emit('<path d="M 590,520 Q 613,510 635,522" fill="none" stroke="#ffffff" stroke-width="1.8" stroke-linecap="round" opacity="0.6"/>')
    emit('</g>')

    # Hugging Battery
    emit('<g id="kid-battery-arm">')
    emit('<path d="M 690,735 C 710,745 705,775 675,780" fill="none" stroke="#2d3238" stroke-width="12" stroke-linecap="round"/>')
    emit('<path d="M 690,735 C 710,745 705,775 675,780" fill="none" stroke="url(#chrome-mirror)" stroke-width="6" stroke-linecap="round"/>')
    
    # 9V Battery
    emit('<g transform="translate(680, 740) rotate(-18)">')
    emit('<rect x="-14" y="-22" width="28" height="44" rx="4" fill="#0d2b45"/>')
    emit('<rect x="-14" y="-8" width="28" height="18" fill="#e6a100"/>')
    emit('<rect x="-10" y="-28" width="8" height="6" fill="url(#brass-sheen)"/>')
    emit('<circle cx="6" cy="-25" r="3.5" fill="url(#brass-sheen)"/>')
    emit('</g>')

    emit('<circle cx="680" cy="765" r="7" fill="url(#kid-yellow)"/>')
    emit('<path d="M 675,760 C 669,765 669,772 677,775" fill="none" stroke="url(#chrome-mirror)" stroke-width="3"/>')
    emit('</g>')

    emit('</g>') # End kid rotate
    emit('</g>') # End kid-robot

    # Studio Spotlight Vignette Overlay
    emit('''
    <radialGradient id="studio-vignette" cx="50%" cy="48%" r="60%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0"/>
      <stop offset="70%" stop-color="#000000" stop-opacity="0.08"/>
      <stop offset="90%" stop-color="#050a12" stop-opacity="0.38"/>
      <stop offset="100%" stop-color="#020408" stop-opacity="0.65"/>
    </radialGradient>
    <rect x="0" y="0" width="1400" height="1050" fill="url(#studio-vignette)"/>
    ''')

    # =========================================================================
    # MASTERPIECE ORNATE PICTURE FRAME (Antique Gilded Gold Baroque Frame)
    # =========================================================================
    emit('<!-- ================= ORNATE PICTURE FRAME ================= -->')
    emit('<g id="museum-picture-frame">')
    
    # Outer dark shadow
    emit('<rect x="0" y="0" width="1400" height="1050" fill="none" stroke="#000000" stroke-width="12"/>')
    
    # Outer Gilded Gold Moulding
    frame_w = 46
    emit(f'<rect x="12" y="12" width="{width - 24}" height="{height - 24}" rx="8" fill="none" stroke="url(#gold-frame-outer)" stroke-width="{frame_w}"/>')
    emit(f'<rect x="24" y="24" width="{width - 48}" height="{height - 48}" rx="6" fill="none" stroke="#ffe899" stroke-width="3" opacity="0.8"/>')
    emit(f'<rect x="42" y="42" width="{width - 84}" height="{height - 84}" rx="4" fill="none" stroke="#54380f" stroke-width="4"/>')
    emit(f'<rect x="46" y="46" width="{width - 92}" height="{height - 92}" rx="3" fill="none" stroke="url(#gold-frame-inner)" stroke-width="6"/>')

    # Museum Velvet Matboard Cutout
    mat_x = 52
    mat_y = 52
    mat_w = width - 104
    mat_h = height - 104
    inner_cut_x = 95
    inner_cut_y = 95
    inner_cut_w = width - 190
    inner_cut_h = height - 190
    mat_path = f"M {mat_x},{mat_y} H {mat_x + mat_w} V {mat_y + mat_h} H {mat_x} Z M {inner_cut_x},{inner_cut_y} V {inner_cut_y + inner_cut_h} H {inner_cut_x + inner_cut_w} V {inner_cut_y} Z"
    emit(f'<path d="{mat_path}" fill="url(#mat-velvet)"/>')

    # Inner Gold Fillet
    emit(f'<rect x="{inner_cut_x}" y="{inner_cut_y}" width="{inner_cut_w}" height="{inner_cut_h}" fill="none" stroke="url(#gold-frame-inner)" stroke-width="5"/>')
    emit(f'<rect x="{inner_cut_x}" y="{inner_cut_y}" width="{inner_cut_w}" height="{inner_cut_h}" fill="none" stroke="#fff4b8" stroke-width="1.5" opacity="0.7"/>')
    emit(f'<rect x="{inner_cut_x+2}" y="{inner_cut_y+2}" width="{inner_cut_w-4}" height="{inner_cut_h-4}" fill="none" stroke="#000000" stroke-width="8" opacity="0.45"/>')

    # Corner Flourishes
    def draw_corner(cx, cy, sx, sy):
        return f'''
        <g transform="translate({cx}, {cy}) scale({sx}, {sy})">
          <path d="M 0,0 C 15,5 30,12 40,25 C 48,36 48,50 38,58 C 30,64 16,60 14,48 C 12,38 22,28 32,32 C 38,35 38,42 34,44 C 30,46 26,42 28,38" fill="none" stroke="url(#gold-frame-outer)" stroke-width="5" stroke-linecap="round"/>
          <path d="M 0,0 C 5,15 12,30 25,40 C 36,48 50,48 58,38 C 64,30 60,16 48,14 C 38,12 28,22 32,32 C 35,38 42,38 44,34 C 46,30 42,26 38,28" fill="none" stroke="url(#gold-frame-outer)" stroke-width="5" stroke-linecap="round"/>
          <circle cx="16" cy="16" r="8" fill="url(#gold-frame-inner)"/>
          <circle cx="16" cy="16" r="4" fill="#fff5b8"/>
        </g>
        '''
    emit(draw_corner(16, 16, 1, 1))
    emit(draw_corner(width - 16, 16, -1, 1))
    emit(draw_corner(16, height - 16, 1, -1))
    emit(draw_corner(width - 16, height - 16, -1, -1))

    emit('</g>') # End museum-picture-frame

    emit('</svg>')
    return '\n'.join(svg)

if __name__ == '__main__':
    svg_content = build_svg()
    out_dir = os.path.abspath('output')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'awkward_robot_family_portrait.svg')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Generated {out_path} ({len(svg_content.encode('utf-8'))} bytes)")
