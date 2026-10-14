#!/usr/bin/env python3
"""Builds 'The Unit Family Portrait' - an awkward robot family photo as SVG.

The whole piece is authored as one SVG document. No text labels anywhere; every
relationship is expressed through pose, gaze and composition.
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "output"
OUT.mkdir(parents=True, exist_ok=True)

SVG = r'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1400" viewBox="0 0 1400 1400">
<defs>
  <radialGradient id="wall" cx="42%" cy="24%" r="95%">
    <stop offset="0%" stop-color="#3a6877"/>
    <stop offset="42%" stop-color="#1e3c49"/>
    <stop offset="100%" stop-color="#08121a"/>
  </radialGradient>
  <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#4d382b"/>
    <stop offset="55%" stop-color="#2a1d15"/>
    <stop offset="100%" stop-color="#120c08"/>
  </linearGradient>
  <radialGradient id="vig" cx="50%" cy="40%" r="75%">
    <stop offset="52%" stop-color="#000000" stop-opacity="0"/>
    <stop offset="100%" stop-color="#000000" stop-opacity="0.66"/>
  </radialGradient>
  <radialGradient id="shadow" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#000000" stop-opacity="0.55"/>
    <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="eyeCyan" cx="38%" cy="34%" r="70%">
    <stop offset="0%" stop-color="#e6ffff"/>
    <stop offset="45%" stop-color="#4fe0ea"/>
    <stop offset="100%" stop-color="#0a6b78"/>
  </radialGradient>
  <radialGradient id="eyeAmber" cx="38%" cy="34%" r="70%">
    <stop offset="0%" stop-color="#fff6cf"/>
    <stop offset="45%" stop-color="#ffb547"/>
    <stop offset="100%" stop-color="#b85f0c"/>
  </radialGradient>
  <radialGradient id="oilGlow" cx="50%" cy="35%" r="65%">
    <stop offset="0%" stop-color="#ffd9a0" stop-opacity="0.9"/>
    <stop offset="100%" stop-color="#ffb457" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="momMetal" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#ffffff"/>
    <stop offset="45%" stop-color="#d7e0e6"/>
    <stop offset="100%" stop-color="#96a3ab"/>
  </linearGradient>
  <linearGradient id="dadOrange" x1="0" y1="0" x2="0.9" y2="1">
    <stop offset="0%" stop-color="#ffb066"/>
    <stop offset="48%" stop-color="#e07b2a"/>
    <stop offset="100%" stop-color="#9c4f14"/>
  </linearGradient>
  <linearGradient id="teenBody" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#41454f"/>
    <stop offset="60%" stop-color="#282b32"/>
    <stop offset="100%" stop-color="#181a1f"/>
  </linearGradient>
  <linearGradient id="mintBody" x1="0" y1="0" x2="0.8" y2="1">
    <stop offset="0%" stop-color="#c8f5eb"/>
    <stop offset="50%" stop-color="#8fd8c8"/>
    <stop offset="100%" stop-color="#5aae9d"/>
  </linearGradient>
  <linearGradient id="grannyBody" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#eec2a0"/>
    <stop offset="55%" stop-color="#c98b6b"/>
    <stop offset="100%" stop-color="#8f5738"/>
  </linearGradient>
  <linearGradient id="dogBody" x1="0" y1="0" x2="0.8" y2="1">
    <stop offset="0%" stop-color="#b3bcc6"/>
    <stop offset="55%" stop-color="#7a8490"/>
    <stop offset="100%" stop-color="#4e5760"/>
  </linearGradient>
  <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="16"/>
  </filter>
  <filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur stdDeviation="7" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>

<!-- ==================== STUDIO BACKDROP ==================== -->
<rect width="1400" height="1400" fill="url(#wall)"/>
<g transform="translate(0,200)">
<g filter="url(#soft)" opacity="0.55">
  <ellipse cx="360" cy="290" rx="280" ry="230" fill="#42707d" opacity="0.35"/>
  <ellipse cx="1070" cy="250" rx="320" ry="250" fill="#2c5663" opacity="0.4"/>
  <ellipse cx="700" cy="540" rx="440" ry="250" fill="#0f2129" opacity="0.5"/>
  <ellipse cx="160" cy="660" rx="260" ry="210" fill="#0a161d" opacity="0.6"/>
  <ellipse cx="1300" cy="600" rx="240" ry="230" fill="#0a161d" opacity="0.5"/>
</g>
<g stroke="#08121a" stroke-width="3" opacity="0.3">
  <line x1="336" y1="-200" x2="300" y2="815"/>
  <line x1="700" y1="-200" x2="700" y2="815"/>
  <line x1="1060" y1="-200" x2="1096" y2="815"/>
</g>

<!-- overhead soft-box key light -->
<g>
  <line x1="628" y1="-200" x2="646" y2="-146" stroke="#1a1d22" stroke-width="5"/>
  <line x1="772" y1="-200" x2="754" y2="-146" stroke="#1a1d22" stroke-width="5"/>
  <rect x="556" y="-152" width="288" height="88" rx="10" fill="#1c2530" stroke="#3a4652" stroke-width="6"/>
  <rect x="570" y="-140" width="260" height="64" rx="6" fill="#f2f5f7" opacity="0.92"/>
  <ellipse cx="700" cy="30" rx="320" ry="170" fill="#ffffff" opacity="0.12" filter="url(#soft)"/>
</g>

<!-- floor -->
<rect y="815" width="1400" height="600" fill="url(#floor)"/>
<ellipse cx="700" cy="905" rx="800" ry="160" fill="#7a563e" opacity="0.12"/>
<line x1="0" y1="815" x2="1400" y2="815" stroke="#080d10" stroke-width="7"/>

<!-- woven rug -->
<ellipse cx="700" cy="912" rx="642" ry="132" fill="#3d293e" opacity="0.6"/>
<ellipse cx="700" cy="903" rx="550" ry="106" fill="#5e4157" opacity="0.78"/>
<ellipse cx="700" cy="903" rx="550" ry="106" fill="none" stroke="#c98b6b" stroke-width="8" opacity="0.5"/>
<ellipse cx="700" cy="903" rx="466" ry="84" fill="none" stroke="#c98b6b" stroke-width="4" opacity="0.32"/>
<path d="M700 820 l138 83 l-138 83 l-138 -83 z" fill="#6d4a63" opacity="0.45"/>

<!-- dropped floor props -->
<g transform="rotate(-14 268 892)">
  <rect x="248" y="872" width="40" height="40" rx="6" fill="#f2c14e"/>
  <rect x="248" y="872" width="40" height="11" rx="5" fill="#e0623a"/>
</g>
<g transform="rotate(20 1075 905)">
  <rect x="1050" y="891" width="46" height="26" rx="8" fill="#7a8490"/>
  <rect x="1092" y="897" width="16" height="10" rx="4" fill="#5f6873"/>
  <rect x="1056" y="897" width="20" height="12" rx="4" fill="#d9a441"/>
</g>
<circle cx="980" cy="880" r="9" fill="#9aa3ad"/>
<circle cx="980" cy="880" r="3" fill="#5f6873"/>
<circle cx="156" cy="900" r="8" fill="#c9553a"/>

<!-- ==================== ANCESTOR PORTRAIT ON THE WALL ==================== -->
<g transform="rotate(-4 995 200)">
  <rect x="928" y="112" width="136" height="170" rx="7" fill="#5c4732" stroke="#2a1e13" stroke-width="7"/>
  <rect x="944" y="128" width="104" height="138" rx="3" fill="#1c2c35"/>
  <rect x="966" y="178" width="62" height="58" rx="11" fill="#c9cdd2"/>
  <rect x="962" y="196" width="10" height="14" rx="3" fill="#9aa3ad"/>
  <rect x="970" y="188" width="8" height="22" rx="3" fill="#c9cdd2"/>
  <rect x="1010" y="188" width="8" height="22" rx="3" fill="#c9cdd2"/>
  <circle cx="994" cy="204" r="4.5" fill="#e0623a"/>
  <rect x="1040" y="192" width="7" height="22" rx="3" fill="#8a939c"/>
  <path d="M998 152 l-16 -12 v24 z" fill="#e79ab0"/>
  <path d="M998 152 l16 -12 v24 z" fill="#e79ab0"/>
  <circle cx="998" cy="152" r="7" fill="#d97c98"/>
</g>

<!-- ==================== GRANNY UNIT-00 (far right, on a stool) ==================== -->
<g transform="translate(1280 720) scale(1.12) translate(-1250 -720)">
  <ellipse cx="1250" cy="818" rx="86" ry="17" fill="url(#shadow)"/>
  <!-- stool -->
  <line x1="1228" y1="722" x2="1212" y2="812" stroke="#5a3f2a" stroke-width="9" stroke-linecap="round"/>
  <line x1="1272" y1="722" x2="1292" y2="812" stroke="#5a3f2a" stroke-width="9" stroke-linecap="round"/>
  <line x1="1250" y1="726" x2="1250" y2="814" stroke="#4a3322" stroke-width="8" stroke-linecap="round"/>
  <ellipse cx="1250" cy="719" rx="67" ry="18" fill="#7a5a3c"/>
  <ellipse cx="1250" cy="713" rx="67" ry="16" fill="#8f6c48"/>
  <ellipse cx="1250" cy="710" rx="58" ry="12" fill="#c98b6b"/>
  <!-- cane -->
  <path d="M1312 706 q22 -8 6 -26" stroke="#8a6a48" stroke-width="8" fill="none" stroke-linecap="round"/>
  <line x1="1312" y1="706" x2="1322" y2="812" stroke="#8a6a48" stroke-width="8" stroke-linecap="round"/>
  <!-- legs -->
  <rect x="1258" y="778" width="20" height="34" rx="8" fill="#8f5738"/>
  <ellipse cx="1268" cy="812" rx="16" ry="8" fill="#6f4327"/>
  <rect x="1216" y="742" width="18" height="30" rx="8" fill="#8f5738" transform="rotate(14 1225 757)"/>
  <ellipse cx="1224" cy="772" rx="15" ry="8" fill="#6f4327"/>
  <!-- hunched torso -->
  <g transform="rotate(15 1250 700)">
    <rect x="1210" y="556" width="80" height="132" rx="36" fill="url(#grannyBody)"/>
    <!-- shawl -->
    <path d="M1200 572 q50 -32 100 0 l10 76 q-60 28 -120 0 z" fill="#4f7f7a" opacity="0.92"/>
    <path d="M1200 648 q60 26 120 0" stroke="#3e6864" stroke-width="5" fill="none"/>
    <g stroke="#3e6864" stroke-width="4" opacity="0.8">
      <line x1="1210" y1="654" x2="1212" y2="666"/>
      <line x1="1226" y1="658" x2="1228" y2="670"/>
      <line x1="1244" y1="660" x2="1246" y2="672"/>
      <line x1="1262" y1="660" x2="1264" y2="672"/>
      <line x1="1280" y1="658" x2="1282" y2="670"/>
      <line x1="1296" y1="654" x2="1298" y2="666"/>
    </g>
    <!-- rust -->
    <path d="M1272 600 q10 18 0 34 q-12 -14 0 -34 z" fill="#7a3d18" opacity="0.7"/>
  </g>
  <!-- knitting -->
  <g>
    <circle cx="1256" cy="662" r="22" fill="#c96a86"/>
    <path d="M1236 656 q22 -12 40 4 M1240 672 q20 10 34 -4" stroke="#a84f68" stroke-width="4" fill="none"/>
    <line x1="1206" y1="646" x2="1290" y2="598" stroke="#c9cdd2" stroke-width="5" stroke-linecap="round"/>
    <line x1="1218" y1="612" x2="1298" y2="656" stroke="#c9cdd2" stroke-width="5" stroke-linecap="round"/>
    <circle cx="1204" cy="648" r="7" fill="#9aa3ad"/>
    <circle cx="1292" cy="596" r="7" fill="#9aa3ad"/>
    <path d="M1240 684 l6 92 q34 12 66 -6 l-6 -84 q-34 14 -66 -2 z" fill="#5f8f8a"/>
    <g stroke="#7fb0aa" stroke-width="5">
      <line x1="1248" y1="700" x2="1300" y2="694"/>
      <line x1="1250" y1="722" x2="1302" y2="716"/>
      <line x1="1252" y1="744" x2="1304" y2="738"/>
      <line x1="1254" y1="766" x2="1306" y2="760"/>
    </g>
  </g>
  <!-- arm holding needles -->
  <path d="M1218 596 q-14 40 6 66" stroke="#c98b6b" stroke-width="24" fill="none" stroke-linecap="round"/>
  <path d="M1288 596 q16 34 -4 60" stroke="#c98b6b" stroke-width="24" fill="none" stroke-linecap="round"/>
  <!-- head -->
  <g transform="rotate(12 1244 520)">
    <circle cx="1244" cy="516" r="43" fill="url(#grannyBody)"/>
    <!-- coiled wire bun -->
    <g fill="none" stroke="#9aa3ad" stroke-width="5">
      <circle cx="1280" cy="492" r="13"/>
      <circle cx="1288" cy="508" r="9"/>
      <circle cx="1278" cy="520" r="7"/>
    </g>
    <!-- bent antenna -->
    <path d="M1224 476 q-12 -26 -30 -30" stroke="#9aa3ad" stroke-width="4" fill="none"/>
    <circle cx="1192" cy="444" r="6" fill="#c0392b"/>
    <!-- big round glasses -->
    <circle cx="1226" cy="520" r="18" fill="#bfe6e0" fill-opacity="0.35" stroke="#d9a441" stroke-width="5"/>
    <circle cx="1264" cy="518" r="18" fill="#bfe6e0" fill-opacity="0.35" stroke="#d9a441" stroke-width="5"/>
    <line x1="1244" y1="520" x2="1246" y2="519" stroke="#d9a441" stroke-width="5"/>
    <line x1="1208" y1="518" x2="1196" y2="512" stroke="#d9a441" stroke-width="5"/>
    <line x1="1282" y1="516" x2="1294" y2="510" stroke="#d9a441" stroke-width="5"/>
    <!-- eyes: one dim / half asleep -->
    <circle cx="1228" cy="522" r="4.5" fill="#2a1f14"/>
    <circle cx="1262" cy="520" r="4.5" fill="#2a1f14" opacity="0.4"/>
    <!-- little smile -->
    <path d="M1236 542 q10 8 20 0" stroke="#6f4327" stroke-width="4" fill="none" stroke-linecap="round"/>
  </g>
</g>

<!-- ==================== DAD "BOLT-7" (right of centre, leaning in) ==================== -->
<g transform="translate(1030 815) scale(0.86) translate(-1030 -815) rotate(2 1030 815)">
  <ellipse cx="1030" cy="818" rx="126" ry="21" fill="url(#shadow)"/>
  <!-- legs -->
  <rect x="970" y="596" width="48" height="216" rx="15" fill="#333a42"/>
  <rect x="1042" y="596" width="48" height="216" rx="15" fill="#2b323a"/>
  <circle cx="994" cy="700" r="9" fill="#1c2228"/>
  <circle cx="1066" cy="700" r="9" fill="#1c2228"/>
  <!-- boots -->
  <path d="M956 798 h76 v10 q0 16 -14 16 h-76 q-12 0 -12 -13 z" fill="#20262c"/>
  <path d="M1030 798 h76 v6 q0 20 -14 20 h-76 q-12 0 -12 -13 z" fill="#191f25"/>
  <!-- torso -->
  <path d="M946 434 L1114 434 L1130 600 L930 600 Z" fill="url(#dadOrange)"/>
  <!-- hazard stripe plate -->
  <path d="M986 556 l96 0 l-6 40 l-84 0 z" fill="#3a4048"/>
  <g stroke="#f2c14e" stroke-width="6" opacity="0.9">
    <line x1="996" y1="594" x2="1012" y2="558"/>
    <line x1="1016" y1="594" x2="1032" y2="558"/>
    <line x1="1036" y1="594" x2="1052" y2="558"/>
    <line x1="1056" y1="594" x2="1072" y2="558"/>
  </g>
  <!-- chest plate -->
  <rect x="988" y="452" width="84" height="96" rx="14" fill="#3a4048"/>
  <rect x="1000" y="466" width="60" height="12" rx="6" fill="#20262c"/>
  <circle cx="1010" cy="512" r="7" fill="#e0623a"/>
  <circle cx="1030" cy="512" r="7" fill="#5fbf6a"/>
  <circle cx="1050" cy="512" r="7" fill="#20262c"/>
  <!-- shoulders -->
  <circle cx="944" cy="450" r="35" fill="url(#dadOrange)"/>
  <circle cx="1116" cy="450" r="35" fill="url(#dadOrange)"/>
  <!-- dented shoulder notch -->
  <path d="M912 436 q-14 12 -6 30 q14 -6 16 -22 z" fill="#8a4a24" opacity="0.85"/>
  <!-- rust patches -->
  <path d="M1104 560 q16 16 4 36 q-18 -14 -4 -36 z" fill="#6e3a1c" opacity="0.7"/>
  <path d="M962 508 q12 10 2 24 q-14 -8 -2 -24 z" fill="#6e3a1c" opacity="0.55"/>
  <!-- head -->
  <g transform="rotate(-2 1030 350)">
    <rect x="964" y="284" width="132" height="132" rx="30" fill="url(#dadOrange)"/>
    <!-- big camera lens eye -->
    <circle cx="1008" cy="342" r="31" fill="#1a1f24"/>
    <circle cx="1008" cy="342" r="23" fill="url(#eyeAmber)"/>
    <circle cx="1008" cy="342" r="9" fill="#2a1a08"/>
    <circle cx="1000" cy="334" r="5" fill="#ffffff" opacity="0.85"/>
    <!-- small mismatched eye -->
    <circle cx="1072" cy="348" r="16" fill="#1a1f24"/>
    <circle cx="1072" cy="348" r="10" fill="url(#eyeAmber)"/>
    <circle cx="1072" cy="348" r="4" fill="#2a1a08"/>
    <!-- bolt brows -->
    <rect x="982" y="302" width="48" height="11" rx="5" fill="#2a1f14" transform="rotate(-8 1006 307)"/>
    <rect x="1050" y="310" width="42" height="10" rx="5" fill="#2a1f14" transform="rotate(11 1071 315)"/>
    <!-- eager grin -->
    <path d="M986 382 q44 34 90 0" fill="none" stroke="#2a1f14" stroke-width="7" stroke-linecap="round"/>
    <line x1="1008" y1="388" x2="1006" y2="400" stroke="#2a1f14" stroke-width="5"/>
    <line x1="1031" y1="396" x2="1031" y2="408" stroke="#2a1f14" stroke-width="5"/>
    <line x1="1054" y1="388" x2="1056" y2="400" stroke="#2a1f14" stroke-width="5"/>
    <!-- bent antenna -->
    <path d="M1028 284 q6 -30 36 -34" stroke="#9aa3ad" stroke-width="6" fill="none" stroke-linecap="round"/>
    <circle cx="1066" cy="250" r="8" fill="#e0623a"/>
    <!-- side bolt -->
    <circle cx="1096" cy="376" r="8" fill="#8a939c"/>
  </g>
  <!-- oil drip under chin -->
  <path d="M1020 418 q6 22 -2 40 q-10 -18 2 -40 z" fill="#1a1f24" opacity="0.8"/>
  <!-- LEFT arm reaching toward mum (never quite touching) -->
  <path d="M944 452 q-54 34 -80 84" fill="none" stroke="#e07b2a" stroke-width="35" stroke-linecap="round"/>
  <path d="M944 452 q-54 34 -80 84" fill="none" stroke="#f7ab63" stroke-width="12" stroke-linecap="round" opacity="0.45"/>
  <g transform="rotate(-12 864 544)">
    <rect x="838" y="520" width="46" height="48" rx="15" fill="#f0a05a"/>
    <line x1="845" y1="524" x2="838" y2="498" stroke="#f0a05a" stroke-width="9" stroke-linecap="round"/>
    <line x1="857" y1="519" x2="854" y2="492" stroke="#f0a05a" stroke-width="9" stroke-linecap="round"/>
    <line x1="869" y1="519" x2="872" y2="494" stroke="#f0a05a" stroke-width="9" stroke-linecap="round"/>
    <line x1="880" y1="526" x2="888" y2="504" stroke="#f0a05a" stroke-width="9" stroke-linecap="round"/>
  </g>
  <!-- RIGHT arm: stiff thumbs-up -->
  <path d="M1116 452 q46 42 40 96" fill="none" stroke="#e07b2a" stroke-width="33" stroke-linecap="round"/>
  <g transform="rotate(6 1154 558)">
    <rect x="1130" y="540" width="54" height="48" rx="16" fill="#f0a05a"/>
    <rect x="1160" y="506" width="19" height="42" rx="9" fill="#f0a05a"/>
    <line x1="1138" y1="560" x2="1152" y2="560" stroke="#c96a20" stroke-width="3"/>
    <line x1="1138" y1="570" x2="1152" y2="570" stroke="#c96a20" stroke-width="3"/>
  </g>
</g>

<!-- ==================== MUM "PEARL" + BABY (centre) ==================== -->
<g transform="rotate(-3 760 815)">
  <ellipse cx="760" cy="818" rx="118" ry="18" fill="url(#shadow)"/>
  <!-- legs -->
  <rect x="716" y="716" width="25" height="94" rx="11" fill="#cdd6dc"/>
  <rect x="779" y="716" width="25" height="94" rx="11" fill="#c2ccd3"/>
  <ellipse cx="728" cy="810" rx="25" ry="9" fill="#9aa6ad"/>
  <ellipse cx="792" cy="810" rx="25" ry="9" fill="#9aa6ad"/>
  <!-- elegant skirt -->
  <path d="M700 542 L820 542 Q842 700 854 786 Q760 818 666 786 Q678 700 700 542 Z" fill="url(#momMetal)"/>
  <path d="M744 550 L734 800" stroke="#c2ccd3" stroke-width="3" fill="none" opacity="0.8"/>
  <path d="M792 550 L802 800" stroke="#c2ccd3" stroke-width="3" fill="none" opacity="0.8"/>
  <rect x="686" y="518" width="148" height="36" rx="13" fill="#2fb3a8"/>
  <circle cx="760" cy="536" r="8" fill="#d9a441"/>
  <!-- torso -->
  <path d="M706 416 L814 416 Q834 438 826 528 L694 528 Q686 438 706 416 Z" fill="url(#momMetal)"/>
  <circle cx="730" cy="468" r="10" fill="#2fb3a8" opacity="0.9"/>
  <circle cx="790" cy="468" r="10" fill="#2fb3a8" opacity="0.9"/>
  <rect x="744" y="450" width="32" height="54" rx="15" fill="#e6edf1"/>
  <!-- flower in chest port -->
  <line x1="762" y1="450" x2="762" y2="430" stroke="#3a7a4a" stroke-width="3"/>
  <circle cx="762" cy="428" r="8" fill="#e0623a"/>
  <circle cx="762" cy="428" r="3.5" fill="#f2c14e"/>
  <!-- neck -->
  <rect x="746" y="388" width="28" height="42" rx="11" fill="#9aa6ad"/>
  <!-- shoulders -->
  <circle cx="708" cy="430" r="25" fill="url(#momMetal)"/>
  <circle cx="812" cy="430" r="25" fill="url(#momMetal)"/>
  <!-- head, tilted away / looking up-left -->
  <g transform="rotate(-10 760 336)">
    <rect x="710" y="258" width="100" height="136" rx="44" fill="url(#momMetal)"/>
    <rect x="722" y="286" width="76" height="88" rx="26" fill="#0e2029"/>
    <ellipse cx="748" cy="320" rx="8" ry="13" fill="url(#eyeCyan)"/>
    <ellipse cx="778" cy="316" rx="8" ry="13" fill="url(#eyeCyan)"/>
    <!-- tight, patient smile -->
    <path d="M744 350 q16 9 32 -2" stroke="#2fb3a8" stroke-width="4" fill="none" stroke-linecap="round"/>
    <circle cx="732" cy="343" r="7" fill="#2fb3a8" opacity="0.4"/>
    <circle cx="792" cy="340" r="7" fill="#2fb3a8" opacity="0.4"/>
    <!-- antenna with little loop -->
    <path d="M760 258 q4 -34 28 -44" stroke="#d9a441" stroke-width="5" fill="none" stroke-linecap="round"/>
    <circle cx="791" cy="210" r="9" fill="none" stroke="#d9a441" stroke-width="5"/>
  </g>
  <!-- right arm hanging, tense -->
  <path d="M812 430 q42 62 22 130" stroke="#e8eef2" stroke-width="27" fill="none" stroke-linecap="round"/>
  <circle cx="832" cy="568" r="17" fill="#cdd6dc"/>
  <!-- left arm: upper, then baby, then forearm cradling -->
  <path d="M708 430 q-40 38 -32 96" stroke="#e8eef2" stroke-width="27" fill="none" stroke-linecap="round"/>
  <g>
    <!-- BABY -->
    <g transform="rotate(-8 660 504)">
      <ellipse cx="662" cy="512" rx="55" ry="61" fill="#f2e6d0"/>
      <path d="M612 494 q50 -22 100 0" stroke="#e79ab0" stroke-width="11" fill="none"/>
      <path d="M614 540 q48 20 96 0" stroke="#e79ab0" stroke-width="11" fill="none"/>
      <circle cx="658" cy="460" r="35" fill="#f2e6d0"/>
      <circle cx="643" cy="456" r="5.5" fill="#2a2f36"/>
      <path d="M668 449 q8 6 0 11" stroke="#2a2f36" stroke-width="4" fill="none" stroke-linecap="round"/>
      <circle cx="658" cy="476" r="9" fill="#e79ab0"/>
      <circle cx="658" cy="476" r="3.4" fill="#a84f68"/>
      <path d="M658 425 q2 -18 16 -23" stroke="#d9a441" stroke-width="4" fill="none"/>
      <circle cx="676" cy="400" r="6" fill="none" stroke="#d9a441" stroke-width="4"/>
      <circle cx="640" cy="482" r="5" fill="#e79ab0" opacity="0.5"/>
      <circle cx="676" cy="480" r="5" fill="#e79ab0" opacity="0.5"/>
    </g>
    <!-- forearm over baby -->
    <path d="M676 526 q34 44 86 34" stroke="#e8eef2" stroke-width="25" fill="none" stroke-linecap="round"/>
    <circle cx="756" cy="558" r="16" fill="#cdd6dc"/>
  </g>
</g>

<!-- ==================== TODDLER "SPROCKET" (on crate) ==================== -->
<g transform="rotate(3 506 700)">
  <ellipse cx="506" cy="818" rx="84" ry="16" fill="url(#shadow)"/>
  <!-- crate -->
  <g transform="rotate(-2 506 758)">
    <rect x="452" y="700" width="108" height="116" rx="8" fill="#8a6136"/>
    <rect x="452" y="700" width="108" height="16" rx="6" fill="#a5763f"/>
    <line x1="452" y1="742" x2="560" y2="742" stroke="#6d4a28" stroke-width="4"/>
    <line x1="452" y1="778" x2="560" y2="778" stroke="#6d4a28" stroke-width="4"/>
    <line x1="506" y1="716" x2="506" y2="816" stroke="#6d4a28" stroke-width="4"/>
    <ellipse cx="480" cy="760" rx="7" ry="10" fill="#6d4a28"/>
  </g>
  <!-- stubby legs -->
  <rect x="482" y="664" width="19" height="44" rx="8" fill="#6fb8a8"/>
  <rect x="513" y="664" width="19" height="44" rx="8" fill="#6fb8a8"/>
  <ellipse cx="492" cy="706" rx="17" ry="7" fill="#4f9a8b"/>
  <ellipse cx="522" cy="706" rx="17" ry="7" fill="#4f9a8b"/>
  <!-- egg body -->
  <ellipse cx="507" cy="638" rx="47" ry="49" fill="url(#mintBody)"/>
  <ellipse cx="507" cy="648" rx="27" ry="25" fill="#eafaf4" opacity="0.8"/>
  <circle cx="507" cy="648" r="8" fill="#e0623a"/>
  <!-- arms flung up -->
  <path d="M468 620 q-28 -26 -16 -58" stroke="#8fd8c8" stroke-width="18" fill="none" stroke-linecap="round"/>
  <path d="M546 620 q28 -26 16 -58" stroke="#8fd8c8" stroke-width="18" fill="none" stroke-linecap="round"/>
  <circle cx="451" cy="556" r="12" fill="#6fb8a8"/>
  <circle cx="562" cy="556" r="12" fill="#6fb8a8"/>
  <!-- toy block -->
  <g transform="rotate(18 568 550)">
    <rect x="554" y="534" width="30" height="30" rx="5" fill="#f2c14e"/>
    <rect x="554" y="534" width="30" height="8" rx="4" fill="#e0623a"/>
    <path d="M569 546 l3 6 l7 1 l-5 5 l1 7 l-6 -3 l-6 3 l1 -7 l-5 -5 l7 -1 z" fill="#e0623a"/>
  </g>
  <!-- wiggly motion marks -->
  <path d="M432 542 q-16 16 -8 38" stroke="#ffe3b0" stroke-width="4" fill="none" opacity="0.7" stroke-linecap="round"/>
  <path d="M582 542 q16 16 8 38" stroke="#ffe3b0" stroke-width="4" fill="none" opacity="0.7" stroke-linecap="round"/>
  <!-- big head -->
  <circle cx="507" cy="562" r="54" fill="url(#mintBody)"/>
  <rect x="473" y="534" width="68" height="56" rx="20" fill="#eafaf4" opacity="0.55"/>
  <!-- mismatched, cross-eyed -->
  <circle cx="489" cy="558" r="16" fill="#ffffff"/>
  <circle cx="494" cy="560" r="8.5" fill="#2a2f36"/>
  <circle cx="523" cy="562" r="10.5" fill="#ffffff"/>
  <circle cx="519" cy="563" r="5" fill="#2a2f36"/>
  <!-- open, surprised mouth -->
  <circle cx="507" cy="588" r="7.5" fill="#c9553a"/>
  <circle cx="474" cy="580" r="7" fill="#e79ab0" opacity="0.6"/>
  <circle cx="539" cy="582" r="7" fill="#e79ab0" opacity="0.6"/>
  <!-- spring antenna -->
  <path d="M507 510 l-9 -11 l18 -8 l-18 -8 l18 -8" stroke="#8a939c" stroke-width="5" fill="none" stroke-linejoin="round" stroke-linecap="round"/>
  <circle cx="512" cy="467" r="10" fill="url(#eyeAmber)" filter="url(#glow)"/>
</g>

<!-- ==================== TEEN "NULL" (far left, slouching away) ==================== -->
<g transform="rotate(-7 322 815)">
  <ellipse cx="322" cy="818" rx="104" ry="18" fill="url(#shadow)"/>
  <!-- long legs -->
  <path d="M312 596 L296 720 L284 802" stroke="#2a2d34" stroke-width="26" fill="none" stroke-linecap="round"/>
  <path d="M344 596 L370 704 L394 802" stroke="#2a2d34" stroke-width="26" fill="none" stroke-linecap="round"/>
  <path d="M314 606 L300 700" stroke="#7b5ea7" stroke-width="5" opacity="0.8"/>
  <path d="M348 606 L368 690" stroke="#7b5ea7" stroke-width="5" opacity="0.8"/>
  <!-- sneakers -->
  <path d="M264 798 h48 q8 0 8 10 q0 12 -12 12 h-48 q-10 0 -10 -11 z" fill="#16181d"/>
  <path d="M372 798 h54 q8 0 8 10 q0 12 -12 12 h-54 q-10 0 -10 -11 z" fill="#16181d"/>
  <!-- hoodie torso -->
  <path d="M290 428 q-12 92 4 178 l70 0 q12 -88 2 -178 q-38 -24 -76 0 z" fill="url(#teenBody)"/>
  <path d="M298 434 q26 36 56 2 q-16 -24 -28 -26 q-16 2 -28 24 z" fill="#3a3d46"/>
  <path d="M300 560 h60 l-6 42 h-48 z" fill="#3a3d46"/>
  <line x1="320" y1="450" x2="316" y2="496" stroke="#7b5ea7" stroke-width="4"/>
  <line x1="342" y1="450" x2="346" y2="496" stroke="#7b5ea7" stroke-width="4"/>
  <circle cx="316" cy="500" r="4" fill="#d9d9d9"/>
  <circle cx="346" cy="500" r="4" fill="#d9d9d9"/>
  <!-- crossed arms -->
  <path d="M298 468 q-8 58 26 68" stroke="#33363f" stroke-width="26" fill="none" stroke-linecap="round"/>
  <path d="M384 468 q10 58 -32 62" stroke="#2c2f37" stroke-width="26" fill="none" stroke-linecap="round"/>
  <!-- glowing phone -->
  <ellipse cx="352" cy="540" rx="30" ry="38" fill="#35d6e0" opacity="0.25" filter="url(#glow)"/>
  <g transform="rotate(-18 348 528)">
    <rect x="330" y="510" width="36" height="54" rx="8" fill="#0d141c"/>
    <rect x="334" y="514" width="28" height="46" rx="5" fill="url(#eyeCyan)"/>
  </g>
  <circle cx="330" cy="540" r="12" fill="#33363f"/>
  <circle cx="374" cy="536" r="12" fill="#2c2f37"/>
  <!-- head tilted down at the phone -->
  <g transform="rotate(20 338 398)">
    <rect x="296" y="338" width="84" height="94" rx="23" fill="#2a2d34"/>
    <rect x="306" y="352" width="64" height="62" rx="17" fill="#0d141c"/>
    <!-- half-lidded, unimpressed eyes -->
    <rect x="315" y="376" width="17" height="7" rx="3" fill="url(#eyeCyan)"/>
    <rect x="343" y="376" width="17" height="7" rx="3" fill="url(#eyeCyan)"/>
    <line x1="312" y1="374" x2="334" y2="374" stroke="#2a2d34" stroke-width="6"/>
    <line x1="340" y1="374" x2="362" y2="374" stroke="#2a2d34" stroke-width="6"/>
    <line x1="326" y1="400" x2="352" y2="400" stroke="#2fb3a8" stroke-width="3"/>
    <!-- headphones -->
    <path d="M300 370 q36 -48 76 -2" stroke="#c0392b" stroke-width="7" fill="none"/>
    <circle cx="298" cy="392" r="21" fill="#1a1d22"/>
    <circle cx="298" cy="392" r="10" fill="#c0392b"/>
    <circle cx="378" cy="392" r="21" fill="#1a1d22"/>
    <circle cx="378" cy="392" r="10" fill="#c0392b"/>
    <!-- antenna -->
    <path d="M338 338 q2 -24 20 -32" stroke="#9aa3ad" stroke-width="4" fill="none"/>
    <circle cx="358" cy="304" r="6" fill="#7b5ea7"/>
    <!-- tiny heart sticker on cheek -->
    <path d="M304 404 q4 -6 8 0 q-4 6 -8 0 z" fill="#c0392b" opacity="0.8"/>
  </g>
</g>

<!-- ==================== PET ROBO-CORG "BIT" (photobombing, front left) ==================== -->
<g transform="rotate(-2 150 780)">
  <ellipse cx="150" cy="816" rx="84" ry="16" fill="url(#shadow)"/>
  <!-- awkwardly splayed back leg -->
  <path d="M118 786 q-42 6 -54 22" stroke="#7a8490" stroke-width="18" fill="none" stroke-linecap="round"/>
  <ellipse cx="62" cy="810" rx="17" ry="10" fill="#565f69"/>
  <!-- haunch -->
  <ellipse cx="140" cy="766" rx="47" ry="50" fill="url(#dogBody)"/>
  <!-- chest and front legs -->
  <rect x="146" y="688" width="46" height="122" rx="21" fill="url(#dogBody)"/>
  <rect x="150" y="790" width="17" height="26" rx="7" fill="#565f69"/>
  <rect x="173" y="790" width="17" height="26" rx="7" fill="#565f69"/>
  <!-- head -->
  <g transform="rotate(-8 182 660)">
    <rect x="152" y="620" width="68" height="62" rx="19" fill="url(#dogBody)"/>
    <rect x="198" y="648" width="32" height="26" rx="11" fill="#9aa3ad"/>
    <rect x="224" y="656" width="13" height="11" rx="4" fill="#2a2f36"/>
    <circle cx="176" cy="644" r="7.5" fill="#1a1d22"/>
    <circle cx="177" cy="642" r="2.5" fill="#ffffff"/>
    <circle cx="199" cy="640" r="5" fill="#1a1d22"/>
    <circle cx="200" cy="639" r="2" fill="#ffffff"/>
    <!-- one ear up, one ear flopped -->
    <path d="M158 620 l-12 -36 l28 13 z" fill="#565f69"/>
    <path d="M208 622 q30 10 20 36 q-22 6 -28 -20 z" fill="#565f69"/>
    <!-- collar -->
    <rect x="150" y="684" width="62" height="12" rx="5" fill="#b5722e"/>
    <circle cx="181" cy="698" r="7" fill="#d9a441"/>
  </g>
  <!-- wagging tail -->
  <path d="M110 738 q-32 -26 -16 -56" stroke="#7a8490" stroke-width="16" fill="none" stroke-linecap="round"/>
  <g stroke="#ffffff" stroke-width="3" fill="none" opacity="0.5" stroke-linecap="round">
    <path d="M88 676 q-8 -10 -2 -20"/>
    <path d="M100 688 q-8 -10 -2 -20"/>
  </g>
  <!-- little question mark of confusion (shape only, no text) -->
  <path d="M232 596 q0 -16 12 -16 q12 0 12 11 q0 8 -10 12 q-3 2 -3 8" stroke="#bfe6e0" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.75"/>
  <circle cx="243" cy="620" r="4" fill="#bfe6e0" opacity="0.75"/>
</g>

</g><!-- /scene -->

<!-- ==================== LIGHT WRAP & VIGNETTE ==================== -->
<rect width="1400" height="1400" fill="url(#vig)"/>
<ellipse cx="700" cy="210" rx="620" ry="300" fill="#ffffff" opacity="0.06" filter="url(#soft)"/>
<ellipse cx="1180" cy="640" rx="220" ry="300" fill="#ffd9a0" opacity="0.05" filter="url(#soft)"/>
</svg>
'''

if __name__ == "__main__":
    svg_path = OUT / "robot_family_portrait.svg"
    svg_path.write_text(SVG, encoding="utf-8")
    print("wrote", svg_path)
