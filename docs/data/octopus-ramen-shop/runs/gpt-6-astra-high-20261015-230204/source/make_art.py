from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path('output')
OUT.mkdir(exist_ok=True)
N='#172f3a'; D='#102832'; C='#fff1cc'; Y='#efb952'; R='#ed7866'; P='#ffc19a'; T='#63aaa0'; TD='#347b79'
s=[]
def add(x): s.append(x)
def path(d, fill='none', stroke=N, sw=4, extra=''):
    add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {extra}/>')
def rect(x,y,w,h,fill,rx=0,stroke=N,sw=4,extra=''):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
def circle(x,y,r,fill,stroke='none',sw=3):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def ellipse(x,y,rx,ry,fill,stroke=N,sw=3):
    add(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def text(x,y,t,size=20,fill=C,weight=500,spacing=0,anchor='middle',extra=''):
    add(f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{fill}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}" {extra}>{escape(t)}</text>')
def arm(d,w=38):
    path(d,'none',N,w+8); path(d,'none',R,w)
def sucker(x,y,r=5): ellipse(x,y,r,r*.7,P,'none')
def star(x,y,r=7):
    path(f'M {x-r} {y} Q {x} {y-1} {x} {y-r} Q {x+1} {y} {x+r} {y} Q {x} {y+1} {x} {y+r} Q {x-1} {y} {x-r} {y}',Y,'none',0)

add('''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="0 0 1200 1200" role="img" aria-labelledby="title desc">
<title id="title">Tako Ramen — Eight arms, one great bowl</title>
<desc id="desc">A coral-red octopus in a chef's hat cooks ramen in a turquoise night-market booth. Eight curling arms stir a pot, wield a ladle and chopsticks, and serve bowls under a golden striped awning and paper lantern. A warm cream border frames the detailed navy, teal, and vermilion illustration.</desc>
<defs>
 <pattern id="paper" patternUnits="userSpaceOnUse" width="17" height="19"><circle cx="3" cy="5" r=".7" fill="#172f3a" opacity=".075"/><circle cx="12" cy="15" r=".5" fill="#172f3a" opacity=".06"/></pattern>
 <pattern id="wall" patternUnits="userSpaceOnUse" width="52" height="52"><path d="M0 0V52" fill="none" stroke="#fff1cc" stroke-width="1" opacity=".065"/></pattern>
 <pattern id="waves" width="64" height="32" patternUnits="userSpaceOnUse"><path d="M-32 32a32 32 0 0164 0a32 32 0 0164 0M-24 32a24 24 0 0148 0m16 0a24 24 0 0148 0M-16 32a16 16 0 0132 0m32 0a16 16 0 0132 0M-8 32a8 8 0 0116 0m48 0a8 8 0 0116 0" fill="none" stroke="#9cc5ac" stroke-width="1.3" opacity=".32"/></pattern>
 <linearGradient id="lantern" x1="0" x2="1"><stop stop-color="#e99e48"/><stop offset=".5" stop-color="#ffdb83"/><stop offset="1" stop-color="#e99e48"/></linearGradient>
 <linearGradient id="broth" x2="0" y2="1"><stop stop-color="#efb952"/><stop offset="1" stop-color="#d8873e"/></linearGradient>
</defs>''')
# Paper border and midnight stage
rect(0,0,1200,1200,C,0,'none',0)
rect(26,26,1148,1148,N,34,'none',0)
rect(43,43,1114,1114,'none',22,T,1)
rect(27,27,1146,1146,'url(#paper)',32,'none',0)
text(600,91,'THE NIGHT MARKET',17,C,600,5)
path('M 265 84 H 399 M 801 84 H 935',stroke=T,sw=1)
star(242,84,6); star(958,84,6)
text(600,134,'EIGHT ARMS. ONE GREAT BOWL.',25,C,700,3)
# Background floating details
for x,y,r in [(113,232,7),(1080,191,6),(1098,450,8),(101,735,6),(1094,851,5),(125,978,7),(1055,1010,6)]: star(x,y,r)
for x,y in [(139,330),(1072,297),(110,508),(1069,728),(142,856),(1099,610),(100,1049)]: circle(x,y,2.5,T)
# round soft moon shape behind lantern
circle(220,555,105,'#213e44')
# Ground
ellipse(601,1083,474,27,'#0b222b','none')
path('M 111 1085 H 1089',stroke=T,sw=2)
# Booth structure, side planes and feet
rect(207,343,786,696,TD,5)
rect(230,390,740,432,'#203e44',0)
rect(232,392,736,428,'url(#wall)',0,'none',0)
path('M 994 365 L 1034 346 V 1035 L 994 1060 Z',TD)
path('M 1009 402 V 817 M 1011 880 V 1017',stroke=T,sw=3)
rect(205,1031,46,60,N,6)
rect(948,1031,46,60,N,6)
rect(211,1039,17,41,TD,3,'none',0)
rect(954,1039,17,41,TD,3,'none',0)
# sign roof offset and cream fascia
path('M 180 186 L 207 167 H 1008 L 1033 188 V 325 H 180 Z',TD)
rect(177,185,850,143,C,13,N,6)
rect(191,198,822,117,'none',7,R,2)
# sign coin on left
circle(254,257,43,R,N,3)
# mini octopus sign icon
path('M235 258 V245 C235 221 273 221 273 245 V259 C287 263 282 279 273 274 L268 267 C269 283 255 282 254 269 C251 285 239 281 241 267 C231 282 220 268 235 258 Z',N,'none',0)
circle(246,247,3,C);circle(262,247,3,C)
text(628,278,'TAKO RAMEN',71,N,900,2)
# awning cast shadow and canopy
path('M 176 343 H 1027 L 1060 407 V 449 H 158 V 407 Z',D,'none',0)
path('M 185 329 H 1018 L 1053 393 H 150 Z',Y,N,5)
# Trapezoidal striped roof
for a,b,c,d in [(185,270,245,150),(355,440,435,340),(525,610,625,530),(695,780,815,720),(865,950,1005,910)]:
    path(f'M{a} 330 H{b} L{c} 393 H{d} Z',C,'none',0)
path('M185 329 H1018 L1053 393 H150 Z','none',N,5)
for i in range(10):
    x=150+i*90.3
    path(f'M{x} 394 h90.3 v19 q-45.15 35 -90.3 0 Z',C if i%2==0 else Y,N,3)
path('M 161 393 H 1042',stroke=N,sw=4)
# upright posts
rect(198,434,24,389,Y,3)
rect(981,434,24,389,Y,3)
path('M 206 448 V 804 M 989 448 V 804',stroke=C,sw=3)
# left lantern, wire, caps
path('M 260 427 V 462',stroke=N,sw=5)
rect(235,459,50,12,N,4)
rect(219,471,82,134,'url(#lantern)',34,N,4)
for y in [487,505,523,541,559,577,594]:
    path(f'M 224 {y} Q 260 {y+8} 296 {y}',stroke='#ad713e',sw=1.2)
path('M244 478 Q233 540 244 597 M276 478 Q287 540 276 597',stroke=C,sw=2)
rect(236,602,48,12,N,4)
path('M260 614 V636 M251 638 H269',stroke=Y,sw=3)
text(260,531,'HOT',19,N,900,1)
text(260,554,'NOODS',13,N,800,.5)
# kitchen shelf with stacks of dishes
path('M 244 682 H 964',stroke=N,sw=13)
path('M 244 677 H 964',stroke=T,sw=5)
for y in [658,648,638]:
    path(f'M 291 {y} Q 320 {y+18} 348 {y} Z',C,N,3)
# right hanging menu
path('M 882 485 L 918 454 L 954 485',stroke=Y,sw=2)
rect(865,484,105,183,C,5,N,4)
rect(873,492,89,167,'none',0,R,1)
text(917,514,'TONIGHT',12,N,800,1)
path('M 883 527 H 950',stroke=R,sw=2)
text(917,551,'SHOYU',14,N,700,1)
text(917,571,'MISO',14,N,700,1)
text(917,591,'SPICY',14,N,700,1)
circle(917,627,19,R)
text(917,634,'08',19,C,800)
# little condiment jars on back shelf
rect(787,629,25,43,R,5,N,3);rect(784,622,31,10,C,2,N,3)
rect(826,641,19,31,Y,3,N,3);path('M829 637 L838 625 L842 640',C,N,3)
# rear utensils: ladle and high chopsticks
path('M 369 550 L 337 471',stroke=N,sw=13)
path('M 369 550 L 337 471',stroke=C,sw=6)
ellipse(330,457,23,27,T,N,4)
path('M317 456 Q322 441 335 444',stroke=C,sw=3)
# chopsticks diagonal right above noodle strand
path('M 800 526 L 867 462 M 808 538 L 887 482',stroke=N,sw=10)
path('M 800 526 L 867 462 M 808 538 L 887 482',stroke=Y,sw=5)
# noodles hanging from chopsticks
for i in range(5):
    x=845+i*6
    path(f'M {x} {494-i*3} C {x-17} 538 {x+8} 557 {x-9} 585 S {x-18} 619 {x-11} 640',stroke=N,sw=7)
    path(f'M {x} {494-i*3} C {x-17} 538 {x+8} 557 {x-9} 585 S {x-18} 619 {x-11} 640',stroke=Y,sw=3.2)
# 1 & 2: upper arms, waving the utensils
arm('M 551 657 C 492 659 476 614 451 582 C 426 548 391 578 369 550',36)
for x,y in [(510,649),(488,632),(474,609),(453,587),(425,573),(399,575)]: sucker(x,y)
arm('M 680 654 C 743 658 752 611 766 567 C 778 530 801 545 812 520',36)
for x,y in [(720,647),(741,628),(753,605),(761,581),(771,560),(791,546)]: sucker(x,y)
# 3 & 4: arms at the stove and tasting bowl
arm('M 559 686 C 509 653 465 654 436 686 C 418 706 401 697 395 710',33)
for x,y in [(490,668),(467,676),(448,693),(426,709)]: sucker(x,y,4)
arm('M 683 681 C 735 709 767 709 788 680 C 800 661 820 662 831 678',33)
for x,y in [(733,703),(757,704),(778,693),(798,678)]: sucker(x,y,4)
# tasting bowl held in rear right hand
path('M 794 646 Q 804 683 833 683 Q 860 683 874 646 Z',C,N,4)
ellipse(834,646,40,10,C,N,3)
ellipse(834,646,32,6,Y,'none')
path('M809 658 Q831 673 855 658',stroke=R,sw=3)
# head mantle
path('M 517 625 C 507 599 513 551 530 529 C 551 498 585 489 616 492 C 672 489 705 522 711 572 C 715 608 707 630 693 655 L 687 715 Q 609 759 538 711 Z',R,N,5)
# soft face light patch
path('M 532 579 C 532 542 559 520 590 518',stroke=P,sw=9)
# apron straps, laid before face
path('M549 662 L566 704 M674 662 L658 705',stroke=N,sw=15)
path('M549 662 L566 704 M674 662 L658 705',stroke=C,sw=9)
# chef hat silhouette and band
path('M 543 512 L 538 486 C 512 486 501 463 511 444 C 519 427 538 421 554 429 C 565 402 601 399 618 421 C 644 397 677 418 676 437 C 701 431 720 451 713 473 C 709 489 695 494 683 492 L 681 515 Z',C,N,5)
path('M 555 445 Q 561 457 559 472 M 619 437 V 471 M 680 453 Q 671 465 674 477',stroke='#d9c7a4',sw=4)
path('M 540 491 Q 614 481 685 495 L 681 523 Q 612 510 544 523 Z',C,N,4)
path('M 551 507 Q 615 499 674 509',stroke=Y,sw=3)
# face eyes & eyebrows
path('M553 568 Q566 561 579 567 M644 566 Q657 560 668 567',stroke=N,sw=4)
ellipse(567,588,7,10,N,'none');ellipse(655,588,7,10,N,'none')
circle(569,585,2,C);circle(657,585,2,C)
ellipse(545,608,15,7,'#df6056','none');ellipse(678,608,15,7,'#df6056','none')
# happy puckered octopus mouth
path('M594 613 Q611 630 629 613 Q625 639 611 639 Q598 638 594 613 Z',N,N,3)
path('M603 631 Q612 626 621 632',stroke=R,sw=5)
# a little drop on temple
path('M688 553 Q700 567 692 572 Q681 575 688 553',P,'none',0)
# 5 & 6: low lateral curls
arm('M 553 708 C 491 700 468 749 426 745 C 403 744 387 726 370 741 C 355 755 366 778 383 770',34)
for x,y in [(501,722),(480,737),(458,751),(433,757),(408,752),(379,751)]: sucker(x,y,4.5)
arm('M 683 711 C 742 722 769 752 814 740 C 837 734 850 718 872 735 C 894 752 881 779 864 766',34)
for x,y in [(737,738),(760,749),(787,756),(814,753),(839,745),(866,748)]: sucker(x,y,4.5)
# apron white bib
path('M565 683 Q611 697 660 683 L678 757 Q613 798 547 758 Z',C,N,4)
path('M 583 725 Q 611 737 640 725 V 751 Q612 768 584 751 Z',Y,N,3)
path('M604 737 Q609 731 614 737 Q619 731 624 737 Q625 741 614 749 Q602 742 604 737',R,'none',0)
# 7 & 8 front serving arms
arm('M 555 743 C 533 762 538 790 506 795 C 482 798 478 777 490 769',30)
for x,y in [(541,769),(531,787),(511,802)]: sucker(x,y,4)
arm('M 670 748 C 691 767 693 800 729 806 C 761 813 790 803 797 783',31)
for x,y in [(690,779),(705,799),(727,814),(753,813),(778,802)]: sucker(x,y,4)
# stove, burner and cooking pot
rect(302,790,170,30,TD,5,N,4)
rect(317,782,139,12,N,2)
for x in [337,357,378,398,419,438]:
    path(f'M{x} 783 Q{x-7} 773 {x} 766 Q{x+8} 773 {x} 783',Y,'none',0)
path('M 323 731 V 774 Q 386 798 451 774 V 731 Z',T,N,4)
path('M 331 745 V 772 Q 342 779 351 779 V 745',C,'none',0)
path('M322 744 H307 Q293 759 311 765 H322 M452 744 H466 Q480 759 462 765 H452',stroke=N,sw=10)
path('M322 744 H307 Q293 759 311 765 H322 M452 744 H466 Q480 759 462 765 H452',stroke=T,sw=4)
ellipse(387,730,65,15,C,N,4)
ellipse(387,730,54,9,'url(#broth)','none')
path('M348 731 Q359 722 369 730 T389 730 T409 730 T429 729',stroke=C,sw=3)
# stirring stick in grasp
path('M 403 729 L 398 689',stroke=N,sw=9)
path('M 403 729 L 398 689',stroke=Y,sw=4)
path('M388 704 Q400 699 407 706',stroke=R,sw=13)
# wisps of steam, deliberately delicate
for d in ['M355 705 C335 681 369 670 354 647','M381 696 C365 677 392 660 382 640','M413 703 C429 684 405 671 420 649']:
    path(d,stroke=C,sw=3,extra='opacity=".67"')
# counter slab
path('M 180 815 H 1025 L 1050 842 H 154 Z',Y,N,5)
path('M 192 823 H 1015',stroke=C,sw=3)
rect(154,841,896,26,R,4,N,5)
path('M167 849 H1034',stroke=P,sw=3)
# booth front panels
rect(181,868,844,193,Y,3,N,5)
rect(200,885,386,158,TD,3,N,3)
rect(604,885,402,158,TD,3,N,3)
rect(201,886,384,156,'url(#waves)',2,'none',0)
rect(605,886,400,156,'url(#waves)',2,'none',0)
# front medallion and lovely lockup
rect(354,913,480,100,C,50,N,4)
text(594,955,'BROTH & SOUL',30,N,800,3)
text(594,984,'MADE WITH ALL EIGHT ARMS',12,TD,700,2)
circle(322,964,7,Y);circle(865,964,7,Y)
# left service bowl on top, below front hand
ellipse(509,821,65,10,N,'none')
path('M456 783 Q462 821 509 829 Q552 823 563 783 Z',C,N,4)
path('M466 800 Q510 820 551 800',stroke=R,sw=6)
ellipse(509,783,54,12,C,N,4)
ellipse(509,784,44,7,Y,'none')
path('M482 782 Q489 770 499 781 T519 781 T540 782',stroke=C,sw=3)
for x,y in [(489,782),(516,777),(535,785)]: path(f'M{x} {y} l6 -3',stroke=TD,sw=4)
# huge signature ramen bowl foreground
ellipse(754,850,115,13,N,'none')
path('M 644 778 Q 650 829 696 847 Q 751 870 810 846 Q 850 828 861 778 Z',R,N,5)
# bowl cream lower decoration
path('M668 817 Q754 849 837 817 Q820 841 798 849 Q750 866 706 849 Q682 840 668 817 Z',C,'none',0)
path('M 679 835 Q750 862 826 835',stroke=N,sw=2)
# repeating simple rim motif
for x in range(669,840,22):
    path(f'M{x} 801 v8 h11 v-8',stroke=C,sw=3)
ellipse(752,779,109,28,C,N,5)
ellipse(752,779,97,21,'url(#broth)',N,2)
# nori crisp back corner
path('M 785 769 L 791 720 L 827 729 L 820 776 Z',N,N,3)
for x in [797,805,813]: path(f'M{x} 735 l-4 28',stroke=TD,sw=2)
# noodle nests
for d in ['M673 779 C683 759 706 762 710 777 S735 794 744 779 S765 759 782 778','M676 784 C690 767 700 770 705 785 S728 800 740 785 S758 769 777 785','M686 771 C698 753 718 763 719 775 S742 790 754 775 S778 766 787 781','M691 786 C702 777 711 783 718 791','M734 768 C746 757 762 762 770 773']:
    path(d,stroke=N,sw=6)
    path(d,stroke=Y,sw=3.5)
# egg half angled
add('<g transform="rotate(-25 721 754)">')
ellipse(721,754,26,34,C,N,3)
ellipse(721,759,16,20,Y,'#da9140',2)
path('M713 754 Q719 744 726 751',stroke='#ffdc7c',sw=3)
add('</g>')
# pork slice
path('M 772 790 C 771 775 796 760 816 767 C 836 773 830 788 812 794 Z',P,N,3)
path('M785 785 C783 775 807 769 815 776 Q823 786 803 787 Q792 788 798 780',stroke=R,sw=3)
# scallions
for x,y,a in [(677,773,20),(693,794,-20),(744,791,25),(761,766,-20),(835,782,35),(779,798,10),(731,780,50)]:
    add(f'<ellipse cx="{x}" cy="{y}" rx="6" ry="3" transform="rotate({a} {x} {y})" fill="{T}" stroke="{N}" stroke-width="1.5"/>')
# narutomaki with scalloped edge
path('M751 746 l6 -4 6 4 7 0 2 7 5 5 -4 6 -1 7 -8 1 -5 4 -6 -4 -7 -1 -1 -7 -4 -5 5 -6 Z',C,N,2)
path('M754 759 C755 748 771 750 769 760 C767 768 756 766 759 759 Q762 755 765 759',stroke=R,sw=2.6)
# steam from hero bowl
path('M718 710 C698 690 729 680 720 660 M748 729 C767 708 738 699 750 681 M779 713 C791 698 779 688 784 678',stroke=C,sw=3,extra='opacity=".8"')
# right small tray with soy bottle & chopsticks holder
ellipse(931,818,37,8,N,'none')
path('M907 777 L913 750 H941 L947 777 V812 Q928 824 907 812 Z',D,N,3)
rect(916,738,22,15,R,3,N,3)
rect(909,781,36,24,C,3,N,2)
text(927,797,'SOY',10,N,800,1)
# left towel over counter
path('M 237 810 H285 L292 883 Q268 893 245 883 Z',C,N,3)
path('M251 821 L256 875 M263 821 L269 878 M276 821 L282 875',stroke=T,sw=2)
path('M247 871 L290 871',stroke=R,sw=3)
# subtle construction details
for x in [212,991]:
    for y in [898,1030]: circle(x,y,3,N)
# bottom typography
text(600,1121,'COME HUNGRY. LEAVE HAPPY.',20,C,700,3)
text(600,1145,'EST. 08  /  NOODLES UNTIL MIDNIGHT',11,T,600,2)
path('M 213 1115 H 337 M 863 1115 H 987',stroke=T,sw=1)
# final fine paper fleck overlay
rect(0,0,1200,1200,'url(#paper)',0,'none',0,extra='pointer-events="none"')
add('</svg>')
(OUT/'tako-ramen.svg').write_text('\n'.join(s))
print(f'Wrote {OUT / "tako-ramen.svg"} ({(OUT / "tako-ramen.svg").stat().st_size:,} bytes)')
