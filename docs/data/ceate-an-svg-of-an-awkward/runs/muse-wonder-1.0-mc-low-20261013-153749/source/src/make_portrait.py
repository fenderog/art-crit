#!/usr/bin/env python3
from pathlib import Path

OUT = Path("output/awkward-robot-family-portrait.svg")
OUT.parent.mkdir(parents=True, exist_ok=True)

svg = r'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900">
<defs>
  <radialGradient id="wall" cx="50%" cy="38%" r="75%">
    <stop offset="0%" stop-color="#f6ead8"/><stop offset="45%" stop-color="#e7cdb4"/>
    <stop offset="78%" stop-color="#c9a58c"/><stop offset="100%" stop-color="#9b7a68"/>
  </radialGradient>
  <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#b08a6e"/><stop offset="100%" stop-color="#7d5a49"/>
  </linearGradient>
  <radialGradient id="spot" cx="50%" cy="42%" r="55%">
    <stop offset="0%" stop-color="#fff8e6" stop-opacity=".55"/><stop offset="70%" stop-color="#fff8e6" stop-opacity=".12"/><stop offset="100%" stop-color="#fff8e6" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="teal" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#7fd1cb"/><stop offset="100%" stop-color="#2f7f86"/></linearGradient>
  <linearGradient id="coral" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#ffb3a0"/><stop offset="100%" stop-color="#d45f68"/></linearGradient>
  <linearGradient id="purple" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#c4a6e8"/><stop offset="100%" stop-color="#6f5aa8"/></linearGradient>
  <linearGradient id="yellow" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#ffe38a"/><stop offset="100%" stop-color="#eaa834"/></linearGradient>
  <linearGradient id="mint" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#cdeac0"/><stop offset="100%" stop-color="#7da87a"/></linearGradient>
  <linearGradient id="metal" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#f2f4f6"/><stop offset="100%" stop-color="#aeb8bf"/></linearGradient>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="10"/></filter>
  <filter id="soft2" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3"/></filter>
</defs>

<!-- studio backdrop -->
<rect width="1200" height="900" fill="url(#wall)"/>
<path d="M0 610 Q600 565 1200 610 L1200 900 L0 900Z" fill="url(#floor)"/>
<path d="M0 610 Q600 565 1200 610" fill="none" stroke="#8a6752" stroke-width="4" opacity=".5"/>
<ellipse cx="600" cy="430" rx="560" ry="430" fill="url(#spot)"/>
<!-- draped curtains at edges -->
<path d="M0 0 H150 Q120 220 145 430 Q160 650 120 900 H0Z" fill="#8e4a4a"/>
<path d="M45 0 Q75 300 55 900 M95 0 Q120 300 105 900" stroke="#6f3438" stroke-width="18" fill="none" opacity=".65"/>
<path d="M1200 0 H1050 Q1080 220 1055 430 Q1040 650 1080 900 H1200Z" fill="#8e4a4a"/>
<path d="M1155 0 Q1125 300 1145 900 M1105 0 Q1080 300 1095 900" stroke="#6f3438" stroke-width="18" fill="none" opacity=".65"/>
<!-- framed empty studio props / plant -->
<g opacity=".9"><path d="M105 760 q10-90-35-140 q75 5 70 75 q40-55 85-50 q-35 65-75 75 q45 35 30 95Z" fill="#5d7d55"/><rect x="78" y="750" width="92" height="68" rx="10" fill="#9b5e46"/><rect x="70" y="742" width="108" height="18" rx="8" fill="#c07a52"/></g>
<g opacity=".9"><path d="M1090 765 q-8-85 38-130 q-70 8-64 68 q-38-50-80-44 q34 60 70 70 q-42 34-26 90Z" fill="#5d7d55"/><rect x="1028" y="755" width="88" height="64" rx="10" fill="#9b5e46"/><rect x="1020" y="747" width="104" height="17" rx="8" fill="#c07a52"/></g>
<!-- rug and shadows -->
<ellipse cx="600" cy="792" rx="455" ry="72" fill="#7a3f3f" opacity=".9"/>
<ellipse cx="600" cy="786" rx="425" ry="62" fill="#a85a50"/>
<ellipse cx="600" cy="786" rx="385" ry="52" fill="none" stroke="#d99a7c" stroke-width="5" stroke-dasharray="14 10" opacity=".8"/>
<ellipse cx="355" cy="790" rx="95" ry="18" fill="#3d2720" opacity=".35" filter="url(#soft2)"/>
<ellipse cx="545" cy="795" rx="130" ry="20" fill="#3d2720" opacity=".35" filter="url(#soft2)"/>
<ellipse cx="760" cy="790" rx="105" ry="18" fill="#3d2720" opacity=".35" filter="url(#soft2)"/>
<ellipse cx="895" cy="792" rx="90" ry="17" fill="#3d2720" opacity=".3" filter="url(#soft2)"/>
<ellipse cx="610" cy="815" rx="95" ry="16" fill="#3d2720" opacity=".35" filter="url(#soft2)"/>

<!-- ===== TEEN, far left: slouched, leaning away ===== -->
<g transform="rotate(7 295 640)">
  <!-- legs -->
  <path d="M272 650 L250 770 M318 650 L342 768" stroke="#4b3f66" stroke-width="26" stroke-linecap="round"/>
  <ellipse cx="238" cy="778" rx="34" ry="13" fill="#3a304f"/><ellipse cx="356" cy="776" rx="34" ry="13" fill="#3a304f"/>
  <!-- body -->
  <rect x="238" y="500" width="118" height="165" rx="28" fill="url(#purple)" stroke="#46365f" stroke-width="5"/>
  <rect x="262" y="540" width="70" height="52" rx="10" fill="#342a4d"/><circle cx="297" cy="566" r="16" fill="#8be8ff"/><circle cx="297" cy="566" r="6" fill="#14324a"/>
  <rect x="258" y="610" width="78" height="12" rx="6" fill="#46365f" opacity=".5"/>
  <!-- crossed arms -->
  <path d="M248 545 L345 605 M348 542 L252 608" stroke="#46365f" stroke-width="24" stroke-linecap="round"/>
  <path d="M248 545 L345 605 M348 542 L252 608" stroke="#9a84c8" stroke-width="13" stroke-linecap="round"/>
  <!-- neck/head -->
  <rect x="282" y="472" width="28" height="34" fill="#9aa5ad"/>
  <rect x="218" y="360" width="158" height="122" rx="34" fill="url(#purple)" stroke="#46365f" stroke-width="5"/>
  <!-- drooping antenna -->
  <path d="M250 362 Q205 310 228 285" fill="none" stroke="#46365f" stroke-width="7" stroke-linecap="round"/><circle cx="230" cy="282" r="11" fill="#6b5a95"/>
  <!-- headphones -->
  <path d="M222 405 Q225 345 297 342 Q370 345 374 405" fill="none" stroke="#2f2745" stroke-width="14"/>
  <rect x="204" y="395" width="30" height="58" rx="14" fill="#2f2745"/><rect x="360" y="395" width="30" height="58" rx="14" fill="#2f2745"/>
  <circle cx="219" cy="424" r="7" fill="#ff7a8a"/><circle cx="375" cy="424" r="7" fill="#ff7a8a"/>
  <!-- half-lidded eyes looking away (left) -->
  <circle cx="265" cy="420" r="17" fill="#fff"/><circle cx="297" cy="420" r="17" fill="#fff"/>
  <circle cx="256" cy="424" r="7" fill="#241d38"/><circle cx="288" cy="424" r="7" fill="#241d38"/>
  <path d="M246 404 h38 M278 404 h38" stroke="#46365f" stroke-width="9" stroke-linecap="round"/>
  <!-- flat unimpressed mouth -->
  <path d="M272 458 q25 6 48-2" fill="none" stroke="#342a4d" stroke-width="6" stroke-linecap="round"/>
  <circle cx="240" cy="445" r="8" fill="#b48ec7" opacity=".8"/><circle cx="354" cy="445" r="8" fill="#b48ec7" opacity=".8"/>
</g>

<!-- ===== DAD, back-left centre: stiff, proud, awkward thumbs-up ===== -->
<g>
  <path d="M425 565 L410 772 M500 565 L520 772" stroke="#274b52" stroke-width="30" stroke-linecap="round"/>
  <ellipse cx="398" cy="780" rx="40" ry="14" fill="#1e363b"/><ellipse cx="534" cy="780" rx="40" ry="14" fill="#1e363b"/>
  <!-- arm behind to teen shoulder (hand hovering just above it) -->
  <path d="M398 430 Q320 440 305 505" fill="none" stroke="#274b52" stroke-width="28" stroke-linecap="round"/>
  <circle cx="302" cy="512" r="19" fill="#d9e2e6" stroke="#274b52" stroke-width="4"/>
  <!-- other arm: stiff thumbs-up -->
  <path d="M535 435 Q585 470 578 525" fill="none" stroke="#274b52" stroke-width="28" stroke-linecap="round"/>
  <g transform="rotate(12 580 520)"><circle cx="580" cy="518" r="19" fill="#d9e2e6" stroke="#274b52" stroke-width="4"/><rect x="572" y="488" width="15" height="30" rx="7" fill="#d9e2e6" stroke="#274b52" stroke-width="3"/></g>
  <!-- torso suit -->
  <rect x="392" y="405" width="150" height="185" rx="26" fill="url(#teal)" stroke="#274b52" stroke-width="5"/>
  <path d="M467 405 L440 500 L467 545 L494 500Z" fill="#eef3f3"/><path d="M455 455 h24 l-12 24Z" fill="#c93b4a"/>
  <circle cx="467" cy="525" r="6" fill="#17363b"/><circle cx="467" cy="548" r="6" fill="#17363b"/>
  <rect x="500" y="452" width="30" height="24" rx="4" fill="#fff" opacity=".85"/><path d="M505 452 l10 12 10-12" fill="#d45f68"/>
  <!-- head -->
  <rect x="452" y="365" width="30" height="42" fill="#9aa5ad"/>
  <rect x="385" y="235" width="165" height="140" rx="28" fill="url(#teal)" stroke="#274b52" stroke-width="5"/>
  <rect x="402" y="258" width="131" height="18" rx="9" fill="#1d4a50" opacity=".35"/>
  <line x1="467" y1="235" x2="467" y2="195" stroke="#274b52" stroke-width="8" stroke-linecap="round"/><circle cx="467" cy="185" r="13" fill="#ffd34d" stroke="#274b52" stroke-width="4"/>
  <!-- ears / bolts -->
  <rect x="368" y="295" width="20" height="36" rx="6" fill="#8fa0a8"/><rect x="547" y="295" width="20" height="36" rx="6" fill="#8fa0a8"/>
  <!-- eyes glancing sideways at teen, raised brow -->
  <circle cx="432" cy="310" r="19" fill="#fff"/><circle cx="502" cy="310" r="19" fill="#fff"/>
  <circle cx="421" cy="312" r="8" fill="#142f36"/><circle cx="491" cy="312" r="8" fill="#142f36"/>
  <path d="M412 282 q20-12 40-2 M482 280 q20-10 40 2" fill="none" stroke="#274b52" stroke-width="6" stroke-linecap="round"/>
  <!-- wide forced grin -->
  <path d="M425 342 q42 22 84 0 q-6 24-42 24 q-36 0-42-24Z" fill="#17363b"/><path d="M432 346 h70" stroke="#fff" stroke-width="7" stroke-linecap="round"/>
  <circle cx="405" cy="335" r="9" fill="#6fb8ad" opacity=".8"/><circle cx="530" cy="335" r="9" fill="#6fb8ad" opacity=".8"/>
</g>

<!-- ===== MOM, back-right centre: leaning into dad, fixing kid ===== -->
<g transform="rotate(-4 675 520)">
  <path d="M650 590 L632 768 M715 590 L748 765" stroke="#7d3542" stroke-width="26" stroke-linecap="round"/>
  <path d="M618 772 q22-16 42 0 q-4 14-42 0Z" fill="#5d2733"/><path d="M735 770 q24-14 42 2 q-6 13-42-2Z" fill="#5d2733"/>
  <!-- arm reaching down to straighten kid's antenna -->
  <path d="M640 470 Q600 545 612 610" fill="none" stroke="#7d3542" stroke-width="24" stroke-linecap="round"/>
  <circle cx="614" cy="618" r="17" fill="#ffe0d1" stroke="#7d3542" stroke-width="4"/>
  <!-- arm linked through dad's side -->
  <path d="M735 465 Q790 500 775 560" fill="none" stroke="#7d3542" stroke-width="24" stroke-linecap="round"/>
  <circle cx="774" cy="566" r="17" fill="#ffe0d1" stroke="#7d3542" stroke-width="4"/>
  <!-- dress body -->
  <path d="M625 420 L735 420 L765 610 L595 610Z" fill="url(#coral)" stroke="#7d3542" stroke-width="5" stroke-linejoin="round"/>
  <path d="M600 575 h160" stroke="#fff" stroke-width="8" stroke-dasharray="2 16" stroke-linecap="round" opacity=".9"/>
  <!-- pearl necklace -->
  <g fill="#fff7e8" stroke="#caa27a" stroke-width="1.5"><circle cx="650" cy="445" r="7"/><circle cx="665" cy="455" r="7"/><circle cx="682" cy="458" r="7"/><circle cx="699" cy="455" r="7"/><circle cx="713" cy="445" r="7"/></g>
  <rect x="665" y="388" width="28" height="38" fill="#c9a18f"/>
  <!-- head -->
  <rect x="598" y="250" width="158" height="132" rx="42" fill="url(#coral)" stroke="#7d3542" stroke-width="5"/>
  <!-- hair bun antenna curls -->
  <circle cx="625" cy="245" r="24" fill="#7d3542"/><circle cx="680" cy="228" r="28" fill="#7d3542"/><circle cx="732" cy="245" r="24" fill="#7d3542"/>
  <circle cx="680" cy="228" r="10" fill="#ffd34d"/>
  <rect x="582" y="305" width="18" height="34" rx="6" fill="#c9a18f"/><rect x="754" y="305" width="18" height="34" rx="6" fill="#c9a18f"/>
  <!-- eyes: one winking, lashes -->
  <circle cx="645" cy="315" r="18" fill="#fff"/><circle cx="650" cy="318" r="8" fill="#3a2028"/>
  <path d="M695 315 q18-14 36 0" fill="none" stroke="#3a2028" stroke-width="7" stroke-linecap="round"/>
  <path d="M625 298 l-10-8 M635 294 l-6-11 M738 296 l10-9 M730 293 l7-11" stroke="#3a2028" stroke-width="4" stroke-linecap="round"/>
  <!-- smile + beauty mark -->
  <path d="M645 350 q32 20 64 0" fill="none" stroke="#7d2432" stroke-width="7" stroke-linecap="round"/>
  <circle cx="730" cy="342" r="4" fill="#7d2432"/><circle cx="620" cy="338" r="10" fill="#ff9d94" opacity=".85"/><circle cx="738" cy="330" r="10" fill="#ff9d94" opacity=".85"/>
</g>

<!-- ===== GRANDMA, far right: hunched, cane, patting kid ===== -->
<g transform="rotate(5 880 650)">
  <path d="M850 665 L838 765 M905 665 L928 760" stroke="#49604a" stroke-width="22" stroke-linecap="round"/>
  <ellipse cx="830" cy="772" rx="30" ry="11" fill="#5b4a68"/><ellipse cx="938" cy="768" rx="30" ry="11" fill="#5b4a68"/>
  <!-- cane -->
  <path d="M945 560 Q985 545 978 585 L970 770" fill="none" stroke="#6b4428" stroke-width="10" stroke-linecap="round"/>
  <!-- reaching arm patting toward kid -->
  <path d="M835 540 Q770 570 735 610" fill="none" stroke="#49604a" stroke-width="22" stroke-linecap="round"/>
  <circle cx="730" cy="614" r="16" fill="#e8dcc8" stroke="#49604a" stroke-width="4"/>
  <!-- shawl body -->
  <path d="M825 500 L935 500 L955 680 L805 680Z" fill="url(#mint)" stroke="#49604a" stroke-width="5" stroke-linejoin="round"/>
  <path d="M825 500 L935 500 L945 555 Q880 585 815 555Z" fill="#f3e2b8"/>
  <path d="M835 600 q45 22 90 0 M830 635 q50 22 100 0" fill="none" stroke="#49604a" stroke-width="5" opacity=".45"/>
  <circle cx="880" cy="575" r="18" fill="#fff" opacity=".8"/><path d="M868 575 h24 M880 563 v24" stroke="#d45f68" stroke-width="4"/>
  <!-- head hunched forward -->
  <rect x="865" y="455" width="26" height="34" fill="#a8b0a2"/>
  <rect x="805" y="355" width="145" height="115" rx="38" fill="url(#mint)" stroke="#49604a" stroke-width="5"/>
  <!-- grey coil bun -->
  <circle cx="835" cy="350" r="20" fill="#d8dde0"/><circle cx="878" cy="338" r="24" fill="#e6eaec"/><circle cx="920" cy="350" r="20" fill="#d8dde0"/>
  <path d="M858 335 q20-14 40 0" fill="none" stroke="#9aa5ad" stroke-width="5"/>
  <!-- spectacles on chain -->
  <g fill="none" stroke="#5a4632" stroke-width="5"><circle cx="845" cy="415" r="22"/><circle cx="910" cy="415" r="22"/><path d="M867 415 h21"/></g>
  <path d="M823 425 Q800 470 825 505 M932 425 Q955 465 935 500" fill="none" stroke="#b08d4a" stroke-width="3" stroke-dasharray="5 5"/>
  <circle cx="845" cy="418" r="7" fill="#2d3a2d"/><circle cx="910" cy="418" r="7" fill="#2d3a2d"/>
  <path d="M822 392 q22-10 44 0 M888 392 q22-10 44 0" fill="none" stroke="#49604a" stroke-width="5" stroke-linecap="round"/>
  <!-- small content smile, looking down at kid -->
  <path d="M858 448 q20 12 40 0" fill="none" stroke="#49604a" stroke-width="6" stroke-linecap="round"/>
  <circle cx="822" cy="440" r="9" fill="#a8c69a" opacity=".9"/><circle cx="933" cy="440" r="9" fill="#a8c69a" opacity=".9"/>
</g>

<!-- ===== KID, front centre: mid-bounce, arms up ===== -->
<g>
  <!-- motion arcs -->
  <path d="M505 585 Q470 555 485 520 M715 585 Q750 555 735 520" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" opacity=".7"/>
  <path d="M520 700 L495 765 M695 700 L725 762" stroke="#8a5a18" stroke-width="22" stroke-linecap="round"/>
  <ellipse cx="483" cy="772" rx="32" ry="12" fill="#b03a3a" transform="rotate(-12 483 772)"/><ellipse cx="738" cy="770" rx="32" ry="12" fill="#2f6fb2" transform="rotate(12 738 770)"/>
  <!-- arms up -->
  <path d="M545 625 Q485 580 470 525" fill="none" stroke="#8a5a18" stroke-width="22" stroke-linecap="round"/>
  <path d="M675 625 Q735 580 750 525" fill="none" stroke="#8a5a18" stroke-width="22" stroke-linecap="round"/>
  <g fill="#fff2c8" stroke="#8a5a18" stroke-width="4"><circle cx="468" cy="518" r="17"/><circle cx="752" cy="518" r="17"/></g>
  <path d="M458 500 v-14 M468 498 v-16 M478 500 v-14 M742 500 v-14 M752 498 v-16 M762 500 v-14" stroke="#8a5a18" stroke-width="5" stroke-linecap="round"/>
  <!-- body -->
  <rect x="530" y="605" width="160" height="125" rx="30" fill="url(#yellow)" stroke="#8a5a18" stroke-width="5"/>
  <path d="M545 650 h130" stroke="#fff" stroke-width="10" stroke-dasharray="3 18" stroke-linecap="round" opacity=".9"/>
  <circle cx="610" cy="685" r="22" fill="#e4574d" stroke="#8a5a18" stroke-width="4"/><circle cx="610" cy="685" r="8" fill="#ffd34d"/>
  <rect x="545" y="570" width="24" height="38" fill="#b8a888" transform="rotate(-8 557 589)"/>
  <!-- head lower, mom hand near antenna -->
  <rect x="535" y="465" width="150" height="118" rx="34" fill="url(#yellow)" stroke="#8a5a18" stroke-width="5"/>
  <!-- bent antenna with star -->
  <path d="M610 465 Q600 420 635 405" fill="none" stroke="#8a5a18" stroke-width="7" stroke-linecap="round"/>
  <path d="M635 385 l6 14 15 1-11 10 3 15-13-8-13 8 3-15-11-10 15-1Z" fill="#ff6b7a" stroke="#8a5a18" stroke-width="3" stroke-linejoin="round"/>
  <rect x="520" y="515" width="17" height="30" rx="6" fill="#b8a888"/><rect x="683" y="515" width="17" height="30" rx="6" fill="#b8a888"/>
  <!-- mismatched excited eyes looking up at camera -->
  <circle cx="575" cy="525" r="20" fill="#fff"/><circle cx="645" cy="525" r="14" fill="#fff"/>
  <circle cx="575" cy="518" r="9" fill="#3a2a12"/><circle cx="645" cy="519" r="6" fill="#3a2a12"/>
  <circle cx="578" cy="515" r="3" fill="#fff"/><circle cx="647" cy="517" r="2" fill="#fff"/>
  <!-- huge open grin -->
  <path d="M565 552 q45 34 90 0 q-4 34-45 34 q-41 0-45-34Z" fill="#6b2d1d"/><ellipse cx="610" cy="576" rx="20" ry="8" fill="#ff8a8a"/>
  <path d="M578 554 h18 v12 h-18Z M622 554 h18 v10 h-18Z" fill="#fff"/>
  <circle cx="548" cy="548" r="10" fill="#f2a541" opacity=".9"/><circle cx="672" cy="548" r="10" fill="#f2a541" opacity=".9"/>
</g>

<!-- ===== ROBO-DOG, front right at grandma's feet ===== -->
<g transform="rotate(-3 835 785)">
  <ellipse cx="835" cy="828" rx="72" ry="13" fill="#3d2720" opacity=".3"/>
  <path d="M885 770 Q930 745 925 710" fill="none" stroke="#6b7a85" stroke-width="11" stroke-linecap="round"/>
  <path d="M795 795 v28 M865 795 v28" stroke="#54636d" stroke-width="14" stroke-linecap="round"/>
  <ellipse cx="788" cy="828" rx="18" ry="8" fill="#3d4a52"/><ellipse cx="872" cy="828" rx="18" ry="8" fill="#3d4a52"/>
  <rect x="775" y="745" width="122" height="62" rx="28" fill="url(#metal)" stroke="#54636d" stroke-width="4"/>
  <circle cx="815" cy="776" r="14" fill="#ffb84d"/><circle cx="815" cy="776" r="5" fill="#7a4a12"/>
  <rect x="748" y="705" width="78" height="62" rx="22" fill="url(#metal)" stroke="#54636d" stroke-width="4"/>
  <!-- floppy ear tilted head curiosity -->
  <path d="M752 712 Q725 730 738 762 Q758 755 762 728Z" fill="#54636d"/><path d="M820 710 Q848 722 842 755 Q822 748 818 725Z" fill="#7d8d97"/>
  <circle cx="770" cy="735" r="9" fill="#fff"/><circle cx="802" cy="735" r="9" fill="#fff"/>
  <circle cx="773" cy="738" r="4" fill="#1d2a31"/><circle cx="799" cy="738" r="4" fill="#1d2a31"/>
  <ellipse cx="786" cy="752" rx="9" ry="7" fill="#2b343a"/><path d="M786 759 q0 10-10 8 M786 759 q0 10 10 8" fill="none" stroke="#2b343a" stroke-width="3" stroke-linecap="round"/>
  <path d="M770 700 Q786 680 802 700" fill="none" stroke="#54636d" stroke-width="6"/><circle cx="786" cy="678" r="7" fill="#ff6b7a"/>
  <!-- bone held sideways -->
  <g transform="rotate(18 835 800)"><rect x="815" y="794" width="42" height="12" rx="6" fill="#fff7e0" stroke="#cbb98f" stroke-width="2"/><circle cx="815" cy="794" r="8" fill="#fff7e0" stroke="#cbb98f" stroke-width="2"/><circle cx="815" cy="806" r="8" fill="#fff7e0" stroke="#cbb98f" stroke-width="2"/><circle cx="857" cy="794" r="8" fill="#fff7e0" stroke="#cbb98f" stroke-width="2"/><circle cx="857" cy="806" r="8" fill="#fff7e0" stroke="#cbb98f" stroke-width="2"/></g>
</g>

<!-- foreground self-timer camera hint (out of focus, bottom edge) -->
<g opacity=".92" filter="url(#soft2)">
  <path d="M565 900 L600 845 L635 900Z" fill="#2b2b30"/><rect x="548" y="818" width="104" height="58" rx="12" fill="#33333a"/>
  <circle cx="600" cy="847" r="20" fill="#15151a"/><circle cx="600" cy="847" r="11" fill="#4a6a7a"/><circle cx="632" cy="830" r="6" fill="#ff4d4d"/>
</g>
<!-- vignette -->
<rect width="1200" height="900" fill="none" stroke="#5d4034" stroke-width="28" opacity=".18"/>
</svg>
'''
OUT.write_text(svg, encoding="utf-8")
print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
