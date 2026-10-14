from pathlib import Path
import math
import random

# Original vector illustration. All coordinates and paths are drawn for this scene.
OUT = Path('output')
OUT.mkdir(exist_ok=True)
svg = []
def add(s): svg.append(s)
def group(attrs=''): add(f'<g {attrs}>')
def end(): add('</g>')
def path(d, fill='none', stroke='#283f40', sw=4, extra=''):
    add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
def rect(x,y,w,h,fill,rx=0,stroke='#283f40',sw=4,extra=''):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
def ellipse(x,y,rx,ry,fill,stroke='#283f40',sw=4,extra=''):
    add(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
def circle(x,y,r,fill,stroke='#283f40',sw=4,extra=''):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
def line(x1,y1,x2,y2,stroke='#283f40',sw=4,extra=''):
    path(f'M{x1} {y1} L{x2} {y2}', 'none', stroke, sw,extra)
def screw(x,y,r=5,c='#f0d39c',angle=-35):
    circle(x,y,r,c,sw=1.8)
    a=math.radians(angle)
    dx,dy=(r-2)*math.cos(a),(r-2)*math.sin(a)
    line(round(x-dx,2),round(y-dy,2),round(x+dx,2),round(y+dy,2),sw=1.5)
def rivets(points,c='#f0d39c'):
    for x,y in points: screw(x,y,c=c)
def bolt(x,y,r,fill='#718c85'):
    pts=' '.join(f'{x+r*math.cos(math.pi/3*i):.2f},{y+r*math.sin(math.pi/3*i):.2f}' for i in range(6))
    add(f'<polygon points="{pts}" fill="{fill}" stroke="#283f40" stroke-width="3"/>')
    circle(x,y,r*.35,'#d8d3ae',sw=2)
def limb(d, color, width=34, shine=None):
    path(d,'none','#283f40',width+8)
    path(d,'none',color,width)
    if shine: path(d,'none',shine,5)
def spark(x,y,r=12,fill='#f0d39c'):
    path(f'M{x} {y-r} Q{x+2} {y-2} {x+r} {y} Q{x+2} {y+2} {x} {y+r} Q{x-2} {y+2} {x-r} {y} Q{x-2} {y-2} {x} {y-r}Z',fill,'none',0)

add('''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1250" viewBox="0 0 1500 1250">
<defs>
  <linearGradient id="paper" x2="0.7" y2="1"><stop stop-color="#f3e6c8"/><stop offset="1" stop-color="#dfcda6"/></linearGradient>
  <radialGradient id="backdrop" cx="48%" cy="38%" r="76%"><stop stop-color="#edc19d"/><stop offset=".58" stop-color="#cf947b"/><stop offset="1" stop-color="#ac6f61"/></radialGradient>
  <linearGradient id="floor" x2="0" y2="1"><stop stop-color="#b2806c"/><stop offset="1" stop-color="#d1a485"/></linearGradient>
  <linearGradient id="curtain" x2="1" y2=".25"><stop stop-color="#153e40"/><stop offset=".35" stop-color="#396560"/><stop offset=".7" stop-color="#21494a"/><stop offset="1" stop-color="#102f34"/></linearGradient>
  <linearGradient id="copper" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="#eaa175"/><stop offset=".5" stop-color="#d87554"/><stop offset="1" stop-color="#b85440"/></linearGradient>
  <linearGradient id="brass" x2=".9" y2="1"><stop stop-color="#f0cf80"/><stop offset=".5" stop-color="#dcb362"/><stop offset="1" stop-color="#b68b46"/></linearGradient>
  <linearGradient id="mint" x2="1" y2=".7"><stop stop-color="#b3d0b6"/><stop offset=".55" stop-color="#7ead9c"/><stop offset="1" stop-color="#4e8980"/></linearGradient>
  <linearGradient id="lilac" x2=".85" y2="1"><stop stop-color="#b3aabd"/><stop offset=".6" stop-color="#8b879f"/><stop offset="1" stop-color="#65667f"/></linearGradient>
  <linearGradient id="orange" x2=".8" y2="1"><stop stop-color="#f1b562"/><stop offset=".52" stop-color="#e78b4f"/><stop offset="1" stop-color="#ca623b"/></linearGradient>
  <linearGradient id="chrome" x2="1" y2="0"><stop stop-color="#537773"/><stop offset=".3" stop-color="#d2d7b8"/><stop offset=".46" stop-color="#f4e9c4"/><stop offset=".65" stop-color="#72938a"/><stop offset="1" stop-color="#3c6260"/></linearGradient>
  <linearGradient id="seat" x2="0" y2="1"><stop stop-color="#667669"/><stop offset="1" stop-color="#344e4a"/></linearGradient>
  <pattern id="dots" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#263f40" opacity=".14"/></pattern>
  <pattern id="cloth" width="12" height="12" patternUnits="userSpaceOnUse"><path d="M0 2H12 M2 0V12" stroke="#e9d5aa" stroke-width=".65" opacity=".16"/></pattern>
  <pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><path d="M0 0V7" stroke="#283f40" stroke-width="1.3" opacity=".23"/></pattern>
  <filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".76" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="linear" slope=".12"/></feComponentTransfer><feBlend in="SourceGraphic" mode="multiply"/></filter>
  <clipPath id="photo"><rect x="73" y="67" width="1354" height="1111" rx="13"/></clipPath>
</defs>
<g stroke-linecap="round" stroke-linejoin="round">''')

# The slightly foxed photographic mount and double ruled border.
rect(0,0,1500,1250,'url(#paper)',0,'none',0)
rect(34,29,1432,1190,'none',21,'#af9170',1.3)
rect(46,41,1408,1166,'none',16,'#faf0d4',2)
rect(68,62,1364,1121,'#233f40',16,'#866f54',2)
group('clip-path="url(#photo)"')
rect(73,67,1354,1111,'url(#backdrop)',0,'none',0)
# Ghosted painted oval on the studio backdrop.
ellipse(738,540,555,449,'none','#f4cea5',2, 'opacity=".32"')
ellipse(738,540,538,432,'none','#925f54',1.5,'opacity=".15"')
path('M198 301 Q270 171 424 138 M1085 147 Q1229 201 1282 350','none','#f4cc9f',2,'opacity=".3"')
# A few hand-painted, almost invisible decorative flecks.
for x,y,r in [(376,264,8),(1102,281,10),(944,186,6),(248,401,5),(1026,353,5)]:
    spark(x,y,r,'#ebba93')
# Backdrop sweep into the floor.
path('M73 935 Q436 875 739 911 Q1092 893 1427 947 L1427 1178H73Z','url(#floor)','none',0)
path('M114 956Q423 916 612 936 M1033 928Q1249 934 1381 969','none','#9d725f',2,'opacity=".4"')
for x,y,rx,ry in [(748,1083,512,69),(362,1068,176,37),(910,1092,138,28),(1231,1111,140,25)]:
    ellipse(x,y,rx,ry,'#6a6355','none',0,'opacity=".19"')
# Heavy teal curtains, with curved stitched folds.
path('M73 67H322C295 147 230 210 228 314C224 451 193 562 143 642C126 677 108 698 73 729Z','url(#curtain)')
path('M73 68H242C209 171 148 203 155 359C160 484 119 574 74 608Z','#244e4d','none',0)
path('M122 78C140 215 100 299 112 427C120 533 87 590 75 620 M200 73C181 193 144 231 149 371C151 487 126 548 106 592 M274 77C226 194 188 226 194 357C202 445 164 559 137 601','none','#598078',3,'opacity=".5"')
path('M73 616Q116 646 158 608L164 632Q117 666 73 644Z','#cca36e',sw=3)
path('M143 644Q140 699 161 725 M145 649Q124 695 140 718','none','#bd955f',5)
path('M150 714L174 743L157 754L143 721Z','#d4ab73',sw=2)
path('M1427 67H1201C1228 174 1300 219 1286 352C1282 474 1325 596 1427 717Z','url(#curtain)')
path('M1328 69C1316 196 1385 237 1360 388C1346 482 1407 592 1427 613V68Z','#204748','none',0)
path('M1250 78C1280 176 1343 246 1323 350C1309 461 1362 567 1396 604 M1324 78C1313 205 1385 245 1357 389C1349 463 1387 554 1415 585 M1395 76C1358 216 1430 291 1399 421','none','#5f8278',3,'opacity=".48"')
path('M1352 610Q1390 641 1427 628V655Q1391 664 1358 633Z','#cca36e',sw=3)
path('M1368 642Q1393 686 1377 730','none','#cca36e',5)
path('M1371 721L1359 752L1382 755L1384 725Z','#d4ab73',sw=2)

# A cable from the antique robot, forgotten on the studio floor.
path('M293 944C237 969 195 1005 216 1051C242 1107 443 1062 478 1108C503 1143 418 1152 401 1121C381 1088 524 1120 568 1115','none','#283f40',8)
path('M293 942C237 968 195 1004 216 1049C242 1105 443 1060 478 1106C503 1141 418 1150 401 1119C381 1086 524 1118 568 1113','none','#bb875c',3)
group('transform="translate(574 1113) rotate(-8)"')
rect(-8,-11,28,22,'#4b6861',5,sw=3)
line(20,-6,31,-6,'#ddd2ae',5);line(20,6,31,6,'#ddd2ae',5)
line(-2,-6,-2,6,sw=2);end()
# Two strips of posing tape; somebody has missed their mark.
path('M1195 1123L1243 1095 M1201 1094L1238 1128','none','#ead1a8',10,'opacity=".75"')

# Tall, anxious parent: stiff shoulders, excessive effort at smiling.
# Rear arm reaches all the way round the family to the sulking teen.
limb('M809 534L918 586L1121 685','#bd7155',45)
circle(913,583,28,'#b8b698');circle(913,583,16,'#3c5855',sw=3)
line(949,611,957,595,'#e5b083',3);line(959,618,967,602,'#e5b083',3)
# Left arm resting on the older generation.
limb('M556 533L514 625L457 663','#c5815c',45)
circle(513,625,27,'#c4b795');bolt(513,625,15)
path('M550 534L529 576','none','#f1b585',6)
# Torso shell.
path('M575 473Q607 465 630 470L753 469Q805 473 828 508L844 738Q806 787 689 790Q589 791 537 744L540 515Q550 487 575 473Z','url(#copper)',sw=5)
path('M801 507Q830 523 830 560L842 738Q815 768 778 774L780 535Z','#b85340','none',0)
path('M553 524Q553 493 592 486L618 486 M553 538V650','none','#f1b68b',7)
path('M565 724L815 724L820 748Q697 790 560 746Z','url(#hatch)','none',0)
# Raised chest panel and subtly crooked bow tie.
path('M620 497L748 497L765 709Q696 737 607 707Z','#ecc394',sw=3)
path('M620 497L607 542L640 577L653 523 M748 497L773 541L737 576L721 521','#ac5845',sw=3)
path('M611 701Q681 726 760 703','none','#9e754f',2)
for y in [579,622,665]:
    circle(686,y,7,'#385a56',sw=2);circle(684,y-2,2,'#d9d3ae','none',0)
# A polished pocket with one pathetic little flower.
path('M769 583L813 578L816 621L775 627Z','#cd7252',sw=3)
path('M777 597L779 554Q787 543 795 552','none','#364f47',3)
path('M780 570Q763 551 764 565Q766 576 780 577Z','#80a68a',sw=2)
for x,y in [(795,543),(803,550),(797,558),(788,552)]: circle(x,y,6,'#f4dba7',sw=1.5)
circle(796,551,5,'#bd784b',sw=1.5)
rivets([(568,516),(800,526),(568,729),(811,735)],'#f2b786')
# Neck, slightly compressed on one side.
rect(640,431,90,53,'#526e63',12,sw=4)
for y in [442,454,466]: path(f'M647 {y}H724','none','#d5c59b',5)
path('M638 477L681 498L646 521L626 492Z','#f0d6aa',sw=3)
path('M727 475L689 498L722 520L747 489Z','#f0d6aa',sw=3)
group('transform="rotate(7 686 502)"')
path('M678 494L642 481Q634 501 641 520L678 510 M693 494L731 482Q736 500 730 519L694 510Z','#3b756c',sw=3)
path('M649 493L672 502L651 511 M723 493L701 502L722 511','none','#78a791',2)
rect(674,491,22,24,'#76a58d',5,sw=3);end()
# Ears and the very upright antenna.
rect(554,321,33,75,'#b78358',9,sw=4);rect(792,316,29,80,'#b78358',8,sw=4)
for y in [334,346,358,370,382]: line(557,y,574,y,'#e5bc83',2);line(802,y,817,y,'#e5bc83',2)
path('M692 259L691 201L704 186','none','#283f40',11)
path('M692 251L691 201L704 186','none','#e3bb8b',5)
ellipse(692,251,23,9,'#ad6348',sw=3)
circle(706,180,13,'#da7653',sw=3);circle(702,176,4,'#f7d298','none',0)
# The copper face, with sculpted bevels and heavy glass mask.
path('M580 279Q584 257 610 255L758 251Q788 252 796 280L808 409Q805 441 773 447L614 450Q583 446 579 419L568 306Q568 288 580 279Z','url(#copper)',sw=5)
path('M580 293Q589 270 614 268L751 265','none','#f6c696',6)
path('M781 280L794 402Q795 428 774 434L619 438','none','#ad543f',6)
path('M596 306Q596 292 613 291L752 287Q775 287 778 309L785 388Q787 412 764 415L624 420Q602 418 601 398Z','#263f40',sw=4)
path('M609 310Q609 303 619 303L750 300Q764 300 766 315L772 387Q773 402 758 404L628 408Q615 408 614 396Z','#415b54','none',0)
# Reflections in the dark face glass.
path('M618 307L643 305L620 361Z','#809586','none',0,'opacity=".27"')
path('M741 302L756 302L770 381L758 390Z','#92a693','none',0,'opacity=".12"')
# Unequal optics amplify the frozen, nervous expression.
ellipse(646,346,24,29,'#ecdcb1',sw=3)
ellipse(734,342,21,25,'#ecdcb1',sw=3)
circle(650,350,10,'#283f40',sw=1);circle(730,346,9,'#283f40',sw=1)
circle(647,346,3,'#f6eac8','none',0);circle(727,342,3,'#f6eac8','none',0)
path('M623 313L658 315 M716 306L746 300','none','#f0c68a',6)
# The over-literal, uncomfortable photographic smile.
path('M645 385Q691 371 744 382L743 397Q691 388 648 400Z','#e7d2a4',sw=3)
for x,y in [(661,383),(679,380),(697,379),(715,380),(731,382)]: line(x,y,x+1,y+12,sw=2)
path('M764 348Q756 361 763 367Q773 367 764 348Z','#95bfac',sw=2)
rivets([(586,285),(780,282),(594,428),(784,424)],'#eac390')
path('M609 278L651 276 M660 276L672 276','none','#a9684e',2)

# The long arm of the mischievous child, behind grandpa's head.
limb('M567 849L489 721L462 577L438 480','#d0b17a',24)
path('M483 681L472 623 M499 726L534 785','none','#f3d392',5)
circle(489,721,19,'#e19750',sw=3);bolt(489,721,10,'#cbad77')
circle(462,577,17,'#e39750',sw=3)
# Two conspicuously raised fingers: the family-photo bunny ears.
group('transform="rotate(-10 439 470)"')
path('M423 488L418 453L410 415Q409 405 418 402Q427 401 430 411L439 443L442 399Q444 389 453 391Q461 393 460 404L457 453Q471 449 476 459L473 483Q455 501 436 499Z','url(#orange)',sw=4)
path('M421 427L433 424 M441 422L458 424 M435 448L447 455L444 474 M452 465L466 459','none','#8f633f',2.5)
end()

# The upholstered photographer's bench.
path('M235 874L1133 874L1110 977Q694 1005 262 973Z','#304b48',sw=5)
path('M270 965L259 1053L288 1059L319 971 M1053 974L1084 1064L1114 1056L1094 963','url(#brass)',sw=4)
path('M230 788Q231 755 269 751L1084 751Q1126 753 1137 790L1150 905L217 905Z','url(#seat)',sw=5)
path('M251 787Q250 772 276 772H1078Q1104 773 1113 795','none','#9a9d80',3)
path('M226 806L1135 806L1147 905H216Z','url(#cloth)','none',0)
for x in [289,449,608,768,928,1088]:
    path(f'M{x-25} 825Q{x} 849 {x+25} 825 M{x-25} 871Q{x} 849 {x+25} 871','none','#304c46',2)
    circle(x,849,6,'#acaf87',sw=2)
path('M218 889Q415 873 671 887Q898 873 1147 892L1152 934Q897 957 664 940Q426 954 212 933Z','#75806a',sw=5)
path('M223 919Q416 938 666 922Q918 938 1139 920','none','#c2b48a',2.5)
path('M674 893L672 926','none','#4d5e51',3)

# Grandfather's mismatched, gently splayed legs.
limb('M329 859L326 958L303 1025','#b59d6d',38)
limb('M418 859L427 946L460 1024','#b59d6d',38)
for x,y,rot in [(326,956,4),(428,947,-9)]:
    group(f'transform="rotate({rot} {x} {y})"')
    rect(x-23,y-23,46,44,'#5b7061',10,sw=3)
    for yy in range(y-14,y+17,8): line(x-18,yy,x+18,yy,'#e3c68b',3)
    end()
# Old-fashioned metal slippers.
path('M280 1006Q302 998 321 1015L341 1032L339 1060Q303 1079 254 1064L253 1048Q258 1028 280 1023Z','url(#brass)',sw=4)
path('M443 1010Q458 1004 478 1020L513 1041Q522 1054 511 1067Q469 1078 431 1059L429 1045Z','url(#brass)',sw=4)
path('M256 1054Q296 1069 338 1050 M434 1050Q473 1069 514 1056','none','#6a664c',4)
path('M272 1034L312 1039 M282 1026L315 1033 M456 1027L482 1042 M449 1035L474 1049','none','#917746',2)
# Grandfather's body, slightly slumped to one side.
path('M288 650Q319 637 378 641L439 658Q466 669 471 706L464 835Q389 877 282 841L270 712Q267 667 288 650Z','url(#brass)',sw=5)
path('M433 661Q459 675 458 714L451 826Q421 846 400 847L411 682Z','#b88c49','none',0)
path('M287 684L297 806','none','#f7d999',6)
path('M292 827Q380 854 452 827','none','#9c7540',3)
rect(321,624,74,40,'url(#chrome)',8,sw=3)
path('M305 649L350 675L328 701L302 673 M396 650L357 675L376 700L412 668','#f2dca6',sw=3)
path('M339 672L353 665L367 674L362 693L347 695Z','#617e6a',sw=3)
path('M347 695L337 758L359 774L373 754L361 693Z','#617e6a',sw=3)
path('M345 739L366 719 M342 752L368 729','none','#95a37a',2)
# Patches, vents, and an old repair that has outlived the warranty.
path('M387 719L442 725L434 787L382 781Z','#dfc894',sw=2.5)
rivets([(393,727),(435,732),(390,773),(428,779)],'#d1a662')
for y in [742,752,762]: line(398,y,426,y+3,'#726d4d',3)
path('M294 757L321 752L329 797L300 803Z','#6e8c78',sw=2.5)
screw(303,765,3.8);screw(320,789,3.8)
path('M299 732L307 719L300 708 M418 805L434 807 M423 813L437 815','none','#8c713f',2)
# A wind-up key peeks out behind the left shoulder.
limb('M272 697L240 690','#879887',10)
path('M239 690C205 669 219 648 235 661Q244 672 239 690C264 667 273 688 260 698Q249 704 239 690Z','#bcad75',sw=3)
# Arm to the cane.
limb('M282 696L249 773L263 824','#c49e57',32)
circle(249,773,23,'#d2ba7d',sw=3);bolt(249,773,12,'#a69260')
path('M276 706L262 741','none','#f1d194',4)
# The walking stick's crook and rubber ferrule.
path('M227 826Q226 797 245 799Q264 800 259 820L243 1039','none','#283f40',15)
path('M227 826Q226 797 245 799Q264 800 259 820L243 1039','none','#97764e',8)
path('M248 865L244 910 M243 926L241 978','none','#d3b783',2)
ellipse(242,1045,15,12,'#6c8d76',sw=3)
# Articulated fingers wrapped around the cane.
path('M255 805Q270 800 277 814L277 834Q273 846 259 844L246 838L246 816Z','url(#brass)',sw=3)
for y in [816,826,835]: path(f'M248 {y}L266 {y+2}','none','#796640',2.5)
# His other hand is steadying the unruly child.
limb('M451 694L493 755L551 828','#c39b56',32)
circle(493,755,22,'#bbaf79',sw=3);bolt(493,755,11)
path('M520 784L539 808','none','#efd392',4)
# Antenna with a kink and a visibly repaired wire.
path('M325 481L321 451L305 437L314 416','none','#283f40',10)
path('M325 481L321 451L305 437L314 416','none','#c5ac74',4)
circle(315,411,10,'#769b85',sw=3)
path('M313 443L326 438 M316 448L329 443','none','#f1dab0',4)
# Elder's head: warm yellow enamel, age, and a patient sideways glance.
group('transform="rotate(-5 361 558)"')
rect(247,532,26,56,'#ab8950',8,sw=3)
rect(452,522,27,60,'#ab8950',8,sw=3)
path('M270 489Q273 470 299 470H420Q446 472 457 493L464 605Q463 626 440 637L296 638Q269 633 266 611L260 513Q260 498 270 489Z','url(#brass)',sw=5)
path('M277 502Q279 485 299 484H406','none','#fae0a1',6)
path('M444 500L449 601Q449 617 433 623L299 626','none','#ac8448',5)
# Optic bridge and circular lens rims.
path('M296 547L419 540','none','#5f725f',11)
circle(310,548,35,'#817f59',sw=3)
circle(310,548,28,'#eadcae',sw=3)
circle(410,540,34,'#817f59',sw=3)
circle(410,540,27,'#eadcae',sw=3)
# One sleepy shutter and one half-open eye looking towards the child.
path('M285 548Q307 534 335 546L335 551Q310 555 285 550Z','#bca66d',sw=2)
path('M291 554Q311 565 328 552','none','#283f40',4)
circle(420,548,9,'#293e3c',sw=1)
path('M385 533Q409 524 436 534L435 543L385 540Z','#c2ac76',sw=2)
path('M287 512L330 516 M391 506L434 501','none','#eedeac',8)
path('M288 508L330 512 M391 502L434 497','none','#796844',3)
# A little triangular nose, and moustache-like cooling fins.
path('M356 549L345 575L364 576Z','#b18c4e',sw=2.5)
path('M352 580Q333 570 318 585L314 596Q337 597 353 587Q369 599 394 591L389 580Q368 570 352 580Z','#d9d0a0',sw=3)
path('M335 608Q355 603 376 607','none','#5e6248',3)
path('M343 615L369 614','none','#937a49',2)
# Scratches, screws, and one ceramic repair staple.
rivets([(280,491),(438,492),(284,614),(443,610)],'#e9d09a')
path('M404 479L399 486L406 496L401 506','none','#897047',2)
line(395,488,406,487,'#e6dec1',3);line(399,499,410,497,'#e6dec1',3)
path('M279 582L287 576 M279 590L291 581','none','#b4884b',2)
end()

# Mother: rounded seafoam enamel, keeping everybody presentable.
# Lower legs and little heeled feet.
limb('M910 872L900 975L878 1056','#70998a',34)
limb('M984 872L996 977L1012 1059','#70998a',34)
circle(900,975,23,'#c6ccb0',sw=3);circle(996,977,23,'#c6ccb0',sw=3)
circle(900,975,11,'#65887a',sw=2);circle(996,977,11,'#65887a',sw=2)
path('M891 1006L883 1034 M1003 1006L1008 1037','none','#cfe0bb',5)
path('M862 1044Q880 1041 891 1053L907 1072L907 1091L882 1098L831 1092Q825 1080 838 1070L857 1060Z','url(#mint)',sw=4)
path('M998 1045Q1010 1040 1025 1057L1055 1076Q1068 1084 1060 1094Q1028 1104 994 1095L986 1077Z','url(#mint)',sw=4)
path('M833 1086Q873 1098 906 1082 M994 1087Q1025 1099 1060 1087','none','#37574f',4)
path('M878 1059L887 1065 M1006 1059L1018 1066','none','#e1ddba',4)
# Skirtlike flared pelvic shell, seated on the bench.
path('M875 764L1009 765Q1050 801 1047 866Q983 912 857 876Q848 817 875 764Z','url(#mint)',sw=5)
path('M874 848Q955 888 1033 852L1030 872Q949 903 866 875Z','#50887c','none',0)
path('M878 862Q943 889 1025 870','none','#c7d6b0',3)
# Main curved torso.
path('M895 584Q952 565 990 596Q1012 612 1017 646L1003 766Q976 798 879 771L863 675Q848 610 895 584Z','url(#mint)',sw=5)
path('M985 600Q1002 618 1003 647L991 749L1011 757L1018 644Q1014 614 985 600Z','#498779','none',0)
path('M879 627Q879 609 896 603 M877 644L890 728','none','#d1dfbb',6)
path('M885 738Q936 759 1008 738L1007 766Q949 788 889 766Z','#38685f',sw=3)
ellipse(952,759,22,17,'#d6be84',sw=3)
path('M943 758L951 750L961 758L953 768Z','#ba704c',sw=2)
# Collar and hex-nut pearl necklace.
rect(907,548,68,48,'url(#chrome)',13,sw=3)
path('M888 589L923 620L941 597L958 619L988 592Q942 568 888 589Z','#ebddba',sw=3)
path('M883 613Q927 673 993 618','none','#3d645a',3)
for x,y in [(888,619),(897,631),(909,642),(924,650),(941,653),(958,648),(974,638),(987,626)]:
    bolt(x,y,5.7,'#e9d7ac')
# Small enamel flower brooch.
for x,y in [(989,654),(999,660),(995,671),(983,672),(981,661)]: circle(x,y,7,'#d98c73',sw=1.7)
circle(990,663,5,'#eccb83',sw=1.5)
# One arm preoccupied with straightening the copper parent's tie.
limb('M875 643L811 599L742 523','#78a897',32)
circle(811,599,23,'#b5c8ab',sw=3);circle(811,599,11,'#578477',sw=2)
path('M851 628L830 613 M789 567L758 533','none','#d4dfbc',5)
path('M746 536L728 525L718 513L702 510Q694 505 699 499Q703 495 714 498L727 502L719 491Q715 484 722 481Q730 480 735 489L747 503L757 518Z','url(#mint)',sw=3)
path('M723 513L733 508 M730 521L741 515','none','#47746a',2)
# Other arm cups the baby from underneath.
limb('M1014 640L1042 756L960 841','#74a18f',34)
circle(1042,756,24,'#b9cbae',sw=3);circle(1042,756,11,'#588278',sw=2)
path('M1022 671L1034 728 M1027 780L995 812','none','#c2d8b4',5)
# Ear buns: each parent comes from a different factory.
ellipse(867,476,25,40,'#598b7b',sw=4)
ellipse(1060,469,25,40,'#598b7b',sw=4)
ellipse(1067,469,13,29,'#ced7b3',sw=3)
path('M1064 450Q1078 468 1066 487','none','#698f7d',3)
# Swept, dome-shaped head, a hint of an old kitchen appliance.
path('M864 479Q860 407 906 386Q953 363 1006 390Q1055 415 1060 476L1049 529Q1030 559 972 566Q909 563 880 536Z','url(#mint)',sw=5)
path('M877 448Q896 393 945 391','none','#d5e1bc',7)
path('M960 389Q1017 393 1042 440','none','#538879',3)
# Raised forehead plates suggest a meticulously kept coiffure.
path('M867 463Q913 438 944 407Q974 446 1059 459','none','#385f57',4)
path('M879 450Q921 430 941 410 M955 410Q987 441 1045 449','none','#c5d9b5',3)
path('M888 473Q917 446 945 448Q1000 450 1039 475L1035 520Q1017 547 971 550Q927 549 900 531Z','#e7dcba',sw=3)
path('M897 500Q913 487 931 496 M966 493Q983 481 1006 490','none','#5c7c6a',5)
# Side glance at the wonky bow tie.
ellipse(917,506,12,15,'#293f3b',sw=2);ellipse(982,502,12,15,'#293f3b',sw=2)
circle(914,501,3.5,'#fbefc8','none',0);circle(979,497,3.5,'#fbefc8','none',0)
path('M906 489L900 483 M910 486L907 479 M976 483L973 477','none','#3d5c51',2.8)
path('M945 501L938 517L950 518','none','#acac87',2.5)
path('M961 531Q974 523 985 529Q975 538 961 531Z','#b96e57',sw=2)
ellipse(909,525,11,5,'#d28e75','none',0,'opacity=".65"');ellipse(1009,520,10,5,'#d28e75','none',0,'opacity=".65"')
screw(881,479,5,'#d9d6b0');screw(1046,477,5,'#d9d6b0')
# Earrings are washers, not pearls.
circle(886,541,10,'#d5b272',sw=2.5);circle(886,541,4,'#6b9c88',sw=1.5)
circle(1044,537,10,'#d5b272',sw=2.5);circle(1044,537,4,'#6b9c88',sw=1.5)

# Teenager's gangly legs and conspicuously uncooperative stance.
limb('M1165 864L1159 978L1120 1083','#747987',30)
limb('M1223 870L1240 973L1281 1066','#747987',30)
# Accordion knees.
for x,y,rot in [(1159,978,12),(1240,973,-19)]:
    group(f'transform="rotate({rot} {x} {y})"')
    rect(x-21,y-23,42,48,'#344c4c',9,sw=3)
    for yy in range(y-16,y+19,8): line(x-17,yy,x+17,yy,'#adaab3',3)
    end()
path('M1146 1013L1130 1060 M1256 1005L1272 1042','none','#b8b2c1',4)
path('M1104 1069L1136 1079L1152 1104Q1150 1116 1134 1122L1070 1122Q1054 1116 1061 1101L1092 1089Z','#404750',sw=4)
path('M1263 1053L1290 1049L1312 1064L1341 1079Q1352 1095 1337 1104L1277 1104Q1262 1098 1260 1085Z','#404750',sw=4)
path('M1066 1113H1139 M1270 1094Q1307 1101 1344 1093','none','#d4c6b0',6)
path('M1095 1092L1123 1104 M1105 1085L1132 1097 M1280 1068L1303 1083 M1289 1063L1312 1078','none','#c7b8b4',3)
# Sloping torso; the kid who would rather be anywhere else.
path('M1136 677Q1184 669 1226 694L1260 725L1251 865Q1189 892 1118 861L1113 733Q1110 694 1136 677Z','url(#lilac)',sw=5)
path('M1163 701Q1195 696 1229 716L1230 846Q1183 865 1135 842L1139 730Z','#35494d',sw=3)
path('M1147 714L1164 742L1153 763 M1218 718L1207 743L1226 758','none','#777d8a',4)
# Heart sticker is partly hidden beneath the defensive crossed arms.
path('M1187 766C1175 749 1161 763 1169 776L1186 793L1201 778C1212 762 1197 754 1187 766Z','#d89080',sw=2)
path('M1184 771L1190 778L1184 784','none','#764f53',2)
path('M1131 840Q1186 865 1242 845L1241 865Q1184 887 1127 863Z','#53566c',sw=3)
for x,y in [(1139,854),(1158,859),(1178,862),(1198,862),(1218,858),(1234,854)]: circle(x,y,3,'#c1b6bc',sw=1)
# Arms firmly crossed.
limb('M1126 718L1095 800L1199 816','#9293a7',31)
circle(1095,800,23,'#5a6870',sw=3);bolt(1095,800,11,'#c0babc')
limb('M1249 737L1267 820L1148 794','#9696aa',32)
circle(1267,820,23,'#5a6870',sw=3);bolt(1267,820,11,'#c0babc')
path('M1249 757L1258 794 M1120 815L1165 822','none','#c3bdc8',4)
# Hands lock onto opposite elbows.
path('M1157 780L1136 779Q1127 781 1128 792L1128 805Q1132 816 1144 815L1162 810Z','#a4a1b1',sw=3)
path('M1131 790L1148 792 M1132 799L1148 801','none','#596774',2)
path('M1191 805L1209 804Q1222 805 1221 816L1214 833L1193 837L1184 828Z','#aaa5b3',sw=3)
path('M1196 817L1216 818 M1193 825L1212 828','none','#596774',2)
# Loosely hanging headphone cable.
path('M1278 611C1320 726 1280 783 1294 861C1305 924 1224 918 1218 874','none','#283f40',5)
path('M1278 611C1320 726 1280 783 1294 861C1305 924 1224 918 1218 874','none','#ac9885',1.5)
rect(1212,861,12,23,'#ccb188',3,sw=2)
# Neck leans away from the rest of the group.
path('M1161 644L1154 687L1199 705L1216 658Z','url(#chrome)',sw=4)
path('M1164 663L1208 680 M1161 674L1204 691','none','#3b5755',3)
# The tilted head and oversized headphones are one cohesive silhouette.
group('transform="rotate(10 1191 578)"')
path('M1101 566Q1081 473 1174 466Q1271 456 1288 552','none','#293e42',17)
path('M1101 566Q1081 473 1174 466Q1271 456 1288 552','none','#a89cae',9)
# A deliberately bent antenna.
path('M1180 492L1195 451L1234 455','none','#283f40',9)
path('M1180 492L1195 451L1234 455','none','#bfb5ba',4)
circle(1240,455,8,'#d59573',sw=2.5)
path('M1117 506Q1125 489 1147 488L1239 492Q1263 498 1270 523L1279 620Q1278 644 1255 656L1145 650Q1119 646 1117 623L1107 536Q1106 517 1117 506Z','url(#lilac)',sw=5)
path('M1119 528Q1137 512 1154 512L1224 516Q1247 520 1249 539L1255 612Q1254 627 1238 631L1148 626Q1134 621 1131 607Z','#d2c9c3',sw=3)
# Fringe: a hinged sun visor, aggressively asymmetric.
path('M1111 526L1117 503Q1125 488 1147 488L1240 492Q1263 498 1270 523L1272 545L1230 536L1227 523L1214 548L1202 531L1188 548L1183 528L1160 544L1158 530Z','#62697b',sw=3)
path('M1127 506L1170 503 M1180 503L1194 504','none','#bdb2c0',3)
# Deadpan eyes, both pointing away from the camera.
path('M1147 566L1180 566L1180 585Q1161 594 1148 582Z','#f1e2c7',sw=2.5)
path('M1201 568L1238 568L1236 586Q1218 595 1202 583Z','#f1e2c7',sw=2.5)
rect(1167,568,9,18,'#293e42',4,'none',0);rect(1224,570,9,17,'#293e42',4,'none',0)
line(1145,564,1183,568,'#364952',5);line(1200,568,1240,566,'#364952',5)
path('M1198 601L1223 603','none','#4b545b',4)
path('M1219 610L1228 610','none','#8b8187',2)
# Ear cups, a scuffed casing, and a safety-pin earring.
rect(1095,548,31,67,'#4b5e64',12,sw=3)
rect(1085,559,25,48,'#c3b4ba',10,sw=3)
rect(1262,549,31,71,'#4b5e64',12,sw=3)
rect(1281,560,20,48,'#c3b4ba',9,sw=3)
line(1093,570,1093,594,'#ece0cd',3);line(1290,571,1290,595,'#ece0cd',3)
path('M1256 645L1262 674Q1262 684 1253 684Q1245 684 1245 675L1243 651','none','#283f40',7)
path('M1256 645L1262 674Q1262 684 1253 684Q1245 684 1245 675L1243 651','none','#d8c7a6',3)
path('M1129 634L1143 637 M1132 641L1143 644','none','#e0c5b2',2)
screw(1247,506,4.5,'#d8bfaa');screw(1234,642,4.5,'#d8bfaa')
end()
# Dad's too-heavy hand lands on the reluctant shoulder, above the torso.
path('M1105 669Q1118 660 1130 669L1153 684Q1160 690 1154 697Q1148 702 1140 695L1129 688L1140 711Q1145 720 1138 723Q1130 726 1126 717L1114 696L1119 713Q1122 722 1115 724Q1109 725 1105 718L1096 695Q1091 679 1105 669Z','url(#copper)',sw=3.5)
path('M1108 677L1120 684 M1127 703L1135 700 M1107 705L1115 702','none','#914f3c',2)

# The orange child, unable to sit still.
# Short legs swing in opposite directions; one boot invades the foreground.
limb('M588 908L558 966L529 1001','#d9a258',29)
limb('M654 909L706 941L747 981','#d9a258',29)
circle(558,966,20,'#a7ab7d',sw=3);bolt(558,966,10,'#e5c38a')
circle(706,941,20,'#a7ab7d',sw=3);bolt(706,941,10,'#e5c38a')
path('M724 957L735 969 M547 982L539 990','none','#f6d18d',5)
group('transform="rotate(14 526 1017)"')
path('M510 990L539 989L550 1017Q555 1035 542 1045L506 1049Q487 1049 487 1034Q488 1018 506 1013Z','url(#orange)',sw=4)
path('M490 1034Q520 1046 548 1031','none','#f4dca2',6)
path('M511 1008L536 1010 M507 1017L538 1019','none','#725f42',3)
end()
group('transform="rotate(-30 759 993)"')
path('M738 964L765 963L776 980L801 986Q815 993 808 1007Q795 1026 735 1015L725 1002Z','url(#orange)',sw=4)
path('M729 1006Q773 1023 810 1003','none','#f2d89c',7)
path('M751 978L765 990 M760 973L774 986','none','#765f42',3)
path('M796 992L798 1003','none','#f4c77e',5)
end()
# The orange lunchbox-shaped body is slightly askew.
group('transform="rotate(-9 623 865)"')
path('M574 808Q619 793 670 810L697 839L686 903Q625 930 559 903L550 846Z','url(#orange)',sw=5)
path('M565 822L570 846L672 829L673 811','none','#fad28d',5)
path('M572 850L670 836L680 891Q630 912 574 894Z','#f1c777',sw=3)
path('M583 860L618 855L622 879L586 884Z','#456d60',sw=2.5)
path('M588 877L593 868L599 873L606 861L613 863','none','#b4c7a2',2)
circle(654,858,10,'#cb7050',sw=2.5);circle(658,883,6,'#75a492',sw=2)
path('M577 910Q629 927 684 905','none','#a15d36',3)
screw(561,842,4,'#f8d592');screw(680,841,4,'#f8d592')
end()
# Grandpa's protective hand on the child's near shoulder.
path('M541 813Q548 804 558 811L578 827Q584 833 579 838Q574 843 568 837L560 831L564 846Q565 854 558 854Q552 855 550 846L545 840L544 848Q541 855 535 850L530 832Z','url(#brass)',sw=3)
path('M548 818L558 826 M548 835L557 832','none','#8c7147',2)
# The other hand reaches across to its baby sibling.
limb('M687 843L727 820L788 835','#dd9852',25)
circle(727,820,18,'#98a987',sw=3);bolt(727,820,9,'#dfc18a')
path('M749 827L774 833','none','#f6cb82',4)
# Neck like a wound-up spring.
path('M595 799L606 822L646 816L642 791Z','#5b7b67',sw=3)
path('M601 804L642 800 M605 813L645 809','none','#e2c784',4)
# Head pitched at an entirely different angle to everyone else.
group('transform="rotate(-13 621 743)"')
# Little antenna with its rubber cap.
path('M629 679L630 657L613 644','none','#283f40',8)
path('M629 679L630 657L613 644','none','#d7bc80',3)
circle(610,641,9,'#da7551',sw=3)
ellipse(628,677,17,7,'#a9763c',sw=2)
rect(522,724,27,48,'#b5a36f',9,sw=3)
rect(698,709,26,51,'#b5a36f',9,sw=3)
path('M548 687Q584 669 648 676Q692 679 705 704L712 767Q708 798 679 811L567 809Q539 798 535 775L534 715Q535 697 548 687Z','url(#orange)',sw=5)
path('M550 709Q554 691 583 689L646 690','none','#f9d693',6)
path('M694 715L700 769Q695 789 679 796L584 799','none','#b76438',5)
path('M554 721Q556 707 572 706L669 705Q687 706 690 725L692 763Q690 782 672 789L576 789Q557 785 555 768Z','#f2d7a0',sw=3)
# One delighted squint and one enormous open optic.
path('M567 737Q582 715 600 735','none','#334d41',6)
ellipse(652,738,23,26,'#3e6253',sw=3)
ellipse(650,738,15,19,'#f7e9bd',sw=2)
circle(655,740,8,'#283f40',sw=1);circle(653,736,3,'#fff0c9','none',0)
path('M635 708L662 700','none','#75572f',4)
path('M588 758Q619 774 658 756Q659 781 629 786Q600 787 588 758Z','#354e42',sw=3)
path('M600 763L607 774L619 776L617 767 M638 767L638 775L649 767','#f6e4b7',sw=2)
ellipse(574,758,8,5,'#de8b55','none',0)
path('M670 762L682 758 M671 769L680 766','none','#c27d48',2)
rivets([(547,712),(690,699),(550,780),(692,781)],'#f5d490')
# A visibly replaced corner plate.
path('M548 691L565 686L568 706L543 714Z','#8da68a',sw=2)
screw(552,699,3.8,'#e7d6a3')
end()

# Baby: an egg-shaped new model with mismatched curious optics.
# Feet first; one has curled under its mother's hand.
limb('M850 867L838 886','#e0cc97',17)
limb('M894 863L910 878','#e0cc97',17)
ellipse(832,889,17,11,'#94b7a1',sw=3,extra='transform="rotate(-20 832 889)"')
ellipse(914,880,18,11,'#94b7a1',sw=3,extra='transform="rotate(17 914 880)"')
path('M831 896L837 888 M914 887L914 878','none','#456e61',2)
ellipse(870,832,47,48,'#efdeb1',sw=4,extra='transform="rotate(-8 870 832)"')
path('M826 836Q871 856 912 829L910 855Q877 891 838 863Z','url(#mint)',sw=3)
path('M851 851L859 875 M890 848L887 875','none','#537f70',2)
# Newborn serial port represented only as shapes, never lettering.
circle(869,817,9,'#6b9884',sw=2);circle(869,817,3,'#e7d3a1',sw=1)
# The siblings clasp hands.
limb('M831 816L812 837L791 835','#c7ceb0',17)
path('M780 826L790 823Q799 826 801 834L796 843Q791 848 785 842L778 837Z','#e6b764',sw=2.7)
path('M789 825L789 833L798 836 M783 832L787 841','none','#8a7148',1.8)
# Other hand rests on mother's wrist.
limb('M910 812L934 830','#c7ceb0',17)
path('M930 821Q947 816 951 827L948 843Q944 848 938 842L928 834Z','#eddda9',sw=3)
path('M938 825L943 837 M933 829L938 841','none','#9d976e',2)
# Mother's broad hand under the baby makes the cradling relationship explicit.
path('M963 831L952 842L933 862L913 865Q904 869 907 876Q910 881 922 878L938 875L925 885Q919 891 925 895Q931 899 940 891L957 878L948 891Q945 899 952 901Q959 900 964 890L977 860Q981 847 973 838Z','url(#mint)',sw=3.5)
path('M943 869L950 877 M952 879L960 884','none','#416d61',2)
# Coil antenna and a single sproutlike lamp.
path('M869 711C854 703 883 698 868 691C854 684 879 680 867 674','none','#283f40',4)
circle(867,670,8,'#df9871',sw=2.5)
path('M806 748Q809 705 851 701Q899 690 926 723Q940 743 932 771Q918 805 874 808Q830 808 812 782Z','url(#paper)',sw=4)
path('M816 739Q824 715 850 713','none','#fff1cf',5)
path('M812 774Q830 803 872 806Q920 802 932 771L933 779Q914 816 870 815Q826 811 812 782Z','#99b5a0',sw=2.5)
# Ear discs.
circle(809,758,11,'#9cb8a1',sw=3);circle(933,754,11,'#9cb8a1',sw=3)
circle(809,758,4,'#e8d9ad',sw=1.5);circle(933,754,4,'#e8d9ad',sw=1.5)
# Big pupil tracks the older sibling.
circle(850,748,25,'#517a69',sw=3);circle(850,748,19,'#f6e8bf',sw=2)
circle(843,749,12,'#283f40',sw=1);circle(839,744,4,'#fff2d0','none',0)
circle(902,746,19,'#517a69',sw=3);circle(902,746,14,'#f6e8bf',sw=2)
circle(897,747,9,'#283f40',sw=1);circle(894,743,3,'#fff2d0','none',0)
path('M837 715L852 712 M898 716L910 720','none','#809880',3)
ellipse(831,776,8,4,'#dda183','none',0);ellipse(913,772,7,4,'#dda183','none',0)
# A wing-nut pacifier, with hanging washer ring.
path('M863 775Q852 765 848 776Q846 786 861 785L878 785Q891 784 887 776Q883 770 875 776Z','#cc8c69',sw=2.5)
circle(870,780,8,'#e9bd7c',sw=2.5)
circle(870,792,10,'none','#283f40',4);circle(870,792,10,'none','#d6ac74',2)
screw(865,706,3.5,'#decea3');screw(824,793,3.5,'#decea3')

# Small wear marks, stitch lines and glints give the illustration a tactile finish.
# Ground scuffs are restrained, as on an old photographic backdrop.
for d in ['M314 1121L339 1123','M338 1131L387 1133','M666 1107L700 1109','M758 1136L813 1133','M987 1131L1020 1130','M1308 1140L1328 1137','M180 1072L192 1071']:
    path(d,'none','#986e58',1.6,'opacity=".45"')
# Very sparse chips on the enamel; always shaped, not random visual clutter.
for d in ['M583 404L589 403','M756 438L766 436','M292 791L295 799','M886 704L888 711','M988 716L989 726','M1189 850L1198 849','M617 887L628 885','M662 700L670 702']:
    path(d,'none','#f1d8ad',2.3,'opacity=".8"')
# Quiet half-tone shade accents.
path('M549 561L571 570L576 693L547 701Z','url(#dots)','none',0)
path('M978 667L1006 657L995 731L977 734Z','url(#dots)','none',0)
path('M392 796L444 799L438 821L392 836Z','url(#dots)','none',0)
path('M1135 745L1151 751L1145 775L1125 788Z','url(#dots)','none',0)
# A unified, delicate print grain. The SVG remains fully scalable.
rect(73,67,1354,1111,'#8e795e',0,'none',0,'opacity=".105" filter="url(#grain)" style="mix-blend-mode:soft-light"')
end() # photo clip
# Inner cream keyline and little die-cut corner ornaments on the mount.
rect(77,71,1346,1103,'none',11,'#f4d6aa',1.6)
for x,y,rot in [(50,46,0),(1450,46,90),(1450,1204,180),(50,1204,270)]:
    group(f'transform="translate({x} {y}) rotate({rot})"')
    path('M0 22V0H22','none','#987957',2)
    path('M7 18V7H18','none','#c49b70',1)
    end()
# Subtle flecks in the paper mount, outside the image only.
random.seed(42)
for _ in range(340):
    x=random.uniform(15,1485); y=random.uniform(12,1238)
    if x<63 or x>1437 or y<56 or y>1189:
        ellipse(round(x,2),round(y,2),round(random.uniform(.25,1),2),round(random.uniform(.25,.65),2),'#92724e','none',0,'opacity=".20"')
end()
add('</svg>')
(OUT/'awkward-family.svg').write_text('\n'.join(svg))
print(f'Wrote {OUT / "awkward-family.svg"} ({(OUT / "awkward-family.svg").stat().st_size:,} bytes)')
