#!/usr/bin/env python3
"""Generate an SVG illustration: octopus chef at a ramen booth."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "output" / "octopus-chef-ramen-booth.svg"

SVG = r'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="1200" height="900">
  <title>Octopus Chef at a Ramen Booth</title>
  <desc>A cheerful octopus chef with eight arms multitasking at a cozy ramen-ya booth.</desc>

  <defs>
    <linearGradient id="wallGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FFF3D6"/>
      <stop offset="68%" stop-color="#FFE7B5"/>
      <stop offset="100%" stop-color="#FFD9A0"/>
    </linearGradient>
    <linearGradient id="woodGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#A8642E"/>
      <stop offset="100%" stop-color="#7A3E1A"/>
    </linearGradient>
    <linearGradient id="woodTop" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#D99A52"/>
      <stop offset="100%" stop-color="#B87433"/>
    </linearGradient>
    <linearGradient id="octoGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#C084FC"/>
      <stop offset="52%" stop-color="#9D5FE8"/>
      <stop offset="100%" stop-color="#7C3ED1"/>
    </linearGradient>
    <linearGradient id="octoBelly" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#F1D6FF"/>
      <stop offset="100%" stop-color="#DDB6FA"/>
    </linearGradient>
    <radialGradient id="lanternGlow" cx="50%" cy="45%" r="55%">
      <stop offset="0%" stop-color="#FFF7C2"/>
      <stop offset="60%" stop-color="#FFE27A"/>
      <stop offset="100%" stop-color="#FFB43A" stop-opacity=".85"/>
    </radialGradient>
    <radialGradient id="brothGrad" cx="50%" cy="42%" r="62%">
      <stop offset="0%" stop-color="#FFE28A"/>
      <stop offset="68%" stop-color="#F6B73C"/>
      <stop offset="100%" stop-color="#D98A1F"/>
    </radialGradient>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="160%">
      <feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="#4A1E00" flood-opacity="0.18"/>
    </filter>
    <!-- noodle wiggle reused in the big bowl -->
    <path id="noodle" d="M-145 0 q18-14 36 0 t36 0 t36 0 t36 0 t36 0 t36 0 t36 0" fill="none" stroke="#FFF0A8" stroke-width="7" stroke-linecap="round"/>
  </defs>

  <!-- ===== BACKGROUND WALL ===== -->
  <rect width="1200" height="900" fill="url(#wallGrad)"/>
  <!-- faint sun-disc -->
  <circle cx="600" cy="375" r="235" fill="#FF9E4A" opacity=".16"/>
  <circle cx="600" cy="375" r="195" fill="#FF9E4A" opacity=".13"/>

  <!-- paper texture dots -->
  <g fill="#B87433" opacity=".07">
    <circle cx="90" cy="160" r="5"/><circle cx="220" cy="90" r="4"/><circle cx="1050" cy="130" r="5"/>
    <circle cx="980" cy="300" r="4"/><circle cx="150" cy="390" r="4"/><circle cx="1080" cy="460" r="5"/>
  </g>

  <!-- ===== HANGING SIGN ===== -->
  <g filter="url(#softShadow)">
    <line x1="600" y1="0" x2="600" y2="26" stroke="#7A3E1A" stroke-width="5"/>
    <rect x="418" y="26" width="364" height="74" rx="16" fill="#1E3A5F"/>
    <rect x="430" y="38" width="340" height="50" rx="10" fill="none" stroke="#F7D08A" stroke-width="2.5" stroke-dasharray="7 6"/>
    <text x="600" y="76" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="34" font-weight="700" letter-spacing="8" fill="#FFE9B8">RAMEN-YA</text>
  </g>

  <!-- ===== LANTERNS ===== -->
  <g stroke="#7A3E1A" stroke-width="3">
    <line x1="145" y1="0" x2="145" y2="58"/><line x1="1055" y1="0" x2="1055" y2="58"/>
  </g>
  <g filter="url(#softShadow)">
    <ellipse cx="145" cy="128" rx="72" ry="70" fill="url(#lanternGlow)"/>
    <path d="M76 103 Q145 88 214 103 M76 153 Q145 168 214 153" fill="none" stroke="#E8890C" stroke-width="3" opacity=".7"/>
    <rect x="118" y="52" width="54" height="14" rx="5" fill="#2B2118"/><rect x="118" y="192" width="54" height="14" rx="5" fill="#2B2118"/>
    <text x="145" y="145" text-anchor="middle" font-family="Georgia, serif" font-size="38" font-weight="700" fill="#C62828">ら</text>
  </g>
  <g filter="url(#softShadow)">
    <ellipse cx="1055" cy="128" rx="72" ry="70" fill="url(#lanternGlow)"/>
    <path d="M986 103 Q1055 88 1124 103 M986 153 Q1055 168 1124 153" fill="none" stroke="#E8890C" stroke-width="3" opacity=".7"/>
    <rect x="1028" y="52" width="54" height="14" rx="5" fill="#2B2118"/><rect x="1028" y="192" width="54" height="14" rx="5" fill="#2B2118"/>
    <text x="1055" y="145" text-anchor="middle" font-family="Georgia, serif" font-size="38" font-weight="700" fill="#C62828">麺</text>
  </g>

  <!-- ===== NOREN CURTAIN (behind chef) ===== -->
  <g>
    <rect x="250" y="118" width="700" height="16" rx="8" fill="#7A3E1A"/>
    <g filter="url(#softShadow)">
      <path d="M265 134 h142 v142 q-35 16-71 0 q-36 16-71 0 Z" fill="#C0392B"/>
      <path d="M422 134 h156 v142 q-39 16-78 0 q-39 16-78 0 Z" fill="#C0392B"/>
      <path d="M593 134 h142 v142 q-35 16-71 0 q-36 16-71 0 Z" fill="#C0392B"/>
      <path d="M750 134 h185 v142 q-46 16-92 0 q-47 16-93 0 Z" fill="#C0392B"/>
    </g>
    <g fill="#FFF3D6" font-family="Georgia, serif" font-weight="700" text-anchor="middle">
      <text x="336" y="216" font-size="40">た</text>
      <text x="500" y="216" font-size="40">こ</text>
      <text x="664" y="216" font-size="40">や</text>
      <text x="842" y="216" font-size="40">き</text>
    </g>
    <g stroke="#8E2323" stroke-width="2" opacity=".5">
      <line x1="407" y1="134" x2="407" y2="266"/><line x1="578" y1="134" x2="578" y2="266"/><line x1="735" y1="134" x2="735" y2="266"/>
    </g>
  </g>

  <!-- menu board (left) -->
  <g transform="rotate(-3 312 330)" filter="url(#softShadow)">
    <rect x="248" y="292" width="128" height="104" rx="10" fill="#FFF8E8" stroke="#7A3E1A" stroke-width="3"/>
    <text x="312" y="320" text-anchor="middle" font-family="Georgia, serif" font-size="15" font-weight="700" fill="#7A3E1A">— MENU —</text>
    <g font-family="Georgia, serif" font-size="14" fill="#4A2C14">
      <text x="262" y="346">• shoyu</text><text x="262" y="368">• miso</text><text x="262" y="390">• spicy ✦</text>
    </g>
  </g>
  <!-- specials board (right) -->
  <g transform="rotate(3 890 330)" filter="url(#softShadow)">
    <rect x="824" y="292" width="132" height="104" rx="10" fill="#1E3A5F"/>
    <text x="890" y="322" text-anchor="middle" font-family="Georgia, serif" font-size="14" font-weight="700" letter-spacing="2" fill="#F7D08A">TODAY</text>
    <text x="890" y="350" text-anchor="middle" font-family="Georgia, serif" font-size="15" fill="#FFF3D6">octo tonkotsu</text>
    <text x="890" y="376" text-anchor="middle" font-family="Georgia, serif" font-size="13" fill="#F7D08A">8 arms · 0 wait!</text>
  </g>

  <!-- ===== STOCK POT (left of chef) ===== -->
  <g filter="url(#softShadow)">
    <ellipse cx="352" cy="492" rx="92" ry="18" fill="#3A3A44"/>
    <path d="M262 470 h180 l-14 92 a18 18 0 0 1-18 15 h-116 a18 18 0 0 1-18-15 Z" fill="#4A4A56"/>
    <path d="M262 470 h180 l-5 34 H267 Z" fill="#62626E"/>
    <ellipse cx="352" cy="470" rx="90" ry="17" fill="#7A7A88"/>
    <ellipse cx="352" cy="469" rx="76" ry="13" fill="#F6B73C"/>
    <ellipse cx="330" cy="466" rx="20" ry="5" fill="#FFF0A8" opacity=".8"/>
    <circle cx="382" cy="472" r="5" fill="#FFF0A8" opacity=".7"/>
    <rect x="238" y="488" width="26" height="12" rx="6" fill="#2E2E36"/><rect x="440" y="488" width="26" height="12" rx="6" fill="#2E2E36"/>
  </g>
  <!-- pot steam -->
  <g fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round" opacity=".75">
    <path d="M318 448 q-12-22 0-40 q12-18 0-36"/><path d="M352 452 q-12-22 0-40 q12-18 0-36"/><path d="M386 448 q-12-22 0-40 q12-18 0-36"/>
  </g>

  <!-- ===== OCTOPUS CHEF ===== -->
  <!-- back tentacles -->
  <g fill="none" stroke="#7C3ED1" stroke-linecap="round">
    <path d="M512 512 C440 500 398 452 404 396" stroke-width="30"/>
    <path d="M688 512 C760 500 802 452 796 396" stroke-width="30"/>
    <path d="M500 548 C420 560 368 530 356 478" stroke-width="28"/>
    <path d="M700 548 C780 560 832 530 844 478" stroke-width="28"/>
  </g>
  <g fill="none" stroke="#9D5FE8" stroke-linecap="round">
    <path d="M520 528 C452 528 404 566 398 612" stroke-width="28"/>
    <path d="M680 528 C748 528 796 566 802 612" stroke-width="28"/>
    <path d="M548 556 C500 592 452 596 416 578" stroke-width="26"/>
    <path d="M652 556 C700 592 748 596 784 578" stroke-width="26"/>
  </g>
  <!-- suckers on back arms -->
  <g fill="#E9D5FF">
    <circle cx="424" cy="430" r="7"/><circle cx="440" cy="472" r="7"/><circle cx="776" cy="430" r="7"/><circle cx="760" cy="472" r="7"/>
    <circle cx="386" cy="500" r="6"/><circle cx="814" cy="500" r="6"/><circle cx="424" cy="596" r="6"/><circle cx="776" cy="596" r="6"/>
  </g>

  <!-- head / mantle -->
  <g filter="url(#softShadow)">
    <path d="M600 268 C492 268 452 348 456 430 C459 492 502 544 600 544 C698 544 741 492 744 430 C748 348 708 268 600 268 Z" fill="url(#octoGrad)"/>
    <ellipse cx="600" cy="478" rx="92" ry="58" fill="url(#octoBelly)" opacity=".92"/>
  </g>
  <!-- head spots -->
  <g fill="#FFFFFF" opacity=".28">
    <circle cx="508" cy="330" r="10"/><circle cx="536" cy="306" r="6"/><circle cx="692" cy="330" r="10"/><circle cx="664" cy="306" r="6"/>
  </g>

  <!-- chef hat -->
  <g filter="url(#softShadow)">
    <path d="M514 286 C492 238 522 196 562 202 C574 182 626 182 638 202 C678 196 708 238 686 286 Z" fill="#FFFFFF"/>
    <path d="M514 286 h172 v22 a10 10 0 0 1-10 10 H524 a10 10 0 0 1-10-10 Z" fill="#F1F5F9"/>
    <path d="M540 218 q10 28 0 62 M600 206 v78 M660 218 q-10 28 0 62" fill="none" stroke="#E2E8F0" stroke-width="4"/>
    <rect x="514" y="284" width="172" height="7" fill="#E11D48"/>
  </g>
  <!-- hachimaki band -->
  <path d="M470 356 q130-30 260 0 l-4 24 q-126-26-252 0 Z" fill="#1E3A5F"/>
  <circle cx="600" cy="366" r="11" fill="#FFFFFF"/><circle cx="600" cy="366" r="6" fill="#E11D48"/>
  <path d="M726 356 l42-14 -6 22 18 8-46 12 Z" fill="#1E3A5F"/>

  <!-- face -->
  <g>
    <ellipse cx="548" cy="420" rx="26" ry="30" fill="#1E1433"/><ellipse cx="652" cy="420" rx="26" ry="30" fill="#1E1433"/>
    <circle cx="557" cy="410" r="9" fill="#fff"/><circle cx="661" cy="410" r="9" fill="#fff"/>
    <circle cx="543" cy="432" r="4" fill="#fff" opacity=".9"/><circle cx="647" cy="432" r="4" fill="#fff" opacity=".9"/>
    <!-- blush -->
    <ellipse cx="498" cy="458" rx="20" ry="11" fill="#F9A8D4" opacity=".85"/><ellipse cx="702" cy="458" rx="20" ry="11" fill="#F9A8D4" opacity=".85"/>
    <!-- happy open smile -->
    <path d="M572 462 q28 24 56 0 q-4 26-28 26 q-24 0-28-26 Z" fill="#4A1030"/>
    <path d="M584 480 q16 8 32 0 q-6 10-16 10 q-10 0-16-10 Z" fill="#F472B6"/>
    <!-- raised brows -->
    <path d="M524 382 q24-12 48-2 M628 380 q24-10 48 2" fill="none" stroke="#4C1D95" stroke-width="6" stroke-linecap="round"/>
  </g>

  <!-- apron -->
  <g filter="url(#softShadow)">
    <path d="M536 520 h128 l16 96 a14 14 0 0 1-14 16 H534 a14 14 0 0 1-14-16 Z" fill="#FFFFFF"/>
    <path d="M536 520 h128 l3 20 H533 Z" fill="#E11D48"/>
    <text x="600" y="592" text-anchor="middle" font-family="Georgia, serif" font-size="30" font-weight="700" fill="#C0392B">匠</text>
  </g>

  <!-- front arms + props -->
  <!-- arm L1: ladle over pot -->
  <path d="M486 470 C436 452 396 462 366 440" fill="none" stroke="#9D5FE8" stroke-width="28" stroke-linecap="round"/>
  <g transform="rotate(-28 366 440)">
    <rect x="360" y="392" width="10" height="52" rx="5" fill="#8A5A2B"/>
    <ellipse cx="365" cy="390" rx="22" ry="13" fill="#C0C6CE"/><ellipse cx="365" cy="389" rx="15" ry="8" fill="#F6B73C"/>
  </g>
  <!-- arm R1: chopsticks + noodles -->
  <path d="M714 470 C764 452 800 428 818 388" fill="none" stroke="#9D5FE8" stroke-width="28" stroke-linecap="round"/>
  <g stroke="#7A3E1A" stroke-width="6" stroke-linecap="round">
    <line x1="812" y1="392" x2="852" y2="330"/><line x1="828" y1="398" x2="876" y2="342"/>
  </g>
  <g fill="none" stroke="#FFE9A8" stroke-width="6" stroke-linecap="round">
    <path d="M846 344 q-4 34-14 52 M862 350 q0 32-10 48 M832 340 q-6 30-16 46"/>
  </g>
  <!-- arm L2: holding egg -->
  <path d="M492 528 C436 540 402 574 402 606" fill="none" stroke="#8B4FE0" stroke-width="26" stroke-linecap="round"/>
  <g filter="url(#softShadow)">
    <ellipse cx="402" cy="612" rx="24" ry="19" fill="#FFF8E8" stroke="#E8D9B8" stroke-width="2"/>
    <circle cx="402" cy="612" r="9" fill="#F59E0B"/>
  </g>
  <!-- arm R2: thumbs-up-ish holding narutomaki -->
  <path d="M708 528 C764 540 798 574 798 606" fill="none" stroke="#8B4FE0" stroke-width="26" stroke-linecap="round"/>
  <g filter="url(#softShadow)">
    <circle cx="798" cy="612" r="20" fill="#FFFFFF" stroke="#F9A8D4" stroke-width="3"/>
    <path d="M798 600 q10 6 4 12 q-5 5-10 0 q-4-5 1-8 q6-3 8 2" fill="none" stroke="#EC4899" stroke-width="3.5" stroke-linecap="round"/>
  </g>
  <!-- suckers front -->
  <g fill="#E9D5FF">
    <circle cx="438" cy="462" r="6"/><circle cx="762" cy="438" r="6"/><circle cx="436" cy="560" r="6"/><circle cx="764" cy="560" r="6"/>
  </g>

  <!-- ===== COUNTER ===== -->
  <g filter="url(#softShadow)">
    <rect x="70" y="632" width="1060" height="34" rx="10" fill="url(#woodTop)"/>
    <rect x="70" y="660" width="1060" height="10" fill="#8A4E22"/>
    <rect x="96" y="670" width="1008" height="150" fill="url(#woodGrad)"/>
    <g stroke="#5E2F12" stroke-width="3" opacity=".55">
      <line x1="280" y1="670" x2="280" y2="820"/><line x1="480" y1="670" x2="480" y2="820"/>
      <line x1="680" y1="670" x2="680" y2="820"/><line x1="880" y1="670" x2="880" y2="820"/>
    </g>
    <g stroke="#C98A4A" stroke-width="2" opacity=".5">
      <path d="M120 706 q120-10 240 0 M700 760 q140-10 260 0 M140 786 q100-8 200 0"/>
    </g>
    <!-- booth plaque -->
    <rect x="492" y="706" width="216" height="58" rx="10" fill="#1E3A5F"/>
    <text x="600" y="743" text-anchor="middle" font-family="Georgia, serif" font-size="22" font-weight="700" letter-spacing="3" fill="#FFE9B8">TAKO RAMEN</text>
  </g>

  <!-- ===== BIG RAMEN BOWL (foreground centre) ===== -->
  <g filter="url(#softShadow)">
    <path d="M386 648 h428 c0 92-62 142-138 156 l-10 22 H534 l-10-22 C448 790 386 740 386 648 Z" fill="#C0392B"/>
    <path d="M386 648 h428 c0 14-2 27-6 40 H392 c-4-13-6-26-6-40 Z" fill="#93291F"/>
    <path d="M410 706 q60 34 130 22 M560 768 q70 10 130-22" fill="none" stroke="#F7D08A" stroke-width="6" opacity=".65" stroke-linecap="round"/>
    <ellipse cx="600" cy="648" rx="214" ry="34" fill="#FFF8E8"/>
    <ellipse cx="600" cy="646" rx="192" ry="28" fill="url(#brothGrad)"/>
  </g>
  <!-- noodles -->
  <g>
    <use href="#noodle" transform="translate(600 632)"/><use href="#noodle" transform="translate(600 646) scale(.92)"/>
    <use href="#noodle" transform="translate(600 658) scale(.8)"/>
  </g>
  <!-- toppings -->
  <g filter="url(#softShadow)">
    <ellipse cx="492" cy="636" rx="30" ry="17" fill="#FFF8E8" stroke="#E8D9B8" stroke-width="2"/>
    <circle cx="492" cy="636" r="10" fill="#F59E0B"/>
    <circle cx="706" cy="632" r="22" fill="#FFFFFF" stroke="#F9A8D4" stroke-width="3"/>
    <path d="M706 620 q11 7 4 13 q-5 5-11 0 q-4-5 2-9 q6-3 8 2" fill="none" stroke="#EC4899" stroke-width="3.5" stroke-linecap="round"/>
    <ellipse cx="646" cy="654" rx="26" ry="10" fill="#7C4A21"/><ellipse cx="646" cy="650" rx="26" ry="9" fill="#A8642E"/>
    <g fill="#22C55E"><ellipse cx="540" cy="656" rx="14" ry="6" transform="rotate(-18 540 656)"/><ellipse cx="580" cy="662" rx="14" ry="6" transform="rotate(14 580 662)"/><ellipse cx="664" cy="662" rx="13" ry="6" transform="rotate(-12 664 662)"/></g>
    <rect x="452" y="618" width="52" height="20" rx="5" fill="#14532D" transform="rotate(-8 478 628)"/>
  </g>
  <!-- bowl steam -->
  <g fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round" opacity=".8">
    <path d="M520 604 q-12-22 0-40 q12-18 0-34"/><path d="M600 610 q-12-22 0-40 q12-18 0-34"/><path d="M680 604 q-12-22 0-40 q12-18 0-34"/>
  </g>
  <!-- chopsticks resting on bowl -->
  <g stroke="#7A3E1A" stroke-width="7" stroke-linecap="round">
    <line x1="742" y1="600" x2="838" y2="540"/><line x1="758" y1="616" x2="862" y2="562"/>
  </g>

  <!-- small side bowl (left on counter) -->
  <g filter="url(#softShadow)">
    <path d="M168 640 h132 c0 38-26 60-58 68 l-4 10 h-28 l-4-10 c-24-8-38-30-38-68 Z" fill="#1E3A5F"/>
    <ellipse cx="234" cy="640" rx="66" ry="12" fill="#FFF8E8"/><ellipse cx="234" cy="639" rx="56" ry="9" fill="#F6B73C"/>
    <circle cx="218" cy="637" r="7" fill="#22C55E"/><circle cx="252" cy="640" r="6" fill="#EC4899"/>
  </g>
  <!-- tea cup (right on counter) -->
  <g filter="url(#softShadow)">
    <path d="M906 626 h84 l-8 58 a12 12 0 0 1-12 10 h-44 a12 12 0 0 1-12-10 Z" fill="#FFF8E8" stroke="#D9C7A5" stroke-width="2"/>
    <ellipse cx="948" cy="626" rx="42" ry="9" fill="#BFE3C6"/><ellipse cx="948" cy="625" rx="34" ry="6" fill="#7FB069"/>
    <text x="948" y="668" text-anchor="middle" font-family="Georgia, serif" font-size="20" font-weight="700" fill="#2F6B3A">茶</text>
  </g>
  <!-- soy bottle -->
  <g filter="url(#softShadow)">
    <rect x="322" y="596" width="30" height="46" rx="7" fill="#3B1F0E"/><rect x="332" y="582" width="10" height="16" rx="3" fill="#B91C1C"/>
    <rect x="327" y="608" width="20" height="20" rx="3" fill="#F7D08A"/>
  </g>

  <!-- ===== FLOOR ===== -->
  <rect x="0" y="820" width="1200" height="80" fill="#5E2F12"/>
  <rect x="0" y="820" width="1200" height="8" fill="#3E1E08"/>
  <g stroke="#7A4A22" stroke-width="2" opacity=".6">
    <line x1="120" y1="828" x2="80" y2="900"/><line x1="420" y1="828" x2="400" y2="900"/><line x1="720" y1="828" x2="720" y2="900"/><line x1="1020" y1="828" x2="1060" y2="900"/>
  </g>

  <!-- sparkles -->
  <g fill="#FFD93B">
    <path d="M222 268 l5 13 13 5-13 5-5 13-5-13-13-5 13-5Z"/>
    <path d="M968 268 l5 13 13 5-13 5-5 13-5-13-13-5 13-5Z"/>
    <path d="M872 520 l4 10 10 4-10 4-4 10-4-10-10-4 10-4Z"/>
    <path d="M322 548 l4 10 10 4-10 4-4 10-4-10-10-4 10-4Z"/>
  </g>

  <!-- caption -->
  <text x="600" y="878" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="21" font-style="italic" fill="#FFE9B8">Eight arms, one perfect bowl — served with a smile!</text>
</svg>
'''

def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(SVG, encoding="utf-8")
    size = OUT.stat().st_size
    print(f"Wrote {OUT} ({size} bytes)")

if __name__ == "__main__":
    main()
