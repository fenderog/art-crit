from pathlib import Path

# A hand-drawn, layered studio portrait. All artwork is original SVG geometry.
OUT = Path('output')
OUT.mkdir(exist_ok=True)
s = []
def add(markup): s.append(markup)
add('''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1360" viewBox="0 0 1440 1360" role="img" aria-label="An awkward studio portrait of a robot family">
<defs>
  <linearGradient id="back" x2="0" y2="1"><stop stop-color="#173c40"/><stop offset="1" stop-color="#527770"/></linearGradient>
  <radialGradient id="halo"><stop stop-color="#b6bea0" stop-opacity=".47"/><stop offset=".7" stop-color="#9cb09a" stop-opacity=".18"/><stop offset="1" stop-color="#9cb09a" stop-opacity="0"/></radialGradient>
  <linearGradient id="ivory" x1="0" y1="0" x2=".9" y2="1"><stop stop-color="#f2e2b9"/><stop offset=".55" stop-color="#d6c9a2"/><stop offset="1" stop-color="#a5a58b"/></linearGradient>
  <linearGradient id="mint" x2=".85" y2="1"><stop stop-color="#aac4ab"/><stop offset=".55" stop-color="#739e91"/><stop offset="1" stop-color="#486f68"/></linearGradient>
  <linearGradient id="coral" x2=".85" y2="1"><stop stop-color="#ecab7c"/><stop offset=".5" stop-color="#cb7959"/><stop offset="1" stop-color="#9d5445"/></linearGradient>
  <linearGradient id="gold" x2=".85" y2="1"><stop stop-color="#f4ce78"/><stop offset=".6" stop-color="#dba348"/><stop offset="1" stop-color="#ae713d"/></linearGradient>
  <linearGradient id="dark" x2=".8" y2="1"><stop stop-color="#5a7170"/><stop offset="1" stop-color="#293e43"/></linearGradient>
  <linearGradient id="glass" x2=".8" y2="1"><stop stop-color="#253e42"/><stop offset="1" stop-color="#132f34"/></linearGradient>
  <linearGradient id="screen" x2="0" y2="1"><stop stop-color="#769d8a"/><stop offset="1" stop-color="#adc2a1"/></linearGradient>
  <linearGradient id="sofa" x2="0" y2="1"><stop stop-color="#bc7650"/><stop offset="1" stop-color="#854e3f"/></linearGradient>
  <pattern id="grain" width="37" height="41" patternUnits="userSpaceOnUse"><circle cx="3" cy="7" r=".8" fill="#ffedc2"/><circle cx="22" cy="26" r=".6" fill="#ffedc2"/><path d="M13 34h1M29 12h1" stroke="#172f32" stroke-width="1"/></pattern>
  <pattern id="wallpaper" width="126" height="126" patternUnits="userSpaceOnUse"><path d="M63 55v16M55 63h16M59 59l8 8M67 59l-8 8" stroke="#c4c7a3" opacity=".12" fill="none" stroke-width="1.2"/><path d="M0 0L63 63 126 0M0 126l63-63 63 63" stroke="#a3b69a" opacity=".035" fill="none"/></pattern>
  <pattern id="scan" width="4" height="6" patternUnits="userSpaceOnUse"><path d="M0 1h4" stroke="#284b47" stroke-opacity=".12"/></pattern>
  <clipPath id="photo"><rect x="65" y="65" width="1310" height="1230" rx="125"/></clipPath>
  <g id="bolt" stroke="#273f40" stroke-width="2"><circle r="6" fill="#a2afa0"/><path d="M-2 2l4-4"/></g>
  <g id="bigjoint" stroke="#263f40" stroke-width="5"><circle r="24" fill="#324e4e"/><circle r="14" fill="#aaac8e"/><circle r="5" fill="#465c55"/></g>
  <g id="smalljoint" stroke="#263f40" stroke-width="4"><circle r="16" fill="#3b5856"/><circle r="7" fill="#c2b891"/></g>
</defs>
<rect width="1440" height="1360" fill="#e9dbb9"/>
<rect x="30" y="30" width="1380" height="1300" rx="152" fill="none" stroke="#8d9a83" stroke-width="2"/>
<g clip-path="url(#photo)">
<rect x="65" y="65" width="1310" height="1230" fill="url(#back)"/>
<rect x="65" y="65" width="1310" height="1055" fill="url(#wallpaper)"/>
<ellipse cx="702" cy="622" rx="633" ry="635" fill="url(#halo)"/>
<!-- The pulled studio curtains are deliberately a little uneven. -->
<g fill="#1b4144" stroke="#193a3e" stroke-width="3">
<path d="M65 65H213Q186 335 138 526Q96 724 126 1100H65Z"/>
<path d="M1375 65H1249Q1275 408 1312 580Q1344 806 1310 1100h65Z"/>
</g>
<g stroke="#678779" stroke-width="3" opacity=".24" fill="none"><path d="M157 83Q147 352 103 541M191 89Q157 417 125 512M86 605q-9 231 9 452M1304 91q5 294 41 478"/><path d="M1274 91q10 316 47 453M1354 623q15 226-14 425"/></g>
<path d="M65 1102Q720 1067 1375 1102V1295H65Z" fill="#b1a486"/>
<path d="M65 1103Q720 1068 1375 1103" fill="none" stroke="#1e4443" stroke-width="4" opacity=".5"/>
<g stroke="#7c8974" fill="none" stroke-width="2" opacity=".3"><path d="M210 1100l-111 194M462 1087l-41 207M741 1084l13 210M1012 1089l80 205M1253 1098l121 163M65 1187q644-36 1310 0"/></g>
<ellipse cx="732" cy="1155" rx="508" ry="111" fill="#536a5d" opacity=".45"/>
<ellipse cx="732" cy="1150" rx="485" ry="95" fill="#718579" stroke="#365653" stroke-width="4"/>
<ellipse cx="732" cy="1150" rx="456" ry="77" fill="none" stroke="#c0ba96" stroke-width="3"/>
<ellipse cx="732" cy="1150" rx="438" ry="67" fill="none" stroke="#a3ab8c" stroke-width="1.5"/>
<g fill="#223f3b" opacity=".22"><ellipse cx="475" cy="1143" rx="208" ry="32"/><ellipse cx="818" cy="1144" rx="118" ry="25"/><ellipse cx="1122" cy="1160" rx="137" ry="29"/></g>
<!-- Mother's elegant but locked knees. -->
<g stroke="#263f40" stroke-width="5" stroke-linejoin="round">
<path d="M746 723l18 223 18 160h49l1-176 12-204" fill="url(#coral)"/>
<path d="M842 718l30 213-6 174h47l27-178-10-224" fill="url(#coral)"/>
<path d="M780 960l42-1M877 962l43 2" fill="none"/>
<path d="M782 1091l46-2 15 39q-26 19-95 13-5-23 34-50Z" fill="#314d4c"/>
<path d="M871 1094l42 1q50 25 46 44-63 12-91-10Z" fill="#314d4c"/>
<path d="M750 1138q47 7 90-5M873 1136q45 7 80 0" stroke="#d7c49c" stroke-width="3" fill="none"/>
</g>
<!-- Father: broad, overdressed, and catastrophically stiff. -->
<g stroke="#263f40" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
<path d="M391 737l-5 212 24 164h58l-5-180 29-181M509 746l10 179-12 184h58l37-172-7-193" fill="url(#mint)"/>
<path d="M406 1103h66l10 37q-55 16-105-1-3-24 29-36ZM511 1101h61q36 15 37 38-52 15-105-2Z" fill="#314c48"/>
<path d="M383 1137q46 8 94 0M510 1136q48 10 93 0" stroke="#9aaa90" stroke-width="3"/>
<path d="M408 467l-43 57 10 220q111 48 231-1l-7-218-59-52Z" fill="url(#mint)"/>
<path d="M571 495l28 30 7 218-30 12-5-199Z" fill="#426b64" stroke-width="3"/>
<path d="M404 490l-22 45 9 173" fill="none" stroke="#c3d4b4" stroke-width="5"/>
<path d="M395 719q82 23 178 3" fill="none" stroke="#31594f" stroke-width="3"/>
<path d="M451 449v46q30 23 64-2l-5-46" fill="#a9b39a"/>
<path d="M453 467h58M453 480h58" stroke-width="3"/>
<path d="M431 485l46 18-35 49-34-50ZM477 503l41-19 33 26-40 41Z" fill="#e9ddbc" stroke-width="4"/>
<path d="M400 535l39 46-19 112M550 529l-29 54 16 121" fill="none" stroke="#3d685f" stroke-width="3"/>
<rect x="538" y="588" width="34" height="44" rx="5" fill="#607f70" stroke-width="3"/>
<path d="M545 588v-17m11 17v-13" stroke="#e8ca87" stroke-width="5"/>
<!-- Left arm carries a limp, solitary flower. -->
<path d="M365 526q-39 0-41 42l-2 122 29 9 37-130" fill="url(#mint)"/>
<use href="#bigjoint" x="345" y="684"/>
<path d="M325 701l-17 114 39 9 22-121" fill="url(#mint)"/>
<path d="M320 803q-20 8-13 37l11 15 13-6 13 5 12-20-8-23Z" fill="#c8c7a2" stroke-width="4"/>
<path d="M316 824l11 14m5-15 4 18m9-17-1 13" stroke-width="3"/>
<!-- His other hand cannot quite commit to a hug. -->
<path d="M594 529q37-5 42 32l3 110-38 5-21-113" fill="url(#mint)"/>
<use href="#bigjoint" x="620" y="681"/>
<path d="M605 700l5 87 41 3-8-95" fill="url(#mint)"/>
<path d="M610 781l-5 23q-6 16 2 20 8 1 15-17l3 29q2 9 9 7 5-1 4-11l-1-22 10 26q4 8 10 4 5-3 1-13l-9-24 11 14q7 7 12 1 3-4-3-12l-20-25Z" fill="#c5c7a1" stroke-width="4"/>
</g>
<g fill="none" stroke="#436449" stroke-width="4" stroke-linecap="round"><path d="M330 840q21 40 7 83"/><path d="M338 875q20-8 26 7-18 6-25-2M339 898q-21-11-25 4 13 10 25 2" fill="#6c8a61"/></g>
<g transform="translate(337 930) rotate(18)" stroke="#694f3d" stroke-width="2"><path d="M0-9q-23-12-24 1 2 12 20 8-15 16-3 22 14 3 14-17 20 12 24-1 1-12-20-12 6-20-6-19-11 1-5 18" fill="#d5ac62"/><circle r="7" fill="#775c3f"/></g>
<!-- Dad's head tilts away from the pulled tie. -->
<g transform="rotate(-5 475 372)" stroke="#263f40" stroke-width="6" stroke-linejoin="round">
<path d="M376 297l19-23h162l31 22v151l-22 17H391l-15-18Z" fill="url(#mint)"/>
<path d="M557 275l31 21v151l-22 17V298Z" fill="#4f786d" stroke-width="3"/>
<rect x="361" y="341" width="21" height="62" rx="9" fill="#b2b798"/>
<rect x="584" y="338" width="19" height="63" rx="9" fill="#a1aa8f"/>
<path d="M453 274v-29h36v29" fill="#677f6d" stroke-width="4"/>
<path d="M469 244l-5-38" fill="none" stroke-width="4"/><circle cx="463" cy="201" r="9" fill="#d99968" stroke-width="3"/>
<rect x="397" y="301" width="152" height="96" rx="23" fill="url(#glass)" stroke-width="4"/>
<path d="M406 325q1-15 20-15h52" fill="none" stroke="#78938b" stroke-width="3"/>
<path d="M417 337l28-6M494 332l29 10" stroke="#e9d9ab" stroke-width="5" fill="none"/>
<ellipse cx="434" cy="361" rx="12" ry="16" fill="#f6dda2" stroke="none"/>
<ellipse cx="509" cy="361" rx="10" ry="14" fill="#f6dda2" stroke="none"/>
<circle cx="436" cy="365" r="4" fill="#44605a" stroke="none"/><circle cx="511" cy="365" r="4" fill="#44605a" stroke="none"/>
<path d="M420 418q47-9 100 0l-4 23h-91Z" fill="#eee0b9" stroke-width="4"/>
<path d="M442 418v22m20-24v24m20-24v24m20-23v22" stroke-width="2.5"/>
<path d="M391 315v112" stroke="#cbdbb7" stroke-width="4" fill="none"/>
<use href="#bolt" x="393" y="446"/><use href="#bolt" x="548" y="446"/>
<path d="M556 353v31m11-31v31" stroke="#2d514d" stroke-width="2"/>
</g>
<!-- Mother puts a hand on both unwilling neighbours. -->
<g stroke="#263f40" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<path d="M728 480q-26-28-53-25l-88 39 13 33 92-21 37 28" fill="url(#coral)"/>
<use href="#smalljoint" x="682" y="481"/>
<path d="M588 492q-23-14-38-12l-32 4q-12 3-8 11 3 5 14 2l20-1-32 10q-10 4-6 10 3 5 13 2l29-9-23 12q-9 6-5 11 4 5 13 0l28-10-13 11q-6 7 0 12 5 4 14-4l34-23Z" fill="#e6b382" stroke-width="3.5"/>
<path d="M884 475q30-4 45 29l40 105-33 17-60-101" fill="url(#coral)"/>
<use href="#bigjoint" x="952" y="623"/>
<path d="M961 603l53 34-12 34-62-26" fill="url(#coral)"/>
<path d="M749 445q-49 10-51 61l20 88-19 104q96 62 220 7l-21-110 14-91q-5-51-59-60Z" fill="url(#coral)"/>
<path d="M886 482q21 4 26 28l-14 87 21 108-28 10-21-111Z" fill="#a15847" stroke="none"/>
<path d="M724 491q-16 28 6 91" fill="none" stroke="#f2bd8c" stroke-width="5"/>
<path d="M719 597q84 28 178 0l3 26q-91 28-185 0Z" fill="#294b4a"/>
<circle cx="810" cy="623" r="18" fill="#dcbb7e" stroke-width="3"/><circle cx="810" cy="623" r="8" fill="#658274" stroke-width="2"/>
<path d="M735 657l-9 38m161-39 7 39" stroke="#f0ac7c" stroke-width="3"/>
<path d="M777 411v43q26 24 57-2v-41" fill="#969f85"/>
<path d="M778 427h55m-55 11h55" stroke-width="2.5"/>
<path d="M765 449l37 30-29 31-38-53M839 448l-37 31 26 32 48-51" fill="#efdcaf" stroke-width="3.5"/>
</g>
<!-- Pearl-like bearing necklace. -->
''')
for x,y,r in [(743,477,7),(750,493,7),(762,507,7),(778,517,7),(796,522,8),(815,521,8),(833,515,7),(849,505,7),(861,490,7),(866,473,7)]:
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#e9d7aa" stroke="#665f4a" stroke-width="2"/>')
add('''<!-- Smooth oval face, fixed polite smile and a slightly overworked eye. -->
<g transform="rotate(6 806 338)" stroke="#263f40" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<path d="M724 265q-21-57 23-68 26-7 39 15 16-42 49-24 24 13 11 39 41-10 53 17 14 27-21 45" fill="#ab5c48"/>
<path d="M746 217q-17 13-4 35M812 200q20 3 12 26M868 244q15 8 7 24" fill="none" stroke="#de976d" stroke-width="3"/>
<ellipse cx="805" cy="330" rx="98" ry="99" fill="url(#coral)"/>
<path d="M719 296q13-42 44-45" fill="none" stroke="#f0ba89" stroke-width="5"/>
<path d="M744 280q61-36 127 7l-3 67q-60 30-122-1Z" fill="url(#glass)" stroke-width="4"/>
<path d="M756 294q16-6 29 1M831 294l23 3" stroke="#e6c48d" stroke-width="4" fill="none"/>
<path d="M756 325q16-22 30 0M829 325q15-22 29 0" stroke="#f4d797" stroke-width="6" fill="none"/>
<path d="M755 313l-6-5m32 6 4-7m46 5-3-7m25 10 7-6" stroke="#f4d797" stroke-width="2.5"/>
<path d="M777 384q29 13 52-3" fill="none" stroke-width="4"/>
<path d="M775 378l-5 10M830 376l4 9" stroke-width="2"/>
<ellipse cx="744" cy="368" rx="11" ry="5" fill="#a95848" stroke="none"/><ellipse cx="862" cy="367" rx="11" ry="5" fill="#a95848" stroke="none"/>
<circle cx="706" cy="334" r="15" fill="#c89564"/><circle cx="904" cy="334" r="15" fill="#c89564"/>
<path d="M705 349v19m199-19v19" stroke="#e1be79" stroke-width="3"/>
<path d="M705 366l-8 12 8 11 8-11ZM904 366l-8 12 8 11 8-11Z" fill="#ebcb88" stroke-width="2"/>
<use href="#bolt" x="758" y="403"/><use href="#bolt" x="854" y="402"/>
</g>
<!-- Sofa sits in front of the standing generation. -->
<g stroke="#493f35" stroke-width="5" stroke-linejoin="round">
<path d="M241 1014l-13 116q11 14 35 4l32-110M851 1022l27 110q14 12 35 0l-4-112" fill="#5a5140"/>
<path d="M233 857v-52q0-42 46-42h567q55 0 58 54v91Z" fill="url(#sofa)"/>
<path d="M266 838v-21q0-22 23-22h541q43 0 43 45" fill="none" stroke="#d09a6a" stroke-width="3"/>
<path d="M260 804l58 75 74-79 75 79 73-79 75 80 71-79 76 78 75-71" fill="none" stroke="#955c45" stroke-width="3"/>
<path d="M233 908q309-39 669 0v111q-337 54-669-2Z" fill="#a76b4a"/>
<path d="M264 924q315-28 607 2v59q-302 28-607-2Z" fill="#c18c5b" stroke-width="3"/>
<path d="M545 913v84" stroke-width="3"/>
<path d="M211 903q-26-20-13-50 12-26 48-16 24 7 23 38l-1 133-52 2Z" fill="url(#sofa)"/>
<path d="M876 889q-8-33 23-41 44-11 49 27 2 19-17 32l-6 105-52 4Z" fill="url(#sofa)"/>
<path d="M211 863q11-17 34-2M890 872q15-15 36-1" fill="none" stroke="#dda878" stroke-width="4"/>
<path d="M271 1014q283 25 595 1" fill="none" stroke="#ddad77" stroke-width="3"/>
</g>
''')
for x in (318,467,615,762):
    add(f'<circle cx="{x}" cy="879" r="5" fill="#714a38"/><path d="M{x-4} 875l8 8" stroke="#cf9464" stroke-width="1.5"/>')
add('''<!-- Teen: one ear covered, turned away, ankles nowhere near straight. -->
<g stroke="#243e40" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<path d="M1036 875l-17 115 18 137 37-1 12-134 24-116" fill="url(#dark)"/>
<path d="M1105 884l18 119 47 117 37-14-30-128-12-109" fill="url(#dark)"/>
<path d="M1024 990l55 5M1125 1005l57-21" stroke="#9aa891" stroke-width="3"/>
<path d="M1037 1121l38-1 7 39q-45 20-102 10-2-20 57-48Z" fill="#d4c7a2"/>
<path d="M1170 1112l34-15q39 3 52 23-18 28-72 44l-16-16Z" fill="#d4c7a2"/>
<path d="M986 1168q43 7 91-12M1183 1157q43-12 69-37" fill="none" stroke-width="3"/>
<path d="M1035 1131l22 8m-34-1 21 8m-34-1 18 7M1197 1115l-16 15m27-12-18 15m28-10-16 15" stroke="#65756a" stroke-width="3"/>
<path d="M1066 625l-39 33-25 210q76 54 169 21l-1-205-50-48Z" fill="url(#dark)"/>
<path d="M1040 665l-24 191" stroke="#7c9290" stroke-width="4"/>
<path d="M1048 654l39 44-40 28M1134 649l-47 49 58 28" fill="#566f6d" stroke-width="3"/>
<path d="M1088 699l-13 146" stroke="#b0af92" stroke-width="2"/>
<path d="M1066 630l1 20q21 20 49-4l3-27" fill="#8b9f8d"/>
<path d="M1069 640h47" stroke-width="2"/>
<path d="M1070 866l52 8m-80-1 18 4" stroke="#94a396" stroke-width="2"/>
<!-- Folded arms form a firm barrier. -->
<path d="M1030 673q-31-3-34 30l-13 89q-4 24 19 29l137-25-6-36-107 13 28-66" fill="url(#dark)"/>
<use href="#smalljoint" x="1005" y="796"/>
<path d="M1151 673q27 1 35 26l22 106q2 27-26 28l-127-50 12-32 93 28-23-74" fill="url(#dark)"/>
<use href="#smalljoint" x="1183" y="810"/>
<path d="M1068 751l-35-12q-10-2-12 5-1 5 9 10l-14-2q-11-1-12 7 0 5 10 8l-6 1q-9 2-5 9l42 16 14-11Z" fill="#9aac96" stroke-width="3"/>
<path d="M1133 763l24-4q13-3 17 4 3 6-9 10l-15 5 14-1q11 0 10 8-1 5-12 6l-29 6Z" fill="#9aac96" stroke-width="3"/>
<path d="M1050 802l68 27" stroke="#728985" stroke-width="3"/>
<!-- Mother's fingers placed on teen's shoulder, not reciprocated. -->
<path d="M1001 636q19-5 34 10l15 16q4 8-2 11-5 2-11-5l-8-8 6 18q3 9-4 11-6 1-9-8l-6-17 1 21q0 9-7 9-6-1-6-10l-2-18-6 13q-4 7-10 3-4-3 0-11l5-20Z" fill="#e1ac7d" stroke-width="3.5"/>
</g>
<g transform="rotate(10 1114 554)" stroke="#243e40" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
<path d="M1037 481l33-22h104l33 30-9 128-28 21-119-7-24-25Z" fill="url(#dark)"/>
<path d="M1180 479l27 10-9 128-28 21 12-113" fill="#273f44" stroke-width="3"/>
<path d="M1054 511l118-4 8 80-122 7Z" fill="url(#glass)" stroke-width="4"/>
<path d="M1069 548l34 9M1127 552l35-11" stroke="#b8d5b3" stroke-width="5"/>
<path d="M1089 559v10m57-17v12" stroke="#f1d8a0" stroke-width="7"/>
<path d="M1119 611l39-4 4-7" fill="none" stroke="#c7c6a0" stroke-width="3.5"/>
<!-- A swept asymmetric metal fringe. -->
<path d="M1038 493l-13-30 24 1-5-23 38 13 50-14 63 25 4 51-48-36-19 48-18-32-53 43 3-30-29 24Z" fill="#263d42"/>
<path d="M1056 472l26 8m32-14 25 8m-77 27 19-16" stroke="#607b76" stroke-width="3"/>
<path d="M1032 558q-30-105 36-125 65-18 106 11" fill="none" stroke="#1b3338" stroke-width="14"/>
<path d="M1033 543q-17-76 32-100 47-21 87-6" fill="none" stroke="#b79162" stroke-width="4"/>
<rect x="1014" y="532" width="34" height="69" rx="15" fill="#c6975f"/>
<rect x="1021" y="543" width="13" height="46" rx="6" fill="#6e7865" stroke-width="2"/>
<path d="M1029 603q-14 85 27 99" fill="none" stroke="#142e34" stroke-width="4"/>
<use href="#bolt" x="1063" y="610"/>
<circle cx="1190" cy="609" r="9" fill="none" stroke="#d6b574" stroke-width="3"/>
</g>
<!-- Grandmother's little treaded feet: an older model, lovingly polished. -->
<g stroke="#283f3e" stroke-width="5" stroke-linejoin="round">
<path d="M289 971l-8 110h39l31-107M389 976l3 109h42l10-110" fill="#a3aa8c"/>
<path d="M251 1069q-21 3-22 35-1 31 23 33h78q26 0 27-32 0-35-27-36Z" fill="#354f4a"/>
<path d="M377 1071q-24 0-24 34-1 32 25 33h78q25 0 25-33-1-33-25-34Z" fill="#354f4a"/>
<path d="M252 1082h76q16 0 16 22 0 21-16 21h-76q-12 0-12-21 0-22 12-22ZM378 1083h76q15 0 15 22t-15 21h-76q-14 0-14-21t14-22Z" fill="#8d9c80" stroke-width="3"/>
</g>
''')
for x in [255,279,307,330,379,403,431,456]:
    add(f'<circle cx="{x}" cy="1104" r="8" fill="#536c5e" stroke="#2a4541" stroke-width="2"/>')
add('''<g stroke="#283f3e" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<path d="M288 811q-37 21-35 68l-7 94q90 53 211 5l-20-104q-4-54-45-65Z" fill="url(#ivory)"/>
<path d="M285 832l-20 132q94 39 174 1l-30-131" fill="#849480" stroke-width="3"/>
<path d="M315 851l-4 109m70-110 13 111" stroke="#bdc0a1" stroke-width="3"/>
<path d="M332 871h44v48h-44Z" fill="#526e62" stroke-width="3"/>
<path d="M340 882h28m-28 10h28m-28 10h28" stroke="#b7bd96" stroke-width="2"/>
<!-- A crocheted shawl, translated into punched metal lace. -->
<path d="M301 803l-39 38 24 17 9-10 11 19 14-12 16 21 20-15 18 16 16-20 20 9 8-20 21 4 5-28-47-21Z" fill="#ebd6ad" stroke-width="3"/>
<path d="M282 836l15-13 13 18 13-10 16 19 14-11 19 15 17-23 17 7 10-16" fill="none" stroke="#b59e78" stroke-width="2"/>
<path d="M285 872q-36-22-46 11l-2 55q-1 22 22 29l63 7 7-34-51-13 20-32" fill="url(#ivory)"/>
<use href="#smalljoint" x="257" y="937"/>
<path d="M321 938l36-5q11-2 14 5 1 6-11 9l-9 2 21 2q11 1 10 8-1 6-12 6l-19-2 13 6q9 4 5 10-4 4-14 0l-34-7Z" fill="#d8c99e" stroke-width="3"/>
<!-- Granny quietly reaches around the little one. -->
<path d="M432 860q24-5 34 25l11 29 68-17 12 30-83 33q-23 8-34-16l-25-53" fill="url(#ivory)"/>
<use href="#smalljoint" x="461" y="932"/>
<path d="M541 897q8-14 25-17l27 2q9 1 8 8-1 5-11 5l-18-1 23 8q9 4 6 10-3 5-12 1l-22-5 15 10q7 6 2 11-5 4-13-1l-18-12-5 10Z" fill="#e0cda2" stroke-width="3"/>
<path d="M331 780v36q23 20 43-2v-34" fill="#9aab90"/>
</g>
<!-- Granny's cathode-ray face, bifocals and little side coils. -->
<g transform="rotate(-7 340 729)" stroke="#283f3e" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<circle cx="237" cy="711" r="28" fill="#a4ae91"/>
<circle cx="451" cy="711" r="28" fill="#a4ae91"/>
<path d="M222 695q29-2 28 17-1 20-27 13M439 697q27-4 28 14-1 18-28 16" fill="none" stroke="#597a6a" stroke-width="3"/>
<path d="M242 674q2-32 39-33h120q41 2 41 35v108q-2 26-31 28H277q-37-2-37-35Z" fill="url(#ivory)"/>
<path d="M416 649q26 7 26 31v104q-2 26-31 28h-15q22-15 20-38Z" fill="#a9aa89" stroke="none"/>
<rect x="258" y="660" width="155" height="114" rx="29" fill="#586e5a" stroke-width="3"/>
<rect x="267" y="669" width="138" height="98" rx="23" fill="url(#screen)" stroke-width="3"/>
<rect x="267" y="669" width="138" height="98" rx="23" fill="url(#scan)" stroke="none"/>
<path d="M278 691q11-10 26-5m53 0q15-10 30-1" fill="none" stroke="#426650" stroke-width="3"/>
<path d="M283 714q10 11 21-2m58 1q11 11 23-2" fill="none" stroke="#365c49" stroke-width="4"/>
<path d="M320 743q16 10 29-2" fill="none" stroke="#365c49" stroke-width="3"/>
<path d="M274 701h39v25q-22 17-38-1ZM352 701h40l-2 25q-22 16-38-1Z" fill="#e5d9a7" fill-opacity=".13" stroke="#7b553e" stroke-width="3"/>
<path d="M313 710q20-12 39 0M259 704l15 6m118 0 24-7" stroke="#7b553e" stroke-width="3" fill="none"/>
<path d="M264 708q-19 77 24 94M414 708q18 65-16 91" fill="none" stroke="#b08a50" stroke-width="2" stroke-dasharray="2 5"/>
<path d="M284 788h59m-59 8h59" stroke="#75866c" stroke-width="2"/>
<circle cx="385" cy="791" r="9" fill="#c8945c" stroke-width="2"/><path d="M382 794l6-6" stroke-width="2"/>
<path d="M272 654q31-7 61-4" fill="none" stroke="#fff0c5" stroke-width="3"/>
<!-- An old-fashioned antenna bobbin. -->
<path d="M324 640l-13-35 46-4-9 40" fill="#b4b79a" stroke-width="3"/>
<path d="M316 612l38-5m-35 13 33-5m-31 12 29-4" stroke="#5e7a68" stroke-width="2"/>
<path d="M332 602l-7-23" stroke-width="3"/><circle cx="323" cy="575" r="7" fill="#d9bd84" stroke-width="2"/>
</g>
<!-- The child has yanked the tie into a wildly incorrect diagonal. -->
<g stroke="#2a4240" stroke-linejoin="round" stroke-linecap="round">
<path d="M471 510l18-4 11 22-18 18-16-20Z" fill="#a75443" stroke-width="3"/>
<path d="M482 543l13-8 74 290-22 19-22-18Z" fill="#bb6650" stroke-width="4"/>
<path d="M492 573l10-3m-5 28 13-4m-6 31 14-4m-7 33 16-4m-9 32 17-4m-7 31 14-4m-7 30 13-4m-6 29 13-3m-6 24 12-3" stroke="#e6b177" stroke-width="5"/>
</g>
<!-- Little legs swing freely, with shoes pointing in opposite directions. -->
<g stroke="#2a4240" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<path d="M604 963l-14 68 22 66 34-8-5-66 19-58" fill="url(#gold)"/>
<path d="M691 963l13 65-16 52 34 15 37-61-15-75" fill="url(#gold)"/>
<use href="#smalljoint" x="617" y="1030"/><use href="#smalljoint" x="732" y="1028"/>
<path d="M612 1085l31-5 19 21q10 18-5 26-48 13-77-6-9-22 32-36Z" fill="#b05f46"/>
<path d="M695 1075l31 15q32 2 40 25 1 15-14 20-44-2-73-25Z" fill="#b05f46"/>
<path d="M582 1118q35 15 75 4M682 1107q30 22 76 22" stroke="#e5bb81" stroke-width="3"/>
<path d="M612 1095l24 2m-30 8 29 2M714 1095l-10 12m22-7-9 14" stroke="#e5c59a" stroke-width="3"/>
<path d="M612 835l-35 38 2 87q60 44 166 10l7-104-36-35Z" fill="url(#gold)"/>
<path d="M725 854l27 12-7 104-22 6Z" fill="#b97e3a" stroke-width="3"/>
<path d="M599 878l-1 67" fill="none" stroke="#ffe0a0" stroke-width="4"/>
<rect x="626" y="883" width="69" height="55" rx="10" fill="#e5bd6b" stroke-width="3"/>
<path d="M640 898h12v12h-12Z" fill="#627f6b" stroke-width="2"/>
<circle cx="676" cy="904" r="7" fill="#ba6547" stroke-width="2"/>
<path d="M638 925h43" stroke="#956e3c" stroke-width="2"/>
<use href="#bolt" x="604" y="960"/><use href="#bolt" x="719" y="961"/>
<!-- The guilty fist holds the tie, not the adult's hand. -->
<path d="M595 858q-15-12-30-7l-21-26-24 19 34 42q15 15 40-1" fill="url(#gold)"/>
<use href="#smalljoint" x="560" y="870"/>
<path d="M518 831q-10-10-6-17 4-7 12 1l8 7-3-18q-1-11 6-11 7-1 9 10l4 19 4-15q3-9 10-6 6 3 1 13l-4 17 7 7q4 11-9 17l-17-1Z" fill="#edc479" stroke-width="3.5"/>
<!-- A very enthusiastic, very badly timed wave. -->
<path d="M746 861q22 0 28-20l14-68-29-9-34 69" fill="url(#gold)"/>
<use href="#smalljoint" x="771" y="814"/>
<path d="M758 773l-11-22-16-12q-8-7-2-13 5-5 13 2l10 8-4-33q-1-11 7-12 8 0 9 10l4 23 7-38q2-10 10-8 6 2 4 13l-5 36 13-26q5-10 12-6 7 4 1 13l-15 30 13-12q8-7 13-1 5 5-3 13l-28 35Z" fill="#edc479" stroke-width="3.5"/>
<path d="M763 746l18 6m-13-29 1 11m14-9-3 11m15-6-6 10" stroke="#9a783f" stroke-width="2"/>
<path d="M644 814l2 29q17 15 40-2l2-27" fill="#9b9e78"/>
<path d="M647 828h39" stroke-width="2"/>
</g>
<g transform="rotate(-13 657 767)" stroke="#2a4240" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<path d="M577 725q1-30 29-34h109q29 0 31 32v77q0 26-30 31H607q-30-3-30-29Z" fill="url(#gold)"/>
<path d="M721 695q24 4 25 30v75q0 26-30 31h-12q19-18 17-41Z" fill="#ba813c" stroke="none"/>
<rect x="590" y="710" width="140" height="75" rx="24" fill="url(#glass)" stroke-width="3"/>
<path d="M601 725q4-8 16-8h26" fill="none" stroke="#899d80" stroke-width="3"/>
<circle cx="621" cy="748" r="17" fill="#f3dfaa" stroke="none"/>
<circle cx="693" cy="747" r="13" fill="#f3dfaa" stroke="none"/>
<circle cx="624" cy="750" r="6" fill="#4b6b58" stroke="none"/><circle cx="696" cy="749" r="5" fill="#4b6b58" stroke="none"/>
<path d="M638 799q20 25 47-1Z" fill="#243f3b" stroke-width="3"/>
<path d="M649 800v9h11v-9" fill="#f8e4b7" stroke-width="2"/>
<path d="M597 792l9-1m107-1 7-1" stroke="#bc7043" stroke-width="5"/>
<rect x="560" y="737" width="16" height="41" rx="6" fill="#bd7545" stroke-width="3"/>
<rect x="746" y="737" width="16" height="41" rx="6" fill="#bd7545" stroke-width="3"/>
<path d="M650 691l-4-19 15-8-12-14 12-11" fill="none" stroke-width="3"/>
<circle cx="662" cy="635" r="8" fill="#d47950" stroke-width="3"/>
<path d="M590 699l37-1" stroke="#ffe2a2" stroke-width="3"/>
<use href="#bolt" x="602" y="812"/><use href="#bolt" x="715" y="811"/>
</g>
<!-- A small mechanical dog has brought the unplugged portrait-flash cable. -->
<ellipse cx="951" cy="1184" rx="137" ry="22" fill="#254640" opacity=".22"/>
<g stroke="#293f3d" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<path d="M933 1109q18-52 64-22 35 21 15 58l-12 27-80-4Z" fill="url(#ivory)"/>
<path d="M1006 1117q35-22 29-43-2-13-14-13" fill="none" stroke-width="12"/>
<path d="M1006 1117q35-22 29-43-2-13-14-13" fill="none" stroke="#bcae80" stroke-width="5"/>
<path d="M968 1130q31-5 35 24l-4 19 17 3q13 4 7 14h-50l-10-22" fill="#c4bb93" stroke-width="4"/>
<circle cx="981" cy="1150" r="12" fill="#8b9a7f" stroke-width="3"/>
<path d="M914 1133l-9 39-13 3q-12 7-5 15h46l12-52M941 1136l-1 39 13 1q10 6 4 15h-35" fill="url(#ivory)" stroke-width="4"/>
<path d="M915 1102l2 32 39 6 5-32" fill="#b15f45" stroke-width="4"/>
<circle cx="929" cy="1136" r="9" fill="#dfbd70" stroke-width="2"/>
<g transform="rotate(-17 927 1077)">
<path d="M886 1046q2-26 32-26h44q28 4 27 31l-9 54q-8 20-39 16l-46-6q-21-6-17-30Z" fill="url(#ivory)"/>
<path d="M952 1027q28-21 39 0l-5 58q-13 11-27-2Z" fill="#7e9380" stroke-width="4"/>
<path d="M882 1040q-18-11-25 4l-4 41q11 10 22 2" fill="#7e9380" stroke-width="4"/>
<path d="M888 1055q30-12 57 6l-3 31-55-1Z" fill="#2b4641" stroke-width="3"/>
<ellipse cx="905" cy="1071" rx="7" ry="10" fill="#f3d491" stroke="none"/>
<ellipse cx="933" cy="1071" rx="6" ry="9" fill="#f3d491" stroke="none"/>
<path d="M871 1086h31q16 0 16 16-1 13-18 15h-23q-19-4-16-18 0-8 10-13Z" fill="#d5c9a2" stroke-width="3"/>
<path d="M861 1092q14-8 23 0v10q-10 9-20 0Z" fill="#2a4540" stroke-width="3"/>
<path d="M883 1110h20" stroke-width="3"/>
<use href="#bolt" x="948" y="1105"/>
</g>
<!-- The loose lead is a quiet explanation for all the waiting. -->
<path d="M889 1114q-42 4-33 36 10 43-54 40-79-6-91 10-15 24 46 26 87 4 92-6" fill="none" stroke="#233d3b" stroke-width="5"/>
<g transform="translate(851 1219) rotate(-16)"><path d="M0-9h27v18H0Z" fill="#b76b4f" stroke-width="3"/><path d="M28-5h13m-13 10h13" fill="none" stroke="#c7b68b" stroke-width="4"/></g>
</g>
<!-- Tiny scuffs catch the light on well-loved metal. -->
<g fill="none" stroke="#f7e1b6" stroke-width="1.6" opacity=".6" stroke-linecap="round"><path d="M401 610l9-8m-7 17 16-14M545 351l-7 6M863 554l10-13m-7 20 11-12M288 915l9-8m-7 16 13-12M687 957l9-6m-6 11 12-9M1102 851l14-9m-7 14 12-8M959 1090l7-8"/></g>
<rect x="65" y="65" width="1310" height="1230" fill="url(#grain)" opacity=".28" pointer-events="none"/>
</g>
<rect x="65" y="65" width="1310" height="1230" rx="125" fill="none" stroke="#263f40" stroke-width="7"/>
<rect x="79" y="79" width="1282" height="1202" rx="112" fill="none" stroke="#d5c99f" stroke-width="1.5" opacity=".45"/>
<!-- Four quiet mounting rosettes, no lettering. -->
<g fill="#b49a6a" stroke="#647760" stroke-width="1.5">
<path d="M61 47l5 9 10 5-10 5-5 10-5-10-9-5 9-5ZM1379 47l5 9 10 5-10 5-5 10-5-10-9-5 9-5ZM61 1284l5 9 10 5-10 5-5 10-5-10-9-5 9-5ZM1379 1284l5 9 10 5-10 5-5 10-5-10-9-5 9-5Z"/>
</g>
</svg>''')
# Keep the published directory image-only; the generator lives beside it.
svg = '\n'.join(s)
(OUT / 'family_portrait.svg').write_text(svg)
print(f'Wrote {OUT / "family_portrait.svg"} ({len(svg):,} bytes)')

# Quick Look uses square thumbnails. Render on a square canvas, then remove
# only the extra bottom margin so that the exported PNG is not clipped.
import shutil
import subprocess
import tempfile
if shutil.which('qlmanage') and shutil.which('ffmpeg'):
    with tempfile.TemporaryDirectory(prefix='.portrait-render-', dir='.') as tmp:
        render_file = Path(tmp) / 'portrait.svg'
        render_file.write_text(svg.replace(
            'width="1440" height="1360" viewBox="0 0 1440 1360"',
            'width="1440" height="1440" viewBox="0 0 1440 1440"', 1))
        subprocess.run(['qlmanage', '-t', '-s', '1440', '-o', tmp,
                        str(render_file)], check=True, capture_output=True)
        subprocess.run(['ffmpeg', '-y', '-i', str(render_file) + '.png',
                        '-vf', 'crop=1440:1360:0:0', '-frames:v', '1',
                        str(OUT / 'family_portrait.png')],
                       check=True, capture_output=True)
    print(f'Wrote {OUT / "family_portrait.png"}')
