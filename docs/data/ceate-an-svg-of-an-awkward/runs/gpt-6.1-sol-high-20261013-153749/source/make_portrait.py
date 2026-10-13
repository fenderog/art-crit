from pathlib import Path
import random

OUT = Path('output')
OUT.mkdir(exist_ok=True)
parts = []
def add(s): parts.append(s)
def bolt(x,y,r=7):
    add(f'<g transform="translate({x} {y})"><circle r="{r}" fill="#c9c7ae" stroke="#293d3c" stroke-width="2"/><path d="M{-r*.45} {r*.45} L{r*.45} {-r*.45}" stroke="#667a73" stroke-width="2"/></g>')
def rivets(points,r=6):
    for x,y in points: bolt(x,y,r)
def joint(x,y,r=19,color='#859d95'):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" stroke="#293d3c" stroke-width="4"/><circle cx="{x}" cy="{y}" r="{r*.45}" fill="#314847"/><path d="M{x-r*.3} {y-r*.3}l{r*.6} {r*.6}" stroke="#b2b9a0" stroke-width="2"/>')

add('''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1280" viewBox="0 0 1440 1280">
<defs>
  <linearGradient id="paper" x2="0" y2="1"><stop stop-color="#f1e8ce"/><stop offset="1" stop-color="#daceaf"/></linearGradient>
  <linearGradient id="wall" x2="0.15" y2="1"><stop stop-color="#cbd2b8"/><stop offset=".55" stop-color="#a6b8a5"/><stop offset="1" stop-color="#819c90"/></linearGradient>
  <radialGradient id="glow" cx=".43" cy=".35" r=".65"><stop stop-color="#eff0cf" stop-opacity=".8"/><stop offset="1" stop-color="#d5dfbe" stop-opacity="0"/></radialGradient>
  <linearGradient id="floor" x2="0" y2="1"><stop stop-color="#d2af91"/><stop offset="1" stop-color="#b98770"/></linearGradient>
  <linearGradient id="blue" x2="1" y2=".25"><stop stop-color="#799eaa"/><stop offset=".45" stop-color="#527c89"/><stop offset="1" stop-color="#355e6b"/></linearGradient>
  <linearGradient id="mint" x2="1" y2=".45"><stop stop-color="#bed5b9"/><stop offset=".55" stop-color="#91b9a1"/><stop offset="1" stop-color="#638e7f"/></linearGradient>
  <linearGradient id="red" x2="1" y2=".4"><stop stop-color="#dc8c6f"/><stop offset=".5" stop-color="#c26b53"/><stop offset="1" stop-color="#995045"/></linearGradient>
  <linearGradient id="cream" x2="1" y2=".4"><stop stop-color="#eee1b5"/><stop offset=".5" stop-color="#cebd8e"/><stop offset="1" stop-color="#a3916c"/></linearGradient>
  <linearGradient id="gold" x2="1" y2=".3"><stop stop-color="#edbf65"/><stop offset=".5" stop-color="#d89c4d"/><stop offset="1" stop-color="#b5733c"/></linearGradient>
  <linearGradient id="screen" x2="0" y2="1"><stop stop-color="#243a38"/><stop offset="1" stop-color="#3e5952"/></linearGradient>
  <pattern id="mesh" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M0 4H8M4 0V8" stroke="#293d3c" stroke-width="1" opacity=".3"/></pattern>
  <pattern id="dots" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.2" fill="#283e3b" opacity=".18"/></pattern>
  <pattern id="rug" width="46" height="46" patternUnits="userSpaceOnUse" patternTransform="rotate(-7)"><path d="M0 23L23 0 46 23 23 46Z" fill="none" stroke="#eed7ae" stroke-width="1.4" opacity=".24"/><circle cx="23" cy="23" r="2" fill="#ecd6ae" opacity=".25"/></pattern>
  <clipPath id="picture"><rect x="62" y="62" width="1316" height="1156" rx="120"/></clipPath>
  <filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".67" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="linear" slope=".075"/></feComponentTransfer><feBlend in="SourceGraphic" mode="multiply"/></filter>
</defs>
<rect width="1440" height="1280" fill="url(#paper)"/>
<rect x="39" y="39" width="1362" height="1202" rx="136" fill="none" stroke="#796f55" stroke-width="2"/>
<rect x="49" y="49" width="1342" height="1182" rx="129" fill="none" stroke="#b3a78a"/>
<g clip-path="url(#picture)">
<rect x="62" y="62" width="1316" height="1156" fill="url(#wall)"/>
<path d="M190 1040V623C190 319 373 120 720 120S1250 319 1250 623V1040Z" fill="#8da79b" stroke="#718d81" stroke-width="3"/>
<path d="M222 1040V623C222 341 399 151 720 151S1218 341 1218 623V1040Z" fill="url(#wall)" stroke="#d7d9b5" stroke-width="2"/>
<rect x="62" y="62" width="1316" height="988" fill="url(#glow)"/>
<!-- Unevenly hung photographic curtains. -->
<path d="M62 62H290C256 192 171 284 62 314Z" fill="#8b6b4e"/>
<path d="M62 67H265C232 172 153 243 62 279Z" fill="#bc975f"/>
<path d="M84 62C95 145 86 207 62 253M136 62C145 141 114 222 82 255M193 62C190 149 145 210 105 236M248 62C216 143 184 181 156 204" fill="none" stroke="#d6b47a" stroke-width="9" opacity=".65"/>
<path d="M1378 62H1196C1242 272 1248 723 1378 1038Z" fill="#95714e"/>
<path d="M1378 62H1221C1263 269 1277 755 1378 970Z" fill="#be9c69"/>
<path d="M1249 66C1282 352 1298 713 1378 900M1290 67C1301 444 1344 654 1378 730M1336 69C1329 335 1357 443 1378 516" fill="none" stroke="#d7b780" stroke-width="10" opacity=".65"/>
<path d="M1264 570Q1321 597 1378 578L1378 603Q1329 624 1269 597Z" fill="#637f71" stroke="#40584e" stroke-width="3"/>
<path d="M1350 604Q1310 653 1338 727" fill="none" stroke="#dcc391" stroke-width="7"/>
<path d="M1338 716l-10 34m11-31 9 29m-9-30 0 33" stroke="#dcc391" stroke-width="5"/>
<!-- Barely visible studio seams and a crooked decorative star. -->
<path d="M716 154V279M714 194h10" stroke="#779688" stroke-width="2" opacity=".3"/>
<path d="M1030 240l9 18 21 1-14 16 5 21-20-10-18 12 3-22-16-14 22-3Z" fill="none" stroke="#c9cfac" stroke-width="3" transform="rotate(13 1030 269)"/>
<circle cx="334" cy="355" r="39" fill="none" stroke="#c7d0b0" stroke-width="2" opacity=".6"/>
<rect x="62" y="1016" width="1316" height="230" fill="url(#floor)"/>
<path d="M62 1018H1378M62 1032H1378" stroke="#687f70" stroke-width="3"/>
<path d="M191 1033L120 1218M432 1033L400 1218M735 1033L761 1218M1012 1033L1124 1218M1279 1033L1378 1151" stroke="#9e7860" opacity=".4" stroke-width="2"/>
<ellipse cx="745" cy="1132" rx="539" ry="125" fill="#94664f" opacity=".25"/>
<path d="M211 1059Q718 1014 1249 1067L1292 1169Q742 1232 155 1166Z" fill="#a36454" stroke="#dfbb90" stroke-width="5"/>
<path d="M228 1072Q718 1030 1233 1078L1262 1159Q730 1213 185 1155Z" fill="url(#rug)" stroke="#d6a781" stroke-width="2"/>
<path d="M169 1169l-9 18m30-16-7 18m29-15-6 18m1027-13 8 17m-29-15 8 17m-29-15 7 17" stroke="#dfbb90" stroke-width="3"/>
<g fill="#304740" opacity=".16"><ellipse cx="525" cy="1087" rx="156" ry="28"/><ellipse cx="831" cy="1088" rx="144" ry="27"/><ellipse cx="1093" cy="1124" rx="145" ry="24"/><ellipse cx="310" cy="1146" rx="125" ry="22"/><ellipse cx="717" cy="1158" rx="100" ry="24"/></g>
<!-- The eldest's slightly lopsided chair. -->
<g stroke="#344b42" stroke-linejoin="round">
<path d="M975 1102L955 779Q1090 736 1213 800L1217 1102" fill="none" stroke-width="17"/>
<path d="M979 809Q1090 781 1191 824L1194 994H985Z" fill="#536d5b" stroke-width="4"/>
<path d="M993 811L995 986M1180 827L1180 985" fill="none" stroke="#8b9a71" stroke-width="3"/>
<path d="M966 998Q1082 972 1210 1008L1212 1040Q1080 1065 966 1032Z" fill="#876448" stroke-width="4"/>
<path d="M978 1035L968 1145H950L955 1030M1186 1043L1212 1142H1228L1210 1039" fill="#6d7153" stroke-width="4"/>
<path d="M948 897L1006 912M1180 925L1230 909" stroke-width="13" stroke-linecap="round"/>
</g>
<!-- Father: broad-shouldered, determined to look formal. -->
<g stroke="#293d3c" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">
<path d="M467 798L460 966L504 972L527 804M581 802L588 974L630 975L637 802" fill="url(#blue)"/>
<path d="M467 847L515 852M464 859L513 864M586 850L632 849M588 862L631 862" stroke="#aac4bd" stroke-width="3"/>
<path d="M460 982L458 1038M501 982L499 1038M589 986L592 1038M629 986L634 1038" fill="none" stroke="#526f70" stroke-width="18"/>
<path d="M456 1032Q428 1035 416 1068L419 1085H524L528 1060 502 1037Z" fill="#354e52"/>
<path d="M590 1035L581 1065 587 1087H707Q704 1057 640 1035Z" fill="#354e52"/>
<path d="M423 1070H517M594 1071H696" stroke="#9fafa0" stroke-width="3"/>
<path d="M532 486V548H584V488" fill="#929f8d"/>
<path d="M535 514H582M535 525H582M535 536H582" stroke-width="3"/>
<path d="M424 548Q550 527 674 554L692 789Q674 818 546 825Q434 819 409 788Z" fill="url(#blue)"/>
<path d="M437 567Q551 549 657 570L667 767Q552 790 428 767Z" fill="none" stroke="#a9bcb0" stroke-width="2"/>
<path d="M501 549L545 594 484 633 464 556M606 550L552 594 614 628 644 559" fill="#9eb4ad"/>
<path d="M545 579L570 586 557 614 534 610Z" fill="#a95646"/>
<path d="M536 611L557 615 581 738 555 762 534 734Z" fill="#bd6b54"/>
<path d="M542 624L556 687" stroke="#e1a280" stroke-width="3"/>
<path d="M599 662H650V704H599Z" fill="#335966" stroke-width="3"/>
<path d="M610 663L611 643 620 656 627 640 633 657 641 650 641 663" fill="#e0d5b5" stroke-width="2"/>
<path d="M444 720H489M444 730H489M444 740H489" stroke="#315461" stroke-width="5"/>
<!-- One stiff arm reaches for the teenager. -->
<path d="M427 576Q400 565 384 599L351 665 379 682 432 620" fill="url(#blue)"/>
<path d="M369 658L345 682 335 660 351 638" fill="#a4b6a6"/>
<!-- The other arm is resolutely straight. -->
<path d="M675 570Q711 577 711 613L698 735 664 731 654 607" fill="url(#blue)"/>
<path d="M697 761L689 821 662 819 663 756" fill="#73948d"/>
<path d="M666 812Q651 815 649 833L648 865 660 870 666 847 668 874 681 876 686 849 688 868 700 865 702 833 692 815Z" fill="#c1c7ac" stroke-width="3"/>
<!-- Box head, not quite level. -->
<path d="M502 306L499 258" fill="none" stroke="#566e69" stroke-width="7"/>
<circle cx="498" cy="250" r="13" fill="#d5a052"/>
<path d="M420 332L438 311H649L669 332V481L649 501H439L419 479Z" fill="url(#blue)"/>
<path d="M436 326H641M434 334V463" stroke="#b1cbc1" stroke-width="4"/>
<path d="M424 368H408V431H424M667 369H683V431H667" fill="#788f85"/>
<rect x="443" y="350" width="201" height="108" rx="22" fill="url(#screen)" stroke-width="3"/>
<path d="M454 365Q544 352 628 365" fill="none" stroke="#8aaba0" stroke-width="2" opacity=".5"/>
<!-- Eyes looking at the unplugged cable, not the camera. -->
<circle cx="489" cy="401" r="19" fill="#d9dfb7" stroke="none"/>
<circle cx="595" cy="403" r="20" fill="#d9dfb7" stroke="none"/>
<circle cx="497" cy="409" r="8" fill="#2c413d" stroke="none"/>
<circle cx="604" cy="411" r="8" fill="#2c413d" stroke="none"/>
<path d="M470 377L501 380M578 368L611 363" stroke="#c0c9a4" stroke-width="5"/>
<path d="M518 442L579 437 581 448 519 449Z" fill="#c0c9a4" stroke-width="2"/>
<path d="M559 438V447M567 438V447" stroke="#415a4b" stroke-width="2"/>
<path d="M631 383Q647 406 635 410Q624 407 631 383Z" fill="#9eb9b1" stroke-width="2"/>
<path d="M487 477H574M588 477H618" stroke="#355b66" stroke-width="3"/>
</g>
''')
rivets([(437,341),(648,341),(438,476),(649,477),(423,782),(676,784)])
joint(481,973,24); joint(611,978,24); joint(690,743,22); joint(367,664,20)
add('''<!-- Mother: impeccable polish, a smile held a little too long. -->
<g stroke="#293d3c" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">
<path d="M771 830L765 1019H804L822 829M860 829L866 1022H906L909 831" fill="url(#mint)"/>
<path d="M764 956H810M764 967H808M866 959H906M867 970H906" stroke="#476e61" stroke-width="3"/>
<path d="M764 1021L745 1066 747 1084H829L824 1069 802 1021M866 1022L860 1068 864 1084H954L953 1067 906 1022" fill="#425d50"/>
<path d="M751 1071H821M872 1071H944" stroke="#a8bea0" stroke-width="3"/>
<path d="M800 497V552H862V499" fill="#b4bfa1"/>
<path d="M800 520H862M800 531H862" stroke-width="3"/>
<!-- Far arm wraps around the elder. -->
<path d="M941 574Q981 565 993 621L1011 729 975 740 946 638 929 613" fill="url(#mint)"/>
<path d="M980 741Q1015 771 1050 780L1060 751Q1030 735 1013 716" fill="#9fbaa2"/>
<path d="M734 555Q836 521 935 557L962 703 992 845Q839 889 699 844L725 707Z" fill="url(#mint)"/>
<path d="M750 578Q833 554 918 579L940 697 966 825Q842 855 728 825L752 695Z" fill="none" stroke="#d2dec0" stroke-width="2"/>
<path d="M733 552Q782 567 831 596Q881 566 934 554L919 616 886 606 834 634 780 606 748 617Z" fill="#dfe2bd"/>
<path d="M735 714Q837 740 958 713L964 739Q840 765 728 739Z" fill="#40695d"/>
<ellipse cx="841" cy="742" rx="24" ry="15" fill="#d8b35f" stroke-width="3"/>
<ellipse cx="841" cy="742" rx="10" ry="6" fill="#486f61" stroke-width="2"/>
<path d="M780 772L764 826M834 777L831 838M891 771L909 828" stroke="#658e7c" stroke-width="3"/>
<!-- Near arm will settle on the little one's head. -->
<path d="M735 581Q712 573 704 607L706 713 739 714 762 604" fill="url(#mint)"/>
<path d="M721 733L754 809 780 794 748 719" fill="#a8c8ab"/>
<!-- Sculptural head with a coiled, meticulously styled aerial. -->
<path d="M869 329C928 288 918 242 885 248C851 254 858 292 884 286C902 282 891 265 881 269" fill="none" stroke="#47685b" stroke-width="8"/>
<path d="M772 337Q823 290 894 328Q943 349 948 417L937 490Q830 545 747 490L734 416Q733 364 772 337Z" fill="url(#mint)"/>
<path d="M755 381Q771 336 822 331" fill="none" stroke="#e0e5c4" stroke-width="6"/>
<path d="M750 392Q837 362 931 393L921 467Q836 502 758 468Z" fill="url(#screen)" stroke-width="3"/>
<path d="M773 402Q792 386 812 400M862 400Q882 383 904 399" fill="none" stroke="#a6c6a1" stroke-width="4"/>
<path d="M776 419Q794 406 812 419M865 419Q884 406 902 419" fill="none" stroke="#e2e7bd" stroke-width="6"/>
<path d="M779 415l-6-8m15 5-3-9m111 12 7-9m-15 6 2-9" stroke="#e2e7bd" stroke-width="3"/>
<path d="M805 445Q839 460 876 444L868 467Q838 479 812 465Z" fill="#dedfb5" stroke-width="2"/>
<path d="M810 456Q837 466 873 453M828 453L827 470M849 454L850 470" fill="none" stroke="#668570" stroke-width="2"/>
<ellipse cx="772" cy="446" rx="9" ry="7" fill="#d39175" stroke="none"/>
<ellipse cx="911" cy="444" rx="9" ry="7" fill="#d39175" stroke="none"/>
<path d="M736 408L724 412V451L742 457M947 405L960 412V451L943 459" fill="#bac4a3"/>
<circle cx="733" cy="468" r="10" fill="#d9b45b" stroke-width="3"/>
<circle cx="953" cy="468" r="10" fill="#d9b45b" stroke-width="3"/>
<!-- A tiny flower pinned to the collar, with real bolts for petals. -->
<path d="M864 608L878 640M877 628L893 625" stroke="#426758" stroke-width="3"/>
<g fill="#d1a66a" stroke-width="2"><circle cx="862" cy="593" r="9"/><circle cx="874" cy="600" r="9"/><circle cx="870" cy="613" r="9"/><circle cx="855" cy="614" r="9"/><circle cx="850" cy="601" r="9"/></g>
<circle cx="862" cy="603" r="8" fill="#9d6450" stroke-width="2"/>
</g>
''')
joint(722,716,22,'#b7c8a7'); joint(993,732,21,'#b7c8a7')
rivets([(766,480),(919,481),(715,833),(977,833)],5)
add('''<!-- Teenager: leaning out of the family, arms firmly crossed. -->
<g transform="rotate(-9 325 878)" stroke="#293d3c" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">
<path d="M262 951L244 1050 268 1060 305 959M348 961L365 1054 390 1047 389 949" fill="#536866"/>
<path d="M247 1070L236 1119 263 1125 272 1077M371 1069L376 1111 400 1109 395 1066" fill="#979c85"/>
<path d="M236 1116L207 1136 208 1157H293L292 1141 264 1122M376 1108L356 1134 359 1154H442L438 1134 400 1108" fill="#485753"/>
<path d="M215 1145H287M366 1143H431" stroke="#d2c5a2" stroke-width="3"/>
<path d="M305 767V808H351V770" fill="#89958a"/>
<path d="M306 781H350M306 790H350" stroke-width="3"/>
<path d="M247 813L293 793 353 798 394 828 405 958Q327 988 244 952Z" fill="url(#red)"/>
<path d="M261 823L291 809 353 814 380 835M258 937Q328 961 391 944" fill="none" stroke="#efab88" stroke-width="3"/>
<path d="M283 803L304 835 327 816 348 840 365 809" fill="#b1af94"/>
<!-- A rebellious pin: an asymmetric lightning bolt, no lettering. -->
<circle cx="371" cy="852" r="16" fill="#3d5651" stroke-width="2"/>
<path d="M372 839L362 853 371 853 367 865 381 850 372 850Z" fill="#deb564" stroke="none"/>
<path d="M260 820Q226 821 228 858L260 902 290 885 268 852" fill="url(#red)"/>
<path d="M388 827Q417 841 407 871L374 918 347 901 376 859" fill="url(#red)"/>
<path d="M261 883L338 903 345 925 270 919 252 899Z" fill="#b6b59b"/>
<path d="M373 897L296 873 284 894 355 925 377 917Z" fill="#c9c5a6"/>
<path d="M292 877L274 875 269 883 275 890 287 891M338 906L354 906 358 916 350 923 341 922" fill="#d9cdab" stroke-width="3"/>
<!-- Angular head and one oversized audio receiver. -->
<path d="M306 642L311 606 342 594 334 576" fill="none" stroke="#697a6a" stroke-width="6"/>
<path d="M261 650L284 635H366L393 668 389 751 365 781H276L252 755Z" fill="url(#red)"/>
<path d="M274 650H357M266 661L265 699" stroke="#eeae8a" stroke-width="4"/>
<path d="M275 673H368L373 738 274 737Z" fill="url(#screen)" stroke-width="3"/>
<path d="M283 696H307M340 697H363" stroke="#d3d9b0" stroke-width="7"/>
<path d="M299 697V706M355 697V706" stroke="#d3d9b0" stroke-width="5"/>
<path d="M296 722L343 727" stroke="#c7caa6" stroke-width="4"/>
<path d="M289 681L310 684M340 684L364 681" stroke="#8d9f84" stroke-width="3"/>
<path d="M259 664Q320 613 387 660" fill="none" stroke="#344f48" stroke-width="9"/>
<rect x="240" y="683" width="27" height="54" rx="11" fill="#d1ae65"/>
<path d="M247 694V725M256 694V725" stroke="#816645" stroke-width="3"/>
<rect x="383" y="683" width="22" height="51" rx="9" fill="#d1ae65"/>
<path d="M390 694V723" stroke="#816645" stroke-width="3"/>
<path d="M282 756H300M309 757H325" stroke="#8a4b3e" stroke-width="3"/>
<path d="M275 930l12-3m2 11 15-4m52 8 20-5" stroke="#e7a181" stroke-width="2"/>
</g>
<!-- Dad's well-meant hand, unwelcome on the headphones. -->
<g stroke="#293d3c" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">
<path d="M354 645Q331 624 300 638L282 647Q275 653 284 659L306 655 289 667Q284 674 293 677L320 664 305 681Q303 689 312 689L338 671 325 688Q326 698 335 694L359 672Z" fill="#bcc4a7"/>
<path d="M315 642L342 655" fill="none" stroke="#899b84" stroke-width="2"/>
</g>
''')
# Knees, rotated with the teenager.
add('<g transform="rotate(-9 325 878)">')
joint(258,1063,18,'#b7b59a'); joint(383,1060,18,'#b7b59a')
rivets([(282,646),(367,655),(280,761),(371,754)],4)
add('</g>')
add('''<!-- Elder: warm, dented, drifting off, with a flower from the child. -->
<g transform="rotate(6 1101 863)" stroke="#293d3c" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">
<path d="M1026 969L1044 1067 1077 1064 1077 968M1110 974L1125 1071 1158 1064 1154 967" fill="#a59472"/>
<path d="M1048 1085L1038 1114H1107L1102 1097 1081 1083M1129 1088L1124 1117H1195L1192 1101 1160 1085" fill="#6c6b55"/>
<path d="M1047 1068L1051 1091M1076 1068L1078 1090M1128 1071L1135 1092M1156 1070L1160 1090" stroke="#667563" stroke-width="9"/>
<path d="M1074 784V818H1121V786" fill="#a39f7d"/>
<path d="M1074 797H1121M1074 807H1121" stroke-width="3"/>
<path d="M1027 820Q1096 800 1163 827L1190 960Q1103 1005 1007 965Z" fill="url(#cream)"/>
<path d="M1037 828Q1096 825 1157 835L1173 940Q1095 967 1026 945Z" fill="none" stroke="#f3dfb4" stroke-width="2"/>
<!-- Scalloped insulating shawl. -->
<path d="M1026 817L1049 811Q1099 846 1148 817L1165 825 1181 889Q1169 904 1156 890Q1140 909 1127 892Q1113 909 1096 896Q1082 910 1068 894Q1055 906 1041 891Q1026 899 1018 886Z" fill="#e6d9b3" stroke-width="3"/>
<path d="M1035 832L1042 875M1052 839L1058 878M1072 844L1077 880M1094 849V883M1114 847L1111 882M1135 839L1133 879M1154 835L1151 875" stroke="#b8ab86" stroke-width="2"/>
<path d="M1062 914H1146V947H1062Z" fill="#a89b74" stroke-width="2"/>
<path d="M1073 925H1136M1073 936H1136" stroke="#65705b" stroke-width="4"/>
<path d="M1025 840Q1000 837 998 869L1011 917 1040 907 1040 863M1168 846Q1197 851 1194 884L1176 920 1152 905 1170 871" fill="url(#cream)"/>
<path d="M1012 916L1069 936 1078 917 1036 895M1170 916L1117 937 1108 918 1150 897" fill="#b6b292"/>
<!-- Old-fashioned winding key. -->
<path d="M1203 694L1238 694" stroke="#647463" stroke-width="10"/>
<path d="M1237 694C1223 687 1229 663 1245 671C1260 679 1244 692 1237 694C1254 692 1269 706 1255 716C1240 727 1231 705 1237 694Z" fill="#bda46d" stroke-width="3"/>
<path d="M1024 663Q1097 615 1167 663L1200 690 1186 770Q1100 813 1019 774L1003 697Z" fill="url(#cream)"/>
<path d="M1020 682Q1090 645 1156 669" fill="none" stroke="#f0e0b7" stroke-width="5"/>
<!-- A beautifully old patch and a small dent. -->
<path d="M1124 650L1135 661 1145 648" fill="#ab976e" stroke-width="2"/>
<path d="M1033 749L1060 758 1054 780 1029 773Z" fill="#bda985" stroke-width="2"/>
<path d="M1019 697Q1095 668 1184 700L1174 748Q1096 775 1028 746Z" fill="#556a57" stroke-width="3"/>
<!-- Oversized spectacles: one sleepy eye and one cracked lens. -->
<ellipse cx="1058" cy="717" rx="32" ry="29" fill="#dbe1be" fill-opacity=".23"/>
<ellipse cx="1144" cy="715" rx="33" ry="30" fill="#dbe1be" fill-opacity=".23"/>
<path d="M1090 714Q1101 704 1111 714M1026 710L1009 704M1177 706L1194 700" fill="none"/>
<path d="M1041 721Q1059 730 1074 719M1127 717Q1143 725 1159 714" fill="none" stroke="#e2e0b3" stroke-width="4"/>
<path d="M1155 691L1145 704 1154 711 1140 724" fill="none" stroke="#bbcfb1" stroke-width="1.6"/>
<path d="M1069 775L1121 774 1128 763" fill="none" stroke="#4d614f" stroke-width="4"/>
<path d="M1079 768V775M1091 768V775M1103 768V775" stroke="#b5a579" stroke-width="2"/>
</g>
''')
add('<g transform="rotate(6 1101 863)">')
joint(1023,908,17,'#d0c09a'); joint(1165,914,17,'#d0c09a'); joint(1064,1076,16,'#adae8c'); joint(1144,1079,16,'#adae8c')
rivets([(1027,672),(1170,682),(1169,765),(1035,767)],4)
add('''<!-- Trembling fingers curled around a slightly bent mechanical daisy. -->
<g stroke="#293d3c" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">
<path d="M1089 938Q1096 889 1086 849L1100 824" fill="none" stroke="#597455" stroke-width="5"/>
<path d="M1091 889Q1066 895 1062 871Q1087 870 1091 889M1093 874Q1118 878 1127 855Q1101 849 1093 874" fill="#8b9e68"/>
<g transform="translate(1100 822) rotate(22)" fill="#e6c76e" stroke-width="2"><ellipse cy="-16" rx="8" ry="14"/><ellipse cx="16" rx="14" ry="8"/><ellipse cy="16" rx="8" ry="14"/><ellipse cx="-16" rx="14" ry="8"/><ellipse cy="-15" rx="6" ry="13" transform="rotate(45)"/><ellipse cy="-15" rx="6" ry="13" transform="rotate(135)"/><ellipse cy="-15" rx="6" ry="13" transform="rotate(225)"/><circle r="10" fill="#b9854a"/><path d="M-4 4L4-4" stroke="#6a694d"/></g>
<path d="M1065 917L1082 913Q1093 912 1095 921L1092 932 1077 934M1119 919L1104 916Q1094 915 1091 923L1094 934 1110 936" fill="#d8cba5"/>
<path d="M1075 922L1088 924M1109 926L1097 926" stroke="#899577" stroke-width="2"/>
</g></g>
<!-- Mother's hand, slightly too controlling on the elder's shoulder. -->
<g stroke="#293d3c" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">
<path d="M1039 754Q1057 746 1074 756L1089 778Q1090 786 1081 785L1069 771 1076 792Q1073 800 1066 796L1058 776 1062 797Q1058 805 1051 799L1046 778 1044 794Q1037 801 1032 793L1030 772Z" fill="#c1d1af"/>
</g>
<!-- A cable that should definitely still be plugged in. -->
<circle cx="643" cy="771" r="17" fill="#2e4749" stroke="#a7b8a5" stroke-width="3"/>
<circle cx="643" cy="771" r="7" fill="#d3b979"/>
<path d="M645 771C729 774 725 836 662 846S577 850 586 891" fill="none" stroke="#293d3c" stroke-width="11" stroke-linecap="round"/>
<path d="M645 771C729 774 725 836 662 846S577 850 586 891" fill="none" stroke="#b99165" stroke-width="4" stroke-linecap="round"/>
<!-- Youngest: delighted by the one thing they were told not to touch. -->
<g stroke="#293d3c" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">
<path d="M665 1036L640 1090 669 1100 696 1052M726 1052L749 1092 777 1078 757 1031" fill="#748e80"/>
<!-- Spring legs, one foot turned fully sideways. -->
<path d="M649 1106l23 10-27 5 21 11-21 5M758 1097l23 1-18 14 26-1-14 13" fill="none" stroke="#3a5147" stroke-width="8"/>
<path d="M649 1106l23 10-27 5 21 11-21 5M758 1097l23 1-18 14 26-1-14 13" fill="none" stroke="#c5c7a0" stroke-width="3"/>
<path d="M642 1134L608 1147 606 1164H685L680 1144 662 1136M774 1121L769 1150 789 1160 833 1143 826 1126 796 1123" fill="#9c6246"/>
<path d="M613 1155H678M783 1150L823 1136" stroke="#dfb47a" stroke-width="3"/>
<path d="M690 927V956H731V924" fill="#a5b49a"/>
<path d="M692 938H729M692 947H729" stroke-width="3"/>
<path d="M660 956Q709 942 754 956L778 1033Q719 1071 648 1040Z" fill="url(#gold)"/>
<path d="M669 967Q709 956 746 967L761 1027Q711 1046 665 1030Z" fill="none" stroke="#f2d093" stroke-width="2"/>
<rect x="682" y="984" width="56" height="36" rx="8" fill="#4a6454" stroke-width="3"/>
<circle cx="696" cy="1002" r="6" fill="#bdcc91" stroke="none"/>
<circle cx="724" cy="1002" r="6" fill="#ca7b50" stroke="none"/>
<path d="M699 1044L708 1050 714 1044 720 1049 728 1041" fill="none" stroke="#99663c" stroke-width="2"/>
<!-- Left arm holds the loose plug up as a prize. -->
<path d="M661 968L615 988 594 969 648 947" fill="#d8aa60"/>
<path d="M593 961L582 915 608 909 622 956" fill="#a6b493"/>
<path d="M583 909L574 897Q573 884 584 882L610 890 614 901 604 918Z" fill="#c8cca2" stroke-width="3"/>
<path d="M587 888L588 877 605 875 608 891Z" fill="#ab794e" stroke-width="3"/>
<path d="M590 876L587 864M600 875L598 863" stroke="#e4d2a2" stroke-width="5"/>
<path d="M578 893L593 896M581 901L597 904" stroke="#829577" stroke-width="2"/>
<!-- The other hand insists on holding onto mother. -->
<path d="M754 972L788 954 801 918 777 908 761 939 742 947" fill="#d6aa61"/>
<path d="M778 913L775 894Q774 886 782 887L789 900 790 883Q794 877 799 882L805 899 808 889Q815 886 818 893L814 916 800 925Z" fill="#cad1a9" stroke-width="3"/>
<!-- Lopsided rounded head. -->
<path d="M708 809L707 777 725 765 739 781" fill="none" stroke="#547460" stroke-width="6"/>
<circle cx="741" cy="782" r="8" fill="#bc7151" stroke-width="3"/>
<path d="M639 827Q711 797 780 834L789 909Q765 939 713 940Q664 940 636 913Z" fill="url(#gold)"/>
<path d="M652 833Q705 814 753 831" fill="none" stroke="#f7d591" stroke-width="5"/>
<path d="M649 849Q713 833 773 853L776 902Q715 925 648 903Z" fill="url(#screen)" stroke-width="3"/>
<ellipse cx="680" cy="872" rx="21" ry="23" fill="#d4dfae" stroke-width="2"/>
<ellipse cx="674" cy="872" rx="10" ry="12" fill="#304a3e" stroke="none"/>
<circle cx="669" cy="865" r="4" fill="#f5e5b9" stroke="none"/>
<path d="M736 873l15-7-16-8" fill="none" stroke="#d4dfae" stroke-width="6"/>
<path d="M705 895Q724 910 744 893" fill="none" stroke="#d4dfae" stroke-width="4"/>
<path d="M719 902L719 910 727 910 727 902" fill="#ece0b4" stroke-width="2"/>
<circle cx="655" cy="898" r="7" fill="#bc7253" stroke="none"/>
<circle cx="767" cy="894" r="7" fill="#bc7253" stroke="none"/>
<path d="M636 857L624 862V893L637 897M787 856L801 861V892L788 898" fill="#a3ae8a"/>
</g>
''')
joint(608,967,17,'#c4c69c'); joint(650,1098,16,'#c3c79e'); joint(765,1089,16,'#c3c79e')
rivets([(647,837),(778,843),(650,918),(774,915),(659,1031),(764,1028)],4)
add('''<!-- Mother's second hand rests on the child's crooked antenna. -->
<g stroke="#293d3c" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">
<path d="M760 792Q781 799 789 815L794 837Q791 844 784 839L779 824 778 844Q773 850 768 843L768 824 763 842Q755 846 753 838L755 820 748 834Q740 837 738 830L747 808Z" fill="#cad6b3"/>
<path d="M757 807L776 814" stroke="#819e82" stroke-width="2"/>
</g>
<!-- A robot cat has chosen the only person it trusts. -->
<g stroke="#293d3c" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
<path d="M1011 1115C1055 1124 1084 1103 1076 1074C1069 1049 1048 1072 1060 1088" fill="none" stroke="#293d3c" stroke-width="14"/>
<path d="M1011 1115C1055 1124 1084 1103 1076 1074C1069 1049 1048 1072 1060 1088" fill="none" stroke="#acb5a0" stroke-width="7"/>
<path d="M952 1087Q1019 1070 1034 1120L1017 1145H922L920 1126Z" fill="#82998b"/>
<path d="M977 1102L1009 1104M977 1112L1017 1114M977 1122L1019 1124" stroke="#455e51" stroke-width="3"/>
<path d="M933 1099L916 1061 945 1073 968 1056 977 1102" fill="#acb6a0"/>
<path d="M923 1072L935 1083M965 1067L958 1085" stroke="#c8c9ac" stroke-width="3"/>
<path d="M917 1097Q946 1081 973 1100L975 1126Q947 1141 918 1128Z" fill="#d2cfac"/>
<path d="M925 1110L936 1114M955 1113L966 1108" stroke="#435e4e" stroke-width="3"/>
<path d="M941 1121L947 1125 951 1120" fill="#9b6550" stroke-width="2"/>
<path d="M915 1118L900 1115M916 1125L901 1129M975 1115L987 1110M976 1123L990 1124" stroke-width="2"/>
<path d="M965 1131L965 1148H992Q1000 1143 990 1138L981 1137M926 1131L923 1148H947" fill="#a3ae94" stroke-width="3"/>
</g>
<!-- A fallen bolt and a formal shoe that has not quite found its mark. -->
<g transform="translate(544 1142) rotate(22)"><path d="M-16-6H9V6H-16Z" fill="#9b9c7d" stroke="#3b5042" stroke-width="2"/><path d="M7-10H16L22-4V4L16 10H7Z" fill="#c5bb91" stroke="#3b5042" stroke-width="2"/><path d="M-13-6V6M-7-6V6M-1-6V6" stroke="#566c54" stroke-width="2"/></g>
<path d="M453 1103l-4 11m5-5-11-3M858 1103l-5 12m0-6 11 4" stroke="#eee0b8" stroke-width="2" opacity=".6"/>
''')
# Delicate, deterministic surface freckles; restrained print texture.
random.seed(42)
add('<g fill="#f5e8c8" opacity=".15">')
for _ in range(650):
    x=random.uniform(65,1375); y=random.uniform(65,1215)
    r=random.choice([.5,.7,1,1.3])
    add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>')
add('''</g>
</g>
<rect x="62" y="62" width="1316" height="1156" rx="120" fill="none" stroke="#4d6252" stroke-width="3"/>
<!-- Print grain sits over the artwork, never over the paper border. -->
<rect x="64" y="64" width="1312" height="1152" rx="118" fill="#9b957c" opacity=".13" filter="url(#grain)" style="mix-blend-mode:multiply"/>
<g fill="#a89a73" stroke="#786d52" stroke-width="1.5"><path d="M80 39l7 4v8l-7 4-7-4v-8Z"/><path d="M1360 39l7 4v8l-7 4-7-4v-8Z"/><path d="M80 1225l7 4v8l-7 4-7-4v-8Z"/><path d="M1360 1225l7 4v8l-7 4-7-4v-8Z"/></g>
<g stroke="#e6dabc" stroke-width="2"><path d="M77 50l6-6M1357 50l6-6M77 1236l6-6M1357 1236l6-6"/></g>
</svg>''')
(OUT / 'family_portrait.svg').write_text('\n'.join(parts))
print(f'Wrote {OUT / "family_portrait.svg"}')
