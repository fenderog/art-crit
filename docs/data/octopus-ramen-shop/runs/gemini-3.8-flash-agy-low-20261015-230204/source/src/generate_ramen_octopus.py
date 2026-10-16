#!/usr/bin/env python3
"""
generate_ramen_octopus.py
Generates a detailed, vibrant SVG illustration of an octopus chef at a ramen booth.
All elements are 100% self-contained vectors with beautiful custom Japanese crests,
rich shading, and flawless z-ordering.
"""

import os
import xml.etree.ElementTree as ET

def build_svg():
    width = 1200
    height = 900
    
    defs = []
    
    # --- Gradients ---
    defs.append('''
    <linearGradient id="bgNight" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#080c18"/>
      <stop offset="45%" stop-color="#0f1629"/>
      <stop offset="80%" stop-color="#1b172a"/>
      <stop offset="100%" stop-color="#261b2b"/>
    </linearGradient>
    
    <radialGradient id="lanternGlowRed" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ff4a36" stop-opacity="0.9"/>
      <stop offset="40%" stop-color="#ff331f" stop-opacity="0.45"/>
      <stop offset="80%" stop-color="#ff1a00" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="#ff0000" stop-opacity="0"/>
    </radialGradient>

    <radialGradient id="lanternGlowAmber" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffb703" stop-opacity="0.92"/>
      <stop offset="35%" stop-color="#fb8500" stop-opacity="0.5"/>
      <stop offset="75%" stop-color="#d46b08" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#b25000" stop-opacity="0"/>
    </radialGradient>

    <radialGradient id="warmStallGlow" cx="50%" cy="45%" r="60%">
      <stop offset="0%" stop-color="#ffbe0b" stop-opacity="0.32"/>
      <stop offset="50%" stop-color="#fb5607" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#3a0ca3" stop-opacity="0"/>
    </radialGradient>

    <!-- Wood Gradients -->
    <linearGradient id="roofWood" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#38231a"/>
      <stop offset="50%" stop-color="#2a1811"/>
      <stop offset="100%" stop-color="#1a0f0a"/>
    </linearGradient>

    <linearGradient id="tileGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#4e3e34"/>
      <stop offset="50%" stop-color="#30221b"/>
      <stop offset="100%" stop-color="#21150f"/>
    </linearGradient>

    <linearGradient id="counterWood" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#e8a868"/>
      <stop offset="25%" stop-color="#cf8245"/>
      <stop offset="70%" stop-color="#9a5226"/>
      <stop offset="100%" stop-color="#612f12"/>
    </linearGradient>

    <linearGradient id="counterFront" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#4a2810"/>
      <stop offset="20%" stop-color="#341b0b"/>
      <stop offset="100%" stop-color="#190c05"/>
    </linearGradient>

    <linearGradient id="postWood" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#5a3825"/>
      <stop offset="40%" stop-color="#805035"/>
      <stop offset="70%" stop-color="#5a3825"/>
      <stop offset="100%" stop-color="#3b2214"/>
    </linearGradient>

    <!-- Octopus Skin Gradients -->
    <linearGradient id="octoHeadGrad" x1="20%" y1="10%" x2="80%" y2="90%">
      <stop offset="0%" stop-color="#ff7f70"/>
      <stop offset="25%" stop-color="#ff4a3d"/>
      <stop offset="65%" stop-color="#e32626"/>
      <stop offset="100%" stop-color="#9e1220"/>
    </linearGradient>

    <linearGradient id="octoArmGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ff7566"/>
      <stop offset="50%" stop-color="#ed2f2f"/>
      <stop offset="100%" stop-color="#91111d"/>
    </linearGradient>

    <linearGradient id="octoArmGrad2" x1="100%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ff8577"/>
      <stop offset="40%" stop-color="#ed2f2f"/>
      <stop offset="100%" stop-color="#8a101a"/>
    </linearGradient>

    <radialGradient id="suckerGrad" cx="35%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="45%" stop-color="#ffd5db"/>
      <stop offset="85%" stop-color="#f28e9b"/>
      <stop offset="100%" stop-color="#e05768"/>
    </radialGradient>

    <!-- Chef Outfit Gradients -->
    <linearGradient id="hachimakiGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="70%" stop-color="#f2f2f7"/>
      <stop offset="100%" stop-color="#d8d8e5"/>
    </linearGradient>

    <linearGradient id="apronGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#243d70"/>
      <stop offset="60%" stop-color="#162647"/>
      <stop offset="100%" stop-color="#0c1426"/>
    </linearGradient>

    <linearGradient id="norenIndigo" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#263f6e"/>
      <stop offset="75%" stop-color="#1a2b4d"/>
      <stop offset="100%" stop-color="#111c33"/>
    </linearGradient>

    <!-- Kitchenware Gradients -->
    <linearGradient id="steelPot" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#939fb3"/>
      <stop offset="25%" stop-color="#edf0f2"/>
      <stop offset="50%" stop-color="#d1d7dd"/>
      <stop offset="85%" stop-color="#707a82"/>
      <stop offset="100%" stop-color="#4c545c"/>
    </linearGradient>

    <linearGradient id="knifeBlade" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="35%" stop-color="#e9edf0"/>
      <stop offset="70%" stop-color="#b0b8bf"/>
      <stop offset="100%" stop-color="#6f767d"/>
    </linearGradient>

    <!-- Food Gradients -->
    <radialGradient id="brothGrad" cx="45%" cy="45%" r="55%">
      <stop offset="0%" stop-color="#ffd56b"/>
      <stop offset="35%" stop-color="#f6a666"/>
      <stop offset="70%" stop-color="#cb6c24"/>
      <stop offset="95%" stop-color="#853b0b"/>
      <stop offset="100%" stop-color="#582404"/>
    </radialGradient>

    <linearGradient id="noodleGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#fff3c4"/>
      <stop offset="40%" stop-color="#fadc80"/>
      <stop offset="80%" stop-color="#e7b944"/>
      <stop offset="100%" stop-color="#bb8b23"/>
    </linearGradient>

    <radialGradient id="eggYolk" cx="40%" cy="35%" r="60%">
      <stop offset="0%" stop-color="#ffbe0b"/>
      <stop offset="45%" stop-color="#fb8500"/>
      <stop offset="85%" stop-color="#dc5104"/>
      <stop offset="100%" stop-color="#a32c00"/>
    </radialGradient>

    <radialGradient id="eggWhite" cx="45%" cy="40%" r="55%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="70%" stop-color="#fef9ee"/>
      <stop offset="90%" stop-color="#d8bc92"/>
      <stop offset="100%" stop-color="#a88156"/>
    </radialGradient>

    <radialGradient id="chashuPork" cx="45%" cy="45%" r="55%">
      <stop offset="0%" stop-color="#eddcd2"/>
      <stop offset="25%" stop-color="#c98a72"/>
      <stop offset="55%" stop-color="#9c5339"/>
      <stop offset="85%" stop-color="#6e2d19"/>
      <stop offset="100%" stop-color="#401408"/>
    </radialGradient>

    <linearGradient id="bowlCeramic" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#c92535"/>
      <stop offset="40%" stop-color="#a01724"/>
      <stop offset="80%" stop-color="#6d0f18"/>
      <stop offset="100%" stop-color="#40060c"/>
    </linearGradient>

    <linearGradient id="lanternRedBody" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#961717"/>
      <stop offset="25%" stop-color="#ed2f2f"/>
      <stop offset="50%" stop-color="#ff5746"/>
      <stop offset="80%" stop-color="#ed2f2f"/>
      <stop offset="100%" stop-color="#821010"/>
    </linearGradient>

    <linearGradient id="lanternYellowBody" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#b86608"/>
      <stop offset="25%" stop-color="#fca514"/>
      <stop offset="50%" stop-color="#ffe67e"/>
      <stop offset="80%" stop-color="#fca514"/>
      <stop offset="100%" stop-color="#9c5102"/>
    </linearGradient>
    ''')
    
    # --- Filters ---
    defs.append('''
    <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="15" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="dropShadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="2" dy="5" stdDeviation="4" flood-color="#000000" flood-opacity="0.4"/>
    </filter>

    <filter id="counterShadow" x="-20%" y="-20%" width="140%" height="160%">
      <feDropShadow dx="0" dy="7" stdDeviation="7" flood-color="#050302" flood-opacity="0.55"/>
    </filter>

    <filter id="steamBlur" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="8" result="blur"/>
    </filter>
    ''')

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    parts.append('<defs>' + ''.join(defs) + '</defs>')
    
    # -------------------------------------------------------------------------
    # 1. NIGHT SKY & BACKGROUND AMBIENCE
    # -------------------------------------------------------------------------
    parts.append('<!-- BACKGROUND -->')
    parts.append(f'<rect width="{width}" height="{height}" fill="url(#bgNight)"/>')
    
    bokeh_lights = [
        (80, 200, 24, "#ffb703", 0.15),
        (160, 160, 18, "#fb8500", 0.12),
        (220, 240, 32, "#ff006e", 0.10),
        (980, 190, 28, "#48cae4", 0.12),
        (1060, 150, 35, "#ffb703", 0.15),
        (1130, 220, 20, "#ffbe0b", 0.18),
        (880, 260, 16, "#ff006e", 0.10),
        (130, 290, 15, "#48cae4", 0.14),
        (1020, 280, 22, "#fb8500", 0.15),
    ]
    for bx, by, br, bcol, bop in bokeh_lights:
        parts.append(f'<circle cx="{bx}" cy="{by}" r="{br}" fill="{bcol}" opacity="{bop}" filter="url(#softGlow)"/>')
        
    parts.append(f'<ellipse cx="600" cy="440" rx="490" ry="330" fill="url(#warmStallGlow)"/>')

    # -------------------------------------------------------------------------
    # 2. YATAI BOOTH BACK WALL & SHELVES
    # -------------------------------------------------------------------------
    parts.append('<!-- YATAI BACKDROP & FRAMEWORK -->')
    parts.append('<rect x="140" y="200" width="920" height="460" fill="#201511"/>')
    for px in range(160, 1060, 48):
        parts.append(f'<line x1="{px}" y1="200" x2="{px}" y2="660" stroke="#160e0a" stroke-width="2.5"/>')
        parts.append(f'<line x1="{px+1}" y1="200" x2="{px+1}" y2="660" stroke="#2c1d17" stroke-width="1"/>')
        
    # Back shelves
    parts.append('<rect x="180" y="280" width="840" height="15" rx="2" fill="url(#postWood)" filter="url(#dropShadow)"/>')
    parts.append('<rect x="180" y="410" width="840" height="15" rx="2" fill="url(#postWood)" filter="url(#dropShadow)"/>')

    # Shelf Items: Top shelf
    parts.append('''
    <g id="shelf-items-top">
      <!-- Sake bottle 1 -->
      <path d="M 220,280 L 220,248 C 220,238 228,231 232,221 L 232,212 L 244,212 L 244,221 C 248,231 256,238 256,248 L 256,280 Z" fill="#2d5a4c"/>
      <rect x="228" y="242" width="20" height="24" fill="#f4ebd9" rx="1"/>
      <line x1="238" y1="246" x2="238" y2="262" stroke="#991b1b" stroke-width="2"/>
      <path d="M 264,280 L 260,266 L 274,266 L 270,280 Z" fill="#e9ecef"/>

      <!-- Soy sauce cruet -->
      <rect x="290" y="240" width="22" height="40" rx="3" fill="#6c2d1b"/>
      <ellipse cx="301" cy="240" rx="11" ry="3" fill="#8d3d25"/>
      <path d="M 297,240 L 305,240 L 304,230 L 298,230 Z" fill="#cb3a2a"/>
      <path d="M 306,236 Q 318,238 314,226" fill="none" stroke="#cb3a2a" stroke-width="2.5" stroke-linecap="round"/>

      <!-- Shichimi togarashi shaker -->
      <rect x="330" y="246" width="18" height="34" rx="2" fill="#d90429"/>
      <path d="M 328,246 L 350,246 L 347,236 L 331,236 Z" fill="#ffb703"/>
      <circle cx="339" cy="261" r="4.5" fill="#f8f9fa"/>
      <!-- Tiny red chili icon -->
      <path d="M 338,258 Q 342,261 339,265" stroke="#d90429" stroke-width="1.8" fill="none"/>

      <!-- Tea canisters -->
      <rect x="370" y="225" width="36" height="55" rx="4" fill="#3a5a40"/>
      <rect x="367" y="221" width="42" height="7" rx="2" fill="#e9c46a"/>
      <rect x="378" y="242" width="20" height="26" fill="#fdf0d5" rx="1"/>
      <!-- Golden tea leaf motif -->
      <circle cx="388" cy="255" r="5" fill="#e9c46a"/>
    </g>
    ''')

    # Menu Fudas on Back Wall (rendered with stylized vector brushstrokes)
    fuda_positions = [680, 725, 770, 815, 860]
    for fx in fuda_positions:
        parts.append(f'''
        <g id="fuda-{fx}">
          <rect x="{fx}" y="215" width="36" height="60" rx="2" fill="#d8a47f" stroke="#784828" stroke-width="1.5" filter="url(#dropShadow)"/>
          <line x1="{fx+18}" y1="210" x2="{fx+18}" y2="215" stroke="#4a2e1b" stroke-width="1.5"/>
          <circle cx="{fx+18}" cy="210" r="2" fill="#ffb703"/>
          <!-- Stylized vertical menu brushstrokes -->
          <line x1="{fx+18}" y1="225" x2="{fx+18}" y2="233" stroke="#2b1810" stroke-width="3" stroke-linecap="round"/>
          <line x1="{fx+12}" y1="237" x2="{fx+24}" y2="237" stroke="#2b1810" stroke-width="2" stroke-linecap="round"/>
          <line x1="{fx+18}" y1="241" x2="{fx+18}" y2="249" stroke="#2b1810" stroke-width="2.5" stroke-linecap="round"/>
          <line x1="{fx+14}" y1="253" x2="{fx+22}" y2="253" stroke="#2b1810" stroke-width="2" stroke-linecap="round"/>
          
          <line x1="{fx+4}" y1="262" x2="{fx+32}" y2="262" stroke="#a06038" stroke-width="0.8"/>
          <!-- Red artisan stamp seal (Hanko) at bottom -->
          <rect x="{fx+14}" y="265" width="8" height="6" fill="#c92535" rx="1"/>
        </g>
        ''')

    # Garlic basket & ginger on lower shelf
    parts.append('''
    <g id="shelf-lower-props">
      <path d="M 880,410 C 880,390 925,390 925,410 Z" fill="#bc6c25"/>
      <circle cx="892" cy="398" r="7" fill="#fefae0" stroke="#ddb892"/>
      <circle cx="905" cy="396" r="8" fill="#fff" stroke="#ddb892"/>
      <circle cx="913" cy="401" r="6.5" fill="#fefae0" stroke="#ddb892"/>
      <path d="M 905,388 L 905,383 M 892,391 L 890,387" stroke="#8a5a36" stroke-width="1.5" stroke-linecap="round"/>
    </g>
    ''')

    # Giant Stockpot / Cauldron of Broth on the Left
    parts.append('''
    <!-- BOILING BROTH STOCKPOT (LEFT) -->
    <g id="broth-cauldron" filter="url(#dropShadow)">
      <rect x="175" y="555" width="165" height="15" rx="3" fill="#1b1c1e"/>
      <!-- Blue-orange gas flame -->
      <path d="M 190,555 Q 195,545 200,555 Q 210,542 220,555 Q 230,544 240,555 Q 250,542 260,555 Q 270,545 280,555 Q 290,543 300,555 Q 310,546 320,555 Q 325,548 330,555 Z" fill="#ff7b00" opacity="0.85"/>
      <path d="M 195,555 Q 200,548 205,555 Q 215,546 225,555 Q 235,547 245,555 Q 255,546 265,555 Q 275,548 285,555 Q 295,547 305,555 Q 315,549 325,555 Z" fill="#00f5d4" opacity="0.9"/>

      <!-- Pot Body -->
      <path d="M 180,450 L 180,545 C 180,555 190,558 257,558 C 325,558 335,555 335,545 L 335,450 Z" fill="url(#steelPot)"/>
      <path d="M 180,470 C 160,470 160,495 180,495" fill="none" stroke="#495057" stroke-width="7" stroke-linecap="round"/>
      <path d="M 335,470 C 355,470 355,495 335,495" fill="none" stroke="#495057" stroke-width="7" stroke-linecap="round"/>
      
      <!-- Pot Rim -->
      <ellipse cx="257" cy="450" rx="77" ry="20" fill="#6c757d"/>
      <ellipse cx="257" cy="450" rx="72" ry="17" fill="url(#brothGrad)"/>
      
      <!-- Simmering bubbles -->
      <circle cx="225" cy="448" r="6" fill="#ffe6a7" opacity="0.75"/>
      <circle cx="270" cy="446" r="9" fill="#ffe6a7" opacity="0.8"/>
      <circle cx="245" cy="454" r="5" fill="#fff" opacity="0.85"/>
      <circle cx="290" cy="452" r="7" fill="#ffe6a7" opacity="0.65"/>
      <circle cx="215" cy="453" r="4" fill="#ffd166" opacity="0.7"/>

      <!-- Scallion stalk & kombu kelp in broth -->
      <path d="M 230,452 C 210,420 190,410 170,415" fill="none" stroke="#2d6a4f" stroke-width="12" stroke-linecap="round"/>
      <path d="M 230,452 C 210,420 190,410 170,415" fill="none" stroke="#74c69d" stroke-width="6" stroke-linecap="round"/>
      <path d="M 170,415 C 163,417 155,422 150,425" fill="none" stroke="#f8f9fa" stroke-width="8" stroke-linecap="round"/>
      <polygon points="295,448 315,395 340,405 320,453" fill="#1b4332" opacity="0.9"/>
    </g>
    ''')

    # -------------------------------------------------------------------------
    # 3. BACKGROUND TENTACLES & OCTOPUS BODY (BEHIND COUNTER)
    # -------------------------------------------------------------------------
    parts.append('<!-- BACKGROUND TENTACLES -->')
    
    # Tentacle 1: High Top-Left holding Noodle Basket (Tebo Strainer)
    parts.append('''
    <g id="tentacle-1-noodle-strainer">
      <path d="M 500,450 C 460,360 370,250 280,200 C 240,175 210,210 240,240 C 275,275 330,280 370,340 C 400,390 420,470 470,490" 
            fill="url(#octoArmGrad1)" filter="url(#dropShadow)"/>
      <g fill="url(#suckerGrad)" stroke="#c9184a" stroke-width="1.2">
        <circle cx="430" cy="315" r="9"/> <circle cx="430" cy="315" r="5" fill="#f87171"/>
        <circle cx="390" cy="265" r="8.5"/> <circle cx="390" cy="265" r="4.5" fill="#f87171"/>
        <circle cx="340" cy="225" r="8"/> <circle cx="340" cy="225" r="4" fill="#f87171"/>
        <circle cx="295" cy="205" r="7.5"/> <circle cx="295" cy="205" r="3.5" fill="#f87171"/>
        <circle cx="250" cy="202" r="7"/> <circle cx="250" cy="202" r="3" fill="#f87171"/>
        <circle cx="230" cy="225" r="6.5"/> <circle cx="230" cy="225" r="3" fill="#f87171"/>
      </g>
      <path d="M 235,225 C 220,235 215,260 238,265 C 255,270 265,250 255,235 Z" fill="#e02222"/>

      <!-- Noodle Basket Strainer (Tebo) -->
      <rect x="235" y="190" width="12" height="110" rx="3" transform="rotate(-25, 240, 240)" fill="#a0522d" stroke="#5c2c10" stroke-width="1.5" filter="url(#dropShadow)"/>
      <g transform="translate(195, 270) rotate(-15)">
        <ellipse cx="40" cy="20" rx="26" ry="10" fill="#adb5bd" stroke="#495057" stroke-width="2"/>
        <path d="M 14,20 Q 18,75 40,82 Q 62,75 66,20 Z" fill="#6c757d" opacity="0.85"/>
        <path d="M 20,32 Q 40,42 60,32 M 22,46 Q 40,56 58,46 M 26,60 Q 40,68 54,60" fill="none" stroke="#dee2e6" stroke-width="1.2" opacity="0.75"/>
        <path d="M 25,22 L 32,78 M 40,20 L 40,82 M 55,22 L 48,78" fill="none" stroke="#dee2e6" stroke-width="1.2" opacity="0.75"/>
        
        <!-- Steaming hot ramen noodles shaking in air -->
        <path d="M 24,18 C 15, -15 65,-40 35,-70 C 15,-100 8,-20 30,10" fill="none" stroke="url(#noodleGrad)" stroke-width="3.5" stroke-linecap="round"/>
        <path d="M 32,15 C 25, -25 75,-30 45,-85 C 20,-115 15,-30 42,8" fill="none" stroke="url(#noodleGrad)" stroke-width="3" stroke-linecap="round"/>
        <path d="M 45,15 C 55, -20 15,-50 50,-90 C 75,-120 40,-35 48,12" fill="none" stroke="url(#noodleGrad)" stroke-width="3.2" stroke-linecap="round"/>
        <path d="M 52,18 C 65, -10 35,-45 60,-80 C 80,-105 50,-25 56,15" fill="none" stroke="url(#noodleGrad)" stroke-width="2.8" stroke-linecap="round"/>
        <circle cx="20" cy="-30" r="3" fill="#ffe899"/>
        <circle cx="55" cy="-55" r="2.5" fill="#ffe899"/>
        <circle cx="40" cy="-95" r="2" fill="#fff"/>
        <circle cx="68" cy="-82" r="2.5" fill="#ffe899"/>
      </g>
    </g>
    ''')

    # Tentacle 6: High Top-Right holding Scallion Spice Dish
    parts.append('''
    <g id="tentacle-6-seasoning">
      <path d="M 680,420 C 760,340 830,260 890,240 C 940,225 960,270 920,300 C 880,330 810,360 750,420 C 710,460 670,490 650,500" 
            fill="url(#octoArmGrad2)" filter="url(#dropShadow)"/>
      <g fill="url(#suckerGrad)" stroke="#c9184a" stroke-width="1.2">
        <circle cx="780" cy="315" r="9"/> <circle cx="780" cy="315" r="5" fill="#f87171"/>
        <circle cx="830" cy="275" r="8.5"/> <circle cx="830" cy="275" r="4.5" fill="#f87171"/>
        <circle cx="885" cy="255" r="8"/> <circle cx="885" cy="255" r="4" fill="#f87171"/>
        <circle cx="930" cy="265" r="7.5"/> <circle cx="930" cy="265" r="3.5" fill="#f87171"/>
        <circle cx="915" cy="305" r="7"/> <circle cx="915" cy="305" r="3" fill="#f87171"/>
      </g>
      <path d="M 915,295 C 930,300 940,320 925,335 C 910,345 895,330 905,315 Z" fill="#e02222"/>

      <g transform="translate(875, 320) rotate(35)">
        <ellipse cx="25" cy="10" rx="22" ry="9" fill="#1b4332" stroke="#2d6a4f" stroke-width="2"/>
        <ellipse cx="25" cy="9" rx="18" ry="6" fill="#40916c"/>
        <circle cx="20" cy="9" r="2.5" fill="#74c69d"/>
        <circle cx="26" cy="7" r="3" fill="#95d5b2"/>
        <circle cx="31" cy="9" r="2.5" fill="#52b788"/>
      </g>

      <!-- Scallions & sesame seeds gently fluttering down towards the ramen bowl -->
      <g id="falling-scallions">
        <ellipse cx="850" cy="370" rx="4" ry="2.5" transform="rotate(25, 850, 370)" fill="#52b788" stroke="#1b4332" stroke-width="0.8"/>
        <ellipse cx="835" cy="410" rx="4.5" ry="3" transform="rotate(-30, 835, 410)" fill="#74c69d" stroke="#1b4332" stroke-width="0.8"/>
        <ellipse cx="860" cy="430" rx="3.5" ry="2.2" transform="rotate(45, 860, 430)" fill="#95d5b2" stroke="#2d6a4f" stroke-width="0.8"/>
        <ellipse cx="820" cy="455" rx="4" ry="2.8" transform="rotate(15, 820, 455)" fill="#52b788" stroke="#1b4332" stroke-width="0.8"/>
        <ellipse cx="845" cy="490" rx="4.2" ry="2.5" transform="rotate(-20, 845, 490)" fill="#74c69d" stroke="#1b4332" stroke-width="0.8"/>
        <ellipse cx="785" cy="510" rx="4.5" ry="3" transform="rotate(35, 785, 510)" fill="#52b788" stroke="#1b4332" stroke-width="0.8"/>

        <!-- Sesame seeds -->
        <ellipse cx="840" cy="390" rx="1.5" ry="2.5" transform="rotate(15, 840, 390)" fill="#fff3b0"/>
        <ellipse cx="855" cy="450" rx="1.5" ry="2.5" transform="rotate(-40, 855, 450)" fill="#eddcd2"/>
        <ellipse cx="810" cy="475" rx="1.5" ry="2.5" transform="rotate(25, 810, 475)" fill="#fff3b0"/>
        <ellipse cx="825" cy="520" rx="1.5" ry="2.5" transform="rotate(-15, 825, 520)" fill="#fff3b0"/>
      </g>
    </g>
    ''')

    # Tentacle 8: Far Right Thumbs Up (smooth, distinct silhouette)
    parts.append('''
    <g id="tentacle-8-thumbs-up">
      <path d="M 660,510 C 730,500 800,480 870,510 C 920,530 940,580 890,600 C 830,620 770,550 700,550 C 660,550 630,540 620,530" 
            fill="url(#octoArmGrad2)" filter="url(#dropShadow)"/>
      <g fill="url(#suckerGrad)" stroke="#c9184a" stroke-width="1.2">
        <circle cx="780" cy="500" r="8"/> <circle cx="780" cy="500" r="4" fill="#f87171"/>
        <circle cx="830" cy="505" r="8"/> <circle cx="830" cy="505" r="4" fill="#f87171"/>
        <circle cx="875" cy="525" r="7.5"/> <circle cx="875" cy="525" r="3.5" fill="#f87171"/>
        <circle cx="900" cy="555" r="7"/> <circle cx="900" cy="555" r="3" fill="#f87171"/>
      </g>
      <!-- Stylized upright thumb tip -->
      <path d="M 885,550 C 905,540 910,500 890,490 C 875,480 865,510 875,530 Z" fill="#ff4d4d"/>
      <circle cx="890" cy="505" r="4" fill="#fff" stroke="#e02222" stroke-width="1"/>
    </g>
    ''')

    # Octopus Body & Head
    parts.append('''
    <!-- OCTOPUS CHEF BODY & HEAD -->
    <g id="octopus-chef-main" filter="url(#dropShadow)">
      <!-- Torso Base -->
      <ellipse cx="590" cy="480" rx="90" ry="80" fill="url(#octoHeadGrad)"/>

      <!-- Apron (Maekake) -->
      <path d="M 520,460 L 660,460 L 675,580 C 675,600 505,600 505,580 Z" fill="url(#apronGrad)" stroke="#2b3a67" stroke-width="1.5"/>
      <path d="M 505,465 Q 590,480 675,465" fill="none" stroke="#f8f9fa" stroke-width="4"/>
      <!-- Apron Crest: Golden Double Ring with Japanese Ramen Crest -->
      <circle cx="590" cy="525" r="26" fill="none" stroke="#ffd166" stroke-width="2.5"/>
      <circle cx="590" cy="525" r="22" fill="none" stroke="#ffffff" stroke-width="1"/>
      <!-- Stylized Ramen Crest in Apron -->
      <path d="M 576,525 Q 590,535 604,525" fill="none" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
      <path d="M 580,518 Q 590,510 600,518" fill="none" stroke="#ffd166" stroke-width="2" stroke-linecap="round"/>

      <!-- Head (Mantle) -->
      <path d="M 470,380 C 460,250 520,170 595,170 C 670,170 730,250 720,380 C 720,430 680,460 595,460 C 510,460 470,430 470,380 Z" 
            fill="url(#octoHeadGrad)"/>
      
      <!-- Specular Highlights -->
      <ellipse cx="560" cy="230" rx="55" ry="32" transform="rotate(-15, 560, 230)" fill="#ffffff" opacity="0.22"/>
      <ellipse cx="545" cy="220" rx="25" ry="14" transform="rotate(-15, 545, 220)" fill="#ffffff" opacity="0.4"/>

      <!-- Chef Headband (Hachimaki) -->
      <path d="M 720,300 C 760,285 785,295 805,280 C 790,310 765,315 725,315 Z" fill="url(#hachimakiGrad)" stroke="#ced4da" stroke-width="1"/>
      <path d="M 722,310 C 770,315 795,335 815,345 C 790,350 760,340 720,325 Z" fill="url(#hachimakiGrad)" stroke="#ced4da" stroke-width="1"/>
      <circle cx="722" cy="310" r="10" fill="#ffffff" stroke="#ced4da" stroke-width="1.5"/>

      <!-- Front headband strap -->
      <path d="M 472,315 Q 590,350 718,305 L 722,325 Q 590,370 468,335 Z" fill="url(#hachimakiGrad)" stroke="#ced4da" stroke-width="1.5"/>
      <circle cx="592" cy="340" r="10" fill="#d90429"/>
      <path d="M 592,332 L 594,338 L 600,340 L 594,342 L 592,348 L 590,342 L 584,340 L 590,338 Z" fill="#ffd166"/>

      <!-- EXPRESSIVE ANIME/MANGA FACE -->
      <!-- Rosy blush cheeks -->
      <ellipse cx="510" cy="405" rx="18" ry="10" fill="#ff4d6d" opacity="0.5" filter="url(#softGlow)"/>
      <ellipse cx="675" cy="400" rx="18" ry="10" fill="#ff4d6d" opacity="0.5" filter="url(#softGlow)"/>

      <!-- Left Eye -->
      <g id="left-eye">
        <ellipse cx="535" cy="365" rx="22" ry="26" fill="#1b1b1e"/>
        <ellipse cx="537" cy="365" rx="19" ry="23" fill="#2d1b10"/>
        <ellipse cx="538" cy="366" rx="16" ry="20" fill="#6a3810"/>
        <ellipse cx="540" cy="367" rx="12" ry="15" fill="#000000"/>
        <circle cx="545" cy="357" r="7.5" fill="#ffffff"/>
        <circle cx="532" cy="377" r="3.5" fill="#ffffff" opacity="0.85"/>
        <circle cx="547" cy="375" r="2" fill="#ffffff" opacity="0.9"/>
        <path d="M 512,355 Q 538,332 562,350" fill="none" stroke="#2b090d" stroke-width="4.5" stroke-linecap="round"/>
        <path d="M 515,338 Q 542,330 560,342" fill="none" stroke="#800e1b" stroke-width="3.5" stroke-linecap="round"/>
      </g>

      <!-- Right Eye -->
      <g id="right-eye">
        <ellipse cx="650" cy="360" rx="22" ry="26" fill="#1b1b1e"/>
        <ellipse cx="648" cy="360" rx="19" ry="23" fill="#2d1b10"/>
        <ellipse cx="647" cy="361" rx="16" ry="20" fill="#6a3810"/>
        <ellipse cx="645" cy="362" rx="12" ry="15" fill="#000000"/>
        <circle cx="650" cy="352" r="7.5" fill="#ffffff"/>
        <circle cx="637" cy="372" r="3.5" fill="#ffffff" opacity="0.85"/>
        <circle cx="652" cy="370" r="2" fill="#ffffff" opacity="0.9"/>
        <path d="M 625,350 Q 648,330 674,350" fill="none" stroke="#2b090d" stroke-width="4.5" stroke-linecap="round"/>
        <path d="M 626,340 Q 645,328 672,335" fill="none" stroke="#800e1b" stroke-width="3.5" stroke-linecap="round"/>
      </g>

      <!-- Octopus Siphon Mouth Smile -->
      <path d="M 578,405 Q 592,398 606,405 Q 612,425 592,427 Q 572,425 578,405 Z" fill="#99101d" stroke="#59060f" stroke-width="2"/>
      <ellipse cx="592" cy="413" rx="11" ry="8" fill="#e02222"/>
      <path d="M 584,415 Q 592,422 600,415" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
      <ellipse cx="592" cy="406" rx="5" ry="2" fill="#ff7b7b"/>
    </g>
    ''')

    # -------------------------------------------------------------------------
    # 4. WOODEN COUNTERTOP & TABLETOP PREP STATIONS
    # -------------------------------------------------------------------------
    parts.append('<!-- COUNTERTOP BASE -->')
    parts.append('''
    <!-- Counter Surface -->
    <polygon points="60,630 1140,630 1200,730 0,730" fill="url(#counterWood)" filter="url(#counterShadow)"/>
    <line x1="0" y1="730" x2="1200" y2="730" stroke="#f6bd60" stroke-width="3"/>
    <!-- Counter Front Drop -->
    <rect x="0" y="730" width="1200" height="170" fill="url(#counterFront)"/>
    ''')
    for px in range(0, 1220, 60):
        parts.append(f'<line x1="{px}" y1="730" x2="{px}" y2="900" stroke="#120803" stroke-width="3"/>')
        parts.append(f'<line x1="{px+1}" y1="730" x2="{px+1}" y2="900" stroke="#5a3014" stroke-width="1.2"/>')

    # Cutting Board on Left Counter
    parts.append('''
    <g id="cutting-board" filter="url(#dropShadow)">
      <polygon points="170,645 410,645 435,715 145,715" fill="#b07d52" stroke="#684120" stroke-width="2"/>
      <polygon points="145,715 435,715 435,728 145,728" fill="#684120"/>
      <!-- Wood grain -->
      <line x1="200" y1="645" x2="175" y2="715" stroke="#94633b" stroke-width="1.5"/>
      <line x1="280" y1="645" x2="255" y2="715" stroke="#94633b" stroke-width="1.5"/>
      <line x1="360" y1="645" x2="335" y2="715" stroke="#94633b" stroke-width="1.5"/>

      <!-- Rolled Braised Chashu Pork Belly on Board -->
      <path d="M 230,670 C 230,655 290,655 290,670 L 285,695 C 285,705 225,705 225,695 Z" fill="url(#chashuPork)"/>
      <ellipse cx="260" cy="665" rx="30" ry="12" fill="#582110"/>
      <line x1="230" y1="678" x2="288" y2="678" stroke="#eddcd2" stroke-width="1.5"/>
      <line x1="228" y1="687" x2="286" y2="687" stroke="#eddcd2" stroke-width="1.5"/>

      <!-- Fresh scallion stalks on board -->
      <path d="M 160,705 L 230,690" stroke="#2d6a4f" stroke-width="6" stroke-linecap="round"/>
      <path d="M 160,705 L 230,690" stroke="#74c69d" stroke-width="3" stroke-linecap="round"/>
      <circle cx="210" cy="708" r="3.5" fill="#52b788" stroke="#1b4332" stroke-width="1"/>
      <circle cx="210" cy="708" r="1.8" fill="#d8f3dc"/>
    </g>
    ''')

    # Side Dishes on Right Counter (Gyoza, Tea, Chopsticks)
    parts.append('''
    <g id="counter-right-props" filter="url(#dropShadow)">
      <!-- Plate of Crispy Gyoza -->
      <ellipse cx="980" cy="670" rx="65" ry="24" fill="#ffffff" stroke="#dee2e6" stroke-width="2"/>
      <ellipse cx="980" cy="668" rx="55" ry="18" fill="#f8f9fa"/>
      
      <!-- Gyoza 1 -->
      <path d="M 935,665 C 945,652 965,652 975,665 C 960,672 950,672 935,665 Z" fill="#faedcd" stroke="#d4a373" stroke-width="1.2"/>
      <path d="M 940,667 Q 955,673 970,667" stroke="#bc6c25" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="945" y1="658" x2="948" y2="664" stroke="#d4a373" stroke-width="1"/>
      <line x1="955" y1="656" x2="956" y2="664" stroke="#d4a373" stroke-width="1"/>
      <line x1="965" y1="658" x2="964" y2="664" stroke="#d4a373" stroke-width="1"/>

      <!-- Gyoza 2 -->
      <path d="M 965,670 C 975,657 995,657 1005,670 C 990,677 980,677 965,670 Z" fill="#faedcd" stroke="#d4a373" stroke-width="1.2"/>
      <path d="M 970,672 Q 985,678 1000,672" stroke="#bc6c25" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="975" y1="663" x2="978" y2="669" stroke="#d4a373" stroke-width="1"/>
      <line x1="985" y1="661" x2="986" y2="669" stroke="#d4a373" stroke-width="1"/>
      <line x1="995" y1="663" x2="994" y2="669" stroke="#d4a373" stroke-width="1"/>

      <!-- Gyoza 3 -->
      <path d="M 995,675 C 1005,662 1025,662 1035,675 C 1020,682 1010,682 995,675 Z" fill="#faedcd" stroke="#d4a373" stroke-width="1.2"/>
      <path d="M 1000,677 Q 1015,683 1030,677" stroke="#bc6c25" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="1005" y1="668" x2="1008" y2="674" stroke="#d4a373" stroke-width="1"/>
      <line x1="1015" y1="666" x2="1016" y2="674" stroke="#d4a373" stroke-width="1"/>
      <line x1="1025" y1="668" x2="1024" y2="674" stroke="#d4a373" stroke-width="1"/>

      <!-- Dipping Sauce Dish -->
      <ellipse cx="1065" cy="688" rx="20" ry="9" fill="#e9ecef" stroke="#adb5bd" stroke-width="1.5"/>
      <ellipse cx="1065" cy="687" rx="16" ry="6.5" fill="#2b1408"/>
      <circle cx="1063" cy="687" r="2.5" fill="#d90429" opacity="0.85"/>

      <!-- Ceramic Hot Green Tea Cup (Yunomi) -->
      <path d="M 885,635 L 890,685 C 890,692 918,692 918,685 L 923,635 Z" fill="#e9d8a6" stroke="#b08968" stroke-width="1.5"/>
      <ellipse cx="904" cy="635" rx="19" ry="7" fill="#52b788"/>
      <path d="M 904,628 Q 910,612 902,602" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" opacity="0.45"/>

      <!-- Pair of Premium Wooden Chopsticks on Ceramic Rest in Foreground -->
      <path d="M 810,750 C 815,740 830,740 835,750 C 830,755 815,755 810,750 Z" fill="#e02222" stroke="#99101d" stroke-width="1"/>
      <polygon points="760,752 920,742 920,746 760,755" fill="#5c3818"/>
      <polygon points="760,756 920,748 920,752 760,759" fill="#754822"/>
      <rect x="885" y="743" width="20" height="9" fill="#d4af37"/>
    </g>
    ''')

    # -------------------------------------------------------------------------
    # 5. FOREGROUND TENTACLES (WORKING ON TOP OF COUNTER & PREP BOARD)
    # -------------------------------------------------------------------------
    parts.append('<!-- FOREGROUND ACTIVE TENTACLES & TOOLS (OVER COUNTER) -->')

    # Tentacle 2: Holding Wooden Ladle with Luscious Flowing Broth
    parts.append('''
    <g id="tentacle-2-broth-ladle">
      <!-- Arm swooping from octopus side towards the cauldron -->
      <path d="M 520,480 C 430,470 360,420 310,430 C 270,440 270,480 305,490 C 350,500 400,540 480,550" 
            fill="url(#octoArmGrad1)" filter="url(#dropShadow)"/>
      <g fill="url(#suckerGrad)" stroke="#c9184a" stroke-width="1.2">
        <circle cx="410" cy="470" r="8.5"/> <circle cx="410" cy="470" r="4" fill="#f87171"/>
        <circle cx="360" cy="445" r="8"/> <circle cx="360" cy="445" r="4" fill="#f87171"/>
        <circle cx="315" cy="440" r="7.5"/> <circle cx="315" cy="440" r="3.5" fill="#f87171"/>
        <circle cx="285" cy="460" r="7"/> <circle cx="285" cy="460" r="3" fill="#f87171"/>
      </g>
      <!-- Coiled tentacle holding the wooden ladle handle -->
      <path d="M 290,455 C 275,465 280,485 300,485 C 315,485 320,465 305,455 Z" fill="#e02222"/>

      <!-- Wooden Ladle dipping into cauldron -->
      <g id="ladle-tool" filter="url(#dropShadow)">
        <polygon points="255,445 325,465 323,472 253,452" fill="#8d5524" stroke="#4a2810" stroke-width="1"/>
        <ellipse cx="250" cy="448" rx="20" ry="12" fill="#6f3e1b" stroke="#381d0a" stroke-width="1.5"/>
        <ellipse cx="250" cy="448" rx="16" ry="9" fill="url(#brothGrad)"/>
      </g>

      <!-- Glossy liquid stream of tonkotsu broth pouring from ladle -->
      <path d="M 260,452 C 285,475 315,505 345,540 C 355,535 345,520 320,490 C 295,465 275,446 260,452 Z" fill="url(#brothGrad)" opacity="0.95" filter="url(#dropShadow)"/>
      <path d="M 268,455 Q 305,490 338,530" fill="none" stroke="#fff3b0" stroke-width="2" stroke-linecap="round" opacity="0.9"/>
      <circle cx="295" cy="485" r="3" fill="#ffd166"/>
      <circle cx="330" cy="525" r="3.5" fill="#ffd166"/>
      <circle cx="350" cy="548" r="2.5" fill="#ffe899"/>
    </g>
    ''')

    # Tentacle 3: Steadying arm resting ON the cutting board
    parts.append('''
    <g id="tentacle-3-steadying">
      <path d="M 480,560 C 430,590 340,610 280,640 C 240,660 250,700 290,700 C 330,700 360,660 440,630" 
            fill="url(#octoArmGrad1)" filter="url(#dropShadow)"/>
      <g fill="url(#suckerGrad)" stroke="#c9184a" stroke-width="1.2">
        <circle cx="370" cy="625" r="8"/> <circle cx="370" cy="625" r="4" fill="#f87171"/>
        <circle cx="310" cy="650" r="7.5"/> <circle cx="310" cy="650" r="3.5" fill="#f87171"/>
        <circle cx="270" cy="680" r="7"/> <circle cx="270" cy="680" r="3" fill="#f87171"/>
      </g>
      <path d="M 285,685 C 275,695 295,705 315,700 C 325,695 315,680 295,682 Z" fill="#eb2a2a"/>
    </g>
    ''')

    # Tentacle 4 & Japanese Santoku Knife: slicing chashu pork ON TOP of cutting board
    parts.append('''
    <g id="tentacle-4-knife-slicing">
      <path d="M 520,520 C 460,530 420,550 380,580 C 350,605 360,640 395,640 C 435,640 460,590 510,570" 
            fill="url(#octoArmGrad1)" filter="url(#dropShadow)"/>
      <g fill="url(#suckerGrad)" stroke="#c9184a" stroke-width="1.2">
        <circle cx="445" cy="550" r="8"/> <circle cx="445" cy="550" r="4" fill="#f87171"/>
        <circle cx="395" cy="575" r="7.5"/> <circle cx="395" cy="575" r="3.5" fill="#f87171"/>
        <circle cx="365" cy="610" r="7"/> <circle cx="365" cy="610" r="3" fill="#f87171"/>
      </g>
      <path d="M 375,615 C 360,625 365,645 385,645 C 400,645 405,630 395,615 Z" fill="#e02222"/>

      <!-- Japanese Santoku Knife -->
      <g transform="translate(365, 635) rotate(-10)" filter="url(#dropShadow)">
        <rect x="-44" y="-6" width="44" height="13" rx="3" fill="#2b1810" stroke="#100804" stroke-width="1"/>
        <rect x="-2" y="-7" width="5" height="15" fill="#d4af37"/>
        <path d="M 3,-7 L 85,-7 C 105,-4 112,6 110,18 L 3,18 Z" fill="url(#knifeBlade)" stroke="#495057" stroke-width="1"/>
        <line x1="3" y1="16" x2="108" y2="16" stroke="#ffffff" stroke-width="2"/>
        <ellipse cx="25" cy="4" rx="4" ry="2" fill="#d8dde2"/>
        <ellipse cx="40" cy="4" rx="4" ry="2" fill="#d8dde2"/>
        <ellipse cx="55" cy="4" rx="4" ry="2" fill="#d8dde2"/>
        <ellipse cx="70" cy="4" rx="4" ry="2" fill="#d8dde2"/>
        <ellipse cx="85" cy="4" rx="4" ry="2" fill="#d8dde2"/>
      </g>

      <!-- Sliced rounds of savory chashu pork falling cleanly in front of knife -->
      <g transform="translate(310, 680)" filter="url(#dropShadow)">
        <ellipse cx="0" cy="0" rx="18" ry="12" fill="url(#chashuPork)" stroke="#4a1805" stroke-width="1.5"/>
        <path d="M -11,0 C -7,-9 7,-9 11,0 C 13,7 0,9 -6,4" fill="none" stroke="#fff" stroke-width="2" opacity="0.85"/>
        <line x1="-12" y1="-3" x2="-4" y2="-5" stroke="#2b0d04" stroke-width="2"/>
        <line x1="2" y1="2" x2="10" y2="0" stroke="#2b0d04" stroke-width="2"/>
      </g>
      <g transform="translate(340, 690)" filter="url(#dropShadow)">
        <ellipse cx="0" cy="0" rx="19" ry="13" fill="url(#chashuPork)" stroke="#4a1805" stroke-width="1.5"/>
        <path d="M -12,0 C -8,-10 8,-10 12,0 C 14,8 0,10 -7,4" fill="none" stroke="#fff" stroke-width="2.2" opacity="0.85"/>
        <line x1="-10" y1="-2" x2="-2" y2="-4" stroke="#2b0d04" stroke-width="2"/>
        <line x1="4" y1="3" x2="12" y2="1" stroke="#2b0d04" stroke-width="2"/>
      </g>
      <!-- Chopped scallion rounds next to pork -->
      <circle cx="365" cy="700" r="4" fill="#52b788" stroke="#1b4332" stroke-width="1"/>
      <circle cx="365" cy="700" r="2" fill="#d8f3dc"/>
      <circle cx="378" cy="708" r="3.5" fill="#52b788" stroke="#1b4332" stroke-width="1"/>
      <circle cx="378" cy="708" r="1.8" fill="#d8f3dc"/>
      <circle cx="390" cy="696" r="4.2" fill="#74c69d" stroke="#1b4332" stroke-width="1"/>
      <circle cx="390" cy="696" r="2.2" fill="#d8f3dc"/>
    </g>
    ''')

    # -------------------------------------------------------------------------
    # 6. THE MASTERPIECE RAMEN BOWL (SHOWPIECE ON CENTER COUNTER)
    # -------------------------------------------------------------------------
    parts.append('<!-- MASTERPIECE RAMEN BOWL (CENTER SHOWPIECE) -->')
    parts.append('''
    <g id="masterpiece-ramen-bowl" filter="url(#counterShadow)">
      <!-- Foot ring shadow -->
      <ellipse cx="560" cy="805" rx="95" ry="18" fill="#1b0808" opacity="0.7"/>
      <!-- Foot ring base -->
      <ellipse cx="560" cy="795" rx="90" ry="16" fill="#3d050a" stroke="#d4af37" stroke-width="1.5"/>

      <!-- Deep Lacquer Ceramic Bowl Body -->
      <path d="M 370,685 C 375,775 450,800 560,800 C 670,800 745,775 750,685 Z" fill="url(#bowlCeramic)" stroke="#2b0507" stroke-width="2"/>
      
      <!-- Outer Bowl Traditional Meander Crest -->
      <path d="M 390,705 Q 560,735 730,705" fill="none" stroke="#d4af37" stroke-width="6" opacity="0.9"/>
      <path d="M 405,707 Q 560,737 715,707" fill="none" stroke="#ffffff" stroke-width="1.8" stroke-dasharray="8 6"/>

      <!-- Bowl Outer Rim -->
      <ellipse cx="560" cy="682" rx="190" ry="58" fill="#9e1522" stroke="#d4af37" stroke-width="3"/>
      <!-- Bowl Inner Rim -->
      <ellipse cx="560" cy="682" rx="180" ry="52" fill="#fdf0d5" stroke="#780000" stroke-width="2"/>

      <!-- GLORIOUS BROTH -->
      <ellipse cx="560" cy="684" rx="172" ry="48" fill="url(#brothGrad)"/>
      <ellipse cx="550" cy="680" rx="145" ry="38" fill="none" stroke="#ffd166" stroke-width="2.5" opacity="0.6"/>
      <ellipse cx="530" cy="675" rx="90" ry="22" fill="#fff" opacity="0.2"/>

      <!-- WAVY RAMEN NOODLE MASS -->
      <g id="bowl-noodles" opacity="0.95">
        <path d="M 430,685 Q 450,675 470,686 Q 490,697 510,685 Q 530,673 550,685 Q 570,697 590,685 Q 610,673 630,685 Q 650,697 670,685" fill="none" stroke="url(#noodleGrad)" stroke-width="4.5" stroke-linecap="round"/>
        <path d="M 425,692 Q 445,680 465,692 Q 485,704 505,692 Q 525,680 545,692 Q 565,704 585,692 Q 605,680 625,692 Q 645,704 665,692" fill="none" stroke="url(#noodleGrad)" stroke-width="4.2" stroke-linecap="round"/>
        <path d="M 435,700 Q 455,688 475,700 Q 495,712 515,700 Q 535,688 555,700 Q 575,712 595,700 Q 615,688 635,700 Q 655,712 675,700" fill="none" stroke="url(#noodleGrad)" stroke-width="4.5" stroke-linecap="round"/>
        <path d="M 445,678 Q 465,668 485,678 Q 505,688 525,678 Q 545,668 565,678 Q 585,688 605,678 Q 625,668 645,678" fill="none" stroke="url(#noodleGrad)" stroke-width="3.8" stroke-linecap="round"/>
      </g>

      <!-- ARTFUL RAMEN TOPPINGS -->

      <!-- 1. Crisp Dark Nori Sheets -->
      <g id="topping-nori" filter="url(#dropShadow)">
        <polygon points="410,610 455,580 480,670 435,695" fill="#132a13" stroke="#0b1a0b" stroke-width="1.5"/>
        <polygon points="410,610 455,580 480,670 435,695" fill="#1b4332" opacity="0.35"/>
        <polygon points="450,595 495,570 520,665 475,685" fill="#0b1a0b" stroke="#050d05" stroke-width="1.5"/>
        <polygon points="450,595 495,570 520,665 475,685" fill="#1b4332" opacity="0.4"/>
      </g>

      <!-- 2. Tender Braised Chashu Pork Slices in Bowl -->
      <g id="topping-chashu-1" transform="translate(480, 675) rotate(-10)" filter="url(#dropShadow)">
        <ellipse cx="0" cy="0" rx="42" ry="28" fill="url(#chashuPork)" stroke="#3d1308" stroke-width="2"/>
        <path d="M -26,2 C -20,-18 15,-20 28,0 C 35,16 5,24 -14,14 C -22,8 -24,-4 -12,-8" fill="none" stroke="#fdf0d5" stroke-width="4.5" stroke-linecap="round" opacity="0.9"/>
        <path d="M -26,2 C -20,-18 15,-20 28,0 C 35,16 5,24 -14,14 C -22,8 -24,-4 -12,-8" fill="none" stroke="#eddcd2" stroke-width="2" stroke-linecap="round"/>
        <line x1="-25" y1="-5" x2="-8" y2="-9" stroke="#1f0904" stroke-width="3" stroke-linecap="round"/>
        <line x1="2" y1="-12" x2="18" y2="-10" stroke="#1f0904" stroke-width="3.5" stroke-linecap="round"/>
        <line x1="8" y1="5" x2="26" y2="2" stroke="#1f0904" stroke-width="3" stroke-linecap="round"/>
        <line x1="-15" y1="10" x2="2" y2="12" stroke="#1f0904" stroke-width="2.5" stroke-linecap="round"/>
      </g>

      <g id="topping-chashu-2" transform="translate(535, 665) rotate(15)" filter="url(#dropShadow)">
        <ellipse cx="0" cy="0" rx="40" ry="26" fill="url(#chashuPork)" stroke="#3d1308" stroke-width="2"/>
        <path d="M -24,2 C -18,-16 14,-18 26,0 C 32,15 4,22 -12,12 C -20,6 -22,-3 -10,-7" fill="none" stroke="#fdf0d5" stroke-width="4" stroke-linecap="round" opacity="0.9"/>
        <path d="M -24,2 C -18,-16 14,-18 26,0 C 32,15 4,22 -12,12 C -20,6 -22,-3 -10,-7" fill="none" stroke="#eddcd2" stroke-width="1.8" stroke-linecap="round"/>
        <line x1="-20" y1="-5" x2="-5" y2="-8" stroke="#1f0904" stroke-width="3" stroke-linecap="round"/>
        <line x1="4" y1="-10" x2="20" y2="-8" stroke="#1f0904" stroke-width="3.5" stroke-linecap="round"/>
        <line x1="6" y1="6" x2="22" y2="3" stroke="#1f0904" stroke-width="3" stroke-linecap="round"/>
      </g>

      <!-- 3. Menma (Seasoned Bamboo Shoots) -->
      <g id="topping-menma" filter="url(#dropShadow)">
        <polygon points="610,655 655,645 658,655 613,665" fill="#c49a45" stroke="#875f1b" stroke-width="1"/>
        <polygon points="615,662 660,652 663,662 618,672" fill="#dcb15b" stroke="#875f1b" stroke-width="1"/>
        <polygon points="612,670 656,660 659,670 615,680" fill="#b08632" stroke="#734e0f" stroke-width="1"/>
      </g>

      <!-- 4. Classic Pink Narutomaki (Spiral Fish Cake) -->
      <g id="topping-naruto" transform="translate(565, 705) rotate(12)" filter="url(#dropShadow)">
        <path d="M 0,-20 L 5,-18 L 10,-21 L 14,-16 L 19,-17 L 21,-11 L 25,-10 L 25,-4 L 27,0 L 25,5 L 24,10 L 20,13 L 18,18 L 12,18 L 8,22 L 3,19 L -2,22 L -6,18 L -12,20 L -15,15 L -20,15 L -21,9 L -25,7 L -23,1 L -26,-3 L -22,-8 L -23,-13 L -17,-14 L -15,-20 L -9,-18 Z" fill="#ffffff" stroke="#e9ecef" stroke-width="1.2"/>
        <path d="M 0,-1 C 6,-3 9,4 6,8 C 2,12 -8,9 -9,2 C -11,-6 2,-12 9,-8 C 16,-4 16,9 9,14" fill="none" stroke="#ff007f" stroke-width="3.5" stroke-linecap="round"/>
      </g>

      <!-- 5. Fresh Chopped Scallions (Negi) -->
      <g id="topping-negi">
    ''')
    
    negi_cluster = [
        (515, 695, 4.5, "#52b788"), (525, 690, 5, "#74c69d"), (535, 697, 4.2, "#40916c"),
        (522, 702, 4.8, "#52b788"), (532, 706, 4.2, "#74c69d"), (542, 700, 5.2, "#95d5b2"),
        (512, 708, 4.0, "#2d6a4f"), (520, 712, 4.5, "#52b788"), (538, 711, 4.0, "#40916c"),
        (548, 707, 4.6, "#74c69d"), (505, 698, 3.8, "#52b788"), (528, 685, 4.4, "#95d5b2")
    ]
    for nx, ny, nr, ncol in negi_cluster:
        parts.append(f'''
        <circle cx="{nx}" cy="{ny}" r="{nr}" fill="{ncol}" stroke="#1b4332" stroke-width="1"/>
        <circle cx="{nx}" cy="{ny}" r="{nr*0.5}" fill="#d8f3dc"/>
        ''')
    parts.append('</g><!-- end topping-negi -->')
    
    sesame_seeds = [
        (470, 700), (495, 715), (555, 722), (580, 718), (560, 685), (635, 680), (620, 710)
    ]
    for sx, sy in sesame_seeds:
        parts.append(f'<ellipse cx="{sx}" cy="{sy}" rx="1.8" ry="1.2" transform="rotate(35, {sx}, {sy})" fill="#fff3b0"/>')

    parts.append('</g><!-- end masterpiece-ramen-bowl -->')

    # -------------------------------------------------------------------------
    # 7. FOREGROUND ARMS INTERACTING DIRECTLY WITH BOWL
    # -------------------------------------------------------------------------
    parts.append('<!-- ARMS DIRECTLY INTERACTING WITH RAMEN BOWL -->')

    # Tentacle 5 & Bamboo Cooking Chopsticks (Saibashi): placing the glowing Ajitsuke Tamago into the bowl!
    parts.append('''
    <g id="tentacle-5-chopsticks-egg">
      <path d="M 640,470 C 690,480 720,530 690,570 C 670,595 635,595 625,565 C 615,535 600,510 575,495" 
            fill="url(#octoArmGrad2)" filter="url(#dropShadow)"/>
      <g fill="url(#suckerGrad)" stroke="#c9184a" stroke-width="1.2">
        <circle cx="675" cy="505" r="8"/> <circle cx="675" cy="505" r="4" fill="#f87171"/>
        <circle cx="695" cy="545" r="7.5"/> <circle cx="695" cy="545" r="3.5" fill="#f87171"/>
        <circle cx="665" cy="580" r="7"/> <circle cx="665" cy="580" r="3" fill="#f87171"/>
      </g>
      <path d="M 630,565 C 615,575 625,595 645,590 C 658,585 650,565 635,565 Z" fill="#eb2a2a"/>

      <!-- High-contrast natural bamboo chopsticks with vermilion tips (Saibashi) -->
      <line x1="660" y1="520" x2="600" y2="675" stroke="#f3c066" stroke-width="5" stroke-linecap="round" filter="url(#dropShadow)"/>
      <line x1="660" y1="520" x2="648" y2="550" stroke="#c1121f" stroke-width="5.5" stroke-linecap="round"/>
      <line x1="610" y1="650" x2="600" y2="675" stroke="#4a2810" stroke-width="3" stroke-linecap="round"/>

      <line x1="645" y1="530" x2="585" y2="685" stroke="#f3c066" stroke-width="4.5" stroke-linecap="round" filter="url(#dropShadow)"/>
      <line x1="645" y1="530" x2="633" y2="560" stroke="#c1121f" stroke-width="5" stroke-linecap="round"/>
      <line x1="595" y1="660" x2="585" y2="685" stroke="#4a2810" stroke-width="2.5" stroke-linecap="round"/>

      <!-- Halved Marinated Ramen Egg held at chopstick tips -->
      <g id="held-egg" transform="translate(590, 675) rotate(-22)" filter="url(#dropShadow)">
        <ellipse cx="0" cy="0" rx="26" ry="18" fill="url(#eggWhite)" stroke="#8d5b2d" stroke-width="2"/>
        <circle cx="0" cy="0" r="12" fill="url(#eggYolk)"/>
        <ellipse cx="3" cy="-3" rx="4" ry="2.5" fill="#ffffff" opacity="0.85"/>
        <circle cx="-3" cy="4" r="1.5" fill="#ffffff" opacity="0.6"/>
      </g>
    </g>
    ''')

    # Tentacle 7: Presenting the Finished Masterpiece Bowl to the Customer
    parts.append('''
    <g id="tentacle-7-serving-bowl">
      <path d="M 640,540 C 700,580 750,650 720,720 C 695,765 635,765 590,735 C 570,720 580,695 610,705 C 640,715 670,710 680,680 C 690,640 650,600 610,570" 
            fill="url(#octoArmGrad2)" filter="url(#dropShadow)"/>
      <g fill="url(#suckerGrad)" stroke="#c9184a" stroke-width="1.2">
        <circle cx="715" cy="660" r="9"/> <circle cx="715" cy="660" r="4.5" fill="#f87171"/>
        <circle cx="680" cy="735" r="8.5"/> <circle cx="680" cy="735" r="4" fill="#f87171"/>
        <circle cx="620" cy="745" r="8"/> <circle cx="620" cy="745" r="4" fill="#f87171"/>
        <circle cx="585" cy="725" r="7.5"/> <circle cx="585" cy="725" r="3.5" fill="#f87171"/>
      </g>
      <path d="M 590,725 C 575,720 575,700 595,700 C 610,700 610,720 595,725 Z" fill="#e02222"/>
    </g>
    ''')

    # -------------------------------------------------------------------------
    # 8. BILLOWING STEAM & AROMATIC VAPORS
    # -------------------------------------------------------------------------
    parts.append('<!-- STEAM & VAPOR TRAILS -->')
    parts.append('''
    <g id="steam-effects" opacity="0.65">
      <path d="M 240,430 C 220,360 270,300 230,220 C 195,150 250,90 280,50" 
            fill="none" stroke="#ffffff" stroke-width="18" stroke-linecap="round" filter="url(#steamBlur)" opacity="0.4"/>
      <path d="M 270,420 C 290,340 220,280 280,190 C 330,120 280,70 310,20" 
            fill="none" stroke="#ffffff" stroke-width="12" stroke-linecap="round" filter="url(#steamBlur)" opacity="0.5"/>
      <path d="M 255,425 C 240,350 260,290 245,210 C 230,140 270,80 295,30" 
            fill="none" stroke="#ffeaa7" stroke-width="6" stroke-linecap="round" opacity="0.6"/>

      <!-- Steam from Masterpiece Bowl -->
      <path d="M 540,640 C 510,570 560,500 520,420 C 490,360 540,290 500,220" 
            fill="none" stroke="#ffffff" stroke-width="14" stroke-linecap="round" filter="url(#steamBlur)" opacity="0.45"/>
      <path d="M 590,630 C 630,550 580,480 620,400 C 650,340 610,270 630,200" 
            fill="none" stroke="#ffffff" stroke-width="12" stroke-linecap="round" filter="url(#steamBlur)" opacity="0.4"/>
      <path d="M 560,635 C 540,560 580,490 550,410 C 520,340 570,280 540,210" 
            fill="none" stroke="#fff" stroke-width="4.5" stroke-linecap="round" opacity="0.75"/>
      <path d="M 580,635 C 610,570 570,510 600,440 C 625,380 595,320 620,250" 
            fill="none" stroke="#ffe8d6" stroke-width="3.5" stroke-linecap="round" opacity="0.7"/>

      <!-- Noodle basket steam -->
      <path d="M 230,210 C 200,160 240,100 210,50" 
            fill="none" stroke="#ffffff" stroke-width="8" stroke-linecap="round" filter="url(#steamBlur)" opacity="0.5"/>
    </g>
    ''')

    # -------------------------------------------------------------------------
    # 9. FOREGROUND FRAME: ROOF, NOREN CURTAINS & LANTERNS
    # -------------------------------------------------------------------------
    parts.append('<!-- FOREGROUND FRAME: ROOF, NOREN & LANTERNS -->')

    # Roof Awning
    parts.append('''
    <g id="stall-roof" filter="url(#dropShadow)">
      <rect x="0" y="45" width="1200" height="26" fill="url(#postWood)"/>
      <line x1="0" y1="71" x2="1200" y2="71" stroke="#251208" stroke-width="3"/>
      <polygon points="0,0 1200,0 1200,50 0,50" fill="url(#roofWood)"/>
    ''')
    for rx in range(0, 1240, 50):
        parts.append(f'<polygon points="{rx},0 {rx+18},0 {rx+24},50 {rx+6},50" fill="url(#tileGrad)"/>')
        parts.append(f'<circle cx="{rx+15}" cy="50" r="7" fill="#805035" stroke="#362219" stroke-width="1.5"/>')
        parts.append(f'<circle cx="{rx+15}" cy="50" r="3.5" fill="#d4af37"/>')

    parts.append('''
      <!-- Wooden Support Pillars -->
      <rect x="25" y="70" width="40" height="610" fill="url(#postWood)"/>
      <rect x="1135" y="70" width="40" height="610" fill="url(#postWood)"/>
      <polygon points="25,130 85,73 25,73" fill="#3b2214"/>
      <polygon points="1175,130 1115,73 1175,73" fill="#3b2214"/>
    </g>
    ''')

    # Noren Curtains with 100% Vector Emblems & Crests (No font dependencies!)
    parts.append('''
    <g id="noren-curtains" filter="url(#dropShadow)">
      <rect x="70" y="68" width="1060" height="9" rx="3" fill="#c49a45" stroke="#785318" stroke-width="1"/>
    ''')
    
    noren_xs = [100, 305, 510, 715, 920]
    panel_w = 180
    panel_h = 105

    for idx, nx in enumerate(noren_xs):
        cx = nx + panel_w / 2
        parts.append(f'''
        <rect x="{nx+25}" y="62" width="16" height="12" rx="2" fill="#14213d"/>
        <rect x="{nx+panel_w-41}" y="62" width="16" height="12" rx="2" fill="#14213d"/>
        
        <path d="M {nx},74 L {nx+panel_w},74 L {nx+panel_w},{74+panel_h} Q {cx},{74+panel_h-6} {nx},{74+panel_h} Z" fill="url(#norenIndigo)"/>
        <path d="M {nx},{74+panel_h-14} L {nx+panel_w},{74+panel_h-14} L {nx+panel_w},{74+panel_h-7} L {nx},{74+panel_h-7} Z" fill="#ffffff" opacity="0.95"/>
        
        <!-- Outer Crest Double Ring -->
        <circle cx="{cx}" cy="{74+45}" r="27" fill="none" stroke="#ffffff" stroke-width="2"/>
        <circle cx="{cx}" cy="{74+45}" r="23" fill="none" stroke="#ffffff" stroke-width="0.8" stroke-dasharray="4 2"/>
        ''')
        
        if idx == 0:
            # Panel 1: Steaming Ramen Bowl Emblem
            parts.append(f'''
            <ellipse cx="{cx}" cy="{74+48}" rx="14" ry="6" fill="#ffd166"/>
            <path d="M {cx-14},{74+48} C {cx-12},{74+60} {cx+12},{74+60} {cx+14},{74+48} Z" fill="#ffffff"/>
            <!-- Steam curls -->
            <path d="M {cx-6},{74+42} Q {cx-9},{74+34} {cx-6},{74+30}" stroke="#ffffff" stroke-width="1.8" fill="none" stroke-linecap="round"/>
            <path d="M {cx},{74+42} Q {cx+3},{74+34} {cx},{74+30}" stroke="#ffffff" stroke-width="1.8" fill="none" stroke-linecap="round"/>
            <path d="M {cx+6},{74+42} Q {cx+3},{74+34} {cx+6},{74+30}" stroke="#ffffff" stroke-width="1.8" fill="none" stroke-linecap="round"/>
            ''')
        elif idx == 1:
            # Panel 2: Traditional Triple Swirl / Tomoe Crest
            parts.append(f'''
            <g transform="translate({cx}, {74+45})">
              <circle cx="0" cy="0" r="14" fill="#ffffff"/>
              <circle cx="0" cy="0" r="11" fill="#1b2a4a"/>
              <!-- Swirl petals -->
              <circle cx="-3" cy="-3" r="4" fill="#ffd166"/>
              <circle cx="4" cy="-2" r="4" fill="#ffd166"/>
              <circle cx="-1" cy="4" r="4" fill="#ffd166"/>
            </g>
            ''')
        elif idx == 2:
            # Panel 3: Central Master Emblem - Golden Octopus Chef Mascot!
            parts.append(f'''
            <path d="M {cx-12},{74+44} C {cx-14},{74+32} {cx+14},{74+32} {cx+12},{74+44} C {cx+15},{74+52} {cx-15},{74+52} {cx-12},{74+44} Z" fill="#ffd166"/>
            <path d="M {cx-10},{74+48} Q {cx-14},{74+58} {cx-8},{74+58} Q {cx-4},{74+54} {cx},{74+58} Q {cx+4},{74+54} {cx+8},{74+58} Q {cx+14},{74+58} {cx+10},{74+48}" fill="none" stroke="#ffd166" stroke-width="2.5" stroke-linecap="round"/>
            <line x1="{cx-12}" y1="{74+38}" x2="{cx+12}" y2="{74+38}" stroke="#ffffff" stroke-width="2"/>
            <circle cx="{cx}" cy="{74+38}" r="1.5" fill="#e63946"/>
            <circle cx="{cx-4}" cy="{74+42}" r="1.8" fill="#1b1c1e"/>
            <circle cx="{cx+4}" cy="{74+42}" r="1.8" fill="#1b1c1e"/>
            ''')
        elif idx == 3:
            # Panel 4: Crossed Chopsticks with Golden Star / Wheat Motif
            parts.append(f'''
            <line x1="{cx-12}" y1="{74+35}" x2="{cx+12}" y2="{74+55}" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round"/>
            <line x1="{cx+12}" y1="{74+35}" x2="{cx-12}" y2="{74+55}" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round"/>
            <circle cx="{cx}" cy="{74+45}" r="5" fill="#ffd166"/>
            <circle cx="{cx}" cy="{74+45}" r="2" fill="#c92535"/>
            ''')
        elif idx == 4:
            # Panel 5: Traditional Japanese Paper Lantern & Flame Crest
            parts.append(f'''
            <rect x="{cx-9}" y="{74+35}" width="18" height="20" rx="4" fill="#ffd166" stroke="#ffffff" stroke-width="1.5"/>
            <line x1="{cx-7}" y1="{74+40}" x2="{cx+7}" y2="{74+40}" stroke="#c92535" stroke-width="1.2"/>
            <line x1="{cx-8}" y1="{74+45}" x2="{cx+8}" y2="{74+45}" stroke="#c92535" stroke-width="1.2"/>
            <line x1="{cx-7}" y1="{74+50}" x2="{cx+7}" y2="{74+50}" stroke="#c92535" stroke-width="1.2"/>
            <line x1="{cx}" y1="{74+31}" x2="{cx}" y2="{74+35}" stroke="#ffffff" stroke-width="1.5"/>
            <line x1="{cx}" y1="{74+55}" x2="{cx}" y2="{74+59}" stroke="#ffd166" stroke-width="2"/>
            ''')

    parts.append('</g><!-- end noren-curtains -->')

    # Glowing Paper Lanterns (Chochin)
    parts.append('''
    <!-- LANTERNS -->
    <!-- Left Red Lantern (Chochin) -->
    <g id="lantern-left">
      <circle cx="120" cy="220" r="140" fill="url(#lanternGlowRed)"/>
      <line x1="120" y1="75" x2="120" y2="150" stroke="#120803" stroke-width="3"/>
      
      <rect x="95" y="145" width="50" height="12" rx="3" fill="#1b1c1e" stroke="#000" stroke-width="1.5" filter="url(#dropShadow)"/>

      <path d="M 98,157 C 65,185 60,250 98,280 L 142,280 C 180,250 175,185 142,157 Z" fill="url(#lanternRedBody)" filter="url(#dropShadow)"/>
      
      <path d="M 85,180 Q 120,187 155,180" fill="none" stroke="#4a0000" stroke-width="1.8"/>
      <path d="M 75,205 Q 120,213 165,205" fill="none" stroke="#4a0000" stroke-width="1.8"/>
      <path d="M 72,230 Q 120,240 168,230" fill="none" stroke="#4a0000" stroke-width="2"/>
      <path d="M 78,255 Q 120,263 162,255" fill="none" stroke="#4a0000" stroke-width="1.8"/>

      <ellipse cx="120" cy="220" rx="32" ry="45" fill="#ff7566" opacity="0.5" filter="url(#softGlow)"/>

      <!-- Vector Japanese Calligraphy for "ラーメン" -->
      <!-- ラ -->
      <path d="M 110,187 L 130,187 M 112,193 L 126,193 C 126,201 123,205 112,207" stroke="#1a0003" stroke-width="3.5" fill="none" stroke-linecap="round"/>
      <!-- ー -->
      <line x1="120" y1="212" x2="120" y2="228" stroke="#1a0003" stroke-width="3.5" stroke-linecap="round"/>
      <!-- メ -->
      <path d="M 127,235 L 113,252 M 115,241 Q 124,244 127,253" stroke="#1a0003" stroke-width="3.5" fill="none" stroke-linecap="round"/>
      <!-- ン -->
      <circle cx="115" cy="262" r="2" fill="#1a0003"/>
      <path d="M 112,272 Q 118,277 127,262" stroke="#1a0003" stroke-width="3.5" fill="none" stroke-linecap="round"/>

      <rect x="98" y="280" width="44" height="10" rx="2" fill="#1b1c1e" stroke="#000" stroke-width="1.5"/>
      <line x1="120" y1="290" x2="120" y2="325" stroke="#d4af37" stroke-width="3" stroke-linecap="round"/>
      <ellipse cx="120" cy="325" rx="5" ry="8" fill="#ffd166"/>
    </g>

    <!-- Right Amber/Yellow Lantern (Chochin) -->
    <g id="lantern-right">
      <circle cx="1080" cy="220" r="140" fill="url(#lanternGlowAmber)"/>
      <line x1="1080" y1="75" x2="1080" y2="150" stroke="#120803" stroke-width="3"/>

      <rect x="1055" y="145" width="50" height="12" rx="3" fill="#1b1c1e" stroke="#000" stroke-width="1.5" filter="url(#dropShadow)"/>

      <path d="M 1058,157 C 1025,185 1020,250 1058,280 L 1102,280 C 1140,250 1135,185 1102,157 Z" fill="url(#lanternYellowBody)" filter="url(#dropShadow)"/>

      <path d="M 1045,180 Q 1080,187 1115,180" fill="none" stroke="#7a3e00" stroke-width="1.8"/>
      <path d="M 1035,205 Q 1080,213 1125,205" fill="none" stroke="#7a3e00" stroke-width="1.8"/>
      <path d="M 1032,230 Q 1080,240 1128,230" fill="none" stroke="#7a3e00" stroke-width="2"/>
      <path d="M 1038,255 Q 1080,263 1122,255" fill="none" stroke="#7a3e00" stroke-width="1.8"/>

      <ellipse cx="1080" cy="220" rx="32" ry="45" fill="#fff3b0" opacity="0.6" filter="url(#softGlow)"/>

      <!-- Vector Japanese Kanji for "蛸堂" (Tako-do) -->
      <!-- 蛸 -->
      <g stroke="#1b1000" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <!-- 虫 radical (left) -->
        <rect x="1066" y="196" width="9" height="7" rx="1"/>
        <line x1="1070" y1="192" x2="1070" y2="210"/>
        <line x1="1065" y1="210" x2="1074" y2="206"/>
        <circle cx="1073" cy="209" r="1" fill="#1b1000"/>
        <!-- 肖 (right) -->
        <path d="M 1083,193 Q 1087,196 1086,201 M 1093,193 Q 1089,196 1090,201"/>
        <line x1="1081" y1="202" x2="1094" y2="202"/>
        <rect x="1082" y="205" width="11" height="7" rx="1"/>
        <line x1="1082" y1="208" x2="1093" y2="208"/>
      </g>
      <!-- 堂 -->
      <g stroke="#1b1000" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <line x1="1080" y1="228" x2="1080" y2="235"/>
        <line x1="1072" y1="233" x2="1076" y2="236"/>
        <line x1="1088" y1="233" x2="1084" y2="236"/>
        <path d="M 1070,240 L 1090,240 L 1090,243"/>
        <rect x="1074" y="244" width="12" height="7" rx="1"/>
        <!-- 土 -->
        <line x1="1073" y1="258" x2="1087" y2="258"/>
        <line x1="1080" y1="253" x2="1080" y2="265"/>
        <line x1="1069" y1="265" x2="1091" y2="265" stroke-width="3"/>
      </g>

      <rect x="1058" y="280" width="44" height="10" rx="2" fill="#1b1c1e" stroke="#000" stroke-width="1.5"/>
      <line x1="1080" y1="290" x2="1080" y2="325" stroke="#d4af37" stroke-width="3" stroke-linecap="round"/>
      <ellipse cx="1080" cy="325" rx="5" ry="8" fill="#ffd166"/>
    </g>
    ''')

    # Close SVG
    parts.append('</svg>')
    
    return '\n'.join(parts)

def main():
    svg_content = build_svg()
    
    # Validate with ET
    ET.fromstring(svg_content)
    print("XML Validation passed!")

    out_dir = "output"
    os.makedirs(out_dir, exist_ok=True)
    out_svg_path = os.path.join(out_dir, "octopus_chef_ramen.svg")
    
    with open(out_svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"SVG generated successfully: {out_svg_path} ({len(svg_content)} bytes)")

if __name__ == "__main__":
    main()
