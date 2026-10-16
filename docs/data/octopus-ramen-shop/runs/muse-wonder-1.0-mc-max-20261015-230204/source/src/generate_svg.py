#!/usr/bin/env python3
"""Generate an SVG illustration: octopus chef at a ramen booth (yatai)."""
import pathlib

OUT = pathlib.Path("output/octopus-ramen-chef.svg")
OUT.parent.mkdir(parents=True, exist_ok=True)

svg = r'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900" role="img" aria-labelledby="title desc">
  <title id="title">Octopus chef at a ramen booth</title>
  <desc id="desc">A cheerful pink octopus wearing a chef hat, serving ramen from a cozy Japanese yatai stall with lanterns, noren curtains and steaming bowls.</desc>
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FFF3D6"/>
      <stop offset="55%" stop-color="#FFE3B3"/>
      <stop offset="100%" stop-color="#FFD29A"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="38%" r="65%">
      <stop offset="0%" stop-color="#FFF8E6" stop-opacity="0.95"/>
      <stop offset="55%" stop-color="#FFE9B8" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="#FFE9B8" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="octoGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FF8FB1"/>
      <stop offset="45%" stop-color="#FF6B9D"/>
      <stop offset="100%" stop-color="#F4507A"/>
    </linearGradient>
    <linearGradient id="octoDark" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FF7AA8"/>
      <stop offset="100%" stop-color="#E84A73"/>
    </linearGradient>
    <linearGradient id="woodGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#D9A06B"/>
      <stop offset="100%" stop-color="#B67D45"/>
    </linearGradient>
    <linearGradient id="woodDark" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#9C6B3F"/>
      <stop offset="100%" stop-color="#7A4E2A"/>
    </linearGradient>
    <linearGradient id="roofGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#E94E3C"/>
      <stop offset="100%" stop-color="#C1271D"/>
    </linearGradient>
    <linearGradient id="brothGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FFC94D"/>
      <stop offset="100%" stop-color="#FF9E2E"/>
    </linearGradient>
    <linearGradient id="hatGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="#FFEAF0"/>
    </linearGradient>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#7A2E1F" flood-opacity="0.18"/>
    </filter>
    <filter id="cardShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#5C2A12" flood-opacity="0.22"/>
    </filter>
  </defs>

  <!-- ===== BACKGROUND ===== -->
  <rect width="1200" height="900" fill="url(#bgGrad)"/>
  <ellipse cx="600" cy="380" rx="620" ry="420" fill="url(#glow)"/>
  <!-- bokeh / string light dots -->
  <g opacity="0.55" fill="#FFB84D">
    <circle cx="92" cy="108" r="5"/><circle cx="185" cy="72" r="4"/><circle cx="1025" cy="88" r="5"/>
    <circle cx="1108" cy="142" r="4"/><circle cx="58" cy="228" r="4"/><circle cx="1148" cy="268" r="4"/>
  </g>
  <!-- string lights wire -->
  <path d="M 38 92 Q 300 138 600 92 T 1162 92" fill="none" stroke="#8B5E3C" stroke-width="2.5" stroke-linecap="round" opacity="0.7"/>
  <g>
    <circle cx="150" cy="108" r="10" fill="#FFD166" stroke="#E9A426" stroke-width="1.5"/><circle cx="150" cy="108" r="4" fill="#FFF3B0"/>
    <circle cx="320" cy="118" r="10" fill="#FF8FA3" stroke="#E56B81" stroke-width="1.5"/><circle cx="320" cy="118" r="4" fill="#FFE5EC"/>
    <circle cx="490" cy="104" r="10" fill="#FFD166" stroke="#E9A426" stroke-width="1.5"/>
    <circle cx="660" cy="102" r="10" fill="#7FE7C4" stroke="#3DBE96" stroke-width="1.5"/>
    <circle cx="830" cy="110" r="10" fill="#FFD166" stroke="#E9A426" stroke-width="1.5"/>
    <circle cx="990" cy="108" r="10" fill="#FF8FA3" stroke="#E56B81" stroke-width="1.5"/>
  </g>

  <!-- ground shadow -->
  <ellipse cx="600" cy="832" rx="520" ry="28" fill="#D98A3D" opacity="0.22"/>
  <ellipse cx="600" cy="828" rx="440" ry="20" fill="#B96A1F" opacity="0.14"/>

  <!-- ===== BOOTH STRUCTURE ===== -->
  <!-- back wall -->
  <rect x="148" y="178" width="904" height="452" rx="10" fill="#FFF7E8" stroke="#E8C9A0" stroke-width="2"/>
  <!-- inner warm panel -->
  <rect x="168" y="198" width="864" height="412" rx="8" fill="#FFEDCC"/>

  <!-- side shelves inside -->
  <g opacity="0.95">
    <rect x="188" y="278" width="150" height="10" rx="5" fill="#B67D45"/>
    <rect x="862" y="278" width="150" height="10" rx="5" fill="#B67D45"/>
    <!-- bottles left -->
    <rect x="202" y="238" width="18" height="40" rx="6" fill="#2A9D8F"/><rect x="206" y="228" width="10" height="12" rx="3" fill="#1F766C"/>
    <rect x="228" y="242" width="16" height="36" rx="6" fill="#E9C46A"/><rect x="232" y="232" width="8" height="12" rx="3" fill="#C79A2E"/>
    <rect x="252" y="236" width="18" height="42" rx="6" fill="#E76F51"/><rect x="256" y="226" width="10" height="12" rx="3" fill="#B84A2E"/>
    <!-- stacked bowls right -->
    <g>
      <ellipse cx="902" cy="272" rx="28" ry="8" fill="#FFFFFF" stroke="#D9D9D9" stroke-width="1.2"/>
      <path d="M874 272 Q902 290 930 272 Z" fill="#FFFFFF" stroke="#D9D9D9" stroke-width="1.2"/>
      <ellipse cx="902" cy="258" rx="26" ry="7" fill="#FF6B6B"/><path d="M876 258 Q902 274 928 258 Z" fill="#FF6B6B"/>
      <ellipse cx="955" cy="270" rx="24" ry="7" fill="#4ECDC4"/><path d="M931 270 Q955 286 979 270 Z" fill="#4ECDC4"/>
    </g>
    <!-- tiny bowls left shelf -->
    <ellipse cx="306" cy="272" rx="22" ry="6" fill="#FFFFFF" stroke="#DDD" stroke-width="1"/><path d="M284 272 Q306 286 328 272 Z" fill="#5AA9E6"/>
  </g>

  <!-- vertical posts -->
  <rect x="132" y="148" width="30" height="610" rx="8" fill="url(#woodDark)"/>
  <rect x="1038" y="148" width="30" height="610" rx="8" fill="url(#woodDark)"/>
  <rect x="132" y="148" width="30" height="18" rx="8" fill="#5C3A1E" opacity="0.35"/>
  <rect x="1038" y="148" width="30" height="18" rx="8" fill="#5C3A1E" opacity="0.35"/>

  <!-- ROOF -->
  <g filter="url(#softShadow)">
    <path d="M 72 168 L 188 78 L 1012 78 L 1128 168 Q 1128 184 1112 184 L 88 184 Q 72 184 72 168 Z" fill="url(#roofGrad)"/>
    <!-- roof tiles lines -->
    <g stroke="#A91E16" stroke-width="2" opacity="0.45" fill="none">
      <path d="M 210 92 L 190 168"/><path d="M 360 86 L 345 170"/><path d="M 510 82 L 505 172"/>
      <path d="M 660 82 L 665 172"/><path d="M 810 86 L 825 170"/><path d="M 960 92 L 980 168"/>
    </g>
    <rect x="72" y="164" width="1056" height="14" rx="7" fill="#7A1A12"/>
    <!-- roof sign board -->
    <g filter="url(#cardShadow)">
      <rect x="398" y="28" width="404" height="62" rx="14" fill="#FFF8E6" stroke="#E63946" stroke-width="3.5"/>
      <circle cx="432" cy="59" r="18" fill="#FF6B9D"/><circle cx="426" cy="54" r="3.2" fill="white"/><circle cx="436" cy="54" r="3.2" fill="white"/>
      <path d="M422 66 Q432 71 442 66" stroke="white" stroke-width="2" fill="none" stroke-linecap="round"/>
      <circle cx="768" cy="59" r="18" fill="#FF6B9D"/><circle cx="762" cy="54" r="3.2" fill="white"/><circle cx="772" cy="54" r="3.2" fill="white"/>
      <path d="M758 66 Q768 71 778 66" stroke="white" stroke-width="2" fill="none" stroke-linecap="round"/>
    </g>
    <text x="600" y="70" text-anchor="middle" font-family="Arial Black, Arial, sans-serif" font-weight="900" font-size="30" letter-spacing="3" fill="#C1271D">TAKO RAMEN</text>
    <text x="600" y="86" text-anchor="middle" font-family="Hiragino Sans, Noto Sans JP, sans-serif" font-size="11" letter-spacing="4" fill="#8B5E3C">たこ やき ラーメン</text>
  </g>

  <!-- NOREN curtains -->
  <g filter="url(#softShadow)">
    <rect x="162" y="178" width="876" height="10" rx="5" fill="#5C3A1E"/>
    <!-- panels -->
    <g>
      <path d="M162 188 H318 V282 Q318 294 306 294 H174 Q162 294 162 282 Z" fill="#E63946"/>
      <path d="M328 188 H472 V282 Q472 294 460 294 H340 Q328 294 328 282 Z" fill="#D62828"/>
      <path d="M482 188 H618 V282 Q618 294 606 294 H494 Q482 294 482 282 Z" fill="#E63946"/>
      <path d="M628 188 H764 V282 Q764 294 752 294 H640 Q628 294 628 282 Z" fill="#D62828"/>
      <path d="M774 188 H908 V282 Q908 294 896 294 H786 Q774 294 774 282 Z" fill="#E63946"/>
      <path d="M918 188 H1038 V282 Q1038 294 1026 294 H930 Q918 294 918 282 Z" fill="#D62828"/>
    </g>
    <!-- noren text / icons -->
    <g fill="white" font-family="Hiragino Sans, Noto Sans JP, sans-serif" font-weight="700" text-anchor="middle">
      <text x="240" y="248" font-size="34">ラ</text>
      <text x="400" y="248" font-size="34">ー</text>
      <text x="550" y="248" font-size="34">メ</text>
      <text x="696" y="248" font-size="34">ン</text>
      <!-- mini octopus icon on last panels -->
      <g transform="translate(841,232)">
        <ellipse rx="20" ry="17" fill="white"/><circle cx="-7" cy="-3" r="2.6" fill="#E63946"/><circle cx="7" cy="-3" r="2.6" fill="#E63946"/>
        <path d="M-6 6 Q0 9 6 6" stroke="#E63946" stroke-width="1.8" fill="none" stroke-linecap="round"/>
        <path d="M-16 12 Q-18 20 -12 22 M-6 14 Q-6 22 0 22 M6 14 Q8 22 14 20" stroke="white" stroke-width="4" fill="none" stroke-linecap="round"/>
      </g>
      <text x="978" y="250" font-size="22">たこ</text>
    </g>
    <g stroke="white" stroke-width="1.2" opacity="0.35"><line x1="318" y1="192" x2="318" y2="290"/><line x1="472" y1="192" x2="472" y2="290"/><line x1="618" y1="192" x2="618" y2="290"/><line x1="764" y1="192" x2="764" y2="290"/><line x1="908" y1="192" x2="908" y2="290"/></g>
  </g>

  <!-- LANTERNS -->
  <g filter="url(#softShadow)">
    <!-- left lantern -->
    <line x1="228" y1="188" x2="228" y2="218" stroke="#5C3A1E" stroke-width="2.5"/>
    <ellipse cx="228" cy="252" rx="34" ry="38" fill="#FFFBEB" stroke="#E63946" stroke-width="2.5"/>
    <ellipse cx="228" cy="252" rx="34" ry="38" fill="none" stroke="#F4A261" stroke-width="1" opacity="0.6"/>
    <path d="M194 238 Q228 248 262 238 M194 266 Q228 256 262 266" stroke="#E9C46A" stroke-width="1.2" fill="none" opacity="0.7"/>
    <rect x="212" y="212" width="32" height="8" rx="3" fill="#222"/><rect x="212" y="284" width="32" height="8" rx="3" fill="#222"/>
    <text x="228" y="262" text-anchor="middle" font-family="Hiragino Sans, sans-serif" font-weight="800" font-size="22" fill="#E63946">麺</text>
    <!-- right lantern -->
    <line x1="972" y1="188" x2="972" y2="218" stroke="#5C3A1E" stroke-width="2.5"/>
    <ellipse cx="972" cy="252" rx="34" ry="38" fill="#FFFBEB" stroke="#E63946" stroke-width="2.5"/>
    <path d="M938 238 Q972 248 1006 238 M938 266 Q972 256 1006 266" stroke="#E9C46A" stroke-width="1.2" fill="none" opacity="0.7"/>
    <rect x="956" y="212" width="32" height="8" rx="3" fill="#222"/><rect x="956" y="284" width="32" height="8" rx="3" fill="#222"/>
    <text x="972" y="262" text-anchor="middle" font-family="Hiragino Sans, sans-serif" font-weight="800" font-size="20" fill="#E63946">たこ</text>
    <!-- glow -->
    <ellipse cx="228" cy="252" rx="52" ry="54" fill="#FFD166" opacity="0.18"/>
    <ellipse cx="972" cy="252" rx="52" ry="54" fill="#FFD166" opacity="0.18"/>
  </g>

  <!-- ===== OCTOPUS CHEF ===== -->
  <g id="octopus">
    <!-- back tentacles (behind body) -->
    <g fill="none" stroke-linecap="round">
      <path d="M 492 472 C 420 470, 352 448, 312 386" stroke="#E84A73" stroke-width="40"/>
      <path d="M 492 472 C 420 470, 352 448, 312 386" stroke="url(#octoGrad)" stroke-width="34"/>
      <path d="M 708 472 C 778 468, 848 442, 894 378" stroke="#E84A73" stroke-width="40"/>
      <path d="M 708 472 C 778 468, 848 442, 894 378" stroke="url(#octoGrad)" stroke-width="34"/>
    </g>

    <!-- body / mantle behind counter shadow -->
    <ellipse cx="600" cy="548" rx="168" ry="62" fill="#C73A5B" opacity="0.22"/>

    <!-- main head -->
    <g filter="url(#softShadow)">
      <ellipse cx="600" cy="398" rx="162" ry="148" fill="url(#octoGrad)" stroke="#D94F70" stroke-width="3"/>
      <!-- head highlight -->
      <ellipse cx="548" cy="328" rx="52" ry="34" fill="white" opacity="0.28" transform="rotate(-18 548 328)"/>
      <ellipse cx="532" cy="318" rx="18" ry="10" fill="white" opacity="0.45" transform="rotate(-18 532 318)"/>
      <!-- spots -->
      <circle cx="492" cy="368" r="9" fill="#FF9EBB" opacity="0.75"/><circle cx="512" cy="348" r="6" fill="#FF9EBB" opacity="0.6"/>
      <circle cx="702" cy="362" r="8" fill="#FF9EBB" opacity="0.7"/><circle cx="688" cy="342" r="5" fill="#FF9EBB" opacity="0.55"/>
    </g>

    <!-- chef hat -->
    <g filter="url(#softShadow)">
      <!-- puff -->
      <ellipse cx="548" cy="218" rx="56" ry="42" fill="url(#hatGrad)" stroke="#E8CBD3" stroke-width="1.8"/>
      <ellipse cx="600" cy="202" rx="62" ry="48" fill="url(#hatGrad)" stroke="#E8CBD3" stroke-width="1.8"/>
      <ellipse cx="652" cy="218" rx="56" ry="42" fill="url(#hatGrad)" stroke="#E8CBD3" stroke-width="1.8"/>
      <ellipse cx="600" cy="228" rx="78" ry="28" fill="white"/>
      <!-- band -->
      <rect x="506" y="232" width="188" height="42" rx="14" fill="white" stroke="#E8CBD3" stroke-width="1.8"/>
      <rect x="506" y="232" width="188" height="10" rx="5" fill="#FFF0F3"/>
      <circle cx="600" cy="253" r="7" fill="#FF6B9D"/><circle cx="578" cy="253" r="3.5" fill="#FFB3C6"/><circle cx="622" cy="253" r="3.5" fill="#FFB3C6"/>
      <!-- tiny octopus pin on hat -->
      <g transform="translate(658,250) scale(0.55)"><ellipse rx="14" ry="12" fill="#FF6B9D"/><circle cx="-5" cy="-2" r="1.8" fill="white"/><circle cx="5" cy="-2" r="1.8" fill="white"/><path d="M-10 8 Q-12 14 -7 15 M0 10 Q0 16 5 15 M10 8 Q12 14 7 15" stroke="#FF6B9D" stroke-width="3.5" fill="none" stroke-linecap="round"/></g>
    </g>

    <!-- neckerchief -->
    <path d="M 516 498 L 600 540 L 684 498 L 672 472 L 600 492 L 528 472 Z" fill="#E63946" stroke="#B91F2E" stroke-width="1.5"/>
    <circle cx="600" cy="510" r="10" fill="#C1271D" stroke="#8F1A12" stroke-width="1.2"/><circle cx="600" cy="510" r="4" fill="#FFD166"/>

    <!-- FACE -->
    <g>
      <!-- eyes -->
      <ellipse cx="540" cy="398" rx="17" ry="22" fill="#1A1A2E"/>
      <ellipse cx="660" cy="398" rx="17" ry="22" fill="#1A1A2E"/>
      <circle cx="546" cy="390" r="6.5" fill="white"/><circle cx="666" cy="390" r="6.5" fill="white"/>
      <circle cx="536" cy="408" r="3" fill="white" opacity="0.9"/><circle cx="656" cy="408" r="3" fill="white" opacity="0.9"/>
      <!-- happy closed arc brows -->
      <path d="M 518 366 Q 540 354 562 366" fill="none" stroke="#8E2A44" stroke-width="3.5" stroke-linecap="round"/>
      <path d="M 638 366 Q 660 354 682 366" fill="none" stroke="#8E2A44" stroke-width="3.5" stroke-linecap="round"/>
      <!-- blush -->
      <ellipse cx="492" cy="434" rx="24" ry="13" fill="#FF8FA3" opacity="0.85"/>
      <ellipse cx="708" cy="434" rx="24" ry="13" fill="#FF8FA3" opacity="0.85"/>
      <g stroke="#E85D7A" stroke-width="1.6" stroke-linecap="round" opacity="0.7"><path d="M482 430 L490 438 M492 428 L500 436"/><path d="M698 428 L706 436 M708 430 L716 438"/></g>
      <!-- mouth open smile -->
      <path d="M 568 438 Q 600 468 632 438 Q 628 462 600 466 Q 572 462 568 438 Z" fill="#7A1F2E" stroke="#5C1420" stroke-width="1.2"/>
      <ellipse cx="600" cy="456" rx="14" ry="6" fill="#FF8FA3"/>
      <!-- nose tiny -->
      <ellipse cx="600" cy="422" rx="5" ry="3.5" fill="#E84A73" opacity="0.6"/>
    </g>

    <!-- FRONT TENTACLES -->
    <!-- left upper holding ladle -->
    <g>
      <path d="M 478 478 C 410 486, 332 462, 288 398 C 272 374, 262 348, 268 322" fill="none" stroke="#D94F70" stroke-width="42" stroke-linecap="round"/>
      <path d="M 478 478 C 410 486, 332 462, 288 398 C 272 374, 262 348, 268 322" fill="none" stroke="url(#octoGrad)" stroke-width="36" stroke-linecap="round"/>
      <!-- suckers -->
      <g fill="#FFC2D1" stroke="#E87A95" stroke-width="0.8">
        <circle cx="398" cy="474" r="7"/><circle cx="348" cy="452" r="6.5"/><circle cx="308" cy="416" r="6"/><circle cx="282" cy="374" r="5.5"/>
      </g>
      <!-- ladle -->
      <g transform="rotate(-18 268 300)">
        <rect x="262" y="252" width="9" height="62" rx="4.5" fill="#8B5E3C"/>
        <ellipse cx="266" cy="246" rx="22" ry="14" fill="#C0C8D1" stroke="#8A95A5" stroke-width="1.5"/>
        <ellipse cx="266" cy="244" rx="16" ry="8" fill="#FFD29A"/>
        <path d="M 252 242 Q 266 236 280 242" stroke="#FF9E2E" stroke-width="2" fill="none"/>
      </g>
      <!-- steam from ladle -->
      <path d="M 252 228 Q 246 212 254 198 Q 262 184 256 168" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" opacity="0.75"/>
    </g>

    <!-- left lower stirring pot tentacle -->
    <g>
      <path d="M 472 512 C 408 528, 352 538, 318 528" fill="none" stroke="#D94F70" stroke-width="40" stroke-linecap="round"/>
      <path d="M 472 512 C 408 528, 352 538, 318 528" fill="none" stroke="url(#octoGrad)" stroke-width="34" stroke-linecap="round"/>
      <g fill="#FFC2D1"><circle cx="402" cy="524" r="6.5"/><circle cx="362" cy="532" r="6"/></g>
      <!-- wooden spoon in pot -->
      <line x1="318" y1="528" x2="352" y2="486" stroke="#8B5E3C" stroke-width="8" stroke-linecap="round"/>
      <ellipse cx="356" cy="482" rx="10" ry="7" fill="#D9A06B" transform="rotate(-38 356 482)"/>
    </g>

    <!-- right upper chopsticks + noodles -->
    <g>
      <path d="M 722 478 C 788 480, 862 452, 908 398 C 928 374, 938 350, 934 322" fill="none" stroke="#D94F70" stroke-width="42" stroke-linecap="round"/>
      <path d="M 722 478 C 788 480, 862 452, 908 398 C 928 374, 938 350, 934 322" fill="none" stroke="url(#octoGrad)" stroke-width="36" stroke-linecap="round"/>
      <g fill="#FFC2D1"><circle cx="798" cy="472" r="7"/><circle cx="852" cy="448" r="6.5"/><circle cx="892" cy="412" r="6"/><circle cx="918" cy="368" r="5.5"/></g>
      <!-- chopsticks -->
      <g stroke="#5C3A1E" stroke-width="5" stroke-linecap="round">
        <line x1="918" y1="332" x2="874" y2="438"/>
        <line x1="938" y1="328" x2="898" y2="438"/>
      </g>
      <!-- lifted noodles wavy -->
      <g fill="none" stroke="#FFE66D" stroke-width="5" stroke-linecap="round">
        <path d="M 882 438 Q 876 468 886 492 Q 894 518 886 548"/>
        <path d="M 894 438 Q 890 472 900 496 Q 908 520 900 548"/>
        <path d="M 906 438 Q 904 466 912 490 Q 918 514 912 542"/>
      </g>
      <g fill="none" stroke="#FFD93D" stroke-width="2.5" stroke-linecap="round" opacity="0.9">
        <path d="M 888 442 Q 884 470 892 494"/><path d="M 900 442 Q 898 470 906 494"/>
      </g>
      <!-- noodle steam curl -->
      <path d="M 886 420 Q 878 402 890 388" fill="none" stroke="white" stroke-width="2.8" stroke-linecap="round" opacity="0.8"/>
    </g>

    <!-- right lower offering tentacle holding small bowl -->
    <g>
      <path d="M 728 512 C 788 528, 842 534, 878 520" fill="none" stroke="#D94F70" stroke-width="40" stroke-linecap="round"/>
      <path d="M 728 512 C 788 528, 842 534, 878 520" fill="none" stroke="url(#octoGrad)" stroke-width="34" stroke-linecap="round"/>
      <g fill="#FFC2D1"><circle cx="792" cy="524" r="6.5"/><circle cx="832" cy="530" r="6"/></g>
    </g>

    <!-- bottom curl tentacles on counter -->
    <g fill="none" stroke-linecap="round">
      <path d="M 512 542 C 478 566, 438 572, 410 558 C 392 549, 388 532, 400 522" stroke="#D94F70" stroke-width="38"/>
      <path d="M 512 542 C 478 566, 438 572, 410 558 C 392 549, 388 532, 400 522" stroke="url(#octoGrad)" stroke-width="32"/>
      <path d="M 688 542 C 722 566, 762 572, 790 558 C 808 549, 812 532, 800 522" stroke="#D94F70" stroke-width="38"/>
      <path d="M 688 542 C 722 566, 762 572, 790 558 C 808 549, 812 532, 800 522" stroke="url(#octoGrad)" stroke-width="32"/>
    </g>
    <g fill="#FFC2D1"><circle cx="452" cy="562" r="6"/><circle cx="418" cy="552" r="5.5"/><circle cx="748" cy="562" r="6"/><circle cx="782" cy="552" r="5.5"/></g>

    <!-- center bottom tentacles holding serving bowl -->
    <g fill="none" stroke-linecap="round">
      <path d="M 548 548 C 534 576, 522 592, 504 600" stroke="#D94F70" stroke-width="36"/>
      <path d="M 548 548 C 534 576, 522 592, 504 600" stroke="url(#octoDark)" stroke-width="30"/>
      <path d="M 652 548 C 666 576, 678 592, 696 600" stroke="#D94F70" stroke-width="36"/>
      <path d="M 652 548 C 666 576, 678 592, 696 600" stroke="url(#octoDark)" stroke-width="30"/>
    </g>
  </g>

  <!-- ===== COUNTER ===== -->
  <g filter="url(#softShadow)">
    <rect x="118" y="598" width="964" height="22" rx="8" fill="#E8B88A"/>
    <rect x="108" y="616" width="984" height="52" rx="10" fill="url(#woodGrad)" stroke="#8B5E3C" stroke-width="1.5"/>
    <g stroke="#8B5E3C" stroke-width="1.2" opacity="0.45"><line x1="180" y1="616" x2="180" y2="668"/><line x1="340" y1="616" x2="340" y2="668"/><line x1="520" y1="616" x2="520" y2="668"/><line x1="700" y1="616" x2="700" y2="668"/><line x1="860" y1="616" x2="860" y2="668"/><line x1="1000" y1="616" x2="1000" y2="668"/></g>
    <!-- lower front panel -->
    <rect x="128" y="668" width="944" height="118" rx="12" fill="url(#woodDark)"/>
    <g opacity="0.28" stroke="#5C3A1E" stroke-width="2"><line x1="268" y1="676" x2="268" y2="778"/><line x1="428" y1="676" x2="428" y2="778"/><line x1="588" y1="676" x2="588" y2="778"/><line x1="748" y1="676" x2="748" y2="778"/><line x1="908" y1="676" x2="908" y2="778"/></g>
    <!-- front sign -->
    <g filter="url(#cardShadow)">
      <rect x="398" y="684" width="404" height="86" rx="14" fill="#FFF8E6" stroke="#E63946" stroke-width="2.8"/>
      <text x="600" y="716" text-anchor="middle" font-family="Hiragino Sans, Noto Sans JP, sans-serif" font-weight="800" font-size="26" fill="#C1271D">たこラーメン</text>
      <text x="600" y="742" text-anchor="middle" font-family="Arial, sans-serif" font-weight="700" font-size="13" letter-spacing="3.5" fill="#5C3A1E">OCTOPUS • RAMEN • YA-TAI</text>
      <g fill="#FF6B9D"><circle cx="432" cy="720" r="5"/><circle cx="768" cy="720" r="5"/><circle cx="432" cy="742" r="3.5"/><circle cx="768" cy="742" r="3.5"/></g>
    </g>
  </g>

  <!-- ===== FOOD ON COUNTER ===== -->
  <!-- left pot -->
  <g filter="url(#cardShadow)">
    <ellipse cx="318" cy="602" rx="72" ry="14" fill="#5C3A1E" opacity="0.22"/>
    <path d="M 252 548 L 260 600 Q 262 614 278 614 H 358 Q 374 614 376 600 L 384 548 Z" fill="#2B2D42" stroke="#1A1B2E" stroke-width="1.5"/>
    <ellipse cx="318" cy="548" rx="66" ry="14" fill="#3A3E5C"/>
    <ellipse cx="318" cy="546" rx="56" ry="10" fill="url(#brothGrad)"/>
    <g fill="#FF9E2E" opacity="0.8"><circle cx="298" cy="544" r="4"/><circle cx="322" cy="548" r="3"/><circle cx="340" cy="543" r="3.5"/></g>
    <g fill="#7BC950"><circle cx="308" cy="546" r="2.5"/><circle cx="332" cy="545" r="2.2"/><circle cx="318" cy="550" r="2"/></g>
    <rect x="246" y="560" width="14" height="8" rx="4" fill="#1A1B2E"/><rect x="376" y="560" width="14" height="8" rx="4" fill="#1A1B2E"/>
    <!-- pot steam -->
    <g fill="none" stroke="white" stroke-linecap="round" opacity="0.85">
      <path d="M 292 522 Q 284 502 294 486 Q 302 472 296 456" stroke-width="4"/>
      <path d="M 318 518 Q 312 496 322 480 Q 330 464 324 448" stroke-width="4.5"/>
      <path d="M 344 522 Q 338 504 346 488" stroke-width="3.5"/>
    </g>
  </g>

  <!-- center serving bowl (hero) -->
  <g filter="url(#cardShadow)">
    <ellipse cx="600" cy="618" rx="108" ry="16" fill="#5C3A1E" opacity="0.20"/>
    <!-- bowl body -->
    <path d="M 492 572 Q 500 622 548 632 L 652 632 Q 700 622 708 572 Z" fill="#E63946" stroke="#B91F2E" stroke-width="1.8"/>
    <path d="M 492 572 Q 500 622 548 632 L 652 632 Q 700 622 708 572" fill="none" stroke="white" stroke-width="2" opacity="0.25"/>
    <!-- white stripe -->
    <path d="M 498 592 Q 600 606 702 592 L 700 604 Q 600 618 500 604 Z" fill="white" opacity="0.92"/>
    <text x="600" y="606" text-anchor="middle" font-family="Hiragino Sans, sans-serif" font-weight="800" font-size="11" fill="#E63946">たこ</text>
    <!-- broth top -->
    <ellipse cx="600" cy="572" rx="108" ry="20" fill="#FFF3D6" stroke="#B91F2E" stroke-width="1.5"/>
    <ellipse cx="600" cy="572" rx="96" ry="16" fill="url(#brothGrad)"/>
    <!-- noodles mound -->
    <g fill="none" stroke="#FFE66D" stroke-width="4.5" stroke-linecap="round">
      <path d="M 536 568 Q 560 554 588 566 Q 612 576 640 564 Q 658 556 668 568"/>
      <path d="M 544 574 Q 568 562 594 572 Q 618 580 644 570"/>
    </g>
    <!-- toppings: egg -->
    <g><ellipse cx="556" cy="566" rx="20" ry="11" fill="white" stroke="#E8DCC6" stroke-width="1"/><ellipse cx="556" cy="566" rx="10" ry="6.5" fill="#FFB703" stroke="#E09A00" stroke-width="0.8"/></g>
    <!-- narutomaki -->
    <g><circle cx="640" cy="564" r="13" fill="white" stroke="#FFB3C6" stroke-width="1.2"/><path d="M 632 564 Q 640 556 648 564 Q 640 572 632 564 M 636 564 Q 640 560 644 564" fill="none" stroke="#FF6B9D" stroke-width="2" stroke-linecap="round"/></g>
    <!-- chashu -->
    <ellipse cx="600" cy="576" rx="16" ry="8" fill="#C97A4A" stroke="#9C5A2E" stroke-width="1" transform="rotate(-8 600 576)"/><ellipse cx="600" cy="576" rx="9" ry="4" fill="#E8A87C" transform="rotate(-8 600 576)"/>
    <!-- green onions -->
    <g fill="#5CB85C" stroke="#3A8A3A" stroke-width="0.6"><circle cx="576" cy="560" r="3.2"/><circle cx="590" cy="564" r="2.8"/><circle cx="618" cy="558" r="3"/><circle cx="628" cy="574" r="2.6"/><circle cx="562" cy="574" r="2.8"/></g>
    <!-- nori -->
    <rect x="660" y="544" width="18" height="26" rx="3" fill="#1A3A2A" transform="rotate(12 669 557)"/>
    <!-- steam hero -->
    <g fill="none" stroke="white" stroke-linecap="round" opacity="0.65">
      <path d="M 548 538 Q 540 516 552 498 Q 560 484 554 470" stroke-width="4.5"/>
      <path d="M 600 536 Q 594 512 604 494 Q 612 478 606 464" stroke-width="5"/>
      <path d="M 652 538 Q 644 516 656 498 Q 664 484 658 470" stroke-width="4.5"/>
    </g>
  </g>

  <!-- right small bowl being offered -->
  <g filter="url(#cardShadow)">
    <ellipse cx="892" cy="560" rx="54" ry="10" fill="#5C3A1E" opacity="0.18"/>
    <path d="M 842 522 Q 848 554 870 560 L 914 560 Q 936 554 942 522 Z" fill="#2EC4B6" stroke="#1A9A8E" stroke-width="1.5"/>
    <ellipse cx="892" cy="522" rx="50" ry="11" fill="#E0FFF8" stroke="#1A9A8E" stroke-width="1.2"/>
    <ellipse cx="892" cy="522" rx="42" ry="8" fill="url(#brothGrad)"/>
    <g fill="none" stroke="#FFE66D" stroke-width="3" stroke-linecap="round"><path d="M 868 520 Q 882 512 896 520 Q 908 526 918 520"/></g>
    <circle cx="880" cy="518" r="6" fill="white" stroke="#FFB3C6" stroke-width="0.8"/><path d="M876 518 Q880 514 884 518" stroke="#FF6B9D" stroke-width="1.2" fill="none"/>
    <g fill="#5CB85C"><circle cx="902" cy="516" r="2"/><circle cx="910" cy="520" r="1.8"/></g>
    <path d="M 872 500 Q 866 484 874 472" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" opacity="0.8"/>
    <path d="M 896 498 Q 890 480 900 466" fill="none" stroke="white" stroke-width="3.2" stroke-linecap="round" opacity="0.8"/>
  </g>

  <!-- left small bowl on counter -->
  <g filter="url(#cardShadow)">
    <ellipse cx="228" cy="618" rx="52" ry="9" fill="#5C3A1E" opacity="0.16"/>
    <path d="M 180 584 Q 186 610 206 616 L 250 616 Q 270 610 276 584 Z" fill="#4361EE" stroke="#2A3FBF" stroke-width="1.4"/>
    <ellipse cx="228" cy="584" rx="48" ry="10" fill="#EAF0FF" stroke="#2A3FBF" stroke-width="1"/>
    <ellipse cx="228" cy="584" rx="40" ry="7.5" fill="url(#brothGrad)"/>
    <g fill="none" stroke="#FFE66D" stroke-width="2.8" stroke-linecap="round"><path d="M206 582 Q220 574 234 582 Q244 586 252 582"/></g>
    <ellipse cx="218" cy="580" rx="9" ry="5" fill="white"/><ellipse cx="218" cy="580" rx="4.5" ry="2.8" fill="#FFB703"/>
  </g>

  <!-- chopsticks resting + spoon on counter right -->
  <g opacity="0.95">
    <line x1="968" y1="606" x2="1022" y2="590" stroke="#5C3A1E" stroke-width="4" stroke-linecap="round"/>
    <line x1="970" y1="614" x2="1024" y2="600" stroke="#5C3A1E" stroke-width="4" stroke-linecap="round"/>
    <ellipse cx="982" cy="622" rx="16" ry="7" fill="#C0C8D1" stroke="#8A95A5" stroke-width="1" transform="rotate(-12 982 622)"/>
  </g>

  <!-- menu board hanging right -->
  <g filter="url(#cardShadow)" transform="rotate(2 1002 378)">
    <rect x="938" y="318" width="128" height="122" rx="10" fill="#FFF8E6" stroke="#8B5E3C" stroke-width="2.5"/>
    <rect x="938" y="318" width="128" height="28" rx="10" fill="#E63946"/>
    <text x="1002" y="338" text-anchor="middle" font-family="Arial, sans-serif" font-weight="800" font-size="12" letter-spacing="1.5" fill="white">MENU</text>
    <g font-family="Hiragino Sans, Arial, sans-serif" font-size="11" fill="#3A2310">
      <text x="952" y="366">• 醤油  ¥800</text>
      <text x="952" y="386">• 味噌  ¥900</text>
      <text x="952" y="406">• たこ  ¥950</text>
      <text x="952" y="426">• 餃子  ¥400</text>
    </g>
    <circle cx="1002" cy="326" r="3" fill="#FFD166" stroke="#8B5E3C" stroke-width="0.8"/>
  </g>

  <!-- price / open sign left -->
  <g filter="url(#cardShadow)" transform="rotate(-3 188 392)">
    <rect x="118" y="352" width="140" height="76" rx="10" fill="#1A1A2E"/>
    <rect x="124" y="358" width="128" height="64" rx="7" fill="none" stroke="#FFD166" stroke-width="1.2" stroke-dasharray="4 3"/>
    <text x="188" y="382" text-anchor="middle" font-family="Arial Black, sans-serif" font-weight="900" font-size="16" fill="#FFD166" letter-spacing="1">OPEN</text>
    <text x="188" y="402" text-anchor="middle" font-family="Hiragino Sans, sans-serif" font-size="9.5" fill="white">営業中 • いらっしゃい</text>
    <circle cx="132" cy="366" r="3" fill="#7FE7C4"/><circle cx="244" cy="366" r="3" fill="#FF8FA3"/>
  </g>

  <!-- STOOLS foreground -->
  <g filter="url(#cardShadow)">
    <g>
      <ellipse cx="268" cy="802" rx="52" ry="10" fill="#5C3A1E" opacity="0.18"/>
      <rect x="216" y="752" width="104" height="16" rx="8" fill="#E63946" stroke="#B91F2E" stroke-width="1.2"/>
      <rect x="228" y="768" width="10" height="36" rx="4" fill="#5C3A1E"/><rect x="298" y="768" width="10" height="36" rx="4" fill="#5C3A1E"/>
      <rect x="218" y="788" width="100" height="6" rx="3" fill="#5C3A1E" opacity="0.7"/>
      <ellipse cx="268" cy="752" rx="52" ry="9" fill="#FF6B6B"/>
    </g>
    <g>
      <ellipse cx="932" cy="802" rx="52" ry="10" fill="#5C3A1E" opacity="0.18"/>
      <rect x="880" y="752" width="104" height="16" rx="8" fill="#2EC4B6" stroke="#1A9A8E" stroke-width="1.2"/>
      <rect x="892" y="768" width="10" height="36" rx="4" fill="#5C3A1E"/><rect x="962" y="768" width="10" height="36" rx="4" fill="#5C3A1E"/>
      <rect x="882" y="788" width="100" height="6" rx="3" fill="#5C3A1E" opacity="0.7"/>
      <ellipse cx="932" cy="752" rx="52" ry="9" fill="#7FE7C4"/>
    </g>
    <g>
      <ellipse cx="600" cy="818" rx="46" ry="8" fill="#5C3A1E" opacity="0.14"/>
      <rect x="554" y="776" width="92" height="14" rx="7" fill="#FFB703" stroke="#D99A00" stroke-width="1.1"/>
      <rect x="566" y="790" width="9" height="28" rx="3" fill="#5C3A1E"/><rect x="625" y="790" width="9" height="28" rx="3" fill="#5C3A1E"/>
      <ellipse cx="600" cy="776" rx="46" ry="8" fill="#FFD166"/>
    </g>
  </g>

  <!-- sparkles / finishing touches -->
  <g fill="#FFD166">
    <path d="M 178 478 L 182 490 L 194 494 L 182 498 L 178 510 L 174 498 L 162 494 L 174 490 Z"/>
    <path d="M 1028 482 L 1031 491 L 1040 494 L 1031 497 L 1028 506 L 1025 497 L 1016 494 L 1025 491 Z"/>
    <path d="M 478 178 L 480.5 184 L 486 186.5 L 480.5 189 L 478 195 L 475.5 189 L 470 186.5 L 475.5 184 Z" fill="#FF8FA3"/>
    <path d="M 728 168 L 730 173 L 735 175 L 730 177 L 728 182 L 726 177 L 721 175 L 726 173 Z"/>
  </g>
  <g fill="white" opacity="0.9"><circle cx="386" cy="512" r="3"/><circle cx="814" cy="500" r="2.8"/><circle cx="1042" cy="548" r="2.5"/><circle cx="158" cy="548" r="2.5"/></g>

  <!-- caption pill -->
  <g filter="url(#cardShadow)">
    <rect x="368" y="842" width="464" height="36" rx="18" fill="#1A1A2E"/>
    <text x="600" y="866" text-anchor="middle" font-family="Arial, sans-serif" font-weight="700" font-size="13" letter-spacing="1.2" fill="white">✦  CHEF TAKO  •  FRESH NOODLES, HAPPY TENTACLES  ✦</text>
  </g>
</svg>
'''

OUT.write_text(svg, encoding="utf-8")
print(f"Wrote {OUT} ({len(svg.encode('utf-8'))} bytes)")
