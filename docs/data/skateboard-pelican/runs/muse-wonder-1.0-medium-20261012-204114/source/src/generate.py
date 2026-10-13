#!/usr/bin/env python3
"""Generate a pelican-riding-a-skateboard SVG illustration."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "output"
OUT.mkdir(parents=True, exist_ok=True)

svg = r'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900" role="img" aria-labelledby="t d">
<title id="t">A pelican riding a skateboard</title>
<desc id="d">A cheerful white pelican wearing a backwards teal cap rides a pink skateboard along a sunny seaside boardwalk at golden hour.</desc>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#6fd8ef"/><stop offset=".55" stop-color="#bdeef2"/><stop offset="1" stop-color="#ffedb8"/>
  </linearGradient>
  <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0ea6b7"/><stop offset="1" stop-color="#087f9a"/>
  </linearGradient>
  <linearGradient id="board" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#ff5e78"/><stop offset=".55" stop-color="#ff3d68"/><stop offset="1" stop-color="#ff8a3d"/>
  </linearGradient>
  <linearGradient id="beak" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffb02e"/><stop offset="1" stop-color="#ff7a1a"/>
  </linearGradient>
  <linearGradient id="pouch" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ff9d76"/><stop offset="1" stop-color="#ff6b4a"/>
  </linearGradient>
  <radialGradient id="sun" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="#fff7ae"/><stop offset=".75" stop-color="#ffd84d"/><stop offset="1" stop-color="#ffb52e"/>
  </radialGradient>
  <g id="wheel">
    <circle r="38" fill="#ffd23f" stroke="#173a47" stroke-width="7"/>
    <circle r="22" fill="#fff3b0" stroke="#173a47" stroke-width="4"/>
    <circle r="8" fill="#00a8a8" stroke="#173a47" stroke-width="3"/>
    <path d="M0-22 V-9 M19 11 L8 4 M-19 11 L-8 4" stroke="#173a47" stroke-width="4" stroke-linecap="round"/>
  </g>
  <g id="cloud" fill="#ffffff" opacity=".9">
    <ellipse cx="0" cy="0" rx="72" ry="34"/><ellipse cx="52" cy="8" rx="58" ry="26"/><ellipse cx="-54" cy="10" rx="52" ry="24"/>
  </g>
</defs>

<!-- SKY / SEA -->
<rect width="1200" height="900" fill="url(#sky)"/>
<circle cx="986" cy="218" r="108" fill="url(#sun)" stroke="#173a47" stroke-width="6"/>
<g stroke="#ffb52e" stroke-width="9" stroke-linecap="round" opacity=".8">
  <path d="M986 72v-34M1088 116l24-24M1132 218h34M1088 320l24 24M884 116l-24-24"/>
</g>
<g><animateTransform attributeName="transform" type="translate" values="0 0; 28 0; 0 0" dur="9s" repeatCount="indefinite"/>
  <use href="#cloud" x="180" y="118"/><use href="#cloud" x="470" y="82" transform="scale(.72)" opacity=".75"/>
</g>
<use href="#cloud" x="690" y="148" transform="scale(.62)" opacity=".7"/>
<g fill="none" stroke="#173a47" stroke-width="4" stroke-linecap="round" opacity=".55">
  <path d="M92 262 q18-16 36 0 q18-16 36 0"/><path d="M238 302 q14-12 28 0 q14-12 28 0"/>
</g>
<path d="M0 452 Q300 432 620 452 T1200 448 V602 H0Z" fill="url(#sea)"/>
<g stroke="#bff6ff" stroke-width="6" stroke-linecap="round" opacity=".75" fill="none">
  <path d="M70 505 q42-14 84 0 t84 0"/><path d="M740 522 q42-14 84 0 t84 0"/><path d="M420 560 q38-12 76 0 t76 0"/>
</g>
<!-- distant palms -->
<g stroke="#116b67" stroke-width="10" stroke-linecap="round" fill="none">
  <path d="M96 590 C86 520 92 480 112 438"/><path d="M112 440 C76 414 44 416 18 438 M112 440 C98 402 70 386 38 390 M112 440 C128 402 158 388 190 394 M112 440 C146 420 178 424 202 446"/>
  <path d="M1092 592 C1102 528 1096 492 1078 458"/><path d="M1078 460 C1048 436 1018 436 994 456 M1078 460 C1090 428 1116 414 1146 418 M1078 460 C1110 442 1140 446 1162 466"/>
</g>

<!-- BOARDWALK -->
<path d="M0 592 H1200 V900 H0Z" fill="#f6bd72"/>
<path d="M0 592 H1200 V632 H0Z" fill="#e99a52"/>
<g stroke="#b96f35" stroke-width="5" opacity=".55">
  <path d="M0 682 H1200M0 748 H1200M0 824 H1200"/>
  <path d="M150 592 L70 900M410 592 L380 900M680 592 L690 900M940 592 L1020 900"/>
</g>
<g fill="#173a47" opacity=".1"><ellipse cx="250" cy="650" rx="18" ry="6"/><ellipse cx="880" cy="706" rx="24" ry="7"/><ellipse cx="560" cy="858" rx="30" ry="8"/></g>

<!-- speed lines -->
<g stroke="#ffffff" stroke-width="9" stroke-linecap="round" opacity=".85">
  <path d="M44 512 H196"/><path d="M22 574 H158"/><path d="M66 640 H214"/>
</g>
<g stroke="#173a47" stroke-width="5" stroke-linecap="round" opacity=".25"><path d="M44 512 H196M22 574 H158M66 640 H214"/></g>

<!-- shadow -->
<ellipse cx="590" cy="806" rx="360" ry="34" fill="#7a3f16" opacity=".28"/>

<g>
<animateTransform attributeName="transform" type="translate" values="0 0; 0 -7; 0 0" dur="1.15s" repeatCount="indefinite"/>

  <!-- SKATEBOARD -->
  <g transform="rotate(-3 590 730)">
    <path d="M282 706 Q272 742 314 744 L872 744 Q918 742 926 708 Q928 690 900 688 L330 688 Q292 688 282 706Z" fill="url(#board)" stroke="#173a47" stroke-width="7"/>
    <path d="M300 700 H902" stroke="#ffe66d" stroke-width="8" stroke-linecap="round"/>
    <circle cx="368" cy="700" r="6" fill="#173a47"/><circle cx="838" cy="700" r="6" fill="#173a47"/>
    <path d="M398 742 v18 M790 742 v18" stroke="#173a47" stroke-width="10" stroke-linecap="round"/>
    <g transform="translate(398 778)"><g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur=".55s" repeatCount="indefinite"/><use href="#wheel"/></g></g>
    <g transform="translate(790 778)"><g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur=".55s" repeatCount="indefinite"/><use href="#wheel"/></g></g>
  </g>

  <!-- back leg (behind body lower edge) -->
  <path d="M642 586 C660 640 668 668 674 700" fill="none" stroke="#ff8a1e" stroke-width="22" stroke-linecap="round"/>
  <path d="M640 700 q52-16 92 2 q-34 18-92 12 q-24-3-18-12 q4-6 18-2Z" fill="#ffb02e" stroke="#173a47" stroke-width="6" stroke-linejoin="round"/>

  <!-- tail feathers -->
  <g fill="#eaf7f7" stroke="#173a47" stroke-width="6" stroke-linejoin="round">
    <path d="M310 470 L172 408 Q218 500 292 528Z"/><path d="M322 512 L160 512 Q226 562 322 560Z"/><path d="M340 448 L224 348 Q246 440 318 482Z"/>
  </g>

  <!-- BODY -->
  <path d="M286 520 C286 424 392 356 548 366 C694 376 802 448 806 536 C810 626 706 676 548 676 C402 676 286 622 286 520Z" fill="#fffdf6" stroke="#173a47" stroke-width="7"/>
  <path d="M352 610 C430 656 650 662 748 590" fill="none" stroke="#cfe8e8" stroke-width="8" stroke-linecap="round"/>

  <!-- balancing wing (far, left-down) -->
  <path d="M390 452 C300 470 232 526 202 606 C268 606 356 560 408 506Z" fill="#dff3f3" stroke="#173a47" stroke-width="6" stroke-linejoin="round"/>
  <path d="M246 570 C290 536 338 508 382 492" fill="none" stroke="#9fc9cf" stroke-width="5" stroke-linecap="round"/>

  <!-- front leg -->
  <path d="M520 640 C510 668 506 684 508 706" fill="none" stroke="#ff8a1e" stroke-width="22" stroke-linecap="round"/>
  <path d="M474 706 q50-18 96 0 q-30 20-92 14 q-28-3-22-12 q4-7 18-2Z" fill="#ffb02e" stroke="#173a47" stroke-width="6" stroke-linejoin="round"/>

  <!-- NECK -->
  <path d="M650 430 C648 340 664 272 716 214 C748 178 806 182 824 226 C838 260 812 292 782 306 C736 328 724 376 736 442 C744 486 700 506 664 486 C640 472 651 456 650 430Z" fill="#fffdf6" stroke="#173a47" stroke-width="7" stroke-linejoin="round"/>
  <!-- hide neck/body seam -->
  <path d="M650 430 C648 380 656 320 682 272" fill="none" stroke="#fffdf6" stroke-width="18"/>

  <!-- main wing -->
  <path d="M428 416 C540 382 682 424 716 510 C672 596 520 632 424 566 C380 514 386 452 428 416Z" fill="#eefafa" stroke="#173a47" stroke-width="7" stroke-linejoin="round"/>
  <g fill="none" stroke="#9fc9cf" stroke-width="6" stroke-linecap="round">
    <path d="M448 470 C530 442 632 462 682 506"/><path d="M442 522 C522 496 620 512 674 544"/><path d="M486 570 C548 552 616 560 656 574"/>
  </g>
  <circle cx="468" cy="448" r="9" fill="#00a8a8"/><circle cx="640" cy="452" r="9" fill="#ff5e78"/>

  <!-- HEAD -->
  <ellipse cx="772" cy="204" rx="92" ry="76" fill="#fffdf6" stroke="#173a47" stroke-width="7"/>
  <!-- crest -->
  <g fill="#fff3b0" stroke="#173a47" stroke-width="6" stroke-linejoin="round">
    <path d="M706 148 L668 92 L724 122 L742 66 L768 120 L812 78 L816 136 C776 118 738 124 706 148Z"/>
  </g>
  <!-- POUCH + BEAK -->
  <path d="M824 238 C880 282 950 306 1032 300 C966 348 872 340 824 282Z" fill="url(#pouch)" stroke="#173a47" stroke-width="6" stroke-linejoin="round"/>
  <path d="M838 202 C930 218 1024 252 1086 292 C1030 302 918 278 842 242 C824 232 824 208 838 202Z" fill="url(#beak)" stroke="#173a47" stroke-width="7" stroke-linejoin="round"/>
  <path d="M860 226 C940 242 1010 266 1058 288" fill="none" stroke="#c75a00" stroke-width="4" stroke-linecap="round" opacity=".6"/>
  <circle cx="1078" cy="290" r="7" fill="#173a47"/>
  <!-- gular flutter lines -->
  <path d="M866 292 q28 18 62 20 M850 268 q22 22 54 28" fill="none" stroke="#d84f35" stroke-width="4" stroke-linecap="round" opacity=".65"/>

  <!-- eye + cheek -->
  <circle cx="790" cy="196" r="27" fill="#ffffff" stroke="#173a47" stroke-width="5"/>
  <circle cx="798" cy="198" r="11" fill="#173a47"/><circle cx="802" cy="193" r="4" fill="#fff"/>
  <circle cx="742" cy="238" r="16" fill="#ffb3c1" opacity=".85"/>
  <path d="M724 176 q18-14 38-8" fill="none" stroke="#173a47" stroke-width="5" stroke-linecap="round"/>

  <!-- backwards cap -->
  <path d="M700 158 C716 104 790 84 842 122 C862 136 866 158 852 166 L716 178 C700 176 696 170 700 158Z" fill="#00a8a8" stroke="#173a47" stroke-width="7" stroke-linejoin="round"/>
  <path d="M716 174 C668 166 626 176 596 202 C640 210 686 202 724 188Z" fill="#ff5e78" stroke="#173a47" stroke-width="6" stroke-linejoin="round"/>
  <circle cx="782" cy="106" r="11" fill="#ff5e78" stroke="#173a47" stroke-width="5"/>
  <path d="M730 148 C762 124 806 118 838 132" fill="none" stroke="#007f7f" stroke-width="6" stroke-linecap="round"/>

  <!-- raised wingtip giving thumbs-up vibe at neck -->
  <path d="M648 438 C706 414 786 438 814 500 C774 534 692 524 660 492 C642 474 636 448 648 438Z" fill="#dff3f3" stroke="#173a47" stroke-width="6" stroke-linejoin="round"/>
</g>

<!-- foreground motion puffs -->
<g fill="#fff" stroke="#173a47" stroke-width="5" opacity=".9">
  <ellipse cx="238" cy="786" rx="46" ry="18"/><ellipse cx="282" cy="772" rx="30" ry="14"/>
  <ellipse cx="966" cy="800" rx="38" ry="15"/>
</g>
<g fill="#173a47"><circle cx="1048" cy="852" r="6"/><circle cx="1106" cy="836" r="5"/><circle cx="118" cy="850" r="5"/></g>
</svg>
'''

(OUT / "pelican-skateboard.svg").write_text(svg, encoding="utf-8")
print(f"Wrote {OUT / 'pelican-skateboard.svg'} ({len(svg)} bytes)")
