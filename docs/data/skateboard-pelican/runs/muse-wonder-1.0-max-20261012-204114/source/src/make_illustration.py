#!/usr/bin/env python3
"""Generate 'Pelican Riding a Skateboard' — a hand-built SVG illustration.

Style: bold flat coastal poster, deep-navy outlines, sunset seaside
promenade. The pelican faces right, carving on a red skateboard, one
wing swept back for balance, teal backwards cap, sunglasses, and a
coral scarf streaming behind it.

Output: ./output/pelican-skateboard.svg
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "output" / "pelican-skateboard.svg"

SVG = r"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="1200" height="900"
     role="img" aria-labelledby="title desc">
  <title id="title">A pelican riding a skateboard</title>
  <desc id="desc">A cheerful white pelican wearing sunglasses and a teal backwards cap rides a red skateboard along a sunny seaside promenade, wing swept back for balance, long orange beak and pouch forward, palm trees and ocean behind.</desc>

  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#6fd3f2"/>
      <stop offset=".55" stop-color="#aee9f7"/>
      <stop offset="1" stop-color="#ffedbe"/>
    </linearGradient>
    <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#159bb5"/>
      <stop offset="1" stop-color="#0b6e91"/>
    </linearGradient>
    <linearGradient id="sun" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffe066"/>
      <stop offset="1" stop-color="#ffb340"/>
    </linearGradient>
    <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffd9a0"/>
      <stop offset="1" stop-color="#f7b267"/>
    </linearGradient>
    <linearGradient id="beak" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#ffb347"/>
      <stop offset="1" stop-color="#ff7b3d"/>
    </linearGradient>
    <linearGradient id="pouch" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffc49b"/>
      <stop offset="1" stop-color="#ff8f6b"/>
    </linearGradient>
    <linearGradient id="deck" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ff5d73"/>
      <stop offset="1" stop-color="#e53855"/>
    </linearGradient>
    <linearGradient id="wingShade" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#ffffff"/>
      <stop offset="1" stop-color="#dbe9f2"/>
    </linearGradient>
    <pattern id="dots" width="46" height="46" patternUnits="userSpaceOnUse">
      <circle cx="8" cy="8" r="3" fill="#ffffff" opacity=".28"/>
    </pattern>
    <clipPath id="canvas"><rect width="1200" height="900"/></clipPath>
  </defs>

  <g clip-path="url(#canvas)">
    <!-- ======================= SKY ======================= -->
    <rect width="1200" height="900" fill="url(#sky)"/>
    <rect width="1200" height="560" fill="url(#dots)"/>

    <!-- sun + rays -->
    <g opacity=".9">
      <g fill="#ffd166" opacity=".45">
        <path d="M920 38 L946 118 L894 118 Z"/>
        <path d="M1048 92 L1002 158 L966 122 Z"/>
        <path d="M792 92 L838 158 L874 122 Z"/>
        <path d="M1075 215 L995 222 L1002 178 Z"/>
        <path d="M765 215 L845 222 L838 178 Z"/>
      </g>
      <circle cx="920" cy="205" r="112" fill="url(#sun)" stroke="#143642" stroke-width="6"/>
      <circle cx="920" cy="205" r="86" fill="none" stroke="#ffcf4d" stroke-width="4" opacity=".7"/>
    </g>

    <!-- clouds -->
    <g fill="#ffffff" stroke="#143642" stroke-width="5" stroke-linejoin="round">
      <path d="M92 168 a42 42 0 0 1 40-42 a54 54 0 0 1 100-14 a40 40 0 0 1 52 38 a28 28 0 0 1-8 48 H112 a30 30 0 0 1-20-30Z"/>
      <path d="M1018 388 a30 30 0 0 1 28-30 a40 40 0 0 1 74-8 a30 30 0 0 1 38 28 a20 20 0 0 1-6 34 h-118 a22 22 0 0 1-16-24Z" opacity=".95"/>
      <path d="M356 108 a26 26 0 0 1 24-26 a36 36 0 0 1 64-8 a26 26 0 0 1 34 24 a18 18 0 0 1-5 30 H372 a20 20 0 0 1-16-20Z" opacity=".9"/>
    </g>

    <!-- distant birds -->
    <g fill="none" stroke="#143642" stroke-width="5" stroke-linecap="round" opacity=".75">
      <path d="M222 268 q18-16 36 0 q18-16 36 0"/>
      <path d="M292 306 q12-11 24 0 q12-11 24 0"/>
      <path d="M1062 300 q13-12 26 0 q13-12 26 0"/>
    </g>

    <!-- ======================= SEA ======================= -->
    <rect x="0" y="478" width="1200" height="150" fill="url(#sea)"/>
    <rect x="0" y="478" width="1200" height="8" fill="#e8fbff" opacity=".8"/>
    <g fill="none" stroke="#bff3ff" stroke-width="6" stroke-linecap="round" opacity=".8">
      <path d="M40 528 q30-14 60 0 t60 0 t60 0"/>
      <path d="M880 540 q30-14 60 0 t60 0 t60 0"/>
      <path d="M150 578 q26-12 52 0 t52 0"/>
      <path d="M960 592 q26-12 52 0 t52 0"/>
      <path d="M620 520 q24-11 48 0 t48 0"/>
    </g>
    <!-- tiny sailboat -->
    <g stroke="#143642" stroke-width="4" stroke-linejoin="round">
      <path d="M118 452 L118 398 L158 452 Z" fill="#ffffff"/>
      <path d="M126 452 L168 420 L168 452 Z" fill="#ffd166"/>
      <path d="M98 452 h92 l-14 20 h-62 Z" fill="#e53855"/>
    </g>

    <!-- ======================= PROMENADE ======================= -->
    <path d="M0 628 L1200 628 L1200 900 L0 900 Z" fill="url(#ground)"/>
    <path d="M0 628 L1200 628 L1200 650 L0 650 Z" fill="#fff1cf"/>
    <g stroke="#d98d4e" stroke-width="4" opacity=".55">
      <path d="M0 700 L1200 692"/>
      <path d="M0 782 L1200 778"/>
      <path d="M140 650 L60 900 M420 650 L400 900 M720 650 L760 900 M1010 650 L1120 900"/>
    </g>
    <g fill="#e8935a" opacity=".6">
      <ellipse cx="180" cy="742" rx="16" ry="5"/><ellipse cx="1035" cy="742" rx="20" ry="6"/>
      <ellipse cx="950" cy="842" rx="16" ry="5"/><ellipse cx="120" cy="842" rx="22" ry="6"/>
    </g>

    <!-- palm trees -->
    <g stroke-linecap="round" stroke-linejoin="round">
      <!-- left palm -->
      <path d="M118 640 C130 540 126 470 96 402" fill="none" stroke="#8a5a33" stroke-width="26"/>
      <path d="M118 640 C130 540 126 470 96 402" fill="none" stroke="#143642" stroke-width="30" opacity="0" />
      <g fill="none" stroke="#15945f" stroke-width="15">
        <path d="M96 402 C50 360 8 352-28 372"/>
        <path d="M96 402 C66 344 22 318-22 322"/>
        <path d="M96 402 C96 338 122 300 164 282"/>
        <path d="M96 402 C140 356 190 348 232 366"/>
        <path d="M96 402 C132 380 176 386 208 410"/>
      </g>
      <circle cx="84" cy="414" r="15" fill="#8a5a33" stroke="#143642" stroke-width="4"/>
      <circle cx="110" cy="420" r="13" fill="#8a5a33" stroke="#143642" stroke-width="4"/>
      <!-- right palm (behind sun side, smaller) -->
      <path d="M1128 632 C1118 556 1122 500 1148 448" fill="none" stroke="#8a5a33" stroke-width="20"/>
      <g fill="none" stroke="#15945f" stroke-width="12">
        <path d="M1148 448 C1112 410 1072 402 1038 418"/>
        <path d="M1148 448 C1148 396 1170 366 1204 350"/>
        <path d="M1148 448 C1184 412 1224 404 1256 420"/>
        <path d="M1148 448 C1118 424 1080 424 1052 442"/>
      </g>
    </g>

    <!-- ======================= MOTION / SHADOW ======================= -->
    <ellipse cx="612" cy="806" rx="350" ry="30" fill="#143642" opacity=".18"/>
    <ellipse cx="612" cy="806" rx="230" ry="18" fill="#143642" opacity=".14"/>
    <g stroke="#ffffff" stroke-width="11" stroke-linecap="round" opacity=".9">
      <path d="M62 486 H224"/><path d="M30 548 H196"/><path d="M84 610 H238"/>
    </g>
    <g stroke="#19a7bd" stroke-width="8" stroke-linecap="round" opacity=".65">
      <path d="M96 518 H230"/><path d="M58 580 H206"/>
    </g>

    <!-- ======================= SKATEBOARD ======================= -->
    <g transform="rotate(-5 610 742)">
      <!-- wheels (drawn first, behind deck) -->
      <g stroke="#143642" stroke-width="6">
        <circle cx="438" cy="772" r="36" fill="#ffd166"/>
        <circle cx="792" cy="772" r="36" fill="#ffd166"/>
        <circle cx="438" cy="772" r="15" fill="#143642"/>
        <circle cx="792" cy="772" r="15" fill="#143642"/>
      </g>
      <g stroke="#fff3c4" stroke-width="5" stroke-linecap="round">
        <path d="M438 748 v-14 M420 786 l-10 10 M456 786 l10 10"/>
        <path d="M792 748 v-14 M774 786 l-10 10 M810 786 l10 10"/>
      </g>
      <!-- trucks -->
      <g fill="#9fb6c3" stroke="#143642" stroke-width="5">
        <rect x="416" y="742" width="44" height="18" rx="5"/>
        <rect x="770" y="742" width="44" height="18" rx="5"/>
      </g>
      <!-- deck -->
      <path d="M322 716 C330 700 366 696 420 700 L812 700 C868 700 902 706 908 724 C912 738 896 750 852 752 L386 756 C338 756 314 738 322 716Z"
            fill="url(#deck)" stroke="#143642" stroke-width="6" stroke-linejoin="round"/>
      <path d="M338 716 C420 706 760 706 890 720" fill="none" stroke="#ffe3e8" stroke-width="7" stroke-linecap="round" opacity=".8"/>
      <path d="M470 712 L760 712" stroke="#143642" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 18" opacity=".55"/>
      <!-- lightning bolt on deck -->
      <path d="M612 706 L574 736 L606 736 L580 750 L646 720 L612 720 Z" fill="#ffd166" stroke="#143642" stroke-width="4" stroke-linejoin="round"/>
    </g>

    <!-- dust puffs at wheels -->
    <g fill="#ffffff" stroke="#143642" stroke-width="4" opacity=".92">
      <circle cx="352" cy="782" r="18"/><circle cx="322" cy="792" r="13"/><circle cx="380" cy="794" r="11"/>
    </g>

    <!-- ======================= PELICAN ======================= -->
    <g stroke-linejoin="round" stroke-linecap="round">

      <!-- far leg (darker, behind body) -->
      <path d="M512 566 C492 616 478 664 486 716" fill="none" stroke="#e56f2e" stroke-width="17"/>
      <path d="M452 720 C470 708 512 708 526 718 C512 730 472 734 452 720Z" fill="#f5833c" stroke="#143642" stroke-width="5"/>

      <!-- far wing peeking above body -->
      <path d="M596 344 C620 278 676 232 742 224 C706 272 682 318 676 368 C650 352 622 350 596 344Z"
            fill="#c9dbe8" stroke="#143642" stroke-width="6"/>

      <!-- tail feathers -->
      <g stroke="#143642" stroke-width="6">
        <path d="M398 452 L272 398 L322 478 L258 486 L346 536 L330 574 L414 540 C398 512 394 482 398 452Z" fill="#ffffff"/>
        <path d="M356 500 L282 486 L346 536 L330 574 L386 548" fill="#2e3d4d"/>
      </g>

      <!-- swept-back near wing (behind body, for balance) -->
      <g stroke="#143642" stroke-width="6">
        <path d="M520 392 C430 306 306 262 176 282 C238 322 276 356 306 398 L196 386 C262 428 330 470 412 486 C462 494 514 452 520 392Z"
              fill="url(#wingShade)"/>
        <path d="M306 398 L196 386 C240 414 282 438 326 454 L288 408Z" fill="#2e3d4d"/>
        <path d="M250 342 C320 372 400 418 452 462" fill="none" stroke="#9db9c9" stroke-width="5"/>
      </g>

      <!-- body -->
      <path d="M386 478 C382 388 462 306 584 304 C700 302 778 376 774 482 C770 580 680 646 562 640 C460 635 390 572 386 478Z"
            fill="#ffffff" stroke="#143642" stroke-width="7"/>
      <!-- belly shading -->
      <path d="M430 548 C500 606 650 606 724 520 C700 596 620 640 540 632 C486 626 446 592 430 548Z" fill="#e6f0f6"/>
      <g fill="none" stroke="#b8cfdd" stroke-width="5">
        <path d="M452 420 C500 392 580 386 640 404"/>
        <path d="M440 466 C492 438 584 432 650 452"/>
      </g>

      <!-- neck: dark under-stroke then white over-stroke = clean outline -->
      <path d="M648 452 C700 376 706 300 770 248" fill="none" stroke="#143642" stroke-width="92"/>
      <path d="M648 452 C700 376 706 300 770 248" fill="none" stroke="#ffffff" stroke-width="76"/>
      <!-- neck shading -->
      <path d="M700 360 C716 322 732 292 756 268" fill="none" stroke="#dbe9f2" stroke-width="12" opacity=".9"/>

      <!-- scarf (around neck base, streaming left) -->
      <g stroke="#143642" stroke-width="6">
        <path d="M652 402 C580 372 500 376 428 410 C472 424 492 438 470 462 C540 452 614 452 668 438 Z" fill="#ef476f"/>
        <path d="M428 410 C472 424 492 438 470 462 C448 452 424 434 428 410Z" fill="#d90429" stroke="none" opacity=".35"/>
        <path d="M618 388 C650 382 676 396 682 420 C684 444 664 462 638 460 C614 458 600 436 604 416 C606 402 610 392 618 388Z" fill="#ef476f"/>
      </g>
      <path d="M632 402 L624 448" stroke="#ffffff" stroke-width="5" opacity=".7"/>

      <!-- head -->
      <g transform="rotate(-8 790 238)">
        <ellipse cx="790" cy="238" rx="66" ry="54" fill="#ffffff" stroke="#143642" stroke-width="7"/>
      </g>
      <!-- crest feathers -->
      <path d="M742 200 L690 168 L716 214 L668 204 L724 246" fill="#ffffff" stroke="#143642" stroke-width="6"/>

      <!-- beak + pouch -->
      <g stroke="#143642" stroke-width="6">
        <!-- pouch (under beak, sagging) -->
        <path d="M838 258 L1032 322 C1010 382 934 408 876 376 C838 355 824 306 838 258Z" fill="url(#pouch)"/>
        <!-- pouch crease + little fish tail peeking out -->
        <path d="M866 292 C910 340 962 356 1004 338" fill="none" stroke="#e56f2e" stroke-width="5"/>
        <path d="M934 366 l26-22 -4 30 24 8 -30 10 -10-18Z" fill="#19a7bd"/>
        <!-- upper beak -->
        <path d="M836 214 L1078 296 C1100 304 1102 318 1086 326 C1068 335 1034 330 1004 320 L842 268 C826 250 826 228 836 214Z" fill="url(#beak)"/>
      </g>
      <path d="M856 230 L1048 296" stroke="#ffe1ae" stroke-width="7" stroke-linecap="round"/>
      <!-- hooked tip + nostril line -->
      <path d="M1078 296 C1096 306 1094 326 1076 334" fill="none" stroke="#143642" stroke-width="6"/>
      <circle cx="872" cy="238" r="5" fill="#143642"/>

      <!-- sunglasses -->
      <g stroke="#143642">
        <path d="M846 226 L896 240" fill="none" stroke-width="7"/>
        <circle cx="812" cy="232" r="27" fill="#143642"/>
        <circle cx="812" cy="232" r="27" fill="none" stroke-width="5"/>
        <path d="M796 218 a22 22 0 0 1 14-8" fill="none" stroke="#ffffff" stroke-width="6"/>
      </g>

      <!-- backwards cap -->
      <g stroke="#143642" stroke-width="6">
        <path d="M726 226 C724 178 762 148 806 152 C846 156 868 184 864 220 L846 226 C820 204 766 202 740 230 Z" fill="#00a896"/>
        <path d="M726 226 L656 240 C640 244 636 230 650 220 L716 196 Z" fill="#008f7d"/>
        <circle cx="798" cy="152" r="10" fill="#ffd166"/>
      </g>
      <path d="M756 176 C776 162 812 162 834 178" fill="none" stroke="#ffffff" stroke-width="5" opacity=".65"/>

      <!-- near leg + webbed foot on the deck -->
      <path d="M618 606 C632 646 638 678 632 714" fill="none" stroke="#ff8c42" stroke-width="19"/>
      <g fill="#ff8c42" stroke="#143642" stroke-width="5">
        <path d="M588 722 C606 706 660 704 682 716 C668 732 660 734 636 732 L662 744 C636 750 596 744 582 734 Z"/>
      </g>

      <!-- near wing folded over body (small, resting) -->
      <g stroke="#143642" stroke-width="6">
        <path d="M486 386 C566 356 660 386 678 458 C692 516 646 570 576 574 C506 578 452 522 456 456 C458 424 468 398 486 386Z" fill="url(#wingShade)"/>
        <path d="M560 540 C600 548 642 528 660 492 C664 536 628 570 576 574 C540 576 508 562 486 538 C510 542 534 542 560 540Z" fill="#2e3d4d"/>
      </g>
      <g fill="none" stroke="#9db9c9" stroke-width="5">
        <path d="M500 428 C548 402 616 404 652 432"/>
        <path d="M496 474 C544 448 614 450 650 476"/>
      </g>
    </g>

    <!-- ======================= FOREGROUND SPARKLE ======================= -->
    <g fill="#ffffff" stroke="#143642" stroke-width="4" stroke-linejoin="round">
      <path d="M986 452 l7 18 18 7-18 7-7 18-7-18-18-7 18-7Z"/>
      <path d="M238 640 l5 13 13 5-13 5-5 13-5-13-13-5 13-5Z"/>
      <path d="M1058 610 l5 13 13 5-13 5-5 13-5-13-13-5 13-5Z" fill="#ffd166"/>
    </g>
    <!-- foreground grass tufts -->
    <g fill="none" stroke="#15945f" stroke-width="6" stroke-linecap="round">
      <path d="M64 884 C60 862 52 848 38 838 M64 884 C66 860 74 844 88 834 M64 884 C64 866 64 852 64 840"/>
      <path d="M1136 878 C1132 856 1124 842 1110 832 M1136 878 C1138 854 1146 838 1160 828"/>
    </g>
  </g>
</svg>
"""

def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(SVG, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size/1024:.1f} KiB)")

if __name__ == "__main__":
    main()
