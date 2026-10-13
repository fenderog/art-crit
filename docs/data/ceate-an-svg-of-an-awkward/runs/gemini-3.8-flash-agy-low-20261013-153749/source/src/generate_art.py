#!/usr/bin/env python3
"""
Generate an intricate, high-quality SVG representing an awkward family portrait of robots.
No text allowed.
"""

def generate_svg():
    svg_code = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="100%" height="100%">
  <defs>
    <!-- Background Gradients -->
    <radialGradient id="vignette" cx="50%" cy="45%" r="65%">
      <stop offset="0%" stop-color="#4a3f55"/>
      <stop offset="60%" stop-color="#2a2235"/>
      <stop offset="100%" stop-color="#140f1c"/>
    </radialGradient>
    <linearGradient id="wallPatternGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#5a4d66" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#251c30" stop-opacity="0.6"/>
    </linearGradient>
    <linearGradient id="floorGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1e1822"/>
      <stop offset="20%" stop-color="#2c1e22"/>
      <stop offset="100%" stop-color="#120b0d"/>
    </linearGradient>
    <linearGradient id="rugGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#542329"/>
      <stop offset="50%" stop-color="#843b44"/>
      <stop offset="100%" stop-color="#542329"/>
    </linearGradient>

    <!-- Metallic & Component Gradients -->
    <!-- Gold / Brass (Mom) -->
    <linearGradient id="brassGrad" x1="0.2" y1="0" x2="0.8" y2="1">
      <stop offset="0%" stop-color="#ffe28a"/>
      <stop offset="40%" stop-color="#d4af37"/>
      <stop offset="70%" stop-color="#aa820a"/>
      <stop offset="100%" stop-color="#5a4505"/>
    </linearGradient>
    <linearGradient id="brassDark" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#a67c1e"/>
      <stop offset="100%" stop-color="#4e3b0d"/>
    </linearGradient>
    <linearGradient id="pearlGrad" x1="0.3" y1="0" x2="0.7" y2="1">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="60%" stop-color="#d9e2ec"/>
      <stop offset="100%" stop-color="#9fb3c8"/>
    </linearGradient>

    <!-- Industrial Cast Iron / Steel (Dad) -->
    <linearGradient id="castIron" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#8b95a5"/>
      <stop offset="45%" stop-color="#535c68"/>
      <stop offset="85%" stop-color="#313740"/>
      <stop offset="100%" stop-color="#1e2229"/>
    </linearGradient>
    <linearGradient id="castIronDark" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#3c434d"/>
      <stop offset="100%" stop-color="#181c22"/>
    </linearGradient>
    <linearGradient id="rustAccent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#8d4024"/>
      <stop offset="100%" stop-color="#5c2612"/>
    </linearGradient>

    <!-- Sleek Matte Dark/Neon (Emo Teen) -->
    <linearGradient id="emoBody" x1="0" y1="0" x2="0.8" y2="1">
      <stop offset="0%" stop-color="#383842"/>
      <stop offset="50%" stop-color="#212128"/>
      <stop offset="100%" stop-color="#111115"/>
    </linearGradient>
    <linearGradient id="emoPurple" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#b827fc"/>
      <stop offset="100%" stop-color="#491069"/>
    </linearGradient>

    <!-- Retro Beige Plastic (Nerd Kid) -->
    <linearGradient id="beigePlastic" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#fff8e7"/>
      <stop offset="50%" stop-color="#e8dec8"/>
      <stop offset="100%" stop-color="#b8ad96"/>
    </linearGradient>
    <linearGradient id="crtScreen" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#153621"/>
      <stop offset="50%" stop-color="#1f5232"/>
      <stop offset="100%" stop-color="#0c2014"/>
    </linearGradient>

    <!-- Toddler / Baby Chrome & Primary Yellow -->
    <linearGradient id="toddlerYellow" x1="0.2" y1="0" x2="0.8" y2="1">
      <stop offset="0%" stop-color="#fff066"/>
      <stop offset="50%" stop-color="#f5b300"/>
      <stop offset="100%" stop-color="#b37d00"/>
    </linearGradient>
    <linearGradient id="toddlerBlue" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#4dc9ff"/>
      <stop offset="100%" stop-color="#006b99"/>
    </linearGradient>

    <!-- Dog / Pet Toaster Chrome -->
    <linearGradient id="chrome" x1="0.2" y1="0" x2="0.8" y2="1">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="25%" stop-color="#d6dde6"/>
      <stop offset="50%" stop-color="#99aab8"/>
      <stop offset="75%" stop-color="#e2e8f0"/>
      <stop offset="100%" stop-color="#64748b"/>
    </linearGradient>

    <!-- Glows and Lighting Filters -->
    <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <filter id="neonGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur1"/>
      <feGaussianBlur stdDeviation="8" result="blur2"/>
      <feMerge>
        <feMergeNode in="blur2"/>
        <feMergeNode in="blur1"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="dropShadow" x="-15%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="18" stdDeviation="15" flood-color="#08060a" flood-opacity="0.7"/>
    </filter>
    <filter id="sofaShadow" x="-20%" y="-10%" width="140%" height="140%">
      <feDropShadow dx="0" dy="25" stdDeviation="20" flood-color="#050307" flood-opacity="0.85"/>
    </filter>

    <!-- Victorian Wallpaper Pattern -->
    <pattern id="damask" width="60" height="60" patternUnits="userSpaceOnUse">
      <path d="M30 5 C35 15 45 15 45 25 C45 35 35 35 30 45 C25 35 15 35 15 25 C15 15 25 15 30 5 Z" fill="none" stroke="#685775" stroke-width="1.5" stroke-opacity="0.2"/>
      <circle cx="30" cy="25" r="3" fill="#685775" fill-opacity="0.2"/>
      <circle cx="0" cy="0" r="2" fill="#685775" fill-opacity="0.15"/>
      <circle cx="60" cy="0" r="2" fill="#685775" fill-opacity="0.15"/>
      <circle cx="0" cy="60" r="2" fill="#685775" fill-opacity="0.15"/>
      <circle cx="60" cy="60" r="2" fill="#685775" fill-opacity="0.15"/>
    </pattern>

    <!-- Carpet Texture Pattern -->
    <pattern id="carpetPattern" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M0 20 L20 0 L40 20 L20 40 Z" fill="none" stroke="#99444f" stroke-width="1" stroke-opacity="0.3"/>
      <circle cx="20" cy="20" r="3" fill="#3b171c" fill-opacity="0.4"/>
    </pattern>
  </defs>

  <!-- ================= BACKGROUND STUDIO SETTING ================= -->
  <!-- Main Studio Wall -->
  <rect x="0" y="0" width="1200" height="900" fill="url(#vignette)"/>
  <rect x="0" y="0" width="1200" height="680" fill="url(#damask)"/>

  <!-- Studio Backdrop Curtain / Arch Drape -->
  <path d="M-20 0 C200 40 250 200 180 500 C150 620 50 680 -20 700 Z" fill="#22182b" opacity="0.5"/>
  <path d="M1220 0 C1000 40 950 200 1020 500 C1050 620 1150 680 1220 700 Z" fill="#22182b" opacity="0.5"/>

  <!-- Awkward Framed Landscape on Wall (Slightly Crooked / Tilting) -->
  <g transform="translate(180, 110) rotate(-4.5)">
    <!-- Picture frame shadow -->
    <rect x="-4" y="-4" width="138" height="108" rx="3" fill="#100b17" opacity="0.6"/>
    <!-- Gilt Frame -->
    <rect x="0" y="0" width="130" height="100" rx="3" fill="#7d6328" stroke="#d4af37" stroke-width="3"/>
    <!-- Picture Canvas: Schematic of an Oil Derrick / Power Plant -->
    <rect x="8" y="8" width="114" height="84" fill="#202c33"/>
    <!-- Stylized schematic mountain and electricity tower -->
    <polygon points="12,80 45,40 70,80" fill="#324952"/>
    <polygon points="55,80 85,30 118,80" fill="#44616d"/>
    <!-- Wire lines & little glowing moon/lightbulb -->
    <line x1="8" y1="50" x2="122" y2="65" stroke="#ffe28a" stroke-width="1" stroke-dasharray="3,3" opacity="0.7"/>
    <circle cx="35" cy="25" r="7" fill="#ffdd55" opacity="0.85"/>
    <path d="M35 15 L35 18 M35 32 L35 35 M25 25 L28 25 M42 25 L45 25" stroke="#ffdd55" stroke-width="1.5"/>
    <!-- Hanging Wire -->
    <line x1="65" y1="0" x2="65" y2="-45" stroke="#8a7752" stroke-width="1.5"/>
    <circle cx="65" cy="-45" r="3" fill="#d4af37"/>
  </g>

  <!-- Studio Floor -->
  <rect x="0" y="660" width="1200" height="240" fill="url(#floorGrad)"/>
  <!-- Floor baseboard molding -->
  <rect x="0" y="650" width="1200" height="16" fill="#1b1320"/>
  <rect x="0" y="662" width="1200" height="4" fill="#3a2b42"/>

  <!-- Ornate Photographer's Studio Rug -->
  <ellipse cx="600" cy="775" rx="560" ry="105" fill="#180e14" opacity="0.6"/>
  <ellipse cx="600" cy="770" rx="540" ry="95" fill="url(#rugGrad)"/>
  <ellipse cx="600" cy="770" rx="530" ry="88" fill="url(#carpetPattern)"/>
  <ellipse cx="600" cy="770" rx="510" ry="78" fill="none" stroke="#dca858" stroke-width="3" stroke-dasharray="8,5" opacity="0.7"/>
  <ellipse cx="600" cy="770" rx="460" ry="65" fill="none" stroke="#631b25" stroke-width="6" opacity="0.6"/>

  <!-- Studio Cables Snaking on Floor (adds awkward staging realism) -->
  <path d="M-50 780 C120 790 180 840 240 820 C290 805 320 830 420 840" fill="none" stroke="#110d14" stroke-width="10" stroke-linecap="round"/>
  <path d="M-50 780 C120 790 180 840 240 820 C290 805 320 830 420 840" fill="none" stroke="#252530" stroke-width="6" stroke-linecap="round"/>
  
  <path d="M1250 750 C1100 770 1020 850 940 830 C880 815 820 860 760 845" fill="none" stroke="#110d14" stroke-width="8" stroke-linecap="round"/>
  <path d="M1250 750 C1100 770 1020 850 940 830 C880 815 820 860 760 845" fill="none" stroke="#36222b" stroke-width="5" stroke-linecap="round"/>

  <!-- ================= THE VELVET STUDIO SOFA ================= -->
  <!-- Huge heavy family sofa anchoring the center/parents -->
  <g id="sofa" filter="url(#sofaShadow)">
    <!-- Sofa Backrest Cushion -->
    <path d="M 330 380 C 330 350, 870 350, 870 380 L 890 600 L 310 600 Z" fill="#4d1c2b"/>
    <!-- Backrest Tufting Details -->
    <path d="M 350 420 Q 600 400 850 420" stroke="#2c0f18" stroke-width="3" fill="none"/>
    <path d="M 340 480 Q 600 460 860 480" stroke="#2c0f18" stroke-width="3" fill="none"/>
    <path d="M 335 540 Q 600 520 865 540" stroke="#2c0f18" stroke-width="3" fill="none"/>
    <!-- Tufting buttons -->
    <g fill="#210810">
      <circle cx="420" cy="420" r="4"/><circle cx="510" cy="415" r="4"/><circle cx="600" cy="412" r="4"/><circle cx="690" cy="415" r="4"/><circle cx="780" cy="420" r="4"/>
      <circle cx="380" cy="480" r="4"/><circle cx="470" cy="475" r="4"/><circle cx="560" cy="470" r="4"/><circle cx="640" cy="470" r="4"/><circle cx="730" cy="475" r="4"/><circle cx="820" cy="480" r="4"/>
      <circle cx="420" cy="535" r="4"/><circle cx="510" cy="530" r="4"/><circle cx="600" cy="528" r="4"/><circle cx="690" cy="530" r="4"/><circle cx="780" cy="535" r="4"/>
    </g>
    <!-- Left Armrest -->
    <path d="M 270 480 C 270 440, 340 440, 350 510 L 340 660 C 330 680, 260 670, 260 620 Z" fill="#692439" stroke="#3b111e" stroke-width="4"/>
    <!-- Right Armrest -->
    <path d="M 930 480 C 930 440, 860 440, 850 510 L 860 660 C 870 680, 940 670, 940 620 Z" fill="#581e30" stroke="#3b111e" stroke-width="4"/>
    <!-- Main Seat Cushion -->
    <path d="M 280 590 C 310 575, 890 575, 920 590 C 930 645, 910 670, 890 675 L 310 675 C 290 670, 270 645, 280 590 Z" fill="#752940" stroke="#4a1524" stroke-width="4"/>
    <!-- Cushion Creases -->
    <path d="M 595 590 L 595 670" stroke="#421320" stroke-width="4"/>
    <path d="M 430 595 L 420 670" stroke="#421320" stroke-width="3"/>
    <path d="M 765 595 L 775 670" stroke="#421320" stroke-width="3"/>
    <!-- Ornate Turned Wood Legs -->
    <path d="M 305 675 L 295 725 L 315 725 L 320 675 Z" fill="#241410"/>
    <path d="M 880 675 L 870 725 L 890 725 L 895 675 Z" fill="#241410"/>
    <path d="M 590 675 L 585 725 L 605 725 L 600 675 Z" fill="#241410"/>
  </g>

  <!-- ================= CHARACTER 1: FATHER ROBOT (SITTING RIGHT-CENTER) ================= -->
  <!-- Bulky, industrial 1960s steel powerhouse. Over-formal, stiff, wearing an undersized necktie.
       Looking slightly stressed/overwhelmed by family chaos, pressure gauge nearing red. -->
  <g id="father-robot" filter="url(#dropShadow)">
    <!-- Shadow on sofa -->
    <ellipse cx="735" cy="625" rx="145" ry="35" fill="#1f0910" opacity="0.6"/>

    <!-- Dad's Legs / Treads tucked awkwardly -->
    <g id="dad-legs">
      <!-- Left leg (viewer left) -->
      <rect x="635" y="580" width="65" height="110" rx="12" fill="url(#castIronDark)" stroke="#1a1c20" stroke-width="3"/>
      <!-- Accordion rubber knee -->
      <path d="M 630 650 Q 667 640 705 650 Q 667 660 630 650" fill="#111" stroke="#222" stroke-width="2"/>
      <path d="M 630 665 Q 667 655 705 665 Q 667 675 630 665" fill="#111" stroke="#222" stroke-width="2"/>
      <!-- Foot / heavy magnetic boot -->
      <rect x="620" y="690" width="85" height="35" rx="8" fill="url(#castIron)" stroke="#111" stroke-width="3"/>
      <line x1="625" y1="715" x2="700" y2="715" stroke="#111" stroke-width="3"/>

      <!-- Right leg (viewer right) -->
      <rect x="765" y="580" width="65" height="110" rx="12" fill="url(#castIronDark)" stroke="#1a1c20" stroke-width="3"/>
      <path d="M 760 650 Q 797 640 835 650 Q 797 660 760 650" fill="#111" stroke="#222" stroke-width="2"/>
      <path d="M 760 665 Q 797 655 835 665 Q 797 675 760 665" fill="#111" stroke="#222" stroke-width="2"/>
      <!-- Foot -->
      <rect x="755" y="690" width="85" height="35" rx="8" fill="url(#castIron)" stroke="#111" stroke-width="3"/>
      <line x1="760" y1="715" x2="835" y2="715" stroke="#111" stroke-width="3"/>
    </g>

    <!-- Dad's Torso: Heavy Riveted Boiler Tank -->
    <g id="dad-torso">
      <!-- Main torso box/cylinder -->
      <rect x="615" y="340" width="235" height="255" rx="35" fill="url(#castIron)" stroke="#22272e" stroke-width="5"/>
      <!-- Chest Highlight -->
      <path d="M 630 355 Q 732 345 835 355 L 830 395 Q 732 380 630 395 Z" fill="#ffffff" opacity="0.12"/>
      <!-- Industrial Rivets -->
      <g fill="#282d36" stroke="#5d6775" stroke-width="1">
        <circle cx="630" cy="355" r="4"/><circle cx="660" cy="355" r="4"/><circle cx="805" cy="355" r="4"/><circle cx="835" cy="355" r="4"/>
        <circle cx="630" cy="575" r="4"/><circle cx="660" cy="575" r="4"/><circle cx="805" cy="575" r="4"/><circle cx="835" cy="575" r="4"/>
        <circle cx="630" cy="420" r="4"/><circle cx="630" cy="495" r="4"/>
        <circle cx="835" cy="420" r="4"/><circle cx="835" cy="495" r="4"/>
      </g>

      <!-- Chest Grill / Ventilation Slits -->
      <g stroke="#1d2128" stroke-width="4" stroke-linecap="round">
        <line x1="645" y1="520" x2="685" y2="520"/>
        <line x1="645" y1="535" x2="685" y2="535"/>
        <line x1="645" y1="550" x2="685" y2="550"/>
      </g>

      <!-- Dad's Stress Indicator: Pressure Gauge on Chest -->
      <circle cx="780" cy="520" r="32" fill="#fffdec" stroke="#333" stroke-width="4"/>
      <circle cx="780" cy="520" r="28" fill="none" stroke="#ddd" stroke-width="2"/>
      <!-- Gauge dial marks & danger zone (red arc) -->
      <path d="M 770 495 A 25 25 0 0 1 802 525" fill="none" stroke="#e03131" stroke-width="5"/>
      <path d="M 758 525 A 25 25 0 0 1 770 495" fill="none" stroke="#888" stroke-width="3"/>
      <!-- Gauge needle pointing to DANGER / OVERHEATING from awkwardness -->
      <line x1="780" y1="520" x2="798" y2="504" stroke="#c92a2a" stroke-width="3" stroke-linecap="round"/>
      <circle cx="780" cy="520" r="4" fill="#222"/>

      <!-- Awkward Tiny Necktie (stiff red striped clip-on tie) -->
      <polygon points="720,345 745,345 748,358 717,358" fill="#ffffff" stroke="#aaa" stroke-width="1.5"/> <!-- White collar -->
      <polygon points="725,358 740,358 745,372 720,372" fill="#a61e2b"/> <!-- Tie knot -->
      <polygon points="723,372 742,372 748,460 732,480 717,460" fill="#c92a2a" stroke="#7a101b" stroke-width="1.5"/> <!-- Tie body -->
      <!-- Diagonal stripes on tie -->
      <path d="M 723 390 L 742 400 M 720 415 L 744 425 M 718 440 L 747 450" stroke="#fcc2d7" stroke-width="2.5" fill="none"/>
    </g>

    <!-- Dad's Arms & Stiff Posture -->
    <!-- Left arm resting stiffly on his lap, clenching knee -->
    <g id="dad-left-arm">
      <!-- Shoulder ball -->
      <circle cx="615" cy="380" r="24" fill="url(#castIronDark)" stroke="#1e2229" stroke-width="3"/>
      <!-- Upper arm -->
      <path d="M 610 395 C 600 440, 620 480, 645 510" fill="none" stroke="url(#castIron)" stroke-width="26" stroke-linecap="round"/>
      <!-- Elbow hinge bolt -->
      <circle cx="640" cy="505" r="12" fill="#282d36" stroke="#ffe28a" stroke-width="2"/>
      <!-- Forearm & hand clutching his own thigh stiffly -->
      <path d="M 645 510 L 680 540" fill="none" stroke="url(#castIron)" stroke-width="22" stroke-linecap="round"/>
      <!-- Heavy claw fingers -->
      <path d="M 675 530 C 695 535, 705 550, 700 565" fill="none" stroke="#252a32" stroke-width="8" stroke-linecap="round"/>
      <path d="M 685 540 C 705 545, 715 560, 708 575" fill="none" stroke="#3d444f" stroke-width="7" stroke-linecap="round"/>
    </g>

    <!-- Right arm: Arm around Mom, but held rigidly aloft, barely touching her shoulder!
         (The classic awkward hovering hand / hover-hand pose!) -->
    <g id="dad-right-arm-hover">
      <!-- Shoulder ball -->
      <circle cx="850" cy="380" r="24" fill="url(#castIronDark)" stroke="#1e2229" stroke-width="3"/>
      <!-- Upper arm reaching out to Mom (who is sitting to his left/viewer's right? Wait, Mom is at x~450! Dad's arm reaches towards Mom at x~450!)
           Ah! Dad is at x~735, Mom is at x~450! Dad's LEFT arm is towards Mom!
           Let's make Dad's arm reaching towards Mom have the legendary awkward 'Hover Clamp'!
      -->
    </g>

    <!-- Dad's Hover-Clamp Arm (Reaching toward Mom at viewer's left) -->
    <g id="dad-hover-arm">
      <!-- Reaches from Dad's torso across behind/above Mom's shoulder, clamp suspended nervously in mid-air -->
      <path d="M 615 375 C 550 365, 510 360, 485 365" fill="none" stroke="url(#castIron)" stroke-width="24" stroke-linecap="round"/>
      <circle cx="540" cy="365" r="11" fill="#222" stroke="#666" stroke-width="2"/>
      <!-- Forearm extending over Mom's shoulder without actually touching her -->
      <path d="M 485 365 L 450 380" fill="none" stroke="url(#castIron)" stroke-width="18" stroke-linecap="round"/>
      <circle cx="450" cy="380" r="9" fill="#181c22"/>
      <!-- The Awkward Hover-Clamp (open claw floating 2 inches above Mom's polished gold shoulder) -->
      <path d="M 445 372 C 435 360, 415 360, 410 375" fill="none" stroke="#485360" stroke-width="6" stroke-linecap="round"/>
      <path d="M 445 388 C 435 400, 415 400, 410 385" fill="none" stroke="#485360" stroke-width="6" stroke-linecap="round"/>
      <!-- Little nervous tension sparks / hesitation sweat drop made of oil -->
      <path d="M 425 350 C 425 344, 430 338, 430 334 C 430 338, 435 344, 435 350 C 435 354, 431 356, 425 350 Z" fill="#2b5c8f" opacity="0.8"/>
    </g>

    <!-- Dad's Outer Right Arm (resting tense at side) -->
    <g id="dad-outer-arm">
      <path d="M 850 380 C 885 410, 890 480, 860 550" fill="none" stroke="url(#castIron)" stroke-width="24" stroke-linecap="round"/>
      <circle cx="882" cy="455" r="11" fill="#222" stroke="#666" stroke-width="2"/>
      <path d="M 860 550 L 835 590" fill="none" stroke="url(#castIron)" stroke-width="18" stroke-linecap="round"/>
      <path d="M 835 590 C 825 610, 840 625, 855 615" fill="none" stroke="#333" stroke-width="8" stroke-linecap="round"/>
    </g>

    <!-- Dad's Head & Neck -->
    <g id="dad-head">
      <!-- Heavy neck bellows / exhaust pipe -->
      <rect x="710" y="305" width="45" height="40" rx="5" fill="#2a3039" stroke="#111" stroke-width="2"/>
      <line x1="710" y1="315" x2="755" y2="315" stroke="#444" stroke-width="2"/>
      <line x1="710" y1="325" x2="755" y2="325" stroke="#444" stroke-width="2"/>
      <line x1="710" y1="335" x2="755" y2="335" stroke="#444" stroke-width="2"/>

      <!-- Tiny nervous steam escaping from left neck bolt -->
      <path d="M 700 315 Q 685 305 690 295 Q 680 285 690 270" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.35" stroke-linecap="round"/>
      <path d="M 698 322 Q 680 315 682 305" fill="none" stroke="#ffffff" stroke-width="2" opacity="0.25" stroke-linecap="round"/>

      <!-- Head Block: Heavy Retro-Futuristic TV/Box Head -->
      <rect x="655" y="175" width="155" height="135" rx="20" fill="url(#castIron)" stroke="#222830" stroke-width="5"/>
      <!-- Head Visor / Face Plate -->
      <rect x="670" y="195" width="125" height="95" rx="14" fill="#181c22" stroke="#38404d" stroke-width="3"/>

      <!-- Eyes: Stiff, asymmetric, slightly cross-eyed or anxious round lenses -->
      <!-- Left Eye -->
      <circle cx="705" cy="235" r="20" fill="#2a3039" stroke="#5d6878" stroke-width="2.5"/>
      <circle cx="705" cy="235" r="14" fill="#ffdd55" filter="url(#softGlow)"/>
      <circle cx="709" cy="233" r="6" fill="#1b1c20"/> <!-- Pupil looking nervously sideways at wife/kids -->
      <circle cx="712" cy="230" r="2.5" fill="#ffffff"/> <!-- Glint -->
      <!-- Eyebrow: Stiff diagonal metal plate giving an anxious/strained expression -->
      <polygon points="690,206 726,212 725,218 689,212" fill="#444d5a"/>

      <!-- Right Eye -->
      <circle cx="760" cy="235" r="20" fill="#2a3039" stroke="#5d6878" stroke-width="2.5"/>
      <circle cx="760" cy="235" r="14" fill="#ffdd55" filter="url(#softGlow)"/>
      <circle cx="762" cy="233" r="6" fill="#1b1c20"/> <!-- Pupil also darting sideways -->
      <circle cx="765" cy="230" r="2.5" fill="#ffffff"/> <!-- Glint -->
      <!-- Eyebrow: Raised higher in worry -->
      <polygon points="742,216 778,208 779,214 743,222" fill="#444d5a"/>

      <!-- Mouth: Grid of LED speaker slots arranged in a tight, unconvincing, flat/grimace line -->
      <rect x="702" y="267" width="60" height="12" rx="4" fill="#0f1216"/>
      <g fill="#ffc83b">
        <circle cx="712" cy="273" r="2.5"/><circle cx="722" cy="273" r="2.5"/><circle cx="732" cy="273" r="2.5"/><circle cx="742" cy="273" r="2.5"/><circle cx="752" cy="273" r="2.5"/>
      </g>

      <!-- Dad's Antenna: One straight, one bent awkwardly from garage door accident -->
      <line x1="685" y1="175" x2="675" y2="135" stroke="#535c68" stroke-width="4" stroke-linecap="round"/>
      <circle cx="673" cy="130" r="6" fill="#d4af37"/>

      <line x1="775" y1="175" x2="785" y2="148" stroke="#535c68" stroke-width="4" stroke-linecap="round"/>
      <line x1="785" y1="148" x2="805" y2="152" stroke="#535c68" stroke-width="4" stroke-linecap="round"/> <!-- Bent angle -->
      <circle cx="810" cy="153" r="6" fill="#c92a2a"/> <!-- Blinking red error diode -->
    </g>
  </g>

  <!-- ================= CHARACTER 2: MOTHER ROBOT (SITTING LEFT-CENTER) ================= -->
  <!-- 1950s Art-Deco / Mid-Century streamlined aesthetic: Polished brass/gold, hourglass chassis,
       pearl necklace made of ball bearings, prim and proper posture, frozen "pageant smile" screen,
       rigidly pretending everything is perfectly under control despite absolute chaos. -->
  <g id="mother-robot" filter="url(#dropShadow)">
    <!-- Shadow on sofa -->
    <ellipse cx="450" cy="625" rx="130" ry="32" fill="#1f0910" opacity="0.6"/>

    <!-- Mom's Legs: Slender brass tubes crossed demurely and primly at ankles -->
    <g id="mom-legs">
      <!-- Upper thighs in a sleek champagne bell skirt chassis -->
      <path d="M 380 540 Q 450 535 520 540 L 535 620 Q 450 635 365 620 Z" fill="url(#brassDark)" stroke="#4e3b0d" stroke-width="3"/>
      <!-- Lower legs crossed -->
      <!-- Right leg crossed over left -->
      <path d="M 435 620 C 440 660, 455 690, 480 730" fill="none" stroke="url(#brassGrad)" stroke-width="16" stroke-linecap="round"/>
      <circle cx="455" cy="685" r="9" fill="#d4af37" stroke="#333" stroke-width="2"/> <!-- Ornate knee joint -->
      <!-- Dainty retro chrome/brass high-heel foot -->
      <path d="M 475 725 L 505 730 L 495 745 L 470 740 Z" fill="#aa820a" stroke="#4e3b0d" stroke-width="2"/>
      <line x1="495" y1="730" x2="492" y2="750" stroke="#775d0e" stroke-width="3"/> <!-- Heel spike -->

      <!-- Left leg underneath -->
      <path d="M 420 620 C 415 660, 410 690, 420 735" fill="none" stroke="url(#brassDark)" stroke-width="14" stroke-linecap="round"/>
      <path d="M 412 730 L 435 735 L 428 748 L 408 742 Z" fill="#775d0e"/>
    </g>

    <!-- Mom's Torso: Hourglass Art-Deco Body -->
    <g id="mom-torso">
      <!-- Lower torso / waist -->
      <path d="M 405 450 Q 450 460 495 450 L 515 550 Q 450 560 385 550 Z" fill="url(#brassGrad)" stroke="#6d540f" stroke-width="3.5"/>
      <!-- Cinched waist ring -->
      <ellipse cx="450" cy="455" rx="42" ry="10" fill="#3a2a07" stroke="#d4af37" stroke-width="2"/>

      <!-- Upper Chest: Curved streamlined bustier -->
      <path d="M 390 365 C 390 345, 510 345, 510 365 C 520 415, 485 455, 450 455 C 415 455, 380 415, 390 365 Z" fill="url(#brassGrad)" stroke="#6d540f" stroke-width="4"/>
      <!-- Gleaming polish reflection curve -->
      <path d="M 405 365 C 415 410, 430 435, 442 445" fill="none" stroke="#fff" stroke-width="4" opacity="0.6" stroke-linecap="round"/>

      <!-- Pearl Necklace: Chrome ball bearings strung tightly around her neck -->
      <g filter="url(#dropShadow)">
        <path d="M 415 352 Q 450 375 485 352" fill="none" stroke="#888" stroke-width="2"/>
        <circle cx="417" cy="353" r="6" fill="url(#pearlGrad)"/>
        <circle cx="427" cy="359" r="6.5" fill="url(#pearlGrad)"/>
        <circle cx="438" cy="363" r="7" fill="url(#pearlGrad)"/>
        <circle cx="450" cy="365" r="7.5" fill="url(#pearlGrad)"/> <!-- Center pearl -->
        <circle cx="462" cy="363" r="7" fill="url(#pearlGrad)"/>
        <circle cx="473" cy="359" r="6.5" fill="url(#pearlGrad)"/>
        <circle cx="483" cy="353" r="6" fill="url(#pearlGrad)"/>
      </g>
    </g>

    <!-- Mom's Arms: Primly folded hands on lap, fingers rigidly locked together -->
    <g id="mom-arms">
      <!-- Right shoulder & arm -->
      <circle cx="390" cy="375" r="18" fill="url(#brassDark)" stroke="#4e3b0d" stroke-width="2.5"/>
      <path d="M 385 385 C 370 430, 395 480, 420 495" fill="none" stroke="url(#brassGrad)" stroke-width="16" stroke-linecap="round"/>
      <!-- Left shoulder & arm -->
      <circle cx="510" cy="375" r="18" fill="url(#brassDark)" stroke="#4e3b0d" stroke-width="2.5"/>
      <path d="M 515 385 C 530 430, 505 480, 475 495" fill="none" stroke="url(#brassGrad)" stroke-width="16" stroke-linecap="round"/>
      <!-- Clasped hands on lap (rigidly polite grip) -->
      <ellipse cx="448" cy="498" rx="28" ry="15" fill="url(#brassDark)" stroke="#d4af37" stroke-width="2"/>
      <!-- Delicately articulated chrome fingers interlocking tensely -->
      <path d="M 432 492 C 445 498, 455 498, 465 492" fill="none" stroke="#fff" stroke-width="2"/>
      <path d="M 432 500 C 445 506, 455 506, 465 500" fill="none" stroke="#fff" stroke-width="2"/>
    </g>

    <!-- Mom's Head & Hair -->
    <g id="mom-head">
      <!-- Slender fluted neck -->
      <path d="M 438 315 L 438 350 L 462 350 L 462 315 Z" fill="url(#brassDark)" stroke="#3a2a07" stroke-width="2"/>
      <ellipse cx="450" cy="330" rx="12" ry="4" fill="#d4af37"/>

      <!-- Sleek 1950s "Hairdo" made of spun polished brass curls / vacuum tube dome -->
      <!-- Coiffed vintage hairstyle helmet -->
      <path d="M 395 245 C 390 170, 510 170, 505 245 C 525 240, 530 290, 495 295 C 490 270, 410 270, 405 295 C 370 290, 375 240, 395 245 Z" fill="url(#brassDark)" stroke="#4e3b0d" stroke-width="3"/>
      <!-- Hair swirls / ribbed art-deco crest -->
      <path d="M 410 220 Q 450 190 490 220" fill="none" stroke="#ffe28a" stroke-width="5" stroke-linecap="round"/>
      <path d="M 420 200 Q 450 180 480 200" fill="none" stroke="#ffe28a" stroke-width="4" stroke-linecap="round"/>
      <circle cx="450" cy="180" r="7" fill="#ffe28a"/> <!-- Top decorative hair sphere -->

      <!-- Head Face Capsule -->
      <ellipse cx="450" cy="255" rx="50" ry="45" fill="url(#brassGrad)" stroke="#4e3b0d" stroke-width="3.5"/>
      <!-- Glossy Face Screen Insert -->
      <ellipse cx="450" cy="257" rx="38" ry="32" fill="#141a24" stroke="#82661d" stroke-width="2.5"/>

      <!-- Mom's Eyes: Glowing, unnervingly wide, desperate pleasantness -->
      <!-- Cat-eye winged frames on her screen -->
      <path d="M 420 240 Q 432 230 442 245 Q 430 248 420 240 Z" fill="#3ddc97" opacity="0.15"/>
      <path d="M 480 240 Q 468 230 458 245 Q 470 248 480 240 Z" fill="#3ddc97" opacity="0.15"/>

      <!-- Eyelashes / decorative winged ridges -->
      <line x1="420" y1="238" x2="412" y2="232" stroke="#d4af37" stroke-width="2"/>
      <line x1="422" y1="234" x2="416" y2="226" stroke="#d4af37" stroke-width="2"/>
      <line x1="478" y1="238" x2="486" y2="232" stroke="#d4af37" stroke-width="2"/>
      <line x1="476" y1="234" x2="482" y2="226" stroke="#d4af37" stroke-width="2"/>

      <!-- Glowing Cyan/Mint Eyes (forced wide, over-enthusiastic) -->
      <ellipse cx="433" cy="246" rx="9" ry="11" fill="#4ef2bb" filter="url(#softGlow)"/>
      <circle cx="434" cy="245" r="4" fill="#082b1d"/>
      <circle cx="436" cy="242" r="2" fill="#ffffff"/>

      <ellipse cx="467" cy="246" rx="9" ry="11" fill="#4ef2bb" filter="url(#softGlow)"/>
      <circle cx="466" cy="245" r="4" fill="#082b1d"/>
      <circle cx="464" cy="242" r="2" fill="#ffffff"/>

      <!-- Mom's Smile: LED matrix forced into an overly wide, twitching pageant smile! -->
      <path d="M 432 270 Q 450 286 468 270" fill="none" stroke="#4ef2bb" stroke-width="3" stroke-linecap="round" filter="url(#softGlow)"/>
      <!-- Rosy Cheeks (warm vacuum glow diodes) -->
      <circle cx="422" cy="265" r="5" fill="#ff5e7e" opacity="0.6" filter="url(#softGlow)"/>
      <circle cx="478" cy="265" r="5" fill="#ff5e7e" opacity="0.6" filter="url(#softGlow)"/>
    </g>
  </g>

  <!-- ================= CHARACTER 3: EMO TEENAGER ROBOT (STANDING FAR RIGHT) ================= -->
  <!-- Slender, tall, slouching away from the family, arms crossed petulantly.
       Matte black / charcoal carbon fiber chassis with neon magenta/purple accents.
       One optical lens covered by an angled metal "emo fringe" / swoop bang plate.
       Looking down and away at a retro portable audio tape/hologram device or pure teen angst. -->
  <g id="emo-teen" filter="url(#dropShadow)" transform="translate(10, 0)">
    <!-- Floor Shadow -->
    <ellipse cx="985" cy="740" rx="65" ry="18" fill="#0c0712" opacity="0.75"/>

    <!-- Slouching legs (one knee bent insouciantly) -->
    <g id="teen-legs">
      <!-- Right leg straight -->
      <line x1="995" y1="480" x2="1010" y2="730" stroke="url(#emoBody)" stroke-width="22" stroke-linecap="round"/>
      <circle cx="1002" cy="590" r="12" fill="#18181f" stroke="#b827fc" stroke-width="2"/> <!-- Purple joint -->
      <!-- Clunky combat boot / chunky cyber high-top -->
      <polygon points="995,715 1035,720 1045,742 985,742" fill="#121217" stroke="#333" stroke-width="2"/>
      <line x1="1000" y1="738" x2="1040" y2="738" stroke="#b827fc" stroke-width="3"/> <!-- Neon sole trim -->

      <!-- Left leg angled / knee popped out in bored rebellion -->
      <path d="M 960 480 L 935 595 L 965 725" fill="none" stroke="url(#emoBody)" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="935" cy="595" r="11" fill="#18181f" stroke="#b827fc" stroke-width="2"/>
      <!-- Boot angled -->
      <polygon points="950,710 985,725 978,744 938,735" fill="#121217" stroke="#333" stroke-width="2"/>
      <line x1="945" y1="735" x2="978" y2="742" stroke="#b827fc" stroke-width="3"/>
    </g>

    <!-- Torso: Leaning/hunched spine, black hoodie silhouette -->
    <g id="teen-torso">
      <!-- Slouching spine curve -->
      <path d="M 985 340 Q 995 410 975 490" fill="none" stroke="url(#emoBody)" stroke-width="50" stroke-linecap="round"/>
      <!-- Chest panel with distressed / emo stencil glitch graphic -->
      <rect x="955" y="365" width="42" height="60" rx="8" fill="#14141a" stroke="#252530" stroke-width="2"/>
      <!-- Little cracked heart / skull wire graphic -->
      <path d="M 968 395 C 963 388, 974 380, 976 388 C 978 380, 989 388, 984 395 L 976 405 Z" fill="#b827fc" opacity="0.8"/>
      <line x1="973" y1="384" x2="980" y2="402" stroke="#121217" stroke-width="1.5"/> <!-- Crack in heart -->

      <!-- Loose hanging auxiliary cables (like hoodie drawstrings) dangling down -->
      <path d="M 968 348 Q 962 385 965 435" fill="none" stroke="#222" stroke-width="3"/>
      <circle cx="965" cy="437" r="3" fill="#b827fc"/>
      <path d="M 978 348 Q 973 395 975 448" fill="none" stroke="#222" stroke-width="3"/>
      <circle cx="975" cy="450" r="3" fill="#b827fc"/>
    </g>

    <!-- Arms: Tightly crossed over chest in defensive, aloof posture -->
    <g id="teen-arms">
      <!-- Slouching shoulders -->
      <circle cx="950" cy="350" r="14" fill="#202028"/>
      <circle cx="1015" cy="355" r="14" fill="#202028"/>
      <!-- Right arm crossing inward -->
      <path d="M 1015 355 C 1025 400, 990 425, 940 425" fill="none" stroke="url(#emoBody)" stroke-width="18" stroke-linecap="round"/>
      <!-- Left arm folded under -->
      <path d="M 950 350 C 935 395, 960 435, 1005 435" fill="none" stroke="url(#emoBody)" stroke-width="18" stroke-linecap="round"/>
      <!-- Gloved / matte black hand tucked under armpit -->
      <ellipse cx="942" cy="422" rx="10" ry="7" fill="#111" stroke="#333" stroke-width="1.5"/>
      <ellipse cx="1005" cy="432" rx="10" ry="7" fill="#111" stroke="#333" stroke-width="1.5"/>
      <!-- Studded wristband / spiky bolt cuff on wrist -->
      <g fill="#c0c0c0">
        <polygon points="985,420 990,414 995,420"/>
        <polygon points="995,421 1000,415 1005,421"/>
      </g>
    </g>

    <!-- Head & Angsty Swoop Fringe Hair -->
    <!-- Head tilted down and turned AWAY from the happy parents toward the right edge -->
    <g id="teen-head" transform="rotate(8, 985, 290)">
      <!-- Neck with spiked collar -->
      <rect x="975" y="315" width="20" height="28" rx="4" fill="#1c1c24"/>
      <rect x="972" y="325" width="26" height="8" rx="2" fill="#0d0d12" stroke="#b827fc" stroke-width="1.5"/>
      <!-- Spikes on collar -->
      <polygon points="973,329 967,329 970,332" fill="#fff"/>
      <polygon points="997,329 1003,329 1000,332" fill="#fff"/>

      <!-- Cylindrical/geometric angular head unit -->
      <rect x="950" y="225" width="70" height="95" rx="16" fill="url(#emoBody)" stroke="#16161e" stroke-width="3.5"/>
      <rect x="955" y="240" width="55" height="65" rx="10" fill="#0d0d12"/>

      <!-- Eye: Only ONE eye visible! Half-lidded, glowing moody magenta, rolling eyes upward/away -->
      <!-- Left eye hidden by bangs! Right eye visible: -->
      <path d="M 985 260 Q 998 256 1005 262" stroke="#ff2a8d" stroke-width="4" stroke-linecap="round" fill="none" filter="url(#neonGlow)"/>
      <circle cx="994" cy="265" r="3" fill="#ff2a8d" filter="url(#softGlow)"/>

      <!-- Mouth: Dissatisfied flat slanting slash -->
      <line x1="978" y1="290" x2="996" y2="287" stroke="#444" stroke-width="2.5" stroke-linecap="round"/>

      <!-- Signature EMO SWOOP BANGS: Swept sheet-metal plate covering one eye in dramatic asymmetric swoop -->
      <path d="M 945 220 C 970 215, 1015 215, 1025 240 C 1030 255, 1000 270, 970 288 C 955 298, 948 280, 950 250 Z" fill="#1c1b24" stroke="#b827fc" stroke-width="2.5"/>
      <!-- Hair highlight streak (vibrant hot purple/magenta streak) -->
      <path d="M 955 225 Q 995 225 978 280" fill="none" stroke="#ff007f" stroke-width="4" stroke-linecap="round" filter="url(#softGlow)"/>

      <!-- Chunky Over-Ear Cyber Headphones clamped on head (tuned out from family!) -->
      <ellipse cx="945" cy="265" rx="9" ry="24" fill="#0c0c10" stroke="#ff2a8d" stroke-width="2.5"/>
      <path d="M 945 240 C 950 195, 1010 195, 1020 245" fill="none" stroke="#252530" stroke-width="7"/>
    </g>
  </g>

  <!-- ================= CHARACTER 4: NERD / MIDDLE-CHILD ROBOT (STANDING LEFT) ================= -->
  <!-- Over-eager, dorky, 1980s beige box / early PC aesthetic.
       Giant thick bottle-glass magnifying spectacles over a flickering terminal screen.
       Dorky clip-on bowtie / pocket protector full of screwdrivers.
       Standing uncomfortably close to Mom, trying desperately to stand up straight and smile for the camera,
       holding a completely irrelevant science fair award trophy or circuit board. -->
  <g id="nerd-child" filter="url(#dropShadow)">
    <!-- Floor Shadow -->
    <ellipse cx="230" cy="740" rx="55" ry="16" fill="#0c0712" opacity="0.7"/>

    <!-- Dorky legs: Thin, telescoping ribbed radio-antenna legs standing pigeon-toed! (awkward stance) -->
    <g id="nerd-legs">
      <!-- Left leg pigeon-toed -->
      <path d="M 210 570 L 195 650 L 210 730" fill="none" stroke="#7e7765" stroke-width="12" stroke-linecap="round"/>
      <circle cx="195" cy="650" r="8" fill="#524d3f"/>
      <!-- Square beige sneaker foot turned inward -->
      <polygon points="195,725 230,720 235,738 190,740" fill="url(#beigePlastic)" stroke="#524d3f" stroke-width="2"/>
      <line x1="200" y1="735" x2="230" y2="730" stroke="#c0392b" stroke-width="3"/> <!-- Red sneaker stripe -->

      <!-- Right leg pigeon-toed -->
      <path d="M 250 570 L 260 650 L 245 730" fill="none" stroke="#7e7765" stroke-width="12" stroke-linecap="round"/>
      <circle cx="260" cy="650" r="8" fill="#524d3f"/>
      <!-- Foot turned inward towards the other foot! (Ultimate dork stance) -->
      <polygon points="260,725 225,720 220,738 265,740" fill="url(#beigePlastic)" stroke="#524d3f" stroke-width="2"/>
      <line x1="255" y1="735" x2="225" y2="730" stroke="#c0392b" stroke-width="3"/>
    </g>

    <!-- Torso: Retro 1980s Desktop Computer Tower Body -->
    <g id="nerd-torso">
      <rect x="180" y="420" width="105" height="155" rx="14" fill="url(#beigePlastic)" stroke="#8e836f" stroke-width="4"/>
      <!-- Disk Drive slots (3.5" and 5.25" floppy drives!) -->
      <rect x="195" y="440" width="75" height="16" rx="2" fill="#363229"/>
      <line x1="205" y1="448" x2="260" y2="448" stroke="#111" stroke-width="2"/> <!-- Drive slot -->
      <circle cx="264" cy="448" r="2" fill="#2ecc71"/> <!-- Activity LED -->

      <rect x="195" y="465" width="75" height="16" rx="2" fill="#363229"/>
      <line x1="205" y1="473" x2="260" y2="473" stroke="#111" stroke-width="2"/>
      <circle cx="264" cy="473" r="2" fill="#e74c3c"/>

      <!-- Pocket Protector on chest! (Plastic sleeve holding pens/tuning forks/antennae) -->
      <rect x="195" y="505" width="45" height="50" rx="3" fill="#ffffff" opacity="0.85" stroke="#aaa" stroke-width="1.5"/>
      <polygon points="195,505 240,505 240,518 217,525 195,518" fill="#e0e0e0"/>
      <!-- Pens / Screwdrivers protruding -->
      <line x1="203" y1="507" x2="203" y2="492" stroke="#e74c3c" stroke-width="4" stroke-linecap="round"/>
      <line x1="212" y1="507" x2="212" y2="488" stroke="#3498db" stroke-width="4" stroke-linecap="round"/>
      <line x1="222" y1="507" x2="222" y2="495" stroke="#f1c40f" stroke-width="3" stroke-linecap="round"/>
      <line x1="231" y1="507" x2="231" y2="490" stroke="#2ecc71" stroke-width="3" stroke-linecap="round"/>

      <!-- Dorky Polka-dot Bowtie at collar -->
      <polygon points="218,422 248,422 242,434 224,434" fill="#ffffff"/>
      <circle cx="233" cy="428" r="5" fill="#3498db"/>
      <polygon points="212,422 233,428 212,435" fill="#2980b9"/>
      <polygon points="254,422 233,428 254,435" fill="#2980b9"/>
      <!-- Dots on bowtie -->
      <circle cx="220" cy="428" r="1.5" fill="#fff"/><circle cx="246" cy="428" r="1.5" fill="#fff"/>
    </g>

    <!-- Arms: Proudly presenting an awkward project / holding hands rigidly at attention -->
    <g id="nerd-arms">
      <!-- Right arm stiffly down at seam -->
      <path d="M 180 435 C 160 480, 160 520, 172 555" fill="none" stroke="#9e947f" stroke-width="12" stroke-linecap="round"/>
      <!-- Left arm bent upward, proudly clutching an old floppy disk or circuit board to show Mom -->
      <path d="M 285 435 C 310 470, 310 500, 290 525" fill="none" stroke="#9e947f" stroke-width="12" stroke-linecap="round"/>
      <circle cx="290" cy="525" r="7" fill="#524d3f"/>
      <!-- Green PCB circuit board held up proudly -->
      <rect x="282" y="505" width="28" height="38" rx="2" fill="#1b5e20" stroke="#0d3310" stroke-width="1.5"/>
      <line x1="286" y1="515" x2="304" y2="515" stroke="#ffd700" stroke-width="1.5"/>
      <line x1="286" y1="525" x2="300" y2="525" stroke="#ffd700" stroke-width="1.5"/>
      <line x1="294" y1="515" x2="294" y2="535" stroke="#ffd700" stroke-width="1.5"/>
      <circle cx="295" cy="535" r="3" fill="#222"/> <!-- Tiny microchip -->
      <!-- Clamping gripper fingers clutching the PCB -->
      <path d="M 285 530 C 275 525, 275 538, 285 535" stroke="#333" stroke-width="3" fill="none"/>
    </g>

    <!-- Head: CRT Monitor Head with Giant Thick Nerd Glasses -->
    <g id="nerd-head">
      <!-- Neck pivot spindle -->
      <rect x="222" y="395" width="22" height="28" rx="4" fill="#6d6554"/>

      <!-- CRT Monitor Casing -->
      <rect x="165" y="275" width="135" height="122" rx="22" fill="url(#beigePlastic)" stroke="#8e836f" stroke-width="4"/>
      <!-- Curved CRT screen with scanlines -->
      <rect x="178" y="288" width="108" height="95" rx="14" fill="url(#crtScreen)" stroke="#1a3d24" stroke-width="3"/>

      <!-- Scanline lines across CRT screen -->
      <g stroke="#26633d" stroke-width="1" opacity="0.4">
        <line x1="180" y1="300" x2="284" y2="300"/>
        <line x1="180" y1="315" x2="284" y2="315"/>
        <line x1="180" y1="330" x2="284" y2="330"/>
        <line x1="180" y1="345" x2="284" y2="345"/>
        <line x1="180" y1="360" x2="284" y2="360"/>
        <line x1="180" y1="375" x2="284" y2="375"/>
      </g>

      <!-- Giant Thick Round Horn-Rimmed Nerd Glasses with white bridge tape! -->
      <g id="nerd-glasses" filter="url(#dropShadow)">
        <!-- Left Lens (Viewer's left) -->
        <circle cx="208" cy="332" r="24" fill="#ffffff" fill-opacity="0.25" stroke="#111" stroke-width="6"/>
        <circle cx="208" cy="332" r="21" fill="none" stroke="#222" stroke-width="2"/>
        <circle cx="208" cy="332" r="16" fill="#00ff66" opacity="0.85" filter="url(#softGlow)"/> <!-- Glowing CRT eye phosphor -->
        <circle cx="208" cy="332" r="6" fill="#05240f"/> <!-- Pupil staring intently into camera -->
        <circle cx="211" cy="329" r="3" fill="#ffffff"/> <!-- Glint -->
        <!-- Glare diagonal across lens -->
        <path d="M 194 322 L 204 316 M 198 335 L 216 322" stroke="#ffffff" stroke-width="2.5" opacity="0.7" stroke-linecap="round"/>

        <!-- Right Lens (Viewer's right) -->
        <circle cx="258" cy="332" r="24" fill="#ffffff" fill-opacity="0.25" stroke="#111" stroke-width="6"/>
        <circle cx="258" cy="332" r="21" fill="none" stroke="#222" stroke-width="2"/>
        <circle cx="258" cy="332" r="16" fill="#00ff66" opacity="0.85" filter="url(#softGlow)"/>
        <circle cx="258" cy="332" r="6" fill="#05240f"/>
        <circle cx="261" cy="329" r="3" fill="#ffffff"/>
        <!-- Glare -->
        <path d="M 244 322 L 254 316 M 248 335 L 266 322" stroke="#ffffff" stroke-width="2.5" opacity="0.7" stroke-linecap="round"/>

        <!-- Eyeglass Bridge: WRAPPED IN WHITE MASKING TAPE (classic nerd trope!) -->
        <rect x="228" y="328" width="10" height="8" rx="1" fill="#fff" stroke="#d5d5d5" stroke-width="1"/>
        <line x1="230" y1="329" x2="230" y2="335" stroke="#bbb" stroke-width="1"/>
        <line x1="235" y1="329" x2="235" y2="335" stroke="#bbb" stroke-width="1"/>
        <!-- Frame temples -->
        <line x1="184" y1="332" x2="167" y2="325" stroke="#111" stroke-width="4"/>
        <line x1="282" y1="332" x2="298" y2="325" stroke="#111" stroke-width="4"/>
      </g>

      <!-- Nerd Mouth: Over-enthusiastic buck-toothed / chevron smile pixelated on screen -->
      <polygon points="228,368 238,368 238,375 228,375" fill="#ffffff" stroke="#00ff66" stroke-width="1"/> <!-- Buck tooth 1 -->
      <polygon points="238,368 248,368 248,375 238,375" fill="#ffffff" stroke="#00ff66" stroke-width="1"/> <!-- Buck tooth 2 -->
      <path d="M 220 368 Q 238 376 256 368" stroke="#00ff66" stroke-width="2.5" fill="none" filter="url(#softGlow)"/>

      <!-- Twin Telescoping Rabbit-Ear Antennae sticking up at crooked angle -->
      <line x1="205" y1="275" x2="185" y2="215" stroke="#a09785" stroke-width="3" stroke-linecap="round"/>
      <circle cx="183" cy="212" r="5" fill="#c0392b"/>

      <line x1="260" y1="275" x2="280" y2="225" stroke="#a09785" stroke-width="3" stroke-linecap="round"/>
      <circle cx="282" cy="222" r="5" fill="#3498db"/>
    </g>
  </g>

  <!-- ================= CHARACTER 5: HYPERACTIVE TODDLER / BABY BOT (CENTER FOREGROUND) ================= -->
  <!-- Sitting directly in front on the ornate rug between Dad and Mom's knees, completely oblivious
       to photo dignity. Made of colorful Fisher-Price style plastic spheres and stamped tin.
       Head on a wobbly spring, tilted sideways at 30 degrees. Spilling oil / battery juice or
       clutching a wrench/toy screwdriver, spinning gears on chest. Pure chaotic toddler energy. -->
  <g id="toddler-bot" filter="url(#dropShadow)" transform="translate(565, 590)">
    <!-- Toddler Rug Shadow -->
    <ellipse cx="25" cy="180" rx="60" ry="18" fill="#150810" opacity="0.6"/>

    <!-- Toddler Little Caterpillar Wheels / Tiny Chubby Legs splayed out on rug -->
    <g id="baby-legs">
      <!-- Left chubby foot splayed out -->
      <ellipse cx="-30" cy="170" rx="22" ry="14" fill="url(#toddlerYellow)" stroke="#b37d00" stroke-width="2.5"/>
      <circle cx="-40" cy="170" r="5" fill="#333"/>
      <circle cx="-25" cy="170" r="5" fill="#333"/>
      <!-- Right chubby foot splayed out -->
      <ellipse cx="80" cy="170" rx="22" ry="14" fill="url(#toddlerYellow)" stroke="#b37d00" stroke-width="2.5"/>
      <circle cx="70" cy="170" r="5" fill="#333"/>
      <circle cx="85" cy="170" r="5" fill="#333"/>
    </g>

    <!-- Toddler Body: Round bright yellow / red sphere / dome torso -->
    <g id="baby-torso">
      <ellipse cx="25" cy="120" rx="48" ry="44" fill="url(#toddlerYellow)" stroke="#a16f00" stroke-width="3.5"/>
      <!-- Belly Panel: Rotating primary-colored toy gears -->
      <circle cx="25" cy="122" rx="26" ry="26" fill="#1b2a4a" stroke="#d4af37" stroke-width="2"/>
      <!-- Colorful spinning gears on belly -->
      <!-- Big Blue Gear -->
      <g transform="translate(18, 116)">
        <circle cx="0" cy="0" r="14" fill="#00a8ff" stroke="#0077b6" stroke-width="2"/>
        <rect x="-3" y="-16" width="6" height="32" fill="#0077b6"/>
        <rect x="-16" y="-3" width="32" height="6" fill="#0077b6"/>
        <circle cx="0" cy="0" r="4" fill="#fff"/>
      </g>
      <!-- Small Red Interlocking Gear -->
      <g transform="translate(35, 130)">
        <circle cx="0" cy="0" r="10" fill="#ff4757" stroke="#b31220" stroke-width="1.5"/>
        <rect x="-2" y="-12" width="4" height="24" fill="#b31220"/>
        <rect x="-12" y="-2" width="24" height="4" fill="#b31220"/>
        <circle cx="0" cy="0" r="3" fill="#fff"/>
      </g>
    </g>

    <!-- Toddler Chubby Little Arms waving wildly -->
    <g id="baby-arms">
      <!-- Left arm reaching up toward Mom's dress/knees -->
      <path d="M -15 110 C -40 100, -55 75, -60 55" fill="none" stroke="url(#toddlerBlue)" stroke-width="14" stroke-linecap="round"/>
      <circle cx="-62" cy="52" r="9" fill="#ff4757"/> <!-- Red ball fist -->
      <!-- Clutched in fist: An oversized steel wrench twice its size! -->
      <g transform="translate(-65, 48) rotate(-40)">
        <rect x="-6" y="-35" width="12" height="70" rx="3" fill="url(#chrome)" stroke="#666" stroke-width="1.5"/>
        <!-- Wrench jaws -->
        <path d="M -14 -35 L 14 -35 L 14 -48 L 4 -48 L 4 -40 L -4 -40 L -4 -48 L -14 -48 Z" fill="url(#chrome)" stroke="#555" stroke-width="1.5"/>
      </g>

      <!-- Right arm splashing/banging on the floor -->
      <path d="M 65 110 C 85 120, 100 135, 105 160" fill="none" stroke="url(#toddlerBlue)" stroke-width="14" stroke-linecap="round"/>
      <circle cx="106" cy="162" r="9" fill="#ff4757"/>
    </g>

    <!-- Baby's Neck: A WOBBLY LOOSE COILED SPRING! (Explains the chaotic head tilt) -->
    <g id="baby-spring-neck">
      <path d="M 25 76 Q 35 70 20 64 Q 35 58 20 52 Q 35 46 22 40" fill="none" stroke="#777" stroke-width="5" stroke-linecap="round"/>
    </g>

    <!-- Baby Head: Bolted sphere, tilted wildly at a 25-degree angle -->
    <g id="baby-head" transform="translate(22, 35) rotate(-22)">
      <!-- Spherical fishbowl / bubble dome head -->
      <circle cx="0" cy="0" r="34" fill="url(#chrome)" stroke="#4a5568" stroke-width="3"/>
      <!-- Face visor screen -->
      <circle cx="0" cy="0" r="26" fill="#111c24" stroke="#e0e0e0" stroke-width="2"/>

      <!-- Giant Dials / Googly Eyes -->
      <!-- Left Eye: Wide open spiral dizzy pupil -->
      <circle cx="-10" cy="-4" r="11" fill="#fff" stroke="#222" stroke-width="1.5"/>
      <!-- Hypno / toddler spiral pupil -->
      <path d="M -10 -4 m -7,0 a 7,7 0 1,0 14,0 a 7,7 0 1,0 -14,0 m 3,0 a 4,4 0 1,0 8,0 a 4,4 0 1,0 -8,0" fill="none" stroke="#2e86de" stroke-width="1.8"/>

      <!-- Right Eye: Cross-eyed or star pupil -->
      <circle cx="12" cy="-4" r="11" fill="#fff" stroke="#222" stroke-width="1.5"/>
      <polygon points="12,-10 14,-6 18,-6 15,-3 16,1 12,-1 8,1 9,-3 6,-6 10,-6" fill="#ff9f43"/>
      <circle cx="12" cy="-4" r="3" fill="#222"/>

      <!-- Open laughing/shrieking mouth diode -->
      <path d="M -8 11 Q 0 22 10 11 Z" fill="#ff4757" stroke="#333" stroke-width="1.5"/>
      <polygon points="-3,11 3,11 0,15" fill="#ffffff"/> <!-- Single baby pixel tooth! -->

      <!-- Teletubby/Baby Propeller Beanie Antenna on head! Spinning joyously -->
      <line x1="0" y1="-34" x2="0" y2="-48" stroke="#333" stroke-width="3"/>
      <!-- Spinning twin rotor blades with motion swoosh -->
      <ellipse cx="0" cy="-49" rx="18" ry="4" fill="#ffdd59" stroke="#d4ac0d" stroke-width="1.5" transform="rotate(15, 0, -49)"/>
      <circle cx="0" cy="-49" r="3" fill="#eb3b5a"/>
      <path d="M -22 -48 C -15 -55, 15 -55, 22 -48" fill="none" stroke="#ffeaa7" stroke-width="1" stroke-dasharray="2,2"/>
    </g>

    <!-- Little Puddle of Machine Oil Leaking from Diaper / Chassis (Classic awkward family baby accident!) -->
    <ellipse cx="30" cy="178" rx="28" ry="8" fill="#122533" opacity="0.8"/>
    <ellipse cx="38" cy="180" rx="14" ry="4" fill="#1b3d54" opacity="0.9"/>
    <!-- Little rainbow sheen on oil puddle -->
    <path d="M 20 178 Q 35 174 48 178" fill="none" stroke="#8854d0" stroke-width="2" opacity="0.6"/>
    <path d="M 25 180 Q 38 177 44 180" fill="none" stroke="#20bf6b" stroke-width="1.5" opacity="0.6"/>
  </g>

  <!-- ================= CHARACTER 6: THE FAMILY PET (ROBOT DOG / TOASTER HOUND - FAR LEFT) ================= -->
  <!-- Made from a retro chrome toaster body with vacuum tube tail, slinky neck,
       one ear standing up and one flopped down, wagging antenna tail sparking,
       pantingly looking up at Mom or Dad with toast popping out of its back! -->
  <g id="pet-robot" filter="url(#dropShadow)" transform="translate(70, 630)">
    <!-- Floor Shadow -->
    <ellipse cx="55" cy="115" rx="55" ry="14" fill="#0c0712" opacity="0.65"/>

    <!-- Doggy Legs: Four little piston legs -->
    <g id="dog-legs">
      <!-- Back legs -->
      <line x1="85" y1="65" x2="92" y2="108" stroke="#4a5568" stroke-width="8" stroke-linecap="round"/>
      <circle cx="95" cy="110" r="6" fill="#1a202c"/>
      <line x1="70" y1="65" x2="75" y2="106" stroke="#2d3748" stroke-width="8" stroke-linecap="round"/>
      <circle cx="78" cy="108" r="6" fill="#1a202c"/>

      <!-- Front legs -->
      <line x1="25" y1="65" x2="20" y2="108" stroke="#4a5568" stroke-width="8" stroke-linecap="round"/>
      <circle cx="18" cy="110" r="6" fill="#1a202c"/>
      <line x1="40" y1="65" x2="36" y2="106" stroke="#2d3748" stroke-width="8" stroke-linecap="round"/>
      <circle cx="34" cy="108" r="6" fill="#1a202c"/>
    </g>

    <!-- Dog Body: Two-Slot 1950s Art-Deco Chrome Toaster -->
    <g id="dog-torso">
      <rect x="20" y="25" width="75" height="48" rx="14" fill="url(#chrome)" stroke="#475569" stroke-width="2.5"/>
      <!-- Chrome reflection line -->
      <line x1="26" y1="35" x2="88" y2="35" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" opacity="0.8"/>
      <!-- Toaster bread slots on back -->
      <line x1="35" y1="25" x2="65" y2="25" stroke="#1e293b" stroke-width="5" stroke-linecap="round"/>
      <!-- Slices of Toast Popping Out! (Smoking slightly!) -->
      <g transform="translate(42, 5) rotate(-8)">
        <rect x="0" y="0" width="18" height="22" rx="3" fill="#d97706" stroke="#78350f" stroke-width="1.5"/>
        <path d="M -2 4 C 0 -2, 18 -2, 20 4 Z" fill="#b45309"/> <!-- Crust top -->
        <!-- Little buttery smile on toast -->
        <rect x="5" y="8" width="6" height="6" rx="1" fill="#fde047"/>
      </g>
      <!-- Tiny wisp of smoke from toast -->
      <path d="M 48 0 Q 52 -10 46 -18 Q 50 -25 45 -32" fill="none" stroke="#cbd5e1" stroke-width="2" opacity="0.4" stroke-linecap="round"/>

      <!-- Toaster Lever Handle (acting as side flank dial) -->
      <rect x="85" y="42" width="10" height="4" fill="#0f172a"/>
      <circle cx="95" cy="44" r="4" fill="#dc2626"/>
    </g>

    <!-- Dog Slinky Flexible Neck -->
    <g id="dog-neck">
      <path d="M 22 45 Q 8 38 12 25" fill="none" stroke="#64748b" stroke-width="12" stroke-linecap="round"/>
      <!-- Slinky coil ribs -->
      <ellipse cx="16" cy="38" rx="7" ry="3" fill="#cbd5e1" transform="rotate(-30, 16, 38)"/>
      <ellipse cx="14" cy="32" rx="7" ry="3" fill="#cbd5e1" transform="rotate(-30, 14, 32)"/>
    </g>

    <!-- Dog Head: Tilted retro kettle / iron shape -->
    <g id="dog-head" transform="translate(10, 18) rotate(-15)">
      <path d="M -15 -8 L 8 -12 C 18 -12, 22 2, 14 10 L -12 8 Z" fill="url(#chrome)" stroke="#334155" stroke-width="2"/>
      <!-- Floppy Sheet-Metal Ear (one up, one down) -->
      <!-- Left ear up in alert doggy attention -->
      <path d="M -10 -10 C -15 -25, -2 -28, -2 -12 Z" fill="#64748b" stroke="#334155" stroke-width="1.5"/>
      <!-- Right ear floppy -->
      <path d="M 2 -11 C 6 -18, 14 -12, 10 -4 Z" fill="#475569" stroke="#1e293b" stroke-width="1.5"/>

      <!-- Doggy Eyes: Glowing round camera apertures staring upward devotedly -->
      <circle cx="2" cy="-2" r="5" fill="#38bdf8" filter="url(#softGlow)"/>
      <circle cx="2" cy="-2" r="2" fill="#0c4a6e"/>
      <circle cx="3" cy="-3" r="1" fill="#fff"/>

      <!-- Doggy Snout: Hex-nut nose -->
      <polygon points="16,3 19,5 19,9 16,11 13,9 13,5" fill="#0f172a"/>

      <!-- Doggy Tongue: Pink ribbon tape / copper strip panting out happily -->
      <path d="M 6 8 C 8 18, 14 18, 12 8 Z" fill="#f43f5e" stroke="#be123c" stroke-width="1"/>
      <line x1="9" y1="8" x2="9" y2="15" stroke="#be123c" stroke-width="1"/>
    </g>

    <!-- Dog Tail: Wagging Spring Antenna with glowing amber bulb tip -->
    <g id="dog-tail">
      <!-- Motion wag lines -->
      <path d="M 88 15 C 98 12, 108 22, 102 32" fill="none" stroke="#fbbf24" stroke-width="1" stroke-dasharray="2,2"/>
      <!-- Spring coil -->
      <path d="M 90 32 Q 98 24 92 18 Q 102 12 96 6" fill="none" stroke="#64748b" stroke-width="3" stroke-linecap="round"/>
      <!-- Lit bulb tip -->
      <circle cx="96" cy="4" r="5" fill="#f59e0b" filter="url(#softGlow)"/>
      <circle cx="96" cy="4" r="2" fill="#fff"/>
    </g>
  </g>

  <!-- ================= FOREGROUND LIGHTING & VIGNETTE POLISH ================= -->
  <!-- Warm studio flash highlight across the family -->
  <ellipse cx="600" cy="450" rx="550" ry="380" fill="url(#vignette)" opacity="0.12" style="mix-blend-mode: overlay;"/>

  <!-- Vintage portrait border / subtle rounded matte inner frame -->
  <rect x="15" y="15" width="1170" height="870" rx="20" fill="none" stroke="#251b2e" stroke-width="12" opacity="0.8"/>
  <rect x="22" y="22" width="1156" height="856" rx="14" fill="none" stroke="#d4af37" stroke-width="2" opacity="0.4"/>
  <!-- Corner filigree accents on portrait frame -->
  <g stroke="#d4af37" stroke-width="2" fill="none" opacity="0.5">
    <path d="M 30 50 L 50 50 L 50 30"/>
    <circle cx="50" cy="50" r="3" fill="#d4af37"/>
    <path d="M 1170 50 L 1150 50 L 1150 30"/>
    <circle cx="1150" cy="50" r="3" fill="#d4af37"/>
    <path d="M 30 850 L 50 850 L 50 870"/>
    <circle cx="50" cy="850" r="3" fill="#d4af37"/>
    <path d="M 1170 850 L 1150 850 L 1150 870"/>
    <circle cx="1150" cy="850" r="3" fill="#d4af37"/>
  </g>
</svg>'''
    return svg_code

if __name__ == '__main__':
    code = generate_svg()
    # Save code to output directory
    with open('output/awkward_robot_family.svg', 'w') as f:
        f.write(code)
    print("SVG generated successfully at output/awkward_robot_family.svg")
