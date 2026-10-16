#!/usr/bin/env python3
"""
Generates an SVG of an Awkward 1980s Studio Family Portrait of Robots.
No text is included anywhere in the artwork.
Relationships and personalities are conveyed through pose, eye focus,
body language, and studio composition.
"""

import os


def create_svg():
    W, H = 1400, 1400
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')

    # ==========================================
    # DEFS: Gradients, Filters, Clips
    # ==========================================
    svg.append('''  <defs>
    <!-- Studio Backdrop Radial Glow -->
    <radialGradient id="bgGlow" cx="48%" cy="40%" r="68%" fx="44%" fy="34%">
      <stop offset="0%" stop-color="#3d7385"/>
      <stop offset="35%" stop-color="#234859"/>
      <stop offset="70%" stop-color="#132836"/>
      <stop offset="100%" stop-color="#08111a"/>
    </radialGradient>

    <!-- Warm Secondary Studio Fill Light -->
    <radialGradient id="warmMottle" cx="72%" cy="28%" r="48%">
      <stop offset="0%" stop-color="#8f5140" stop-opacity="0.34"/>
      <stop offset="50%" stop-color="#522b36" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#132836" stop-opacity="0"/>
    </radialGradient>

    <!-- Cool Cyan Mottle Patch -->
    <radialGradient id="cyanMottle" cx="24%" cy="52%" r="42%">
      <stop offset="0%" stop-color="#4ea8b8" stop-opacity="0.24"/>
      <stop offset="60%" stop-color="#225566" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="#08111a" stop-opacity="0"/>
    </radialGradient>

    <!-- Ghostly 1980s Double-Exposure Inset Mask -->
    <radialGradient id="insetFade" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.32"/>
      <stop offset="55%" stop-color="#ffffff" stop-opacity="0.22"/>
      <stop offset="82%" stop-color="#ffffff" stop-opacity="0.06"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>

    <!-- Vignette Overlay -->
    <radialGradient id="vignette" cx="50%" cy="50%" r="72%">
      <stop offset="56%" stop-color="#000000" stop-opacity="0"/>
      <stop offset="86%" stop-color="#04080e" stop-opacity="0.48"/>
      <stop offset="100%" stop-color="#020408" stop-opacity="0.85"/>
    </radialGradient>

    <!-- Velvet Stool Cushion Gradient -->
    <linearGradient id="velvetSeat" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#962739"/>
      <stop offset="45%" stop-color="#6b1624"/>
      <stop offset="100%" stop-color="#3d0912"/>
    </linearGradient>

    <!-- Studio Floor Carpet Gradient -->
    <linearGradient id="studioFloor" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e1724"/>
      <stop offset="35%" stop-color="#15101a"/>
      <stop offset="100%" stop-color="#08060a"/>
    </linearGradient>

    <!-- Dad: Vintage Beige/Olive Computer Steel -->
    <linearGradient id="dadBody" x1="10%" y1="5%" x2="88%" y2="95%">
      <stop offset="0%" stop-color="#e3dec8"/>
      <stop offset="45%" stop-color="#c4bc9f"/>
      <stop offset="80%" stop-color="#9b9275"/>
      <stop offset="100%" stop-color="#756d54"/>
    </linearGradient>
    <linearGradient id="dadDark" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#807860"/>
      <stop offset="100%" stop-color="#4e4938"/>
    </linearGradient>
    <linearGradient id="dadScreen" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#11291a"/>
      <stop offset="50%" stop-color="#0a1c11"/>
      <stop offset="100%" stop-color="#06120a"/>
    </linearGradient>
    <linearGradient id="plaidTie" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#c23b2b"/>
      <stop offset="50%" stop-color="#8f2418"/>
      <stop offset="100%" stop-color="#5e140c"/>
    </linearGradient>

    <!-- Mom: Retro-Futuristic Pearl Lavender & Rose Gold -->
    <linearGradient id="momBody" x1="15%" y1="5%" x2="85%" y2="95%">
      <stop offset="0%" stop-color="#fdf7ff"/>
      <stop offset="35%" stop-color="#eadcf2"/>
      <stop offset="75%" stop-color="#bfa8d1"/>
      <stop offset="100%" stop-color="#8b739e"/>
    </linearGradient>
    <linearGradient id="momRoseGold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f7d4c6"/>
      <stop offset="40%" stop-color="#d99b84"/>
      <stop offset="80%" stop-color="#a66953"/>
      <stop offset="100%" stop-color="#734232"/>
    </linearGradient>
    <linearGradient id="momVisor" x1="0%" y1="0%" x2="100%" y2="90%">
      <stop offset="0%" stop-color="#2b1238"/>
      <stop offset="50%" stop-color="#190824"/>
      <stop offset="100%" stop-color="#0e0314"/>
    </linearGradient>

    <!-- Teen: Matte Charcoal & Slate -->
    <linearGradient id="teenBody" x1="10%" y1="0%" x2="90%" y2="100%">
      <stop offset="0%" stop-color="#4e5566"/>
      <stop offset="45%" stop-color="#343845"/>
      <stop offset="85%" stop-color="#1f222b"/>
      <stop offset="100%" stop-color="#14161c"/>
    </linearGradient>
    <linearGradient id="teenHoodie" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2f333d"/>
      <stop offset="60%" stop-color="#1e2029"/>
      <stop offset="100%" stop-color="#111217"/>
    </linearGradient>
    <linearGradient id="teenScreen" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#210c18"/>
      <stop offset="100%" stop-color="#0d0309"/>
    </linearGradient>

    <!-- Kid: Bright Toy Yellow & Cherry Red -->
    <linearGradient id="kidYellow" x1="15%" y1="5%" x2="85%" y2="95%">
      <stop offset="0%" stop-color="#ffeb70"/>
      <stop offset="45%" stop-color="#f5bd1f"/>
      <stop offset="85%" stop-color="#c98806"/>
      <stop offset="100%" stop-color="#965f00"/>
    </linearGradient>
    <linearGradient id="kidRed" x1="10%" y1="10%" x2="90%" y2="90%">
      <stop offset="0%" stop-color="#ff6352"/>
      <stop offset="50%" stop-color="#d92b1c"/>
      <stop offset="100%" stop-color="#8c1309"/>
    </linearGradient>
    <linearGradient id="kidTeal" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#66f0f0"/>
      <stop offset="55%" stop-color="#1fa6b8"/>
      <stop offset="100%" stop-color="#0d6370"/>
    </linearGradient>
    <radialGradient id="glassDome" cx="35%" cy="30%" r="65%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.55"/>
      <stop offset="30%" stop-color="#b5f5ff" stop-opacity="0.22"/>
      <stop offset="75%" stop-color="#3da1b8" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#125163" stop-opacity="0.48"/>
    </radialGradient>

    <!-- Grandpa: Tarnished Brass & Copper -->
    <linearGradient id="brassBody" x1="0%" y1="0%" x2="100%" y2="90%">
      <stop offset="0%" stop-color="#e8c37e"/>
      <stop offset="35%" stop-color="#b8883b"/>
      <stop offset="70%" stop-color="#875c1d"/>
      <stop offset="100%" stop-color="#54360c"/>
    </linearGradient>
    <linearGradient id="copperDark" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#bf704d"/>
      <stop offset="50%" stop-color="#824023"/>
      <stop offset="100%" stop-color="#4d210e"/>
    </linearGradient>
    <radialGradient id="furnaceGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#fff3a1"/>
      <stop offset="35%" stop-color="#ff9d2e"/>
      <stop offset="70%" stop-color="#d93800"/>
      <stop offset="100%" stop-color="#4a0900"/>
    </radialGradient>

    <!-- Pet: Chrome & Teal Vacuum Dog -->
    <linearGradient id="chromeMetal" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="25%" stop-color="#cfd8e3"/>
      <stop offset="50%" stop-color="#7c8b9e"/>
      <stop offset="75%" stop-color="#e1e8f0"/>
      <stop offset="100%" stop-color="#536070"/>
    </linearGradient>

    <!-- Glow & Drop Shadow Filters -->
    <filter id="dropShadow" x="-15%" y="-15%" width="135%" height="135%">
      <feDropShadow dx="6" dy="12" stdDeviation="8" flood-color="#04080e" flood-opacity="0.58"/>
    </filter>
    <filter id="neonGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="4.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="softBlur" x="-25%" y="-25%" width="150%" height="150%">
      <feGaussianBlur stdDeviation="24"/>
    </filter>

    <clipPath id="canvasClip">
      <rect x="0" y="0" width="1400" height="1400"/>
    </clipPath>
  </defs>''')

    svg.append('  <g clip-path="url(#canvasClip)">')

    # ==========================================
    # 1. STUDIO BACKDROP & OLAN MILLS LASERS
    # ==========================================
    svg.append(f'    <rect x="0" y="0" width="{W}" height="{H}" fill="url(#bgGlow)"/>')
    svg.append(f'    <rect x="0" y="0" width="{W}" height="{H}" fill="url(#warmMottle)"/>')
    svg.append(f'    <rect x="0" y="0" width="{W}" height="{H}" fill="url(#cyanMottle)"/>')

    # Soft studio mottled clouds
    clouds = [
        (360, 260, 250, 170, "#4f8fa3", 0.15),
        (960, 220, 280, 200, "#8c5347", 0.16),
        (700, 460, 340, 230, "#3d7a8f", 0.12),
        (240, 660, 260, 190, "#2b586e", 0.18),
        (1140, 600, 270, 210, "#633948", 0.15),
    ]
    svg.append('    <g filter="url(#softBlur)">')
    for cx, cy, rx, ry, col, op in clouds:
        svg.append(f'      <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{col}" opacity="{op}"/>')
    svg.append('    </g>')

    # Cheesy 1980s Studio Laser Grid Backdrop Lines
    svg.append('    <g opacity="0.28" filter="url(#neonGlow)">')
    for i in range(7):
        y2 = 55 + i * 75
        svg.append(f'      <line x1="-20" y1="{420 - i*15}" x2="1420" y2="{y2}" stroke="#ff38a8" stroke-width="{2.2 - i*0.2}" stroke-dasharray="18 8 6 8"/>')
    for i in range(6):
        y1 = 85 + i * 65
        svg.append(f'      <line x1="1420" y1="{y1}" x2="-20" y2="{540 + i*35}" stroke="#2ce8f5" stroke-width="{1.8 - i*0.15}"/>')
    svg.append('      <polygon points="185,140 225,105 240,158" fill="none" stroke="#ff42b3" stroke-width="2.5" opacity="0.55"/>')
    svg.append('      <polygon points="820,95 865,65 850,122" fill="none" stroke="#33f2ff" stroke-width="2.5" opacity="0.55"/>')
    svg.append('      <polygon points="560,80 595,55 610,98" fill="none" stroke="#ffdb4d" stroke-width="2" opacity="0.45"/>')
    svg.append('    </g>')

    # ==========================================
    # 1B. CLASSIC 1980s FLOATING GHOSTLY DOUBLE-EXPOSURE INSET (Top Right Corner!)
    # A quintessential awkward 80s Olan Mills portrait trope: a soft-focus floating
    # side-profile double-exposure of Dad Robot gazing pensively into the distance!
    # ==========================================
    svg.append('''    <g id="ghostly-dad-inset" transform="translate(1150, 215)" opacity="0.28">
      <!-- Soft glowing halo behind floating inset -->
      <ellipse cx="0" cy="0" rx="145" ry="130" fill="#4ea8b8" opacity="0.25" filter="url(#softBlur)"/>
      <g transform="rotate(-5) scale(0.92)">
        <!-- Bent Rabbit-Ear Antennas -->
        <line x1="-15" y1="-98" x2="-62" y2="-168" stroke="#9ba3ab" stroke-width="5" stroke-linecap="round"/>
        <circle cx="-62" cy="-168" r="7" fill="#d94e28"/>
        <polyline points="20,-98 48,-142 12,-165" fill="none" stroke="#9ba3ab" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="12" cy="-165" r="7" fill="#d94e28"/>
        <!-- 3/4 Profile CRT Monitor Casing facing left-upward -->
        <rect x="-95" y="-95" width="190" height="168" rx="18" fill="url(#dadBody)" stroke="#3b3628" stroke-width="4"/>
        <rect x="-85" y="-76" width="135" height="128" rx="14" fill="url(#dadScreen)" stroke="#26231a" stroke-width="3.5"/>
        <!-- Side Cooling Vents on CRT Depth -->
        <line x1="62" y1="-60" x2="82" y2="-60" stroke="#4f4937" stroke-width="4" stroke-linecap="round"/>
        <line x1="62" y1="-42" x2="82" y2="-42" stroke="#4f4937" stroke-width="4" stroke-linecap="round"/>
        <line x1="62" y1="-24" x2="82" y2="-24" stroke="#4f4937" stroke-width="4" stroke-linecap="round"/>
        <!-- Taped Dad Glasses in 3/4 view -->
        <rect x="-82" y="-48" width="58" height="44" rx="6" fill="none" stroke="#1c1b18" stroke-width="7"/>
        <rect x="-12" y="-48" width="54" height="44" rx="6" fill="none" stroke="#1c1b18" stroke-width="7"/>
        <line x1="-24" y1="-30" x2="-12" y2="-30" stroke="#1c1b18" stroke-width="7"/>
        <rect x="-23" y="-37" width="11" height="14" rx="2" transform="rotate(8)" fill="#f2efe4"/>
        <!-- Pensive Glowing Green Eyes & Stiff Mustache/Grimace -->
        <g filter="url(#neonGlow)">
          <circle cx="-55" cy="-26" r="14" fill="none" stroke="#3dff74" stroke-width="3.5"/>
          <circle cx="-58" cy="-28" r="5" fill="#3dff74"/>
          <circle cx="14" cy="-26" r="13" fill="none" stroke="#3dff74" stroke-width="3.5"/>
          <circle cx="11" cy="-28" r="4.5" fill="#3dff74"/>
          <rect x="-58" y="12" width="84" height="20" rx="5" fill="#091f10" stroke="#3dff74" stroke-width="3"/>
          <line x1="-58" y1="22" x2="26" y2="22" stroke="#3dff74" stroke-width="2.5"/>
          <line x1="-30" y1="12" x2="-30" y2="32" stroke="#3dff74" stroke-width="2.5"/>
          <line x1="-2" y1="12" x2="-2" y2="32" stroke="#3dff74" stroke-width="2.5"/>
        </g>
      </g>
      <!-- Soft vignette ring blending inset into backdrop -->
      <ellipse cx="0" cy="0" rx="145" ry="130" fill="none" stroke="#162e3d" stroke-width="42" filter="url(#softBlur)"/>
    </g>''')

    # ==========================================
    # 2. STUDIO FLOOR & POSING STOOLS
    # ==========================================
    svg.append('    <path d="M -20 960 Q 700 925 1420 965 L 1420 1420 L -20 1420 Z" fill="url(#studioFloor)"/>')
    svg.append('    <path d="M -20 960 Q 700 925 1420 965" fill="none" stroke="#2f253b" stroke-width="4" opacity="0.75"/>')

    # Main Group Shift: Center the 5-robot + 1-dog pyramid nicely inside 1400x1400
    # Shift X by +90, Y by -55 so all feet, shoes, dog paws, and cables have generous breathing room!
    svg.append('    <g id="portrait-subjects" transform="translate(90, -55)">')

    # Floor shadows under characters
    floor_shadows = [
        (230, 1215, 155, 36),   # Teen
        (465, 1230, 195, 44),   # Dad
        (735, 1230, 180, 42),   # Mom
        (985, 1240, 165, 42),   # Grandpa
        (595, 1295, 185, 44),   # Kid
        (895, 1320, 160, 36),   # Pet Dog
    ]
    for cx, cy, rx, ry in floor_shadows:
        svg.append(f'      <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#040307" opacity="0.72" filter="url(#softBlur)"/>')

    # Studio posing stool under Grandpa (right)
    svg.append('''      <g id="grandpa-stool">
        <path d="M 905 1110 L 880 1240 M 1065 1110 L 1090 1240 M 985 1115 L 985 1250" stroke="#5b6675" stroke-width="10" stroke-linecap="round"/>
        <ellipse cx="985" cy="1190" rx="88" ry="16" fill="none" stroke="#454e59" stroke-width="6"/>
        <path d="M 880 1075 C 880 1055, 1090 1055, 1090 1075 L 1085 1112 C 1085 1130, 885 1130, 885 1112 Z" fill="url(#velvetSeat)" stroke="#2b060d" stroke-width="3"/>
        <ellipse cx="985" cy="1075" rx="105" ry="22" fill="#9c2b3f" stroke="#4a0d17" stroke-width="2"/>
      </g>''')

    # Studio posing bench under Dad & Mom (center)
    svg.append('''      <g id="center-bench">
        <rect x="375" y="1095" width="460" height="120" rx="10" fill="#231924" stroke="#120c13" stroke-width="3"/>
        <rect x="368" y="1080" width="474" height="32" rx="12" fill="url(#velvetSeat)" stroke="#380912" stroke-width="2.5"/>
      </g>''')

    # ==========================================
    # 3. TEENAGER ROBOT (Back Left - Slouching, Angsty, Rolling Eyes)
    # ==========================================
    svg.append('''      <g id="teen-robot" filter="url(#dropShadow)">
        <!-- Long gangly legs in awkward pigeon-toed stance -->
        <!-- Left Leg -->
        <path d="M 185 820 L 165 1010 L 180 1175" fill="none" stroke="#1e222b" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M 185 820 L 165 1010 L 180 1175" fill="none" stroke="#394052" stroke-width="12" stroke-dasharray="14 10" stroke-linecap="round"/>
        <circle cx="165" cy="1010" r="18" fill="url(#teenBody)" stroke="#12141a" stroke-width="3"/>
        <!-- Right Leg -->
        <path d="M 275 815 L 288 1005 L 265 1175" fill="none" stroke="#1e222b" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M 275 815 L 288 1005 L 265 1175" fill="none" stroke="#394052" stroke-width="12" stroke-dasharray="14 10" stroke-linecap="round"/>
        <circle cx="288" cy="1005" r="18" fill="url(#teenBody)" stroke="#12141a" stroke-width="3"/>

        <!-- Chunky Scuffed Sneaker Boots (Pigeon-toed inward) -->
        <g transform="translate(180, 1170) rotate(8)">
          <path d="M -32 -15 L 38 -15 C 52 -15, 62 12, 58 26 L -38 26 C -42 12, -38 -15, -32 -15 Z" fill="#252830" stroke="#101217" stroke-width="3"/>
          <rect x="-40" y="16" width="100" height="12" rx="5" fill="#d9d4c5" stroke="#101217" stroke-width="2.5"/>
          <path d="M -10 -15 L 15 -5 M -12 -3 L 15 5" stroke="#ff2a85" stroke-width="3" stroke-linecap="round"/>
        </g>
        <g transform="translate(265, 1170) rotate(-12)">
          <path d="M -38 -15 L 32 -15 C 38 -15, 42 12, 38 26 L -58 26 C -62 12, -52 -15, -38 -15 Z" fill="#252830" stroke="#101217" stroke-width="3"/>
          <rect x="-60" y="16" width="100" height="12" rx="5" fill="#d9d4c5" stroke="#101217" stroke-width="2.5"/>
          <path d="M -15 -5 L 10 -15 M -15 5 L 12 -3" stroke="#ff2a85" stroke-width="3" stroke-linecap="round"/>
        </g>

        <!-- Slouched Torso & Dark Hoodie Vest -->
        <g transform="translate(225, 640) rotate(-9)">
          <!-- Spine / Pelvis connector -->
          <rect x="-45" y="135" width="90" height="45" rx="12" fill="#1b1d24" stroke="#0f1014" stroke-width="3"/>
          <!-- Main Chassis -->
          <path d="M -82 -125 L 78 -115 L 65 145 L -68 145 Z" fill="url(#teenBody)" stroke="#101217" stroke-width="3.5" stroke-linejoin="round"/>
          <!-- Hoodie Cloth Overlay -->
          <path d="M -88 -120 C -95 -20, -82 80, -74 150 L -22 150 L -15 -95 Z" fill="url(#teenHoodie)" stroke="#0e1014" stroke-width="3"/>
          <path d="M 84 -110 C 90 -15, 78 80, 70 150 L 18 150 L 15 -90 Z" fill="url(#teenHoodie)" stroke="#0e1014" stroke-width="3"/>
          <!-- Exposed Chest Cassette Deck & Equalizer Bars -->
          <rect x="-32" y="-55" width="64" height="48" rx="6" fill="#14171f" stroke="#4f5669" stroke-width="2"/>
          <circle cx="-14" cy="-31" r="9" fill="#2b303d" stroke="#ff2a85" stroke-width="2"/>
          <circle cx="14" cy="-31" r="9" fill="#2b303d" stroke="#2ce8f5" stroke-width="2"/>
          <!-- Decorative Band/Skater Stickers (purely geometric, no text) -->
          <polygon points="-58,-45 -38,-62 -43,-32 -25,-42 -48,-18" fill="#ffd92e" stroke="#111" stroke-width="1.5"/>
          <circle cx="48" cy="-35" r="14" fill="#ff2a85" stroke="#111" stroke-width="2"/>
          <path d="M 41 -40 L 45 -36 M 45 -40 L 41 -36 M 51 -40 L 55 -36 M 55 -40 L 51 -36" stroke="#111" stroke-width="2"/>
          <path d="M 41 -29 Q 48 -34 55 -29" fill="none" stroke="#111" stroke-width="2"/>
          <polygon points="36,25 58,18 52,44" fill="#33f2ff" stroke="#111" stroke-width="1.5"/>
          <!-- Hoodie Pocket & Drawstrings -->
          <path d="M -62 55 L -42 135 L 42 135 L 58 55 Z" fill="#181a21" stroke="#0d0e12" stroke-width="2.5"/>
          <path d="M -18 -95 Q -24 -25 -20 15" fill="none" stroke="#d9d4c5" stroke-width="3.5" stroke-linecap="round"/>
          <path d="M 16 -90 Q 22 -20 14 22" fill="none" stroke="#d9d4c5" stroke-width="3.5" stroke-linecap="round"/>

          <!-- Left Arm (Slouched down into hoodie pocket) -->
          <path d="M -85 -100 C -130 -30, -125 55, -52 95" fill="none" stroke="#1b1e26" stroke-width="26" stroke-linecap="round"/>
          <path d="M -85 -100 C -130 -30, -125 55, -52 95" fill="none" stroke="#3c4254" stroke-width="12" stroke-dasharray="10 8" stroke-linecap="round"/>

          <!-- Right Arm (Bent holding retro handheld console, ignoring camera) -->
          <path d="M 80 -95 C 122 -35, 118 45, 42 52" fill="none" stroke="#1b1e26" stroke-width="26" stroke-linecap="round"/>
          <path d="M 80 -95 C 122 -35, 118 45, 42 52" fill="none" stroke="#3c4254" stroke-width="12" stroke-dasharray="10 8" stroke-linecap="round"/>

          <!-- Handheld Game Console & Mechanical Claws -->
          <g transform="translate(18, 42) rotate(18)">
            <rect x="-28" y="-36" width="56" height="68" rx="8" fill="#8f8b9e" stroke="#111" stroke-width="3"/>
            <rect x="-20" y="-28" width="40" height="32" rx="4" fill="#46612b" stroke="#1e2912" stroke-width="2"/>
            <!-- Handheld screen glow -->
            <circle cx="-8" cy="16" r="6" fill="#d92445"/>
            <circle cx="10" cy="12" r="5" fill="#d92445"/>
            <path d="M 22 -12 L 36 -4 L 22 8" fill="none" stroke="#5e6578" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
          </g>

          <!-- Coiled Neck & Tilted Head -->
          <path d="M -18 -120 L -24 -165 L 14 -162 L 18 -118 Z" fill="#252933" stroke="#101217" stroke-width="3"/>
          <line x1="-22" y1="-150" x2="16" y2="-148" stroke="#576075" stroke-width="4"/>
          <line x1="-20" y1="-136" x2="17" y2="-134" stroke="#576075" stroke-width="4"/>

          <!-- Head Unit (Tilted away, rolling eyes up-left) -->
          <g transform="translate(-8, -230) rotate(-11)">
            <!-- Bulky Stereo Headphones -->
            <path d="M -88 10 C -95 -85, 95 -85, 88 10" fill="none" stroke="#22252e" stroke-width="16" stroke-linecap="round"/>
            <path d="M -84 5 C -90 -78, 90 -78, 84 5" fill="none" stroke="#ff2a85" stroke-width="4" stroke-linecap="round"/>
            <!-- Headphone Cord dangling -->
            <path d="M -88 32 C -115 95, -75 140, -35 195" fill="none" stroke="#ff2a85" stroke-width="3.5"/>

            <!-- Main Head Box -->
            <rect x="-75" y="-52" width="150" height="106" rx="22" fill="url(#teenBody)" stroke="#0f1117" stroke-width="4"/>
            <!-- Ear Cups -->
            <rect x="-96" y="-22" width="26" height="58" rx="12" fill="#191b22" stroke="#ff2a85" stroke-width="3"/>
            <rect x="70" y="-22" width="26" height="58" rx="12" fill="#191b22" stroke="#ff2a85" stroke-width="3"/>

            <!-- Dark Glass Visor -->
            <rect x="-60" y="-36" width="120" height="74" rx="14" fill="url(#teenScreen)" stroke="#2d3240" stroke-width="3"/>

            <!-- LED Eyes Rolling Hard Up-Left in peak teen exasperation -->
            <g filter="url(#neonGlow)">
              <!-- Left Eye -->
              <ellipse cx="-26" cy="-6" rx="18" ry="16" fill="#290917" stroke="#ff2e93" stroke-width="2.5"/>
              <circle cx="-33" cy="-14" r="7.5" fill="#ff47a3"/>
              <circle cx="-35" cy="-16" r="2.5" fill="#ffffff"/>
              <!-- Heavy unimpressed eyelid cutting across middle -->
              <path d="M -46 -4 L -6 -10" stroke="#ff2e93" stroke-width="4" stroke-linecap="round"/>

              <!-- Right Eye -->
              <ellipse cx="26" cy="-6" rx="18" ry="16" fill="#290917" stroke="#ff2e93" stroke-width="2.5"/>
              <circle cx="19" cy="-14" r="7.5" fill="#ff47a3"/>
              <circle cx="17" cy="-16" r="2.5" fill="#ffffff"/>
              <!-- Heavy unimpressed eyelid -->
              <path d="M 6 -4 L 46 -10" stroke="#ff2e93" stroke-width="4" stroke-linecap="round"/>

              <!-- Flat wavy annoyed mouth line -->
              <path d="M -22 22 C -8 16, 8 26, 24 18" fill="none" stroke="#ff2e93" stroke-width="3.5" stroke-linecap="round"/>
            </g>
            <!-- Glass screen glare -->
            <path d="M -52 -30 L -25 -30 L -45 -5 L -52 -5 Z" fill="#ffffff" opacity="0.1"/>
          </g>
        </g>
      </g>''')

    # ==========================================
    # 4. GRANDPA ROBOT (Seated Right - Brass/Steampunk, Asleep, Tilted)
    # ==========================================
    svg.append('''      <g id="grandpa-robot" filter="url(#dropShadow)">
        <!-- Short Copper Accordion Legs resting on stool -->
        <!-- Left Leg -->
        <path d="M 935 1030 C 915 1090, 915 1145, 925 1195" fill="none" stroke="#472814" stroke-width="28" stroke-linecap="round"/>
        <path d="M 935 1030 C 915 1090, 915 1145, 925 1195" fill="none" stroke="#b87e3b" stroke-width="16" stroke-dasharray="9 9" stroke-linecap="round"/>
        <!-- Right Leg -->
        <path d="M 1025 1030 C 1045 1090, 1045 1145, 1038 1195" fill="none" stroke="#472814" stroke-width="28" stroke-linecap="round"/>
        <path d="M 1025 1030 C 1045 1090, 1045 1145, 1038 1195" fill="none" stroke="#b87e3b" stroke-width="16" stroke-dasharray="9 9" stroke-linecap="round"/>

        <!-- Heavy Riveted Iron Diving-Boot Feet -->
        <g transform="translate(915, 1205) rotate(6)">
          <path d="M -38 -15 L 28 -15 C 40 -15, 45 15, 40 25 L -44 25 Z" fill="url(#copperDark)" stroke="#2e1307" stroke-width="3"/>
          <rect x="-46" y="16" width="88" height="12" rx="4" fill="#3b2313" stroke="#1f1108" stroke-width="2.5"/>
          <circle cx="-18" cy="2" r="3.5" fill="#e3bd78"/>
          <circle cx="4" cy="2" r="3.5" fill="#e3bd78"/>
          <circle cx="24" cy="2" r="3.5" fill="#e3bd78"/>
        </g>
        <g transform="translate(1042, 1205) rotate(-5)">
          <path d="M -28 -15 L 38 -15 C 44 15, 40 25, 44 25 L -40 25 C -45 15, -40 -15, -28 -15 Z" fill="url(#copperDark)" stroke="#2e1307" stroke-width="3"/>
          <rect x="-42" y="16" width="88" height="12" rx="4" fill="#3b2313" stroke="#1f1108" stroke-width="2.5"/>
          <circle cx="-20" cy="2" r="3.5" fill="#e3bd78"/>
          <circle cx="0" cy="2" r="3.5" fill="#e3bd78"/>
          <circle cx="20" cy="2" r="3.5" fill="#e3bd78"/>
        </g>

        <!-- Barrel Boiler Torso (Leaning slightly right, slumped in nap) -->
        <g transform="translate(985, 865) rotate(6)">
          <!-- Exhaust Smokestack Pipe on Back Shoulder -->
          <path d="M 55 -185 L 72 -265 L 98 -265 L 85 -175 Z" fill="url(#copperDark)" stroke="#2b1206" stroke-width="3"/>
          <ellipse cx="85" cy="-265" rx="16" ry="6" fill="#2b1206" stroke="#b87e3b" stroke-width="2"/>
          <!-- Sleepy Steam Puffs rising from smokestack -->
          <circle cx="95" cy="-295" r="14" fill="#d9e4ec" opacity="0.35" filter="url(#neonGlow)"/>
          <circle cx="112" cy="-328" r="22" fill="#d9e4ec" opacity="0.25" filter="url(#neonGlow)"/>
          <circle cx="135" cy="-368" r="30" fill="#d9e4ec" opacity="0.15" filter="url(#neonGlow)"/>

          <!-- Main Cylindrical Boiler Body -->
          <rect x="-102" y="-165" width="204" height="310" rx="78" fill="url(#brassBody)" stroke="#362005" stroke-width="4"/>
          <!-- Oxidized Verdigris Patina Patches -->
          <path d="M -92 -60 Q -65 -45 -75 -15 Q -95 10 -98 -35 Z" fill="#4ca68a" opacity="0.42"/>
          <path d="M 65 45 Q 95 55 88 95 Q 60 110 55 75 Z" fill="#4ca68a" opacity="0.42"/>
          <path d="M -55 -152 Q -15 -135 15 -158 Z" fill="#4ca68a" opacity="0.35"/>

          <!-- Horizontal Brass Boiler Bands & Rivets -->
          <path d="M -101 -75 Q 0 -55 101 -75" fill="none" stroke="#47280a" stroke-width="10"/>
          <path d="M -101 -75 Q 0 -55 101 -75" fill="none" stroke="#ffd885" stroke-width="3" stroke-dasharray="4 18" stroke-linecap="round"/>
          <path d="M -101 55 Q 0 75 101 55" fill="none" stroke="#47280a" stroke-width="10"/>
          <path d="M -101 55 Q 0 75 101 55" fill="none" stroke="#ffd885" stroke-width="3" stroke-dasharray="4 18" stroke-linecap="round"/>

          <!-- Belly Furnace Grate (Warm sleepy ember glow) -->
          <circle cx="-6" cy="-5" r="52" fill="url(#copperDark)" stroke="#2e1406" stroke-width="4"/>
          <circle cx="-6" cy="-5" r="38" fill="url(#furnaceGlow)"/>
          <!-- Iron Grate Bars over furnace -->
          <line x1="-32" y1="-32" x2="-32" y2="22" stroke="#2e1406" stroke-width="5"/>
          <line x1="-15" y1="-41" x2="-15" y2="31" stroke="#2e1406" stroke-width="5"/>
          <line x1="3" y1="-41" x2="3" y2="31" stroke="#2e1406" stroke-width="5"/>
          <line x1="20" y1="-32" x2="20" y2="22" stroke="#2e1406" stroke-width="5"/>

          <!-- Vintage Pressure Gauge on Upper Chest (Purely graphical dial, no numbers) -->
          <circle cx="-38" cy="-115" r="24" fill="#f5ecd7" stroke="#3b2309" stroke-width="4"/>
          <path d="M -52 -110 A 16 16 0 0 1 -24 -110" fill="none" stroke="#c93b1e" stroke-width="4"/>
          <line x1="-38" y1="-115" x2="-48" y2="-122" stroke="#1a1105" stroke-width="3" stroke-linecap="round"/>
          <circle cx="-38" cy="-115" r="4" fill="#3b2309"/>

          <!-- Exposed Brass Cogs on Right Chest -->
          <circle cx="38" cy="-112" r="20" fill="#d9a84e" stroke="#3b2309" stroke-width="3" stroke-dasharray="7 5"/>
          <circle cx="38" cy="-112" r="8" fill="#47280a"/>
          <circle cx="62" cy="-94" r="14" fill="#b87333" stroke="#3b2309" stroke-width="2.5" stroke-dasharray="5 4"/>

          <!-- Huge Brass Ear Trumpet (Hearing Aid) extending from Left Side of Head -->
          <g transform="translate(-85, -245) rotate(-18)">
            <path d="M 18 0 C -15 -5, -45 -25, -75 -55 L -92 -10 C -55 -5, -20 10, 18 14 Z" fill="url(#brassBody)" stroke="#382005" stroke-width="3"/>
            <ellipse cx="-84" cy="-32" rx="12" ry="26" transform="rotate(20 -84 -32)" fill="#291504" stroke="#e3bd78" stroke-width="3"/>
          </g>

          <!-- Lantern-Style Head (Drooped forward & right, fast asleep) -->
          <g transform="translate(-4, -225) rotate(14)">
            <!-- Dome Top & Finial -->
            <path d="M -68 -35 C -68 -95, 68 -95, 68 -35 Z" fill="url(#copperDark)" stroke="#2e1307" stroke-width="3.5"/>
            <circle cx="0" cy="-86" r="12" fill="url(#brassBody)" stroke="#2e1307" stroke-width="3"/>
            <!-- Main Head Cylinder -->
            <rect x="-64" y="-38" width="128" height="86" rx="16" fill="url(#brassBody)" stroke="#362005" stroke-width="4"/>

            <!-- Thick Handlebar Mustache Plate & Whisker Bolts -->
            <path d="M -78 24 C -55 4, -18 18, 0 8 C 18 18, 55 4, 78 24 C 58 44, 22 36, 0 24 C -22 36, -58 44, -78 24 Z" fill="url(#copperDark)" stroke="#261005" stroke-width="3"/>
            <circle cx="-55" cy="24" r="3" fill="#ffd885"/>
            <circle cx="55" cy="24" r="3" fill="#ffd885"/>

            <!-- Left Eye (Closed sleepy shutter) -->
            <circle cx="-28" cy="-8" r="20" fill="#2b1806" stroke="#e3bd78" stroke-width="4"/>
            <path d="M -46 -8 Q -28 8 -10 -8" fill="none" stroke="#e3bd78" stroke-width="4" stroke-linecap="round"/>

            <!-- Right Eye (Cracked glass monocle & closed shutter) -->
            <circle cx="28" cy="-8" r="24" fill="#75c8d6" fill-opacity="0.28" stroke="#ffd885" stroke-width="5"/>
            <path d="M 10 -8 Q 28 8 46 -8" fill="none" stroke="#e3bd78" stroke-width="4" stroke-linecap="round"/>
            <!-- Monocle crack lines -->
            <path d="M 22 -24 L 30 -8 L 42 -12 M 30 -8 L 26 8" fill="none" stroke="#ffffff" stroke-width="2" opacity="0.75"/>
            <!-- Monocle Chain dangling down -->
            <path d="M 52 -4 Q 72 45 45 95" fill="none" stroke="#ffd885" stroke-width="2.5" stroke-dasharray="4 4"/>
          </g>

          <!-- Both Hands Clasped Over Walking Cane in Front -->
          <path d="M -98 -110 C -135 -35, -95 45, -22 52" fill="none" stroke="#472814" stroke-width="26" stroke-linecap="round"/>
          <path d="M -98 -110 C -135 -35, -95 45, -22 52" fill="none" stroke="#b87e3b" stroke-width="14" stroke-dasharray="9 8" stroke-linecap="round"/>
          <path d="M 96 -110 C 132 -35, 88 45, 8 52" fill="none" stroke="#472814" stroke-width="26" stroke-linecap="round"/>
          <path d="M 96 -110 C 132 -35, 88 45, 8 52" fill="none" stroke="#b87e3b" stroke-width="14" stroke-dasharray="9 8" stroke-linecap="round"/>

          <!-- Walking Cane (Copper Pipe with Brass Valve Handle) -->
          <g transform="translate(-8, 45) rotate(-6)">
            <line x1="0" y1="0" x2="-12" y2="335" stroke="#8c4422" stroke-width="14" stroke-linecap="round"/>
            <line x1="-2" y1="0" x2="-14" y2="335" stroke="#d98b5f" stroke-width="4" stroke-linecap="round"/>
            <!-- Rubber cane tip -->
            <rect x="-22" y="320" width="20" height="22" rx="5" fill="#1c1a17"/>
            <!-- Brass T-handle & clasped copper mittens -->
            <rect x="-34" y="-12" width="68" height="18" rx="8" fill="url(#brassBody)" stroke="#2e1406" stroke-width="3"/>
            <circle cx="-14" cy="2" r="18" fill="url(#copperDark)" stroke="#2e1406" stroke-width="3"/>
            <circle cx="14" cy="4" r="18" fill="url(#copperDark)" stroke="#2e1406" stroke-width="3"/>
          </g>
        </g>
      </g>''')

    # ==========================================
    # 5. DAD ROBOT (Center-Left - Boxy 80s Mainframe, Stiff, Sweating, Clip-on Tie)
    # ==========================================
    svg.append('''      <g id="dad-robot" filter="url(#dropShadow)">
        <!-- Stiff Boxy Legs planted wide apart -->
        <!-- Left Leg -->
        <path d="M 405 920 L 395 1075 L 395 1195" fill="none" stroke="#595340" stroke-width="38" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M 405 920 L 395 1075 L 395 1195" fill="none" stroke="#9e9578" stroke-width="22" stroke-dasharray="16 10" stroke-linecap="round"/>
        <rect x="372" y="1055" width="46" height="32" rx="6" fill="url(#dadBody)" stroke="#3d3829" stroke-width="3"/>
        <!-- Right Leg -->
        <path d="M 525 920 L 535 1075 L 535 1195" fill="none" stroke="#595340" stroke-width="38" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M 525 920 L 535 1075 L 535 1195" fill="none" stroke="#9e9578" stroke-width="22" stroke-dasharray="16 10" stroke-linecap="round"/>
        <rect x="512" y="1055" width="46" height="32" rx="6" fill="url(#dadBody)" stroke="#3d3829" stroke-width="3"/>

        <!-- Orthogonal Brown Loafers / Boxy Shoes -->
        <g transform="translate(390, 1200)">
          <path d="M -42 -18 L 35 -18 L 42 22 L -52 22 Z" fill="#4a3525" stroke="#24180e" stroke-width="3.5" stroke-linejoin="round"/>
          <rect x="-54" y="14" width="98" height="10" rx="3" fill="#261b12"/>
          <rect x="-22" y="-8" width="38" height="8" rx="2" fill="#8c6d46"/>
        </g>
        <g transform="translate(540, 1200)">
          <path d="M -35 -18 L 42 -18 L 52 22 L -42 22 Z" fill="#4a3525" stroke="#24180e" stroke-width="3.5" stroke-linejoin="round"/>
          <rect x="-44" y="14" width="98" height="10" rx="3" fill="#261b12"/>
          <rect x="-16" y="-8" width="38" height="8" rx="2" fill="#8c6d46"/>
        </g>

        <!-- Rigid Rectangular Mainframe Torso -->
        <g transform="translate(465, 755) rotate(-1.5)">
          <!-- Pelvis Unit -->
          <rect x="-105" y="125" width="210" height="58" rx="10" fill="url(#dadDark)" stroke="#363225" stroke-width="3.5"/>
          <line x1="-65" y1="125" x2="-65" y2="183" stroke="#363225" stroke-width="3"/>
          <line x1="65" y1="125" x2="65" y2="183" stroke="#363225" stroke-width="3"/>

          <!-- Main Chest Tower -->
          <rect x="-122" y="-165" width="244" height="300" rx="14" fill="url(#dadBody)" stroke="#3b3628" stroke-width="4"/>
          <!-- Recessed Panel Bevel -->
          <rect x="-106" y="-148" width="212" height="266" rx="8" fill="none" stroke="#8a8268" stroke-width="2.5"/>

          <!-- Left Chest Cooling Louvers -->
          <g stroke="#4f4937" stroke-width="5" stroke-linecap="round">
            <line x1="-92" y1="-120" x2="-42" y2="-120"/>
            <line x1="-92" y1="-104" x2="-42" y2="-104"/>
            <line x1="-92" y1="-88" x2="-42" y2="-88"/>
            <line x1="-92" y1="-72" x2="-42" y2="-72"/>
            <line x1="-92" y1="-56" x2="-42" y2="-56"/>
          </g>

          <!-- Right Chest Floppy Disk Drive & Blinking Status LEDs -->
          <rect x="25" y="-128" width="70" height="44" rx="4" fill="#524c3a" stroke="#2e2a1f" stroke-width="2.5"/>
          <rect x="33" y="-110" width="54" height="8" rx="2" fill="#1f1d16"/>
          <rect x="72" y="-98" width="12" height="6" rx="1" fill="#d94e28"/>
          <!-- Status LEDs -->
          <circle cx="35" cy="-66" r="6" fill="#38e864" filter="url(#neonGlow)"/>
          <circle cx="55" cy="-66" r="6" fill="#ffbd2e" filter="url(#neonGlow)"/>
          <circle cx="75" cy="-66" r="6" fill="#ff3b2e"/>

          <!-- Reel-to-Reel Magnetic Tape Deck in Lower Belly -->
          <rect x="-88" y="-25" width="176" height="118" rx="8" fill="#454030" stroke="#2b281d" stroke-width="3"/>
          <circle cx="-42" cy="34" r="36" fill="#29261c" stroke="#9e9578" stroke-width="3"/>
          <circle cx="-42" cy="34" r="10" fill="#dfd9c3"/>
          <path d="M -42 -2 L -42 18 M -73 52 L -55 42 M -11 52 L -29 42" stroke="#9e9578" stroke-width="4"/>
          <circle cx="42" cy="34" r="36" fill="#29261c" stroke="#9e9578" stroke-width="3"/>
          <circle cx="42" cy="34" r="10" fill="#dfd9c3"/>
          <path d="M 42 -2 L 42 18 M 11 52 L 29 42 M 73 52 L 55 42" stroke="#9e9578" stroke-width="4"/>
          <!-- Unspooling loose tape glitch (Dad is stressed!) -->
          <path d="M -12 55 Q 0 92 14 55" fill="none" stroke="#1a1410" stroke-width="3.5"/>

          <!-- Shirt Collar Plates & Awkward Crooked Clip-On Plaid Tie -->
          <polygon points="-58,-165 -8,-132 -38,-115" fill="#f5f2e6" stroke="#3b3628" stroke-width="3" stroke-linejoin="round"/>
          <polygon points="58,-165 8,-132 38,-115" fill="#f5f2e6" stroke="#3b3628" stroke-width="3" stroke-linejoin="round"/>
          <!-- Clip-on tie skewed 13 degrees -->
          <g transform="translate(0, -142) rotate(13)">
            <polygon points="-16,0 16,0 10,22 -10,22" fill="url(#plaidTie)" stroke="#2b0905" stroke-width="2.5"/>
            <polygon points="-10,22 10,22 24,148 0,178 -24,148" fill="url(#plaidTie)" stroke="#2b0905" stroke-width="2.5"/>
            <!-- Tartan plaid stripes -->
            <line x1="-12" y1="45" x2="14" y2="65" stroke="#ffcf54" stroke-width="2.5" opacity="0.75"/>
            <line x1="-16" y1="80" x2="18" y2="105" stroke="#388552" stroke-width="3" opacity="0.75"/>
            <line x1="-20" y1="115" x2="21" y2="145" stroke="#ffcf54" stroke-width="2.5" opacity="0.75"/>
            <line x1="12" y1="45" x2="-14" y2="65" stroke="#388552" stroke-width="2.5" opacity="0.75"/>
            <line x1="16" y1="80" x2="-18" y2="105" stroke="#ffcf54" stroke-width="2.5" opacity="0.75"/>
            <!-- Metal clip visible at top -->
            <rect x="-12" y="-5" width="24" height="6" rx="2" fill="#d0d7de" stroke="#333" stroke-width="1.5"/>
          </g>

          <!-- Dad's Right Arm (Viewer's Left): Hovering in a stiff, awkward "hover-hand" over Teen's right shoulder -->
          <path d="M -122 -135 C -162 -150, -155 -225, -182 -268" fill="none" stroke="#595340" stroke-width="30" stroke-linecap="round"/>
          <path d="M -122 -135 C -162 -150, -155 -225, -182 -268" fill="none" stroke="#b0a789" stroke-width="16" stroke-dasharray="12 8" stroke-linecap="round"/>
          <!-- Stiff open pincer claw hovering uncertainly in mid-air -->
          <g transform="translate(-188, -280) rotate(-38)">
            <rect x="-16" y="-12" width="32" height="22" rx="5" fill="url(#dadDark)" stroke="#2b281d" stroke-width="2.5"/>
            <path d="M -14 -12 C -26 -35, -10 -50, -4 -38" fill="none" stroke="#8a8268" stroke-width="8" stroke-linecap="round"/>
            <path d="M 14 -12 C 26 -35, 10 -50, 4 -38" fill="none" stroke="#8a8268" stroke-width="8" stroke-linecap="round"/>
            <!-- Nervous vibration lines around hover-claw -->
            <path d="M -32 -28 Q -36 -40 -26 -48" fill="none" stroke="#47e6ff" stroke-width="2.5" stroke-linecap="round" opacity="0.75"/>
            <path d="M 32 -28 Q 36 -40 26 -48" fill="none" stroke="#47e6ff" stroke-width="2.5" stroke-linecap="round" opacity="0.75"/>
          </g>

          <!-- Dad's Left Arm (Viewer's Right): Rigidly resting on knee -->
          <path d="M 122 -130 C 165 -55, 148 55, 92 145" fill="none" stroke="#595340" stroke-width="30" stroke-linecap="round"/>
          <path d="M 122 -130 C 165 -55, 148 55, 92 145" fill="none" stroke="#b0a789" stroke-width="16" stroke-dasharray="12 8" stroke-linecap="round"/>
          <circle cx="88" cy="152" r="20" fill="url(#dadDark)" stroke="#2b281d" stroke-width="3"/>

          <!-- Boxy CRT Monitor Head -->
          <g transform="translate(0, -285) rotate(2)">
            <!-- Neck Mount -->
            <rect x="-34" y="82" width="68" height="42" fill="#595340" stroke="#2b281d" stroke-width="3"/>
            <!-- Bent Rabbit-Ear Antennas on Top -->
            <line x1="-25" y1="-98" x2="-78" y2="-178" stroke="#9ba3ab" stroke-width="5" stroke-linecap="round"/>
            <circle cx="-78" cy="-178" r="7" fill="#d94e28"/>
            <!-- Right antenna kinked/bent awkwardly -->
            <polyline points="25,-98 58,-148 18,-172" fill="none" stroke="#9ba3ab" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="18" cy="-172" r="7" fill="#d94e28"/>
            <path d="M -38 -96 C -38 -118, 38 -118, 38 -96 Z" fill="url(#dadDark)" stroke="#2b281d" stroke-width="3"/>

            <!-- Outer CRT Casing -->
            <rect x="-118" y="-98" width="236" height="186" rx="20" fill="url(#dadBody)" stroke="#3b3628" stroke-width="4.5"/>
            <rect x="-106" y="-86" width="212" height="162" rx="14" fill="#8f876d" stroke="#4f4937" stroke-width="2.5"/>

            <!-- Recessed Dark Green CRT Screen -->
            <rect x="-94" y="-74" width="188" height="138" rx="18" fill="url(#dadScreen)" stroke="#26231a" stroke-width="4"/>

            <!-- CRT Scanlines -->
            <g stroke="#1d472b" stroke-width="1.5" opacity="0.45">
              <line x1="-88" y1="-55" x2="88" y2="-55"/>
              <line x1="-88" y1="-35" x2="88" y2="-35"/>
              <line x1="-88" y1="-15" x2="88" y2="-15"/>
              <line x1="-88" y1="5" x2="88" y2="5"/>
              <line x1="-88" y1="25" x2="88" y2="25"/>
              <line x1="-88" y1="45" x2="88" y2="45"/>
            </g>

            <!-- Heavy Black-Rimmed "Dad Glasses" Mounted over CRT Monitor -->
            <g transform="translate(0, -18) rotate(-3)">
              <!-- Left Frame -->
              <rect x="-86" y="-32" width="76" height="54" rx="8" fill="#a8e6cf" fill-opacity="0.08" stroke="#1c1b18" stroke-width="8"/>
              <rect x="-86" y="-32" width="76" height="12" rx="3" fill="#1c1b18"/>
              <!-- Right Frame -->
              <rect x="10" y="-32" width="76" height="54" rx="8" fill="#a8e6cf" fill-opacity="0.08" stroke="#1c1b18" stroke-width="8"/>
              <rect x="10" y="-32" width="76" height="12" rx="3" fill="#1c1b18"/>
              <!-- Bridge with white tape repair in center! -->
              <line x1="-10" y1="-12" x2="10" y2="-12" stroke="#1c1b18" stroke-width="8"/>
              <rect x="-7" y="-20" width="14" height="16" rx="2" transform="rotate(8)" fill="#f2efe4" stroke="#aba696" stroke-width="1.5"/>
            </g>

            <!-- Glowing Green Phosphor Eyes & Forced Grimace Smile -->
            <g filter="url(#neonGlow)">
              <!-- Wide Stressed Left Eye (slightly larger twitch) -->
              <circle cx="-48" cy="-16" r="19" fill="none" stroke="#3dff74" stroke-width="4"/>
              <circle cx="-46" cy="-16" r="6" fill="#3dff74"/>
              <!-- Right Eye (squinting/twitching) -->
              <circle cx="48" cy="-16" r="15" fill="none" stroke="#3dff74" stroke-width="4"/>
              <circle cx="46" cy="-16" r="5" fill="#3dff74"/>
              <path d="M 30 -36 L 66 -28" stroke="#3dff74" stroke-width="3.5" stroke-linecap="round"/>
              <path d="M -68 -32 L -28 -38" stroke="#3dff74" stroke-width="3.5" stroke-linecap="round"/>

              <!-- Extremely Stiff, Rectangular Gritted-Teeth "Smile" -->
              <rect x="-56" y="20" width="112" height="28" rx="6" fill="#091f10" stroke="#3dff74" stroke-width="3.5"/>
              <line x1="-56" y1="34" x2="56" y2="34" stroke="#3dff74" stroke-width="3"/>
              <line x1="-34" y1="20" x2="-34" y2="48" stroke="#3dff74" stroke-width="3"/>
              <line x1="-12" y1="20" x2="-12" y2="48" stroke="#3dff74" stroke-width="3"/>
              <line x1="12" y1="20" x2="12" y2="48" stroke="#3dff74" stroke-width="3"/>
              <line x1="34" y1="20" x2="34" y2="48" stroke="#3dff74" stroke-width="3"/>
            </g>

            <!-- Nervous Sweat / Coolant Droplets on Side of Monitor -->
            <path d="M -105 -48 C -112 -32, -98 -32, -105 -48 Z" fill="#47e6ff" stroke="#125e70" stroke-width="1.5"/>
            <path d="M -102 -36 C -112 -15, -92 -15, -102 -36 Z" fill="#47e6ff" stroke="#125e70" stroke-width="1.5"/>
            <path d="M 104 -30 C 96 -12, 112 -12, 104 -30 Z" fill="#47e6ff" stroke="#125e70" stroke-width="1.5"/>
          </g>
        </g>
      </g>''')

    # ==========================================
    # 6. MOM ROBOT (Center-Right - 1960s/80s Glamour Bot, Copper Beehive, Trying Too Hard)
    # ==========================================
    svg.append('''      <g id="mom-robot" filter="url(#dropShadow)">
        <!-- Graceful Sculpted Chrome/Lavender Legs angled politely together -->
        <!-- Left Leg -->
        <path d="M 695 925 L 675 1080 L 690 1200" fill="none" stroke="#6d5680" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M 695 925 L 675 1080 L 690 1200" fill="none" stroke="url(#momBody)" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="675" cy="1080" r="16" fill="url(#momRoseGold)" stroke="#4d2b1f" stroke-width="2.5"/>
        <!-- Right Leg -->
        <path d="M 760 925 L 742 1080 L 752 1200" fill="none" stroke="#6d5680" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M 760 925 L 742 1080 L 752 1200" fill="none" stroke="url(#momBody)" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="742" cy="1080" r="16" fill="url(#momRoseGold)" stroke="#4d2b1f" stroke-width="2.5"/>

        <!-- Retro High-Heeled Chrome Pumps -->
        <g transform="translate(686, 1205)">
          <path d="M -25 -15 L 18 -15 L 28 18 L 2 18 L -8 2 L -14 18 L -26 18 Z" fill="url(#momRoseGold)" stroke="#422116" stroke-width="2.5" stroke-linejoin="round"/>
        </g>
        <g transform="translate(752, 1205)">
          <path d="M -22 -15 L 22 -15 L 32 18 L 6 18 L -4 2 L -10 18 L -22 18 Z" fill="url(#momRoseGold)" stroke="#422116" stroke-width="2.5" stroke-linejoin="round"/>
        </g>

        <!-- Sculpted Hourglass Chassis (Leaning affectionately/possessively left toward Dad) -->
        <g transform="translate(725, 745) rotate(-6)">
          <!-- Flared Peplum Skirt / Hip Unit -->
          <path d="M -68 35 C -105 75, -112 135, -95 168 L 95 168 C 112 135, 105 75, 68 35 Z" fill="url(#momBody)" stroke="#4c385c" stroke-width="3.5"/>
          <path d="M -92 145 Q 0 162 92 145" fill="none" stroke="url(#momRoseGold)" stroke-width="8"/>

          <!-- Narrow Waist & Ribbed Chrome Midsection -->
          <rect x="-46" y="-22" width="92" height="68" rx="18" fill="url(#momRoseGold)" stroke="#4c385c" stroke-width="3"/>
          <line x1="-42" y1="-2" x2="42" y2="-2" stroke="#5e3425" stroke-width="3"/>
          <line x1="-42" y1="16" x2="42" y2="16" stroke="#5e3425" stroke-width="3"/>

          <!-- Upper Hourglass Torso with Dramatic 80s Shoulder Pads -->
          <path d="M -128 -148 L 128 -148 L 62 -12 L -62 -12 Z" fill="url(#momBody)" stroke="#4c385c" stroke-width="4" stroke-linejoin="round"/>
          <!-- Rose-Gold Shoulder Pad Caps -->
          <path d="M -134 -152 C -138 -175, -85 -172, -72 -148 Z" fill="url(#momRoseGold)" stroke="#4c385c" stroke-width="3"/>
          <path d="M 134 -152 C 138 -175, 85 -172, 72 -148 Z" fill="url(#momRoseGold)" stroke="#4c385c" stroke-width="3"/>

          <!-- Heart-Shaped Oscilloscope Screen on Chest -->
          <path d="M 0 -42 C -12 -42, -48 -72, -48 -98 C -48 -118, -22 -126, 0 -106 C 22 -126, 48 -118, 48 -98 C 48 -72, 12 -42, 0 -42 Z" fill="#21092b" stroke="url(#momRoseGold)" stroke-width="4"/>
          <!-- Glowing Pink ECG Heartbeat Wave inside Heart -->
          <polyline points="-36,-88 -18,-88 -10,-108 -2,-68 8,-98 16,-82 36,-82" fill="none" stroke="#ff47b5" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#neonGlow)"/>

          <!-- Oversized Pearl-Bearing Necklace around Collar -->
          <g fill="url(#chromeMetal)" stroke="#42324f" stroke-width="2">
            <circle cx="-56" cy="-148" r="10"/>
            <circle cx="-38" cy="-136" r="11"/>
            <circle cx="-19" cy="-129" r="12"/>
            <circle cx="0" cy="-126" r="13"/>
            <circle cx="19" cy="-129" r="12"/>
            <circle cx="38" cy="-136" r="11"/>
            <circle cx="56" cy="-148" r="10"/>
          </g>

          <!-- Mom's Right Arm (Viewer's Left): Clinging tightly to Dad's Left Arm/Shoulder -->
          <path d="M -118 -135 C -165 -85, -185 -15, -148 25" fill="none" stroke="#6d5680" stroke-width="24" stroke-linecap="round"/>
          <path d="M -118 -135 C -165 -85, -185 -15, -148 25" fill="none" stroke="url(#momBody)" stroke-width="16" stroke-dasharray="12 8" stroke-linecap="round"/>
          <!-- Dainty Rose-Gold Pincer clasped onto Dad's arm -->
          <circle cx="-146" cy="28" r="16" fill="url(#momRoseGold)" stroke="#4c385c" stroke-width="3"/>

          <!-- Mom's Left Arm (Viewer's Right): Reaching down to corral the chaotic Kid Robot -->
          <path d="M 118 -135 C 162 -55, 118 65, 22 162" fill="none" stroke="#6d5680" stroke-width="24" stroke-linecap="round"/>
          <path d="M 118 -135 C 162 -55, 118 65, 22 162" fill="none" stroke="url(#momBody)" stroke-width="16" stroke-dasharray="12 8" stroke-linecap="round"/>

          <!-- Slender Segmented Neck -->
          <rect x="-22" y="-192" width="44" height="44" rx="8" fill="url(#momRoseGold)" stroke="#4c385c" stroke-width="3"/>
          <line x1="-22" y1="-178" x2="22" y2="-178" stroke="#5e3425" stroke-width="2.5"/>
          <line x1="-22" y1="-164" x2="22" y2="-164" stroke="#5e3425" stroke-width="2.5"/>

          <!-- Glamorous Head with Towering Copper-Coil Beehive & Tilted Camera-Ready Smile -->
          <g transform="translate(4, -255) rotate(-8)">
            <!-- Towering 1960s/80s Copper-Tubing Beehive Hairdo -->
            <g stroke="#4a2515" stroke-width="3">
              <ellipse cx="0" cy="-165" rx="46" ry="22" fill="url(#momRoseGold)"/>
              <ellipse cx="0" cy="-142" rx="62" ry="25" fill="url(#momRoseGold)"/>
              <ellipse cx="0" cy="-115" rx="76" ry="28" fill="url(#momRoseGold)"/>
              <ellipse cx="0" cy="-85" rx="88" ry="30" fill="url(#momRoseGold)"/>
              <ellipse cx="0" cy="-52" rx="94" ry="32" fill="url(#momRoseGold)"/>
            </g>
            <!-- Decorative Atomic Hairpins sticking out of Beehive -->
            <line x1="-55" y1="-145" x2="-98" y2="-185" stroke="#5ce6e6" stroke-width="4" stroke-linecap="round"/>
            <circle cx="-98" cy="-185" r="9" fill="#ff47b5" stroke="#21092b" stroke-width="2"/>
            <line x1="58" y1="-138" x2="105" y2="-172" stroke="#5ce6e6" stroke-width="4" stroke-linecap="round"/>
            <circle cx="105" cy="-172" r="9" fill="#5ce6e6" stroke="#0d4a54" stroke-width="2"/>
            <!-- Tiny Spark/Smoke at top of hairdo (overheated hair coil!) -->
            <path d="M 18 -188 L 28 -208 L 15 -202 L 26 -222" fill="none" stroke="#ffea54" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" filter="url(#neonGlow)"/>

            <!-- Dangling Geometric Satellite Earrings -->
            <g transform="translate(-88, 12) rotate(12)">
              <line x1="0" y1="0" x2="0" y2="28" stroke="#ffd885" stroke-width="3"/>
              <polygon points="0,22 -16,48 16,48" fill="#5ce6e6" stroke="#185a66" stroke-width="2"/>
              <circle cx="0" cy="40" r="5" fill="#ff47b5"/>
            </g>
            <g transform="translate(88, 12) rotate(8)">
              <line x1="0" y1="0" x2="0" y2="28" stroke="#ffd885" stroke-width="3"/>
              <polygon points="0,22 -16,48 16,48" fill="#5ce6e6" stroke="#185a66" stroke-width="2"/>
              <circle cx="0" cy="40" r="5" fill="#ff47b5"/>
            </g>

            <!-- Oval Head Shell -->
            <ellipse cx="0" cy="-12" rx="86" ry="66" fill="url(#momBody)" stroke="#4c385c" stroke-width="4"/>

            <!-- Cat-Eye Visor Frame -->
            <path d="M -78 -22 C -65 -52, -18 -42, 0 -28 C 18 -42, 65 -52, 78 -22 C 72 18, 25 22, 0 8 C -25 22, -72 18, -78 -22 Z" fill="url(#momVisor)" stroke="url(#momRoseGold)" stroke-width="4"/>

            <!-- Metal Eyelash Fins on Upper Cat-Eye Corners -->
            <path d="M -72 -26 L -90 -42 M -62 -34 L -76 -52 M -48 -38 L -58 -56" stroke="#4c385c" stroke-width="3.5" stroke-linecap="round"/>
            <path d="M 72 -26 L 90 -42 M 62 -34 L 76 -52 M 48 -38 L 58 -56" stroke="#4c385c" stroke-width="3.5" stroke-linecap="round"/>

            <!-- Glowing Cyan/Magenta Glamour Eyes (Intensely wide "Everything is fine!" stare) -->
            <g filter="url(#neonGlow)">
              <!-- Left Eye -->
              <ellipse cx="-34" cy="-14" rx="16" ry="14" fill="#123845" stroke="#5ce6e6" stroke-width="3"/>
              <circle cx="-32" cy="-14" r="6" fill="#ffffff"/>
              <!-- Right Eye (Slightly askew shutter wink) -->
              <ellipse cx="34" cy="-14" rx="16" ry="11" fill="#123845" stroke="#5ce6e6" stroke-width="3"/>
              <circle cx="32" cy="-14" r="5" fill="#ffffff"/>

              <!-- Rosy Airbrushed Cheek Glows -->
              <ellipse cx="-52" cy="18" rx="14" ry="8" fill="#ff47b5" opacity="0.55"/>
              <ellipse cx="52" cy="18" rx="14" ry="8" fill="#ff47b5" opacity="0.55"/>

              <!-- Exaggerated Neon Lipstick Smile Arc -->
              <path d="M -32 22 Q 0 48 32 22 Q 0 34 -32 22 Z" fill="#ff2e93" stroke="#ff94c8" stroke-width="2.5"/>
            </g>
          </g>
        </g>
      </g>''')

    # ==========================================
    # 7. KID ROBOT (Front Center - Toy Tin/Plastic Bot, Upside-Down/Tilted, Hyperactive)
    # ==========================================
    svg.append('''      <g id="kid-robot" filter="url(#dropShadow)">
        <!-- Kid's Splayed Toy Legs & Spring-Loaded Sneakers -->
        <!-- Left Leg sticking out at wild angle -->
        <path d="M 535 1175 L 445 1235" fill="none" stroke="#1fa6b8" stroke-width="26" stroke-linecap="round"/>
        <path d="M 535 1175 L 445 1235" fill="none" stroke="#ffe863" stroke-width="14" stroke-dasharray="10 8" stroke-linecap="round"/>
        <g transform="translate(425, 1238) rotate(-32)">
          <rect x="-28" y="-18" width="52" height="36" rx="12" fill="url(#kidRed)" stroke="#5c0b04" stroke-width="3"/>
          <rect x="-32" y="10" width="60" height="12" rx="6" fill="#ffffff" stroke="#5c0b04" stroke-width="2.5"/>
        </g>

        <!-- Right Leg kicked up on the other side -->
        <path d="M 635 1175 L 725 1215" fill="none" stroke="#1fa6b8" stroke-width="26" stroke-linecap="round"/>
        <path d="M 635 1175 L 725 1215" fill="none" stroke="#ffe863" stroke-width="14" stroke-dasharray="10 8" stroke-linecap="round"/>
        <g transform="translate(745, 1218) rotate(25)">
          <rect x="-24" y="-18" width="52" height="36" rx="12" fill="url(#kidRed)" stroke="#5c0b04" stroke-width="3"/>
          <rect x="-28" y="10" width="60" height="12" rx="6" fill="#ffffff" stroke="#5c0b04" stroke-width="2.5"/>
        </g>

        <!-- Round Roly-Poly Toy Torso (Tilted 16 deg sideways in mid-wiggle) -->
        <g transform="translate(590, 1105) rotate(16)">
          <!-- Giant Golden Wind-Up Key on Side/Back -->
          <g transform="translate(-95, -15) rotate(-15)">
            <rect x="-18" y="-8" width="28" height="16" rx="4" fill="url(#kidYellow)" stroke="#6e4500" stroke-width="3"/>
            <circle cx="-36" cy="-22" r="20" fill="none" stroke="url(#kidYellow)" stroke-width="10"/>
            <circle cx="-36" cy="-22" r="20" fill="none" stroke="#6e4500" stroke-width="2.5"/>
            <circle cx="-36" cy="22" r="20" fill="none" stroke="url(#kidYellow)" stroke-width="10"/>
            <circle cx="-36" cy="22" r="20" fill="none" stroke="#6e4500" stroke-width="2.5"/>
          </g>

          <!-- Main Spherical/Stubby Body -->
          <rect x="-82" y="-88" width="164" height="156" rx="52" fill="url(#kidYellow)" stroke="#6e4500" stroke-width="4"/>
          <!-- Red Diaper / Pelvis Trim -->
          <path d="M -76 15 Q 0 42 76 15 L 68 52 C 50 75, -50 75, -68 52 Z" fill="url(#kidRed)" stroke="#5c0b04" stroke-width="3.5"/>

          <!-- Colorful Arcade Push-Buttons & Radar Spinner on Belly -->
          <rect x="-56" y="-58" width="112" height="62" rx="16" fill="#182436" stroke="#0d6370" stroke-width="3.5"/>
          <circle cx="-30" cy="-27" r="14" fill="#ff3b2e" stroke="#ffffff" stroke-width="2"/>
          <circle cx="4" cy="-36" r="10" fill="#38e864" stroke="#ffffff" stroke-width="2"/>
          <circle cx="8" cy="-14" r="10" fill="#33f2ff" stroke="#ffffff" stroke-width="2"/>
          <polygon points="36,-42 48,-16 24,-16" fill="#ffde2e" stroke="#ffffff" stroke-width="2" stroke-linejoin="round"/>

          <!-- Kid's Left Arm (Viewer's Left): Flailing High in the Air Waving! -->
          <path d="M -78 -52 C -135 -95, -145 -165, -95 -215" fill="none" stroke="#0d6370" stroke-width="24" stroke-linecap="round"/>
          <path d="M -78 -52 C -135 -95, -145 -165, -95 -215" fill="none" stroke="url(#kidTeal)" stroke-width="16" stroke-dasharray="9 7" stroke-linecap="round"/>
          <!-- Red Magnet Claw Waving with Motion Arcs -->
          <g transform="translate(-92, -222) rotate(-35)">
            <path d="M -18 10 L -18 -12 C -18 -28, 18 -28, 18 -12 L 18 10" fill="none" stroke="url(#kidRed)" stroke-width="12" stroke-linecap="round"/>
            <path d="M -24 -28 Q 0 -42 24 -28" fill="none" stroke="#ffea54" stroke-width="3" stroke-linecap="round"/>
            <path d="M -32 -38 Q 0 -55 32 -38" fill="none" stroke="#ffea54" stroke-width="2.5" stroke-linecap="round"/>
          </g>

          <!-- Kid's Right Arm (Viewer's Right): Grabbing onto the Robo-Dog's Tail/Hose! -->
          <path d="M 78 -42 C 135 -25, 175 18, 212 42" fill="none" stroke="#0d6370" stroke-width="24" stroke-linecap="round"/>
          <path d="M 78 -42 C 135 -25, 175 18, 212 42" fill="none" stroke="url(#kidTeal)" stroke-width="16" stroke-dasharray="9 7" stroke-linecap="round"/>

          <!-- Boingy Jack-in-the-Box Spring Neck (Stretched & Tilted Wildly!) -->
          <path d="M -15 -88 L 18 -102 L -18 -116 L 20 -130 L -12 -145 L 12 -156" fill="none" stroke="#b8c4d1" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>

          <!-- Bubble-Helmet Head with Propeller Beanie (Cocked 22 degrees!) -->
          <g transform="translate(8, -212) rotate(22)">
            <!-- Collar Ring -->
            <ellipse cx="0" cy="48" rx="68" ry="16" fill="url(#kidRed)" stroke="#5c0b04" stroke-width="3.5"/>

            <!-- Inner Robot Face inside Dome -->
            <rect x="-52" y="-36" width="104" height="78" rx="26" fill="url(#kidTeal)" stroke="#09454f" stroke-width="3.5"/>

            <!-- Mismatched Googly/Pinwheel Eyes -->
            <!-- Big Left Eye (Dilated pupil looking up-right) -->
            <circle cx="-24" cy="-6" r="20" fill="#ffffff" stroke="#09454f" stroke-width="3"/>
            <circle cx="-16" cy="-10" r="9" fill="#111822"/>
            <circle cx="-19" cy="-13" r="3.5" fill="#ffffff"/>
            <!-- Smaller Right Eye (Bright white sclera with pupil looking down-left for full googly cross-eyed energy!) -->
            <circle cx="24" cy="-10" r="15" fill="#ffffff" stroke="#09454f" stroke-width="3"/>
            <circle cx="18" cy="-4" r="6.5" fill="#111822"/>
            <circle cx="16" cy="-6" r="2.5" fill="#ffffff"/>

            <!-- Goofy Open-Mouthed Laugh with Metal Tongue Sticking Out -->
            <path d="M -26 18 Q 0 42 26 18 Z" fill="#182436" stroke="#09454f" stroke-width="3"/>
            <!-- Pink/Red Springy Metal Tongue -->
            <path d="M -8 26 C -8 48, 16 48, 14 26 Z" fill="#ff477e" stroke="#7a0d2e" stroke-width="2.5"/>
            <line x1="3" y1="26" x2="4" y2="39" stroke="#7a0d2e" stroke-width="2"/>

            <!-- Clear Glass Bubble Helmet Dome -->
            <circle cx="0" cy="-4" r="72" fill="url(#glassDome)" stroke="#8cf4ff" stroke-width="3"/>
            <!-- Specular Highlight on Bubble Dome -->
            <path d="M -48 -38 A 56 56 0 0 1 12 -58" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="0.65"/>

            <!-- Propeller Beanie Cap Perched on Top of Dome -->
            <path d="M -42 -62 C -35 -92, 35 -92, 42 -62 Z" fill="url(#kidRed)" stroke="#5c0b04" stroke-width="3"/>
            <path d="M -18 -82 Q 0 -62 18 -82" fill="none" stroke="#ffe863" stroke-width="4"/>
            <line x1="0" y1="-84" x2="0" y2="-104" stroke="#d0d7de" stroke-width="6"/>
            <!-- Spinning Propeller Blades & Blur -->
            <ellipse cx="0" cy="-104" rx="54" ry="8" fill="#ffe863" opacity="0.35"/>
            <path d="M -48 -104 C -25 -114, -5 -98, 0 -104 C 5 -110, 25 -94, 48 -104 C 25 -112, -25 -96, -48 -104 Z" fill="url(#kidYellow)" stroke="#6e4500" stroke-width="2.5"/>
            <circle cx="0" cy="-104" r="7" fill="url(#kidRed)" stroke="#5c0b04" stroke-width="2"/>
          </g>
        </g>

        <!-- Mom's Hand resting firmly on the outer rim of Kid's Bubble Helmet to keep him in frame -->
        <circle cx="712" cy="918" r="18" fill="url(#momRoseGold)" stroke="#4c385c" stroke-width="3"/>
      </g>''')

    # ==========================================
    # 8. ROBO-PET DOG (Front Right - Canister Vacuum Dog, Butt to Camera, Chewing Cable)
    # ==========================================
    svg.append('''      <g id="robo-dog" filter="url(#dropShadow)">
        <!-- Studio Flash Sync Cable running across foreground floor (Being chewed by dog!) -->
        <path d="M -110 1320 Q 280 1280 580 1330 T 895 1280 T 1310 1305" fill="none" stroke="#1b1c21" stroke-width="11" stroke-linecap="round"/>
        <path d="M -110 1320 Q 280 1280 580 1330 T 895 1280 T 1310 1305" fill="none" stroke="#434652" stroke-width="3" stroke-dasharray="18 12" stroke-linecap="round"/>

        <!-- Vacuum Hose Tail sticking up on left (being grabbed by Kid Robot!) -->
        <path d="M 805 1165 C 775 1135, 795 1095, 825 1068" fill="none" stroke="#2c3540" stroke-width="16" stroke-linecap="round"/>
        <path d="M 805 1165 C 775 1135, 795 1095, 825 1068" fill="none" stroke="#5ce6e6" stroke-width="10" stroke-dasharray="6 6" stroke-linecap="round"/>
        <!-- Kid's Red Magnet Claw clamped onto the tail! -->
        <circle cx="800" cy="1125" r="16" fill="url(#kidRed)" stroke="#5c0b04" stroke-width="3"/>
        <!-- Glowing Antenna Pom-Pom on Tip of Tail -->
        <circle cx="828" cy="1062" r="14" fill="#ff47b5" filter="url(#neonGlow)"/>

        <!-- Stubby Roller-Caster Legs (Play-bow / squatting posture, rear higher than front) -->
        <!-- Back Left Leg -->
        <path d="M 822 1225 L 805 1295" stroke="url(#chromeMetal)" stroke-width="18" stroke-linecap="round"/>
        <circle cx="802" cy="1302" r="14" fill="#22262e" stroke="#8f9ba8" stroke-width="4"/>
        <!-- Back Right Leg -->
        <path d="M 875 1235 L 868 1308" stroke="url(#chromeMetal)" stroke-width="18" stroke-linecap="round"/>
        <circle cx="868" cy="1315" r="14" fill="#22262e" stroke="#8f9ba8" stroke-width="4"/>
        <!-- Front Left Leg -->
        <path d="M 925 1250 L 935 1305" stroke="url(#chromeMetal)" stroke-width="18" stroke-linecap="round"/>
        <circle cx="938" cy="1312" r="14" fill="#22262e" stroke="#8f9ba8" stroke-width="4"/>
        <!-- Front Right Leg -->
        <path d="M 968 1245 L 988 1295" stroke="url(#chromeMetal)" stroke-width="18" stroke-linecap="round"/>
        <circle cx="992" cy="1302" r="14" fill="#22262e" stroke="#8f9ba8" stroke-width="4"/>

        <!-- Chrome Canister Body (Angled down toward front-right) -->
        <g transform="translate(885, 1205) rotate(14)">
          <rect x="-85" y="-48" width="170" height="96" rx="46" fill="url(#chromeMetal)" stroke="#2b333d" stroke-width="4"/>
          <!-- Teal Racing Stripe around Canister -->
          <rect x="-35" y="-46" width="42" height="92" fill="url(#kidTeal)" stroke="#125163" stroke-width="2.5"/>
          <!-- Rear Exhaust Port (Facing semi-toward camera!) -->
          <circle cx="-62" cy="0" r="20" fill="#2c3540" stroke="#181d24" stroke-width="3"/>
          <circle cx="-62" cy="0" r="10" fill="#14181f"/>
          <!-- Red Collared Tag Ring -->
          <path d="M 48 -46 L 48 46" stroke="#d92b1c" stroke-width="14" stroke-linecap="round"/>
          <polygon points="52,48 42,68 62,68" fill="#ffe863" stroke="#6e4500" stroke-width="2"/>
        </g>

        <!-- Dog Head Turned Back Looking Wild-Eyed at Camera while Chewing Sync Cord -->
        <g transform="translate(965, 1235) rotate(-8)">
          <!-- Snout / Dustbuster Head -->
          <path d="M -38 -36 L 42 -22 C 62 -15, 62 25, 42 32 L -38 42 Z" fill="url(#chromeMetal)" stroke="#2b333d" stroke-width="3.5" stroke-linejoin="round"/>
          <!-- Floppy Satellite-Dish Metal Ears -->
          <ellipse cx="-18" cy="-46" rx="28" ry="12" transform="rotate(-28 -18 -46)" fill="url(#kidTeal)" stroke="#125163" stroke-width="3"/>
          <ellipse cx="14" cy="-42" rx="26" ry="11" transform="rotate(22 14 -42)" fill="url(#kidTeal)" stroke="#125163" stroke-width="3"/>

          <!-- Glowing Yellow Googly Sensor Eyes -->
          <circle cx="-6" cy="-8" r="13" fill="#181d24" stroke="#2b333d" stroke-width="2.5"/>
          <circle cx="-4" cy="-8" r="7" fill="#ffea54" filter="url(#neonGlow)"/>
          <circle cx="24" cy="-4" r="11" fill="#181d24" stroke="#2b333d" stroke-width="2.5"/>
          <circle cx="22" cy="-4" r="6" fill="#ffea54" filter="url(#neonGlow)"/>

          <!-- Rubber Nose Bumper -->
          <circle cx="52" cy="4" r="10" fill="#d92b1c" stroke="#4a0904" stroke-width="2.5"/>

          <!-- Jaws Clamped onto the Studio Sync Cable with Bright Electric Sparks! -->
          <path d="M -12 28 L 36 24" stroke="#181d24" stroke-width="6" stroke-linecap="round"/>
          <!-- Electric Sparks flying from chewed cable -->
          <g stroke="#33f2ff" stroke-width="3" stroke-linecap="round" filter="url(#neonGlow)">
            <polyline points="-8,45 -22,32 -14,25 -28,12"/>
            <polyline points="12,48 24,65 18,72 32,86"/>
            <polyline points="28,36 48,32 42,22 62,18"/>
          </g>
          <g stroke="#ffea54" stroke-width="2.5" stroke-linecap="round" filter="url(#neonGlow)">
            <line x1="-18" y1="52" x2="-34" y2="62"/>
            <line x1="4" y1="54" x2="2" y2="74"/>
            <line x1="36" y1="44" x2="54" y2="56"/>
          </g>
        </g>

        <!-- Small Puddle of Dark Motor Oil on Floor under Robo-Dog (Oops!) -->
        <path d="M 815 1335 C 785 1332, 772 1348, 805 1355 C 835 1362, 875 1358, 868 1342 C 862 1330, 838 1338, 815 1335 Z" fill="#0d131a" stroke="#2a3f54" stroke-width="1.5"/>
        <path d="M 805 1344 Q 828 1350 848 1343" fill="none" stroke="#47a8bd" stroke-width="2" opacity="0.5"/>
      </g>''')

    svg.append('    </g>')  # End of #portrait-subjects

    # ==========================================
    # 9. FOREGROUND STUDIO DETAILS & VIGNETTE
    # ==========================================
    motes = [
        (140, 320, 3.5), (380, 160, 2.5), (680, 120, 4.0),
        (960, 190, 3.0), (1260, 380, 3.5), (150, 780, 2.5),
        (540, 520, 2.0), (920, 580, 2.5), (1280, 820, 3.0)
    ]
    svg.append('    <g fill="#ffffff" opacity="0.28" filter="url(#neonGlow)">')
    for mx, my, mr in motes:
        svg.append(f'      <circle cx="{mx}" cy="{my}" r="{mr}"/>')
    svg.append('    </g>')

    svg.append(f'    <rect x="0" y="0" width="{W}" height="{H}" fill="url(#vignette)" pointer-events="none"/>')

    # Subtle vintage studio print inner gold-trimmed mat border
    svg.append(f'    <rect x="24" y="24" width="{W-48}" height="{H-48}" rx="8" fill="none" stroke="#8c734b" stroke-width="2.5" opacity="0.45"/>')
    svg.append(f'    <rect x="32" y="32" width="{W-64}" height="{H-64}" rx="6" fill="none" stroke="#d9bd8c" stroke-width="1" opacity="0.3"/>')

    svg.append('  </g>')
    svg.append('</svg>')
    return "\n".join(svg)


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    svg_content = create_svg()
    output_path = os.path.join("output", "awkward_robot_family_portrait.svg")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Wrote {output_path} ({len(svg_content)} bytes)")
