#!/usr/bin/env python3
"""Generate an awkward robot family portrait as an SVG.

The whole artwork is emitted from this script so the source stays in the
repository while only the finished image lands in ./output/.
"""

SVG = r'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 -225 1400 1400" width="1400" height="1400">
  <defs>
    <!-- ============ GRADIENTS ============ -->
    <linearGradient id="gWall" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#e9d9b8"/>
      <stop offset="0.72" stop-color="#d9c39c"/>
      <stop offset="1" stop-color="#c8ac82"/>
    </linearGradient>
    <linearGradient id="gFloor" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#a9743f"/>
      <stop offset="1" stop-color="#7c4f26"/>
    </linearGradient>
    <radialGradient id="gRug" cx="0.5" cy="0.5" r="0.6">
      <stop offset="0" stop-color="#b8543f"/>
      <stop offset="0.7" stop-color="#8f382b"/>
      <stop offset="1" stop-color="#6f2a20"/>
    </radialGradient>

    <linearGradient id="gSteel" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#eef2f7"/>
      <stop offset="0.45" stop-color="#c3ccd8"/>
      <stop offset="1" stop-color="#8b97a6"/>
    </linearGradient>
    <linearGradient id="gDad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#9dc2e0"/>
      <stop offset="0.5" stop-color="#6f9ec6"/>
      <stop offset="1" stop-color="#43688e"/>
    </linearGradient>
    <linearGradient id="gDadDark" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#5c86ad"/>
      <stop offset="1" stop-color="#33506e"/>
    </linearGradient>
    <linearGradient id="gMom" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f3c6ad"/>
      <stop offset="0.5" stop-color="#e19a78"/>
      <stop offset="1" stop-color="#c2704f"/>
    </linearGradient>
    <linearGradient id="gMomDark" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#d38a68"/>
      <stop offset="1" stop-color="#a5573a"/>
    </linearGradient>
    <linearGradient id="gTeen" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#b6f0dd"/>
      <stop offset="0.5" stop-color="#74ceb4"/>
      <stop offset="1" stop-color="#3f9c85"/>
    </linearGradient>
    <linearGradient id="gGrandpa" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#e4d29a"/>
      <stop offset="0.5" stop-color="#c3aa6c"/>
      <stop offset="1" stop-color="#93783e"/>
    </linearGradient>
    <linearGradient id="gBaby" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffe89a"/>
      <stop offset="0.5" stop-color="#f4c94f"/>
      <stop offset="1" stop-color="#d9a326"/>
    </linearGradient>
    <linearGradient id="gDog" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#d3dae3"/>
      <stop offset="1" stop-color="#8d99a7"/>
    </linearGradient>
    <linearGradient id="gCouch" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#4f8f86"/>
      <stop offset="0.55" stop-color="#3c746d"/>
      <stop offset="1" stop-color="#2c5852"/>
    </linearGradient>
    <linearGradient id="gCouchSeat" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#5ca195"/>
      <stop offset="1" stop-color="#356762"/>
    </linearGradient>
    <linearGradient id="gChair" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#b06a53"/>
      <stop offset="1" stop-color="#7d4535"/>
    </linearGradient>

    <radialGradient id="gGlow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#b6f4ff" stop-opacity="0.95"/>
      <stop offset="0.5" stop-color="#7fd8ff" stop-opacity="0.5"/>
      <stop offset="1" stop-color="#7fd8ff" stop-opacity="0"/>
    </radialGradient>

    <!-- ============ PATTERNS ============ -->
    <pattern id="pStripes" width="120" height="120" patternUnits="userSpaceOnUse">
      <rect width="120" height="120" fill="none"/>
      <rect x="0" y="0" width="45" height="120" fill="#ffffff" opacity="0.10"/>
    </pattern>
    <pattern id="pFloor" width="120" height="120" patternUnits="userSpaceOnUse">
      <rect width="120" height="120" fill="none"/>
      <line x1="0" y1="0" x2="120" y2="0" stroke="#5f3a1b" stroke-width="3" opacity="0.5"/>
      <line x1="0" y1="0" x2="0" y2="120" stroke="#5f3a1b" stroke-width="3" opacity="0.35"/>
    </pattern>
    <pattern id="pRug" width="44" height="44" patternUnits="userSpaceOnUse" patternTransform="rotate(0)">
      <rect width="44" height="44" fill="none"/>
      <circle cx="22" cy="22" r="15" fill="none" stroke="#e6c48a" stroke-width="3" opacity="0.55"/>
      <circle cx="22" cy="22" r="5" fill="#e6c48a" opacity="0.5"/>
    </pattern>
    <pattern id="pRust" width="26" height="26" patternUnits="userSpaceOnUse">
      <rect width="26" height="26" fill="none"/>
      <circle cx="8" cy="7" r="5" fill="#8a5a3c" opacity="0.75"/>
      <circle cx="20" cy="18" r="4" fill="#6f452b" opacity="0.7"/>
      <circle cx="4" cy="20" r="3" fill="#9a6a45" opacity="0.6"/>
    </pattern>

    <!-- ============ FILTERS ============ -->
    <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="10"/>
    </filter>
    <filter id="soft2" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="4"/>
    </filter>
    <filter id="vignette" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="0"/>
      <feComponentTransfer>
        <feFuncA type="identity"/>
      </feComponentTransfer>
    </filter>

    <clipPath id="clipFrame"><rect x="0" y="-225" width="1400" height="1400"/></clipPath>
  </defs>

  <g clip-path="url(#clipFrame)">
    <!-- ================= WALL & FLOOR ================= -->
    <rect x="0" y="-225" width="1400" height="935" fill="url(#gWall)"/>
    <rect x="0" y="-225" width="1400" height="935" fill="url(#pStripes)"/>
    <rect x="0" y="688" width="1400" height="26" fill="#a9835a"/>
    <rect x="0" y="714" width="1400" height="6" fill="#7d5c3a"/>

    <rect x="0" y="720" width="1400" height="455" fill="url(#gFloor)"/>
    <rect x="0" y="720" width="1400" height="455" fill="url(#pFloor)"/>

    <!-- rug -->
    <ellipse cx="720" cy="820" rx="560" ry="95" fill="url(#gRug)"/>
    <ellipse cx="720" cy="820" rx="560" ry="95" fill="url(#pRug)"/>
    <ellipse cx="720" cy="820" rx="560" ry="95" fill="none" stroke="#e6c48a" stroke-width="4" opacity="0.6"/>

    <!-- shadow under furniture -->
    <ellipse cx="720" cy="742" rx="600" ry="34" fill="#2a1c10" opacity="0.35" filter="url(#soft)"/>
    <ellipse cx="185" cy="742" rx="180" ry="28" fill="#2a1c10" opacity="0.35" filter="url(#soft)"/>

    <!-- ================= WALL DECOR ================= -->
    <!-- crooked picture frame -->
    <g transform="rotate(-6 1010 175)">
      <rect x="922" y="96" width="180" height="150" rx="6" fill="#6d4a30"/>
      <rect x="934" y="108" width="156" height="126" rx="3" fill="#f4ecd6"/>
      <rect x="942" y="116" width="140" height="98" fill="#cfe6df"/>
      <circle cx="1060" cy="146" r="16" fill="#f2d27a"/>
      <path d="M942 214 L990 168 L1024 200 L1064 156 L1082 176 L1082 214 Z" fill="#7fae8e"/>
      <path d="M942 214 L996 190 L1040 210 L1082 188 L1082 214 Z" fill="#5d8a6c"/>
      <rect x="922" y="96" width="180" height="150" rx="6" fill="none" stroke="#4f3220" stroke-width="4"/>
    </g>

    <!-- wall clock -->
    <g>
      <circle cx="185" cy="150" r="60" fill="#f3e6cb" stroke="#7a5a3a" stroke-width="8"/>
      <circle cx="185" cy="150" r="50" fill="#fbf5e6"/>
      <g stroke="#5a4430" stroke-width="4" stroke-linecap="round">
        <line x1="185" y1="108" x2="185" y2="118"/>
        <line x1="185" y1="182" x2="185" y2="192"/>
        <line x1="143" y1="150" x2="153" y2="150"/>
        <line x1="217" y1="150" x2="227" y2="150"/>
      </g>
      <line x1="185" y1="150" x2="185" y2="122" stroke="#5a4430" stroke-width="5" stroke-linecap="round"/>
      <line x1="185" y1="150" x2="208" y2="164" stroke="#5a4430" stroke-width="4" stroke-linecap="round"/>
      <circle cx="185" cy="150" r="5" fill="#7a5a3a"/>
    </g>

    <!-- bunting, slightly wonky -->
    <path d="M330 40 Q720 110 1120 30" fill="none" stroke="#8a6a48" stroke-width="4"/>
    <g>
      <polygon points="400,58 445,64 424,108" fill="#e08a6a"/>
      <polygon points="500,74 545,80 522,124" fill="#6fb0a0"/>
      <polygon points="600,85 645,90 622,134" fill="#f0c85c"/>
      <polygon points="700,92 745,95 722,140" fill="#9a8ac8"/>
      <polygon points="800,94 845,95 822,140" fill="#e08a6a"/>
      <polygon points="900,90 945,88 922,134" fill="#6fb0a0"/>
      <polygon points="1000,80 1045,76 1022,122" fill="#f0c85c"/>
    </g>

    <!-- potted plant at right -->
    <g>
      <ellipse cx="1310" cy="726" rx="70" ry="16" fill="#2a1c10" opacity="0.35" filter="url(#soft)"/>
      <path d="M1310 640 C1270 580 1235 560 1215 520 C1260 530 1295 560 1310 600 C1320 550 1350 520 1390 505 C1368 560 1340 590 1310 640 Z" fill="#5e8f63"/>
      <path d="M1310 640 C1290 600 1270 585 1250 575 C1275 585 1300 610 1310 640 Z" fill="#4c7a52"/>
      <path d="M1272 646 L1348 646 L1338 726 L1282 726 Z" fill="#b96a45"/>
      <rect x="1266" y="638" width="88" height="16" rx="5" fill="#c97952"/>
      <path d="M1272 646 L1348 646 L1338 726 L1282 726 Z" fill="url(#pRust)" opacity="0.25"/>
    </g>

    <!-- ================= COUCH ================= -->
    <g>
      <!-- back -->
      <rect x="330" y="420" width="920" height="250" rx="44" fill="url(#gCouch)"/>
      <rect x="330" y="420" width="920" height="250" rx="44" fill="none" stroke="#26504a" stroke-width="6"/>
      <!-- button tufts -->
      <g fill="#2c5852" opacity="0.8">
        <circle cx="500" cy="480" r="0"/>
      </g>
      <!-- seam between cushions -->
      <line x1="700" y1="440" x2="700" y2="648" stroke="#26504a" stroke-width="5" opacity="0.7"/>
      <line x1="880" y1="440" x2="880" y2="648" stroke="#26504a" stroke-width="5" opacity="0.7"/>
      <!-- seat -->
      <rect x="300" y="596" width="980" height="128" rx="32" fill="url(#gCouchSeat)"/>
      <rect x="300" y="596" width="980" height="128" rx="32" fill="none" stroke="#26504a" stroke-width="6"/>
      <!-- seat seam -->
      <path d="M470 600 L470 716" stroke="#26504a" stroke-width="4" opacity="0.5"/>
      <path d="M700 600 L700 716" stroke="#26504a" stroke-width="4" opacity="0.5"/>
      <path d="M930 600 L930 716" stroke="#26504a" stroke-width="4" opacity="0.5"/>
      <path d="M1140 600 L1140 716" stroke="#26504a" stroke-width="4" opacity="0.5"/>
      <!-- arms -->
      <rect x="286" y="512" width="84" height="212" rx="40" fill="#3c746d" stroke="#26504a" stroke-width="6"/>
      <rect x="1210" y="512" width="84" height="212" rx="40" fill="#3c746d" stroke="#26504a" stroke-width="6"/>
      <!-- feet -->
      <rect x="330" y="714" width="42" height="30" rx="8" fill="#5a3a26"/>
      <rect x="1208" y="714" width="42" height="30" rx="8" fill="#5a3a26"/>
      <!-- throw pillow, crooked, wedged beside Dad -->
      <g transform="rotate(-8 393 604)">
        <rect x="350" y="561" width="86" height="86" rx="20" fill="#e0a35a" stroke="#b57a37" stroke-width="4"/>
        <path d="M350 579 q43 16 86 0" fill="none" stroke="#b57a37" stroke-width="3" opacity="0.55"/>
        <circle cx="393" cy="604" r="6" fill="#b57a37"/>
      </g>
    </g>

    <!-- ================= GRANDPA ARMCHAIR ================= -->
    <g>
      <rect x="78" y="452" width="232" height="238" rx="42" fill="url(#gChair)" stroke="#5d3126" stroke-width="6"/>
      <rect x="62" y="596" width="264" height="120" rx="30" fill="#b06a53" stroke="#5d3126" stroke-width="6"/>
      <rect x="46" y="520" width="70" height="200" rx="32" fill="#9a5744" stroke="#5d3126" stroke-width="6"/>
      <rect x="272" y="520" width="70" height="200" rx="32" fill="#9a5744" stroke="#5d3126" stroke-width="6"/>
      <rect x="86" y="708" width="36" height="28" rx="8" fill="#5a3a26"/>
      <rect x="266" y="708" width="36" height="28" rx="8" fill="#5a3a26"/>
    </g>

    <!-- ================= GRANDPA ROBOT ================= -->
    <g>
      <!-- hunched torso -->
      <path d="M112 470 Q118 428 160 424 L226 424 Q268 428 274 470 L284 612 Q284 628 264 628 L122 628 Q102 628 102 612 Z"
            fill="url(#gGrandpa)" stroke="#6f5a2c" stroke-width="5"/>
      <!-- rust patches -->
      <path d="M112 540 Q128 522 150 545 L150 600 Q128 615 112 596 Z" fill="url(#pRust)" opacity="0.75"/>
      <path d="M240 470 Q262 460 274 480 L274 520 Q250 528 238 508 Z" fill="url(#pRust)" opacity="0.6"/>
      <!-- cardigan buttons -->
      <line x1="192" y1="440" x2="192" y2="620" stroke="#7a642f" stroke-width="5" opacity="0.7"/>
      <circle cx="192" cy="480" r="6" fill="#5e4a1f"/>
      <circle cx="192" cy="540" r="6" fill="#5e4a1f"/>
      <circle cx="192" cy="600" r="6" fill="#5e4a1f"/>
      <!-- left arm on armrest with cane -->
      <rect x="70" y="500" width="70" height="46" rx="22" fill="#c3aa6c" stroke="#6f5a2c" stroke-width="4" transform="rotate(24 105 523)"/>
      <circle cx="72" cy="560" r="22" fill="#d8c48f" stroke="#6f5a2c" stroke-width="4"/>
      <!-- cane -->
      <line x1="60" y1="556" x2="44" y2="726" stroke="#6b4a2f" stroke-width="10" stroke-linecap="round"/>
      <path d="M60 556 q22 -18 34 4" fill="none" stroke="#6b4a2f" stroke-width="10" stroke-linecap="round"/>
      <!-- right arm holding tumbler -->
      <rect x="258" y="492" width="74" height="44" rx="22" fill="#c3aa6c" stroke="#6f5a2c" stroke-width="4" transform="rotate(-28 295 514)"/>
      <g transform="translate(322 500)">
        <rect x="-16" y="-6" width="32" height="40" rx="6" fill="#bfe4ea" opacity="0.85" stroke="#7fa9b0" stroke-width="3"/>
        <rect x="-18" y="-12" width="36" height="12" rx="4" fill="#8a8f98"/>
      </g>
      <!-- neck -->
      <rect x="176" y="392" width="34" height="40" rx="10" fill="#9c8148"/>
      <!-- head : dented square, tilted -->
      <g transform="rotate(-7 193 340)">
        <rect x="132" y="286" width="122" height="112" rx="20" fill="url(#gGrandpa)" stroke="#6f5a2c" stroke-width="5"/>
        <!-- dents -->
        <path d="M132 330 q18 -12 30 4 q-8 16 -30 8 Z" fill="#8f7434" opacity="0.8"/>
        <circle cx="238" cy="312" r="12" fill="#8f7434" opacity="0.8"/>
        <!-- big monocle eye -->
        <circle cx="168" cy="336" r="26" fill="#f7efd8" stroke="#6f5a2c" stroke-width="5"/>
        <circle cx="172" cy="338" r="11" fill="#3a4a5a"/>
        <circle cx="176" cy="334" r="4" fill="#fff"/>
        <!-- other eye: dim small -->
        <circle cx="226" cy="336" r="3" fill="#6f5a2c"/>
        <circle cx="226" cy="336" r="9" fill="none" stroke="#6f5a2c" stroke-width="3" opacity="0.6"/>
        <!-- wire mustache -->
        <path d="M170 368 q14 -10 26 0 q12 -10 26 0" fill="none" stroke="#7a6430" stroke-width="5" stroke-linecap="round"/>
        <!-- drooping antenna -->
        <path d="M196 286 q6 -30 34 -36" fill="none" stroke="#7a6430" stroke-width="6" stroke-linecap="round"/>
        <circle cx="232" cy="249" r="8" fill="#e8d29a" stroke="#6f5a2c" stroke-width="3"/>
        <!-- crooked little smile -->
        <path d="M182 382 q16 12 32 -2" fill="none" stroke="#5e4a1f" stroke-width="4" stroke-linecap="round"/>
      </g>
      <!-- sleepy dust / bird on head -->
      <g transform="translate(212 244)">
        <ellipse cx="0" cy="0" rx="20" ry="13" fill="#7fa9c9"/>
        <circle cx="14" cy="-6" r="9" fill="#8fb8d6"/>
        <circle cx="17" cy="-8" r="2.4" fill="#1b2530"/>
        <polygon points="23,-7 31,-4 23,-2" fill="#e0a35a"/>
        <path d="M-18 -2 q-14 -6 -22 -1 q12 3 22 4 Z" fill="#6b93b3"/>
        <path d="M8 -12 q6 -12 14 -10 q-6 6 -6 12 Z" fill="#6b93b3"/>
      </g>
      <!-- legs -->
      <rect x="128" y="610" width="52" height="96" rx="12" fill="#b39a5c" stroke="#6f5a2c" stroke-width="4"/>
      <rect x="212" y="610" width="52" height="96" rx="12" fill="#b39a5c" stroke="#6f5a2c" stroke-width="4"/>
      <rect x="120" y="696" width="68" height="26" rx="10" fill="#6f5a2c"/>
      <rect x="204" y="696" width="68" height="26" rx="10" fill="#6f5a2c"/>
    </g>

    <!-- ================= DAD ROBOT ================= -->
    <g>
      <!-- thighs / lap -->
      <rect x="470" y="556" width="176" height="92" rx="26" fill="url(#gDadDark)"/>
      <!-- torso -->
      <rect x="462" y="352" width="192" height="272" rx="34" fill="url(#gDad)" stroke="#31506e" stroke-width="5"/>
      <!-- chest plate -->
      <rect x="500" y="398" width="116" height="96" rx="14" fill="#3a5a7c" stroke="#27425d" stroke-width="4"/>
      <circle cx="530" cy="430" r="8" fill="#e05c5c"/>
      <circle cx="586" cy="430" r="8" fill="#6fe0a0"/>
      <rect x="512" y="456" width="92" height="12" rx="6" fill="#27425d"/>
      <!-- shoulder pads -->
      <circle cx="470" cy="392" r="30" fill="url(#gDadDark)" stroke="#27425d" stroke-width="4"/>
      <circle cx="646" cy="392" r="30" fill="url(#gDadDark)" stroke="#27425d" stroke-width="4"/>
      <!-- crossed arms -->
      <g transform="rotate(20 558 452)">
        <rect x="452" y="424" width="212" height="54" rx="27" fill="url(#gDadDark)" stroke="#27425d" stroke-width="4"/>
      </g>
      <g transform="rotate(-20 558 494)">
        <rect x="452" y="466" width="212" height="54" rx="27" fill="url(#gDad)" stroke="#27425d" stroke-width="4"/>
      </g>
      <circle cx="452" cy="452" r="20" fill="#8fb4d4" stroke="#27425d" stroke-width="4"/>
      <circle cx="664" cy="494" r="20" fill="#8fb4d4" stroke="#27425d" stroke-width="4"/>
      <!-- neck -->
      <rect x="539" y="318" width="38" height="44" rx="10" fill="#4c7a9e" stroke="#27425d" stroke-width="4"/>
      <!-- head -->
      <g transform="rotate(-3 560 262)">
        <rect x="498" y="230" width="124" height="106" rx="18" fill="url(#gDad)" stroke="#31506e" stroke-width="5"/>
        <!-- visor -->
        <rect x="510" y="258" width="100" height="42" rx="21" fill="#16212e"/>
        <circle cx="540" cy="279" r="9" fill="#8fe8ff"/>
        <circle cx="582" cy="279" r="9" fill="#8fe8ff"/>
        <circle cx="543" cy="276" r="3" fill="#fff"/>
        <circle cx="585" cy="276" r="3" fill="#fff"/>
        <!-- angry brow over left eye -->
        <rect x="514" y="248" width="42" height="9" rx="4.5" fill="#31506e" transform="rotate(13 535 252)"/>
        <!-- mouth : flat line -->
        <rect x="536" y="312" width="48" height="7" rx="3.5" fill="#31506e"/>
        <!-- antenna nub -->
        <rect x="552" y="212" width="16" height="22" rx="6" fill="#4c7a9e"/>
        <circle cx="560" cy="210" r="8" fill="#8fe8ff"/>
        <!-- bolt ears -->
        <circle cx="496" cy="282" r="9" fill="#33506e"/>
        <circle cx="624" cy="282" r="9" fill="#33506e"/>
      </g>
      <!-- legs -->
      <rect x="494" y="596" width="56" height="118" rx="12" fill="#4c7a9e" stroke="#27425d" stroke-width="4"/>
      <rect x="566" y="596" width="56" height="118" rx="12" fill="#4c7a9e" stroke="#27425d" stroke-width="4"/>
      <rect x="486" y="700" width="72" height="28" rx="11" fill="#27425d"/>
      <rect x="558" y="700" width="72" height="28" rx="11" fill="#27425d"/>
    </g>

    <!-- ================= MOM ROBOT ================= -->
    <g>
      <!-- lap -->
      <rect x="742" y="556" width="152" height="92" rx="26" fill="url(#gMomDark)"/>
      <!-- torso : soft curve -->
      <path d="M748 400 Q748 368 786 364 L850 364 Q888 368 888 400 L900 606 Q900 626 878 626 L758 626 Q736 626 736 606 Z"
            fill="url(#gMom)" stroke="#9c4f34" stroke-width="5"/>
      <!-- apron / plate -->
      <path d="M776 412 Q818 396 860 412 L852 540 Q818 556 784 540 Z" fill="#f6e2d2" opacity="0.85" stroke="#c98a6a" stroke-width="3"/>
      <path d="M796 448 q22 -10 44 0" fill="none" stroke="#d99a78" stroke-width="4" stroke-linecap="round"/>
      <circle cx="818" cy="492" r="10" fill="#e05c7a"/>
      <!-- left arm reaching to Dad shoulder (resisted) -->
      <path d="M760 414 Q690 396 640 372" fill="none" stroke="#e19a78" stroke-width="40" stroke-linecap="round"/>
      <path d="M760 414 Q690 396 640 372" fill="none" stroke="#c2704f" stroke-width="40" stroke-linecap="round" opacity="0.25"/>
      <circle cx="634" cy="370" r="24" fill="#f3c6ad" stroke="#9c4f34" stroke-width="4"/>
      <!-- right arm down to baby -->
      <path d="M880 430 Q910 520 858 592" fill="none" stroke="#e19a78" stroke-width="38" stroke-linecap="round"/>
      <circle cx="852" cy="600" r="23" fill="#f3c6ad" stroke="#9c4f34" stroke-width="4"/>
      <!-- neck -->
      <rect x="796" y="332" width="40" height="44" rx="12" fill="#c2704f"/>
      <!-- head -->
      <ellipse cx="816" cy="282" rx="70" ry="66" fill="url(#gMom)" stroke="#9c4f34" stroke-width="5"/>
      <!-- screen face -->
      <rect x="770" y="242" width="92" height="72" rx="18" fill="#2a1620"/>
      <circle cx="798" cy="270" r="9" fill="#ffd27f"/>
      <circle cx="834" cy="270" r="9" fill="#ffd27f"/>
      <circle cx="800" cy="267" r="3" fill="#fff"/>
      <circle cx="836" cy="267" r="3" fill="#fff"/>
      <path d="M792 292 q24 20 48 0" fill="none" stroke="#ffd27f" stroke-width="5" stroke-linecap="round"/>
      <!-- worried brows -->
      <path d="M786 254 q10 -6 20 -1" fill="none" stroke="#ffd27f" stroke-width="3" stroke-linecap="round"/>
      <path d="M846 254 q-10 -6 -20 -1" fill="none" stroke="#ffd27f" stroke-width="3" stroke-linecap="round"/>
      <!-- antennae with beads -->
      <path d="M778 220 q-14 -34 -34 -40" fill="none" stroke="#c2704f" stroke-width="6" stroke-linecap="round"/>
      <circle cx="742" cy="178" r="9" fill="#ffd27f" stroke="#9c4f34" stroke-width="3"/>
      <path d="M854 220 q14 -34 34 -40" fill="none" stroke="#c2704f" stroke-width="6" stroke-linecap="round"/>
      <circle cx="890" cy="178" r="9" fill="#ffd27f" stroke="#9c4f34" stroke-width="3"/>
      <!-- earrings -->
      <circle cx="748" cy="306" r="9" fill="#ffd27f" stroke="#9c4f34" stroke-width="3"/>
      <circle cx="884" cy="306" r="9" fill="#ffd27f" stroke="#9c4f34" stroke-width="3"/>
      <!-- cheek blush -->
      <circle cx="770" cy="308" r="10" fill="#e07a7a" opacity="0.35"/>
      <circle cx="864" cy="308" r="10" fill="#e07a7a" opacity="0.35"/>
      <!-- legs -->
      <rect x="768" y="612" width="52" height="106" rx="12" fill="#c2704f" stroke="#9c4f34" stroke-width="4"/>
      <rect x="830" y="612" width="52" height="106" rx="12" fill="#c2704f" stroke="#9c4f34" stroke-width="4"/>
      <rect x="760" y="702" width="68" height="28" rx="11" fill="#9c4f34"/>
      <rect x="822" y="702" width="68" height="28" rx="11" fill="#9c4f34"/>
    </g>

    <!-- ================= TEEN ROBOT ================= -->
    <g transform="rotate(5 1035 480)">
      <!-- hips -->
      <rect x="986" y="546" width="118" height="62" rx="28" fill="#3f9c85"/>
      <!-- legs sitting, one foot tucked across the other -->
      <rect x="990" y="590" width="50" height="132" rx="14" fill="#4ba891" stroke="#2f7d69" stroke-width="4"/>
      <rect x="982" y="710" width="66" height="28" rx="11" fill="#2f7d69"/>
      <rect x="1054" y="590" width="50" height="132" rx="14" fill="#5cb8a0" stroke="#2f7d69" stroke-width="4"/>
      <rect x="1046" y="710" width="66" height="28" rx="11" fill="#2f7d69"/>
      <!-- tucked ankle over the other -->
      <rect x="1036" y="688" width="74" height="34" rx="16" fill="#5cb8a0" stroke="#2f7d69" stroke-width="4" transform="rotate(18 1073 705)"/>
      <!-- torso, hunched forward -->
      <path d="M992 392 Q992 364 1022 360 L1068 360 Q1098 364 1098 396 L1104 566 Q1104 586 1082 586 L1010 586 Q990 586 992 564 Z"
            fill="url(#gTeen)" stroke="#2f7d69" stroke-width="5"/>
      <!-- hoodie pocket -->
      <path d="M1006 494 Q1050 482 1090 494 L1086 562 Q1050 572 1012 562 Z" fill="#5cb8a0" opacity="0.85" stroke="#2f7d69" stroke-width="3"/>
      <!-- hoodie drawstrings -->
      <path d="M1022 384 q-6 26 -2 40" fill="none" stroke="#e05c9a" stroke-width="4" stroke-linecap="round"/>
      <path d="M1056 384 q6 24 4 38" fill="none" stroke="#e05c9a" stroke-width="4" stroke-linecap="round"/>
      <circle cx="1020" cy="428" r="4" fill="#e05c9a"/>
      <circle cx="1061" cy="426" r="4" fill="#e05c9a"/>
      <!-- shoulders -->
      <circle cx="994" cy="398" r="27" fill="#5cb8a0" stroke="#2f7d69" stroke-width="4"/>
      <circle cx="1094" cy="398" r="27" fill="#5cb8a0" stroke="#2f7d69" stroke-width="4"/>
      <!-- both arms folded down, clutching phone in lap -->
      <path d="M994 406 Q974 486 1020 552" fill="none" stroke="#74ceb4" stroke-width="34" stroke-linecap="round"/>
      <path d="M1094 408 Q1114 486 1070 552" fill="none" stroke="#74ceb4" stroke-width="34" stroke-linecap="round"/>
      <g transform="rotate(-22 1050 566)">
        <rect x="1028" y="538" width="42" height="64" rx="8" fill="#1c2733" stroke="#0f1720" stroke-width="3"/>
        <rect x="1033" y="544" width="32" height="50" rx="4" fill="#7fe9d0"/>
        <circle cx="1049" cy="564" r="5" fill="#1c2733"/>
        <circle cx="1049" cy="580" r="5" fill="#1c2733"/>
      </g>
      <circle cx="1022" cy="550" r="15" fill="#74ceb4" stroke="#2f7d69" stroke-width="4"/>
      <circle cx="1076" cy="556" r="15" fill="#74ceb4" stroke="#2f7d69" stroke-width="4"/>
      <!-- long drooping neck -->
      <path d="M1042 344 Q1050 308 1036 284" fill="none" stroke="#74ceb4" stroke-width="26" stroke-linecap="round"/>
      <!-- head tilted down toward the phone -->
      <g transform="rotate(16 1032 262)">
        <rect x="984" y="208" width="104" height="98" rx="26" fill="url(#gTeen)" stroke="#2f7d69" stroke-width="5"/>
        <!-- heavy-lidded LED eyes, bored -->
        <rect x="998" y="238" width="32" height="16" rx="8" fill="#0f2a24"/>
        <rect x="1042" y="238" width="32" height="16" rx="8" fill="#0f2a24"/>
        <circle cx="1016" cy="248" r="4.5" fill="#d8fff2"/>
        <circle cx="1064" cy="246" r="4.5" fill="#d8fff2"/>
        <!-- flat unimpressed mouth -->
        <rect x="1014" y="278" width="44" height="6" rx="3" fill="#2f7d69"/>
        <!-- headphones -->
        <path d="M980 246 Q978 198 1036 196 Q1092 198 1094 246" fill="none" stroke="#e05c9a" stroke-width="12" stroke-linecap="round"/>
        <rect x="968" y="238" width="26" height="46" rx="12" fill="#e05c9a" stroke="#a83a71" stroke-width="3"/>
        <rect x="1080" y="238" width="26" height="46" rx="12" fill="#e05c9a" stroke="#a83a71" stroke-width="3"/>
        <!-- LED hair spikes -->
        <path d="M1002 208 q6 -26 22 -30 q-2 16 4 26 Z" fill="#7fe9d0"/>
        <path d="M1038 202 q8 -30 26 -30 q-4 18 2 30 Z" fill="#e05c9a"/>
        <path d="M1068 212 q12 -24 28 -20 q-8 14 -8 26 Z" fill="#7fe9d0"/>
        <!-- little antenna -->
        <line x1="1030" y1="204" x2="1022" y2="178" stroke="#2f7d69" stroke-width="5" stroke-linecap="round"/>
        <circle cx="1020" cy="174" r="7" fill="#e05c9a"/>
      </g>
    </g>

    <!-- ================= BABY ROBOT (on floor, front centre) ================= -->
    <g>
      <ellipse cx="672" cy="800" rx="96" ry="24" fill="#2a1c10" opacity="0.4" filter="url(#soft)"/>
      <!-- body -->
      <path d="M610 700 Q604 646 668 642 Q732 646 726 700 L736 778 Q736 796 716 796 L620 796 Q600 796 600 778 Z"
            fill="url(#gBaby)" stroke="#b8851c" stroke-width="5"/>
      <!-- belly plate -->
      <rect x="636" y="700" width="64" height="62" rx="16" fill="#fff3c8" stroke="#d9a326" stroke-width="3"/>
      <circle cx="668" cy="720" r="7" fill="#e07a7a"/>
      <circle cx="668" cy="742" r="7" fill="#6fb0a0"/>
      <!-- arms up, reaching toward Mom -->
      <path d="M616 676 Q580 620 596 566" fill="none" stroke="#f4c94f" stroke-width="30" stroke-linecap="round"/>
      <circle cx="598" cy="560" r="18" fill="#ffe89a" stroke="#b8851c" stroke-width="4"/>
      <path d="M722 678 Q752 640 742 600" fill="none" stroke="#f4c94f" stroke-width="30" stroke-linecap="round"/>
      <circle cx="744" cy="594" r="18" fill="#ffe89a" stroke="#b8851c" stroke-width="4"/>
      <!-- legs splayed -->
      <rect x="628" y="768" width="42" height="60" rx="16" fill="#f4c94f" stroke="#b8851c" stroke-width="4"/>
      <rect x="676" y="772" width="46" height="54" rx="18" fill="#f4c94f" stroke="#b8851c" stroke-width="4" transform="rotate(22 699 799)"/>
      <ellipse cx="646" cy="828" rx="24" ry="10" fill="#d9a326"/>
      <ellipse cx="714" cy="832" rx="24" ry="10" fill="#d9a326" transform="rotate(20 714 832)"/>
      <!-- head: big round -->
      <circle cx="668" cy="592" r="58" fill="url(#gBaby)" stroke="#b8851c" stroke-width="5"/>
      <!-- huge single eye -->
      <circle cx="668" cy="590" r="30" fill="#fffdf5" stroke="#b8851c" stroke-width="4"/>
      <circle cx="668" cy="590" r="15" fill="#3a5a7c"/>
      <circle cx="674" cy="584" r="5" fill="#fff"/>
      <circle cx="668" cy="590" r="30" fill="none" stroke="#6fb0a0" stroke-width="2" opacity="0.5"/>
      <!-- happy mouth -->
      <path d="M646 626 q22 20 44 0" fill="none" stroke="#b8851c" stroke-width="5" stroke-linecap="round"/>
      <!-- tiny antenna with a bead -->
      <line x1="668" y1="536" x2="668" y2="508" stroke="#b8851c" stroke-width="6" stroke-linecap="round"/>
      <circle cx="668" cy="502" r="10" fill="#e05c5c" stroke="#a83a71" stroke-width="3"/>
      <!-- blush -->
      <circle cx="626" cy="618" r="9" fill="#e07a7a" opacity="0.4"/>
      <circle cx="710" cy="618" r="9" fill="#e07a7a" opacity="0.4"/>
    </g>

    <!-- ================= ROBOT DOG (front right) ================= -->
    <g>
      <ellipse cx="1010" cy="812" rx="110" ry="26" fill="#2a1c10" opacity="0.4" filter="url(#soft)"/>
      <!-- tail, stiff and wagging up -->
      <path d="M1100 720 q50 -20 56 -70" fill="none" stroke="#8d99a7" stroke-width="18" stroke-linecap="round"/>
      <circle cx="1158" cy="646" r="12" fill="#d3dae3" stroke="#6f7c8b" stroke-width="3"/>
      <!-- body -->
      <rect x="922" y="694" width="184" height="104" rx="44" fill="url(#gDog)" stroke="#6f7c8b" stroke-width="5"/>
      <!-- chest plate -->
      <rect x="944" y="722" width="90" height="56" rx="16" fill="#eef2f7" opacity="0.8" stroke="#9aa6b4" stroke-width="3"/>
      <circle cx="972" cy="740" r="6" fill="#8d99a7"/>
      <circle cx="1006" cy="740" r="6" fill="#8d99a7"/>
      <!-- front legs -->
      <rect x="938" y="786" width="34" height="50" rx="12" fill="#9aa6b4" stroke="#6f7c8b" stroke-width="4"/>
      <rect x="998" y="786" width="34" height="50" rx="12" fill="#9aa6b4" stroke="#6f7c8b" stroke-width="4"/>
      <!-- back legs -->
      <rect x="1060" y="782" width="38" height="54" rx="14" fill="#9aa6b4" stroke="#6f7c8b" stroke-width="4"/>
      <!-- head -->
      <g transform="rotate(-8 900 700)">
        <rect x="840" y="646" width="120" height="104" rx="34" fill="url(#gDog)" stroke="#6f7c8b" stroke-width="5"/>
        <!-- ears : one up one down -->
        <path d="M852 652 q-18 -56 12 -66 q14 30 12 62 Z" fill="#9aa6b4" stroke="#6f7c8b" stroke-width="4"/>
        <path d="M948 654 q34 -34 8 -58 q-24 18 -30 54 Z" fill="#9aa6b4" stroke="#6f7c8b" stroke-width="4"/>
        <!-- muzzle -->
        <rect x="860" y="712" width="80" height="40" rx="18" fill="#e6ebf1" stroke="#6f7c8b" stroke-width="3"/>
        <ellipse cx="900" cy="716" rx="10" ry="7" fill="#3a4652"/>
        <!-- eyes : hopeful -->
        <circle cx="872" cy="686" r="10" fill="#16212e"/>
        <circle cx="928" cy="686" r="10" fill="#16212e"/>
        <circle cx="875" cy="683" r="3.5" fill="#fff"/>
        <circle cx="931" cy="683" r="3.5" fill="#fff"/>
        <!-- tongue -->
        <path d="M892 748 q4 22 -8 26 q-12 -6 -6 -26 Z" fill="#e07a8a" stroke="#c05a6a" stroke-width="2.5"/>
        <!-- antenna -->
        <line x1="900" y1="646" x2="900" y2="616" stroke="#6f7c8b" stroke-width="5" stroke-linecap="round"/>
        <circle cx="900" cy="612" r="8" fill="#ffd27f" stroke="#c99a3a" stroke-width="3"/>
      </g>
    </g>

    <!-- ================= FOREGROUND / PHOTO EFFECTS ================= -->
    <!-- flash glare -->
    <circle cx="170" cy="90" r="180" fill="url(#gGlow)" opacity="0.55" filter="url(#soft)"/>
    <circle cx="170" cy="90" r="60" fill="#ffffff" opacity="0.5" filter="url(#soft)"/>
    <!-- vignette -->
    <rect x="0" y="0" width="1400" height="950" fill="none"/>
    <radialGradient id="gVig" cx="0.5" cy="0.48" r="0.75">
      <stop offset="0.6" stop-color="#000000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000000" stop-opacity="0.4"/>
    </radialGradient>
    <rect x="0" y="-225" width="1400" height="1400" fill="url(#gVig)"/>
    <!-- inner photo border -->
    <rect x="18" y="-207" width="1364" height="1364" fill="none" stroke="#f5ecd8" stroke-width="14" opacity="0.9"/>
    <rect x="30" y="-195" width="1340" height="1340" fill="none" stroke="#c9b790" stroke-width="3" opacity="0.8"/>
  </g>
</svg>
'''


def main() -> None:
    with open("output/awkward_robot_family.svg", "w", encoding="utf-8") as fh:
        fh.write(SVG)
    print("wrote output/awkward_robot_family.svg", len(SVG), "bytes")


if __name__ == "__main__":
    main()
