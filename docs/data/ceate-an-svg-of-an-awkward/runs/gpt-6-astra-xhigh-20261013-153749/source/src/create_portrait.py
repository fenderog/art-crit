from pathlib import Path
import math
import random

# A hand-built vector illustration. Coordinates are in the portrait's 1440 x 1600
# viewBox; all lettering has deliberately been left out of the image.
OUT = Path(__file__).resolve().parent.parent / 'output'
OUT.mkdir(exist_ok=True)
s = []
def add(x): s.append(x)
def circle(x, y, r, fill, stroke=None, sw=3, extra=''):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"' + (f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '') + f' {extra}/>')
def ellipse(x, y, rx, ry, fill, extra=''):
    add(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" {extra}/>')
def bolt(x, y, r=7, fill='#e6c69b', angle=-35):
    circle(x, y, r, fill, '#293d42', 2)
    add(f'<path d="M{x-r*.48},{y} h{r*.96}" stroke="#293d42" stroke-width="2" transform="rotate({angle} {x} {y})"/>')
def joint(x, y, r, fill='#879c95'):
    circle(x, y, r, '#273e43', '#20353b', 3)
    circle(x-1, y-1, r*.72, fill, '#20353b', 2)
    circle(x, y, r*.31, '#d3c8aa', '#20353b', 2)
    add(f'<path d="M{x-r*.25},{y} h{r*.5}" stroke="#20353b" stroke-width="2.5"/>')
def gear(x, y, r, fill, teeth=12):
    pts=[]
    for i in range(teeth*4):
        a=math.pi*2*i/(teeth*4)
        rr=r if i%4 in (1,2) else r*.81
        pts.append(f'{x+math.cos(a)*rr:.2f},{y+math.sin(a)*rr:.2f}')
    add(f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="#263c41" stroke-width="3"/>')
    circle(x,y,r*.56,'#718b80','#263c41',3)
    bolt(x,y,r*.22)

add('''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1600" viewBox="0 0 1440 1600">
<defs>
  <linearGradient id="paper" x2="1" y2="1"><stop stop-color="#f8edda"/><stop offset="1" stop-color="#e8dac2"/></linearGradient>
  <radialGradient id="backdrop" cx="48%" cy="37%" r="76%"><stop stop-color="#667f7d"/><stop offset=".49" stop-color="#39585d"/><stop offset="1" stop-color="#253e49"/></radialGradient>
  <radialGradient id="halo"><stop stop-color="#bfc5a6" stop-opacity=".25"/><stop offset=".76" stop-color="#aab49d" stop-opacity=".09"/><stop offset="1" stop-color="#97aa9a" stop-opacity="0"/></radialGradient>
  <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#536e6d"/><stop offset="1" stop-color="#344f56"/></linearGradient>
  <linearGradient id="orange" x1="0" y1="0" x2=".95" y2=".6"><stop stop-color="#ecb270"/><stop offset=".48" stop-color="#d99559"/><stop offset="1" stop-color="#af6543"/></linearGradient>
  <linearGradient id="orangeSide" x2="1" y2="0"><stop stop-color="#b6744c"/><stop offset="1" stop-color="#87503a"/></linearGradient>
  <linearGradient id="ivory" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="#fff0cd"/><stop offset=".5" stop-color="#e7d9b7"/><stop offset="1" stop-color="#bfba9c"/></linearGradient>
  <linearGradient id="mint" x1="0" y1="0" x2="1" y2=".7"><stop stop-color="#d2dbc0"/><stop offset=".45" stop-color="#a9c4b0"/><stop offset="1" stop-color="#688e84"/></linearGradient>
  <linearGradient id="brass" x1="0" y1="0" x2="1" y2=".5"><stop stop-color="#ead192"/><stop offset=".48" stop-color="#c9a260"/><stop offset="1" stop-color="#957643"/></linearGradient>
  <linearGradient id="purple" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#b2a2ae"/><stop offset=".45" stop-color="#8e839b"/><stop offset="1" stop-color="#625e7b"/></linearGradient>
  <linearGradient id="yellow" x1="0" y1="0" x2="1" y2=".7"><stop stop-color="#f8d26f"/><stop offset=".55" stop-color="#dfb749"/><stop offset="1" stop-color="#c78d3e"/></linearGradient>
  <linearGradient id="red" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#db8b78"/><stop offset="1" stop-color="#aa5e53"/></linearGradient>
  <linearGradient id="steel" x2="1" y2="0"><stop stop-color="#5b7779"/><stop offset=".3" stop-color="#c6d0b8"/><stop offset=".53" stop-color="#809995"/><stop offset="1" stop-color="#415e63"/></linearGradient>
  <linearGradient id="visor" x1="0" y1="0" x2=".9" y2="1"><stop stop-color="#344e52"/><stop offset="1" stop-color="#20343d"/></linearGradient>
  <pattern id="mesh" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="10" height="10" fill="#665d45"/><circle cx="3" cy="3" r="1.7" fill="#303e3c"/><circle cx="7" cy="8" r="1.1" fill="#303e3c"/></pattern>
  <pattern id="stoolWeave" width="9" height="9" patternUnits="userSpaceOnUse"><rect width="9" height="9" fill="#925e57"/><path d="M0 2h9M2 0v9" stroke="#d89a83" stroke-width=".8" opacity=".26"/></pattern>
  <clipPath id="photo"><rect x="62" y="62" width="1316" height="1476" rx="5"/></clipPath>
  <filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".73" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="linear" slope=".18"/></feComponentTransfer><feBlend in="SourceGraphic" mode="soft-light"/></filter>
</defs>
<rect width="1440" height="1600" fill="url(#paper)"/>
<rect x="53" y="54" width="1334" height="1494" rx="6" fill="#998b75" opacity=".2"/>
<g clip-path="url(#photo)">
<rect x="62" y="62" width="1316" height="1476" fill="url(#backdrop)"/>
<ellipse cx="696" cy="657" rx="613" ry="696" fill="url(#halo)"/>
<!-- The folds of a well-used studio sweep. -->
<g fill="none" stroke-linecap="round">
 <path d="M147 62C197 353 108 710 151 1093" stroke="#93a49a" stroke-width="42" opacity=".035"/>
 <path d="M1241 62C1187 465 1325 696 1276 1094" stroke="#132f3c" stroke-width="66" opacity=".09"/>
 <path d="M299 62C267 218 287 329 247 530" stroke="#bdc9aa" stroke-width="2" opacity=".055"/>
 <path d="M1020 62C981 326 1028 483 1103 609" stroke="#c2cbb0" stroke-width="3" opacity=".035"/>
</g>
<path d="M62 1103Q720 1024 1378 1103V1538H62Z" fill="url(#floor)"/>
<path d="M62 1120Q720 1041 1378 1120" fill="none" stroke="#aab6a0" stroke-width="2" opacity=".06"/>
<!-- Softly printed, layered contact shadows. -->
<ellipse cx="736" cy="1370" rx="567" ry="73" fill="#1f3942" opacity=".22"/>
<ellipse cx="586" cy="1357" rx="158" ry="32" fill="#1e3540" opacity=".42"/>
<ellipse cx="307" cy="1360" rx="172" ry="31" fill="#1e3540" opacity=".39"/>
<ellipse cx="962" cy="1369" rx="154" ry="25" fill="#1e3540" opacity=".39"/>
<ellipse cx="1200" cy="1369" rx="132" ry="24" fill="#1e3540" opacity=".35"/>
<g stroke="#263c41" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<!-- Grandmother's stool: the only piece of studio furniture. -->
<path d="M199 1134L181 1347Q191 1360 207 1348L241 1142M391 1136L430 1347Q439 1358 453 1346L434 1130" fill="#675345"/>
<path d="M210 1264L418 1266" fill="none" stroke="#b98b62" stroke-width="12"/>
<rect x="164" y="1089" width="282" height="89" rx="25" fill="url(#stoolWeave)"/>
<path d="M167 1116Q302 1144 443 1115M184 1148Q309 1168 426 1145" fill="none" stroke="#e0a18b" stroke-width="3"/>
<path d="M185 1173H428" stroke="#493e3b"/>
<!-- Father's very straight, very formal legs. -->
<path d="M478 966L474 1138L548 1144L560 969Z" fill="url(#orangeSide)"/>
<path d="M646 970L658 1141L729 1139L733 969Z" fill="url(#orangeSide)"/>
<path d="M495 996L494 1119M678 997L684 1117" stroke="#e0b37b" stroke-width="10"/>
<path d="M510 1118V1282M693 1118L703 1287" stroke="#263c41" stroke-width="43"/>
<path d="M507 1135V1282M691 1136L701 1284" stroke="url(#steel)" stroke-width="26"/>
<path d="M477 1190L549 1193L552 1308L477 1308Z" fill="url(#orange)"/>
<path d="M665 1194L736 1189L747 1307L671 1311Z" fill="url(#orange)"/>
<path d="M486 1204V1286M678 1207L684 1289" stroke="#edbe7e" stroke-width="5"/>
<path d="M474 1303Q464 1322 444 1329L419 1341Q409 1352 421 1365H553Q566 1355 560 1338L549 1304Z" fill="#374e50"/>
<path d="M671 1306L660 1340Q656 1357 670 1365H800Q810 1353 797 1344L747 1310Z" fill="#374e50"/>
<path d="M420 1350H555M670 1350H796" stroke="#b7baa0" stroke-width="4"/>
<path d="M452 1330L490 1331M730 1330L767 1340" stroke="#71918a" stroke-width="6"/>
</g>''')
joint(512,1147,39,'#b28455'); joint(697,1147,39,'#b28455')
for x,y in [(489,1207),(537,1293),(679,1208),(729,1291)]: bolt(x,y,5)

add('''<g stroke="#263c41" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<!-- Arms behind the adults. Dad's embrace is somewhat too emphatic. -->
<path d="M774 651Q862 579 918 605L1021 657" fill="none" stroke="#263c41" stroke-width="60"/>
<path d="M774 651Q862 579 918 605L1021 657" fill="none" stroke="url(#orange)" stroke-width="45"/>
<path d="M805 629Q862 598 896 609" fill="none" stroke="#f1bc80" stroke-width="5"/>
<path d="M436 649L408 766L380 850" fill="none" stroke="#263c41" stroke-width="66"/>
<path d="M436 649L408 766L380 850" fill="none" stroke="url(#orange)" stroke-width="53"/>
<path d="M413 699L399 745M391 801L383 825" fill="none" stroke="#f3bf80" stroke-width="6"/>
<!-- Father's torso is a little like a well-loved upright toolbox. -->
<path d="M468 599Q432 602 426 638L433 933Q435 981 469 990L741 991Q780 982 783 943L793 648Q791 620 761 609Z" fill="url(#orangeSide)"/>
<path d="M469 599L737 609Q761 612 763 644L756 925Q756 955 730 959L474 952Q449 950 446 920L440 642Q441 608 469 599Z" fill="url(#orange)"/>
<path d="M469 613L723 623M453 650L460 897" fill="none" stroke="#f5c183" stroke-width="5"/>
<path d="M478 655Q479 640 495 640L711 647Q729 648 730 666L726 849Q724 868 706 868L496 862Q479 861 478 844Z" fill="url(#ivory)" stroke-width="4"/>
<path d="M484 674L495 846L714 852" fill="none" stroke="#fff0cc" stroke-width="3"/>
<path d="M572 582V621Q607 639 643 620V581Z" fill="#364d50"/>
<path d="M575 593H640M575 604H640M580 615H637" stroke="#b4b9a0" stroke-width="4"/>
<path d="M567 620L608 647L566 687L531 639Z" fill="#5a7972"/>
<path d="M645 622L608 647L658 689L687 645Z" fill="#5a7972"/>
<path d="M595 643L624 647L631 680L611 695L594 674Z" fill="#314f55"/>
<path d="M611 690L630 684L666 803L640 837L611 813Z" fill="#314f55"/>
<path d="M618 711L643 797" stroke="#77958a" stroke-width="4"/>
<path d="M493 741H555V787Q526 799 497 786Z" fill="#b8bca0" stroke-width="3"/>
<path d="M505 742L503 711M518 742L519 721" stroke="#4f7373" stroke-width="7"/>
<path d="M533 741L535 718" stroke="#c38161" stroke-width="7"/>
<path d="M493 749H555" stroke="#efdfb9" stroke-width="3"/>
<rect x="511" y="891" width="179" height="52" rx="12" fill="#354f50" stroke-width="4"/>
<path d="M458 972L748 977" stroke="#d7a069" stroke-width="4"/>
<path d="M769 683L764 847" stroke="#674a39" stroke-width="5"/>
</g>''')
joint(431,653,43,'#d9a268'); joint(408,773,32,'#94947b')
for x,y in [(465,628),(742,639),(469,925),(741,933)]: bolt(x,y,8)
circle(547,916,18,'#e5d4ad','#263c41',3)
add('<path d="M535 920A13 13 0 0 1 557 907" stroke="#668f86" stroke-width="3" fill="none"/><path d="M547 916L552 906" stroke="#ab5b4b" stroke-width="3"/>')
for i,fill in enumerate(['#dca370','#d9866c','#8fae97']):
    circle(595+i*30,917,7,fill,'#1d373d',2)
    circle(593+i*30,915,2,'#f2dbac')

# Father's head.
add('''<g transform="rotate(-3 605 440)" stroke="#263c41" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<path d="M557 303L551 274L538 264" fill="none" stroke-width="9"/>
<circle cx="536" cy="258" r="15" fill="#df8b6f"/>
<circle cx="532" cy="253" r="4" fill="#f6d2a0" stroke="none"/>
<path d="M714 314L756 342V518L714 550H500V315Z" fill="url(#orangeSide)"/>
<rect x="445" y="373" width="27" height="88" rx="12" fill="#6b7f73"/>
<path d="M448 389H463M448 405H463M448 421H463M448 437H463" stroke="#bbbc99" stroke-width="3"/>
<rect x="463" y="303" width="262" height="244" rx="35" fill="url(#orange)"/>
<path d="M480 337Q480 317 502 317H693" fill="none" stroke="#f4c287" stroke-width="5"/>
<rect x="485" y="336" width="215" height="166" rx="22" fill="#896f51" stroke-width="4"/>
<rect x="492" y="341" width="201" height="152" rx="18" fill="url(#ivory)" stroke-width="3"/>
<path d="M507 370L550 366M622 365L669 376" fill="none" stroke="#536961" stroke-width="8"/>
<circle cx="535" cy="399" r="22" fill="#2d464a" stroke-width="3"/>
<circle cx="642" cy="399" r="22" fill="#2d464a" stroke-width="3"/>
<circle cx="539" cy="400" r="10" fill="#d6d9ae" stroke="none"/>
<circle cx="646" cy="400" r="10" fill="#d6d9ae" stroke="none"/>
<circle cx="541" cy="401" r="4" fill="#263c41" stroke="none"/>
<circle cx="648" cy="401" r="4" fill="#263c41" stroke="none"/>
<path d="M586 411L579 432H595" fill="none" stroke="#9a9578" stroke-width="3"/>
<path d="M544 455L655 457L649 475H551Z" fill="#4e6560" stroke-width="3"/>
<path d="M563 457L567 473M586 458L588 474M609 458L609 474M631 458L629 474" stroke="#e5d7b2" stroke-width="5"/>
<path d="M533 517H570M627 519H686" stroke="#b17b50" stroke-width="3"/>
<path d="M736 362V395M736 411V444M736 460V493" stroke="#442f2e" stroke-width="5"/>
<path d="M741 362V394M741 411V443M741 460V492" stroke="#c28a5a" stroke-width="2"/>
</g>''')
add('<g transform="rotate(-3 605 440)">')
for x,y in [(479,359),(710,358),(480,510),(709,511)]: bolt(x,y,6)
add('</g>')

# Mother: crossed ankles, enamel shell, a fussing hand.
add('''<g stroke="#263c41" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<path d="M865 1036L876 1171L926 1303" fill="none" stroke="#263c41" stroke-width="36"/>
<path d="M865 1036L876 1171L926 1303" fill="none" stroke="url(#steel)" stroke-width="24"/>
<path d="M945 1040L958 1172L900 1308" fill="none" stroke="#263c41" stroke-width="36"/>
<path d="M945 1040L958 1172L900 1308" fill="none" stroke="url(#steel)" stroke-width="24"/>
<path d="M861 1085L890 1083L898 1156L868 1161Z" fill="url(#mint)"/>
<path d="M936 1084L964 1083L973 1157L944 1162Z" fill="url(#mint)"/>
<path d="M904 1298Q926 1281 942 1301L956 1329L1001 1342Q1011 1347 1005 1359L923 1362Q904 1358 902 1345Z" fill="url(#mint)"/>
<path d="M884 1297Q903 1288 916 1309L913 1340Q906 1357 887 1360L836 1358Q825 1344 840 1336L868 1327Z" fill="url(#ivory)"/>
<path d="M835 1349H891M925 1351L1002 1352" stroke="#739389" stroke-width="4"/>
<!-- Her right arm insists on including the reluctant teenager. -->
<path d="M978 698L1030 802L1102 791" fill="none" stroke="#263c41" stroke-width="47"/>
<path d="M978 698L1030 802L1102 791" fill="none" stroke="url(#mint)" stroke-width="35"/>
<path d="M1010 775L1029 791L1081 787" fill="none" stroke="#dce0c3" stroke-width="4"/>
<!-- Skirt-like overlapping body armor. -->
<path d="M849 640Q901 619 953 648Q980 659 985 712L994 879L973 936L1010 1011Q1019 1044 983 1058Q903 1087 818 1046Q799 1036 809 1013L842 935L811 868L806 719Q806 664 849 640Z" fill="url(#mint)"/>
<path d="M955 665Q977 769 967 864L946 934L981 1039" fill="none" stroke="#60877e" stroke-width="9"/>
<path d="M835 690Q831 785 842 857" fill="none" stroke="#e4e5c7" stroke-width="5"/>
<path d="M858 686Q902 673 942 691L956 817Q955 860 902 876Q852 863 843 827Z" fill="url(#ivory)" stroke-width="4"/>
<path d="M864 699Q892 688 924 696" fill="none" stroke="#fff0cc" stroke-width="4"/>
<path d="M848 931Q905 948 974 932L979 950Q909 968 839 950Z" fill="url(#red)" stroke-width="3"/>
<circle cx="910" cy="949" r="11" fill="#d8c6a5" stroke-width="3"/>
<path d="M838 985L826 1024M859 985L851 1033M957 985L971 1035" stroke="#658b82" stroke-width="3"/>
<path d="M834 1042Q898 1068 973 1050" fill="none" stroke="#d6ddbc" stroke-width="4"/>
<path d="M874 602V642Q900 661 930 642L936 602Z" fill="#476b68"/>
<path d="M879 615L931 619M878 627L929 631" stroke="#c8d3b6" stroke-width="4"/>
<path d="M863 650Q874 681 902 693Q929 682 946 653" fill="none" stroke="#546e62" stroke-width="3"/>
<!-- The arm fussing with his crooked tie. -->
<path d="M813 704L753 814L694 778" fill="none" stroke="#263c41" stroke-width="48"/>
<path d="M813 704L753 814L694 778" fill="none" stroke="url(#mint)" stroke-width="36"/>
<path d="M797 731L772 777M738 797L710 779" stroke="#e0e4c5" stroke-width="5"/>
</g>''')
joint(875,1174,24,'#9fb5a1'); joint(956,1172,24,'#9fb5a1')
joint(814,704,29,'#b1c5ac'); joint(755,811,24,'#789c90'); joint(981,703,29,'#b1c5ac'); joint(1030,800,22,'#90ad9a')
for x,y,r in [(865,659,6),(874,672,6),(886,683,6),(901,688,7),(916,683,6),(929,672,6),(939,658,6)]:
    circle(x,y,r,'#eadbbe','#657e70',2)
add('''<path d="M903 704Q885 724 902 736Q922 725 903 704Z" fill="#c67561" stroke="#263c41" stroke-width="3"/>
<path d="M900 715L897 723" stroke="#f2bf8d" stroke-width="3" stroke-linecap="round"/>
<g stroke="#263c41" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
<path d="M704 769L682 751Q675 746 668 751L649 764Q643 770 649 777Q654 782 660 777L676 769L684 780L668 789L654 784Q644 782 644 790Q644 798 653 801L674 811Q682 814 691 806L711 788Z" fill="url(#mint)"/>
<path d="M684 780L694 789M652 769L659 775M652 789L649 797" fill="none" stroke="#73998c" stroke-width="3"/>
</g>''')
for x,y in [(825,920),(984,1007),(852,849),(945,833)]: bolt(x,y,5,'#d6d5af')

# Mother's head: affectionate tilt, nervous smile, eyes checking on the teenager.
add('''<g transform="rotate(9 906 492)" stroke="#263c41" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round">
<path d="M815 413Q804 348 849 348Q875 354 871 386" fill="url(#mint)"/>
<path d="M827 398Q822 363 847 362" fill="none" stroke="#e1e5c5" stroke-width="4"/>
<ellipse cx="1009" cy="482" rx="24" ry="41" fill="#76998a"/>
<ellipse cx="1009" cy="482" rx="11" ry="26" fill="#314d4c" stroke-width="3"/>
<path d="M800 463Q803 374 891 370Q980 362 1003 438L1008 514Q1003 582 927 603Q842 601 815 538Z" fill="url(#mint)"/>
<path d="M813 445Q820 394 871 387" fill="none" stroke="#e9eacb" stroke-width="5"/>
<path d="M808 463Q840 447 851 412Q899 442 996 435" fill="none" stroke="#668d80" stroke-width="3"/>
<path d="M843 454Q909 436 970 453L979 504Q973 538 920 543Q859 542 841 513Z" fill="url(#visor)"/>
<path d="M853 463Q867 454 885 461M930 455Q950 447 965 462" fill="none" stroke="#b7cbb0" stroke-width="3"/>
<path d="M855 489Q871 475 888 489M931 486Q947 472 963 486" fill="none" stroke="#e8dcb5" stroke-width="7"/>
<circle cx="883" cy="492" r="5" fill="#e8dcb5" stroke="none"/>
<circle cx="958" cy="489" r="5" fill="#e8dcb5" stroke="none"/>
<path d="M904 506L901 514L913 514" fill="none" stroke="#668c7e" stroke-width="2.5"/>
<path d="M887 564Q914 577 943 556" fill="none" stroke="#3c5e57" stroke-width="4"/>
<path d="M895 564L895 569M906 566L907 572M918 565L920 570M930 560L933 565" stroke="#e8e3c0" stroke-width="3"/>
<ellipse cx="847" cy="536" rx="11" ry="6" fill="#d58d75" stroke="none" opacity=".8"/>
<ellipse cx="975" cy="531" rx="10" ry="6" fill="#d58d75" stroke="none" opacity=".8"/>
<path d="M971 385L979 396M982 400L985 407" stroke="#64877b" stroke-width="3"/>
</g>''')
add('<g transform="rotate(9 906 492)">')
bolt(819,484,6,'#d5d7b7'); bolt(991,548,6,'#d5d7b7')
add('</g>')

# Father's hand on the far shoulder, placed after the mother's enamel shell.
add('''<g stroke="#263c41" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">
<path d="M1001 649Q1039 644 1054 670L1060 712Q1059 725 1048 725Q1037 725 1037 714L1033 688L1028 687L1036 725Q1037 737 1026 740Q1015 741 1012 728L1005 696L1000 694L1009 726Q1011 738 1001 741Q990 743 986 730L974 691Q970 678 981 669Z" fill="url(#orange)"/>
<path d="M1038 703L1057 700M1011 713L1032 709M990 714L1006 709" stroke="#6f5845" stroke-width="3"/>
<path d="M986 679Q1005 661 1026 673" fill="none" stroke="#f4c08a" stroke-width="4"/>
</g>''')
bolt(1006,682,7)

# Grandmother: squat brass radio, old-fashioned spectacles, flower brooch, cane.
add('''<g stroke="#263c41" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<path d="M232 1107L220 1207L237 1288M349 1114L367 1198L352 1290" fill="none" stroke="#263c41" stroke-width="47"/>
<path d="M232 1107L220 1207L237 1288M349 1114L367 1198L352 1290" fill="none" stroke="url(#steel)" stroke-width="34"/>
<path d="M211 1230L244 1225L256 1295L222 1300Z" fill="url(#brass)"/>
<path d="M351 1229L380 1229L372 1300L338 1301Z" fill="url(#brass)"/>
<path d="M221 1289Q244 1278 258 1299L258 1327Q255 1343 237 1343H178Q165 1333 178 1322L211 1309Z" fill="url(#brass)"/>
<path d="M338 1295L371 1293L392 1316L409 1324Q417 1332 408 1342H349Q334 1341 332 1329Z" fill="url(#brass)"/>
<path d="M180 1332H250M341 1332H406" stroke="#806444" stroke-width="3"/>
<!-- Winding key peeping out from behind her left shoulder. -->
<path d="M210 925L158 888" fill="none" stroke="#273f40" stroke-width="19"/>
<path d="M210 925L158 888" fill="none" stroke="#ba985a" stroke-width="12"/>
<path d="M162 891C125 901 117 875 132 862C142 854 155 861 164 872C153 850 162 827 178 833C196 840 188 869 175 886Z" fill="url(#brass)" stroke-width="4"/>
<path d="M145 875L150 879M176 851L175 858" stroke="#e7c987" stroke-width="4"/>
<!-- Torso and arms. -->
<path d="M207 893Q249 866 338 876Q380 882 397 929L407 1065Q412 1116 361 1131Q277 1155 205 1120Q180 1107 184 1063L183 953Q183 915 207 893Z" fill="url(#brass)"/>
<path d="M206 932Q204 989 210 1065" fill="none" stroke="#f1d79d" stroke-width="5"/>
<path d="M370 937L385 1068Q389 1098 358 1112" fill="none" stroke="#846b43" stroke-width="7"/>
<path d="M241 860V891Q275 910 308 891V859Z" fill="#526a5d"/>
<path d="M245 872H305M245 883H305" stroke="#bea776" stroke-width="4"/>
<path d="M233 943Q279 926 341 943L354 1062Q301 1090 232 1066Z" fill="url(#mesh)" stroke-width="4"/>
<path d="M241 962L343 962M239 983L346 983M237 1004L348 1004M236 1025L351 1025M235 1046L353 1046" stroke="#ddbd7e" stroke-width="6"/>
<path d="M230 1099Q287 1119 350 1100" fill="none" stroke="#f0d095" stroke-width="3"/>
<path d="M188 952L157 1015L166 1100" fill="none" stroke="#263c41" stroke-width="40"/>
<path d="M188 952L157 1015L166 1100" fill="none" stroke="url(#brass)" stroke-width="29"/>
<path d="M172 966L157 996" stroke="#f0d198" stroke-width="4"/>
<!-- The cane. -->
<path d="M148 1122V1106Q148 1081 172 1081Q195 1081 195 1104" fill="none" stroke="#263c41" stroke-width="19"/>
<path d="M148 1122V1106Q148 1081 172 1081Q195 1081 195 1104" fill="none" stroke="#c5ac79" stroke-width="11"/>
<path d="M148 1118L140 1360" stroke="#263c41" stroke-width="15"/>
<path d="M147 1131L140 1354" stroke="#a38d62" stroke-width="8"/>
<path d="M131 1360H149L152 1374H128Z" fill="#263c41" stroke-width="3"/>
<path d="M149 1088L172 1085Q184 1087 184 1098L182 1121Q182 1132 171 1134L153 1133Q143 1130 144 1120Z" fill="url(#brass)" stroke-width="4"/>
<path d="M146 1101L168 1100M145 1112L168 1112M146 1123H167" stroke="#6c694d" stroke-width="3"/>
<!-- Her long, old telescopic arm reaches over to the child. -->
<path d="M388 948L451 1007L547 985" fill="none" stroke="#263c41" stroke-width="41"/>
<path d="M388 948L451 1007L547 985" fill="none" stroke="url(#brass)" stroke-width="29"/>
<path d="M467 1003L519 991" stroke="#536b62" stroke-width="20"/>
<path d="M470 998L518 987" stroke="#c3c7a6" stroke-width="7"/>
</g>''')
joint(220,1203,26,'#ad9c6a'); joint(366,1200,26,'#ad9c6a')
joint(192,952,28,'#b99c63'); joint(157,1016,22,'#949676'); joint(389,951,29,'#bfa265'); joint(451,1006,23,'#9c9c76')
for x,y in [(212,915),(370,913),(207,1099),(375,1090)]: bolt(x,y,6,'#dbbe83')
# Flower brooch, a small organic touch on a machine.
add('<g stroke="#594c3c" stroke-width="2">')
for k in range(6):
    a=k*math.pi/3
    ellipse(round(322+math.cos(a)*12,2),round(916+math.sin(a)*12,2),7,10,'#c47b65',f'transform="rotate({k*60-90} {322+math.cos(a)*12:.2f} {916+math.sin(a)*12:.2f})"')
circle(322,916,7,'#e9ca7b','#594c3c',2)
add('</g>')

add('''<g transform="rotate(-8 284 761)" stroke="#263c41" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round">
<path d="M241 668L236 632Q235 621 244 620L252 620" fill="none" stroke="#405b56" stroke-width="7"/>
<circle cx="260" cy="619" r="12" fill="#a0b99a"/>
<path d="M311 658V642M333 660V646" stroke="#839586" stroke-width="12"/>
<path d="M312 640V628M333 642V632" stroke="#d7ba81" stroke-width="6"/>
<path d="M187 725Q187 664 243 656L313 655Q368 660 380 714L379 806Q373 849 331 864L237 858Q195 848 190 806Z" fill="url(#brass)"/>
<path d="M201 711Q201 681 237 674L304 672" fill="none" stroke="#f6da9f" stroke-width="5"/>
<path d="M204 724Q279 707 360 726L359 803Q353 835 323 841L245 836Q211 830 208 802Z" fill="url(#ivory)" stroke-width="3"/>
<path d="M211 695Q280 680 353 699M222 686Q280 677 341 688" fill="none" stroke="#927c50" stroke-width="3"/>
<path d="M229 744Q241 736 253 740M304 739Q319 735 331 746" fill="none" stroke="#9c8b65" stroke-width="5"/>
<circle cx="241" cy="768" r="18" fill="#4d6259" stroke-width="2"/>
<circle cx="319" cy="768" r="18" fill="#4d6259" stroke-width="2"/>
<path d="M225 764L255 764M303 764L334 764" stroke="#e3d2ab" stroke-width="9"/>
<circle cx="244" cy="773" r="6" fill="#e3d2ab" stroke="none"/>
<circle cx="322" cy="773" r="6" fill="#e3d2ab" stroke="none"/>
<!-- Oversized wire spectacles. -->
<circle cx="241" cy="770" r="31" fill="#dbe0b8" fill-opacity=".09" stroke="#4a5041" stroke-width="5"/>
<circle cx="321" cy="770" r="31" fill="#dbe0b8" fill-opacity=".09" stroke="#4a5041" stroke-width="5"/>
<path d="M272 766Q281 757 290 766M210 762L193 754M352 762L374 752" fill="none" stroke="#4a5041" stroke-width="4"/>
<path d="M219 759Q225 746 241 746M299 759Q305 746 321 746" fill="none" stroke="#f8edc8" stroke-width="3"/>
<path d="M278 776L271 793H284" fill="none" stroke="#9c916f" stroke-width="3"/>
<path d="M253 814Q283 831 312 811" fill="none" stroke="#6a7056" stroke-width="5"/>
<path d="M261 814V819M274 818V823M287 818V824M300 815V820" stroke="#e6d5ad" stroke-width="3"/>
<path d="M209 789L201 784M357 789L365 784" stroke="#b19b6a" stroke-width="2"/>
</g>''')
add('<g transform="rotate(-8 284 761)">')
gear(187,758,26,'#b39359'); gear(380,756,22,'#b39359')
bolt(203,816,5,'#ead098'); bolt(361,815,5,'#ead098')
add('</g>')
# Dad's big hand rests heavily on grandmother's shoulder.
add('''<g stroke="#263c41" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
<path d="M357 851Q379 835 395 853L403 883L401 920Q399 932 389 930Q380 929 380 919L379 896L373 892L376 923Q376 934 366 934Q356 933 355 923L352 894L346 892L348 916Q349 928 339 929Q329 930 327 918L323 884Q323 871 338 866Z" fill="url(#orange)"/>
<path d="M329 903L348 900M356 908L375 905M383 909H400" stroke="#876044" stroke-width="3"/>
<path d="M335 880Q357 857 381 866" stroke="#f5c18a" stroke-width="4" fill="none"/>
</g>''')
bolt(365,877,8)

# Teen. The whole silhouette deliberately leans out of the family grouping.
add('''<g transform="rotate(8 1150 1000)" stroke="#263c41" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<!-- narrow, mismatched stance -->
<path d="M1092 1004L1096 1175L1109 1308M1197 1007L1236 1170L1220 1300" fill="none" stroke="#263c41" stroke-width="37"/>
<path d="M1092 1004L1096 1175L1109 1308M1197 1007L1236 1170L1220 1300" fill="none" stroke="#6f7d85" stroke-width="25"/>
<path d="M1074 1086L1114 1082L1118 1151L1078 1156Z" fill="url(#purple)"/>
<path d="M1200 1084L1233 1075L1253 1146L1215 1159Z" fill="url(#purple)"/>
<path d="M1082 1220L1118 1218L1126 1307L1090 1314Z" fill="url(#purple)"/>
<path d="M1210 1213L1246 1215L1238 1309L1203 1306Z" fill="url(#purple)"/>
<path d="M1088 1301Q1108 1290 1129 1306L1140 1331Q1146 1347 1133 1354L1042 1366Q1026 1359 1036 1344L1076 1323Z" fill="#475560"/>
<path d="M1201 1295Q1223 1286 1237 1308L1289 1324Q1301 1328 1301 1346L1214 1356Q1194 1353 1193 1339Z" fill="#475560"/>
<path d="M1035 1353L1139 1341M1198 1343L1296 1333" stroke="#d4c9b3" stroke-width="6"/>
<path d="M1088 1321L1112 1318M1078 1329L1107 1326M1244 1319L1235 1331M1257 1323L1250 1333" stroke="#a49bac" stroke-width="4"/>
<!-- A loose headphone cable dangling uselessly. -->
<path d="M1043 660Q1007 797 1044 867T1053 1099Q1039 1168 1080 1190" fill="none" stroke="#26343e" stroke-width="7"/>
<path d="M1040 671Q1023 756 1029 797" fill="none" stroke="#bc978c" stroke-width="2"/>
<path d="M1077 1181L1092 1185L1097 1206L1083 1210Z" fill="#c4967b" stroke-width="3"/>
<path d="M1090 1208L1093 1221" stroke="#b4bdad" stroke-width="5"/>
<path d="M1123 734L1121 780L1175 780L1179 731" fill="#6a7c7e"/>
<path d="M1124 751H1176M1123 763H1174" stroke="#acafa2" stroke-width="4"/>
<!-- Angular plum armor, arms folded firmly across it. -->
<path d="M1080 778L1203 771Q1230 772 1236 800L1245 998L1224 1032L1102 1056L1066 1013L1051 822Q1052 791 1080 778Z" fill="url(#purple)"/>
<path d="M1072 798L1086 993L1114 1030" fill="none" stroke="#c4afba" stroke-width="5"/>
<path d="M1204 790L1218 997L1204 1023" fill="none" stroke="#575775" stroke-width="5"/>
<path d="M1100 815L1194 804L1203 985L1109 1000Z" fill="#5e657d" stroke-width="3"/>
<path d="M1080 1013L1211 994" stroke="#b29ba7" stroke-width="3"/>
<circle cx="1144" cy="856" r="23" fill="#d0a487" stroke-width="2"/>
<ellipse cx="1144" cy="856" rx="35" ry="10" fill="none" stroke="#273f48" stroke-width="5" transform="rotate(-27 1144 856)"/>
<path d="M1206 806L1208 825M1214 803L1217 820" stroke="#d5bfbc" stroke-width="2"/>
<path d="M1072 823L1057 932Q1057 949 1075 948L1190 901" fill="none" stroke="#263c41" stroke-width="45"/>
<path d="M1072 823L1057 932Q1057 949 1075 948L1190 901" fill="none" stroke="url(#purple)" stroke-width="32"/>
<path d="M1066 853L1057 907M1100 930L1159 907" stroke="#c4acb6" stroke-width="4"/>
<path d="M1227 813L1246 927Q1250 945 1231 949L1102 972" fill="none" stroke="#263c41" stroke-width="48"/>
<path d="M1227 813L1246 927Q1250 945 1231 949L1102 972" fill="none" stroke="url(#purple)" stroke-width="35"/>
<path d="M1228 852L1240 907M1209 943L1149 955" stroke="#bfacb8" stroke-width="4"/>
<path d="M1106 954L1080 950Q1068 949 1065 959L1064 979Q1063 989 1076 990L1108 988Z" fill="#a69aa9" stroke-width="4"/>
<path d="M1069 962L1091 964M1068 974L1092 975M1074 984L1094 984" stroke="#52606c" stroke-width="3"/>
<path d="M1179 891L1191 877Q1199 869 1207 876L1224 892Q1231 900 1222 909L1207 921Z" fill="#a79baa" stroke-width="4"/>
<path d="M1196 882L1213 898M1189 890L1205 906" stroke="#52606c" stroke-width="3"/>
</g>''')
add('<g transform="rotate(8 1150 1000)">')
joint(1097,1176,25,'#8a8795'); joint(1237,1172,25,'#8a8795')
joint(1070,818,29,'#998d9f'); joint(1224,813,29,'#998d9f'); joint(1241,936,24,'#8f8998')
bolt(1096,1033,6,'#ada6ad'); bolt(1225,1008,6,'#ada6ad')
add('''<g stroke="#263c41" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<!-- Headphones create a defensive little world of their own. -->
<path d="M1043 640Q1028 533 1129 524Q1238 510 1256 636" fill="none" stroke="#213740" stroke-width="24"/>
<path d="M1043 621Q1041 538 1127 535Q1216 520 1248 616" fill="none" stroke="#ba8a7d" stroke-width="10"/>
<path d="M1097 566L1091 543L1124 552L1145 531L1163 559" fill="#8d7f95"/>
<path d="M1071 565L1215 559L1242 597L1237 722L1206 752L1090 743L1058 712L1054 601Z" fill="url(#purple)"/>
<path d="M1072 584L1205 577" stroke="#c6b1ba" stroke-width="4"/>
<path d="M1078 611L1212 603L1216 701L1199 719L1093 717L1078 702Z" fill="url(#visor)" stroke-width="4"/>
<path d="M1088 646L1133 651L1132 668L1088 664Z" fill="#d0d8b4" stroke-width="2"/>
<path d="M1160 650L1202 639L1204 658L1163 668Z" fill="#d0d8b4" stroke-width="2"/>
<path d="M1096 652V662M1169 650V660" stroke="#3c605d" stroke-width="7"/>
<path d="M1129 695L1165 690" stroke="#a7b6a2" stroke-width="4"/>
<path d="M1088 623L1132 632M1163 633L1200 620" stroke="#5e8179" stroke-width="3"/>
<rect x="1031" y="611" width="32" height="85" rx="13" fill="url(#red)"/>
<rect x="1227" y="607" width="32" height="85" rx="13" fill="url(#red)"/>
<ellipse cx="1035" cy="651" rx="19" ry="35" fill="#3d535c"/>
<ellipse cx="1254" cy="649" rx="20" ry="35" fill="#3d535c"/>
<ellipse cx="1034" cy="651" rx="9" ry="20" fill="#ae9e98" stroke-width="3"/>
<ellipse cx="1256" cy="649" rx="10" ry="21" fill="#ae9e98" stroke-width="3"/>
<path d="M1230 585L1221 594M1232 594L1227 599" stroke="#e0c6bd" stroke-width="2"/>
</g></g>''')
# Mom's fingers visibly clamp the teenager's inner shoulder.
add('''<g stroke="#263c41" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
<path d="M1081 782Q1087 766 1103 762L1125 766Q1135 769 1133 779Q1131 786 1120 784L1108 781L1104 786L1124 790Q1135 792 1132 802Q1130 810 1120 808L1102 804L1098 809L1117 814Q1126 817 1122 826Q1119 833 1108 829L1087 821Q1077 817 1076 806Z" fill="url(#mint)"/>
<path d="M1091 781L1087 803M1116 767L1113 782M1115 790L1112 806M1108 813L1104 827" stroke="#5e8679" stroke-width="2.5"/>
</g>''')

# Child's shutter cable: broad loose loops are visible on the studio floor.
add('''<path d="M785 1197C825 1240 766 1331 816 1391C850 1432 1019 1410 1049 1436C1076 1461 1031 1489 957 1475C892 1464 936 1424 1019 1437C1140 1458 1199 1479 1378 1454" fill="none" stroke="#263b42" stroke-width="8" stroke-linecap="round"/>
<path d="M785 1197C825 1240 766 1331 816 1391C850 1432 1019 1410 1049 1436C1076 1461 1031 1489 957 1475C892 1464 936 1424 1019 1437C1140 1458 1199 1479 1378 1454" fill="none" stroke="#98a194" stroke-width="2" opacity=".55" stroke-linecap="round"/>
<g stroke="#263c41" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<!-- Small feet refuse to stand still. -->
<path d="M612 1260L590 1309L575 1360M686 1250L731 1291L709 1322" fill="none" stroke="#263c41" stroke-width="32"/>
<path d="M612 1260L590 1309L575 1360M686 1250L731 1291L709 1322" fill="none" stroke="url(#steel)" stroke-width="21"/>
<path d="M576 1326L599 1333L589 1371L563 1366Z" fill="url(#yellow)"/>
<path d="M713 1299L732 1314L717 1337L694 1325Z" fill="url(#yellow)"/>
<path d="M561 1356Q577 1350 591 1367L597 1382Q597 1394 583 1397L523 1397Q510 1391 517 1377L546 1369Z" fill="#c47b58"/>
<path d="M694 1321Q711 1321 717 1337L753 1342Q765 1349 759 1362Q748 1374 733 1370L691 1356Q681 1343 694 1321Z" fill="#c47b58"/>
<path d="M522 1386H589M698 1346L751 1359" stroke="#f0ce92" stroke-width="4"/>
<!-- Clutching dad's leg with the left hand. -->
<path d="M585 1147L535 1168L526 1108" fill="none" stroke="#263c41" stroke-width="36"/>
<path d="M585 1147L535 1168L526 1108" fill="none" stroke="url(#yellow)" stroke-width="25"/>
<path d="M510 1092L528 1087Q539 1089 540 1102L542 1124Q541 1133 530 1133L511 1129Q504 1127 503 1117L503 1101Z" fill="url(#yellow)" stroke-width="4"/>
<path d="M507 1101L528 1099M506 1112L530 1112M508 1123L530 1124" stroke="#947e43" stroke-width="3"/>
<!-- Other arm: the shutter-release culprit. -->
<path d="M715 1140L751 1196L783 1185" fill="none" stroke="#263c41" stroke-width="34"/>
<path d="M715 1140L751 1196L783 1185" fill="none" stroke="url(#yellow)" stroke-width="23"/>
</g>''')
joint(588,1310,19,'#b8a765'); joint(730,1293,19,'#b8a765'); joint(536,1167,19,'#b7a971'); joint(750,1195,18,'#b7a971')
add('''<g transform="rotate(-9 644 1181)" stroke="#263c41" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round">
<path d="M582 1127Q584 1107 603 1105L686 1106Q708 1107 712 1128L722 1235Q724 1257 705 1270L600 1273Q579 1261 578 1245Z" fill="url(#yellow)"/>
<path d="M591 1133L590 1235Q589 1257 607 1260" fill="none" stroke="#ffdf88" stroke-width="4"/>
<path d="M615 1090V1115Q642 1126 669 1113V1085Z" fill="#71887a"/>
<path d="M620 1102L664 1100" stroke="#d4cf9e" stroke-width="4"/>
<rect x="604" y="1138" width="86" height="84" rx="17" fill="#eedda1" stroke-width="3"/>
<!-- A little hand-painted heart instead of a factory insignia. -->
<path d="M645 1197C608 1174 631 1152 645 1170C660 1146 686 1172 645 1197Z" fill="#c8755f" stroke="#96664a" stroke-width="2"/>
<path d="M626 1171Q632 1163 637 1171" fill="none" stroke="#f5b58b" stroke-width="3"/>
<path d="M614 1241H625M640 1241H651M666 1241H677" stroke="#8f7e46" stroke-width="5"/>
<rect x="576" y="1148" width="14" height="30" rx="5" fill="#6c887c" stroke-width="3"/>
<rect x="704" y="1140" width="14" height="30" rx="5" fill="#6c887c" stroke-width="3"/>
</g>''')
add('<g transform="rotate(-9 644 1181)">')
for x,y in [(601,1124),(692,1124),(598,1251),(701,1249)]: bolt(x,y,4,'#eed491')
add('</g>')
# Kid's mismatched optics and head tilt.
add('''<g transform="rotate(-14 631 1030)" stroke="#263c41" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round">
<path d="M622 962L622 944Q604 944 614 933Q630 926 613 919L602 914" fill="none" stroke="#263c41" stroke-width="6"/>
<circle cx="599" cy="910" r="12" fill="#d98263" stroke-width="3"/>
<path d="M538 985L722 971L745 995L744 1086L719 1110L553 1104Z" fill="#b28a3d"/>
<rect x="535" y="959" width="195" height="143" rx="27" fill="url(#yellow)"/>
<path d="M549 985Q548 973 560 973H696" fill="none" stroke="#ffe397" stroke-width="4"/>
<path d="M553 990Q552 978 566 978H696Q712 978 712 994V1053Q712 1075 693 1077L572 1076Q552 1076 552 1058Z" fill="#e9dca7" stroke-width="3"/>
<circle cx="588" cy="1020" r="31" fill="#5e7e78" stroke-width="4"/>
<circle cx="588" cy="1020" r="23" fill="#273f47" stroke-width="2"/>
<circle cx="594" cy="1018" r="13" fill="#cbd4a7" stroke="none"/>
<circle cx="598" cy="1017" r="6" fill="#29484c" stroke="none"/>
<circle cx="666" cy="1019" r="19" fill="#2c484c" stroke-width="3"/>
<circle cx="670" cy="1017" r="10" fill="#ced6aa" stroke="none"/>
<circle cx="673" cy="1015" r="4" fill="#29484c" stroke="none"/>
<path d="M649 990L675 986" stroke="#7e885d" stroke-width="5"/>
<path d="M616 1050Q637 1071 660 1048Q658 1075 638 1078Q621 1075 616 1050Z" fill="#354e4b" stroke-width="3"/>
<path d="M625 1057L627 1066L638 1068L639 1059" fill="#f2e6ba" stroke-width="2"/>
<rect x="520" y="1004" width="19" height="39" rx="7" fill="#7b9986" stroke-width="3"/>
<rect x="730" y="999" width="16" height="38" rx="7" fill="#7b9986" stroke-width="3"/>
<path d="M571 1088H589M685 1088H700" stroke="#ba943e" stroke-width="3"/>
</g>''')
add('<g transform="rotate(-14 631 1030)">')
bolt(546,984,5,'#f3d47d'); bolt(719,1069,5,'#f3d47d')
add('</g>')
# Grandma's gentle, slightly intrusive pat, overlaying the child's head.
add('''<g stroke="#263c41" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
<path d="M530 972L551 958Q561 952 573 955L602 965Q612 969 608 977Q605 984 596 981L576 975L573 978L595 985Q605 989 601 997Q598 1004 588 1000L568 992L565 995L582 1003Q591 1007 587 1015Q583 1021 573 1016L546 1005L529 992Z" fill="url(#brass)"/>
<path d="M549 973L545 991M587 962L583 977M581 981L577 996M572 998L568 1014" stroke="#8f794c" stroke-width="2.5"/>
</g>
<!-- Tiny remote, enormous red button. -->
<g transform="rotate(12 790 1173)" stroke="#263c41" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
<path d="M778 1167L770 1158Q764 1156 762 1163L762 1186Q762 1195 772 1198L799 1199Q809 1197 809 1187L805 1174Z" fill="url(#yellow)"/>
<rect x="777" y="1133" width="34" height="65" rx="11" fill="#455e5b"/>
<path d="M786 1142V1185" stroke="#94a48c" stroke-width="3"/>
<ellipse cx="794" cy="1148" rx="12" ry="8" fill="#7e4d44" stroke-width="2"/>
<path d="M783 1146V1136Q794 1126 805 1136V1146Q794 1155 783 1146Z" fill="#dd8068" stroke-width="2.5"/>
<path d="M783 1136Q794 1143 805 1136" fill="none" stroke="#f3b287" stroke-width="2"/>
<path d="M766 1167L785 1166Q794 1167 794 1174Q794 1181 785 1181L771 1182" fill="url(#yellow)" stroke-width="3"/>
<path d="M774 1190H786" stroke="#94793e" stroke-width="2"/>
<path d="M789 1199V1207" stroke="#253c40" stroke-width="8"/>
</g>''')

# Hand-drawn wear. Restrained scratches make the family look individually lived-in.
add('''<g fill="none" stroke-linecap="round" stroke-width="2">
<path d="M466 875L469 889M472 873L474 880M743 914L739 925M484 1239L484 1251" stroke="#916748" opacity=".7"/>
<path d="M898 1006L901 1014M899 1020L903 1030M932 878L942 875" stroke="#6a9181" opacity=".6"/>
<path d="M200 1046L201 1061M205 1052L206 1058M277 1116L290 1118" stroke="#8c7c4e" opacity=".7"/>
<path d="M585 1204L587 1212M665 1254L674 1253" stroke="#ab873d" opacity=".6"/>
</g>
<!-- A few bolts and dust motes on the studio floor. -->
<g stroke="#243e45" stroke-width="2" stroke-linecap="round">
<path d="M415 1404L429 1401M422 1397L424 1406"/>
<circle cx="430" cy="1401" r="3" fill="#a99c76"/>
<path d="M1158 1416L1169 1419"/>
<circle cx="1160" cy="1415" r="3" fill="#ac9674"/>
</g>
''')
# Deterministic minute flecks, like an old lithographic print, not visual clutter.
random.seed(21)
add('<g fill="#f2dcb5" opacity=".055">')
for _ in range(1000):
    x=random.uniform(68,1372); y=random.uniform(68,1532)
    r=random.choice([.45,.55,.7,.8,1.05])
    circle(f'{x:.2f}',f'{y:.2f}',r,'#e7dabd')
add('</g>')
add('''<rect x="62" y="62" width="1316" height="1476" fill="#9f977f" opacity=".12" filter="url(#grain)" style="mix-blend-mode:soft-light"/>
</g>
<!-- Quiet paper mat and fine inset rule; no caption, lettering or numbers. -->
<rect x="62" y="62" width="1316" height="1476" rx="5" fill="none" stroke="#253a3e" stroke-opacity=".7" stroke-width="2"/>
<rect x="45" y="45" width="1350" height="1510" rx="6" fill="none" stroke="#b2a38a" stroke-width="1"/>
<g fill="none" stroke="#b4a488" stroke-width="1" opacity=".65"><path d="M31 75V31H75M1365 31H1409V75M31 1525V1569H75M1365 1569H1409V1525"/></g>
</svg>''')
(OUT / 'family_portrait.svg').write_text('\n'.join(s))
print(f'Wrote {OUT / "family_portrait.svg"} ({(OUT / "family_portrait.svg").stat().st_size:,} bytes)')
