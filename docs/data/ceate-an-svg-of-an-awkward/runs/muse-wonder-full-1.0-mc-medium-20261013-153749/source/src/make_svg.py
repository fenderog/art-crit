#!/usr/bin/env python3
"""Generate awkward robot family portrait SVG (no text)."""
import pathlib

OUT = pathlib.Path("output/robot_family_portrait.svg")

svg = r'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 800" width="1000" height="800">
<defs>
  <radialGradient id="backdrop" cx="50%" cy="38%" r="75%">
    <stop offset="0%" stop-color="#c9d8e4"/><stop offset="45%" stop-color="#8ea8bb"/>
    <stop offset="78%" stop-color="#5f7d94"/><stop offset="100%" stop-color="#435d72"/>
  </radialGradient>
  <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#7a6a62"/><stop offset="100%" stop-color="#4b413c"/>
  </linearGradient>
  <linearGradient id="dadBody" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#d8dde3"/><stop offset="55%" stop-color="#9aa5b1"/><stop offset="100%" stop-color="#6e7a88"/>
  </linearGradient>
  <linearGradient id="momBody" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#f6c9a0"/><stop offset="55%" stop-color="#d98a5a"/><stop offset="100%" stop-color="#a95e38"/>
  </linearGradient>
  <linearGradient id="teenBody" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#4a4a5e"/><stop offset="100%" stop-color="#22222e"/>
  </linearGradient>
  <linearGradient id="grampBody" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#c2b49a"/><stop offset="100%" stop-color="#7d7260"/>
  </linearGradient>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="soft2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.5"/></filter>
</defs>

<!-- STUDIO BACKDROP : classic mottled portrait studio -->
<rect width="1000" height="800" fill="url(#backdrop)"/>
<!-- mottling clouds -->
<g fill="#ffffff" opacity="0.14" filter="url(#soft)">
  <ellipse cx="220" cy="180" rx="180" ry="90"/><ellipse cx="780" cy="140" rx="200" ry="100"/>
  <ellipse cx="520" cy="300" rx="260" ry="110"/><ellipse cx="120" cy="420" rx="140" ry="80"/>
  <ellipse cx="880" cy="380" rx="150" ry="90"/>
</g>
<g fill="#2f4a5f" opacity="0.16" filter="url(#soft)">
  <ellipse cx="90" cy="90" rx="160" ry="110"/><ellipse cx="920" cy="90" rx="170" ry="120"/>
  <ellipse cx="500" cy="90" rx="200" ry="70"/>
</g>
<!-- floor / rug -->
<ellipse cx="500" cy="770" rx="520" ry="95" fill="url(#floor)"/>
<ellipse cx="500" cy="735" rx="410" ry="58" fill="#8a3d3d"/>
<ellipse cx="500" cy="735" rx="375" ry="48" fill="none" stroke="#d9b36a" stroke-width="3" stroke-dasharray="10 6" opacity="0.8"/>
<ellipse cx="500" cy="735" rx="320" ry="38" fill="#9c4a42"/>

<!-- fake studio plants, too close to subjects -->
<g stroke="#2e5d3a" stroke-width="5" stroke-linecap="round" fill="none">
  <path d="M62 610 Q30 500 55 430"/><path d="M72 610 Q85 490 60 410"/><path d="M80 610 Q120 510 105 435"/>
  <path d="M938 615 Q970 505 945 430"/><path d="M928 615 Q915 495 940 410"/><path d="M918 615 Q880 515 898 440"/>
</g>
<g fill="#3a7d4a">
  <ellipse cx="48" cy="435" rx="26" ry="12" transform="rotate(-40 48 435)"/><ellipse cx="66" cy="410" rx="24" ry="11" transform="rotate(20 66 410)"/>
  <ellipse cx="102" cy="440" rx="24" ry="11" transform="rotate(35 102 440)"/><ellipse cx="36" cy="495" rx="22" ry="10" transform="rotate(-25 36 495)"/>
  <ellipse cx="952" cy="435" rx="26" ry="12" transform="rotate(40 952 435)"/><ellipse cx="936" cy="410" rx="24" ry="11" transform="rotate(-20 936 410)"/>
  <ellipse cx="900" cy="445" rx="24" ry="11" transform="rotate(-35 900 445)"/><ellipse cx="964" cy="495" rx="22" ry="10" transform="rotate(25 964 495)"/>
</g>
<path d="M38 610 L96 610 L86 660 L48 660 Z" fill="#b56a44" stroke="#7a4228" stroke-width="3"/>
<path d="M904 615 L962 615 L952 665 L914 665 Z" fill="#b56a44" stroke="#7a4228" stroke-width="3"/>

<!-- soft shadows -->
<g fill="#1c2a36" opacity="0.28" filter="url(#soft2)">
  <ellipse cx="205" cy="702" rx="110" ry="16"/><ellipse cx="475" cy="718" rx="130" ry="18"/>
  <ellipse cx="670" cy="715" rx="115" ry="17"/><ellipse cx="845" cy="720" rx="95" ry="16"/>
  <ellipse cx="445" cy="728" rx="70" ry="12"/>
</g>

<!-- ============ GRANDPA (left, seated, asleep) ============ -->
<g id="grandpa">
  <!-- chair -->
  <rect x="118" y="380" width="175" height="230" rx="18" fill="#6b3f2a" stroke="#3f2517" stroke-width="4"/>
  <rect x="132" y="395" width="147" height="165" rx="12" fill="#8a5540"/>
  <rect x="108" y="520" width="195" height="28" rx="12" fill="#5a3523"/>
  <rect x="122" y="545" width="18" height="145" fill="#4a2c1c"/><rect x="270" y="545" width="18" height="145" fill="#4a2c1c"/>
  <!-- legs dangling, one foot crossed over other -->
  <path d="M165 545 L160 650" stroke="#6e6250" stroke-width="22" stroke-linecap="round"/>
  <path d="M245 545 L262 635" stroke="#6e6250" stroke-width="22" stroke-linecap="round"/>
  <ellipse cx="148" cy="662" rx="30" ry="14" fill="#3d3428" transform="rotate(-12 148 662)"/>
  <ellipse cx="282" cy="645" rx="30" ry="14" fill="#3d3428" transform="rotate(18 282 645)"/>
  <!-- rusty rounded body, cardigan-like panels -->
  <rect x="140" y="365" width="135" height="185" rx="32" fill="url(#grampBody)" stroke="#4d4436" stroke-width="4"/>
  <path d="M207 382 L207 535" stroke="#5d5342" stroke-width="3" stroke-dasharray="6 5"/>
  <circle cx="185" cy="430" r="7" fill="#4d4436"/><circle cx="185" cy="465" r="7" fill="#4d4436"/><circle cx="230" cy="430" r="7" fill="#4d4436"/>
  <!-- rust patches -->
  <ellipse cx="162" cy="500" rx="18" ry="12" fill="#b06a3a" opacity="0.7"/><ellipse cx="252" cy="415" rx="12" ry="9" fill="#b06a3a" opacity="0.6"/>
  <ellipse cx="240" cy="515" rx="10" ry="14" fill="#8f5a34" opacity="0.55"/>
  <!-- arm limp over chair arm, holding cane loosely -->
  <path d="M142 410 Q100 470 108 535" stroke="#8a7d68" stroke-width="18" fill="none" stroke-linecap="round"/>
  <circle cx="110" cy="540" r="14" fill="#6e6250" stroke="#4d4436" stroke-width="3"/>
  <path d="M98 525 Q82 500 98 488 Q114 478 118 495" fill="none" stroke="#5a3a22" stroke-width="7" stroke-linecap="round"/>
  <path d="M102 522 L92 675" stroke="#5a3a22" stroke-width="7" stroke-linecap="round"/>
  <!-- other arm folded in lap -->
  <path d="M272 415 Q300 480 240 520" stroke="#8a7d68" stroke-width="18" fill="none" stroke-linecap="round"/>
  <circle cx="232" cy="522" r="13" fill="#6e6250" stroke="#4d4436" stroke-width="3"/>
  <!-- head tilted asleep, drooping to his left -->
  <rect x="192" y="325" width="32" height="45" fill="#6e6250"/>
  <g transform="rotate(-10 208 335)">
    <rect x="148" y="235" width="120" height="105" rx="28" fill="#d6cbb2" stroke="#4d4436" stroke-width="4"/>
    <!-- bald dome + side tufts (wire hair) -->
    <path d="M150 270 Q130 250 138 235 M152 285 Q132 275 140 260" stroke="#e8e2d2" stroke-width="5" fill="none" stroke-linecap="round"/>
    <path d="M266 270 Q286 250 278 235 M264 285 Q284 275 276 260" stroke="#e8e2d2" stroke-width="5" fill="none" stroke-linecap="round"/>
    <!-- bent antenna -->
    <path d="M208 235 Q200 200 220 185 Q235 175 242 188" fill="none" stroke="#6e6250" stroke-width="5" stroke-linecap="round"/>
    <circle cx="244" cy="192" r="8" fill="#b8a888" stroke="#4d4436" stroke-width="3"/>
    <!-- closed eyes (curved down) + thick brows -->
    <path d="M168 292 Q180 300 192 292" fill="none" stroke="#2b2620" stroke-width="4" stroke-linecap="round"/>
    <path d="M224 292 Q236 300 248 292" fill="none" stroke="#2b2620" stroke-width="4" stroke-linecap="round"/>
    <path d="M164 278 L196 274 M220 274 L252 278" stroke="#e8e2d2" stroke-width="6" stroke-linecap="round"/>
    <!-- monocle slipped down on chain -->
    <circle cx="238" cy="318" r="18" fill="#cfe6ef" fill-opacity="0.45" stroke="#c9a227" stroke-width="3"/>
    <path d="M252 304 Q268 330 258 360" fill="none" stroke="#c9a227" stroke-width="2" stroke-dasharray="3 3"/>
    <!-- mouth open snoring, one gold tooth -->
    <ellipse cx="208" cy="322" rx="16" ry="11" fill="#2b2620"/>
    <rect x="202" y="313" width="10" height="8" fill="#e8c84a"/>
    <!-- moustache grille -->
    <rect x="182" y="305" width="52" height="10" rx="5" fill="#e8e2d2" opacity="0.9"/>
  </g>
  <!-- snore bubbles (not letters) -->
  <circle cx="275" cy="240" r="7" fill="none" stroke="#dbeaf2" stroke-width="2.5" opacity="0.9"/>
  <circle cx="298" cy="212" r="11" fill="none" stroke="#dbeaf2" stroke-width="2.5" opacity="0.75"/>
  <circle cx="328" cy="178" r="16" fill="none" stroke="#dbeaf2" stroke-width="2.5" opacity="0.55"/>
</g>

<!-- ============ DAD (center back, stiff, too formal, staring) ============ -->
<g id="dad">
  <!-- legs rigid, feet in perfect V -->
  <rect x="428" y="560" width="34" height="130" fill="#5a6673"/><rect x="492" y="560" width="34" height="130" fill="#5a6673"/>
  <path d="M428 688 L400 710 L465 710 L462 688 Z" fill="#23272e"/><path d="M492 688 L492 710 L557 710 L526 688 Z" fill="#23272e"/>
  <!-- boxy torso like a suit -->
  <rect x="400" y="295" width="155" height="275" rx="14" fill="url(#dadBody)" stroke="#3c4652" stroke-width="4"/>
  <path d="M400 330 L477 400 L555 330 L555 295 L400 295 Z" fill="#3c4652"/>
  <rect x="460" y="350" width="34" height="90" fill="#eef1f4" stroke="#8a95a3" stroke-width="2"/>
  <!-- crooked bowtie -->
  <g transform="rotate(-14 477 345)"><path d="M477 345 L440 328 L440 362 Z" fill="#b03030"/><path d="M477 345 L514 328 L514 362 Z" fill="#b03030"/><circle cx="477" cy="345" r="8" fill="#7d1f1f"/></g>
  <!-- chest gauge + buttons, pocket square antenna -->
  <circle cx="430" cy="460" r="20" fill="#eef6e8" stroke="#3c4652" stroke-width="3"/><path d="M430 460 L442 448" stroke="#c0392b" stroke-width="3" stroke-linecap="round"/>
  <circle cx="477" cy="470" r="6" fill="#3c4652"/><circle cx="477" cy="500" r="6" fill="#3c4652"/><circle cx="477" cy="530" r="6" fill="#3c4652"/>
  <path d="M518 420 L538 400 L530 435 L520 432 Z" fill="#7fc4d8" stroke="#3c4652" stroke-width="2"/>
  <!-- left arm rigid at side, fist clenched -->
  <path d="M402 320 L362 470" stroke="#7d8a99" stroke-width="24" stroke-linecap="round"/>
  <circle cx="358" cy="482" r="17" fill="#5a6673" stroke="#3c4652" stroke-width="3"/>
  <path d="M346 475 L370 475 M346 485 L370 485" stroke="#3c4652" stroke-width="2"/>
  <!-- right arm: hovering hand NOT quite touching Mom's shoulder (awkward gap) -->
  <path d="M553 320 Q620 330 638 365" stroke="#7d8a99" stroke-width="24" fill="none" stroke-linecap="round"/>
  <g fill="#5a6673" stroke="#3c4652" stroke-width="2.5">
    <ellipse cx="642" cy="372" rx="18" ry="13" transform="rotate(20 642 372)"/>
  </g>
  <path d="M632 360 L628 342 M642 359 L642 340 M652 362 L658 344" stroke="#5a6673" stroke-width="5" stroke-linecap="round"/>
  <!-- neck + square head -->
  <rect x="462" y="265" width="30" height="34" fill="#5a6673"/>
  <rect x="405" y="130" width="145" height="140" rx="16" fill="#e6eaef" stroke="#3c4652" stroke-width="4"/>
  <!-- flat-top hair plate + perfectly straight antenna -->
  <rect x="405" y="130" width="145" height="28" rx="12" fill="#3c4652"/>
  <path d="M477 130 L477 78" stroke="#3c4652" stroke-width="6" stroke-linecap="round"/><circle cx="477" cy="68" r="12" fill="#e74c3c" stroke="#7d1f1f" stroke-width="3"/>
  <circle cx="473" cy="64" r="4" fill="#ffb3ab"/>
  <!-- ears: bolts -->
  <rect x="388" y="195" width="18" height="30" rx="4" fill="#8a95a3" stroke="#3c4652" stroke-width="3"/>
  <rect x="549" y="195" width="18" height="30" rx="4" fill="#8a95a3" stroke="#3c4652" stroke-width="3"/>
  <!-- wide unblinking stare straight at viewer -->
  <circle cx="447" cy="195" r="20" fill="#fff" stroke="#3c4652" stroke-width="3"/><circle cx="508" cy="195" r="20" fill="#fff" stroke="#3c4652" stroke-width="3"/>
  <circle cx="447" cy="197" r="10" fill="#2a6fb7"/><circle cx="508" cy="197" r="10" fill="#2a6fb7"/>
  <circle cx="447" cy="197" r="4.5" fill="#111"/><circle cx="508" cy="197" r="4.5" fill="#111"/>
  <!-- raised straight brows, forced grin showing grille teeth -->
  <path d="M425 165 L469 165 M486 165 L530 165" stroke="#3c4652" stroke-width="6" stroke-linecap="round"/>
  <rect x="435" y="232" width="85" height="24" rx="6" fill="#2b2f36" stroke="#111" stroke-width="2"/>
  <path d="M449 232 L449 256 M463 232 L463 256 M477 232 L477 256 M491 232 L491 256 M505 232 L505 256 M435 244 L520 244" stroke="#d9e2ea" stroke-width="2"/>
</g>

<!-- ============ MOM (right of dad, holding baby, exasperated) ============ -->
<g id="mom">
  <!-- legs: one foot tapping (motion arcs) -->
  <path d="M645 565 L638 685" stroke="#8a5a3a" stroke-width="24" stroke-linecap="round"/>
  <path d="M712 565 L725 670" stroke="#8a5a3a" stroke-width="24" stroke-linecap="round"/>
  <ellipse cx="628" cy="700" rx="34" ry="14" fill="#5d3320"/>
  <g transform="rotate(-22 735 678)"><ellipse cx="742" cy="682" rx="34" ry="14" fill="#5d3320"/></g>
  <path d="M745 640 Q775 655 778 685 M758 625 Q795 645 798 685" fill="none" stroke="#dbeaf2" stroke-width="3" opacity="0.7" stroke-linecap="round"/>
  <!-- rounded pear body, apron-like panel -->
  <path d="M610 320 Q600 520 635 575 L735 575 Q770 520 760 320 Q685 285 610 320 Z" fill="url(#momBody)" stroke="#6e3f24" stroke-width="4"/>
  <path d="M640 390 Q685 370 730 390 L725 540 Q685 555 645 540 Z" fill="#fdf3e3" opacity="0.92" stroke="#c9a87a" stroke-width="2"/>
  <circle cx="685" cy="430" r="9" fill="#e67e22" stroke="#6e3f24" stroke-width="2"/><circle cx="685" cy="470" r="9" fill="#e67e22" stroke="#6e3f24" stroke-width="2"/>
  <!-- tool bits in apron pocket -->
  <rect x="655" y="495" width="60" height="34" rx="6" fill="#e8dcc4" stroke="#c9a87a" stroke-width="2"/>
  <path d="M660 495 L682 476" stroke="#7a7a7a" stroke-width="5" stroke-linecap="round"/>
  <circle cx="700" cy="484" r="5" fill="#7a7a7a"/><circle cx="710" cy="492" r="4" fill="#7a7a7a"/>
  <!-- one arm on hip (elbow jutting into Dad's space) -->
  <path d="M615 360 Q565 400 585 450 Q600 480 640 465" stroke="#c97a4a" stroke-width="22" fill="none" stroke-linecap="round"/>
  <circle cx="645" cy="462" r="14" fill="#8a5a3a" stroke="#6e3f24" stroke-width="3"/>
  <!-- head: round, copper, hair = coiled wire buns -->
  <circle cx="685" cy="225" r="72" fill="#f2d1ae" stroke="#6e3f24" stroke-width="4"/>
  <circle cx="618" cy="180" r="24" fill="none" stroke="#b87333" stroke-width="7"/><circle cx="618" cy="180" r="12" fill="none" stroke="#b87333" stroke-width="5"/>
  <circle cx="752" cy="180" r="24" fill="none" stroke="#b87333" stroke-width="7"/><circle cx="752" cy="180" r="12" fill="none" stroke="#b87333" stroke-width="5"/>
  <path d="M630 168 Q685 140 740 168" fill="none" stroke="#b87333" stroke-width="10" stroke-linecap="round"/>
  <!-- single drooping antenna with flower -->
  <path d="M685 153 Q700 115 725 108" fill="none" stroke="#6e3f24" stroke-width="4" stroke-linecap="round"/>
  <g fill="#e87aa0"><circle cx="725" cy="95" r="9"/><circle cx="713" cy="105" r="9"/><circle cx="737" cy="105" r="9"/><circle cx="718" cy="115" r="9"/><circle cx="732" cy="115" r="9"/></g>
  <circle cx="725" cy="105" r="7" fill="#f9d976"/>
  <!-- eyes looking DOWN/SIDE at the jumping kid, half-lidded, one brow up -->
  <ellipse cx="658" cy="222" rx="17" ry="15" fill="#fff" stroke="#6e3f24" stroke-width="3"/>
  <ellipse cx="712" cy="222" rx="17" ry="15" fill="#fff" stroke="#6e3f24" stroke-width="3"/>
  <circle cx="650" cy="228" r="8" fill="#3a7d4a"/><circle cx="704" cy="228" r="8" fill="#3a7d4a"/>
  <circle cx="650" cy="228" r="3.5" fill="#111"/><circle cx="704" cy="228" r="3.5" fill="#111"/>
  <path d="M640 212 Q658 204 676 212" fill="#f2d1ae" stroke="#6e3f24" stroke-width="3"/>
  <path d="M694 212 Q712 204 730 212" fill="#f2d1ae" stroke="#6e3f24" stroke-width="3"/>
  <path d="M640 192 L676 186" stroke="#6e3f24" stroke-width="5" stroke-linecap="round"/>
  <path d="M694 198 L730 202" stroke="#6e3f24" stroke-width="5" stroke-linecap="round"/>
  <!-- lashes, flat unimpressed mouth slightly open as if mid-scold -->
  <path d="M642 210 L632 202 M728 210 L738 202" stroke="#6e3f24" stroke-width="3" stroke-linecap="round"/>
  <path d="M660 262 Q685 255 708 264 Q700 278 685 277 Q668 276 660 262 Z" fill="#5d3320"/>
  <ellipse cx="642" cy="248" rx="12" ry="7" fill="#e8a07a" opacity="0.7"/><ellipse cx="728" cy="248" rx="12" ry="7" fill="#e8a07a" opacity="0.7"/>
  <!-- steam/heat wisp from head vent (patience running out) -->
  <path d="M635 150 Q625 125 635 105 Q645 85 635 65" fill="none" stroke="#ffffff" stroke-width="4" opacity="0.65" stroke-linecap="round"/>
</g>

<!-- ============ TEEN (far right, leaning AWAY, arms crossed, ignoring camera) ============ -->
<g id="teen" transform="rotate(5 855 450)">
  <!-- long skinny legs, one foot pointed toward exit -->
  <path d="M835 555 L828 690 M878 555 L895 685" stroke="#2e2e3e" stroke-width="20" stroke-linecap="round"/>
  <ellipse cx="820" cy="702" rx="30" ry="13" fill="#15151e"/>
  <ellipse cx="918" cy="695" rx="32" ry="13" fill="#15151e" transform="rotate(14 918 695)"/>
  <rect x="802" y="688" width="36" height="8" fill="#e74c6f"/><rect x="888" y="680" width="36" height="8" fill="#e74c6f" transform="rotate(14 888 680)"/>
  <!-- slouching torso, hoodie-like shell -->
  <path d="M800 300 Q855 275 910 300 L900 560 Q855 578 810 560 Z" fill="url(#teenBody)" stroke="#111118" stroke-width="4"/>
  <path d="M815 320 Q855 345 895 320 L890 400 Q855 415 820 400 Z" fill="#3a3a4e"/>
  <!-- glowing chest screen (broken-heart / low battery shapes, no letters) -->
  <rect x="830" y="430" width="52" height="38" rx="6" fill="#111118" stroke="#e74c6f" stroke-width="2"/>
  <path d="M856 462 C838 448 838 434 848 434 C853 434 856 438 856 441 C856 438 859 434 864 434 C874 434 874 448 856 462Z" fill="none" stroke="#e74c6f" stroke-width="2.5"/>
  <path d="M856 441 L852 449 L858 452 L854 460" fill="none" stroke="#e74c6f" stroke-width="2"/>
  <!-- crossed arms, tight -->
  <path d="M805 360 L900 430" stroke="#4a4a62" stroke-width="20" stroke-linecap="round"/>
  <path d="M905 360 L812 435" stroke="#5a5a74" stroke-width="20" stroke-linecap="round"/>
  <circle cx="808" cy="438" r="12" fill="#2e2e3e" stroke="#111" stroke-width="2"/><circle cx="902" cy="433" r="12" fill="#2e2e3e" stroke="#111" stroke-width="2"/>
  <rect x="840" y="255" width="30" height="55" fill="#4a4a62"/>
  <!-- head turned in profile-ish 3/4 away from family, chin down -->
  <g transform="rotate(-8 855 215)">
    <rect x="800" y="150" width="112" height="118" rx="34" fill="#6a6a82" stroke="#22222e" stroke-width="4"/>
    <!-- mohawk: row of spikes, dyed tip -->
    <path d="M820 152 L830 108 L845 148 L855 100 L870 148 L883 110 L893 152" fill="#8e44ad" stroke="#4a2366" stroke-width="3" stroke-linejoin="round"/>
    <!-- headphones over ears, cord dangling -->
    <path d="M798 200 Q798 140 856 138 Q914 140 914 200" fill="none" stroke="#e74c6f" stroke-width="10"/>
    <rect x="782" y="190" width="30" height="48" rx="12" fill="#ffd1dc" stroke="#7d2440" stroke-width="3"/>
    <rect x="898" y="190" width="30" height="48" rx="12" fill="#ffd1dc" stroke="#7d2440" stroke-width="3"/>
    <path d="M797 238 Q790 300 815 330 Q835 355 830 390" fill="none" stroke="#e74c6f" stroke-width="3"/>
    <!-- half-closed eye looking off-frame right, heavy lid -->
    <ellipse cx="838" cy="210" rx="15" ry="13" fill="#fff" stroke="#222" stroke-width="3"/>
    <ellipse cx="882" cy="210" rx="15" ry="13" fill="#fff" stroke="#222" stroke-width="3"/>
    <circle cx="846" cy="214" r="7" fill="#8e44ad"/><circle cx="890" cy="214" r="7" fill="#8e44ad"/>
    <circle cx="846" cy="214" r="3" fill="#111"/><circle cx="890" cy="214" r="3" fill="#111"/>
    <path d="M822 202 Q838 194 854 202 L854 208 L822 208 Z" fill="#4a4a62"/>
    <path d="M866 202 Q882 194 898 202 L898 208 L866 208 Z" fill="#4a4a62"/>
    <path d="M822 188 L852 184 M868 184 L898 188" stroke="#222" stroke-width="4" stroke-linecap="round"/>
    <!-- flat mouth, lip ring bolt -->
    <path d="M842 248 L878 246" stroke="#222" stroke-width="4" stroke-linecap="round"/>
    <circle cx="874" cy="252" r="6" fill="none" stroke="#d9d9d9" stroke-width="2.5"/>
    <!-- cheek sticker / rivet -->
    <path d="M818 232 L830 244 M830 232 L818 244" stroke="#e74c6f" stroke-width="3" stroke-linecap="round"/>
  </g>
  <!-- music notes shapes escaping headphone (circles+stems, not text) -->
  <g fill="#2e2e3e"><ellipse cx="945" cy="185" rx="9" ry="7" transform="rotate(-20 945 185)"/><rect x="951" y="150" width="4" height="36"/><path d="M951 150 Q965 155 960 170 Q955 160 951 162Z"/></g>
  <g fill="#2e2e3e" opacity="0.7"><ellipse cx="962" cy="230" rx="7" ry="5" transform="rotate(-20 962 230)"/><rect x="967" y="205" width="3" height="26"/></g>
</g>

<!-- BABY in Mom's other arm, chewing her finger/cable, upside-down-ish hold -->
<g id="baby" transform="translate(-295 -140) scale(1.38)">
  <path d="M758 350 Q810 380 795 435 Q780 475 730 460" stroke="#c97a4a" stroke-width="22" fill="none" stroke-linecap="round"/>
  <circle cx="725" cy="458" r="14" fill="#8a5a3a" stroke="#6e3f24" stroke-width="3"/>
  <g transform="rotate(18 785 405)">
    <rect x="750" y="375" width="72" height="62" rx="22" fill="#aee3f5" stroke="#3a6a7d" stroke-width="3"/>
    <circle cx="786" cy="360" r="34" fill="#d9f2fb" stroke="#3a6a7d" stroke-width="3"/>
    <!-- single sprout antenna + curl -->
    <path d="M786 326 Q786 305 800 300 Q812 296 810 288" fill="none" stroke="#3a6a7d" stroke-width="4" stroke-linecap="round"/>
    <circle cx="772" cy="358" r="9" fill="#fff" stroke="#3a6a7d" stroke-width="2"/><circle cx="800" cy="358" r="9" fill="#fff" stroke="#3a6a7d" stroke-width="2"/>
    <!-- cross-eyed looking at cable in mouth -->
    <circle cx="776" cy="360" r="4" fill="#111"/><circle cx="796" cy="360" r="4" fill="#111"/>
    <ellipse cx="786" cy="378" rx="12" ry="9" fill="#2b2f36"/>
    <!-- plug pacifier hanging unused from neck, instead chewing black cable -->
    <path d="M786 378 Q770 400 745 405" fill="none" stroke="#222" stroke-width="5" stroke-linecap="round"/>
    <path d="M770 395 Q760 420 770 435" fill="none" stroke="#e87aa0" stroke-width="3"/>
    <rect x="762" y="432" width="16" height="12" rx="3" fill="#e87aa0" stroke="#8a3a5a" stroke-width="2"/>
    <circle cx="770" cy="450" r="6" fill="#f9c9d9" stroke="#8a3a5a" stroke-width="2"/>
    <!-- tiny kicking legs -->
    <path d="M765 437 L755 462 M805 437 L820 458" stroke="#3a6a7d" stroke-width="9" stroke-linecap="round"/>
    <circle cx="752" cy="466" r="8" fill="#3a6a7d"/><circle cx="824" cy="462" r="8" fill="#3a6a7d"/>
    <path d="M752 395 L730 410 M820 395 L842 385" stroke="#3a6a7d" stroke-width="9" stroke-linecap="round"/>
  </g>
  <!-- drool / spark where cable is chewed -->
  <path d="M732 400 L722 390 M738 412 L724 412 M740 392 L750 380" stroke="#f9d976" stroke-width="3" stroke-linecap="round"/>
</g>


<!-- ============ LITTLE KID (front center, mid-jump, photobombing) ============ -->
<g id="kid" transform="translate(-18 28)">
  <!-- motion blur arcs -->
  <path d="M365 620 Q380 560 365 500 M545 620 Q530 560 545 500" fill="none" stroke="#ffffff" stroke-width="4" opacity="0.55" stroke-linecap="round"/>
  <path d="M390 660 Q455 680 520 660" fill="none" stroke="#ffffff" stroke-width="4" opacity="0.45" stroke-linecap="round"/>
  <!-- legs kicking in air (feet off ground, shadow below proves jump) -->
  <path d="M430 600 L395 655" stroke="#c0392b" stroke-width="18" stroke-linecap="round"/>
  <path d="M478 600 L515 640" stroke="#c0392b" stroke-width="18" stroke-linecap="round"/>
  <ellipse cx="382" cy="665" rx="26" ry="12" fill="#f9d976" stroke="#8a6d1b" stroke-width="3" transform="rotate(-20 382 665)"/>
  <ellipse cx="530" cy="648" rx="26" ry="12" fill="#f9d976" stroke="#8a6d1b" stroke-width="3" transform="rotate(25 530 648)"/>
  <!-- small round red body, too-small, belly light -->
  <ellipse cx="455" cy="540" rx="62" ry="72" fill="#e74c3c" stroke="#7d1f1f" stroke-width="4"/>
  <circle cx="455" cy="555" r="22" fill="#fdebd0" stroke="#7d1f1f" stroke-width="3"/>
  <circle cx="455" cy="555" r="12" fill="#f9d976"/><circle cx="450" cy="550" r="4" fill="#fff3b0"/>
  <rect x="420" y="495" width="70" height="14" rx="7" fill="#f9d976" stroke="#7d1f1f" stroke-width="2"/>
  <!-- arms flung wide, one making bunny-ears behind Dad / actually front waving -->
  <path d="M398 515 Q340 480 330 420" stroke="#c0392b" stroke-width="17" fill="none" stroke-linecap="round"/>
  <path d="M512 515 Q570 475 585 415" stroke="#c0392b" stroke-width="17" fill="none" stroke-linecap="round"/>
  <!-- hands with splayed fingers -->
  <g stroke="#7d1f1f" stroke-width="3" fill="#f5b7a8">
    <circle cx="328" cy="412" r="14"/>
    <circle cx="588" cy="407" r="14"/>
  </g>
  <path d="M318 400 L306 384 M330 398 L328 378 M342 402 L354 386" stroke="#c0392b" stroke-width="5" stroke-linecap="round"/>
  <path d="M578 395 L566 379 M590 393 L592 373 M600 397 L612 381" stroke="#c0392b" stroke-width="5" stroke-linecap="round"/>
  <!-- head: big round, propeller cap -->
  <circle cx="455" cy="420" r="58" fill="#fde8d0" stroke="#7d1f1f" stroke-width="4"/>
  <path d="M400 395 Q455 350 510 395 L510 385 Q455 335 400 385 Z" fill="#3498db" stroke="#1a5276" stroke-width="3"/>
  <path d="M455 362 L455 338" stroke="#1a5276" stroke-width="5" stroke-linecap="round"/>
  <ellipse cx="420" cy="335" rx="38" ry="9" fill="#f9d976" stroke="#8a6d1b" stroke-width="2" transform="rotate(-8 420 335)"/>
  <ellipse cx="490" cy="335" rx="38" ry="9" fill="#ffd1dc" stroke="#7d2440" stroke-width="2" transform="rotate(-8 490 335)"/>
  <circle cx="455" cy="335" r="8" fill="#2b2f36"/>
  <!-- propeller spin arcs -->
  <path d="M385 315 Q455 295 525 315" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.6" stroke-linecap="round"/>
  <!-- one eye huge at camera, one winking; tongue out -->
  <circle cx="432" cy="418" r="17" fill="#fff" stroke="#7d1f1f" stroke-width="3"/>
  <circle cx="435" cy="420" r="9" fill="#222"/><circle cx="432" cy="416" r="3.5" fill="#fff"/>
  <path d="M468 418 Q480 410 492 418" fill="none" stroke="#222" stroke-width="4" stroke-linecap="round"/>
  <path d="M414 394 Q432 386 450 394 M466 392 Q480 384 494 392" fill="none" stroke="#7d1f1f" stroke-width="4" stroke-linecap="round"/>
  <!-- huge open grin, missing front tooth -->
  <path d="M418 442 Q455 475 492 442 Q485 472 455 474 Q425 472 418 442 Z" fill="#5d1a1a" stroke="#3a0f0f" stroke-width="2"/>
  <rect x="428" y="442" width="16" height="14" fill="#fff"/><rect x="464" y="442" width="16" height="14" fill="#fff"/>
  <!-- missing tooth gap in middle, tongue -->
  <ellipse cx="460" cy="466" rx="16" ry="9" fill="#e87aa0"/>
  <ellipse cx="415" cy="438" rx="11" ry="7" fill="#f5a08a" opacity="0.8"/><ellipse cx="495" cy="438" rx="11" ry="7" fill="#f5a08a" opacity="0.8"/>
  <!-- freckle rivets -->
  <circle cx="412" cy="432" r="2.5" fill="#7d1f1f"/><circle cx="420" cy="438" r="2.5" fill="#7d1f1f"/><circle cx="492" cy="432" r="2.5" fill="#7d1f1f"/><circle cx="498" cy="438" r="2.5" fill="#7d1f1f"/>
</g>

<!-- bunny-ears: kid's far hand actually behind Dad's leg? Add Dad bunny ears from Mom? -->
<!-- Instead: Dad unknowingly has a small magnet flower stuck to head from kid -->
<g>
  <circle cx="535" cy="145" r="7" fill="#e87aa0"/><circle cx="525" cy="152" r="7" fill="#e87aa0"/><circle cx="545" cy="152" r="7" fill="#e87aa0"/>
  <circle cx="535" cy="151" r="5" fill="#f9d976"/>
</g>

<!-- floating dust / camera flash glare in corner -->
<g fill="#ffffff" opacity="0.5">
  <path d="M88 72 L94 52 L100 72 L120 78 L100 84 L94 104 L88 84 L68 78 Z"/>
  <circle cx="150" cy="120" r="3"/><circle cx="850" cy="90" r="3"/><circle cx="300" cy="80" r="2.5"/>
</g>

<!-- vignette frame like old portrait -->
<rect width="1000" height="800" fill="none" stroke="#1c2a36" stroke-width="28" opacity="0.18"/>
<rect x="14" y="14" width="972" height="772" fill="none" stroke="#e8dcc0" stroke-width="3" opacity="0.55"/>
</svg>
'''

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg, encoding="utf-8")
print(f"wrote {OUT} {OUT.stat().st_size} bytes")
assert "<text" not in svg.lower(), "no text allowed"
