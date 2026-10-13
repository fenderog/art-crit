#!/usr/bin/env python3
"""Generate a cheerful SVG illustration: a pelican riding a skateboard."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "output" / "pelican-skateboard.svg"

SVG = r'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="960" viewBox="0 0 1280 960" role="img" aria-labelledby="title desc">
  <title id="title">A pelican riding a skateboard</title>
  <desc id="desc">A happy white pelican wearing a teal helmet and coral scarf rides a red skateboard along a sunny seaside promenade.</desc>

  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#5db9e8"/>
      <stop offset=".48" stop-color="#a8e0e6"/>
      <stop offset=".78" stop-color="#fff0bd"/>
      <stop offset="1" stop-color="#ffd9a3"/>
    </linearGradient>
    <radialGradient id="sun" cx=".5" cy=".5" r=".5">
      <stop offset="0" stop-color="#fff8b0"/>
      <stop offset=".68" stop-color="#ffd94d"/>
      <stop offset="1" stop-color="#ffab3d"/>
    </radialGradient>
    <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#159bb4"/>
      <stop offset="1" stop-color="#62d2bd"/>
    </linearGradient>
    <linearGradient id="prom" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f7b267"/>
      <stop offset="1" stop-color="#e2704e"/>
    </linearGradient>
    <radialGradient id="bodyGrad" cx=".38" cy=".3" r=".9">
      <stop offset="0" stop-color="#ffffff"/>
      <stop offset=".62" stop-color="#f4fbff"/>
      <stop offset="1" stop-color="#d7e8ef"/>
    </radialGradient>
    <linearGradient id="wingGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#eef7fa"/>
      <stop offset="1" stop-color="#a9c8d8"/>
    </linearGradient>
    <linearGradient id="beakGrad" x1="0" y1="0" x2="1" y2=".35">
      <stop offset="0" stop-color="#ffc44d"/>
      <stop offset="1" stop-color="#ff7a2f"/>
    </linearGradient>
    <linearGradient id="pouchGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffb08a"/>
      <stop offset="1" stop-color="#ff6268"/>
    </linearGradient>
    <linearGradient id="deckGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ff6b5e"/>
      <stop offset="1" stop-color="#d92f45"/>
    </linearGradient>
    <linearGradient id="scarfGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ff5964"/>
      <stop offset="1" stop-color="#e73550"/>
    </linearGradient>
    <filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="7"/>
    </filter>
  </defs>

  <!-- ===== SKY ===== -->
  <rect width="1280" height="960" fill="url(#sky)"/>
  <circle cx="1060" cy="158" r="126" fill="#ffdf75" opacity=".34"/>
  <circle cx="1060" cy="158" r="88" fill="url(#sun)" stroke="#e98a2e" stroke-width="6"/>
  <g fill="#ffffff" opacity=".92">
    <g><ellipse cx="188" cy="128" rx="82" ry="30"/><ellipse cx="245" cy="112" rx="60" ry="38"/><ellipse cx="130" cy="112" rx="48" ry="25"/></g>
    <g opacity=".86"><ellipse cx="585" cy="102" rx="70" ry="24"/><ellipse cx="632" cy="88" rx="48" ry="30"/><ellipse cx="540" cy="90" rx="38" ry="20"/></g>
    <g opacity=".72"><ellipse cx="825" cy="300" rx="58" ry="18"/><ellipse cx="865" cy="288" rx="38" ry="23"/></g>
  </g>
  <!-- distant birds -->
  <g fill="none" stroke="#17465c" stroke-width="5" stroke-linecap="round" opacity=".75">
    <path d="M350 210 q18-16 36 0 q18-16 36 0"/>
    <path d="M438 252 q13-12 27 0 q13-12 27 0"/>
    <path d="M150 285 q12-11 25 0 q12-11 25 0"/>
  </g>

  <!-- title -->
  <g transform="rotate(-4 72 78)">
    <text x="70" y="88" font-family="'Trebuchet MS','Arial Rounded MT Bold',Arial,sans-serif" font-size="54" font-weight="900" letter-spacing="2" fill="#123c4d">SKATE DAY!</text>
    <path d="M72 108 Q215 124 362 104" fill="none" stroke="#ff5964" stroke-width="8" stroke-linecap="round"/>
  </g>

  <!-- ===== SEA & BEACH ===== -->
  <path d="M0 418 L1280 402 L1280 640 L0 660 Z" fill="url(#sea)"/>
  <g fill="none" stroke="#e9fffa" stroke-width="6" stroke-linecap="round" opacity=".72">
    <path d="M65 478 q35-18 70 0 t70 0"/><path d="M310 520 q35-18 70 0 t70 0"/>
    <path d="M770 470 q35-18 70 0 t70 0"/><path d="M1025 525 q35-18 70 0 t70 0"/>
    <path d="M120 575 q35-18 70 0 t70 0"/><path d="M945 590 q35-18 70 0 t70 0"/>
  </g>
  <!-- sailboat -->
  <g transform="translate(215 452)" stroke="#17323f" stroke-width="5" stroke-linejoin="round">
    <path d="M0 42 L92 42 L72 66 L16 66 Z" fill="#ff5964"/>
    <path d="M48 40 L48-48 L88 40 Z" fill="#fff7d6"/>
    <path d="M40 40 L40-28 L8 40 Z" fill="#ffffff"/>
  </g>
  <!-- sand -->
  <path d="M0 612 Q330 580 660 604 T1280 590 L1280 680 L0 700 Z" fill="#ffe0a1"/>
  <path d="M0 650 Q420 622 1280 622 L1280 680 L0 700 Z" fill="#ffd384" opacity=".65"/>

  <!-- ===== PROMENADE ===== -->
  <path d="M0 668 L1280 632 L1280 960 L0 960 Z" fill="url(#prom)"/>
  <g stroke="#b95438" stroke-width="5" opacity=".45" fill="none">
    <path d="M0 730 L1280 700"/><path d="M0 805 L1280 782"/><path d="M0 885 L1280 872"/>
    <path d="M210 672 L160 960"/><path d="M505 660 L500 960"/><path d="M815 648 L875 960"/><path d="M1080 640 L1190 960"/>
  </g>
  <g fill="#8f442e" opacity=".28">
    <ellipse cx="180" cy="900" rx="26" ry="6"/><ellipse cx="1090" cy="735" rx="20" ry="5"/><ellipse cx="1020" cy="915" rx="34" ry="7"/>
  </g>

  <!-- palms -->
  <g fill="none" stroke-linecap="round">
    <path d="M42 690 C70 540 92 410 128 292" stroke="#8a5a33" stroke-width="30"/>
    <path d="M42 690 C70 540 92 410 128 292" stroke="#b57a45" stroke-width="9" stroke-dasharray="4 34"/>
    <g stroke="#239267" stroke-width="17">
      <path d="M130 292 Q55 225 -28 245"/><path d="M130 292 Q90 195 8 165"/>
      <path d="M130 292 Q150 190 235 155"/><path d="M130 292 Q225 215 305 245"/>
      <path d="M130 292 Q205 275 275 320"/>
    </g>
    <circle cx="112" cy="306" r="22" fill="#7a4a26" stroke="#17323f" stroke-width="5"/>
  </g>
  <g fill="none" stroke-linecap="round" opacity=".96">
    <path d="M1218 650 C1200 540 1178 455 1142 382" stroke="#8a5a33" stroke-width="24"/>
    <g stroke="#239267" stroke-width="14">
      <path d="M1144 382 Q1075 315 995 332"/><path d="M1144 382 Q1115 292 1038 268"/>
      <path d="M1144 382 Q1175 292 1255 272"/><path d="M1144 382 Q1225 320 1295 338"/>
    </g>
  </g>

  <!-- wind / speed lines -->
  <g fill="none" stroke="#ffffff" stroke-width="9" stroke-linecap="round" opacity=".82">
    <path d="M72 540 H248"/><path d="M112 602 H292"/><path d="M62 742 H230"/>
  </g>
  <g fill="none" stroke="#1d7f91" stroke-width="7" stroke-linecap="round" opacity=".65">
    <path d="M95 575 H218"/><path d="M85 785 H205"/>
  </g>

  <!-- ground shadow -->
  <ellipse cx="665" cy="862" rx="365" ry="38" fill="#7c2d24" opacity=".25" filter="url(#soft)"/>

  <!-- ===== SKATEBOARD (under the feet) ===== -->
  <g transform="rotate(-2 665 795)">
    <!-- trucks -->
    <rect x="398" y="790" width="82" height="34" rx="9" fill="#8da3ad" stroke="#17323f" stroke-width="6"/>
    <rect x="842" y="790" width="82" height="34" rx="9" fill="#8da3ad" stroke="#17323f" stroke-width="6"/>
    <!-- wheels -->
    <g stroke="#17323f" stroke-width="6">
      <circle cx="439" cy="842" r="36" fill="#fff2cf"/>
      <circle cx="883" cy="842" r="36" fill="#fff2cf"/>
    </g>
    <g fill="none" stroke="#e8843c" stroke-width="6" stroke-linecap="round">
      <path d="M420 824 a26 26 0 0 1 34 8"/><path d="M864 824 a26 26 0 0 1 34 8"/>
    </g>
    <circle cx="439" cy="842" r="13" fill="#ff7a2f" stroke="#17323f" stroke-width="5"/>
    <circle cx="883" cy="842" r="13" fill="#ff7a2f" stroke="#17323f" stroke-width="5"/>
    <!-- deck -->
    <path d="M292 768 C278 742 308 726 362 724 L982 716 C1030 716 1058 740 1050 765 C1043 788 1002 796 948 797 L356 802 C316 802 300 790 292 768 Z" fill="url(#deckGrad)" stroke="#17323f" stroke-width="7" stroke-linejoin="round"/>
    <path d="M330 732 L968 724 C1002 724 1024 740 1030 754 L342 762 C324 750 318 738 330 732 Z" fill="#223a49"/>
    <path d="M318 782 L1028 774" stroke="#ffd93d" stroke-width="6" stroke-linecap="round"/>
    <text x="673" y="791" text-anchor="middle" font-family="'Trebuchet MS',Arial,sans-serif" font-size="19" font-weight="900" letter-spacing="3" fill="#ffffff">PELI · CAN DO IT!</text>
  </g>

  <!-- ===== PELICAN ===== -->
  <g stroke="#17323f" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">

    <!-- tail feathers -->
    <path d="M462 520 L292 448 L330 520 L276 548 L356 580 L312 628 L462 612 Z" fill="#2f4653"/>
    <path d="M430 535 L340 500 M435 570 L350 565" stroke="#d9edf3" stroke-width="5" fill="none"/>

    <!-- far leg + foot -->
    <path d="M565 662 C552 696 548 724 556 754" fill="none" stroke="#dd6428" stroke-width="21"/>
    <path d="M520 750 L622 744 L650 758 L620 766 L642 778 L590 780 L578 790 L552 774 L522 778 L510 762 Z" fill="#f0782e"/>

    <!-- body -->
    <path d="M428 562 C428 468 532 408 664 418 C792 428 862 498 848 586 C834 672 734 714 620 708 C508 702 428 654 428 562 Z" fill="url(#bodyGrad)"/>
    <!-- belly shading -->
    <path d="M500 650 C570 688 730 688 810 620 C770 690 650 724 545 692 C505 680 485 665 500 650 Z" fill="#cfe3ec" stroke="none" opacity=".8"/>

    <!-- near leg + webbed foot -->
    <path d="M672 676 C682 706 684 730 678 756" fill="none" stroke="#f0782e" stroke-width="23"/>
    <path d="M636 750 L742 742 L772 758 L738 768 L760 782 L706 782 L696 796 L664 778 L632 784 L622 764 Z" fill="#ff8a3d"/>

    <!-- neck -->
    <path d="M728 512 C770 442 782 360 798 276 C804 240 824 210 856 208 C890 206 908 238 896 280 C884 328 860 368 854 422 C848 468 862 508 844 538 C808 562 744 556 728 512 Z" fill="url(#bodyGrad)"/>

    <!-- scarf, flowing behind -->
    <path d="M754 492 C664 468 584 500 482 458 C520 512 586 522 500 548 C610 566 700 548 762 532 Z" fill="url(#scarfGrad)"/>
    <path d="M650 492 L628 532 M570 495 L550 526" stroke="#ffd3d8" stroke-width="9" fill="none"/>
    <!-- scarf band -->
    <path d="M742 474 C790 452 838 458 862 486 C850 522 830 540 800 544 C762 538 738 514 742 474 Z" fill="#e73550"/>
    <path d="M765 478 C785 520 810 536 838 508" fill="none" stroke="#ffb3ba" stroke-width="7"/>

    <!-- folded wing -->
    <path d="M486 516 C542 468 664 466 716 526 C756 572 734 646 660 676 C574 696 486 650 470 580 C464 550 470 530 486 516 Z" fill="url(#wingGrad)"/>
    <path d="M520 546 C576 514 656 526 680 576 C692 620 642 652 580 642 C530 632 504 582 520 546 Z" fill="#c9dde8"/>
    <g fill="none" stroke="#7199ad" stroke-width="5">
      <path d="M512 566 C570 540 640 548 676 586"/>
      <path d="M520 606 C572 584 632 590 662 618"/>
    </g>
    <!-- dark flight-feather tips -->
    <path d="M478 590 C505 640 548 668 592 678 L570 642 L600 668 C585 622 545 592 478 590 Z" fill="#2f4653"/>

    <!-- crest peeking from under helmet -->
    <path d="M800 178 L748 138 L766 188 L722 176 L764 216 Z" fill="#ffffff"/>

    <!-- head -->
    <ellipse cx="862" cy="216" rx="80" ry="63" transform="rotate(-8 862 216)" fill="url(#bodyGrad)"/>

    <!-- beak: pouch first, then upper beak -->
    <path d="M912 248 C1002 274 1108 280 1190 272 C1162 344 1082 380 1002 358 C944 342 912 296 912 248 Z" fill="url(#pouchGrad)"/>
    <path d="M946 286 C1012 322 1092 322 1150 288" fill="none" stroke="#d84a3f" stroke-width="5" opacity=".65"/>
    <path d="M902 188 C998 198 1108 234 1200 276 C1112 298 994 286 908 256 C892 234 892 208 902 188 Z" fill="url(#beakGrad)"/>
    <path d="M1180 256 L1214 282 L1178 294 Z" fill="#d95d20"/>
    <path d="M922 214 C1012 224 1102 250 1168 272" fill="none" stroke="#d95d20" stroke-width="5" opacity=".6"/>

    <!-- face -->
    <circle cx="878" cy="218" r="12" fill="#17323f" stroke="none"/>
    <circle cx="882" cy="213" r="4" fill="#ffffff" stroke="none"/>
    <circle cx="842" cy="250" r="15" fill="#ff9d9d" stroke="none" opacity=".65"/>
    <path d="M898 242 q14 10 28 6" fill="none" stroke="#d95d20" stroke-width="5"/>

    <!-- helmet -->
    <path d="M780 200 A84 72 0 0 1 944 188 L946 204 Q864 222 778 216 Z" fill="#12a5a5"/>
    <path d="M824 140 A84 72 0 0 1 902 146 L890 204 L842 208 Z" fill="#ffd93d" stroke="none" opacity=".95"/>
    <rect x="766" y="198" width="192" height="20" rx="10" fill="#0b747c"/>
    <circle cx="862" cy="132" r="10" fill="#ff5964"/>
    <path d="M918 214 C912 238 908 252 900 268" fill="none" stroke="#17323f" stroke-width="6"/>
    <rect x="888" y="264" width="24" height="16" rx="4" fill="#ffd93d"/>
  </g>

  <!-- sparkles -->
  <g fill="#ffd93d" stroke="#17323f" stroke-width="4" stroke-linejoin="round">
    <path d="M1012 408 l9 24 24 9-24 9-9 24-9-24-24-9 24-9z"/>
    <path d="M250 350 l7 19 19 7-19 7-7 19-7-19-19-7 19-7z"/>
    <path d="M1085 650 l7 19 19 7-19 7-7 19-7-19-19-7 19-7z"/>
  </g>
  <circle cx="365" cy="365" r="7" fill="#ff5964"/>
  <circle cx="1135" cy="455" r="8" fill="#12a5a5"/>
  <circle cx="205" cy="455" r="6" fill="#ffd93d"/>

  <!-- foreground grass + shells -->
  <g fill="none" stroke="#187a4d" stroke-width="7" stroke-linecap="round">
    <path d="M62 942 C58 910 48 892 30 878 M72 942 C76 908 88 890 108 876 M84 942 C92 920 108 908 128 904"/>
    <path d="M1150 942 C1146 912 1136 896 1120 884 M1164 942 C1170 910 1182 894 1200 882 M1180 942 C1190 922 1204 912 1222 908"/>
  </g>
  <g stroke="#17323f" stroke-width="4">
    <path d="M150 842 a20 14 0 0 1 40 0 Z" fill="#fff1f2"/>
    <circle cx="1118" cy="858" r="12" fill="#ffe3ec"/>
  </g>

  <!-- poster frame -->
  <rect x="18" y="18" width="1244" height="924" rx="30" fill="none" stroke="#ffffff" stroke-width="5" opacity=".65"/>
</svg>
'''

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(SVG, encoding="utf-8")
print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
