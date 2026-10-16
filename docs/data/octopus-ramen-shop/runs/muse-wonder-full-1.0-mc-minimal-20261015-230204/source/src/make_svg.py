#!/usr/bin/env python3
"""Generate an SVG illustration: octopus chef at a ramen booth (yatai)."""
import os

W, H = 1200, 900

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<title>Octopus Chef at a Ramen Booth</title>
<desc>A cheerful octopus chef in a toque serving ramen from a lantern-lit yatai stall at night.</desc>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#141a38"/><stop offset="0.55" stop-color="#2a2d55"/><stop offset="1" stop-color="#4a3560"/>
  </linearGradient>
  <linearGradient id="wood" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#9c6b3d"/><stop offset="1" stop-color="#7a4e28"/>
  </linearGradient>
  <linearGradient id="woodDark" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#6f4622"/><stop offset="1" stop-color="#523019"/>
  </linearGradient>
  <linearGradient id="octo" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ff8a6b"/><stop offset="0.6" stop-color="#f2644a"/><stop offset="1" stop-color="#d94833"/>
  </linearGradient>
  <radialGradient id="lamp" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#fff3c4"/><stop offset="0.55" stop-color="#ffd66e"/><stop offset="1" stop-color="#f39c2c"/>
  </radialGradient>
  <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#ffdf8a" stop-opacity="0.55"/><stop offset="1" stop-color="#ffdf8a" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="broth" cx="0.5" cy="0.45" r="0.6">
    <stop offset="0" stop-color="#f7c25c"/><stop offset="1" stop-color="#d9822b"/>
  </radialGradient>
</defs>

<!-- ======== SKY ======== -->
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<g fill="#fff" opacity="0.85">
  <circle cx="70" cy="70" r="3"/><circle cx="190" cy="42" r="2.2"/><circle cx="330" cy="88" r="2.6"/>
  <circle cx="1040" cy="55" r="3"/><circle cx="925" cy="100" r="2.2"/><circle cx="1125" cy="140" r="2.6"/>
  <circle cx="540" cy="46" r="2"/><circle cx="690" cy="78" r="2.8"/><circle cx="45" cy="170" r="2.2"/>
  <circle cx="1155" cy="60" r="2"/><circle cx="430" cy="34" r="2.2"/><circle cx="800" cy="40" r="2"/>
</g>
<!-- moon -->
<circle cx="1065" cy="105" r="46" fill="#fdf3d0"/>
<circle cx="1046" cy="90" r="9" fill="#eeddaf"/><circle cx="1082" cy="120" r="6" fill="#eeddaf"/>
<circle cx="1058" cy="128" r="4.5" fill="#eeddaf"/>
<!-- distant rooftops -->
<path d="M0 610 L150 610 L130 575 L30 575 Z" fill="#1d2247"/><rect x="18" y="610" width="112" height="70" fill="#1d2247"/>
<path d="M1050 610 L1200 610 L1170 570 L1080 570 Z" fill="#1d2247"/><rect x="1065" y="610" width="120" height="70" fill="#1d2247"/>
<rect x="55" y="625" width="16" height="20" fill="#ffd66e" opacity="0.8"/><rect x="1100" y="628" width="16" height="20" fill="#ffd66e" opacity="0.8"/>

<!-- ======== GROUND ======== -->
<rect x="0" y="672" width="{W}" height="228" fill="#2c2748"/>
<ellipse cx="600" cy="780" rx="520" ry="95" fill="#3a3462"/>
<g stroke="#241f40" stroke-width="4" opacity="0.7">
  <path d="M60 730 H340 M860 730 H1140 M120 800 H420 M800 810 H1080 M250 865 H520 M700 868 H980"/>
</g>
<ellipse cx="600" cy="700" rx="470" ry="60" fill="url(#glow)"/>

<!-- ======== BOOTH STRUCTURE ======== -->
<!-- side posts -->
<rect x="212" y="235" width="26" height="445" rx="6" fill="url(#woodDark)"/>
<rect x="962" y="235" width="26" height="445" rx="6" fill="url(#woodDark)"/>
<!-- back wall -->
<rect x="238" y="250" width="724" height="430" fill="#3d2a20"/>
<g opacity="0.35" stroke="#241811" stroke-width="5">
  <path d="M320 250 V680 M420 250 V680 M520 250 V680 M620 250 V680 M720 250 V680 M820 250 V680 M900 250 V680"/>
</g>
<!-- warm interior glow -->
<rect x="238" y="250" width="724" height="430" fill="#ff9a3c" opacity="0.10"/>

<!-- roof -->
<path d="M155 258 L600 128 L1045 258 L1005 292 L600 178 L195 292 Z" fill="#27355e"/>
<path d="M155 258 L600 128 L1045 258 L1028 272 L600 152 L172 272 Z" fill="#32467a"/>
<g stroke="#1b2647" stroke-width="4" opacity="0.8">
  <path d="M280 218 L600 128 L920 218 M220 238 L600 148 L980 238" fill="none"/>
</g>
<rect x="585" y="112" width="30" height="30" rx="6" fill="#32467a"/>

<!-- signboard -->
<g>
  <rect x="425" y="188" width="350" height="66" rx="12" fill="#8c2f25" stroke="#5e1e16" stroke-width="5"/>
  <rect x="438" y="199" width="324" height="44" rx="8" fill="none" stroke="#f4c56b" stroke-width="3"/>
  <circle cx="475" cy="221" r="15" fill="#f4c56b"/>
  <path d="M464 232 q3 8 7 0 q4 8 8 0 q4 8 7 0" fill="none" stroke="#f4c56b" stroke-width="4" stroke-linecap="round"/>
  <circle cx="470" cy="218" r="2.4" fill="#8c2f25"/><circle cx="480" cy="218" r="2.4" fill="#8c2f25"/>
  <text x="500" y="235" font-family="Georgia, 'Times New Roman', serif" font-size="27" font-weight="bold" fill="#ffe9b0" letter-spacing="1">TAKO RAMEN</text>
</g>

<!-- noren curtains -->
<g>
  <rect x="238" y="262" width="724" height="12" fill="#523019"/>
  <g fill="#b8402f">
    <path d="M248 274 h100 v88 q-25 14 -50 0 q-25 14 -50 0 Z"/>
    <path d="M358 274 h100 v88 q-25 14 -50 0 q-25 14 -50 0 Z"/>
    <path d="M742 274 h100 v88 q-25 14 -50 0 q-25 14 -50 0 Z"/>
    <path d="M852 274 h100 v88 q-25 14 -50 0 q-25 14 -50 0 Z"/>
  </g>
  <g fill="#ffe9b0" font-family="Georgia, serif" font-size="30" font-weight="bold" text-anchor="middle">
    <text x="298" y="330">麺</text><text x="408" y="330">旨</text><text x="792" y="330">熱</text><text x="902" y="330">蛸</text>
  </g>
</g>

<!-- string lights -->
<path d="M238 300 Q600 380 962 300" fill="none" stroke="#191426" stroke-width="3"/>
<g>
  <circle cx="320" cy="322" r="26" fill="url(#glow)"/><circle cx="320" cy="322" r="9" fill="url(#lamp)"/>
  <circle cx="430" cy="340" r="26" fill="url(#glow)"/><circle cx="430" cy="340" r="9" fill="url(#lamp)"/>
  <circle cx="770" cy="340" r="26" fill="url(#glow)"/><circle cx="770" cy="340" r="9" fill="url(#lamp)"/>
  <circle cx="880" cy="322" r="26" fill="url(#glow)"/><circle cx="880" cy="322" r="9" fill="url(#lamp)"/>
</g>

<!-- hanging lanterns -->
<g>
  <path d="M288 262 v18 M912 262 v18" stroke="#191426" stroke-width="4"/>
  <ellipse cx="288" cy="322" rx="86" ry="86" fill="url(#glow)"/>
  <ellipse cx="912" cy="322" rx="86" ry="86" fill="url(#glow)"/>
  <ellipse cx="288" cy="322" rx="34" ry="42" fill="#e64b3a"/>
  <ellipse cx="912" cy="322" rx="34" ry="42" fill="#e64b3a"/>
  <g fill="none" stroke="#b83324" stroke-width="3">
    <path d="M256 306 q32 12 64 0 M254 322 q34 12 68 0 M256 338 q32 12 64 0"/>
    <path d="M880 306 q32 12 64 0 M878 322 q34 12 68 0 M880 338 q32 12 64 0"/>
  </g>
  <rect x="276" y="278" width="24" height="10" rx="3" fill="#33241a"/><rect x="900" y="278" width="24" height="10" rx="3" fill="#33241a"/>
  <rect x="276" y="356" width="24" height="10" rx="3" fill="#33241a"/><rect x="900" y="356" width="24" height="10" rx="3" fill="#33241a"/>
  <text x="288" y="334" font-family="Georgia, serif" font-size="26" font-weight="bold" fill="#fff2c9" text-anchor="middle">麺</text>
  <text x="912" y="334" font-family="Georgia, serif" font-size="26" font-weight="bold" fill="#fff2c9" text-anchor="middle">蛸</text>
</g>

<!-- shelf with jars & bowls (inside, left) -->
<g>
  <rect x="262" y="430" width="150" height="10" rx="4" fill="url(#wood)"/>
  <rect x="275" y="398" width="26" height="32" rx="5" fill="#7fb3c8"/><rect x="279" y="408" width="18" height="14" fill="#fff" opacity="0.5"/>
  <rect x="310" y="392" width="26" height="38" rx="5" fill="#c86b4a"/><rect x="314" y="404" width="18" height="14" fill="#fff" opacity="0.45"/>
  <rect x="345" y="400" width="26" height="30" rx="5" fill="#8db56a"/><rect x="349" y="410" width="18" height="12" fill="#fff" opacity="0.5"/>
  <path d="M378 430 a16 11 0 0 0 32 0 Z" fill="#f3ead8"/>
  <!-- menu slip -->
  <rect x="270" y="452" width="58" height="92" rx="5" fill="#f7efd8" transform="rotate(-3 299 498)"/>
  <g stroke="#8a6f4d" stroke-width="3" stroke-linecap="round">
    <path d="M282 472 h34 M282 488 h34 M282 504 h24 M282 520 h30"/>
  </g>
  <circle cx="299" cy="462" r="4" fill="#b8402f"/>
</g>

<!-- shelf right: stacked bowls + bottles -->
<g>
  <rect x="788" y="430" width="150" height="10" rx="4" fill="url(#wood)"/>
  <path d="M800 430 a22 14 0 0 0 44 0 Z" fill="#2e5f8a"/><path d="M804 418 a18 11 0 0 0 36 0 Z" fill="#3e77ab"/>
  <path d="M852 430 a22 14 0 0 0 44 0 Z" fill="#f3ead8"/><path d="M856 418 a18 11 0 0 0 36 0 Z" fill="#fff7e6"/>
  <rect x="905" y="394" width="16" height="36" rx="5" fill="#5d7d4a"/><rect x="909" y="384" width="8" height="14" fill="#5d7d4a"/>
</g>

<!-- ======== BIG NOODLE POT (left of chef) ======== -->
<g>
  <path d="M330 560 q28 -34 6 -62 M380 562 q30 -36 8 -66 M428 560 q26 -32 6 -60" fill="none" stroke="#ffffff" stroke-width="7" stroke-linecap="round" opacity="0.55"/>
  <rect x="302" y="558" width="162" height="96" rx="16" fill="#9aa7b5"/>
  <rect x="302" y="558" width="162" height="20" rx="10" fill="#c3ceda"/>
  <ellipse cx="383" cy="562" rx="76" ry="13" fill="url(#broth)"/>
  <path d="M330 560 q14 -7 28 0 q14 -7 28 0 q14 -7 28 0 q12 -6 22 -1" fill="none" stroke="#ffe3a1" stroke-width="5" stroke-linecap="round"/>
  <rect x="314" y="592" width="12" height="48" rx="6" fill="#ffffff" opacity="0.35"/>
  <path d="M302 596 h-18 M464 596 h18" stroke="#7c8a99" stroke-width="10" stroke-linecap="round"/>
  <rect x="322" y="654" width="122" height="12" rx="5" fill="#333"/>
  <path d="M345 654 q8 -12 16 0 q9 -14 17 0 q9 -12 16 0 q9 -13 17 0" fill="#ff7a29" opacity="0.95"/>
</g>

<!-- ======== OCTOPUS CHEF ======== -->
<g stroke-linecap="round" stroke-linejoin="round">
  <!-- back tentacles (behind body, over counter) -->
  <path d="M520 570 C470 600 452 640 470 668 C482 686 508 682 510 664" fill="none" stroke="#d94833" stroke-width="30"/>
  <path d="M690 570 C745 600 762 638 746 666 C735 685 708 681 706 662" fill="none" stroke="#d94833" stroke-width="30"/>

  <!-- tentacle holding pepper shaker (upper left, over pot) -->
  <path d="M510 500 C450 480 420 470 402 452" fill="none" stroke="url(#octo)" stroke-width="26"/>
  <g transform="rotate(-24 394 444)">
    <rect x="384" y="420" width="20" height="34" rx="6" fill="#c9d4de"/>
    <rect x="382" y="414" width="24" height="10" rx="4" fill="#7c8a99"/>
  </g>
  <g fill="#3a3a3a"><circle cx="378" cy="478" r="2.6"/><circle cx="390" cy="490" r="2.6"/><circle cx="366" cy="492" r="2.6"/><circle cx="382" cy="504" r="2.6"/></g>

  <!-- tentacle holding ladle (upper right, raised) -->
  <path d="M702 495 C775 470 815 435 828 395" fill="none" stroke="url(#octo)" stroke-width="26"/>
  <path d="M828 398 L858 330" stroke="#8a5a2b" stroke-width="9"/>
  <path d="M840 332 a20 16 0 1 0 38 -4 a20 16 0 1 0 -38 4" fill="#c9d4de"/>
  <ellipse cx="859" cy="328" rx="15" ry="10" fill="url(#broth)"/>

  <!-- body / head -->
  <path d="M600 368 C520 368 488 428 490 498 C491 552 510 600 548 622 L652 622 C690 600 709 552 710 498 C712 428 680 368 600 368 Z" fill="url(#octo)"/>
  <ellipse cx="552" cy="425" rx="26" ry="42" fill="#ffffff" opacity="0.18"/>
  <!-- spots -->
  <g fill="#c93b27" opacity="0.55">
    <circle cx="520" cy="500" r="7"/><circle cx="682" cy="492" r="6"/><circle cx="655" cy="545" r="5"/><circle cx="530" cy="555" r="5"/>
  </g>

  <!-- apron -->
  <path d="M545 528 L655 528 L668 624 L532 624 Z" fill="#f7f2e2"/>
  <path d="M545 528 L655 528 L658 550 L542 550 Z" fill="#e5dcc4"/>
  <path d="M545 528 L570 492 M655 528 L630 492" stroke="#f7f2e2" stroke-width="12" fill="none"/>
  <rect x="578" y="572" width="44" height="34" rx="5" fill="none" stroke="#d8cdb2" stroke-width="3"/>
  <!-- neckerchief -->
  <path d="M570 504 L630 504 L600 536 Z" fill="#2e7fa8"/>
  <circle cx="600" cy="508" r="8" fill="#256a8f"/>

  <!-- face -->
  <circle cx="563" cy="452" r="17" fill="#fff"/><circle cx="637" cy="452" r="17" fill="#fff"/>
  <circle cx="566" cy="456" r="8.5" fill="#26221f"/><circle cx="640" cy="456" r="8.5" fill="#26221f"/>
  <circle cx="569" cy="452" r="3" fill="#fff"/><circle cx="643" cy="452" r="3" fill="#fff"/>
  <path d="M545 430 q18 -12 36 -3 M619 427 q18 -9 36 3" fill="none" stroke="#a93220" stroke-width="6"/>
  <path d="M578 486 q22 18 44 0" fill="none" stroke="#7c2415" stroke-width="6"/>
  <ellipse cx="535" cy="478" rx="14" ry="9" fill="#ffb09a" opacity="0.85"/>
  <ellipse cx="665" cy="478" rx="14" ry="9" fill="#ffb09a" opacity="0.85"/>

  <!-- chef hat (toque) -->
  <g>
    <path d="M522 386 C500 350 520 318 552 322 C560 298 640 298 648 322 C680 318 700 350 678 386 Z" fill="#ffffff"/>
    <path d="M522 386 C500 350 520 318 552 322 C560 298 640 298 648 322 C680 318 700 350 678 386" fill="none" stroke="#e3ddd2" stroke-width="4"/>
    <path d="M555 378 q-4 -28 6 -44 M600 380 v-52 M645 378 q4 -28 -6 -44" fill="none" stroke="#e8e2d5" stroke-width="5"/>
    <rect x="518" y="380" width="164" height="30" rx="9" fill="#ffffff" stroke="#e3ddd2" stroke-width="4"/>
  </g>

  <!-- tentacle holding chopsticks + noodles (front left) -->
  <path d="M525 575 C470 590 445 575 428 545" fill="none" stroke="url(#octo)" stroke-width="26"/>
  <path d="M430 548 L382 470 M444 556 L404 474" stroke="#8a5a2b" stroke-width="7"/>
  <path d="M382 470 q-4 42 6 62 M396 472 q-2 44 8 64 M410 476 q0 40 10 58" fill="none" stroke="#ffd98a" stroke-width="6"/>

  <!-- tentacle presenting a bowl (front right) -->
  <path d="M685 580 C745 600 790 592 818 566" fill="none" stroke="url(#octo)" stroke-width="26"/>
  <g>
    <path d="M770 566 a52 34 0 0 0 104 0 Z" fill="#2e5f8a"/>
    <path d="M770 566 a52 34 0 0 0 104 0" fill="none" stroke="#214a6e" stroke-width="4"/>
    <ellipse cx="822" cy="566" rx="52" ry="11" fill="url(#broth)"/>
    <path d="M790 564 q10 -6 20 0 q10 -6 20 0 q10 -6 18 -1" fill="none" stroke="#ffe3a1" stroke-width="4.5"/>
    <circle cx="806" cy="562" r="8" fill="#fff"/><circle cx="806" cy="562" r="4" fill="#ffb52e"/>
    <rect x="826" y="553" width="18" height="13" rx="3" fill="#f1917b"/>
    <path d="M800 552 q10 -18 2 -34 M828 554 q11 -19 3 -36" fill="none" stroke="#fff" stroke-width="5" opacity="0.6"/>
    <rect x="808" y="596" width="28" height="7" rx="3" fill="#214a6e"/>
  </g>

  <!-- two small front tentacles resting on counter, with suckers -->
  <path d="M560 615 C540 645 540 665 558 678" fill="none" stroke="url(#octo)" stroke-width="24"/>
  <path d="M645 615 C665 645 665 665 647 678" fill="none" stroke="url(#octo)" stroke-width="24"/>
  <g fill="#ffc4ad">
    <circle cx="548" cy="640" r="5"/><circle cx="552" cy="660" r="4.4"/>
    <circle cx="657" cy="640" r="5"/><circle cx="653" cy="660" r="4.4"/>
    <circle cx="478" cy="652" r="5"/><circle cx="738" cy="650" r="5"/>
  </g>
</g>

<!-- ======== COUNTER ======== -->
<g>
  <rect x="195" y="668" width="810" height="26" rx="8" fill="url(#wood)"/>
  <rect x="195" y="668" width="810" height="9" rx="4" fill="#c08b52"/>
  <rect x="222" y="694" width="756" height="78" fill="url(#woodDark)"/>
  <g stroke="#3f2512" stroke-width="4" opacity="0.7">
    <path d="M320 694 V772 M440 694 V772 M560 694 V772 M680 694 V772 M800 694 V772 M905 694 V772"/>
  </g>
  <rect x="222" y="720" width="756" height="8" fill="#3f2512" opacity="0.6"/>
</g>

<!-- bowls & items on counter -->
<g>
  <!-- left bowl -->
  <path d="M262 668 a40 26 0 0 1 80 0 Z" fill="#f3ead8" transform="translate(0,-2)"/>
  <path d="M262 640 a40 26 0 0 0 80 0 Z" fill="#b8402f"/>
  <ellipse cx="302" cy="640" rx="40" ry="9" fill="url(#broth)"/>
  <path d="M282 638 q8 -5 16 0 q8 -5 16 0 q8 -5 14 -1" fill="none" stroke="#ffe3a1" stroke-width="4"/>
  <circle cx="292" cy="637" r="6.5" fill="#fff"/><circle cx="292" cy="637" r="3.2" fill="#ffb52e"/>
  <path d="M318 640 l34 -30 M312 646 l36 -26" stroke="#8a5a2b" stroke-width="5" stroke-linecap="round"/>
  <path d="M288 630 q8 -14 2 -28 M314 630 q9 -15 3 -30" fill="none" stroke="#fff" stroke-width="4.5" opacity="0.55" stroke-linecap="round"/>
  <!-- soy bottle + cup -->
  <rect x="880" y="618" width="20" height="48" rx="6" fill="#5b4632"/><rect x="885" y="606" width="10" height="16" fill="#5b4632"/>
  <rect x="883" y="632" width="14" height="16" fill="#f3ead8"/>
  <path d="M915 666 a18 12 0 0 0 36 0 Z" fill="#7fb3c8"/><ellipse cx="933" cy="652" rx="18" ry="5" fill="#a8cfdf"/>
  <!-- narutomaki plate -->
  <ellipse cx="430" cy="662" rx="34" ry="8" fill="#eaf2f5"/>
  <circle cx="418" cy="654" r="10" fill="#fff"/><path d="M412 654 a6 6 0 1 1 6 6 a3.5 3.5 0 1 0 -3.5 -3.5" fill="none" stroke="#f28bb4" stroke-width="3"/>
  <circle cx="440" cy="652" r="10" fill="#fff"/><path d="M434 652 a6 6 0 1 1 6 6 a3.5 3.5 0 1 0 -3.5 -3.5" fill="none" stroke="#f28bb4" stroke-width="3"/>
</g>

<!-- ======== STOOLS ======== -->
<g>
  <g><rect x="272" y="782" width="96" height="18" rx="9" fill="#b8402f"/><rect x="290" y="800" width="12" height="62" fill="url(#woodDark)"/><rect x="338" y="800" width="12" height="62" fill="url(#woodDark)"/><rect x="290" y="830" width="60" height="9" fill="url(#woodDark)"/></g>
  <g><rect x="552" y="782" width="96" height="18" rx="9" fill="#b8402f"/><rect x="570" y="800" width="12" height="62" fill="url(#woodDark)"/><rect x="618" y="800" width="12" height="62" fill="url(#woodDark)"/><rect x="570" y="830" width="60" height="9" fill="url(#woodDark)"/></g>
  <g><rect x="832" y="782" width="96" height="18" rx="9" fill="#b8402f"/><rect x="850" y="800" width="12" height="62" fill="url(#woodDark)"/><rect x="898" y="800" width="12" height="62" fill="url(#woodDark)"/><rect x="850" y="830" width="60" height="9" fill="url(#woodDark)"/></g>
</g>

<!-- cat customer waiting on middle stool -->
<g>
  <path d="M648 782 q34 -6 30 -34" fill="none" stroke="#e8a34c" stroke-width="12" stroke-linecap="round"/>
  <ellipse cx="600" cy="752" rx="34" ry="30" fill="#f2b25c"/>
  <circle cx="600" cy="712" r="26" fill="#f2b25c"/>
  <path d="M580 694 l-6 -20 l20 10 Z M620 694 l6 -20 l-20 10 Z" fill="#f2b25c"/>
  <path d="M583 692 l-3 -11 l10 6 Z M617 692 l3 -11 l-10 6 Z" fill="#f7c9c0"/>
  <circle cx="591" cy="710" r="3.4" fill="#26221f"/><circle cx="609" cy="710" r="3.4" fill="#26221f"/>
  <path d="M596 720 q4 4 8 0" fill="none" stroke="#26221f" stroke-width="2.6" stroke-linecap="round"/>
  <path d="M570 716 h-14 M571 723 l-13 4 M630 716 h14 M629 723 l13 4" stroke="#d98f35" stroke-width="2.6" stroke-linecap="round"/>
  <path d="M578 742 q22 10 44 0" fill="none" stroke="#d98f35" stroke-width="5"/>
  <ellipse cx="582" cy="780" rx="11" ry="6" fill="#e8a34c"/><ellipse cx="618" cy="780" rx="11" ry="6" fill="#e8a34c"/>
  <rect x="586" y="728" width="28" height="9" rx="4" fill="#b8402f"/><circle cx="600" cy="740" r="5" fill="#f4c56b"/>
</g>

<!-- soft vignette -->
<rect width="{W}" height="{H}" fill="none" stroke="#0c0f24" stroke-width="26" opacity="0.35"/>
</svg>
"""

out = os.path.join(os.path.dirname(__file__), "..", "output", "octopus-ramen.svg")
out = os.path.normpath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"Wrote {out} ({os.path.getsize(out)} bytes)")
