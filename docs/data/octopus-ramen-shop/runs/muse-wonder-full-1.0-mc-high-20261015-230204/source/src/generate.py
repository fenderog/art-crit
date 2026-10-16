#!/usr/bin/env python3
"""Generate an SVG illustration: octopus chef at a ramen booth (yatai)."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "output" / "octopus-ramen-chef.svg"

svg = r'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900" role="img" aria-labelledby="title desc">
<title id="title">Octopus chef at a ramen booth</title>
<desc id="desc">A cheerful octopus wearing a chef hat multitasks with all eight arms at a warmly lit Japanese ramen yatai stall at night.</desc>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#141b38"/><stop offset="0.45" stop-color="#2e2348"/>
    <stop offset="0.75" stop-color="#5c2f4a"/><stop offset="1" stop-color="#7a3a3f"/>
  </linearGradient>
  <radialGradient id="glow" cx="50%" cy="42%" r="55%">
    <stop offset="0" stop-color="#ffd98a" stop-opacity="0.55"/><stop offset="0.5" stop-color="#ffb36b" stop-opacity="0.22"/><stop offset="1" stop-color="#ffb36b" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="lanternGlow" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="#ffe9a8" stop-opacity="0.9"/><stop offset="1" stop-color="#ff9a3d" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="interior" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#5a2f22"/><stop offset="0.35" stop-color="#7a3b26"/><stop offset="1" stop-color="#3d2018"/>
  </linearGradient>
  <linearGradient id="woodTop" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#b07a4a"/><stop offset="0.5" stop-color="#8a5a33"/><stop offset="1" stop-color="#6e4526"/>
  </linearGradient>
  <linearGradient id="woodFront" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#7c4f2c"/><stop offset="1" stop-color="#4d2e18"/>
  </linearGradient>
  <linearGradient id="roof" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#c94a3a"/><stop offset="0.55" stop-color="#a9322b"/><stop offset="1" stop-color="#7d211d"/>
  </linearGradient>
  <linearGradient id="roofStripe" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#e8dcc3"/><stop offset="1" stop-color="#d8c9a8"/>
  </linearGradient>
  <radialGradient id="octo" cx="42%" cy="32%" r="75%">
    <stop offset="0" stop-color="#ffb3a0"/><stop offset="0.35" stop-color="#ff8a7a"/>
    <stop offset="0.7" stop-color="#ef6461"/><stop offset="1" stop-color="#cf4453"/>
  </radialGradient>
  <radialGradient id="octoBelly" cx="50%" cy="45%" r="55%">
    <stop offset="0" stop-color="#ffd0b8" stop-opacity="0.85"/><stop offset="1" stop-color="#ffd0b8" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="hat" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.7" stop-color="#f3ead9"/><stop offset="1" stop-color="#ded2b8"/>
  </linearGradient>
  <radialGradient id="broth" cx="45%" cy="40%" r="65%">
    <stop offset="0" stop-color="#ffd27a"/><stop offset="0.55" stop-color="#f4a742"/><stop offset="1" stop-color="#d97a2b"/>
  </radialGradient>
  <radialGradient id="potBroth" cx="50%" cy="45%" r="60%">
    <stop offset="0" stop-color="#ffe08f"/><stop offset="0.6" stop-color="#f2ae4e"/><stop offset="1" stop-color="#cf7a28"/>
  </radialGradient>
  <linearGradient id="pot" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#5a5f6e"/><stop offset="0.25" stop-color="#2f333f"/><stop offset="1" stop-color="#171a22"/>
  </linearGradient>
  <linearGradient id="lantern" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff0b3"/><stop offset="0.45" stop-color="#ffcf6e"/><stop offset="1" stop-color="#ff9e4f"/>
  </linearGradient>
  <linearGradient id="noren" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#d6463a"/><stop offset="1" stop-color="#a92c28"/>
  </linearGradient>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="soft2" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.2"/></filter>
  <!-- reusable ramen bowl toppings cluster -->
  <g id="naruto">
    <circle r="11" fill="#fff7ee" stroke="#e8b4b8" stroke-width="1.5"/>
    <path d="M0,-6 a6,6 0 1,1 -6,6 a4,4 0 1,0 4,-4 a2.2,2.2 0 1,1 -2,2" fill="none" stroke="#f27a9a" stroke-width="2" stroke-linecap="round"/>
  </g>
  <g id="eggHalf">
    <ellipse rx="16" ry="12" fill="#fffaf0" stroke="#e8d9b8" stroke-width="1.2"/>
    <ellipse rx="8.5" ry="6.5" fill="#ffb52e"/><ellipse cx="-2" cy="-2" rx="3" ry="2" fill="#ffd06b"/>
  </g>
  <g id="scallions">
    <g fill="#3fae4a"><circle cx="-8" cy="0" r="3.2"/><circle cx="0" cy="-3" r="3.2"/><circle cx="8" cy="0" r="3.2"/><circle cx="-4" cy="4" r="2.8"/><circle cx="5" cy="4" r="2.8"/></g>
    <g fill="#8ad67a"><circle cx="-8" cy="-1" r="1.4"/><circle cx="0" cy="-4" r="1.4"/><circle cx="8" cy="-1" r="1.4"/></g>
  </g>
</defs>

<!-- ===== BACKGROUND ===== -->
<rect width="1200" height="900" fill="url(#sky)"/>
<!-- stars -->
<g fill="#fff6d8">
  <circle cx="70" cy="60" r="2.2"/><circle cx="180" cy="38" r="1.6"/><circle cx="300" cy="70" r="2"/><circle cx="430" cy="34" r="1.5"/>
  <circle cx="760" cy="42" r="1.8"/><circle cx="900" cy="66" r="2.2"/><circle cx="1030" cy="36" r="1.6"/><circle cx="1120" cy="88" r="2"/>
  <circle cx="120" cy="130" r="1.4" opacity="0.7"/><circle cx="980" cy="120" r="1.4" opacity="0.7"/><circle cx="560" cy="52" r="1.4" opacity="0.8"/>
  <path d="M240 96 l2.5 6 6 2.5 -6 2.5 -2.5 6 -2.5 -6 -6 -2.5 6 -2.5z" opacity="0.9"/>
  <path d="M1048 150 l2 5 5 2 -5 2 -2 5 -2 -5 -5 -2 5 -2z" opacity="0.85"/>
</g>
<!-- moon -->
<g><circle cx="1082" cy="78" r="34" fill="#fff3c4"/><circle cx="1082" cy="78" r="46" fill="#fff3c4" opacity="0.16"/>
<circle cx="1070" cy="68" r="6" fill="#f2dd9a" opacity="0.7"/><circle cx="1094" cy="88" r="4.5" fill="#f2dd9a" opacity="0.6"/><circle cx="1090" cy="64" r="3" fill="#f2dd9a" opacity="0.6"/></g>
<!-- distant rooftops -->
<g fill="#1c1833" opacity="0.9">
  <path d="M0 300 L70 262 L150 300 L150 380 L0 380z"/><path d="M980 290 L1070 246 L1200 298 L1200 380 L980 380z"/>
  <rect x="18" y="310" width="22" height="28" fill="#ffca7a" opacity="0.75"/><rect x="1040" y="308" width="24" height="30" fill="#ffca7a" opacity="0.7"/>
  <rect x="1100" y="322" width="18" height="22" fill="#ffdf9a" opacity="0.6"/>
</g>
<ellipse cx="600" cy="430" rx="560" ry="380" fill="url(#glow)"/>
<!-- ground -->
<rect x="0" y="768" width="1200" height="132" fill="#22182b"/>
<ellipse cx="600" cy="798" rx="520" ry="34" fill="#ffb36b" opacity="0.13"/>
<g stroke="#3a2a42" stroke-width="2" opacity="0.8"><path d="M40 830 H1160"/><path d="M120 862 H1080"/><path d="M260 800 v28 M520 800 v28 M760 800 v28 M980 800 v28"/></g>

<!-- string lights -->
<g fill="none" stroke="#0f1226" stroke-width="2.5"><path d="M-10 118 Q 300 188 600 132 T 1210 118"/><path d="M-10 70 Q 320 128 660 82 T 1210 66" opacity="0.7"/></g>
<g>
  <g fill="#ffd98a"><circle cx="90" cy="134" r="7"/><circle cx="220" cy="150" r="7"/><circle cx="360" cy="154" r="7"/><circle cx="500" cy="143" r="7"/><circle cx="650" cy="142" r="7"/><circle cx="800" cy="146" r="7"/><circle cx="940" cy="140" r="7"/><circle cx="1080" cy="128" r="7"/></g>
  <g fill="#ffedbb"><circle cx="90" cy="132" r="3"/><circle cx="220" cy="148" r="3"/><circle cx="360" cy="152" r="3"/><circle cx="500" cy="141" r="3"/><circle cx="650" cy="140" r="3"/><circle cx="800" cy="144" r="3"/><circle cx="940" cy="138" r="3"/><circle cx="1080" cy="126" r="3"/></g>
  <g fill="#ffb36b" opacity="0.35"><circle cx="90" cy="134" r="16"/><circle cx="360" cy="154" r="16"/><circle cx="650" cy="142" r="16"/><circle cx="940" cy="140" r="16"/><circle cx="1080" cy="128" r="16"/></g>
</g>

<!-- ===== BOOTH STRUCTURE ===== -->
<!-- interior back wall -->
<rect x="168" y="238" width="864" height="392" rx="6" fill="url(#interior)"/>
<!-- interior shelves -->
<g>
  <rect x="196" y="302" width="200" height="10" rx="3" fill="#4a2a18"/><rect x="804" y="302" width="200" height="10" rx="3" fill="#4a2a18"/>
  <rect x="196" y="392" width="150" height="9" rx="3" fill="#4a2a18" opacity="0.9"/>
  <!-- jars & bottles left -->
  <g><rect x="214" y="266" width="26" height="36" rx="6" fill="#c96a3a"/><rect x="218" y="258" width="18" height="10" rx="3" fill="#8a3b2e"/>
  <rect x="250" y="270" width="22" height="32" rx="5" fill="#7fb069"/><rect x="285" y="262" width="28" height="40" rx="6" fill="#e8c46a"/>
  <rect x="322" y="272" width="20" height="30" rx="5" fill="#b85450"/><rect x="352" y="268" width="24" height="34" rx="5" fill="#8ecae6" opacity="0.9"/></g>
  <!-- stacked bowls right shelf -->
  <g fill="#f6efe0" stroke="#375a8a" stroke-width="2">
    <path d="M826 302 a30 14 0 0 0 60 0z"/><path d="M826 288 a30 14 0 0 0 60 0z"/><path d="M826 274 a30 14 0 0 0 60 0z"/>
    <path d="M906 302 a30 14 0 0 0 60 0z"/><path d="M906 288 a30 14 0 0 0 60 0z"/>
  </g>
  <g stroke="#375a8a" stroke-width="1.6" fill="none" opacity="0.8"><path d="M830 296 h52 M910 296 h52"/></g>
  <!-- hanging utensils right -->
  <g stroke="#d9c9a8" stroke-width="3" stroke-linecap="round"><path d="M970 316 v34"/><path d="M990 316 v28"/></g>
  <ellipse cx="970" cy="358" rx="10" ry="7" fill="#c9ced6"/><rect x="984" y="344" width="13" height="18" rx="3" fill="#c9ced6"/>
  <!-- left shelf bowls/eggs -->
  <g><ellipse cx="236" cy="388" rx="34" ry="10" fill="#6b4426"/><g fill="#fff6e6"><ellipse cx="220" cy="382" rx="9" ry="11"/><ellipse cx="238" cy="380" rx="9" ry="11"/><ellipse cx="254" cy="383" rx="9" ry="11"/></g>
  <g fill="#7ec850"><ellipse cx="306" cy="386" rx="22" ry="9"/><path d="M292 382 q14 -14 28 0" fill="none" stroke="#4a9e3f" stroke-width="3" stroke-linecap="round"/></g></g>
</g>
<!-- side posts -->
<g><rect x="152" y="210" width="26" height="570" rx="6" fill="#5d3820"/><rect x="1022" y="210" width="26" height="570" rx="6" fill="#5d3820"/>
<rect x="158" y="210" width="6" height="570" fill="#8a5a33" opacity="0.6"/><rect x="1028" y="210" width="6" height="570" fill="#8a5a33" opacity="0.6"/></g>

<!-- roof -->
<g>
  <path d="M92 238 L168 150 H1032 L1108 238 L1048 238 L1006 192 H194 L152 238z" fill="#3a1f16" opacity="0.35" transform="translate(0 10)"/>
  <path d="M92 238 L168 150 H1032 L1108 238 L1042 238 L1002 190 H198 L158 238z" fill="url(#roof)"/>
  <!-- roof stripes (canvas awning) -->
  <g opacity="0.92">
    <path d="M278 150 L258 190 H198 L158 238 H92 L168 150z" fill="url(#roofStripe)" opacity="0.0"/>
    <path d="M330 150 L300 238 H236 L282 150z" fill="#efe3c8" opacity="0.28"/><path d="M520 150 L500 238 H436 L472 150z" fill="#efe3c8" opacity="0.28"/>
    <path d="M710 150 L700 238 H636 L662 150z" fill="#efe3c8" opacity="0.28"/><path d="M900 150 L900 238 H836 L852 150z" fill="#efe3c8" opacity="0.28"/>
  </g>
  <!-- scalloped awning edge -->
  <g fill="#8e2620"><path d="M92 238 h1016 v10 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0 q-24 22 -48 0z"/></g>
  <g fill="#efe3c8" opacity="0.9"><circle cx="140" cy="250" r="3"/><circle cx="236" cy="250" r="3"/><circle cx="332" cy="250" r="3"/><circle cx="428" cy="250" r="3"/><circle cx="524" cy="250" r="3"/><circle cx="620" cy="250" r="3"/><circle cx="716" cy="250" r="3"/><circle cx="812" cy="250" r="3"/><circle cx="908" cy="250" r="3"/><circle cx="1004" cy="250" r="3"/><circle cx="1084" cy="248" r="3"/></g>
</g>

<!-- main sign -->
<g transform="translate(0 -34)">
  <rect x="368" y="86" width="464" height="92" rx="16" fill="#2e1a12"/>
  <rect x="376" y="94" width="448" height="76" rx="11" fill="#fdf3d8"/>
  <rect x="376" y="94" width="448" height="76" rx="11" fill="none" stroke="#c94a3a" stroke-width="3"/>
  <!-- tiny octopus icon on sign -->
  <g transform="translate(432 132)"><path d="M-22 14 C-26 -12 -12 -26 0 -26 C12 -26 26 -12 22 14 C16 8 12 18 6 12 C2 19 -4 19 -7 12 C-13 18 -17 8 -22 14z" fill="#ef6461"/>
  <circle cx="-7" cy="-6" r="3.2" fill="#2b1a1a"/><circle cx="8" cy="-6" r="3.2" fill="#2b1a1a"/><path d="M-4 3 Q1 7 6 3" fill="none" stroke="#2b1a1a" stroke-width="2" stroke-linecap="round"/>
  <path d="M-14 -24 q14 -12 28 0 l-3 8 h-22z" fill="#fff" stroke="#ddd2b8" stroke-width="1.5"/></g>
  <text x="468" y="126" font-family="Georgia, 'Times New Roman', serif" font-size="34" font-weight="700" letter-spacing="3" fill="#8e2620">TAKO RAMEN</text>
  <text x="470" y="154" font-family="'Hiragino Sans','Noto Sans CJK JP',sans-serif" font-size="19" letter-spacing="6" fill="#5d3820">たこ ・ らーめん ・ 屋台</text>
  <circle cx="392" cy="110" r="4" fill="#8a5a33"/><circle cx="808" cy="110" r="4" fill="#8a5a33"/><circle cx="392" cy="154" r="4" fill="#8a5a33"/><circle cx="808" cy="154" r="4" fill="#8a5a33"/>
</g>

<!-- noren curtains -->
<g font-family="'Hiragino Sans','Noto Sans CJK JP',sans-serif" font-weight="700">
  <g><rect x="188" y="262" width="150" height="92" rx="4" fill="url(#noren)"/><rect x="348" y="262" width="150" height="92" rx="4" fill="url(#noren)"/>
  <rect x="702" y="262" width="150" height="92" rx="4" fill="url(#noren)"/><rect x="862" y="262" width="150" height="92" rx="4" fill="url(#noren)"/></g>
  <g fill="none" stroke="#7d211d" stroke-width="2" opacity="0.6"><path d="M228 262 v92 M298 262 v92 M388 262 v92 M458 262 v92 M742 262 v92 M812 262 v92 M902 262 v92 M972 262 v92"/></g>
  <g fill="#fff6e6"><circle cx="263" cy="302" r="24" fill="none" stroke="#fff6e6" stroke-width="2.5"/><circle cx="423" cy="302" r="24" fill="none" stroke="#fff6e6" stroke-width="2.5"/>
  <circle cx="777" cy="302" r="24" fill="none" stroke="#fff6e6" stroke-width="2.5"/><circle cx="937" cy="302" r="24" fill="none" stroke="#fff6e6" stroke-width="2.5"/>
  <text x="263" y="314" text-anchor="middle" font-size="30">た</text><text x="423" y="314" text-anchor="middle" font-size="30">こ</text>
  <text x="777" y="314" text-anchor="middle" font-size="28">麺</text><text x="937" y="314" text-anchor="middle" font-size="28">魂</text></g>
  <rect x="180" y="256" width="840" height="9" rx="4" fill="#3a2415"/>
</g>

<!-- lanterns -->
<g>
  <circle cx="132" cy="356" r="86" fill="url(#lanternGlow)"/><circle cx="1068" cy="356" r="86" fill="url(#lanternGlow)"/>
  <g stroke="#2e1a12" stroke-width="3"><path d="M132 246 v42"/><path d="M1068 246 v42"/></g>
  <g><rect x="114" y="286" width="36" height="12" rx="4" fill="#2e1a12"/><ellipse cx="132" cy="356" rx="46" ry="60" fill="url(#lantern)"/>
  <g fill="none" stroke="#e08a3a" stroke-width="2" opacity="0.8"><path d="M88 330 q44 14 88 0 M86 356 h92 M88 382 q44 -14 88 0 M132 298 v116"/></g>
  <rect x="114" y="412" width="36" height="12" rx="4" fill="#2e1a12"/><path d="M132 424 v18" stroke="#c94a3a" stroke-width="4" stroke-linecap="round"/>
  <text x="132" y="370" text-anchor="middle" font-family="'Hiragino Sans','Noto Sans CJK JP',sans-serif" font-size="30" font-weight="700" fill="#8e2620">麺</text></g>
  <g><rect x="1050" y="286" width="36" height="12" rx="4" fill="#2e1a12"/><ellipse cx="1068" cy="356" rx="46" ry="60" fill="url(#lantern)"/>
  <g fill="none" stroke="#e08a3a" stroke-width="2" opacity="0.8"><path d="M1024 330 q44 14 88 0 M1022 356 h92 M1024 382 q44 -14 88 0 M1068 298 v116"/></g>
  <rect x="1050" y="412" width="36" height="12" rx="4" fill="#2e1a12"/><path d="M1068 424 v18" stroke="#c94a3a" stroke-width="4" stroke-linecap="round"/>
  <text x="1068" y="368" text-anchor="middle" font-family="'Hiragino Sans','Noto Sans CJK JP',sans-serif" font-size="22" font-weight="700" fill="#8e2620">らーめん</text></g>
</g>

<!-- ===== OCTOPUS (behind counter) ===== -->
<g>
  <!-- shadow behind head -->
  <ellipse cx="602" cy="452" rx="168" ry="150" fill="#1d0f0c" opacity="0.35" filter="url(#soft)"/>
  <!-- rear curled tentacles peeking at sides of head -->
  <g fill="none" stroke-linecap="round">
    <path d="M478 470 C420 460 392 420 404 382" stroke="#a83a48" stroke-width="40"/>
    <path d="M478 470 C420 460 392 420 404 382" stroke="#e85d62" stroke-width="30"/>
    <path d="M724 470 C780 458 808 422 798 384" stroke="#a83a48" stroke-width="40"/>
    <path d="M724 470 C780 458 808 422 798 384" stroke="#e85d62" stroke-width="30"/>
  </g>
  <g fill="#ffd9c9" opacity="0.9"><circle cx="410" cy="408" r="5"/><circle cx="422" cy="438" r="5"/><circle cx="792" cy="410" r="5"/><circle cx="780" cy="440" r="5"/></g>

  <!-- head / mantle -->
  <path d="M600 252 C690 252 748 322 752 426 C754 482 738 532 706 552 C688 536 678 560 658 544 C644 564 622 552 600 556 C578 552 556 564 542 544 C522 560 512 536 494 552 C462 532 446 482 448 426 C452 322 510 252 600 252z" fill="url(#octo)"/>
  <path d="M600 252 C690 252 748 322 752 426 C754 482 738 532 706 552 C688 536 678 560 658 544 C644 564 622 552 600 556 C578 552 556 564 542 544 C522 560 512 536 494 552 C462 532 446 482 448 426 C452 322 510 252 600 252z" fill="url(#octoBelly)" opacity="0.55"/>
  <!-- head spots / freckles -->
  <g fill="#d94f5c" opacity="0.55"><circle cx="502" cy="340" r="7"/><circle cx="484" cy="376" r="5"/><circle cx="698" cy="338" r="7"/><circle cx="716" cy="374" r="5"/><circle cx="520" cy="306" r="4.5"/><circle cx="682" cy="304" r="4.5"/></g>
  <ellipse cx="540" cy="302" rx="52" ry="26" fill="#fff" opacity="0.28" transform="rotate(-18 540 302)"/>

  <!-- chef hat (tilted) -->
  <g transform="rotate(-7 600 258)">
    <path d="M508 262 C470 236 474 188 512 172 C522 138 562 122 600 134 C638 122 678 138 688 172 C726 188 730 236 692 262 C660 276 540 276 508 262z" fill="url(#hat)"/>
    <g fill="none" stroke="#ddd2b8" stroke-width="3" stroke-linecap="round" opacity="0.9"><path d="M540 238 C534 210 540 184 556 166"/><path d="M600 246 C598 214 600 182 606 156"/><path d="M660 238 C666 210 660 184 644 166"/></g>
    <rect x="504" y="252" width="192" height="34" rx="12" fill="#fdf8ec" stroke="#ded2b8" stroke-width="2.5"/>
    <circle cx="600" cy="269" r="11" fill="#c94a3a"/><text x="600" y="275" text-anchor="middle" font-family="'Hiragino Sans','Noto Sans CJK JP',sans-serif" font-size="13" font-weight="700" fill="#fff">た</text>
  </g>

  <!-- hachimaki knot peeking under hat side -->
  <path d="M702 292 q36 6 44 30 q-22 4 -34 -10z" fill="#375a8a"/><path d="M706 300 q28 16 24 36 q-20 -4 -26 -22z" fill="#2c4a74"/>

  <!-- face -->
  <g>
    <!-- eyes: big, happy, looking toward noodles on right -->
    <ellipse cx="548" cy="386" rx="21" ry="25" fill="#fff"/><ellipse cx="652" cy="386" rx="21" ry="25" fill="#fff"/>
    <circle cx="556" cy="390" r="12.5" fill="#2b1a1a"/><circle cx="660" cy="390" r="12.5" fill="#2b1a1a"/>
    <circle cx="560" cy="385" r="4.5" fill="#fff"/><circle cx="664" cy="385" r="4.5" fill="#fff"/>
    <circle cx="551" cy="396" r="2.2" fill="#fff" opacity="0.9"/><circle cx="655" cy="396" r="2.2" fill="#fff" opacity="0.9"/>
    <!-- brows -->
    <path d="M526 352 Q548 340 570 352" fill="none" stroke="#8e2f3d" stroke-width="5" stroke-linecap="round"/>
    <path d="M630 352 Q652 340 674 352" fill="none" stroke="#8e2f3d" stroke-width="5" stroke-linecap="round"/>
    <!-- mouth: open smile (octopus 'o' turned grin) -->
    <path d="M572 438 Q600 470 628 438 Q622 474 600 476 Q578 474 572 438z" fill="#7a2230"/>
    <path d="M584 458 Q600 470 616 458 Q610 472 600 472 Q590 472 584 458z" fill="#ff8a9a"/>
    <path d="M572 438 Q600 458 628 438" fill="none" stroke="#8e2f3d" stroke-width="4" stroke-linecap="round"/>
    <!-- blush -->
    <ellipse cx="502" cy="430" rx="26" ry="14" fill="#ff6b7d" opacity="0.55"/><ellipse cx="698" cy="430" rx="26" ry="14" fill="#ff6b7d" opacity="0.55"/>
    <g stroke="#e04a5e" stroke-width="2.4" stroke-linecap="round" opacity="0.7"><path d="M492 424 l10 8 M502 422 l9 9"/><path d="M690 422 l9 9 M700 424 l9 8"/></g>
  </g>

  <!-- neckerchief -->
  <g><path d="M540 518 Q600 548 660 518 L646 552 Q600 574 554 552z" fill="#375a8a"/>
  <path d="M600 540 L584 586 Q600 598 616 586z" fill="#2c4a74"/><circle cx="600" cy="542" r="9" fill="#e8c46a" stroke="#b8912e" stroke-width="2"/></g>
</g>

<!-- ===== COUNTER BACK EDGE (octopus emerges behind it) ===== -->
<rect x="158" y="548" width="884" height="18" rx="4" fill="#4a2c18"/>

<!-- ===== STOCK POT (left, behind front tentacles) ===== -->
<g>
  <ellipse cx="322" cy="618" rx="118" ry="16" fill="#000" opacity="0.35" filter="url(#soft2)"/>
  <path d="M232 510 h180 v58 a90 44 0 0 1 -180 0z" fill="url(#pot)"/>
  <ellipse cx="322" cy="510" rx="90" ry="22" fill="#3c414f"/><ellipse cx="322" cy="508" rx="80" ry="18" fill="url(#potBroth)"/>
  <g fill="#ffe9a8" opacity="0.85"><circle cx="292" cy="504" r="5"/><circle cx="330" cy="512" r="4"/><circle cx="356" cy="503" r="5"/><circle cx="312" cy="515" r="3.2"/></g>
  <g fill="#3fae4a"><circle cx="302" cy="510" r="3"/><circle cx="342" cy="506" r="3"/></g>
  <rect x="226" y="528" width="192" height="10" rx="5" fill="#14161d" opacity="0.7"/>
  <g fill="none" stroke="#14161d" stroke-width="7" stroke-linecap="round"><path d="M232 536 q-24 4 -22 22"/><path d="M412 536 q24 4 22 22"/></g>
  <!-- flame under pot hint (on burner behind counter top) -->
  <g opacity="0.9"><path d="M298 618 q10 -18 20 0 q-10 8 -20 0" fill="#ff8a3d"/><path d="M326 618 q8 -14 16 0 q-8 6 -16 0" fill="#ffb52e"/></g>
</g>

<!-- noodle strainer basket middle-left -->
<g><ellipse cx="452" cy="588" rx="52" ry="14" fill="#c9ced6"/><path d="M404 588 a48 26 0 0 0 96 0z" fill="#9aa1ad"/>
<g stroke="#6e7582" stroke-width="1.6"><path d="M416 592 v14 M436 596 v16 M456 596 v16 M476 592 v14"/></g>
<g fill="none" stroke="#ffe1a0" stroke-width="4" stroke-linecap="round"><path d="M418 584 q18 -10 38 0 q18 -8 34 2"/><path d="M424 590 q26 -8 52 0"/></g></g>

<!-- ===== TENTACLES IN ACTION (over counter) ===== -->
<!-- helper style: dark underlay + main -->
<g fill="none" stroke-linecap="round">
  <!-- A: far-left arm holding ladle over pot -->
  <path d="M510 540 C430 560 372 540 348 486" stroke="#a83a48" stroke-width="42"/>
  <path d="M510 540 C430 560 372 540 348 486" stroke="#f06a68" stroke-width="31"/>
  <!-- B: left-mid arm holding bowl (ends under centre bowl) -->
  <path d="M540 556 C500 600 520 640 566 652" stroke="#a83a48" stroke-width="42"/>
  <path d="M540 556 C500 600 520 640 566 652" stroke="#f06a68" stroke-width="31"/>
  <!-- C: right-mid arm sprinkling scallions over centre bowl -->
  <path d="M652 556 C694 578 692 592 664 596" stroke="#a83a48" stroke-width="40"/>
  <path d="M652 556 C694 578 692 592 664 596" stroke="#f06a68" stroke-width="30"/>
  <!-- D: far-right arm lifting noodles high -->
  <path d="M686 540 C780 548 848 508 862 434" stroke="#a83a48" stroke-width="42"/>
  <path d="M686 540 C780 548 848 508 862 434" stroke="#f06a68" stroke-width="31"/>
  <!-- E: extra arm waving / holding nori at far right edge -->
  <path d="M706 520 C800 500 886 528 914 586" stroke="#a83a48" stroke-width="38"/>
  <path d="M706 520 C800 500 886 528 914 586" stroke="#ef6461" stroke-width="28"/>
  <!-- F: extra arm on left resting, holding towel -->
  <path d="M500 524 C420 512 356 542 330 596" stroke="#a83a48" stroke-width="38"/>
  <path d="M500 524 C420 512 356 542 330 596" stroke="#ef6461" stroke-width="28"/>
</g>
<!-- suckers -->
<g fill="#ffd9c9">
  <circle cx="438" cy="552" r="5.5"/><circle cx="398" cy="540" r="5"/><circle cx="368" cy="514" r="4.6"/>
  <circle cx="522" cy="600" r="5.5"/><circle cx="538" cy="632" r="5"/>
  <circle cx="686" cy="600" r="5.5"/><circle cx="680" cy="628" r="4.8"/>
  <circle cx="770" cy="540" r="5.5"/><circle cx="822" cy="512" r="5"/><circle cx="850" cy="476" r="4.6"/>
  <circle cx="806" cy="516" r="5"/><circle cx="868" cy="540" r="4.8"/>
  <circle cx="410" cy="526" r="5"/><circle cx="362" cy="562" r="4.8"/>
</g>
<g fill="#ffb3a0"><circle cx="438" cy="552" r="2.4"/><circle cx="398" cy="540" r="2.2"/><circle cx="770" cy="540" r="2.4"/><circle cx="822" cy="512" r="2.2"/><circle cx="522" cy="600" r="2.4"/><circle cx="686" cy="600" r="2.4"/></g>

<!-- ladle in tentacle A -->
<g transform="rotate(-18 348 470)">
  <rect x="342" y="404" width="11" height="76" rx="5" fill="#8a5a33"/>
  <ellipse cx="348" cy="486" rx="24" ry="15" fill="#d7dce4"/><ellipse cx="348" cy="483" rx="18" ry="10" fill="url(#potBroth)"/>
</g>
<!-- broth drip from ladle -->
<path d="M360 502 q5 12 0 20 q-5 -8 0 -20" fill="#f2ae4e"/>

<!-- towel in tentacle F -->
<g transform="rotate(10 330 606)"><rect x="304" y="592" width="54" height="34" rx="6" fill="#f6efe0"/>
<path d="M304 604 h54 M304 614 h54" stroke="#7fb3d9" stroke-width="3"/></g>

<!-- chopsticks + lifted noodles (tentacle D) -->
<g>
  <g stroke="#5d3820" stroke-width="6" stroke-linecap="round"><path d="M862 434 L908 356"/><path d="M876 442 L930 372"/></g>
  <g fill="none" stroke="#ffe1a0" stroke-width="5" stroke-linecap="round">
    <path d="M864 436 C856 486 872 520 860 566"/><path d="M876 442 C872 494 888 526 876 568"/>
    <path d="M858 430 C846 474 858 514 848 552"/><path d="M884 438 C884 482 896 518 888 554"/>
  </g>
  <g fill="none" stroke="#ffd06b" stroke-width="3" stroke-linecap="round"><path d="M868 440 C862 490 876 524 866 562"/><path d="M880 452 C880 496 890 524 884 556"/></g>
  <!-- noodle bundle at chopsticks -->
  <g fill="none" stroke="#ffe9b3" stroke-width="5" stroke-linecap="round"><path d="M852 432 q16 -10 30 2 q14 -8 24 4"/><path d="M856 442 q22 -8 44 2"/></g>
</g>

<!-- nori sheet in tentacle E -->
<g transform="rotate(14 922 580)"><rect x="900" y="544" width="46" height="56" rx="4" fill="#1f2b23"/>
<path d="M906 552 h34 M906 566 h34 M906 580 h34" stroke="#33473a" stroke-width="2"/></g>

<!-- scallion sprinkle from tentacle C -->
<g fill="#3fae4a"><circle cx="652" cy="600" r="3.4"/><circle cx="640" cy="608" r="3"/><circle cx="664" cy="608" r="3"/><circle cx="648" cy="616" r="2.8"/><circle cx="630" cy="598" r="2.6"/></g>
<g fill="#8ad67a"><circle cx="652" cy="599" r="1.5"/><circle cx="640" cy="607" r="1.3"/></g>

<!-- ===== COUNTER ===== -->
<g>
  <ellipse cx="600" cy="782" rx="470" ry="18" fill="#000" opacity="0.4" filter="url(#soft)"/>
  <!-- counter top -->
  <path d="M132 620 L1068 620 L1044 656 L156 656z" fill="url(#woodTop)"/>
  <g stroke="#5d3820" stroke-width="2" opacity="0.65"><path d="M150 632 H1052"/><path d="M158 644 H1044"/></g>
  <g fill="#5d3820" opacity="0.7"><circle cx="250" cy="638" r="2.5"/><circle cx="520" cy="638" r="2.5"/><circle cx="790" cy="638" r="2.5"/><circle cx="970" cy="638" r="2.5"/></g>
  <!-- front -->
  <rect x="156" y="656" width="888" height="122" fill="url(#woodFront)"/>
  <g stroke="#3a2313" stroke-width="3"><path d="M156 686 H1044"/><path d="M156 724 H1044"/><path d="M330 656 V778 M540 656 V778 M750 656 V778 M920 656 V778"/></g>
  <g stroke="#9c6b3f" stroke-width="1.6" opacity="0.5"><path d="M180 706 q60 -6 120 0 M580 740 q70 -6 140 0 M790 700 q60 -5 110 0"/></g>
  <!-- menu cards hanging on front -->
  <g font-family="'Hiragino Sans','Noto Sans CJK JP',sans-serif">
    <g transform="rotate(-3 250 716)"><rect x="214" y="682" width="72" height="68" rx="5" fill="#fdf3d8"/><rect x="214" y="682" width="72" height="18" rx="5" fill="#c94a3a"/><text x="250" y="696" text-anchor="middle" font-size="12" font-weight="700" fill="#fff">醤油</text><text x="250" y="720" text-anchor="middle" font-size="11" fill="#5d3820">SHOYU</text><text x="250" y="738" text-anchor="middle" font-size="13" font-weight="700" fill="#8e2620">¥900</text></g>
    <g transform="rotate(2 420 716)"><rect x="384" y="682" width="72" height="68" rx="5" fill="#fdf3d8"/><rect x="384" y="682" width="72" height="18" rx="5" fill="#e07a2e"/><text x="420" y="696" text-anchor="middle" font-size="12" font-weight="700" fill="#fff">味噌</text><text x="420" y="720" text-anchor="middle" font-size="11" fill="#5d3820">MISO</text><text x="420" y="738" text-anchor="middle" font-size="13" font-weight="700" fill="#8e2620">¥950</text></g>
    <g transform="rotate(-2 790 716)"><rect x="754" y="682" width="72" height="68" rx="5" fill="#fdf3d8"/><rect x="754" y="682" width="72" height="18" rx="5" fill="#375a8a"/><text x="790" y="696" text-anchor="middle" font-size="12" font-weight="700" fill="#fff">塩</text><text x="790" y="720" text-anchor="middle" font-size="11" fill="#5d3820">SHIO</text><text x="790" y="738" text-anchor="middle" font-size="13" font-weight="700" fill="#8e2620">¥850</text></g>
    <g transform="rotate(3 950 716)"><rect x="908" y="682" width="84" height="68" rx="5" fill="#fdf3d8"/><rect x="908" y="682" width="84" height="18" rx="5" fill="#3fae4a"/><text x="950" y="696" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">たこ特製</text><text x="950" y="720" text-anchor="middle" font-size="10" fill="#5d3820">TAKO SPECIAL</text><text x="950" y="738" text-anchor="middle" font-size="13" font-weight="700" fill="#8e2620">¥1,200</text></g>
  </g>
  <!-- small "OPEN" plaque -->
  <g transform="rotate(-4 622 736)"><rect x="576" y="714" width="92" height="42" rx="8" fill="#2e1a12"/><rect x="582" y="720" width="80" height="30" rx="5" fill="none" stroke="#ffd98a" stroke-width="1.8"/>
  <text x="622" y="741" text-anchor="middle" font-family="Georgia,serif" font-size="17" font-weight="700" letter-spacing="3" fill="#ffd98a">OPEN</text></g>
</g>

<!-- ===== BOWLS ON COUNTER ===== -->
<!-- centre hero bowl (held / garnished) -->
<g transform="translate(0 -52)">
  <ellipse cx="606" cy="726" rx="98" ry="13" fill="#000" opacity="0.35" filter="url(#soft2)"/>
  <path d="M506 656 a100 62 0 0 0 200 0z" fill="#fdf8ec"/>
  <path d="M506 656 a100 62 0 0 0 200 0z" fill="none" stroke="#d8c9a8" stroke-width="2"/>
  <g fill="none" stroke="#375a8a" stroke-width="3"><path d="M516 678 q90 34 180 0"/></g>
  <g fill="#375a8a"><circle cx="566" cy="696" r="4"/><circle cx="606" cy="702" r="4"/><circle cx="646" cy="696" r="4"/></g>
  <path d="M578 716 h56 l-8 12 h-40z" fill="#e8dcc3"/>
  <ellipse cx="606" cy="656" rx="100" ry="24" fill="#fdf8ec" stroke="#d8c9a8" stroke-width="2"/>
  <ellipse cx="606" cy="656" rx="88" ry="19" fill="url(#broth)"/>
  <g fill="none" stroke="#ffe9b3" stroke-width="4" stroke-linecap="round"><path d="M546 652 q20 -8 40 0 q20 -7 40 1"/><path d="M560 662 q24 -6 48 0 q22 -5 42 1"/></g>
  <rect x="548" y="630" width="26" height="30" rx="3" fill="#1f2b23" transform="rotate(-10 561 645)"/>
  <g transform="translate(648 648)"><use href="#eggHalf"/></g>
  <g transform="translate(588 660)"><use href="#naruto"/></g>
  <g transform="translate(622 644)"><use href="#scallions"/></g>
  <!-- chashu -->
  <g transform="rotate(-8 560 648)"><ellipse cx="560" cy="648" rx="18" ry="10" fill="#c97a5a"/><ellipse cx="560" cy="648" rx="11" ry="5.5" fill="#e8a582"/><path d="M548 648 q12 -5 24 0" fill="none" stroke="#a85a3e" stroke-width="2"/></g>
  <!-- spoon -->
  <g transform="rotate(28 688 660)"><rect x="682" y="622" width="10" height="44" rx="5" fill="#f6efe0" stroke="#d8c9a8" stroke-width="1.5"/><ellipse cx="687" cy="670" rx="13" ry="10" fill="#f6efe0" stroke="#d8c9a8" stroke-width="1.5"/></g>
</g>

<!-- right bowl (under lifted noodles) -->
<g>
  <ellipse cx="868" cy="650" rx="82" ry="11" fill="#000" opacity="0.32" filter="url(#soft2)"/>
  <path d="M788 592 a80 50 0 0 0 160 0z" fill="#c94a3a"/><path d="M788 592 a80 50 0 0 0 160 0z" fill="none" stroke="#8e2620" stroke-width="2"/>
  <g fill="none" stroke="#fdf3d8" stroke-width="2.6"><path d="M800 612 q68 26 136 0"/></g>
  <g fill="#fdf3d8"><circle cx="838" cy="626" r="3.4"/><circle cx="868" cy="631" r="3.4"/><circle cx="898" cy="626" r="3.4"/></g>
  <path d="M846 640 h44 l-6 10 h-32z" fill="#8e2620"/>
  <ellipse cx="868" cy="592" rx="80" ry="20" fill="#fdf8ec" stroke="#8e2620" stroke-width="2"/>
  <ellipse cx="868" cy="592" rx="68" ry="15" fill="url(#broth)"/>
  <g transform="translate(836 588) scale(0.9)"><use href="#eggHalf"/></g>
  <g transform="translate(892 596) scale(0.9)"><use href="#naruto"/></g>
  <g transform="translate(866 582) scale(0.85)"><use href="#scallions"/></g>
</g>

<!-- left small bowl / finished serve -->
<g>
  <ellipse cx="226" cy="648" rx="66" ry="10" fill="#000" opacity="0.3" filter="url(#soft2)"/>
  <path d="M162 600 a64 40 0 0 0 128 0z" fill="#375a8a"/><g fill="none" stroke="#fdf3d8" stroke-width="2.2"><path d="M174 616 q52 20 104 0"/></g>
  <path d="M206 638 h40 l-5 9 h-30z" fill="#2c4a74"/>
  <ellipse cx="226" cy="600" rx="64" ry="16" fill="#fdf8ec" stroke="#2c4a74" stroke-width="2"/>
  <ellipse cx="226" cy="600" rx="53" ry="12" fill="url(#broth)"/>
  <g transform="translate(208 596) scale(0.8)"><use href="#naruto"/></g>
  <g transform="translate(244 602) scale(0.75)"><use href="#scallions"/></g>
  <g stroke="#5d3820" stroke-width="4.5" stroke-linecap="round"><path d="M250 594 L286 566"/><path d="M260 600 L298 578"/></g>
</g>

<!-- counter props: chopstick holder, sauces, tea -->
<g>
  <g transform="translate(752 618)"><path d="M-18 -34 h36 v30 a18 12 0 0 1 -36 0z" fill="#7a4a6e"/><ellipse cx="0" cy="-34" rx="18" ry="5" fill="#5d3654"/>
  <g stroke="#8a5a33" stroke-width="3.4" stroke-linecap="round"><path d="M-8 -34 L-14 -62"/><path d="M0 -34 L0 -64"/><path d="M8 -34 L14 -60"/></g></g>
  <g><rect x="958" y="572" width="20" height="44" rx="6" fill="#8e2620"/><rect x="962" y="562" width="12" height="12" rx="3" fill="#2e1a12"/><rect x="961" y="584" width="14" height="16" rx="2" fill="#fdf3d8"/>
  <rect x="986" y="580" width="18" height="36" rx="6" fill="#2e1a12"/><rect x="990" y="571" width="10" height="11" rx="3" fill="#c94a3a"/><rect x="989" y="590" width="12" height="14" rx="2" fill="#fdf3d8"/></g>
  <g><path d="M452 620 a22 14 0 0 0 44 0z" fill="#f6efe0" stroke="#b8a888" stroke-width="1.6"/><ellipse cx="474" cy="620" rx="22" ry="5" fill="#c9a86a"/></g>
  <!-- steam-curl over tea -->
  <path d="M474 606 q-6 -10 0 -20 q6 -10 0 -18" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" opacity="0.65"/>
</g>

<!-- ===== STEAM ===== -->
<g fill="none" stroke="#ffffff" stroke-linecap="round">
  <g stroke-width="7" opacity="0.5"><path d="M292 478 C278 452 304 438 290 408 C280 386 296 372 290 352"/>
  <path d="M336 480 C326 454 350 440 338 412 C330 392 344 378 338 360"/></g>
  <g stroke-width="5.5" opacity="0.55"><path d="M556 566 C546 546 564 534 554 510 C547 492 559 480 554 462"/>
  <path d="M656 568 C648 548 664 536 656 512"/></g>
  <g stroke-width="5" opacity="0.5"><path d="M852 556 C842 536 860 526 852 502"/><path d="M892 558 C884 540 900 530 894 508"/></g>
  <g stroke-width="4" opacity="0.45"><path d="M214 574 C206 556 220 546 214 526"/></g>
</g>
<!-- happy sparkles near hero bowl / noodles -->
<g fill="#ffd98a"><path d="M716 600 l3 8 8 3 -8 3 -3 8 -3 -8 -8 -3 8 -3z"/><path d="M496 608 l2.5 6.5 6.5 2.5 -6.5 2.5 -2.5 6.5 -2.5 -6.5 -6.5 -2.5 6.5 -2.5z"/><path d="M928 420 l2.5 6.5 6.5 2.5 -6.5 2.5 -2.5 6.5 -2.5 -6.5 -6.5 -2.5 6.5 -2.5z"/></g>

<!-- ===== STOOLS ===== -->
<g>
  <g transform="translate(300 800)"><ellipse cx="0" cy="52" rx="52" ry="8" fill="#000" opacity="0.35"/><rect x="-7" y="10" width="14" height="40" rx="4" fill="#3a2313"/><path d="M-34 50 L0 16 L34 50" fill="none" stroke="#3a2313" stroke-width="7" stroke-linecap="round"/><ellipse cx="0" cy="6" rx="52" ry="15" fill="#c94a3a"/><ellipse cx="0" cy="2" rx="52" ry="14" fill="#e85d4f"/><ellipse cx="-14" cy="-2" rx="18" ry="5" fill="#ff9a8a" opacity="0.7"/></g>
  <g transform="translate(600 812)"><ellipse cx="0" cy="52" rx="52" ry="8" fill="#000" opacity="0.35"/><rect x="-7" y="10" width="14" height="40" rx="4" fill="#3a2313"/><path d="M-34 50 L0 16 L34 50" fill="none" stroke="#3a2313" stroke-width="7" stroke-linecap="round"/><ellipse cx="0" cy="6" rx="52" ry="15" fill="#c94a3a"/><ellipse cx="0" cy="2" rx="52" ry="14" fill="#e85d4f"/><ellipse cx="-14" cy="-2" rx="18" ry="5" fill="#ff9a8a" opacity="0.7"/></g>
  <g transform="translate(900 800)"><ellipse cx="0" cy="52" rx="52" ry="8" fill="#000" opacity="0.35"/><rect x="-7" y="10" width="14" height="40" rx="4" fill="#3a2313"/><path d="M-34 50 L0 16 L34 50" fill="none" stroke="#3a2313" stroke-width="7" stroke-linecap="round"/><ellipse cx="0" cy="6" rx="52" ry="15" fill="#375a8a"/><ellipse cx="0" cy="2" rx="52" ry="14" fill="#4a74ad"/><ellipse cx="-14" cy="-2" rx="18" ry="5" fill="#8ab0d9" opacity="0.7"/></g>
</g>

<!-- foreground ground details: fallen leaf / small cat waiting (bonus charm, bottom-left) -->
<g transform="translate(108 812)">
  <ellipse cx="0" cy="34" rx="42" ry="7" fill="#000" opacity="0.35"/>
  <path d="M-26 30 C-30 6 -14 -8 0 -8 C14 -8 30 6 26 30 C14 38 -14 38 -26 30z" fill="#f2a541"/>
  <path d="M-20 -4 L-26 -22 L-8 -14z M20 -4 L26 -22 L8 -14z" fill="#f2a541"/><path d="M-20 -8 L-23 -18 L-11 -12z M20 -8 L23 -18 L11 -12z" fill="#ffd0a0"/>
  <circle cx="-8" cy="6" r="3" fill="#2b1a1a"/><circle cx="8" cy="6" r="3" fill="#2b1a1a"/>
  <path d="M-3 14 Q0 17 3 14" fill="none" stroke="#2b1a1a" stroke-width="1.8" stroke-linecap="round"/>
  <g stroke="#d97f2b" stroke-width="2.4" stroke-linecap="round"><path d="M-14 -2 h8 M12 -2 h-6"/></g>
  <path d="M26 24 q22 2 20 -14" fill="none" stroke="#f2a541" stroke-width="7" stroke-linecap="round"/>
  <path d="M40 14 q6 -2 6 -6" fill="none" stroke="#d97f2b" stroke-width="3" stroke-linecap="round"/>
  <!-- tiny empty bowl in front of cat -->
  <path d="M22 34 a16 9 0 0 0 32 0z" fill="#fdf8ec"/><ellipse cx="38" cy="34" rx="16" ry="4" fill="#e8dcc3"/>
</g>

<!-- caption plate bottom-right -->
<g>
  <rect x="980" y="842" width="190" height="36" rx="18" fill="#171226" opacity="0.72"/>
  <text x="1075" y="865" text-anchor="middle" font-family="Georgia,serif" font-size="14" letter-spacing="1.5" fill="#ffd98a">eight arms · zero wait</text>
</g>

<!-- vignette -->
<rect width="1200" height="900" fill="none" stroke="#0d0a1c" stroke-width="26" opacity="0.22"/>
</svg>
'''

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg, encoding="utf-8")
print(f"Wrote {OUT} ({OUT.stat().st_size/1024:.1f} KB)")
