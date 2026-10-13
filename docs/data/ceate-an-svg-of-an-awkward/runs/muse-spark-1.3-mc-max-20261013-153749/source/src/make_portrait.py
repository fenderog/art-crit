#!/usr/bin/env python3
"""Generate awkward robot family portrait SVG. No text elements."""
import pathlib

SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800">
<defs>
  <linearGradient id="backdrop" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#4a3f33"/>
    <stop offset="0.35" stop-color="#8a7a64"/>
    <stop offset="0.62" stop-color="#c9b89a"/>
    <stop offset="0.75" stop-color="#b7a684"/>
    <stop offset="1" stop-color="#6b5a42"/>
  </linearGradient>
  <radialGradient id="spot" cx="0.5" cy="0.42" r="0.65">
    <stop offset="0" stop-color="#fff8e8" stop-opacity="0.55"/>
    <stop offset="0.5" stop-color="#fff2d0" stop-opacity="0.18"/>
    <stop offset="1" stop-color="#000000" stop-opacity="0.35"/>
  </radialGradient>
  <linearGradient id="floorG" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#8a6b48"/>
    <stop offset="0.25" stop-color="#6f5236"/>
    <stop offset="1" stop-color="#3a2a1c"/>
  </linearGradient>
  <linearGradient id="curtain" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#3d1118"/>
    <stop offset="0.25" stop-color="#82293a"/>
    <stop offset="0.5" stop-color="#a83e50"/>
    <stop offset="0.75" stop-color="#6b1f2c"/>
    <stop offset="1" stop-color="#2e0c12"/>
  </linearGradient>
  <linearGradient id="curtainR" x1="1" y1="0" x2="0" y2="0">
    <stop offset="0" stop-color="#3d1118"/>
    <stop offset="0.25" stop-color="#82293a"/>
    <stop offset="0.5" stop-color="#a83e50"/>
    <stop offset="0.75" stop-color="#6b1f2c"/>
    <stop offset="1" stop-color="#2e0c12"/>
  </linearGradient>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#6b4e12"/>
    <stop offset="0.2" stop-color="#f5d67a"/>
    <stop offset="0.4" stop-color="#9a7a25"/>
    <stop offset="0.6" stop-color="#ffe9a8"/>
    <stop offset="0.8" stop-color="#8a6a20"/>
    <stop offset="1" stop-color="#5a4210"/>
  </linearGradient>
  <linearGradient id="skyG" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#7ab5d6"/>
    <stop offset="0.55" stop-color="#f2c48d"/>
    <stop offset="0.72" stop-color="#e88a5a"/>
    <stop offset="1" stop-color="#7a4a5a"/>
  </linearGradient>
  <linearGradient id="dadBody" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#6d7a89"/>
    <stop offset="0.5" stop-color="#4d5864"/>
    <stop offset="1" stop-color="#2f363e"/>
  </linearGradient>
  <linearGradient id="dadHead" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#8a96a3"/>
    <stop offset="1" stop-color="#4a545f"/>
  </linearGradient>
  <linearGradient id="momSkin" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fefaf0"/>
    <stop offset="0.6" stop-color="#ead9c8"/>
    <stop offset="1" stop-color="#c9a893"/>
  </linearGradient>
  <linearGradient id="momDress" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#7ec8c0"/>
    <stop offset="1" stop-color="#2f7a7a"/>
  </linearGradient>
  <linearGradient id="teenBody" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3a3f4a"/>
    <stop offset="1" stop-color="#15171e"/>
  </linearGradient>
  <linearGradient id="kidBody" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffd84d"/>
    <stop offset="1" stop-color="#e89a1f"/>
  </linearGradient>
  <linearGradient id="granBody" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#cbb89e"/>
    <stop offset="1" stop-color="#7a6a52"/>
  </linearGradient>
  <radialGradient id="vign" cx="0.5" cy="0.5" r="0.75">
    <stop offset="0.55" stop-color="#000000" stop-opacity="0"/>
    <stop offset="1" stop-color="#1a0f08" stop-opacity="0.55"/>
  </radialGradient>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="6"/>
  </filter>
  <filter id="soft2" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="2.5"/>
  </filter>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="6" cy="6" r="4.5" fill="#fff" opacity="0.9"/>
    <circle cx="17" cy="17" r="3.5" fill="#ff9abb" opacity="0.9"/>
  </pattern>
  <pattern id="knit" width="16" height="12" patternUnits="userSpaceOnUse">
    <path d="M0 12 L8 0 L16 12" fill="none" stroke="#8a4a5a" stroke-width="2" opacity="0.6"/>
  </pattern>
  <clipPath id="ovalClip">
    <ellipse cx="600" cy="360" rx="430" ry="235"/>
  </clipPath>
</defs>

<!-- STUDIO BACKDROP -->
<rect x="0" y="0" width="1200" height="800" fill="url(#backdrop)"/>
<g clip-path="url(#ovalClip)">
  <rect x="150" y="110" width="900" height="500" fill="url(#skyG)"/>
  <circle cx="620" cy="310" r="58" fill="#fff2c0" opacity="0.95"/>
  <circle cx="620" cy="310" r="72" fill="#ffedb0" opacity="0.25"/>
  <!-- cheesy mountains -->
  <polygon points="170,380 320,220 470,380" fill="#6a7a8a"/>
  <polygon points="300,250 340,290 320,295 350,320 300,315 320,340 270,320" fill="#fff" opacity="0.9"/>
  <polygon points="380,380 540,190 700,380" fill="#4a5a6a"/>
  <polygon points="515,220 545,255 530,260 555,280 515,275 525,295 495,272" fill="#fff" opacity="0.9"/>
  <polygon points="620,380 760,230 910,380" fill="#5a6a7a"/>
  <polygon points="740,255 765,285 750,288 770,305 735,300" fill="#fff" opacity="0.8"/>
  <!-- lake -->
  <rect x="150" y="380" width="900" height="230" fill="#4a6a8a"/>
  <rect x="150" y="380" width="900" height="10" fill="#fff" opacity="0.4"/>
  <ellipse cx="620" cy="420" rx="70" ry="10" fill="#ffdf9a" opacity="0.6"/>
  <ellipse cx="620" cy="445" rx="95" ry="8" fill="#ffdf9a" opacity="0.3"/>
  <ellipse cx="420" cy="460" rx="120" ry="6" fill="#fff" opacity="0.15"/>
  <ellipse cx="780" cy="480" rx="140" ry="7" fill="#fff" opacity="0.12"/>
  <!-- fake trees -->
  <g fill="#2f4a2f">
    <polygon points="250,380 270,330 290,380"/><rect x="267" y="380" width="6" height="18" fill="#4a3423"/>
    <polygon points="880,380 900,325 920,380"/><rect x="897" y="380" width="6" height="18" fill="#4a3423"/>
    <polygon points="830,380 845,340 860,380"/>
  </g>
</g>
<ellipse cx="600" cy="360" rx="430" ry="235" fill="none" stroke="#e8dcc0" stroke-width="10" opacity="0.35"/>
<ellipse cx="600" cy="360" rx="445" ry="248" fill="none" stroke="#3a2f22" stroke-width="3" opacity="0.4"/>
<rect x="0" y="0" width="1200" height="800" fill="url(#spot)"/>

<!-- FLOOR -->
<rect x="0" y="585" width="1200" height="215" fill="url(#floorG)"/>
<g stroke="#2e2015" stroke-width="2" opacity="0.5">
  <line x1="0" y1="620" x2="1200" y2="620"/>
  <line x1="0" y1="660" x2="1200" y2="660"/>
  <line x1="0" y1="710" x2="1200" y2="710"/>
  <line x1="200" y1="585" x2="80" y2="800"/>
  <line x1="450" y1="585" x2="400" y2="800"/>
  <line x1="750" y1="585" x2="800" y2="800"/>
  <line x1="1000" y1="585" x2="1120" y2="800"/>
</g>
<!-- rug -->
<ellipse cx="600" cy="720" rx="400" ry="68" fill="#7a1f2e" opacity="0.95"/>
<ellipse cx="600" cy="720" rx="360" ry="56" fill="none" stroke="#e8c87a" stroke-width="6" opacity="0.8"/>
<ellipse cx="600" cy="720" rx="300" ry="42" fill="none" stroke="#e8c87a" stroke-width="2" opacity="0.5"/>
<ellipse cx="600" cy="720" rx="120" ry="18" fill="#e8c87a" opacity="0.25"/>

<!-- SIDE CURTAINS -->
<path d="M0,0 L150,0 C130,150 110,350 95,600 L0,600 Z" fill="url(#curtain)"/>
<g stroke="#2a0a10" stroke-width="3" opacity="0.5" fill="none">
  <path d="M30,0 C25,200 20,400 15,600"/>
  <path d="M70,0 C60,200 50,400 45,600"/>
  <path d="M110,0 C95,200 85,400 75,600"/>
</g>
<path d="M1200,0 L1050,0 C1070,150 1090,350 1105,600 L1200,600 Z" fill="url(#curtainR)"/>
<g stroke="#2a0a10" stroke-width="3" opacity="0.5" fill="none">
  <path d="M1170,0 C1175,200 1180,400 1185,600"/>
  <path d="M1130,0 C1140,200 1150,400 1155,600"/>
  <path d="M1090,0 C1105,200 1115,400 1125,600"/>
</g>
<!-- top valance -->
<path d="M0,0 L1200,0 L1200,55 C1000,90 800,20 600,55 C400,90 200,20 0,55 Z" fill="#5a1620"/>
<circle cx="100" cy="45" r="10" fill="#d8a83e"/><circle cx="300" cy="55" r="10" fill="#d8a83e"/>
<circle cx="500" cy="55" r="10" fill="#d8a83e"/><circle cx="700" cy="55" r="10" fill="#d8a83e"/>
<circle cx="900" cy="55" r="10" fill="#d8a83e"/><circle cx="1100" cy="45" r="10" fill="#d8a83e"/>

<!-- ======== SHADOWS ======== -->
<ellipse cx="265" cy="705" rx="90" ry="18" fill="#000" opacity="0.35" filter="url(#soft)"/>
<ellipse cx="485" cy="705" rx="85" ry="16" fill="#000" opacity="0.35" filter="url(#soft)"/>
<ellipse cx="810" cy="715" rx="90" ry="16" fill="#000" opacity="0.35" filter="url(#soft)"/>
<ellipse cx="1052" cy="715" rx="75" ry="15" fill="#000" opacity="0.35" filter="url(#soft)"/>

<!-- ======== DAD ROBOT - stiff patriarch, leaning away ======== -->
<g transform="translate(185,175) rotate(2)">
  <!-- legs -->
  <rect x="45" y="355" width="38" height="125" rx="8" fill="#2f363e" stroke="#1a1e23" stroke-width="3"/>
  <rect x="95" y="355" width="38" height="125" rx="8" fill="#2f363e" stroke="#1a1e23" stroke-width="3"/>
  <rect x="25" y="475" width="70" height="28" rx="10" fill="#1e2329" stroke="#0f1215" stroke-width="2"/>
  <rect x="90" y="475" width="70" height="28" rx="10" fill="#1e2329" stroke="#0f1215" stroke-width="2"/>
  <!-- left arm stiff down (viewer left) -->
  <rect x="0" y="200" width="26" height="145" rx="13" fill="url(#dadBody)" stroke="#1e2329" stroke-width="3"/>
  <circle cx="13" cy="360" r="18" fill="#8a96a3" stroke="#1e2329" stroke-width="3"/>
  <line x1="5" y1="372" x2="5" y2="388" stroke="#1e2329" stroke-width="4" stroke-linecap="round"/>
  <line x1="13" y1="374" x2="13" y2="392" stroke="#1e2329" stroke-width="4" stroke-linecap="round"/>
  <line x1="21" y1="372" x2="21" y2="388" stroke="#1e2329" stroke-width="4" stroke-linecap="round"/>
  <!-- torso -->
  <rect x="22" y="185" width="130" height="180" rx="20" fill="url(#dadBody)" stroke="#1a1e23" stroke-width="4"/>
  <circle cx="42" cy="205" r="5" fill="#9aa6b2"/><circle cx="132" cy="205" r="5" fill="#9aa6b2"/>
  <circle cx="42" cy="345" r="5" fill="#9aa6b2"/><circle cx="132" cy="345" r="5" fill="#9aa6b2"/>
  <!-- chest gauge -->
  <circle cx="62" cy="250" r="22" fill="#e8e0c8" stroke="#1a1e23" stroke-width="3"/>
  <line x1="62" y1="250" x2="74" y2="236" stroke="#c02a2a" stroke-width="3" stroke-linecap="round"/>
  <circle cx="62" cy="250" r="4" fill="#1a1e23"/>
  <!-- buttons -->
  <circle cx="110" cy="235" r="8" fill="#c02a2a" stroke="#1a1e23" stroke-width="2"/>
  <circle cx="110" cy="258" r="8" fill="#2fa84a" stroke="#1a1e23" stroke-width="2"/>
  <circle cx="110" cy="281" r="8" fill="#e8a81f" stroke="#1a1e23" stroke-width="2"/>
  <!-- vent -->
  <g stroke="#1a1e23" stroke-width="3" opacity="0.6">
    <line x1="45" y1="300" x2="130" y2="300"/><line x1="45" y1="312" x2="130" y2="312"/><line x1="45" y1="324" x2="130" y2="324"/>
  </g>
  <!-- rust spots -->
  <ellipse cx="135" cy="335" rx="14" ry="10" fill="#8a4a1f" opacity="0.7"/>
  <ellipse cx="30" cy="275" rx="9" ry="12" fill="#8a4a1f" opacity="0.6"/>
  <ellipse cx="120" cy="195" rx="8" ry="6" fill="#8a4a1f" opacity="0.6"/>
  <!-- crooked tie -->
  <g transform="translate(87,190) rotate(9)">
    <polygon points="-12,0 12,0 8,55 0,70 -8,55" fill="#7a1f2e" stroke="#2a0a10" stroke-width="2"/>
    <polygon points="-6,12 6,12 4,30 -4,30" fill="#a83e50" opacity="0.6"/>
  </g>
  <!-- right arm reaching toward mom but hovering (gap = awkward) -->
  <g transform="translate(150,200) rotate(-52)">
    <rect x="-13" y="0" width="26" height="130" rx="13" fill="url(#dadBody)" stroke="#1a1e23" stroke-width="3"/>
    <circle cx="0" cy="145" r="17" fill="#8a96a3" stroke="#1a1e23" stroke-width="3"/>
  </g>
  <!-- neck -->
  <rect x="70" y="165" width="34" height="25" fill="#2f363e" stroke="#1a1e23" stroke-width="3"/>
  <!-- head -->
  <rect x="27" y="65" width="120" height="105" rx="14" fill="url(#dadHead)" stroke="#1a1e23" stroke-width="4"/>
  <rect x="12" y="95" width="16" height="30" rx="5" fill="#4a545f" stroke="#1a1e23" stroke-width="3"/>
  <rect x="146" y="95" width="16" height="30" rx="5" fill="#4a545f" stroke="#1a1e23" stroke-width="3"/>
  <!-- antenna with drooping flag -->
  <line x1="87" y1="65" x2="87" y2="28" stroke="#1a1e23" stroke-width="4"/>
  <circle cx="87" cy="24" r="7" fill="#c02a2a" stroke="#1a1e23" stroke-width="2"/>
  <path d="M94,18 L124,24 L94,32 Z" fill="#c02a2a" opacity="0.85"/>
  <!-- visor -->
  <rect x="37" y="85" width="100" height="38" rx="10" fill="#10151a" stroke="#1a1e23" stroke-width="2"/>
  <!-- awkward eyes: different heights, different gaze -->
  <circle cx="68" cy="102" r="12" fill="#bff0ff"/>
  <circle cx="71" cy="103" r="5" fill="#102030"/>
  <circle cx="73" cy="101" r="1.8" fill="#fff"/>
  <circle cx="112" cy="107" r="11" fill="#bff0ff"/>
  <circle cx="108" cy="108" r="5" fill="#102030"/>
  <circle cx="110" cy="106" r="1.8" fill="#fff"/>
  <!-- heavy brow, one raised -->
  <rect x="52" y="78" width="32" height="7" rx="3" fill="#1a1e23" transform="rotate(-6 68 81)"/>
  <rect x="98" y="80" width="32" height="7" rx="3" fill="#1a1e23" transform="rotate(4 114 83)"/>
  <!-- brush moustache -->
  <g fill="#3a3a3a" stroke="#1a1e23" stroke-width="1.5">
    <rect x="52" y="128" width="34" height="12" rx="6" transform="rotate(-4 69 134)"/>
    <rect x="88" y="128" width="34" height="12" rx="6" transform="rotate(5 105 134)"/>
  </g>
  <g stroke="#111" stroke-width="1" opacity="0.6">
    <line x1="58" y1="130" x2="58" y2="138"/><line x1="64" y1="130" x2="64" y2="139"/><line x1="70" y1="130" x2="70" y2="139"/>
    <line x1="104" y1="130" x2="104" y2="139"/><line x1="110" y1="130" x2="110" y2="139"/><line x1="116" y1="131" x2="116" y2="138"/>
  </g>
  <!-- forced crooked grin -->
  <path d="M60,148 L110,154 L106,166 L64,161 Z" fill="#102030" stroke="#1a1e23" stroke-width="2"/>
  <rect x="62" y="148" width="46" height="9" fill="#fff" opacity="0.95"/>
  <g stroke="#1a1e23" stroke-width="1.5">
    <line x1="73" y1="148" x2="73" y2="157"/><line x1="84" y1="149" x2="84" y2="158"/><line x1="95" y1="150" x2="95" y2="159"/>
  </g>
  <!-- flash glare -->
  <ellipse cx="50" cy="75" rx="18" ry="10" fill="#fff" opacity="0.35" transform="rotate(-20 50 75)"/>
</g>

<!-- ======== MOM ROBOT - over-eager, leaning in ======== -->
<g transform="translate(415,235) rotate(-6)">
  <ellipse cx="70" cy="475" rx="70" ry="12" fill="#000" opacity="0.2"/>
  <!-- legs pigeon-toed -->
  <g>
    <rect x="45" y="365" width="20" height="90" rx="9" fill="#d9c2a8" stroke="#5a4a3a" stroke-width="2.5"/>
    <rect x="80" y="365" width="20" height="90" rx="9" fill="#d9c2a8" stroke="#5a4a3a" stroke-width="2.5"/>
    <g transform="translate(55,460) rotate(18)">
      <ellipse cx="0" cy="0" rx="22" ry="12" fill="#7a1f2e" stroke="#2a0a10" stroke-width="2"/>
    </g>
    <g transform="translate(90,460) rotate(-20)">
      <ellipse cx="0" cy="0" rx="22" ry="12" fill="#7a1f2e" stroke="#2a0a10" stroke-width="2"/>
    </g>
  </g>
  <!-- dress A-line -->
  <path d="M25,360 L45,230 L100,230 L125,360 C100,375 50,375 25,360 Z" fill="url(#momDress)" stroke="#143a3a" stroke-width="3"/>
  <path d="M25,360 L45,230 L100,230 L125,360 C100,375 50,375 25,360 Z" fill="url(#dots)" opacity="0.55"/>
  <!-- hem lights -->
  <g>
    <circle cx="38" cy="355" r="6" fill="#ff5a7a" stroke="#222" stroke-width="1.5"/>
    <circle cx="58" cy="361" r="6" fill="#ffd84d" stroke="#222" stroke-width="1.5"/>
    <circle cx="78" cy="363" r="6" fill="#5aff8a" stroke="#222" stroke-width="1.5"/>
    <circle cx="98" cy="361" r="6" fill="#5ab5ff" stroke="#222" stroke-width="1.5"/>
    <circle cx="115" cy="355" r="6" fill="#ff5a7a" stroke="#222" stroke-width="1.5"/>
  </g>
  <!-- bodice bow -->
  <polygon points="55,235 73,245 55,255" fill="#ff9abb" stroke="#7a1f2e" stroke-width="2"/>
  <polygon points="91,235 73,245 91,255" fill="#ff9abb" stroke="#7a1f2e" stroke-width="2"/>
  <circle cx="73" cy="245" r="7" fill="#7a1f2e"/>
  <!-- arms clasped nervously -->
  <rect x="28" y="235" width="22" height="95" rx="11" fill="url(#momSkin)" stroke="#5a4a3a" stroke-width="2.5" transform="rotate(-24 39 235)"/>
  <rect x="95" y="235" width="22" height="95" rx="11" fill="url(#momSkin)" stroke="#5a4a3a" stroke-width="2.5" transform="rotate(24 106 235)"/>
  <ellipse cx="62" cy="335" rx="18" ry="14" fill="url(#momSkin)" stroke="#5a4a3a" stroke-width="2.5"/>
  <ellipse cx="84" cy="335" rx="18" ry="14" fill="#e8d5c0" stroke="#5a4a3a" stroke-width="2.5"/>
  <g stroke="#8a7a6a" stroke-width="1.5">
    <line x1="72" y1="328" x2="72" y2="342"/><line x1="77" y1="328" x2="77" y2="342"/>
  </g>
  <!-- neck -->
  <rect x="62" y="195" width="24" height="35" fill="#c9a893" stroke="#5a4a3a" stroke-width="2.5"/>
  <!-- earrings -->
  <line x1="18" y1="150" x2="18" y2="180" stroke="#d8a83e" stroke-width="3"/>
  <rect x="11" y="180" width="14" height="20" rx="3" fill="#8a96a3" stroke="#333" stroke-width="2"/>
  <line x1="130" y1="150" x2="130" y2="180" stroke="#d8a83e" stroke-width="3"/>
  <rect x="123" y="180" width="14" height="20" rx="3" fill="#8a96a3" stroke="#333" stroke-width="2"/>
  <!-- head -->
  <ellipse cx="74" cy="145" rx="58" ry="62" fill="url(#momSkin)" stroke="#5a4a3a" stroke-width="3.5"/>
  <!-- beehive hair -->
  <path d="M16,140 C10,70 40,20 74,18 C108,20 138,70 132,140 C125,105 110,95 74,93 C38,95 23,105 16,140 Z" fill="#4a3a52" stroke="#1e1620" stroke-width="3"/>
  <ellipse cx="74" cy="35" rx="28" ry="22" fill="#5a4a62" stroke="#1e1620" stroke-width="2.5"/>
  <!-- curlers / antenna curls -->
  <g fill="none" stroke="#c9c9d9" stroke-width="4" stroke-linecap="round">
    <path d="M40,55 C25,40 15,45 18,58 C20,66 32,64 30,56"/>
    <path d="M108,55 C123,40 133,45 130,58 C128,66 116,64 118,56"/>
  </g>
  <circle cx="40" cy="62" r="9" fill="#ff5a7a" stroke="#7a1f2e" stroke-width="2"/>
  <circle cx="108" cy="62" r="9" fill="#ff5a7a" stroke="#7a1f2e" stroke-width="2"/>
  <line x1="74" y1="13" x2="74" y2="-8" stroke="#333" stroke-width="3"/>
  <circle cx="74" cy="-12" r="7" fill="#ff5a7a" stroke="#7a1f2e" stroke-width="2">
    <animate attributeName="opacity" values="1;0.3;1" dur="1.6s" repeatCount="indefinite"/>
  </circle>
  <!-- huge eager eyes, slightly crossed -->
  <g>
    <ellipse cx="50" cy="142" rx="20" ry="24" fill="#fff" stroke="#333" stroke-width="2.5"/>
    <ellipse cx="98" cy="142" rx="20" ry="24" fill="#fff" stroke="#333" stroke-width="2.5"/>
    <circle cx="56" cy="150" r="10" fill="#2a7a8a" stroke="#102030" stroke-width="2"/>
    <circle cx="92" cy="150" r="10" fill="#2a7a8a" stroke="#102030" stroke-width="2"/>
    <circle cx="58" cy="152" r="4.5" fill="#0a0a0a"/><circle cx="90" cy="152" r="4.5" fill="#0a0a0a"/>
    <circle cx="60" cy="148" r="2" fill="#fff"/><circle cx="92" cy="148" r="2" fill="#fff"/>
    <!-- lashes -->
    <g stroke="#1a1a1a" stroke-width="2.5" stroke-linecap="round">
      <line x1="32" y1="128" x2="24" y2="120"/><line x1="38" y1="123" x2="33" y2="113"/><line x1="48" y1="120" x2="46" y2="109"/>
      <line x1="116" y1="128" x2="124" y2="120"/><line x1="110" y1="123" x2="115" y2="113"/><line x1="100" y1="120" x2="102" y2="109"/>
    </g>
  </g>
  <!-- blush -->
  <ellipse cx="32" cy="170" rx="12" ry="8" fill="#ff9abb" opacity="0.7"/>
  <ellipse cx="116" cy="170" rx="12" ry="8" fill="#ff9abb" opacity="0.7"/>
  <!-- too-wide smile -->
  <path d="M30,174 C45,205 103,205 118,174 C100,182 48,182 30,174 Z" fill="#5a1a22" stroke="#2a0a10" stroke-width="2.5"/>
  <path d="M32,175 C50,184 98,184 116,175 L112,186 C95,193 53,193 36,186 Z" fill="#fff"/>
  <g stroke="#333" stroke-width="1">
    <line x1="55" y1="181" x2="55" y2="190"/><line x1="68" y1="183" x2="68" y2="192"/><line x1="81" y1="183" x2="81" y2="192"/><line x1="94" y1="181" x2="94" y2="190"/>
  </g>
  <!-- beauty mark bolt -->
  <circle cx="108" cy="192" r="3" fill="#1a1a1a"/>
  <ellipse cx="55" cy="110" rx="16" ry="8" fill="#fff" opacity="0.4"/>
</g>

<!-- ======== TEEN ROBOT - slouched, checked out ======== -->
<g transform="translate(790,235) rotate(9)">
  <!-- skateboard leaning -->
  <g transform="translate(95,260) rotate(-12)">
    <rect x="-18" y="0" width="36" height="150" rx="18" fill="#6b3fa0" stroke="#1a102a" stroke-width="3"/>
    <circle cx="0" cy="35" r="12" fill="#c8ff3e" stroke="#1a102a" stroke-width="2"/>
    <polygon points="0,100 -14,125 0,120 14,145 4,115" fill="#c8ff3e" stroke="#1a102a" stroke-width="2"/>
    <circle cx="-12" cy="160" r="10" fill="#222" stroke="#555" stroke-width="2"/>
    <circle cx="12" cy="160" r="10" fill="#222" stroke="#555" stroke-width="2"/>
  </g>
  <!-- legs: crossed, slouch -->
  <rect x="20" y="330" width="24" height="135" rx="10" fill="#23262f" stroke="#0a0c10" stroke-width="3"/>
  <g transform="translate(50,335) rotate(-14)">
    <rect x="-12" y="0" width="24" height="135" rx="10" fill="#23262f" stroke="#0a0c10" stroke-width="3"/>
  </g>
  <g transform="translate(30,470) rotate(-8)">
    <rect x="-28" y="0" width="56" height="22" rx="10" fill="#c8ff3e" stroke="#1a2020" stroke-width="2.5"/>
  </g>
  <g transform="translate(75,465) rotate(12)">
    <rect x="-28" y="0" width="56" height="22" rx="10" fill="#ff3e7a" stroke="#1a2020" stroke-width="2.5"/>
  </g>
  <!-- torso hoodie -->
  <rect x="8" y="175" width="95" height="165" rx="18" fill="url(#teenBody)" stroke="#0a0c10" stroke-width="3.5"/>
  <rect x="25" y="275" width="60" height="35" rx="8" fill="#2f3542" stroke="#0a0c10" stroke-width="2"/>
  <g stroke="#c8ff3e" stroke-width="2" opacity="0.8">
    <line x1="42" y1="185" x2="38" y2="225"/><line x1="69" y1="185" x2="73" y2="225"/>
  </g>
  <circle cx="38" cy="230" r="5" fill="#c8ff3e"/><circle cx="73" cy="230" r="5" fill="#c8ff3e"/>
  <polygon points="55,245 35,270 50,268 42,295 75,262 60,264" fill="#c8ff3e" stroke="#0a0c10" stroke-width="2"/>
  <circle cx="85" cy="200" r="10" fill="#ff3e7a" stroke="#0a0c10" stroke-width="2"/>
  <circle cx="85" cy="200" r="3" fill="#0a0c10"/>
  <!-- crossed arms tight -->
  <g>
    <rect x="-5" y="210" width="110" height="26" rx="13" fill="#2f3542" stroke="#0a0c10" stroke-width="3" transform="rotate(12 50 223)"/>
    <rect x="-5" y="235" width="110" height="26" rx="13" fill="#23262f" stroke="#0a0c10" stroke-width="3" transform="rotate(-10 50 248)"/>
    <circle cx="95" cy="238" r="13" fill="#8a96a3" stroke="#0a0c10" stroke-width="2.5"/>
    <circle cx="12" cy="232" r="13" fill="#8a96a3" stroke="#0a0c10" stroke-width="2.5"/>
  </g>
  <!-- neck -->
  <rect x="42" y="150" width="26" height="30" fill="#3a3f4a" stroke="#0a0c10" stroke-width="3"/>
  <!-- head turned away (looking right) -->
  <g transform="translate(55,80) rotate(14)">
    <rect x="-38" y="0" width="76" height="85" rx="16" fill="#3a3f4a" stroke="#0a0c10" stroke-width="3.5"/>
    <!-- mohawk fin -->
    <polygon points="-10,-28 10,-28 20,5 -20,5" fill="#c8ff3e" stroke="#0a0c10" stroke-width="2.5"/>
    <line x1="-6" y1="-20" x2="6" y2="-20" stroke="#6b3fa0" stroke-width="4"/>
    <line x1="-10" y1="-8" x2="12" y2="-8" stroke="#ff3e7a" stroke-width="4"/>
    <line x1="-14" y1="2" x2="16" y2="2" stroke="#6b3fa0" stroke-width="3"/>
    <!-- headphones -->
    <path d="M-42,45 C-48,0 -20,-18 0,-18 C20,-18 48,0 42,45" fill="none" stroke="#15171e" stroke-width="10" stroke-linecap="round"/>
    <rect x="-58" y="30" width="24" height="40" rx="10" fill="#ff3e7a" stroke="#0a0c10" stroke-width="3"/>
    <rect x="34" y="30" width="24" height="40" rx="10" fill="#ff3e7a" stroke="#0a0c10" stroke-width="3"/>
    <circle cx="-46" cy="50" r="6" fill="#0a0c10"/><circle cx="46" cy="50" r="6" fill="#0a0c10"/>
    <!-- half-lidded bored eyes looking sideways -->
    <rect x="-30" y="28" width="60" height="26" rx="8" fill="#0f1218"/>
    <ellipse cx="-14" cy="42" rx="11" ry="7" fill="#d9d9e8"/>
    <ellipse cx="16" cy="42" rx="11" ry="7" fill="#d9d9e8"/>
    <circle cx="-8" cy="43" r="4.5" fill="#0a0a0a"/>
    <circle cx="22" cy="43" r="4.5" fill="#0a0a0a"/>
    <rect x="-30" y="28" width="60" height="12" rx="6" fill="#3a3f4a" opacity="0.95"/>
    <line x1="-28" y1="40" x2="-2" y2="40" stroke="#0a0c10" stroke-width="2"/>
    <line x1="4" y1="40" x2="30" y2="40" stroke="#0a0c10" stroke-width="2"/>
    <!-- flat annoyed mouth -->
    <line x1="-15" y1="70" x2="20" y2="72" stroke="#c8a0b0" stroke-width="4" stroke-linecap="round"/>
    <line x1="20" y1="72" x2="24" y2="68" stroke="#c8a0b0" stroke-width="3" stroke-linecap="round"/>
    <!-- zit LED -->
    <circle cx="-22" cy="62" r="5" fill="#ff3e3e" stroke="#5a0a0a" stroke-width="1.5"/>
  </g>
</g>

<!-- ======== GRANDMA ROBOT - forgotten at edge, cropped ======== -->
<g transform="translate(1002,385)">
  <!-- base -->
  <ellipse cx="55" cy="325" rx="62" ry="18" fill="#2a241c" stroke="#1a1510" stroke-width="3"/>
  <circle cx="25" cy="333" r="12" fill="#333" stroke="#111" stroke-width="2"/>
  <circle cx="85" cy="333" r="12" fill="#333" stroke="#111" stroke-width="2"/>
  <!-- body dome -->
  <path d="M5,320 L10,180 C10,140 35,125 55,125 C75,125 100,140 100,180 L105,320 Z" fill="url(#granBody)" stroke="#3a3228" stroke-width="3.5"/>
  <!-- shawl -->
  <path d="M-5,200 C20,175 90,175 115,200 L100,245 C75,225 35,225 10,245 Z" fill="#a83e50" stroke="#4a1620" stroke-width="2.5"/>
  <path d="M-5,200 C20,175 90,175 115,200 L100,245 C75,225 35,225 10,245 Z" fill="url(#knit)" opacity="0.7"/>
  <circle cx="10" cy="248" r="5" fill="#e8c87a"/><circle cx="32" cy="240" r="5" fill="#e8c87a"/>
  <circle cx="78" cy="240" r="5" fill="#e8c87a"/><circle cx="100" cy="248" r="5" fill="#e8c87a"/>
  <!-- control panel -->
  <rect x="32" y="260" width="46" height="40" rx="6" fill="#2a2620" stroke="#1a1510" stroke-width="2"/>
  <circle cx="44" cy="274" r="5" fill="#5aff8a" opacity="0.5"/><circle cx="62" cy="274" r="5" fill="#ff5a3e" opacity="0.9"/>
  <rect x="40" y="286" width="30" height="6" rx="3" fill="#5ab5ff" opacity="0.5"/>
  <!-- left arm knitting -->
  <rect x="-18" y="210" width="22" height="70" rx="11" fill="url(#granBody)" stroke="#3a3228" stroke-width="2.5" transform="rotate(20 -7 210)"/>
  <g transform="translate(-5,275)">
    <line x1="0" y1="0" x2="45" y2="-22" stroke="#c9a86a" stroke-width="3" stroke-linecap="round"/>
    <line x1="0" y1="8" x2="42" y2="-8" stroke="#c9a86a" stroke-width="3" stroke-linecap="round"/>
    <circle cx="48" cy="-18" r="16" fill="none" stroke="#ff9abb" stroke-width="3"/>
    <circle cx="48" cy="-18" r="11" fill="none" stroke="#ff9abb" stroke-width="2"/>
    <circle cx="48" cy="-18" r="6" fill="none" stroke="#c02a5a" stroke-width="2"/>
    <path d="M36,-8 C20,5 5,10 -12,8" fill="none" stroke="#ff9abb" stroke-width="2.5"/>
  </g>
  <!-- right arm holding cat-bot (clinging) -->
  <rect x="96" y="210" width="22" height="65" rx="11" fill="url(#granBody)" stroke="#3a3228" stroke-width="2.5" transform="rotate(-18 107 210)"/>
  <g transform="translate(95,250)">
    <rect x="0" y="10" width="52" height="42" rx="10" fill="#5a5f6a" stroke="#22242a" stroke-width="2.5"/>
    <polygon points="6,12 12,0 20,12" fill="#5a5f6a" stroke="#22242a" stroke-width="2"/>
    <polygon points="32,12 38,0 46,12" fill="#5a5f6a" stroke="#22242a" stroke-width="2"/>
    <circle cx="14" cy="8" r="2.5" fill="#ff9abb"/><circle cx="40" cy="8" r="2.5" fill="#ff9abb"/>
    <line x1="14" y1="32" x2="24" y2="32" stroke="#101215" stroke-width="2.5" stroke-linecap="round"/>
    <line x1="30" y1="32" x2="40" y2="32" stroke="#101215" stroke-width="2.5" stroke-linecap="round"/>
    <path d="M52,35 C65,30 68,18 60,12" fill="none" stroke="#22242a" stroke-width="6" stroke-linecap="round"/>
    <circle cx="60" cy="12" r="5" fill="#c8ff3e" stroke="#22242a" stroke-width="1.5"/>
    <g stroke="#c9c9c9" stroke-width="1">
      <line x1="4" y1="38" x2="-6" y2="36"/><line x1="4" y1="42" x2="-6" y2="44"/>
    </g>
  </g>
  <!-- head -->
  <rect x="28" y="105" width="18" height="25" fill="#7a6a52" stroke="#3a3228" stroke-width="2.5"/>
  <ellipse cx="55" cy="85" rx="48" ry="52" fill="#d9c9b0" stroke="#3a3228" stroke-width="3.5"/>
  <!-- hairnet bun -->
  <circle cx="55" cy="28" r="20" fill="#9a9aa8" stroke="#3a3228" stroke-width="2.5"/>
  <g stroke="#5a5a6a" stroke-width="1" opacity="0.7">
    <line x1="38" y1="22" x2="72" y2="34"/><line x1="38" y1="34" x2="72" y2="22"/><line x1="55" y1="10" x2="55" y2="46"/>
  </g>
  <line x1="55" y1="8" x2="55" y2="-6" stroke="#3a3228" stroke-width="3"/>
  <circle cx="55" cy="-10" r="6" fill="#8a8a9a" stroke="#3a3228" stroke-width="2"/>
  <!-- glasses, one cracked -->
  <circle cx="35" cy="85" r="20" fill="#cfe8f2" opacity="0.55" stroke="#2a2a2a" stroke-width="3"/>
  <circle cx="77" cy="85" r="20" fill="#cfe8f2" opacity="0.55" stroke="#2a2a2a" stroke-width="3"/>
  <line x1="55" y1="82" x2="57" y2="82" stroke="#2a2a2a" stroke-width="3"/>
  <line x1="7" y1="78" x2="15" y2="82" stroke="#2a2a2a" stroke-width="3"/>
  <line x1="97" y1="82" x2="103" y2="78" stroke="#2a2a2a" stroke-width="3"/>
  <g stroke="#2a2a2a" stroke-width="1.2" opacity="0.8">
    <line x1="77" y1="70" x2="70" y2="80"/><line x1="70" y1="80" x2="74" y2="92"/><line x1="70" y1="80" x2="62" y2="86"/>
  </g>
  <!-- tired eyes -->
  <circle cx="35" cy="88" r="4" fill="#2a2a2a"/>
  <circle cx="77" cy="88" r="4" fill="#2a2a2a" opacity="0.45">
    <animate attributeName="opacity" values="0.45;0.1;0.45" dur="2.2s" repeatCount="indefinite"/>
  </circle>
  <path d="M22,68 C30,64 40,64 46,68" fill="none" stroke="#5a5a5a" stroke-width="2"/>
  <path d="M66,68 C74,64 84,64 90,68" fill="none" stroke="#5a5a5a" stroke-width="2"/>
  <!-- small wavy frown -->
  <path d="M42,120 C48,117 52,123 58,120 C64,117 68,123 72,119" fill="none" stroke="#4a2a2a" stroke-width="3" stroke-linecap="round"/>
  <ellipse cx="20" cy="105" rx="8" ry="10" fill="#e8a88a" opacity="0.4"/>
  <ellipse cx="90" cy="105" rx="8" ry="10" fill="#e8a88a" opacity="0.4"/>
</g>

<!-- ======== PET ROBOT DOG - looking the wrong way ======== -->
<g transform="translate(395,635)">
  <ellipse cx="55" cy="95" rx="70" ry="12" fill="#000" opacity="0.3" filter="url(#soft)"/>
  <!-- body -->
  <rect x="10" y="45" width="110" height="45" rx="20" fill="#8a4a2a" stroke="#2a150a" stroke-width="3"/>
  <circle cx="35" cy="67" r="8" fill="#ffd84d" stroke="#2a150a" stroke-width="2"/>
  <circle cx="55" cy="67" r="8" fill="#5aff8a" stroke="#2a150a" stroke-width="2"/>
  <circle cx="75" cy="67" r="8" fill="#5ab5ff" stroke="#2a150a" stroke-width="2"/>
  <!-- wheels -->
  <circle cx="35" cy="95" r="14" fill="#222" stroke="#111" stroke-width="2"/>
  <circle cx="35" cy="95" r="5" fill="#888"/>
  <circle cx="95" cy="95" r="14" fill="#222" stroke="#111" stroke-width="2"/>
  <circle cx="95" cy="95" r="5" fill="#888"/>
  <!-- tail wagging -->
  <g transform="translate(118,50) rotate(-35)">
    <line x1="0" y1="0" x2="28" y2="0" stroke="#2a150a" stroke-width="5" stroke-linecap="round"/>
    <circle cx="32" cy="0" r="7" fill="#ff3e3e" stroke="#2a150a" stroke-width="2">
      <animate attributeName="r" values="7;8.5;7" dur="0.5s" repeatCount="indefinite"/>
    </circle>
  </g>
  <g stroke="#fff" stroke-width="2" opacity="0.4" stroke-linecap="round">
    <line x1="140" y1="35" x2="148" y2="28"/><line x1="144" y1="48" x2="154" y2="48"/>
  </g>
  <!-- head looking up-right away from camera -->
  <g transform="translate(15,10) rotate(-12)">
    <rect x="-25" y="-10" width="60" height="55" rx="14" fill="#a85e32" stroke="#2a150a" stroke-width="3"/>
    <!-- one ear up one flopped -->
    <polygon points="-15,-10 -20,-38 -2,-12" fill="#7a3a1f" stroke="#2a150a" stroke-width="2.5"/>
    <ellipse cx="30" cy="2" rx="10" ry="20" fill="#7a3a1f" stroke="#2a150a" stroke-width="2.5" transform="rotate(35 30 2)"/>
    <!-- eyes gazing up-right -->
    <circle cx="2" cy="15" r="9" fill="#fff" stroke="#2a150a" stroke-width="2"/>
    <circle cx="26" cy="15" r="9" fill="#fff" stroke="#2a150a" stroke-width="2"/>
    <circle cx="5" cy="11" r="4" fill="#102030"/><circle cx="29" cy="11" r="4" fill="#102030"/>
    <circle cx="6.5" cy="9.5" r="1.3" fill="#fff"/><circle cx="30.5" cy="9.5" r="1.3" fill="#fff"/>
    <ellipse cx="14" cy="30" rx="7" ry="5" fill="#1a0f0a"/>
    <!-- tongue lolling -->
    <rect x="18" y="32" width="14" height="26" rx="7" fill="#ff8a9a" stroke="#7a1f2e" stroke-width="2" transform="rotate(8 25 45)"/>
    <line x1="25" y1="36" x2="27" y2="52" stroke="#7a1f2e" stroke-width="1.5"/>
  </g>
</g>

<!-- butterfly drone distracting the dog -->
<g transform="translate(545,498)">
  <path d="M-85,195 C-60,145 -30,80 0,0" fill="none" stroke="#fff" stroke-width="2" stroke-dasharray="5 6" opacity="0.4"/>
  <ellipse cx="-14" cy="-6" rx="14" ry="9" fill="#bff0ff" stroke="#2a5a7a" stroke-width="2" opacity="0.9" transform="rotate(-25 -14 -6)"/>
  <ellipse cx="14" cy="-6" rx="14" ry="9" fill="#ffbff0" stroke="#7a2a5a" stroke-width="2" opacity="0.9" transform="rotate(25 14 -6)"/>
  <rect x="-6" y="-10" width="12" height="22" rx="6" fill="#333" stroke="#111" stroke-width="1.5"/>
  <circle cx="0" cy="16" r="4" fill="#ff3e3e">
    <animate attributeName="opacity" values="1;0.2;1" dur="0.8s" repeatCount="indefinite"/>
  </circle>
  <circle cx="-3" cy="-4" r="2.5" fill="#c8ff3e"/><circle cx="3" cy="-4" r="2.5" fill="#c8ff3e"/>
</g>

<!-- ======== KID ROBOT - goofy chaos goblin, front center ======== -->
<g transform="translate(585,505) rotate(6)">
  <ellipse cx="60" cy="225" rx="75" ry="12" fill="#000" opacity="0.3" filter="url(#soft)"/>
  <!-- legs: one lifted -->
  <rect x="35" y="150" width="22" height="50" rx="10" fill="#c02a2a" stroke="#5a0a0a" stroke-width="2.5"/>
  <g transform="translate(90,150) rotate(-30)">
    <rect x="-11" y="0" width="22" height="50" rx="10" fill="#c02a2a" stroke="#5a0a0a" stroke-width="2.5"/>
    <ellipse cx="0" cy="55" rx="20" ry="11" fill="#222" stroke="#111" stroke-width="2"/>
  </g>
  <ellipse cx="46" cy="205" rx="20" ry="11" fill="#222" stroke="#111" stroke-width="2"/>
  <!-- untied wire lace -->
  <path d="M58,200 C75,205 80,220 68,228 C60,232 70,238 78,232" fill="none" stroke="#eee" stroke-width="3" stroke-linecap="round"/>
  <!-- spring arms: one waving, one finger in nose -->
  <path d="M15,110 L-30,70 L-20,60 L-10,70 L0,60 L10,72" fill="none" stroke="#5a5a5a" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="-35" cy="62" r="14" fill="#ffd84d" stroke="#5a0a0a" stroke-width="2.5"/>
  <g stroke="#5a0a0a" stroke-width="2.5" stroke-linecap="round">
    <line x1="-42" y1="52" x2="-48" y2="40"/><line x1="-35" y1="50" x2="-36" y2="36"/><line x1="-28" y1="52" x2="-24" y2="40"/>
  </g>
  <!-- body toaster -->
  <rect x="5" y="60" width="115" height="100" rx="22" fill="url(#kidBody)" stroke="#5a3a0a" stroke-width="3.5"/>
  <rect x="20" y="48" width="85" height="16" rx="8" fill="#8a6a20" stroke="#5a3a0a" stroke-width="2.5"/>
  <rect x="30" y="52" width="65" height="8" rx="4" fill="#2a1a0a"/>
  <!-- toast popping -->
  <g transform="translate(80,18) rotate(12)">
    <rect x="-16" y="0" width="32" height="34" rx="6" fill="#e8a85a" stroke="#7a4a1a" stroke-width="2.5"/>
    <ellipse cx="0" cy="4" rx="12" ry="6" fill="#c07a2a"/>
  </g>
  <!-- belly panel with jam stain + sticker -->
  <rect x="28" y="120" width="50" height="28" rx="6" fill="#fff8e0" stroke="#5a3a0a" stroke-width="2"/>
  <circle cx="40" cy="134" r="6" fill="#2fa84a"/><circle cx="56" cy="134" r="6" fill="#c02a2a"/><circle cx="66" cy="134" r="4" fill="#888"/>
  <polygon points="100,122 106,133 117,134 108,141 110,152 100,145 90,152 92,141 83,134 94,133" fill="#ff3e7a" stroke="#5a0a1f" stroke-width="2"/>
  <ellipse cx="18" cy="145" rx="10" ry="14" fill="#c02a5a" opacity="0.55"/>
  <!-- face: googly mismatched -->
  <circle cx="42" cy="88" r="23" fill="#fff" stroke="#5a3a0a" stroke-width="3"/>
  <circle cx="92" cy="90" r="13" fill="#fff" stroke="#5a3a0a" stroke-width="3"/>
  <circle cx="50" cy="92" r="9" fill="#2a5ac0" stroke="#102030" stroke-width="2"/>
  <circle cx="88" cy="86" r="6" fill="#2fa84a" stroke="#102030" stroke-width="2"/>
  <circle cx="53" cy="89" r="3" fill="#fff"/><circle cx="90" cy="84" r="2" fill="#fff"/>
  <circle cx="50" cy="92" r="3.5" fill="#0a0a0a"/><circle cx="88" cy="86" r="2.5" fill="#0a0a0a"/>
  <!-- nose bolt + finger in nose hole -->
  <circle cx="68" cy="104" r="7" fill="#8a8a9a" stroke="#333" stroke-width="2"/>
  <g transform="translate(125,80)">
    <path d="M0,30 L15,10 L5,5 L-5,15" fill="none" stroke="#5a5a5a" stroke-width="5" stroke-linecap="round"/>
    <circle cx="-8" cy="14" r="11" fill="#ffd84d" stroke="#5a0a0a" stroke-width="2.5"/>
    <line x1="-8" y1="14" x2="-50" y2="22" stroke="#e8a87a" stroke-width="7" stroke-linecap="round"/>
  </g>
  <!-- open drooling grin -->
  <ellipse cx="62" cy="132" rx="18" ry="14" fill="#4a1010" stroke="#2a0a0a" stroke-width="2.5"/>
  <rect x="46" y="121" width="32" height="8" rx="3" fill="#fff"/>
  <line x1="62" y1="121" x2="62" y2="129" stroke="#333" stroke-width="1.5"/>
  <path d="M72,143 C74,155 70,165 66,172" fill="none" stroke="#3a5a1f" stroke-width="4" stroke-linecap="round"/>
  <ellipse cx="65" cy="176" rx="6" ry="8" fill="#5a8a2f" opacity="0.85"/>
  <!-- propeller beanie crooked -->
  <g transform="translate(45,35) rotate(-14)">
    <ellipse cx="0" cy="0" rx="32" ry="14" fill="#3e7ac8" stroke="#102a4a" stroke-width="2.5"/>
    <path d="M-32,0 C-20,-22 20,-22 32,0" fill="#ff3e3e" stroke="#5a0a0a" stroke-width="2" opacity="0.9"/>
    <line x1="0" y1="-18" x2="0" y2="-34" stroke="#333" stroke-width="4"/>
    <g transform="translate(0,-36) rotate(24)">
      <ellipse cx="-22" cy="0" rx="22" ry="7" fill="#ffd84d" stroke="#5a3a0a" stroke-width="2"/>
      <ellipse cx="22" cy="0" rx="22" ry="7" fill="#ffd84d" stroke="#5a3a0a" stroke-width="2" transform="rotate(8 22 0)"/>
      <circle cx="0" cy="0" r="6" fill="#c02a2a" stroke="#5a0a0a" stroke-width="2"/>
    </g>
  </g>
</g>

<!-- flash dust + grain -->
<g opacity="0.5">
  <circle cx="320" cy="280" r="4" fill="#fff" opacity="0.5"/>
  <circle cx="700" cy="200" r="3" fill="#fff" opacity="0.4"/>
  <circle cx="900" cy="300" r="5" fill="#fff" opacity="0.35"/>
  <circle cx="500" cy="150" r="3" fill="#fff" opacity="0.4"/>
  <circle cx="1050" cy="500" r="4" fill="#fff" opacity="0.3"/>
</g>

<!-- sepia photo tint + vignette -->
<rect x="0" y="0" width="1200" height="800" fill="#c8a05a" opacity="0.08"/>
<rect x="0" y="0" width="1200" height="800" fill="url(#vign)"/>

<!-- ornate gold frame -->
<rect x="0" y="0" width="1200" height="800" fill="none" stroke="url(#gold)" stroke-width="36"/>
<rect x="36" y="36" width="1128" height="728" fill="none" stroke="#2a1e08" stroke-width="4"/>
<rect x="44" y="44" width="1112" height="712" fill="none" stroke="#ffe9a8" stroke-width="2" opacity="0.7"/>
<!-- corner ornaments -->
<g fill="url(#gold)" stroke="#4a3510" stroke-width="2">
  <circle cx="18" cy="18" r="16"/><circle cx="1182" cy="18" r="16"/>
  <circle cx="18" cy="782" r="16"/><circle cx="1182" cy="782" r="16"/>
</g>
<g fill="#5a4210">
  <circle cx="18" cy="18" r="6"/><circle cx="1182" cy="18" r="6"/>
  <circle cx="18" cy="782" r="6"/><circle cx="1182" cy="782" r="6"/>
</g>
</svg>
'''

out = pathlib.Path("output/awkward-robot-family.svg")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(SVG, encoding="utf-8")
print(f"wrote {out} ({out.stat().st_size} bytes)")
# sanity: no text elements
t = SVG.lower()
assert "<text" not in t, "forbidden <text> found"
assert "font" not in t or "font" not in t.replace("",""), ""
print("check: no <text> elements - OK")
