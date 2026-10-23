from pathlib import Path

svg = r'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1000" role="img" aria-label="An awkward family portrait of six robots">
<defs>
  <linearGradient id="wall" x2="0" y2="1"><stop stop-color="#386d69"/><stop offset="1" stop-color="#224e50"/></linearGradient>
  <linearGradient id="floor" x2="0" y2="1"><stop stop-color="#d9ad7d"/><stop offset="1" stop-color="#b77857"/></linearGradient>
  <linearGradient id="brass" x2="1" y2="1"><stop stop-color="#fff0b2"/><stop offset=".45" stop-color="#d9aa59"/><stop offset="1" stop-color="#9b673c"/></linearGradient>
  <linearGradient id="cream" x2="1" y2="1"><stop stop-color="#fff3d2"/><stop offset=".6" stop-color="#e3d4ae"/><stop offset="1" stop-color="#b6aa8d"/></linearGradient>
  <linearGradient id="green" x2="1" y2="1"><stop stop-color="#aac49b"/><stop offset=".55" stop-color="#718e71"/><stop offset="1" stop-color="#466455"/></linearGradient>
  <linearGradient id="rose" x2="1" y2="1"><stop stop-color="#f6b7a3"/><stop offset=".55" stop-color="#d98277"/><stop offset="1" stop-color="#a65359"/></linearGradient>
  <linearGradient id="blue" x2="1" y2="1"><stop stop-color="#789caf"/><stop offset=".55" stop-color="#436d89"/><stop offset="1" stop-color="#2c475f"/></linearGradient>
  <linearGradient id="yellow" x2="1" y2="1"><stop stop-color="#ffe59a"/><stop offset=".65" stop-color="#eab65e"/><stop offset="1" stop-color="#bb7749"/></linearGradient>
  <radialGradient id="glow"><stop stop-color="#f9deb0" stop-opacity=".32"/><stop offset="1" stop-color="#f9deb0" stop-opacity="0"/></radialGradient>
  <pattern id="paper" width="7" height="7" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".65" fill="#fff" opacity=".13"/><circle cx="5" cy="4" r=".5" fill="#142f36" opacity=".11"/></pattern>
  <pattern id="wallpaper" width="86" height="86" patternUnits="userSpaceOnUse"><path d="M43 8C35 25 22 30 13 43c12 13 25 18 30 35 5-17 18-22 30-35C64 30 51 25 43 8Z" fill="none" stroke="#a9c0a4" stroke-width="1.5" opacity=".13"/><circle cx="43" cy="43" r="4" fill="#d6ca99" opacity=".12"/></pattern>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="9" stdDeviation="8" flood-color="#142d31" flood-opacity=".27"/></filter>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="12"/></filter>
  <clipPath id="room"><rect x="22" y="22" width="1156" height="956" rx="28"/></clipPath>
</defs>
<!-- The whole room is a slightly faded, theatrical family-photo set. -->
<rect width="1200" height="1000" fill="#172f34"/>
<g clip-path="url(#room)">
<rect x="22" y="22" width="1156" height="775" fill="url(#wall)"/>
<rect x="22" y="22" width="1156" height="775" fill="url(#wallpaper)"/>
<ellipse cx="602" cy="374" rx="570" ry="450" fill="url(#glow)"/>
<path d="M22 734H1178V22" fill="none" stroke="#173c40" stroke-width="7" opacity=".3"/>
<path d="M22 758H1178" stroke="#e1c294" stroke-width="18"/>
<path d="M22 767H1178" stroke="#8e5f49" stroke-width="8"/>
<rect x="22" y="770" width="1156" height="208" fill="url(#floor)"/>
<path d="M120 770 72 978M340 770 312 978M580 770 580 978M820 770 850 978M1050 770 1100 978" stroke="#8e5c49" stroke-width="3" opacity=".35"/>
<path d="M22 881H1178" stroke="#8e5c49" stroke-width="3" opacity=".25"/>
<ellipse cx="606" cy="882" rx="489" ry="101" fill="#1a3f45" opacity=".28" filter="url(#soft)"/>
<ellipse cx="600" cy="858" rx="495" ry="119" fill="#d3a060"/>
<ellipse cx="600" cy="858" rx="462" ry="94" fill="#854f4b"/>
<ellipse cx="600" cy="858" rx="432" ry="76" fill="none" stroke="#d3a060" stroke-width="4" stroke-dasharray="4 11"/>
<path d="M600 788 620 832 680 835 633 866 648 915 600 884 552 915 567 866 520 835 580 832Z" fill="#d3a060" opacity=".45"/>
<!-- Empty heirloom silhouettes: the humans are conspicuously absent. -->
<g opacity=".8">
 <rect x="73" y="113" width="166" height="197" rx="4" fill="#173e41" stroke="#be955c" stroke-width="10"/>
 <rect x="90" y="130" width="132" height="163" fill="#2d5655" stroke="#e0bd78" stroke-width="2"/>
 <ellipse cx="156" cy="204" rx="44" ry="55" fill="#24494b" stroke="#638276" stroke-width="3"/>
 <path d="M130 211q26-22 52 0v24q-26 22-52 0Z" fill="#183b3e"/>
 <rect x="972" y="113" width="151" height="197" rx="4" fill="#173e41" stroke="#be955c" stroke-width="10"/>
 <rect x="989" y="130" width="117" height="163" fill="#2d5655" stroke="#e0bd78" stroke-width="2"/>
 <path d="M1047 165l42 75h-84Z" fill="#183b3e"/><circle cx="1047" cy="183" r="25" fill="#24494b" stroke="#638276" stroke-width="3"/>
</g>
<!-- Standing father: rigid smile, bent antenna, a hand that cannot quite land. -->
<g id="father" filter="url(#shadow)">
 <ellipse cx="491" cy="823" rx="113" ry="23" fill="#183b3d" opacity=".4"/>
 <path d="M426 627 429 795 481 795 502 633M514 631 532 795 584 795 565 620" fill="url(#green)" stroke="#294c48" stroke-width="8"/>
 <path d="M421 788h66v38h-91q-12-19 25-38M531 788h57q34 19 23 38h-83Z" fill="#263e40" stroke="#192f35" stroke-width="7"/>
 <path d="M421 424Q493 392 563 431L579 644Q500 674 407 641Z" fill="url(#green)" stroke="#294c48" stroke-width="9"/>
 <path d="M447 422 485 461 464 493 428 439M540 423 506 461 530 492 562 440" fill="#d5d6ad" stroke="#35594e" stroke-width="5"/>
 <path d="M491 458h24l12 28-25 111-28-2 19-109Z" fill="#bc6558" stroke="#6f4b45" stroke-width="4"/>
 <path d="m485 501 33 11m-37 18 34 11m-39 20 34 10" stroke="#ecc897" stroke-width="5"/>
 <circle cx="548" cy="601" r="5" fill="#d9b267"/><circle cx="548" cy="621" r="5" fill="#d9b267"/>
 <!-- free arm with an overly formal thumb -->
 <path d="M421 453Q374 490 378 589L397 662" fill="none" stroke="#294c48" stroke-width="42" stroke-linecap="round"/>
 <path d="M421 453Q374 490 378 589L397 662" fill="none" stroke="url(#green)" stroke-width="29" stroke-linecap="round"/>
 <circle cx="380" cy="560" r="19" fill="#a6b590" stroke="#294c48" stroke-width="6"/>
 <path d="M382 649q-6-17 6-25l5-27q3-12 14-7 8 4 4 19l-2 13q20-6 25 7l-4 31q-18 20-48-11Z" fill="url(#green)" stroke="#294c48" stroke-width="6"/>
 <!-- far arm reaches across the emotional gap -->
 <path d="M557 451Q651 458 704 495T824 487" fill="none" stroke="#294c48" stroke-width="42" stroke-linecap="round"/>
 <path d="M557 451Q651 458 704 495T824 487" fill="none" stroke="url(#green)" stroke-width="29" stroke-linecap="round"/>
 <circle cx="690" cy="492" r="18" fill="#a6b590" stroke="#294c48" stroke-width="6"/>
 <path d="M805 472q23-13 40 2l7 19q-7 17-26 8l-23-8Z" fill="url(#green)" stroke="#294c48" stroke-width="6"/>
 <path d="m822 477 2 18m9-18 3 17m8-12 2 13" stroke="#385d50" stroke-width="3"/>
 <path d="M470 420v-30h55v31" fill="url(#brass)" stroke="#574e3b" stroke-width="6"/>
 <!-- head and hair-like cap -->
 <path d="M413 260Q412 223 450 218H532Q568 225 568 262V373Q560 411 521 415H454Q411 402 409 367Z" fill="url(#green)" stroke="#294c48" stroke-width="9"/>
 <path d="M405 260h169v-20q-8-42-52-43h-66q-43 3-51 43Z" fill="#355b52" stroke="#294c48" stroke-width="7"/>
 <path d="M424 214v-28h121v30" fill="#75937a" stroke="#294c48" stroke-width="7"/>
 <path d="M468 186v-25h54" fill="none" stroke="#c1a567" stroke-width="7" stroke-linecap="round"/>
 <circle cx="528" cy="160" r="10" fill="#db8a65" stroke="#704c42" stroke-width="4"/>
 <rect x="390" y="287" width="24" height="57" rx="9" fill="url(#brass)" stroke="#574e3b" stroke-width="6"/>
 <rect x="565" y="287" width="24" height="57" rx="9" fill="url(#brass)" stroke="#574e3b" stroke-width="6"/>
 <path d="M430 284q27-17 53 2m18-1q25-17 48-2" fill="none" stroke="#355047" stroke-width="11" stroke-linecap="round"/>
 <!-- spectacles and sideways pupils -->
 <g fill="#e8e4bd" stroke="#294c48" stroke-width="6"><rect x="426" y="298" width="57" height="42" rx="11"/><rect x="498" y="298" width="57" height="42" rx="11"/></g>
 <path d="M483 311h15" stroke="#294c48" stroke-width="6"/>
 <ellipse cx="465" cy="322" rx="7" ry="12" fill="#243c3c"/><ellipse cx="536" cy="322" rx="7" ry="12" fill="#243c3c"/>
 <circle cx="468" cy="318" r="2.5" fill="#fff6d5"/><circle cx="539" cy="318" r="2.5" fill="#fff6d5"/>
 <path d="M485 339v16h20" fill="none" stroke="#436754" stroke-width="6"/>
 <rect x="445" y="366" width="91" height="25" rx="10" fill="#233d3d" stroke="#294c48" stroke-width="4"/>
 <path d="M460 370v16m18-16v16m19-16v16m18-16v16" stroke="#a4af88" stroke-width="4"/>
 <path d="M447 360q18-17 39 2 23-20 46-2-11 18-43 6-28 13-42-6Z" fill="#d4cfab" stroke="#52634f" stroke-width="3"/>
</g>
<!-- Grandfather, seated and judgmental; his cane claims the foreground. -->
<g id="grandfather" filter="url(#shadow)">
 <path d="M98 554q-25 4-26 34l8 184q3 24 27 25h180q22-3 23-26l-1-181q-2-29-28-32Z" fill="#8b4f49" stroke="#4c4140" stroke-width="9"/>
 <path d="M93 580h193v151H93Z" fill="#ad6756" stroke="#6c4944" stroke-width="6"/>
 <path d="M104 594h171v121H104Z" fill="#96594f"/>
 <circle cx="118" cy="609" r="5" fill="#d1936b"/><circle cx="259" cy="609" r="5" fill="#d1936b"/>
 <path d="M74 653h-18v127h50m198-127h24v127h-46" fill="none" stroke="#4c4140" stroke-width="20" stroke-linecap="round"/>
 <path d="M74 653h-18v127h50m198-127h24v127h-46" fill="none" stroke="#c29a61" stroke-width="10" stroke-linecap="round"/>
 <path d="M138 690l-8 98h61l17-100m13 0 24 100h58l-29-112" fill="url(#cream)" stroke="#625e51" stroke-width="8"/>
 <path d="M120 783h77v34h-92q-7-21 15-34m121 0h63q25 13 19 34h-82Z" fill="#343f3d" stroke="#263837" stroke-width="7"/>
 <path d="M125 525q70-33 140 2l25 158q-84 39-179 0Z" fill="url(#cream)" stroke="#625e51" stroke-width="9"/>
 <path d="m143 522 21 149m76-147-5 149" stroke="#887650" stroke-width="18"/>
 <path d="m144 543 18-3m-12 31 18-3m-12 32 18-3m-11 31 18-3m58-78 18 2m-18 29 18 2m-18 29 18 2" stroke="#d8bb75" stroke-width="6"/>
 <circle cx="190" cy="601" r="21" fill="#a7634f" stroke="#685b48" stroke-width="5"/><path d="m181 601 9-9 9 9-9 9Z" fill="#e0c27b"/>
 <!-- cane -->
 <path d="M289 602v216q0 18-17 18" fill="none" stroke="#3e4942" stroke-width="13" stroke-linecap="round"/>
 <path d="M289 607q0-28 27-24 18 3 11 23" fill="none" stroke="#d5b26c" stroke-width="13" stroke-linecap="round"/>
 <path d="M264 571q20-13 38 1l6 53q-22 19-48-1Z" fill="url(#cream)" stroke="#625e51" stroke-width="7"/>
 <path d="M270 584h28m-27 12h29m-27 12h28" stroke="#99896a" stroke-width="3"/>
 <!-- neck and head -->
 <path d="M170 517v-25h51v29" fill="url(#brass)" stroke="#62563f" stroke-width="6"/>
 <path d="M113 365q2-42 42-46h71q44 7 43 48v107q-9 43-49 46h-63q-45-8-47-46Z" fill="url(#cream)" stroke="#625e51" stroke-width="9"/>
 <path d="M111 374q-28-19-21 5t25 27m154-32q27-19 21 5t-25 27" fill="url(#brass)" stroke="#625e51" stroke-width="7"/>
 <path d="M131 329q9-45 47-39 20-25 44 1 31-1 39 38" fill="#e7dfc2" stroke="#77715e" stroke-width="6"/>
 <path d="M131 390q28-16 53-1m12 0q27-16 53 1" fill="none" stroke="#736e5d" stroke-width="9" stroke-linecap="round"/>
 <g fill="#ece6c8" stroke="#625e51" stroke-width="6"><circle cx="160" cy="418" r="30"/><circle cx="222" cy="418" r="30"/></g>
 <path d="M190 413h4" stroke="#625e51" stroke-width="7"/>
 <path d="M152 421h18m36 0h30" stroke="#625e51" stroke-width="9" stroke-linecap="round"/>
 <circle cx="164" cy="420" r="4" fill="#f9edc9"/><circle cx="228" cy="420" r="4" fill="#f9edc9"/>
 <path d="M186 425v20h17" fill="none" stroke="#9d9378" stroke-width="5"/>
 <path d="M139 463q25-28 52 0 27-28 54 0-10 30-53 9-40 21-53-9Z" fill="#eee5c9" stroke="#8b826c" stroke-width="4"/>
 <path d="M172 489q20-9 40 0" fill="none" stroke="#5b5e51" stroke-width="5"/>
</g>
<!-- Mother, polished and pleasant except for her eyes and clenched hands. -->
<g id="mother" filter="url(#shadow)">
 <ellipse cx="929" cy="824" rx="116" ry="24" fill="#183b3d" opacity=".4"/>
 <path d="M880 640 870 792h55l18-143m8-2 22 145h55l-18-160" fill="url(#rose)" stroke="#774f50" stroke-width="8"/>
 <path d="M862 789h68v36h-91q-5-22 23-36m108 0h60q28 14 23 36h-83Z" fill="#503f46" stroke="#3b363d" stroke-width="7"/>
 <path d="M849 449q77-37 151 1l30 208q-96 35-202-1Z" fill="url(#rose)" stroke="#774f50" stroke-width="9"/>
 <path d="M882 440q42 47 84 0l20 33q-60 69-124 0Z" fill="#f1d7b0" stroke="#986a60" stroke-width="5"/>
 <path d="M895 465q30 31 60 0" fill="none" stroke="#d3a95d" stroke-width="5"/>
 <g fill="#fff0c5" stroke="#987650" stroke-width="2"><circle cx="896" cy="465" r="7"/><circle cx="907" cy="476" r="7"/><circle cx="923" cy="482" r="7"/><circle cx="940" cy="477" r="7"/><circle cx="952" cy="466" r="7"/></g>
 <path d="M849 468q-44 62-5 143l49 43" fill="none" stroke="#774f50" stroke-width="40" stroke-linecap="round"/>
 <path d="M849 468q-44 62-5 143l49 43" fill="none" stroke="url(#rose)" stroke-width="27" stroke-linecap="round"/>
 <circle cx="844" cy="582" r="18" fill="#e4a48b" stroke="#774f50" stroke-width="6"/>
 <path d="M1000 468q40 73-1 137l-66 47" fill="none" stroke="#774f50" stroke-width="40" stroke-linecap="round"/>
 <path d="M1000 468q40 73-1 137l-66 47" fill="none" stroke="url(#rose)" stroke-width="27" stroke-linecap="round"/>
 <circle cx="995" cy="582" r="18" fill="#e4a48b" stroke="#774f50" stroke-width="6"/>
 <path d="M875 641q23-17 47-2l30 12q13 11-2 21l-49-3-22-8Z" fill="url(#rose)" stroke="#774f50" stroke-width="6"/>
 <path d="M950 637q-18-10-34 3l-31 19q-9 14 7 20l44-14 20-10Z" fill="url(#rose)" stroke="#774f50" stroke-width="6"/>
 <path d="m901 655 35 8m-30-18 34 8m-54 16 34-8" stroke="#985c59" stroke-width="3"/>
 <path d="M903 438v-29h47v31" fill="url(#brass)" stroke="#725842" stroke-width="6"/>
 <!-- head leaning subtly away from father's hovering hand -->
 <g transform="rotate(4 927 355)">
 <path d="M854 285q0-47 48-53h57q48 7 49 53v96q-5 49-50 52h-57q-47-7-48-52Z" fill="url(#rose)" stroke="#774f50" stroke-width="9"/>
 <path d="M854 293q-27-14-23 12t26 23m150-35q27-14 23 12t-26 23" fill="url(#brass)" stroke="#725842" stroke-width="6"/>
 <path d="M858 276q-5-47 43-57h57q43 8 45 54l-28-16-17 11-22-20-25 17-23-12-30 23Z" fill="#794e51" stroke="#65454a" stroke-width="6"/>
 <path d="M899 221q-15-31 14-43 27-17 49 7 24 18 4 40" fill="#99605c" stroke="#65454a" stroke-width="7"/>
 <path d="M927 178v-33" stroke="#d4ae6b" stroke-width="6"/><circle cx="927" cy="136" r="12" fill="#f4cc85" stroke="#805b47" stroke-width="4"/>
 <path d="M874 314q22-13 45 0m19 0q23-13 46 0" fill="none" stroke="#815153" stroke-width="7" stroke-linecap="round"/>
 <path d="M875 329q21-19 43 0-20 25-43 0Zm65 0q21-19 43 0-20 25-43 0Z" fill="#fff0cf" stroke="#88565a" stroke-width="4"/>
 <ellipse cx="886" cy="330" rx="7" ry="10" fill="#354a48"/><ellipse cx="951" cy="330" rx="7" ry="10" fill="#354a48"/>
 <circle cx="884" cy="327" r="2" fill="#fff"/><circle cx="949" cy="327" r="2" fill="#fff"/>
 <path d="m874 322-9-7m16 5-5-10m106 12 9-7m-16 5 5-10" stroke="#65454a" stroke-width="3"/>
 <path d="M923 335v21h15" fill="none" stroke="#a96462" stroke-width="5"/>
 <path d="M901 385q26-13 52 0-26 24-52 0Z" fill="#f7dfbf" stroke="#995f5d" stroke-width="4"/>
 <path d="M907 385h40" stroke="#995f5d" stroke-width="3"/>
 </g>
</g>
<!-- Teenager: too tall for the picture, emotionally already elsewhere. -->
<g id="teen" filter="url(#shadow)">
 <ellipse cx="682" cy="836" rx="102" ry="22" fill="#183b3d" opacity=".4"/>
 <path d="M632 673 621 813h55l22-137m10 0 17 137h56l-20-150" fill="url(#blue)" stroke="#293f52" stroke-width="8"/>
 <path d="M615 807h65l-4 34h-92q-3-23 31-34m106 0h60q27 12 26 34h-86Z" fill="#2d3846" stroke="#243440" stroke-width="7"/>
 <path d="M601 494q74-29 137 3l37 184q-83 37-182-1Z" fill="url(#blue)" stroke="#293f52" stroke-width="9"/>
 <path d="M620 487q-20 3-28 34l17 29 26-24m86-37q24 5 26 30l-19 26-19-20" fill="#36576e" stroke="#293f52" stroke-width="6"/>
 <path d="M654 501v55m43-55v55" stroke="#d3ba83" stroke-width="5"/><circle cx="654" cy="561" r="7" fill="#d8b577"/><circle cx="697" cy="561" r="7" fill="#d8b577"/>
 <path d="M620 639q59 17 124-2l7 41q-71 28-156 0Z" fill="#355971" stroke="#293f52" stroke-width="5"/>
 <!-- crossed arms, one hand hidden, one impatiently visible -->
 <path d="M610 532q-37 63 11 105l94 14" fill="none" stroke="#293f52" stroke-width="43" stroke-linecap="round"/>
 <path d="M610 532q-37 63 11 105l94 14" fill="none" stroke="url(#blue)" stroke-width="29" stroke-linecap="round"/>
 <circle cx="622" cy="620" r="18" fill="#7795a4" stroke="#293f52" stroke-width="6"/>
 <path d="M735 534q39 57-7 100l-95 9" fill="none" stroke="#293f52" stroke-width="43" stroke-linecap="round"/>
 <path d="M735 534q39 57-7 100l-95 9" fill="none" stroke="url(#blue)" stroke-width="29" stroke-linecap="round"/>
 <circle cx="727" cy="618" r="18" fill="#7795a4" stroke="#293f52" stroke-width="6"/>
 <path d="M604 624q18-11 40-1l43 14q7 15-10 20l-49-7-26-7Z" fill="url(#blue)" stroke="#293f52" stroke-width="6"/>
 <path d="m622 632 43 12m-36-20 43 12" stroke="#395c74" stroke-width="3"/>
 <!-- headphones at neck, not in use -->
 <path d="M628 463q-9 69 49 71 59 0 52-69" fill="none" stroke="#202f3c" stroke-width="13"/>
 <rect x="615" y="474" width="28" height="52" rx="11" fill="#cf805c" stroke="#293f52" stroke-width="6"/>
 <rect x="713" y="474" width="28" height="52" rx="11" fill="#cf805c" stroke="#293f52" stroke-width="6"/>
 <path d="M655 489v-24h47v27" fill="url(#brass)" stroke="#665841" stroke-width="6"/>
 <g transform="rotate(-7 678 409)">
 <path d="M610 348q3-37 39-41h63q39 5 41 42v87q-6 40-43 43h-59q-39-7-42-43Z" fill="url(#blue)" stroke="#293f52" stroke-width="9"/>
 <path d="M610 361q-25-11-20 13t23 19m139-32q25-11 20 13t-23 19" fill="url(#brass)" stroke="#665841" stroke-width="6"/>
 <path d="M610 357v-28q9-42 52-42h45q37 7 46 40l-30 2-8-15-21 16-28-17-17 20-39 3Z" fill="#273e52" stroke="#293f52" stroke-width="6"/>
 <path d="M644 287q-5-32 21-34m31 35q12-30 33-15" fill="none" stroke="#d1a968" stroke-width="6"/>
 <circle cx="666" cy="247" r="8" fill="#c7745e"/><circle cx="733" cy="269" r="8" fill="#c7745e"/>
 <path d="M628 378h45m18 0h43" stroke="#263d50" stroke-width="9" stroke-linecap="round"/>
 <path d="M630 389h41v28h-41Zm63 0h40v28h-40Z" fill="#d8dfc6" stroke="#293f52" stroke-width="5"/>
 <path d="M631 390h40m23 0h39" stroke="#293f52" stroke-width="7"/>
 <ellipse cx="660" cy="402" rx="6" ry="8" fill="#283d4c"/><ellipse cx="722" cy="402" rx="6" ry="8" fill="#283d4c"/>
 <path d="M680 403v15h12" fill="none" stroke="#47667b" stroke-width="4"/>
 <path d="M657 446h49" stroke="#263d50" stroke-width="7" stroke-linecap="round"/>
 <path d="M654 447l-5-4m59 4 5-4" stroke="#263d50" stroke-width="4"/>
 </g>
</g>
<!-- Child: sincere, delighted, and holding a flower upside down. -->
<g id="child" filter="url(#shadow)">
 <ellipse cx="882" cy="868" rx="86" ry="18" fill="#183b3d" opacity=".35"/>
 <path d="M844 755 837 840h44l11-80m12 0 10 80h44l-8-91" fill="url(#yellow)" stroke="#805d43" stroke-width="7"/>
 <path d="M832 835h53v29h-70q-2-19 17-29m78 0h50q19 10 17 29h-67Z" fill="#536f66" stroke="#3b514e" stroke-width="6"/>
 <path d="M826 650q59-26 113 1l22 122q-71 28-147 0Z" fill="url(#yellow)" stroke="#805d43" stroke-width="8"/>
 <path d="M842 662h80l8 79q-43 21-93 0Z" fill="#648779" stroke="#45645b" stroke-width="5"/>
 <path d="M840 649v35m84-35v35" stroke="#45645b" stroke-width="10"/><circle cx="841" cy="686" r="6" fill="#efd081"/><circle cx="923" cy="686" r="6" fill="#efd081"/>
 <path d="M878 697l8 14 16 3-12 11 3 16-15-8-14 8 3-16-12-11 16-3Z" fill="#edc776"/>
 <!-- one waving mitten; the other absentmindedly droops the flower -->
 <path d="M824 670q-36 7-44-35l-4-35" fill="none" stroke="#805d43" stroke-width="32" stroke-linecap="round"/>
 <path d="M824 670q-36 7-44-35l-4-35" fill="none" stroke="url(#yellow)" stroke-width="21" stroke-linecap="round"/>
 <circle cx="783" cy="641" r="14" fill="#edc36f" stroke="#805d43" stroke-width="5"/>
 <path d="M761 600q-8-20 3-25 10-2 13 14l1-32q4-13 14-7 6 4 3 27l11-18q10-8 16 1 4 7-8 25l-4 20q-21 22-49-5Z" fill="url(#yellow)" stroke="#805d43" stroke-width="6"/>
 <path d="M940 671q37 33 20 78l-8 20" fill="none" stroke="#805d43" stroke-width="32" stroke-linecap="round"/>
 <path d="M940 671q37 33 20 78l-8 20" fill="none" stroke="url(#yellow)" stroke-width="21" stroke-linecap="round"/>
 <path d="M940 758q20-12 32 3l-2 28q-18 15-35-2Z" fill="url(#yellow)" stroke="#805d43" stroke-width="6"/>
 <path d="M959 786q28 34 30 66" fill="none" stroke="#52715b" stroke-width="6"/>
 <path d="M976 817q18-14 30-5-5 16-25 16" fill="#719171" stroke="#456554" stroke-width="3"/>
 <path d="M988 852q-21-4-19 16 9 18 25 0 19 12 25-6-3-20-24-10-1-22-16-18-14 4-8 24-20-10-27 5 2 17 24 5Z" fill="#d77768" stroke="#8b554d" stroke-width="4"/>
 <circle cx="989" cy="858" r="10" fill="#edc677"/>
 <path d="M864 645v-20h43v23" fill="url(#brass)" stroke="#805d43" stroke-width="5"/>
 <path d="M816 547q1-34 35-39h58q36 5 38 39v66q-4 35-38 39h-58q-34-5-36-39Z" fill="url(#yellow)" stroke="#805d43" stroke-width="8"/>
 <rect x="803" y="563" width="17" height="38" rx="7" fill="#dc8b61" stroke="#805d43" stroke-width="5"/><rect x="944" y="563" width="17" height="38" rx="7" fill="#dc8b61" stroke="#805d43" stroke-width="5"/>
 <path d="M881 509v-27" stroke="#805d43" stroke-width="6"/>
 <path d="M881 483v-26" stroke="#52715b" stroke-width="7"/>
 <path d="M879 470q-44-32-50-4 12 25 50 13m4-9q42-34 51-7-9 27-50 16" fill="#d77c64" stroke="#80534a" stroke-width="5"/>
 <circle cx="882" cy="475" r="10" fill="#f4d48a" stroke="#805d43" stroke-width="4"/>
 <circle cx="851" cy="566" r="18" fill="#fff2c9" stroke="#8e6849" stroke-width="5"/><circle cx="913" cy="566" r="18" fill="#fff2c9" stroke="#8e6849" stroke-width="5"/>
 <circle cx="854" cy="570" r="8" fill="#304b49"/><circle cx="916" cy="570" r="8" fill="#304b49"/><circle cx="857" cy="566" r="3" fill="#fff"/><circle cx="919" cy="566" r="3" fill="#fff"/>
 <path d="M878 574v12h10" fill="none" stroke="#ad7a4d" stroke-width="4"/>
 <path d="M850 605q31 31 64 0-5 34-33 34-27-1-31-34Z" fill="#425551" stroke="#805d43" stroke-width="4"/>
 <path d="M858 612h47" stroke="#f4dfae" stroke-width="8"/>
</g>
<!-- The dog has found father's trailing cable. -->
<g id="dog" filter="url(#shadow)">
 <path d="M395 823q66-40 102 2 22 26-13 36-27 7-25-17 4-17 27-6" fill="none" stroke="#344e4d" stroke-width="13" stroke-linecap="round"/>
 <path d="M287 786q51-23 106 6l18 57q-62 31-127-2Z" fill="url(#brass)" stroke="#625c47" stroke-width="7"/>
 <path d="M305 843v35m76-35v35" stroke="#625c47" stroke-width="18" stroke-linecap="round"/>
 <path d="M291 879h29m47 0h30" stroke="#2f4443" stroke-width="15" stroke-linecap="round"/>
 <path d="M269 760q-15-49 18-54l22 37m38 2 24-32q28 13 2 54" fill="#af8251" stroke="#625c47" stroke-width="7"/>
 <path d="M259 746q48-26 95 1l11 65q-53 37-110 0Z" fill="url(#brass)" stroke="#625c47" stroke-width="8"/>
 <circle cx="282" cy="774" r="11" fill="#294745"/><circle cx="333" cy="774" r="11" fill="#294745"/>
 <circle cx="285" cy="771" r="3" fill="#fff0bd"/><circle cx="336" cy="771" r="3" fill="#fff0bd"/>
 <path d="M292 794h31l-5 16h-20Z" fill="#344c49"/>
 <path d="M282 814q29 19 54-1" fill="none" stroke="#625c47" stroke-width="5"/>
 <path d="M310 816q7 26 20 13" fill="#d77768" stroke="#80534a" stroke-width="4"/>
 <path d="M284 832q30 17 62 0" fill="none" stroke="#b86051" stroke-width="12"/>
 <circle cx="316" cy="847" r="10" fill="#e7c677" stroke="#785b43" stroke-width="3"/>
</g>
<!-- A visible curl of cable makes the dog's choice of toy legible. -->
<path d="M421 807q-37-20-44 7-5 23 21 18 18-5 3-19" fill="none" stroke="#283f40" stroke-width="6" stroke-linecap="round"/>
<!-- Gentle unified print texture and a dark vignette, not a frame of text. -->
<rect x="22" y="22" width="1156" height="956" fill="url(#paper)" pointer-events="none"/>
<path d="M22 22h1156v956H22Z" fill="none" stroke="#122e33" stroke-width="44" opacity=".2"/>
</g>
<rect x="14" y="14" width="1172" height="972" rx="34" fill="none" stroke="#d2ad70" stroke-width="9"/>
<rect x="28" y="28" width="1144" height="944" rx="22" fill="none" stroke="#6f684e" stroke-width="2"/>
</svg>'''

Path('output').mkdir(exist_ok=True)
Path('output/awkward_robot_family.svg').write_text(svg)
print(f'Wrote {len(svg):,} bytes')
