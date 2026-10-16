#!/usr/bin/env python3
"""Generate an SVG illustration: an octopus chef at a ramen booth."""
from pathlib import Path

SVG = r'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900" role="img" aria-labelledby="title desc">
<title id="title">Octopus Chef at a Ramen Booth</title>
<desc id="desc">A cheerful octopus wearing a chef hat serves steaming ramen from a cozy night-market booth hung with red lanterns.</desc>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#141b3d"/><stop offset="0.55" stop-color="#2a3566"/><stop offset="1" stop-color="#4a3a6b"/>
  </linearGradient>
  <linearGradient id="boothWall" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#7a4a2e"/><stop offset="1" stop-color="#5d3620"/>
  </linearGradient>
  <linearGradient id="counter" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#c98a4e"/><stop offset="0.12" stop-color="#b5763e"/><stop offset="1" stop-color="#8a5527"/>
  </linearGradient>
  <linearGradient id="roof" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#d94a3e"/><stop offset="1" stop-color="#a82f26"/>
  </linearGradient>
  <radialGradient id="octoBody" cx="0.42" cy="0.32" r="0.85">
    <stop offset="0" stop-color="#ffb3a6"/><stop offset="0.45" stop-color="#ff7a6b"/><stop offset="1" stop-color="#e84a3f"/>
  </radialGradient>
  <radialGradient id="tentacle" cx="0.4" cy="0.3" r="0.9">
    <stop offset="0" stop-color="#ffa496"/><stop offset="1" stop-color="#ee5b4c"/>
  </radialGradient>
  <radialGradient id="lanternGlow" cx="0.5" cy="0.45" r="0.65">
    <stop offset="0" stop-color="#fff3b0"/><stop offset="0.45" stop-color="#ffb74d"/><stop offset="1" stop-color="#e53935"/>
  </radialGradient>
  <radialGradient id="broth" cx="0.5" cy="0.5" r="0.6">
    <stop offset="0" stop-color="#ffe9a8"/><stop offset="0.7" stop-color="#f5b942"/><stop offset="1" stop-color="#e08a1e"/>
  </radialGradient>
  <linearGradient id="pot" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#c7d0d8"/><stop offset="0.5" stop-color="#8d9aa6"/><stop offset="1" stop-color="#5f6b77"/>
  </linearGradient>
  <linearGradient id="bowl" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2e5f8a"/><stop offset="1" stop-color="#1a3a57"/>
  </linearGradient>
  <radialGradient id="warmLight" cx="0.5" cy="0.42" r="0.55">
    <stop offset="0" stop-color="#ffe6a0" stop-opacity="0.34"/><stop offset="1" stop-color="#ffe6a0" stop-opacity="0"/>
  </radialGradient>
  <filter id="soft" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="softer" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="14"/></filter>
</defs>

<!-- ===== Night sky ===== -->
<rect width="1200" height="900" fill="url(#sky)"/>
<g fill="#ffffff">
  <circle cx="70" cy="60" r="2.4" opacity=".9"/><circle cx="180" cy="36" r="1.8" opacity=".7"/>
  <circle cx="340" cy="70" r="2" opacity=".8"/><circle cx="520" cy="34" r="1.6" opacity=".6"/>
  <circle cx="760" cy="48" r="2.2" opacity=".85"/><circle cx="930" cy="30" r="1.7" opacity=".7"/>
  <circle cx="1080" cy="72" r="2.4" opacity=".9"/><circle cx="1150" cy="140" r="1.6" opacity=".6"/>
  <circle cx="42" cy="170" r="1.7" opacity=".6"/><circle cx="660" cy="88" r="1.5" opacity=".55"/>
  <circle cx="1005" cy="110" r="1.6" opacity=".6"/><circle cx="250" cy="112" r="1.5" opacity=".55"/>
</g>
<circle cx="1062" cy="86" r="34" fill="#f7e8b0"/>
<circle cx="1076" cy="80" r="30" fill="#1c2548" opacity="0.92"/>
<circle cx="1062" cy="86" r="58" fill="#f7e8b0" opacity="0.08"/>
<!-- distant rooftops -->
<g fill="#1c2548">
  <path d="M0 300 L120 262 L240 300 L240 360 L0 360 Z"/>
  <path d="M960 300 L1080 258 L1200 300 L1200 360 L960 360 Z"/>
  <rect x="985" y="310" width="18" height="24" fill="#ffd970" opacity=".85"/>
  <rect x="28" y="312" width="16" height="22" fill="#ffd970" opacity=".8"/>
</g>

<!-- ===== Booth structure ===== -->
<g>
  <rect x="150" y="235" width="900" height="430" fill="url(#boothWall)"/>
  <!-- wall planks -->
  <g stroke="#4e2c18" stroke-width="2" opacity="0.5">
    <line x1="270" y1="235" x2="270" y2="665"/><line x1="390" y1="235" x2="390" y2="665"/>
    <line x1="510" y1="235" x2="510" y2="665"/><line x1="630" y1="235" x2="630" y2="665"/>
    <line x1="750" y1="235" x2="750" y2="665"/><line x1="870" y1="235" x2="870" y2="665"/>
    <line x1="990" y1="235" x2="990" y2="665"/>
  </g>
  <!-- warm interior light -->
  <rect x="150" y="235" width="900" height="430" fill="url(#warmLight)"/>
  <!-- side posts -->
  <rect x="150" y="220" width="26" height="620" fill="#4e2c18"/>
  <rect x="1024" y="220" width="26" height="620" fill="#4e2c18"/>
  <!-- roof -->
  <path d="M110 238 L600 128 L1090 238 L1048 268 L600 168 L152 268 Z" fill="url(#roof)"/>
  <path d="M110 238 L600 128 L1090 238" fill="none" stroke="#7c1f16" stroke-width="6" stroke-linecap="round"/>
  <g stroke="#8f2a20" stroke-width="3" opacity="0.55">
    <line x1="300" y1="195" x2="292" y2="248"/><line x1="460" y1="160" x2="454" y2="212"/>
    <line x1="740" y1="160" x2="746" y2="212"/><line x1="900" y1="195" x2="908" y2="248"/>
  </g>
  <!-- sign board -->
  <g>
    <rect x="440" y="182" width="320" height="62" rx="10" fill="#fff6da" stroke="#7c3b18" stroke-width="5"/>
    <circle cx="482" cy="213" r="17" fill="#e84a3f"/>
    <circle cx="482" cy="213" r="10" fill="#fff6da"/>
    <path d="M474 213 q8-7 16 0 q-8 7-16 0" fill="#e84a3f"/>
    <text x="618" y="228" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="36" font-weight="bold" letter-spacing="5" fill="#5d2f0e">RAMEN</text>
  </g>
</g>

<!-- string lights -->
<g fill="none" stroke="#2b2b2b" stroke-width="2.5">
  <path d="M152 268 Q380 330 600 286 Q820 330 1048 268"/>
</g>
<g>
  <circle cx="345" cy="303" r="22" fill="#ffd970" opacity="0.22"/>
  <circle cx="488" cy="298" r="22" fill="#ffd970" opacity="0.22"/>
  <circle cx="712" cy="298" r="22" fill="#ffd970" opacity="0.22"/>
  <circle cx="855" cy="303" r="22" fill="#ffd970" opacity="0.22"/>
  <circle cx="345" cy="303" r="6.5" fill="#ffe9a0"/><circle cx="418" cy="304" r="5.5" fill="#ffb3a6"/>
  <circle cx="488" cy="298" r="6.5" fill="#ffe9a0"/><circle cx="600" cy="291" r="5.5" fill="#a8e6cf"/>
  <circle cx="712" cy="298" r="6.5" fill="#ffe9a0"/><circle cx="782" cy="304" r="5.5" fill="#ffb3a6"/>
  <circle cx="855" cy="303" r="6.5" fill="#ffe9a0"/>
</g>

<!-- hanging lanterns -->
<g>
  <g transform="translate(90,336)">
    <line x1="0" y1="-92" x2="0" y2="-34" stroke="#2b2b2b" stroke-width="3"/>
    <ellipse cx="0" cy="0" rx="34" ry="40" fill="url(#lanternGlow)"/>
    <path d="M-34-12 Q0-6 34-12 M-34 12 Q0 18 34 12" fill="none" stroke="#b71c1c" stroke-width="2.5"/>
    <rect x="-13" y="-46" width="26" height="9" rx="3" fill="#5d2f0e"/><rect x="-13" y="37" width="26" height="9" rx="3" fill="#5d2f0e"/>
    <text x="0" y="9" text-anchor="middle" font-family="Georgia,serif" font-size="22" font-weight="bold" fill="#7c1f16">麺</text>
  </g>
  <g transform="translate(1110,336)">
    <line x1="0" y1="-92" x2="0" y2="-34" stroke="#2b2b2b" stroke-width="3"/>
    <ellipse cx="0" cy="0" rx="34" ry="40" fill="url(#lanternGlow)"/>
    <path d="M-34-12 Q0-6 34-12 M-34 12 Q0 18 34 12" fill="none" stroke="#b71c1c" stroke-width="2.5"/>
    <rect x="-13" y="-46" width="26" height="9" rx="3" fill="#5d2f0e"/><rect x="-13" y="37" width="26" height="9" rx="3" fill="#5d2f0e"/>
    <text x="0" y="9" text-anchor="middle" font-family="Georgia,serif" font-size="22" font-weight="bold" fill="#7c1f16">麺</text>
  </g>
</g>

<!-- noren curtain (behind octopus head, split panels) -->
<g>
  <rect x="176" y="270" width="150" height="110" fill="#25406b"/>
  <rect x="874" y="270" width="150" height="110" fill="#25406b"/>
  <circle cx="251" cy="322" r="26" fill="none" stroke="#fff6da" stroke-width="3"/>
  <path d="M251 304 q14 18 0 36 q-14-18 0-36" fill="#fff6da" opacity="0.9"/>
  <circle cx="949" cy="322" r="26" fill="none" stroke="#fff6da" stroke-width="3"/>
  <path d="M949 304 q14 18 0 36 q-14-18 0-36" fill="#fff6da" opacity="0.9"/>
  <rect x="176" y="270" width="848" height="8" fill="#3a2410"/>
</g>

<!-- shelf props behind -->
<g>
  <rect x="190" y="452" width="150" height="10" fill="#4e2c18"/>
  <rect x="206" y="416" width="26" height="36" rx="4" fill="#d8432f"/><rect x="206" y="426" width="26" height="8" fill="#fff6da"/>
  <rect x="242" y="410" width="26" height="42" rx="4" fill="#2e7d5a"/><rect x="242" y="422" width="26" height="8" fill="#fff6da"/>
  <rect x="278" y="420" width="26" height="32" rx="4" fill="#f5b942"/><rect x="278" y="430" width="26" height="7" fill="#5d2f0e"/>
  <rect x="860" y="452" width="150" height="10" fill="#4e2c18"/>
  <ellipse cx="890" cy="446" rx="24" ry="7" fill="#fff6da"/><path d="M866 446 a24 24 0 0 0 48 0 Z" fill="#2e5f8a"/>
  <ellipse cx="942" cy="446" rx="24" ry="7" fill="#fff6da"/><path d="M918 446 a24 24 0 0 0 48 0 Z" fill="#e84a3f"/>
  <ellipse cx="980" cy="446" rx="20" ry="6" fill="#fff6da"/><path d="M960 446 a20 20 0 0 0 40 0 Z" fill="#2e7d5a"/>
</g>

<!-- ===== OCTOPUS CHEF ===== -->
<!-- back tentacles (raised, behind head) -->
<g fill="url(#tentacle)" stroke="#c93a30" stroke-width="3">
  <!-- waving tentacle, viewer left -->
  <path d="M452 468 C390 430 340 420 318 372 C306 346 322 326 342 332 C358 337 360 356 366 374 C376 404 420 416 468 432 Z"/>
  <!-- tentacle holding menu, viewer right -->
  <path d="M748 468 C810 436 852 424 870 382 C880 358 862 340 844 348 C830 354 830 372 826 388 C818 416 778 430 732 440 Z"/>
</g>
<g fill="#ffd9d2" opacity="0.85">
  <circle cx="348" cy="382" r="6"/><circle cx="368" cy="402" r="5.5"/><circle cx="396" cy="418" r="5"/>
  <circle cx="848" cy="390" r="6"/><circle cx="826" cy="410" r="5.5"/><circle cx="796" cy="424" r="5"/>
</g>
<!-- menu card in right tentacle -->
<g transform="translate(842,300) rotate(8)">
  <rect x="-42" y="-52" width="84" height="104" rx="7" fill="#fff6da" stroke="#7c3b18" stroke-width="4"/>
  <text x="0" y="-28" text-anchor="middle" font-family="Georgia,serif" font-size="14" font-weight="bold" fill="#5d2f0e">MENU</text>
  <g stroke="#9a6a35" stroke-width="3" stroke-linecap="round">
    <line x1="-28" y1="-10" x2="28" y2="-10"/><line x1="-28" y1="4" x2="20" y2="4"/>
    <line x1="-28" y1="18" x2="28" y2="18"/><line x1="-28" y1="32" x2="14" y2="32"/>
  </g>
  <circle cx="0" cy="46" r="0" fill="none"/>
</g>

<!-- head / mantle -->
<g>
  <path d="M600 318 C500 318 438 388 438 478 C438 545 478 592 540 610 L660 610 C722 592 762 545 762 478 C762 388 700 318 600 318 Z" fill="url(#octoBody)" stroke="#c93a30" stroke-width="3.5"/>
  <!-- head sheen + spots -->
  <ellipse cx="520" cy="392" rx="46" ry="62" fill="#ffffff" opacity="0.20" transform="rotate(-18 520 392)"/>
  <g fill="#d94a3e" opacity="0.45">
    <circle cx="478" cy="452" r="7"/><circle cx="726" cy="438" r="6"/><circle cx="706" cy="466" r="4.5"/><circle cx="492" cy="480" r="4.5"/>
  </g>
  <!-- chef hat -->
  <g>
    <path d="M492 344 C470 320 474 286 500 276 C508 252 538 242 560 254 C578 232 622 232 640 254 C662 242 692 252 700 276 C726 286 730 320 708 344 Z" fill="#ffffff" stroke="#d9dde3" stroke-width="3"/>
    <rect x="488" y="338" width="224" height="34" rx="9" fill="#ffffff" stroke="#d9dde3" stroke-width="3"/>
    <g stroke="#e6eaf0" stroke-width="4" stroke-linecap="round">
      <line x1="548" y1="268" x2="544" y2="330"/><line x1="600" y1="258" x2="600" y2="330"/><line x1="652" y1="268" x2="656" y2="330"/>
    </g>
    <ellipse cx="600" cy="355" rx="112" ry="5" fill="#eef1f5"/>
  </g>
  <!-- eyes -->
  <g>
    <ellipse cx="548" cy="468" rx="21" ry="27" fill="#33272a"/>
    <ellipse cx="652" cy="468" rx="21" ry="27" fill="#33272a"/>
    <circle cx="541" cy="458" r="7.5" fill="#fff"/><circle cx="645" cy="458" r="7.5" fill="#fff"/>
    <circle cx="556" cy="478" r="3.5" fill="#fff" opacity=".9"/><circle cx="660" cy="478" r="3.5" fill="#fff" opacity=".9"/>
    <!-- happy brows -->
    <path d="M522 432 Q548 420 574 432" fill="none" stroke="#b03024" stroke-width="5" stroke-linecap="round"/>
    <path d="M626 432 Q652 420 678 432" fill="none" stroke="#b03024" stroke-width="5" stroke-linecap="round"/>
  </g>
  <!-- mouth: cheerful open smile -->
  <path d="M572 518 Q600 540 628 518 Q626 548 600 552 Q574 548 572 518 Z" fill="#7c2118"/>
  <path d="M584 539 Q600 548 616 539 Q610 550 600 550 Q590 550 584 539 Z" fill="#ff8a80"/>
  <!-- blush -->
  <ellipse cx="498" cy="512" rx="24" ry="13" fill="#ff9d94" opacity="0.75"/>
  <ellipse cx="702" cy="512" rx="24" ry="13" fill="#ff9d94" opacity="0.75"/>
  <!-- neckerchief (band + knot, sits above the counter) -->
  <path d="M532 578 Q600 602 668 578 L668 598 Q600 622 532 598 Z" fill="#f5b942" stroke="#d99a1e" stroke-width="3" stroke-linejoin="round"/>
  <path d="M588 596 L600 616 L612 596 Z" fill="#f5b942" stroke="#d99a1e" stroke-width="2.5" stroke-linejoin="round"/>
  <circle cx="600" cy="596" r="8" fill="#e08a1e" stroke="#b96f0d" stroke-width="2.5"/>
</g>

<!-- ===== COUNTER ===== -->
<g>
  <rect x="96" y="602" width="1008" height="26" rx="8" fill="url(#counter)" stroke="#6e3f16" stroke-width="3"/>
  <rect x="120" y="628" width="960" height="150" fill="#6e4525"/>
  <g stroke="#54331a" stroke-width="2.5" opacity="0.6">
    <line x1="120" y1="678" x2="1080" y2="678"/><line x1="120" y1="728" x2="1080" y2="728"/>
  </g>
  <rect x="120" y="628" width="960" height="150" fill="none" stroke="#4e2c18" stroke-width="4"/>
  <!-- counter-top sheen -->
  <rect x="110" y="606" width="980" height="7" rx="3" fill="#ffffff" opacity="0.18"/>
</g>

<!-- front tentacles draped over counter -->
<g fill="url(#tentacle)" stroke="#c93a30" stroke-width="3">
  <path d="M468 600 C430 636 396 648 372 640 C352 633 350 612 364 602 C378 592 394 606 410 606 C428 606 442 592 452 578 Z"/>
  <path d="M540 610 C530 650 540 676 522 690 C506 702 488 690 490 672 C492 658 506 652 506 636 L506 612 Z"/>
  <path d="M660 610 C670 650 660 676 678 690 C694 702 712 690 710 672 C708 658 694 652 694 636 L694 612 Z"/>
  <path d="M732 600 C770 636 804 648 828 640 C848 633 850 612 836 602 C822 592 806 606 790 606 C772 606 758 592 748 578 Z"/>
</g>
<g fill="#ffd9d2" opacity="0.9">
  <circle cx="390" cy="626" r="5.5"/><circle cx="414" cy="614" r="5"/><circle cx="506" cy="654" r="5"/>
  <circle cx="694" cy="654" r="5"/><circle cx="810" cy="626" r="5.5"/><circle cx="786" cy="614" r="5"/>
</g>

<!-- ===== Pot with ladle tentacle (left of counter) ===== -->
<g>
  <!-- tentacle reaching to ladle -->
  <path d="M470 580 C410 560 360 552 322 520 C300 502 286 484 292 466 C298 450 318 448 330 460 C342 472 340 488 356 500 C384 522 430 530 478 540 Z" fill="url(#tentacle)" stroke="#c93a30" stroke-width="3"/>
  <g fill="#ffd9d2"><circle cx="316" cy="486" r="5"/><circle cx="344" cy="504" r="5"/><circle cx="378" cy="520" r="4.5"/></g>
  <!-- ladle -->
  <line x1="300" y1="472" x2="272" y2="540" stroke="#8d9aa6" stroke-width="7" stroke-linecap="round"/>
  <ellipse cx="268" cy="548" rx="20" ry="11" fill="#aeb9c4" stroke="#7c8894" stroke-width="2.5"/>
  <ellipse cx="268" cy="545" rx="15" ry="7" fill="#f5b942"/>
  <!-- pot -->
  <path d="M196 552 L340 552 L332 602 L204 602 Z" fill="url(#pot)" stroke="#4e5963" stroke-width="3"/>
  <ellipse cx="268" cy="552" rx="72" ry="13" fill="#e8eef3" stroke="#7c8894" stroke-width="2.5"/>
  <ellipse cx="268" cy="552" rx="58" ry="9" fill="url(#broth)"/>
  <path d="M196 562 q-20 4-18 16 q2 12 22 10 M340 562 q20 4 18 16 q-2 12-22 10" fill="none" stroke="#4e5963" stroke-width="5"/>
  <!-- steam -->
  <g fill="none" stroke="#ffffff" stroke-linecap="round" opacity="0.85">
    <path d="M238 532 q-10-18 0-34 q10-16 0-32" stroke-width="6" opacity="0.7"/>
    <path d="M268 534 q-10-18 0-34 q10-16 0-32" stroke-width="6"/>
    <path d="M298 532 q-10-18 0-34 q10-16 0-32" stroke-width="6" opacity="0.7"/>
  </g>
</g>

<!-- ===== Big ramen bowl with chopstick tentacle (right / foreground) ===== -->
<g>
  <!-- tentacle holding chopsticks -->
  <path d="M730 580 C790 556 836 540 858 506 C870 487 858 470 842 472 C828 474 824 488 816 502 C800 528 762 542 722 548 Z" fill="url(#tentacle)" stroke="#c93a30" stroke-width="3"/>
  <g fill="#ffd9d2"><circle cx="840" cy="492" r="5"/><circle cx="820" cy="512" r="4.5"/><circle cx="792" cy="528" r="4.5"/></g>
  <!-- chopsticks -->
  <g stroke="#e8b06a" stroke-width="7" stroke-linecap="round">
    <line x1="850" y1="472" x2="898" y2="542"/>
    <line x1="868" y1="480" x2="914" y2="540"/>
  </g>
  <g stroke="#9a6428" stroke-width="2" stroke-linecap="round" opacity="0.7">
    <line x1="850" y1="472" x2="898" y2="542"/><line x1="868" y1="480" x2="914" y2="540"/>
  </g>
  <!-- lifted noodles -->
  <g fill="none" stroke="#ffd970" stroke-width="5" stroke-linecap="round">
    <path d="M900 542 q-6 12 1 20 q6 8 2 16"/>
    <path d="M908 541 q-4 12 3 20 q6 8 3 15"/>
    <path d="M894 543 q-6 10-2 20"/>
  </g>
  <!-- bowl (scaled down so it rests near the counter top) -->
  <g transform="translate(910,548) scale(0.8) translate(-910,-574)">
  <ellipse cx="910" cy="602" rx="118" ry="14" fill="#4e2c18" opacity="0.35"/>
  <path d="M794 574 a116 116 0 0 0 232 0 Z" fill="url(#bowl)" stroke="#12283d" stroke-width="3"/>
  <rect x="874" y="678" width="72" height="12" rx="5" fill="#12283d"/>
  <g fill="none" stroke="#ffffff" stroke-width="3" opacity="0.75">
    <path d="M820 618 q14-12 28 0 q14 12 28 0 q14-12 28 0 q14 12 28 0 q14-12 28 0 q14 12 28 0"/>
  </g>
  <ellipse cx="910" cy="574" rx="116" ry="22" fill="#fff6da" stroke="#d9c9a0" stroke-width="2.5"/>
  <ellipse cx="910" cy="574" rx="100" ry="17" fill="url(#broth)"/>
  <!-- toppings: nori, egg, narutomaki, scallions -->
  <rect x="820" y="540" width="38" height="34" rx="4" fill="#1e3d2a" transform="rotate(-10 839 557)"/>
  <g transform="translate(870,566)">
    <ellipse rx="24" ry="14" fill="#ffffff"/><ellipse rx="11" ry="7.5" fill="#ff9f1a"/>
  </g>
  <g transform="translate(952,562)">
    <circle r="15" fill="#ffffff" stroke="#f0a0a8" stroke-width="2"/>
    <path d="M0-9 a9 9 0 1 1-9 9 a6 6 0 1 0 6-6 a3.5 3.5 0 1 1-3.5 3.5" fill="none" stroke="#ef6f7d" stroke-width="2.5"/>
  </g>
  <g fill="#2e9e5b">
    <circle cx="900" cy="580" r="3.5"/><circle cx="918" cy="584" r="3"/><circle cx="934" cy="578" r="3.5"/>
    <circle cx="886" cy="584" r="3"/><circle cx="968" cy="580" r="3"/>
  </g>
  <g fill="none" stroke="#ffe29a" stroke-width="3.5" stroke-linecap="round" opacity="0.9">
    <path d="M836 576 q10-6 20 0 M930 570 q10-6 20 0 M880 586 q10-5 20 0"/>
  </g>
  <!-- steam -->
  <g fill="none" stroke="#ffffff" stroke-linecap="round">
    <path d="M872 540 q-9-14 0-28" stroke-width="6" opacity="0.75"/>
    <path d="M910 536 q-9-14 0-28" stroke-width="6" opacity="0.9"/>
    <path d="M946 540 q-9-14 0-28" stroke-width="6" opacity="0.75"/>
  </g>
  </g>
</g>

<!-- small served bowl on counter, left-front -->
<g>
  <path d="M404 578 a52 52 0 0 0 104 0 Z" fill="#e84a3f" stroke="#b03024" stroke-width="2.5"/>
  <ellipse cx="456" cy="578" rx="52" ry="10" fill="#fff6da"/>
  <ellipse cx="456" cy="578" rx="42" ry="7.5" fill="url(#broth)"/>
  <circle cx="442" cy="577" r="7" fill="#fff"/><circle cx="442" cy="577" r="3.2" fill="#ef6f7d"/>
  <g fill="#2e9e5b"><circle cx="466" cy="579" r="2.5"/><circle cx="454" cy="581" r="2.2"/></g>
  <path d="M440 562 q-6-12 0-22 M462 560 q-6-12 0-22" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity="0.8"/>
</g>

<!-- ===== Foreground: stools + ground ===== -->
<rect x="0" y="778" width="1200" height="122" fill="#241d33"/>
<rect x="0" y="778" width="1200" height="8" fill="#171221"/>
<g stroke="#3a2c1e" stroke-width="2" opacity="0.5">
  <line x1="0" y1="818" x2="1200" y2="818"/><line x1="0" y1="858" x2="1200" y2="858"/>
</g>
<g>
  <g transform="translate(300,800)">
    <ellipse cx="0" cy="58" rx="58" ry="10" fill="#000" opacity="0.3"/>
    <rect x="-9" y="14" width="18" height="42" fill="#5d3a1e"/>
    <ellipse cx="0" cy="8" rx="52" ry="13" fill="#c0392b"/><ellipse cx="0" cy="3" rx="52" ry="12" fill="#e05244"/>
  </g>
  <g transform="translate(600,806)">
    <ellipse cx="0" cy="58" rx="58" ry="10" fill="#000" opacity="0.3"/>
    <rect x="-9" y="14" width="18" height="42" fill="#5d3a1e"/>
    <ellipse cx="0" cy="8" rx="52" ry="13" fill="#c0392b"/><ellipse cx="0" cy="3" rx="52" ry="12" fill="#e05244"/>
  </g>
  <g transform="translate(900,800)">
    <ellipse cx="0" cy="58" rx="58" ry="10" fill="#000" opacity="0.3"/>
    <rect x="-9" y="14" width="18" height="42" fill="#5d3a1e"/>
    <ellipse cx="0" cy="8" rx="52" ry="13" fill="#c0392b"/><ellipse cx="0" cy="3" rx="52" ry="12" fill="#e05244"/>
  </g>
</g>
<!-- ground warm pool of light -->
<ellipse cx="600" cy="800" rx="480" ry="52" fill="#ffb74d" opacity="0.10" filter="url(#softer)"/>
<!-- vignette -->
<rect width="1200" height="900" fill="none" stroke="#0d0a1a" stroke-width="26" opacity="0.35"/>
</svg>
'''

def main():
    out = Path(__file__).resolve().parent.parent / "output" / "octopus-ramen-chef.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(SVG, encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
