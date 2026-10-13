#!/usr/bin/env python3
"""Generate an awkward robot family portrait as a hand-built SVG (no text)."""
from pathlib import Path

OUT = Path("output/robot-family-portrait.svg")

SVG = r'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="1200" height="900" role="img">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#241c4f"/>
    <stop offset="0.55" stop-color="#4b3a7d"/>
    <stop offset="1" stop-color="#2a2358"/>
  </linearGradient>
  <radialGradient id="muslin" cx="0.5" cy="0.42" r="0.62">
    <stop offset="0" stop-color="#c9b8ff" stop-opacity="0.95"/>
    <stop offset="0.45" stop-color="#9a86e0" stop-opacity="0.85"/>
    <stop offset="0.78" stop-color="#6f5db8" stop-opacity="0.45"/>
    <stop offset="1" stop-color="#6f5db8" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3d3170"/>
    <stop offset="1" stop-color="#1c173d"/>
  </linearGradient>
  <linearGradient id="metalBlue" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#8fd0f5"/><stop offset="1" stop-color="#4f9fd8"/>
  </linearGradient>
  <linearGradient id="metalPeach" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffc4ad"/><stop offset="1" stop-color="#ff8f7a"/>
  </linearGradient>
  <linearGradient id="metalYellow" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffe873"/><stop offset="1" stop-color="#ffb92e"/>
  </linearGradient>
  <linearGradient id="metalDark" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#5a6478"/><stop offset="1" stop-color="#2f3546"/>
  </linearGradient>
  <linearGradient id="metalRust" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#d99a66"/><stop offset="1" stop-color="#9a5f34"/>
  </linearGradient>
  <linearGradient id="screenCream" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff6d8"/><stop offset="1" stop-color="#ffe9a8"/>
  </linearGradient>
  <pattern id="argyle" width="72" height="72" patternUnits="userSpaceOnUse" patternTransform="rotate(0)">
    <rect width="72" height="72" fill="#13b8a6"/>
    <path d="M36 2 L70 36 L36 70 L2 36 Z" fill="#ff2e9a" opacity="0.92"/>
    <path d="M0 0 L18 18 L0 36 Z M72 0 L72 36 L54 18 Z M0 72 L0 36 L18 54 Z M72 72 L54 54 L72 36 Z" fill="#ffd23b" opacity="0.95"/>
    <path d="M-18 54 L54 -18 M18 90 L90 18 M-18 18 L54 90 M18 -18 L90 54" stroke="#ffffff" stroke-width="2.4" stroke-dasharray="6 5" opacity="0.85" fill="none"/>
    <circle cx="36" cy="36" r="3.2" fill="#fff"/>
  </pattern>
  <pattern id="rugDots" width="34" height="20" patternUnits="userSpaceOnUse">
    <circle cx="8" cy="10" r="2.6" fill="#ffef8a" opacity="0.55"/>
    <circle cx="25" cy="10" r="2.6" fill="#7ef0e2" opacity="0.45"/>
  </pattern>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="7"/>
  </filter>
  <clipPath id="dadTorsoClip"><rect x="338" y="330" width="196" height="252" rx="26"/></clipPath>
  <clipPath id="momTorsoClip"><path d="M652 352 Q740 322 820 356 L842 486 Q846 564 794 586 L676 586 Q626 562 634 486 Z"/></clipPath>
  <clipPath id="teenTorsoClip"><path d="M132 408 Q210 378 286 408 L300 576 Q212 602 120 576 Z"/></clipPath>
  <clipPath id="grandpaTorsoClip"><rect x="502" y="562" width="208" height="152" rx="30"/></clipPath>
  <clipPath id="kidTorsoClip"><rect x="820" y="556" width="152" height="150" rx="34"/></clipPath>
  <clipPath id="dogBodyClip"><rect x="288" y="706" width="168" height="92" rx="44"/></clipPath>
</defs>

<!-- ================= BACKDROP : 80s studio ================= -->
<rect width="1200" height="900" fill="url(#bg)"/>
<ellipse cx="600" cy="412" rx="560" ry="370" fill="url(#muslin)"/>
<!-- laser beams -->
<g opacity="0.32">
  <polygon points="-40,120 1240,520 1240,575 -40,185" fill="#00e5ff"/>
  <polygon points="-40,600 1240,190 1240,232 -40,648" fill="#ff2e9a"/>
  <polygon points="-40,285 1240,640 1240,668 -40,318" fill="#00e5ff" opacity="0.7"/>
  <polygon points="180,-40 900,940 940,940 250,-40" fill="#ffe94a" opacity="0.35"/>
</g>
<g opacity="0.18" stroke="#ffffff" stroke-width="1.6">
  <path d="M0 150 H1200 M0 250 H1200 M0 350 H1200 M0 450 H1200" stroke-dasharray="3 14"/>
</g>
<!-- sparkle stars (shapes only) -->
<g fill="#ffffff">
  <path d="M132 112 l5 14 14 5 -14 5 -5 14 -5 -14 -14 -5 14 -5Z" opacity="0.9"/>
  <path d="M1048 96 l6 16 16 6 -16 6 -6 16 -6 -16 -16 -6 16 -6Z" opacity="0.85"/>
  <path d="M912 196 l4 11 11 4 -11 4 -4 11 -4 -11 -11 -4 11 -4Z" opacity="0.7"/>
  <path d="M290 190 l4 10 10 4 -10 4 -4 10 -4 -10 -10 -4 10 -4Z" opacity="0.65"/>
  <circle cx="78" cy="230" r="4" opacity="0.7"/><circle cx="1108" cy="300" r="5" opacity="0.6"/>
  <circle cx="660" cy="96" r="4" opacity="0.75"/><circle cx="470" cy="132" r="3" opacity="0.6"/>
  <circle cx="1020" cy="470" r="3.5" opacity="0.5"/><circle cx="150" cy="430" r="3.5" opacity="0.5"/>
</g>
<!-- floor -->
<path d="M0 724 H1200 V900 H0 Z" fill="url(#floor)"/>
<path d="M0 724 H1200" stroke="#191d30" stroke-width="6"/>
<ellipse cx="600" cy="798" rx="512" ry="72" fill="#5b2a72" stroke="#191d30" stroke-width="5"/>
<ellipse cx="600" cy="798" rx="512" ry="72" fill="url(#rugDots)"/>
<ellipse cx="600" cy="798" rx="442" ry="56" fill="none" stroke="#ff8ac2" stroke-width="3" stroke-dasharray="12 9" opacity="0.8"/>

<!-- fake fern, left prop -->
<g stroke="#191d30" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <path d="M52 724 L70 642 H150 L168 724 Z" fill="#e86a4a"/>
  <path d="M62 668 H158" fill="none" stroke="#ffd23b" stroke-width="6"/>
  <g fill="none" stroke="#2fae6a" stroke-width="9">
    <path d="M108 648 Q64 588 28 592 M110 648 Q108 572 74 538 M112 648 Q142 570 182 544 M110 648 Q168 600 202 618 M108 648 Q88 600 44 560"/>
  </g>
  <g fill="#3ecf7e" stroke-width="3.5">
    <ellipse cx="34" cy="590" rx="18" ry="8" transform="rotate(-28 34 590)"/>
    <ellipse cx="78" cy="540" rx="18" ry="8" transform="rotate(-52 78 540)"/>
    <ellipse cx="182" cy="546" rx="19" ry="8" transform="rotate(38 182 546)"/>
    <ellipse cx="200" cy="620" rx="17" ry="8" transform="rotate(18 200 620)"/>
  </g>
</g>

<!-- Greek column, right prop, slightly tipped -->
<g transform="rotate(4.5 1075 700)" stroke="#191d30" stroke-width="5" stroke-linejoin="round">
  <ellipse cx="1075" cy="788" rx="78" ry="14" fill="#000" opacity="0.28" filter="url(#soft)" stroke="none"/>
  <rect x="1012" y="720" width="126" height="44" rx="8" fill="#e9e4ff"/>
  <rect x="1028" y="512" width="94" height="212" rx="10" fill="#f4f0ff"/>
  <path d="M1048 520 V714 M1075 520 V714 M1102 520 V714" stroke="#b9aee6" stroke-width="6" fill="none"/>
  <rect x="1006" y="472" width="138" height="44" rx="9" fill="#e9e4ff"/>
  <rect x="1020" y="448" width="110" height="26" rx="7" fill="#fff"/>
  <path d="M1040 492 q12 12 24 0 q12 12 24 0 q12 12 24 0" fill="none" stroke="#b9aee6" stroke-width="4"/>
</g>
<!-- little bust / plant pot wobbling on column -->
<g transform="rotate(9 1078 432)" stroke="#191d30" stroke-width="4.5" stroke-linejoin="round">
  <path d="M1042 452 L1052 410 H1106 L1116 452 Z" fill="#ffd23b"/>
  <circle cx="1078" cy="392" r="26" fill="#3ecf7e"/>
  <circle cx="1056" cy="404" r="16" fill="#2fae6a"/><circle cx="1102" cy="402" r="15" fill="#2fae6a"/>
</g>
<path d="M1118 408 q16 8 12 24 M1134 396 q20 12 14 36" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity="0.85"/>

<!-- floor shadows -->
<g fill="#0d0a24" opacity="0.38" filter="url(#soft)">
  <ellipse cx="215" cy="792" rx="118" ry="18"/>
  <ellipse cx="436" cy="800" rx="128" ry="19"/>
  <ellipse cx="738" cy="800" rx="138" ry="19"/>
  <ellipse cx="606" cy="800" rx="150" ry="20"/>
  <ellipse cx="898" cy="802" rx="118" ry="18"/>
  <ellipse cx="376" cy="806" rx="112" ry="16"/>
</g>

<!-- ================= TEEN : embarrassed, exiled left, slouching away ================= -->
<g stroke="#191d30" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <!-- legs: one straight, one bent tapping -->
  <path d="M170 574 L162 710 L196 716 L206 586 Z" fill="#2b3042"/>
  <path d="M238 584 L272 684 L306 672 L282 574 Z" fill="#2b3042"/>
  <!-- sneakers, toe tapping up -->
  <path d="M142 710 Q140 738 168 740 L214 740 Q226 728 214 712 L196 702 L158 700 Z" fill="#ff2e9a"/>
  <path d="M142 728 H216" stroke="#fff" stroke-width="5" fill="none"/>
  <g transform="rotate(-24 292 690)">
    <path d="M258 674 Q256 700 282 702 L330 702 Q342 690 328 676 L308 664 L274 664 Z" fill="#8b5cf6"/>
    <path d="M260 690 H332" stroke="#fff" stroke-width="5" fill="none"/>
  </g>
  <path d="M312 640 q18 -6 30 4 M320 618 q22 -6 36 6" fill="none" stroke="#fff" stroke-width="4" opacity="0.8"/>
  <!-- torso hoodie, slouched: top narrower, tilted -->
  <g transform="rotate(-3 210 500)">
    <path d="M132 408 Q210 378 286 408 L300 576 Q212 602 120 576 Z" fill="url(#metalDark)"/>
    <g clip-path="url(#teenTorsoClip)" opacity="0.98">
      <rect x="116" y="404" width="190" height="182" fill="url(#argyle)"/>
      <!-- hoodie half-off one shoulder + open diagonal showing rebellion -->
      <path d="M116 404 L212 404 L150 590 L116 590 Z" fill="#232733"/>
      <path d="M286 408 L306 590 L250 590 L236 430 Z" fill="#232733" opacity="0.92"/>
    </g>
    <path d="M132 408 Q210 378 286 408 L300 576 Q212 602 120 576 Z" fill="none"/>
    <path d="M178 404 L138 576" fill="none" stroke="#191d30" stroke-width="4"/>
    <!-- hood bunched behind neck -->
    <path d="M150 402 Q210 362 272 402 Q246 382 210 384 Q176 382 150 402Z" fill="#111522"/>
    <!-- crossed arms -->
    <path d="M128 462 Q208 500 294 478 L300 516 Q212 542 124 502 Z" fill="#3d4458"/>
    <path d="M296 452 Q214 496 128 486 L124 524 Q214 536 298 492 Z" fill="#4a546e"/>
    <circle cx="128" cy="490" r="17" fill="#c8d2e8"/>
    <circle cx="298" cy="474" r="17" fill="#c8d2e8"/>
    <path d="M116 482 h22 M288 464 h20" stroke-width="3.5"/>
    <!-- phone outline bulging pocket -->
    <rect x="236" y="538" width="28" height="40" rx="5" fill="#111522" transform="rotate(8 250 558)"/>
    <circle cx="250" cy="570" r="3" fill="#7ef0e2" stroke="none"/>
  </g>
  <!-- neck -->
  <rect x="192" y="356" width="36" height="34" rx="7" fill="#9aa6c2"/>
  <path d="M192 368 H228 M192 380 H228" stroke-width="3"/>
  <!-- head, tilted down and away from family -->
  <g transform="rotate(-9 210 285)">
    <rect x="126" y="198" width="168" height="168" rx="42" fill="url(#metalDark)"/>
    <rect x="144" y="220" width="132" height="116" rx="28" fill="#161b2c"/>
    <!-- emo wire fringe covering one eye -->
    <path d="M138 206 Q210 182 288 208 L282 262 L244 228 L226 268 L198 230 L176 260 L156 224 L140 244 Z" fill="#0c0f1a"/>
    <!-- drooping antenna -->
    <path d="M254 200 Q284 158 262 132" fill="none" stroke-width="6"/>
    <circle cx="261" cy="130" r="10" fill="#8b5cf6"/>
    <!-- headphones -->
    <path d="M132 238 Q210 176 288 238" fill="none" stroke="#8b5cf6" stroke-width="14"/>
    <rect x="112" y="236" width="34" height="62" rx="14" fill="#8b5cf6"/>
    <rect x="274" y="236" width="34" height="62" rx="14" fill="#8b5cf6"/>
    <circle cx="129" cy="267" r="9" fill="#ffd23b" stroke-width="3.5"/>
    <circle cx="291" cy="267" r="9" fill="#ffd23b" stroke-width="3.5"/>
    <!-- face: eye roll up-left, flat mouth -->
    <path d="M162 272 H196" stroke="#7ef0e2" stroke-width="5"/>
    <circle cx="174" cy="264" r="11" fill="#7ef0e2" stroke="none"/>
    <circle cx="168" cy="259" r="5" fill="#0c0f1a" stroke="none"/>
    <path d="M224 258 a13 13 0 1 0 0.1 0" fill="#7ef0e2" stroke="none" opacity="0.95"/>
    <circle cx="230" cy="252" r="5.5" fill="#0c0f1a" stroke="none"/>
    <path d="M216 246 H252" stroke="#161b2c" stroke-width="6"/>
    <path d="M190 312 H232" stroke="#7ef0e2" stroke-width="6"/>
    <path d="M228 312 q8 2 6 9" fill="none" stroke="#7ef0e2" stroke-width="4"/>
    <!-- highlight -->
    <ellipse cx="168" cy="224" rx="22" ry="9" fill="#fff" opacity="0.28" stroke="none" transform="rotate(-18 168 224)"/>
  </g>
</g>
<!-- gap arrow is empty space itself: teen is set apart from dad -->

<!-- ================= DAD : proud, stiff, mid-blink, hover-hand ================= -->
<g stroke="#191d30" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <!-- stiff legs, feet too close together -->
  <rect x="376" y="578" width="52" height="154" rx="10" fill="#33507a"/>
  <rect x="444" y="578" width="52" height="154" rx="10" fill="#33507a"/>
  <path d="M362 730 H436 L442 756 Q402 764 362 754 Z" fill="#191d30"/>
  <path d="M438 730 H510 L516 756 Q476 764 438 754 Z" fill="#191d30"/>
  <path d="M376 606 H428 M444 606 H496" stroke="#7fb8e8" stroke-width="4"/>
  <!-- left arm stuck stiff thumbs-up at side -->
  <path d="M340 362 Q292 420 300 502 L336 514 Q350 446 366 386 Z" fill="url(#metalBlue)"/>
  <g transform="translate(330 526)">
    <circle r="21" fill="#ffe9a8"/>
    <path d="M-6 -16 Q-4 -38 8 -40 Q16 -30 10 -14" fill="#ffe9a8"/>
    <path d="M-14 2 H10 M-12 10 H12" stroke-width="3.5"/>
  </g>
  <!-- torso fridge -->
  <rect x="338" y="330" width="196" height="252" rx="26" fill="url(#metalBlue)"/>
  <g clip-path="url(#dadTorsoClip)">
    <rect x="338" y="368" width="196" height="168" fill="url(#argyle)"/>
    <rect x="338" y="530" width="196" height="52" fill="#2f4a73"/>
  </g>
  <rect x="338" y="330" width="196" height="252" rx="26" fill="none"/>
  <!-- crooked too-short tie over vest -->
  <g transform="rotate(7 436 386)">
    <path d="M424 344 H448 L444 368 H428 Z" fill="#e11d48"/>
    <path d="M428 368 H444 L450 432 L436 448 L422 432 Z" fill="#e11d48"/>
    <circle cx="436" cy="396" r="4" fill="#ffd23b" stroke="none"/>
    <circle cx="436" cy="418" r="4" fill="#ffd23b" stroke="none"/>
  </g>
  <!-- chest gauge + buttons proud dad gadgets -->
  <circle cx="382" cy="404" r="20" fill="#fff"/>
  <path d="M382 404 L394 392" stroke="#e11d48" stroke-width="4"/>
  <circle cx="382" cy="404" r="4" fill="#191d30" stroke="none"/>
  <circle cx="488" cy="398" r="8" fill="#ffd23b"/><circle cx="488" cy="424" r="8" fill="#7ef0e2"/>
  <rect x="360" y="542" width="152" height="18" rx="8" fill="#111522"/>
  <rect x="420" y="540" width="34" height="22" rx="5" fill="#ffd23b"/>
  <!-- right arm rigidly extended around mom, hovering -->
  <path d="M528 366 Q620 348 686 378 L674 414 Q606 396 524 402 Z" fill="url(#metalBlue)"/>
  <circle cx="530" cy="386" r="16" fill="#2f4a73"/>
  <!-- hover hand itself is drawn later, emerging on mom far shoulder -->
  <!-- neck -->
  <rect x="414" y="296" width="44" height="38" rx="7" fill="#9ac8ec"/>
  <!-- boxy head -->
  <rect x="344" y="138" width="184" height="166" rx="26" fill="url(#metalBlue)"/>
  <rect x="362" y="160" width="148" height="118" rx="18" fill="url(#screenCream)"/>
  <rect x="328" y="200" width="22" height="52" rx="9" fill="#2f4a73"/>
  <rect x="522" y="200" width="22" height="52" rx="9" fill="#2f4a73"/>
  <circle cx="339" cy="226" r="7" fill="#ffd23b" stroke-width="3"/><circle cx="533" cy="226" r="7" fill="#ffd23b" stroke-width="3"/>
  <!-- antenna proud straight -->
  <path d="M436 138 V92" fill="none" stroke-width="7"/>
  <circle cx="436" cy="82" r="14" fill="#e11d48"/>
  <circle cx="432" cy="78" r="4" fill="#fff" stroke="none"/>
  <!-- flash glare on forehead -->
  <path d="M492 152 l4 10 10 4 -10 4 -4 10 -4 -10 -10 -4 10 -4Z" fill="#fff" stroke="none"/>
  <!-- face: one eye open, one mid-blink line, huge forced grin -->
  <circle cx="402" cy="206" r="15" fill="#191d30" stroke="none"/>
  <circle cx="407" cy="201" r="5" fill="#fff" stroke="none"/>
  <path d="M452 206 H486" stroke="#191d30" stroke-width="7"/>
  <path d="M380 180 q20 -12 42 -2 M450 178 q20 -10 38 2" fill="none" stroke-width="5"/>
  <path d="M386 238 Q436 272 486 238 L482 260 Q436 282 390 260 Z" fill="#191d30"/>
  <path d="M394 244 H478 M404 242 V260 M422 250 V266 M440 252 V268 M458 250 V264" stroke="#fff" stroke-width="3.5"/>
  <circle cx="436" cy="290" r="6" fill="#2f4a73"/>
  <ellipse cx="380" cy="172" rx="26" ry="10" fill="#fff" opacity="0.35" stroke="none" transform="rotate(-16 380 172)"/>
</g>

<!-- ================= MOM : exhausted organiser, leaning on dad, multitasking ================= -->
<g stroke="#191d30" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <!-- legs, one foot pigeon-toed inward -->
  <path d="M680 582 L672 706 L708 712 L722 590 Z" fill="#c44a6e"/>
  <path d="M756 590 L782 700 L814 690 L802 582 Z" fill="#c44a6e"/>
  <g transform="rotate(18 690 724)">
    <path d="M656 706 H724 L730 732 Q692 742 656 730 Z" fill="#e11d48"/>
    <path d="M690 730 L694 748 H710 L706 728 Z" fill="#191d30"/>
  </g>
  <path d="M764 692 H836 L842 720 Q802 730 764 718 Z" fill="#e11d48"/>
  <path d="M800 716 L804 736 H820 L816 714 Z" fill="#191d30"/>
  <!-- small third utility arm behind, straightening dad tie area -->
  <path d="M648 430 Q590 420 556 452 L572 476 Q608 456 652 462 Z" fill="#ff9d86"/>
  <circle cx="562" cy="464" r="14" fill="#ffe9a8"/>
  <!-- torso, leaning shape -->
  <path d="M652 352 Q740 322 820 356 L842 486 Q846 564 794 586 L676 586 Q626 562 634 486 Z" fill="url(#metalPeach)"/>
  <g clip-path="url(#momTorsoClip)">
    <rect x="630" y="382" width="216" height="170" fill="url(#argyle)"/>
    <path d="M630 540 H850 V590 H630 Z" fill="#c44a6e"/>
  </g>
  <path d="M652 352 Q740 322 820 356 L842 486 Q846 564 794 586 L676 586 Q626 562 634 486 Z" fill="none"/>
  <!-- necklace of bolts -->
  <path d="M700 366 Q738 392 778 366" fill="none" stroke="#ffd23b" stroke-width="5" stroke-dasharray="1 10"/>
  <circle cx="739" cy="384" r="9" fill="#ff2e9a"/>
  <!-- right arm reaching far down to corral the kid (hand lands later on kid head) -->
  <path d="M828 420 Q900 470 902 536 L868 550 Q852 492 806 456 Z" fill="url(#metalPeach)"/>
  <!-- head group leaning hard toward dad -->
  <rect x="716" y="304" width="40" height="36" rx="7" fill="#ffb59e" transform="rotate(14 736 322)"/>
  <g transform="rotate(17 738 238)">
    <!-- wire hair buns -->
    <circle cx="652" cy="204" r="30" fill="#7c3aed"/>
    <circle cx="824" cy="204" r="30" fill="#7c3aed"/>
    <path d="M636 190 q16 -14 32 0 M632 208 q20 -12 40 0 M808 190 q16 -14 32 0 M804 208 q20 -12 40 0" fill="none" stroke="#ffd23b" stroke-width="4"/>
    <circle cx="652" cy="204" r="10" fill="#ffd23b"/><circle cx="824" cy="204" r="10" fill="#ffd23b"/>
    <!-- head -->
    <rect x="656" y="162" width="164" height="150" rx="52" fill="url(#metalPeach)"/>
    <rect x="672" y="182" width="132" height="104" rx="34" fill="#fff0e6"/>
    <!-- big bow on top, slightly crushed against dad -->
    <g transform="rotate(-14 738 154)">
      <path d="M738 154 L684 124 Q672 154 684 180 Z" fill="#ff2e9a"/>
      <path d="M738 154 L792 124 Q804 154 792 180 Z" fill="#ff2e9a"/>
      <circle cx="738" cy="154" r="14" fill="#ffd23b"/>
    </g>
    <!-- face: eyes darting sideways at kid, strained gritted smile, twitch -->
    <circle cx="714" cy="224" r="13" fill="#fff"/>
    <circle cx="720" cy="228" r="7" fill="#191d30" stroke="none"/>
    <circle cx="768" cy="224" r="13" fill="#fff"/>
    <circle cx="774" cy="228" r="7" fill="#191d30" stroke="none"/>
    <path d="M696 204 l-10 -8 M702 200 l-6 -11 M784 202 l10 -9 M778 198 l6 -11" fill="none" stroke-width="4"/>
    <path d="M694 196 q18 -10 34 -2" fill="none" stroke-width="5"/>
    <path d="M752 192 q20 -12 36 0" fill="none" stroke-width="5"/>
    <path d="M704 258 H776" stroke="#191d30" stroke-width="6"/>
    <path d="M708 258 V270 M722 258 V272 M736 258 V272 M750 258 V272 M764 258 V270" stroke="#191d30" stroke-width="3"/>
    <path d="M776 258 q10 2 8 12" fill="none" stroke-width="4"/>
    <circle cx="692" cy="248" r="11" fill="#ff8fab" opacity="0.75" stroke="none"/>
    <circle cx="790" cy="248" r="11" fill="#ff8fab" opacity="0.75" stroke="none"/>
    <!-- eye twitch ticks -->
    <path d="M792 206 l12 -6 M794 218 h13" fill="none" stroke="#191d30" stroke-width="3.5"/>
    <ellipse cx="692" cy="192" rx="22" ry="8" fill="#fff" opacity="0.4" stroke="none" transform="rotate(-16 692 192)"/>
  </g>
  <!-- left arm cradling baby high (arm under baby drawn here, baby on top next) -->
  <path d="M648 372 Q602 392 610 446 L660 436 Q652 400 670 380 Z" fill="url(#metalPeach)"/>
</g>

<!-- ================= BABY : cross-eyed, held lopsided high between parents, reaching for lens ================= -->
<g transform="translate(-40 -70)" stroke="#191d30" stroke-width="4.5" stroke-linejoin="round" stroke-linecap="round">
  <g transform="rotate(21 660 498)">
    <!-- kicking legs -->
    <path d="M630 544 L612 584 L638 594 L654 556 Z" fill="#9fe8c9"/>
    <path d="M676 550 L700 580 L722 564 L700 534 Z" fill="#9fe8c9"/>
    <ellipse cx="624" cy="592" rx="17" ry="11" fill="#ff8fab"/>
    <ellipse cx="714" cy="572" rx="17" ry="11" fill="#ff8fab" transform="rotate(-28 714 572)"/>
    <!-- body toaster -->
    <rect x="600" y="462" width="118" height="94" rx="30" fill="#9fe8c9"/>
    <rect x="600" y="492" width="118" height="42" fill="url(#argyle)"/>
    <path d="M600 528 H718 L710 556 H608 Z" fill="#e8ecf5"/>
    <path d="M616 540 l10 8 M634 540 l10 8 M670 540 l10 8" stroke="#b9c2d8" stroke-width="3"/>
    <!-- arm grabbing up toward mom bow wire -->
    <path d="M706 476 Q738 448 734 418" fill="none" stroke="#9fe8c9" stroke-width="16"/>
    <path d="M706 476 Q738 448 734 418" fill="none" stroke-width="4.5"/>
    <circle cx="734" cy="416" r="12" fill="#ffe9a8"/>
    <!-- head big -->
    <circle cx="658" cy="420" r="54" fill="#c9f5e2"/>
    <path d="M658 366 Q650 338 630 332 Q652 322 664 340 Q676 322 692 336 Q670 344 668 366" fill="none" stroke-width="5"/>
    <circle cx="630" cy="330" r="7" fill="#ff2e9a"/><circle cx="692" cy="334" r="7" fill="#ffd23b"/>
    <!-- ears -->
    <circle cx="604" cy="424" r="11" fill="#9fe8c9"/><circle cx="712" cy="424" r="11" fill="#9fe8c9"/>
    <!-- cross eyes looking in at pacifier -->
    <circle cx="636" cy="416" r="12" fill="#fff"/>
    <circle cx="642" cy="420" r="6" fill="#191d30" stroke="none"/>
    <circle cx="680" cy="416" r="12" fill="#fff"/>
    <circle cx="674" cy="420" r="6" fill="#191d30" stroke="none"/>
    <circle cx="618" cy="438" r="9" fill="#ff8fab" opacity="0.7" stroke="none"/>
    <circle cx="698" cy="438" r="9" fill="#ff8fab" opacity="0.7" stroke="none"/>
    <!-- plug pacifier in mouth -->
    <ellipse cx="658" cy="444" rx="17" ry="13" fill="#ff2e9a"/>
    <rect x="648" y="452" width="20" height="16" rx="4" fill="#ffd23b"/>
    <path d="M653 468 V480 M663 468 V480" stroke-width="4"/>
    <!-- oil drool drop sliding off -->
    <path d="M676 452 Q686 466 680 476 Q674 466 676 452Z" fill="#4dd8ff" stroke-width="3"/>
  </g>
  <!-- reaching hand toward viewer, clear of grandpa -->
  <path d="M682 492 Q692 498 700 502" fill="none" stroke="#9fe8c9" stroke-width="15"/>
  <g transform="translate(706 506)">
    <circle r="22" fill="#ffe9a8"/>
    <path d="M-16 -9 l-14 -13 M-6 -18 l-5 -18 M6 -19 l3 -18 M15 -12 l13 -12" fill="none" stroke-width="5"/>
    <path d="M-13 8 q13 9 26 0" fill="none" stroke-width="3.5"/>
  </g>
  <!-- mom supporting hand under baby -->
  <ellipse cx="668" cy="550" rx="28" ry="15" fill="#ffe9a8"/>
  <path d="M646 544 h44" stroke-width="3.5"/>
</g>

<!-- Dad hover-hand: palm-down hand floats over mom shoulder, shadow below it, touching nothing -->
<g stroke="#191d30" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <ellipse cx="820" cy="420" rx="24" ry="10" fill="#191d30" opacity="0.35" stroke="none"/>
  <path d="M762 386 Q780 392 796 398" fill="none" stroke="#4f9fd8" stroke-width="15"/>
  <path d="M762 386 Q780 392 796 398" fill="none" stroke-width="5"/>
  <g transform="translate(812 400)">
    <ellipse rx="22" ry="14" fill="#ffe9a8" transform="rotate(-10)"/>
    <path d="M-14 7 v13 M-3 10 v14 M8 9 v13 M17 5 l9 9" fill="none" stroke-width="4.5"/>
  </g>
  <path d="M800 432 q4 6 0 11 M812 435 q4 6 0 11 M824 432 q4 6 0 11" fill="none" stroke="#7ef0e2" stroke-width="3.5"/>
</g>

<!-- dad's other misplaced hand resting proudly on grandpa head (drawn before grandpa head top) -->
<!-- ================= GRANDPA : asleep patriarch, seated front centre ================= -->
<g transform="translate(-55 12)" stroke="#191d30" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <!-- stool -->
  <rect x="518" y="684" width="176" height="22" rx="8" fill="#8b5a34"/>
  <path d="M540 706 L528 786 M672 706 L684 786" stroke="#8b5a34" stroke-width="14"/>
  <path d="M532 750 H680" stroke="#8b5a34" stroke-width="9"/>
  <!-- seated legs spread -->
  <path d="M518 690 L478 748 L534 766 L566 712 Z" fill="#6b4a2f"/>
  <path d="M656 700 L700 750 L750 730 L706 682 Z" fill="#6b4a2f"/>
  <path d="M452 744 H540 L546 772 Q500 780 452 768 Z" fill="#3a2a1e"/>
  <path d="M694 744 H782 L788 772 Q740 780 694 768 Z" fill="#3a2a1e"/>
  <!-- rust spots on legs -->
  <circle cx="506" cy="724" r="7" fill="#e07a3a" stroke-width="3"/><circle cx="706" cy="714" r="6" fill="#e07a3a" stroke-width="3"/>
  <!-- torso slumped -->
  <rect x="502" y="562" width="208" height="152" rx="30" fill="url(#metalRust)"/>
  <g clip-path="url(#grandpaTorsoClip)">
    <rect x="502" y="588" width="208" height="126" fill="url(#argyle)" opacity="0.96"/>
    <!-- patches and holes in his matching vest -->
    <rect x="640" y="640" width="34" height="28" rx="4" fill="#ffd23b" transform="rotate(-8 657 654)"/>
    <path d="M642 646 h30 M646 642 v30" stroke="#191d30" stroke-width="2.5" stroke-dasharray="4 4"/>
    <circle cx="548" cy="624" r="9" fill="#9a5f34"/>
  </g>
  <rect x="502" y="562" width="208" height="152" rx="30" fill="none"/>
  <circle cx="606" cy="606" r="7" fill="#ffd23b"/><circle cx="606" cy="632" r="7" fill="#3a2a1e"/>
  <path d="M606 642 q0 10 -6 14" fill="none" stroke-width="3"/>
  <!-- left arm gripping wrench-cane -->
  <path d="M506 596 Q452 630 462 690 L496 700 Q508 650 526 622 Z" fill="url(#metalRust)"/>
  <path d="M474 688 L460 788" stroke="#9aa6c2" stroke-width="13"/>
  <path d="M474 688 L460 788" fill="none" stroke-width="5"/>
  <path d="M452 776 a16 16 0 1 0 16 -16 l-4 12 Z" fill="#c8d2e8"/>
  <circle cx="476" cy="694" r="17" fill="#e8c9a0"/>
  <!-- right arm limp on knee -->
  <path d="M706 600 Q756 636 742 690 L708 694 Q700 646 690 622 Z" fill="url(#metalRust)"/>
  <ellipse cx="726" cy="696" rx="19" ry="14" fill="#e8c9a0"/>
  <!-- neck short, head drooped -->
  <rect x="584" y="530" width="44" height="34" rx="7" fill="#b9895e" transform="rotate(16 606 547)"/>
  <g transform="translate(-26 26) rotate(18 606 462)">
    <!-- old TV head -->
    <rect x="518" y="386" width="176" height="152" rx="28" fill="url(#metalRust)"/>
    <rect x="534" y="404" width="144" height="106" rx="20" fill="#2d241c"/>
    <!-- glass dome + vacuum tube filaments on top -->
    <path d="M566 386 Q570 338 606 336 Q642 338 646 386 Z" fill="#bfefff" opacity="0.88"/>
    <path d="M588 382 V356 M606 384 V348 M624 382 V356" stroke="#ff9a2e" stroke-width="5"/>
    <path d="M588 356 q9 10 18 0 q9 10 18 0" fill="none" stroke="#ffe94a" stroke-width="4"/>
    <ellipse cx="588" cy="360" rx="18" ry="8" fill="#fff" opacity="0.55" stroke="none" transform="rotate(-22 588 360)"/>
    <!-- side dials / hearing horn falling off -->
    <circle cx="516" cy="452" r="16" fill="#8b5a34"/>
    <circle cx="516" cy="452" r="6" fill="#ffd23b" stroke-width="3"/>
    <circle cx="696" cy="452" r="16" fill="#8b5a34"/>
    <circle cx="696" cy="452" r="6" fill="#ffd23b" stroke-width="3"/>
    <!-- sleeping face: closed eyes, wire beard over mouth -->
    <path d="M552 442 q14 12 28 0 M632 442 q14 12 28 0" fill="none" stroke="#ffe9a8" stroke-width="6"/>
    <path d="M546 420 q20 -8 38 0 M628 420 q20 -8 38 0" fill="none" stroke="#e8e0d0" stroke-width="7"/>
    <!-- nose vent + sleep bubbles (no letters) -->
    <circle cx="606" cy="462" r="8" fill="#e8c9a0"/>
    <!-- jagged wire beard hangs below chin, over torso -->
    <path d="M558 490 Q606 518 654 490 L648 542 L636 528 L626 554 L614 534 L602 558 L590 534 L580 552 L570 528 L564 544 Z" fill="#eef0f5"/>
    <path d="M574 500 v30 M586 508 v28 M598 512 v32 M614 512 v28 M626 508 v30 M638 500 v26" stroke="#b9c2d8" stroke-width="3.5" fill="none"/>
    <path d="M578 484 q28 13 56 0" fill="none" stroke="#fff" stroke-width="9"/>
    <!-- rust spots -->
    <circle cx="548" cy="404" r="6" fill="#e07a3a" stroke-width="2.5"/>
    <circle cx="668" cy="500" r="7" fill="#e07a3a" stroke-width="2.5"/>
  </g>
  <!-- sleep bubbles drifting from nose area -->
  <g fill="#bfefff" opacity="0.92">
    <circle cx="630" cy="458" r="10"/><circle cx="654" cy="432" r="14"/><circle cx="684" cy="402" r="19"/>
    <circle cx="626" cy="454" r="3" fill="#fff" stroke="none"/><circle cx="648" cy="426" r="4" fill="#fff" stroke="none"/><circle cx="676" cy="394" r="5" fill="#fff" stroke="none"/>
  </g>
  <!-- dad hand proudly patting grandpa shoulder from behind the stool -->
  <g transform="translate(524 580)">
    <ellipse rx="24" ry="15" fill="#ffe9a8" transform="rotate(-14)"/>
    <path d="M-14 2 v12 M-3 5 v13 M8 4 v12" fill="none" stroke-width="3.5"/>
  </g>
  <path d="M512 566 Q500 540 506 516" fill="none" stroke="#6bb8e8" stroke-width="14" opacity="0"/>
</g>

<!-- ================= KID : feral, on a crate, mid-jump, stepping on grandpa foot ================= -->
<g stroke="#191d30" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <!-- low step crate kid stands on to be taller; legs stay visible above it -->
  <g>
    <rect x="824" y="752" width="148" height="44" rx="8" fill="#c98a4b"/>
    <path d="M824 774 H972 M852 752 V796 M944 752 V796" stroke="#8b5a34" stroke-width="5" fill="none"/>
    <path d="M824 752 L972 796 M972 752 L824 796" stroke="#8b5a34" stroke-width="4" opacity="0.65" fill="none"/>
  </g>
  <!-- legs: one planted flat on crate, one kicked out toward grandpa shoe -->
  <path d="M918 696 L806 744 L818 770 L940 718 Z" fill="#2f6fd0"/>
  <g transform="rotate(-14 770 772)">
    <path d="M734 758 H800 L804 780 Q770 786 734 776 Z" fill="#13b8a6"/>
    <path d="M738 770 H800" stroke="#fff" stroke-width="4"/>
  </g>
  <path d="M716 742 l-9 -11 M730 736 l-3 -14 M744 740 l5 -13" fill="none" stroke="#ffd23b" stroke-width="4"/>
  <path d="M856 698 L852 732 L888 732 L892 700 Z" fill="#2f6fd0"/>
  <path d="M838 730 H906 L910 752 Q874 758 838 750 Z" fill="#e11d48"/>
  <path d="M842 742 H906" stroke="#fff" stroke-width="4"/>
  <!-- torso: oversized vest slipping off one shoulder -->
  <rect x="820" y="556" width="152" height="150" rx="34" fill="url(#metalYellow)"/>
  <g clip-path="url(#kidTorsoClip)">
    <rect x="820" y="580" width="152" height="126" fill="url(#argyle)" transform="rotate(6 896 640)"/>
    <path d="M820 556 H972 V592 H820 Z" fill="#ffb92e"/>
  </g>
  <rect x="820" y="556" width="152" height="150" rx="34" fill="none"/>
  <path d="M820 592 Q896 612 972 578" fill="none" stroke-width="4"/>
  <!-- crooked oversized bowtie -->
  <g transform="rotate(-18 896 574)">
    <path d="M896 574 L852 552 Q842 574 852 596 Z" fill="#e11d48"/>
    <path d="M896 574 L940 552 Q950 574 940 596 Z" fill="#e11d48"/>
    <circle cx="896" cy="574" r="11" fill="#ffd23b"/>
  </g>
  <!-- arms both thrown up waving, motion arcs -->
  <path d="M824 586 Q764 556 756 492 L790 478 Q806 532 840 560 Z" fill="url(#metalYellow)"/>
  <path d="M968 584 Q1024 540 1016 472 L982 462 Q972 524 950 558 Z" fill="url(#metalYellow)"/>
  <g transform="translate(766 480)">
    <circle r="20" fill="#ffe9a8"/>
    <path d="M-14 -10 l-14 -14 M-4 -18 l-4 -19 M8 -18 l5 -18 M16 -8 l14 -12" fill="none" stroke-width="5"/>
  </g>
  <g transform="translate(1008 462)">
    <circle r="20" fill="#ffe9a8"/>
    <path d="M-14 -10 l-14 -14 M-4 -18 l-4 -19 M8 -18 l5 -18 M16 -8 l14 -12" fill="none" stroke-width="5"/>
  </g>
  <path d="M726 452 q-16 30 -4 62 M742 438 q-22 38 -8 78 M1046 430 q20 34 6 70 M1062 444 q14 30 2 58" fill="none" stroke="#fff" stroke-width="4" opacity="0.85"/>
  <!-- head -->
  <rect x="876" y="526" width="40" height="32" rx="7" fill="#ffd93b"/>
  <circle cx="896" cy="468" r="74" fill="url(#metalYellow)"/>
  <circle cx="896" cy="468" r="56" fill="#fff6d8"/>
  <!-- spring antenna with star, bent -->
  <path d="M950 420 q28 -18 20 -42 q16 6 22 -10" fill="none" stroke-width="5"/>
  <path d="M1000 348 l5 12 13 2 -10 8 3 13 -11 -7 -11 7 3 -13 -10 -8 13 -2Z" fill="#ff2e9a" stroke-width="3.5"/>
  <!-- propeller cap spinning -->
  <path d="M852 410 Q896 382 940 410 L930 424 H862 Z" fill="#2f6fd0"/>
  <path d="M896 394 V378" stroke-width="6"/>
  <ellipse cx="896" cy="372" rx="62" ry="12" fill="#ff2e9a" opacity="0.92"/>
  <ellipse cx="896" cy="372" rx="62" ry="12" fill="none"/>
  <ellipse cx="850" cy="372" rx="16" ry="9" fill="#ffd23b"/><ellipse cx="942" cy="372" rx="16" ry="9" fill="#7ef0e2"/>
  <path d="M820 352 q76 -22 152 0" fill="none" stroke="#fff" stroke-width="4" opacity="0.7" stroke-dasharray="8 8"/>
  <!-- face: huge uneven eyes staring at camera, open shouting mouth, missing tooth -->
  <circle cx="866" cy="458" r="19" fill="#fff"/>
  <circle cx="866" cy="458" r="10" fill="#191d30" stroke="none"/>
  <circle cx="870" cy="454" r="4" fill="#fff" stroke="none"/>
  <circle cx="928" cy="454" r="14" fill="#fff"/>
  <circle cx="928" cy="454" r="7" fill="#191d30" stroke="none"/>
  <path d="M920 442 l3 7 7 1 -6 4 2 7 -6 -4 -6 4 2 -7 -6 -4 7 -1Z" fill="#fff" stroke="none"/>
  <path d="M842 430 q22 -14 44 -4 M908 428 q20 -12 38 -2" fill="none" stroke-width="5"/>
  <ellipse cx="896" cy="498" rx="24" ry="20" fill="#7a1f2b"/>
  <ellipse cx="896" cy="506" rx="14" ry="9" fill="#ff6b8a" stroke="none"/>
  <path d="M876 484 H916 L912 496 H896" fill="#fff" stroke-width="3"/>
  <path d="M896 484 V496" stroke-width="3"/>
  <circle cx="846" cy="488" r="10" fill="#ff8fab" opacity="0.7" stroke="none"/>
  <circle cx="946" cy="488" r="10" fill="#ff8fab" opacity="0.7" stroke="none"/>
  <!-- mom hand corralling kid: gripping his shoulder from behind -->
  <path d="M798 556 Q812 568 824 576" fill="none" stroke="#ff9d86" stroke-width="15"/>
  <g transform="translate(826 580)">
    <ellipse rx="20" ry="14" fill="#ffe9a8" transform="rotate(-20)"/>
    <path d="M-12 0 v11 M-1 3 v12 M10 1 v10" fill="none" stroke-width="3.5"/>
  </g>
</g>

<!-- ================= DOG BOT : scratching ear mid-photo, sitting on teen foot ================= -->
<g stroke="#191d30" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
  <!-- tail spring wagging -->
  <path d="M452 726 q38 -28 30 -58" fill="none" stroke="#9aa6c2" stroke-width="9"/>
  <path d="M452 726 q38 -28 30 -58" fill="none" stroke-width="4.5"/>
  <circle cx="482" cy="662" r="11" fill="#e11d48"/>
  <path d="M500 642 q18 14 14 36 M512 628 q24 20 18 50" fill="none" stroke="#fff" stroke-width="4" opacity="0.85"/>
  <!-- body -->
  <rect x="288" y="706" width="168" height="92" rx="44" fill="#c8d2e8"/>
  <g clip-path="url(#dogBodyClip)">
    <rect x="314" y="706" width="116" height="92" fill="url(#argyle)"/>
  </g>
  <rect x="288" y="706" width="168" height="92" rx="44" fill="none"/>
  <circle cx="430" cy="730" r="8" fill="#ffd23b"/>
  <!-- legs: front planted, hind raised scratching ear -->
  <path d="M306 788 L302 826 L334 828 L340 792 Z" fill="#9aa6c2"/>
  <path d="M356 792 L356 826 L386 826 L392 790 Z" fill="#9aa6c2"/>
  <ellipse cx="316" cy="830" rx="20" ry="10" fill="#191d30"/>
  <ellipse cx="372" cy="830" rx="20" ry="10" fill="#191d30"/>
  <path d="M414 786 L444 810 L434 832 L398 808 Z" fill="#9aa6c2"/>
  <ellipse cx="440" cy="824" rx="18" ry="10" fill="#191d30" transform="rotate(24 440 824)"/>
  <!-- scratching hind leg up by head -->
  <path d="M398 716 Q362 672 322 668 L314 694 Q350 702 376 734 Z" fill="#9aa6c2"/>
  <ellipse cx="314" cy="680" rx="17" ry="11" fill="#191d30" transform="rotate(-32 314 680)"/>
  <path d="M292 652 l-8 -12 M306 644 l-2 -15 M320 646 l6 -14" fill="none" stroke="#ffd23b" stroke-width="4"/>
  <!-- head turned up toward teen, not camera -->
  <g transform="rotate(-14 292 690)">
    <rect x="228" y="634" width="118" height="92" rx="28" fill="#e8ecf5"/>
    <path d="M228 684 H292 L286 722 H242 Q228 704 228 684Z" fill="#c8d2e8"/>
    <ellipse cx="238" cy="690" rx="14" ry="11" fill="#e11d48"/>
    <circle cx="234" cy="686" r="4" fill="#fff" stroke="none"/>
    <!-- ears one up one flopped -->
    <path d="M316 638 L344 594 L362 640 Z" fill="#9aa6c2"/>
    <path d="M256 640 L232 600 L268 630 Z" fill="#5a6478" transform="rotate(28 252 622)"/>
    <!-- eyes looking up -->
    <circle cx="272" cy="666" r="11" fill="#fff"/>
    <circle cx="274" cy="660" r="6" fill="#191d30" stroke="none"/>
    <circle cx="310" cy="664" r="9" fill="#fff"/>
    <circle cx="312" cy="659" r="5" fill="#191d30" stroke="none"/>
    <!-- tongue hanging sideways -->
    <path d="M254 710 Q246 734 264 740 Q278 730 272 708 Z" fill="#ff6b8a"/>
    <path d="M262 714 V732" stroke="#d94a6a" stroke-width="3" fill="none"/>
  </g>
  <!-- collar + round tag (blank) -->
  <path d="M332 700 Q306 724 286 706" fill="none" stroke="#e11d48" stroke-width="11"/>
  <circle cx="310" cy="722" r="11" fill="#ffd23b"/>
  <circle cx="310" cy="722" r="4" fill="#fff" stroke-width="2.5"/>
</g>

<!-- ================= TANGLED FAMILY CABLES : literal bonds on the floor ================= -->
<g fill="none" stroke-linecap="round">
  <path d="M210 740 Q300 790 410 756 Q500 728 600 770 Q700 810 800 764 Q880 730 960 768" stroke="#ff2e9a" stroke-width="8"/>
  <path d="M210 740 Q300 790 410 756 Q500 728 600 770 Q700 810 800 764 Q880 730 960 768" stroke="#191d30" stroke-width="2.2" stroke-dasharray="2 14" opacity="0.55"/>
  <path d="M436 756 Q470 800 560 788 Q650 776 690 820 Q740 850 830 812" stroke="#00c2e8" stroke-width="7"/>
  <path d="M180 768 Q280 830 430 812 Q560 798 640 836" stroke="#ffd23b" stroke-width="6"/>
  <path d="M600 788 Q630 760 670 786 Q700 806 670 828 Q640 844 620 820" stroke="#8b5cf6" stroke-width="6"/>
  <!-- loop around dad ankle -->
  <ellipse cx="402" cy="748" rx="34" ry="12" stroke="#ff2e9a" stroke-width="7"/>
  <!-- plug trailing off right toward column -->
  <path d="M960 768 Q1020 786 1064 766" stroke="#ff2e9a" stroke-width="7"/>
</g>
<g stroke="#191d30" stroke-width="4" stroke-linejoin="round">
  <rect x="1062" y="748" width="30" height="24" rx="6" fill="#ffd23b" transform="rotate(-18 1077 760)"/>
  <path d="M1090 754 l16 -8 M1092 766 l17 -2" fill="none" stroke-width="4"/>
  <!-- loose plug by teen foot, disconnected teen -->
  <rect x="150" y="756" width="26" height="20" rx="5" fill="#9aa6c2" transform="rotate(24 163 766)"/>
  <path d="M142 752 l-14 -10 M148 764 l-16 -4" fill="none" stroke-width="3.5"/>
  <path d="M120 732 l6 10 10 1 -8 6 2 10 -9 -5 -8 5 2 -10 -8 -6 10 -1Z" fill="#ffe94a" stroke-width="3"/>
  <!-- wall outlet far right floor -->
  <rect x="1120" y="762" width="44" height="56" rx="9" fill="#e8ecf5"/>
  <circle cx="1142" cy="782" r="6" fill="#191d30" stroke="none"/>
  <circle cx="1142" cy="802" r="6" fill="#191d30" stroke="none"/>
</g>

<!-- harsh flash vignette + foreground soft top light -->
<ellipse cx="600" cy="450" rx="610" ry="460" fill="none" stroke="#0d0a24" stroke-width="70" opacity="0.28" filter="url(#soft)"/>
<path d="M0 0 H1200 V46 Q600 86 0 46 Z" fill="#ffffff" opacity="0.08"/>
<!-- subtle photo border like printed portrait -->
<rect x="18" y="18" width="1164" height="864" rx="18" fill="none" stroke="#ffffff" stroke-width="8" opacity="0.92"/>
<rect x="30" y="30" width="1140" height="840" rx="12" fill="none" stroke="#191d30" stroke-width="3" opacity="0.55"/>
</svg>
'''

def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(SVG, encoding="utf-8")
    # Guard: the brief says no text. Fail loudly if visible text slips in.
    assert "<text" not in SVG.lower(), "SVG must contain no <text> elements"
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
