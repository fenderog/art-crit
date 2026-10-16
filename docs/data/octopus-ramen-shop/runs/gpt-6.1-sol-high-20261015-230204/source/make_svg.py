from pathlib import Path
from html import escape
import random

# A self-contained vector poster. No external assets or fonts are required.
OUT = Path('output')
OUT.mkdir(exist_ok=True)
W = H = 1400
INK = '#203f43'
CREAM = '#fff4d9'
CORAL = '#ee876d'
RED = '#ca5541'
TEAL = '#367875'
s = []
def raw(x): s.append(x)
def path(d, fill='none', stroke=INK, sw=5, **attrs):
    emit('path', d=d, fill=fill, stroke=stroke, stroke_width=sw, **attrs)
def emit(tag, **a):
    a = {k.replace('_','-'):v for k,v in a.items() if v is not None}
    s.append('<'+tag+' '+ ' '.join(f'{k}="{escape(str(v), quote=True)}"' for k,v in a.items())+'/>')
def rect(x,y,w,h,fill,rx=0,stroke=INK,sw=5,**a):
    emit('rect',x=x,y=y,width=w,height=h,rx=rx,fill=fill,stroke=stroke,stroke_width=sw,**a)
def ellipse(x,y,rx,ry,fill,stroke=INK,sw=5,**a):
    emit('ellipse',cx=x,cy=y,rx=rx,ry=ry,fill=fill,stroke=stroke,stroke_width=sw,**a)
def circle(x,y,r,fill,stroke=INK,sw=5,**a): ellipse(x,y,r,r,fill,stroke,sw,**a)
def line(x1,y1,x2,y2,stroke=INK,sw=5,**a):
    emit('line',x1=x1,y1=y1,x2=x2,y2=y2,stroke=stroke,stroke_width=sw,**a)
def text(x,y,t,size=24,fill=INK,weight=600,spacing=0,anchor='middle',**a):
    att = dict(x=x,y=y,fill=fill,font_family='Avenir Next, Avenir, Trebuchet MS, sans-serif',font_size=size,font_weight=weight,letter_spacing=spacing,text_anchor=anchor,**a)
    raw('<text '+' '.join(f'{k.replace("_","-")}="{escape(str(v), quote=True)}"' for k,v in att.items())+'>'+escape(t)+'</text>')
def group(**a): raw('<g '+' '.join(f'{k.replace("_","-")}="{v}"' for k,v in a.items())+'>')
def end(): raw('</g>')
def star(x,y,r=13,color=RED):
    path(f'M{x} {y-r} Q{x+2} {y-2} {x+r} {y} Q{x+2} {y+2} {x} {y+r} Q{x-2} {y+2} {x-r} {y} Q{x-2} {y-2} {x} {y-r}Z',color,'none',0)
def arm(d):
    path(d,'none',INK,65)
    path(d,'none',CORAL,54)
def suckers(points):
    for x,y,r in points:
        ellipse(x,y,r,r*.70,'#ffb899',RED,2)
        path(f'M{x-r*.35} {y+1} Q{x} {y-r*.4} {x+r*.35} {y+1}','none',RED,1.5)

raw('''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1400" viewBox="0 0 1400 1400" role="img" aria-labelledby="title desc">
<title id="title">Octo Ramen — eight arms, one perfect bowl</title>
<desc id="desc">A cheerful coral-colored octopus in a chef's hat runs a tiny teal ramen booth. Eight curling arms juggle a ladle, noodles, a tasting bowl and a steaming bowl of ramen, beneath a red striped awning and a glowing paper lantern. A warm, detailed, vintage-style vector illustration.</desc>
<defs>
  <pattern id="awning" x="184" y="292" width="144" height="120" patternUnits="userSpaceOnUse"><rect width="144" height="120" fill="#e87355"/><path d="M0 0H60L88 120H28Z" fill="#f4b185"/></pattern>
  <pattern id="waves" width="70" height="32" patternUnits="userSpaceOnUse"><path d="M-35 32a35 25 0 0 1 70 0m0 0a35 25 0 0 1 70 0M-35 32a35 16 0 0 1 70 0m0 0a35 16 0 0 1 70 0" fill="none" stroke="#80aaa0" stroke-width="2" opacity=".35"/></pattern>
  <linearGradient id="lantern" x1="0" x2="1"><stop stop-color="#dd6b45"/><stop offset=".5" stop-color="#ffc77e"/><stop offset="1" stop-color="#e4854d"/></linearGradient>
  <linearGradient id="soup" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#e8a644"/><stop offset="1" stop-color="#c57231"/></linearGradient>
  <clipPath id="head"><path d="M566 689C566 611 606 562 700 562S838 614 838 689C838 766 791 812 702 812S566 768 566 689Z"/></clipPath>
  <clipPath id="broth"><ellipse cx="702" cy="857" rx="139" ry="43"/></clipPath>
</defs>
<g stroke-linecap="round" stroke-linejoin="round">
''')
# Warm printed-paper ground, with sparse, deterministic freckles.
rect(0,0,W,H,'#f6e8ca',0,'none',0)
random.seed(8)
for i in range(1900):
    circle(random.uniform(20,1380),random.uniform(20,1380),random.choice([.65,.8,1.1]),'#9e7754','none',0,opacity=random.uniform(.035,.12))
rect(39,39,1322,1322,'none',28,'#b5a687',2)
# Sun disk and understated peripheral steam/wave decorations.
circle(700,657,533,'#efdab1','none',0)
path('M176 697C95 657 119 597 171 608C214 618 195 662 163 644M1212 808C1294 802 1309 745 1264 739C1238 736 1229 762 1248 772','none','#d9c49e',4)
star(191,527,17)
star(1228,398,12)
star(1135,203,17,TEAL)
star(229,243,12,TEAL)
line(123,393,163,393,'#a6a58c',3)
line(143,373,143,413,'#a6a58c',3)
# Header typography, deliberately quiet and separated from the sign.
text(700,103,'EIGHT ARMS. ONE PERFECT BOWL.',19,INK,650,4)
line(226,96,340,96,'#9b9d84',2)
line(1060,96,1174,96,'#9b9d84',2)
# Grounding shadow and a few sidewalk dashes.
ellipse(711,1195,528,45,'#cdbd99','none',0,opacity='.55')
line(133,1217,266,1217,'#b0a486',3)
line(1130,1224,1247,1224,'#b0a486',3)
line(1203,1196,1280,1196,'#b0a486',3)
# Wheels / feet.
for x in (309,1087):
    rect(x-28,1134,56,58,INK,9,INK,4)
    circle(x,1182,23,INK,CREAM,3)
    circle(x,1182,8,'#71908a',INK,3)
# Stall interior and timber frame.
rect(270,389,861,648,INK,7,INK,6)
rect(299,458,802,462,'#244d50',0,'none',0)
rect(298,771,805,149,'#2c5757',0,'none',0)
# Tile joints and shelves, drawn behind the chef.
for y in (713,758,803,848,893):
    line(300,y,1100,y,'#47706a',2)
for y in (713,803,893):
    for x in range(320,1100,94): line(x,y-42,x,y,'#47706a',2)
for y in (758,848):
    for x in range(367,1100,94): line(x,y-42,x,y,'#47706a',2)
# Left, handwritten-style menu placard.
group(transform='rotate(-4 383 620)')
rect(310,531,160,196,'#142f35',6,'#a5b4a0',3)
text(390,563,'TODAY’S',14,CREAM,650,2)
text(390,589,'SPECIAL',21,'#efb46d',750,2)
line(329,602,450,602,'#89a99b',2)
text(328,630,'MISO',17,CREAM,500,1,'start')
text(449,630,'08',17,'#efb46d',500,1,'end')
text(328,659,'SHOYU',17,CREAM,500,1,'start')
text(449,659,'08',17,'#efb46d',500,1,'end')
text(390,698,'made with love',12,'#aec2aa',500,1)
end()
# Jar shelf at upper right.
rect(945,685,150,14,'#c49969',3,INK,3)
for x,h in ((968,69),(1020,88),(1071,58)):
    rect(x-17,685-h,34,h,'#769b88',6,INK,3)
    rect(x-20,681-h,40,11,'#d6ba83',2,INK,3)
    rect(x-12,698-h,24,28,CREAM,2,'none',0)
    path(f'M{x-6} {709-h}h12m-6 -5v13','none',RED,2)
# Tiny hanging order slips.
for x,y,t in ((857,543,'01'),(902,550,'02')):
    line(x,y-23,x,y,'#b5ae8b',2)
    rect(x-16,y,32,73,'#e9d5a6',1,INK,2)
    text(x,y+26,t,12,INK,650,1)
    line(x-6,y+41,x+6,y+41,RED,2)
    line(x-6,y+50,x+6,y+50,RED,2)
# Awning support posts with hand-painted wood accents.
for x in (258,1112):
    rect(x,400,29,620,'#d7a56a',5,INK,5)
    line(x+9,544,x+9,815,'#f3c98c',3)
    path(f'M{x+21} 748v81m-8 34v59','none','#ae7b4c',2)
# Roof silhouette and striped canvas.
path('M184 380L247 292H1151L1215 380V409H184Z','#b54736',INK,6)
path('M247 292H1151L1215 380H184Z','url(#awning)',INK,5)
path('M247 303H1151','none','#f8c28c',4)
path('M185 381H1215V409H185Z',RED,INK,5)
line(202,393,1197,393,'#ef9271',3)
# Scalloped noren panels.
for i in range(6):
    x=277+i*141
    d=f'M{x} 411H{x+132}V493Q{x+67} 528 {x} 493Z'
    path(d,TEAL if i%2==0 else '#2e6968',INK,4)
    path(f'M{x+9} 422H{x+123}','none','#83aaa0',2)
    line(x+66,434,x+66,440,'#b8ceb3',2)
    if i in (0,5):
        circle(x+66,468,19,CREAM,'none',0)
        # Small bowl crest.
        path(f'M{x+53} 466H{x+79}Q{x+76} 478 {x+66} 479Q{x+56} 478 {x+53} 466Z',TEAL,'none',0)
        path(f'M{x+61} 456q-3 3 0 6m10 -6q-3 3 0 6','none',TEAL,2)
    else:
        # Pale, simple seigaiha crest.
        for j in range(3): path(f'M{x+44+j*15} 474q8 -15 16 0','none','#c5d8bd',2.5)
# Wooden sign mounts, then main enamel sign.
for x in (455,945):
    rect(x,237,13,64,'#b97d52',2,INK,3)
path('M431 160H969L996 184V262L970 285H430L405 262V184Z','#c88f58',INK,6)
path('M435 168H965L985 188V256L965 276H435L416 256V188Z',CREAM,INK,3)
path('M434 181H966M434 263H966','none','#c4a66e',2)
text(700,239,'OCTO RAMEN',56,INK,850,3)
for x in (439,962):
    circle(x,218,6,RED,'none',0)
# Little ticket detail on the roof.
text(299,363,'NO. 08',16,INK,750,2)
text(1108,363,'EST. ∞',16,INK,700,1)
# Lantern bracket and hanging lantern: off the right edge of the booth.
path('M1136 423H1222Q1234 423 1234 439V477','none',INK,7)
line(1195,426,1195,479,INK,4)
rect(1171,478,48,16,INK,5,INK,3)
ellipse(1195,567,57,83,'url(#lantern)',INK,5)
for x in (-35,-18,0,18,35):
    path(f'M{1195+x*.65} 490Q{1195+x*1.45} 566 {1195+x*.65} 644','none','#b95b37',2,opacity='.55')
for y in (513,538,566,594,620):
    path(f'M1145 {y}Q1195 {y+12} 1245 {y}','none','#d17c43',2,opacity='.65')
rect(1173,642,44,16,INK,4,INK,3)
# Lantern emblem, not text, so it reads at small sizes.
circle(1195,566,28,CREAM,'none',0)
path('M1176 561H1214Q1210 581 1195 583Q1180 581 1176 561Z',RED,'none',0)
path('M1188 543q-5 6 0 12m12 -12q-5 6 0 12','none',RED,3)
line(1195,659,1195,689,RED,4)
path('M1184 686l-4 25m15 -25v30m10 -30l5 25','none',RED,4)
# Props held by the rear arms. Ladle suspended to the left.
group(transform='rotate(-20 389 587)')
rect(380,512,13,105,'#bd8657',6,INK,4)
line(387,544,387,569,'#f4cc91',3)
path('M354 485Q387 468 420 485L414 517Q387 539 360 517Z','#a3bcb0',INK,4)
ellipse(387,485,33,12,'#426b68',INK,3)
path('M365 507Q387 521 409 507','none','#d9e0be',3)
end()
# Right hand's noodle basket handle and wire basket.
path('M963 623L1006 497','none',INK,13)
path('M963 623L1006 497','none','#b88650',7)
circle(1008,490,7,'#c19761',INK,3)
# Rear limbs, each a separate curling silhouette.
arm('M621 753C534 766 483 709 456 646C435 597 406 578 382 597C361 613 374 639 394 632')
suckers([(439,646,8),(453,673,8),(469,697,8),(490,719,8),(516,737,8)])
arm('M789 755C873 771 917 709 930 655C939 615 959 596 982 612C1001 627 988 650 974 641')
suckers([(917,680,8),(907,709,8),(890,735,8),(867,752,8),(840,765,8)])
# Noodles dangling out of the raised basket.
for i in range(6):
    x=981+i*9
    path(f'M{x} 684C{x-12} 706 {x+12} 717 {x-5} {741+(i%3)*8}','none',INK,7)
    path(f'M{x} 684C{x-12} 706 {x+12} 717 {x-5} {741+(i%3)*8}','none','#f1cf77',4)
path('M961 639L1037 662L1016 704Q982 710 962 685Z','#c6ad78',INK,4)
for j in range(5):
    path(f'M{971+j*12} {646+j*3}L{971+j*9} {691+j*2}','none','#796f4f',2)
for y in (659,671,684):
    path(f'M963 {y}L1028 {y+16}','none','#796f4f',2)
ellipse(999,651,41,12,'#e5ce95',INK,4,transform='rotate(17 999 651)')
# Outer middle arms, tasting and seasoning.
arm('M608 792C525 772 483 819 422 804C377 793 342 772 325 742')
suckers([(389,800,7),(415,816,7),(445,823,8),(474,820,7),(501,810,7)])
arm('M794 791C874 775 934 818 985 788C1011 773 1032 744 1026 717')
suckers([(902,806,8),(929,811,8),(957,808,8),(984,799,7),(1007,780,7)])
# Tiny tasting bowl on the left hand.
ellipse(324,725,42,13,CREAM,INK,4)
path('M283 726Q289 768 323 770Q359 768 365 726Z','#e8b566',INK,4)
path('M293 738Q322 751 355 738','none',RED,3)
ellipse(324,726,35,8,'#986b3b','none',0)
path('M316 701C302 687 329 680 318 663M337 704C326 692 347 684 338 673','none','#e6d7b2',4)
# Seasoning shaker sitting in the right hand.
group(transform='rotate(19 1029 697)')
rect(1011,661,39,65,'#e4b65e',9,INK,4)
rect(1007,653,47,17,'#a5b9a6',5,INK,4)
for x in (1018,1030,1042): circle(x,660,1.6,INK,'none',0)
rect(1018,680,25,27,CREAM,3,'none',0)
path('M1025 699l8 -12m-8 2l8 8','none',RED,3)
end()
# A few grains fall towards the bowl.
for x,y in ((1008,741),(995,756),(1004,773),(988,777)):
    circle(x,y,2.4,'#f6c16c','none',0)
# Main octopus mantle.
path('M566 689C566 611 606 562 700 562S838 614 838 689C838 766 791 812 702 812S566 768 566 689Z',CORAL,INK,6)
group(clip_path='url(#head)')
ellipse(739,640,145,148,'#f29a7c','none',0)
path('M563 707Q584 775 654 794Q712 813 787 780Q756 825 685 833H567Z','#dc705b','none',0)
ellipse(602,671,14,32,'#f9b794','none',0,transform='rotate(13 602 671)',opacity='.75')
# Light mottled mantle spots.
for x,y,r in ((605,619,5),(618,608,3),(788,625,6),(800,643,4),(782,647,3),(592,705,4),(811,700,5)):
    circle(x,y,r,'#d56b57','none',0,opacity='.5')
end()
# Chef's toque, with curved seams.
path('M625 529C598 531 590 500 604 481C615 466 632 463 648 471C647 443 673 428 696 438C711 416 749 426 755 452C786 444 811 468 800 493C817 514 797 538 777 535L775 569H628Z',CREAM,INK,5)
path('M632 526L631 557Q703 571 776 557L777 526Q708 536 632 526Z','#e8d7b6','none',0)
path('M628 530Q704 544 779 530M629 556Q705 568 776 556','none',INK,3)
path('M647 477Q639 492 648 510M695 450Q684 472 690 513M755 463Q766 486 756 510','none','#c9b994',3)
# Face: smiling eyes, rounded siphon, cheeks.
path('M630 669Q648 649 666 669M737 669Q754 649 773 669','none',INK,6)
path('M637 636Q649 630 662 636M744 636Q757 630 769 638','none','#b94e43',4)
ellipse(620,690,18,10,'#d65c54','none',0,opacity='.6')
ellipse(785,690,18,10,'#d65c54','none',0,opacity='.6')
path('M676 707Q676 687 700 687Q725 687 725 707Q724 729 701 729Q678 729 676 707Z','#f5a084',INK,4)
ellipse(702,709,11,9,INK,'none',0)
path('M693 731Q702 741 713 732','none','#b75045',3)
# Neckerchief over the mantle base.
path('M641 772Q701 803 763 772L746 808L705 821L660 806Z',CREAM,INK,4)
path('M697 798L680 834L703 825L720 845L721 803Z','#eabc63',INK,4)
circle(707,802,11,CREAM,INK,3)
# Lower four tentacles, curled around the working counter.
arm('M632 805C572 818 539 873 482 891C440 905 401 891 414 867C423 851 441 861 431 873')
suckers([(569,854,8),(548,875,8),(522,892,8),(492,903,8),(465,909,7),(439,904,7)])
arm('M776 809C829 850 861 899 922 899C961 901 982 883 967 867C955 854 937 870 952 879')
suckers([(834,870,8),(854,889,8),(880,904,8),(909,912,8),(937,911,7),(960,901,7)])
arm('M662 814C632 831 583 831 565 862C546 895 559 922 580 918C597 915 595 898 584 899')
suckers([(575,849,7),(561,869,7),(557,891,7),(566,910,6)])
arm('M742 815C774 832 819 832 837 862C855 894 844 921 823 918C806 915 809 898 819 899')
suckers([(826,849,7),(840,869,7),(844,891,7),(836,910,6)])
# Counter slab. End grain and a slim reflected highlight.
path('M237 923H1165L1191 951L1169 982H233L210 951Z','#b87e50',INK,6)
path('M237 923H1165L1191 951H210Z','#e4b47a',INK,5)
line(245,936,1152,936,'#f3d49a',3)
rect(231,956,940,28,'#be8757',3,INK,5)
line(249,968,1151,968,'#e0ab70',3)
# Counter props: condiment bottles and a chopstick can, to the right.
rect(1045,865,59,64,'#f1d59b',6,INK,4)
rect(1040,859,68,15,'#d6a461',4,INK,4)
rect(1057,886,35,24,CREAM,2,'none',0)
text(1074,904,'CHILI',10,RED,800,1)
for x,y in ((1060,877),(1085,880),(1095,895),(1054,917)):
    circle(x,y,2.1,RED,'none',0)
# Soy cruet.
path('M1005 927V889Q1005 881 1014 880V865H1035V880Q1044 883 1044 891V927Z','#834d39',INK,4)
rect(1010,859,31,11,RED,3,INK,3)
rect(1012,895,26,24,CREAM,2,INK,2)
circle(1025,907,6,RED,'none',0)
# Upright chopsticks, left of bowl.
for x,tilt in ((490,-15),(505,-9),(517,-3),(529,6),(542,12)):
    line(x,859,x+tilt,769,INK,8)
    line(x,859,x+tilt,769,'#d4a76b',4)
path('M481 841H549L541 927H490Z',TEAL,INK,4)
path('M493 848H537M495 916H536','none','#81aa99',3)
circle(514,881,17,CREAM,'none',0)
path('M505 882l7 7l12 -18','none',TEAL,3)
# Stack of plates at the left.
for y in (915,905,895):
    path(f'M306 {y}Q353 {y+18} 402 {y}L395 {y+12}Q355 {y+27} 313 {y+12}Z',CREAM,INK,3)
    ellipse(354,y,48,8,'#ede0bc',INK,3)
# The hero ramen bowl, generous and full.
# Steam is drawn behind the toppings, with broken, organic contours.
for d in ('M641 808C614 784 657 767 640 742C625 723 640 711 647 702',
          'M701 796C675 774 722 756 703 731',
          'M762 810C741 789 783 774 768 751C759 737 768 726 775 718'):
    path(d,'none','#153d42',11,opacity='.18')
    path(d,'none','#fff1cc',6)
# Foot and bowl body.
ellipse(702,955,62,12,'#b17848',INK,4)
path('M553 855C567 926 609 958 702 963C795 958 837 923 852 855Z',CREAM,INK,6)
path('M572 889C590 932 638 948 702 950C765 949 812 931 832 889L825 915C801 951 751 967 701 968C646 963 596 949 577 920Z','#dfcfab','none',0)
# Red bowl stripe and repeating blue markings.
path('M565 884Q704 935 840 884','none',RED,12)
path('M572 903Q702 951 832 903','none',RED,3)
for x in (598,623,648,756,781,806):
    y=910+17*(1-abs(x-702)/110)
    path(f'M{x-6} {y-5}l5 9l8 -4','none',TEAL,3)
circle(702,925,21,CREAM,RED,3)
text(702,935,'8',29,RED,800,0)
# Thick rim and broth.
ellipse(702,854,151,53,CREAM,INK,5)
ellipse(702,855,139,43,'url(#soup)',INK,3)
group(clip_path='url(#broth)')
# Wavy noodle strands woven through the surface.
for k in range(11):
    x=590+k*21
    d=f'M{x} 817C{x-24} 830 {x+26} 835 {x+2} 847S{x-15} 869 {x+7} 877S{x+17} 891 {x-1} 898'
    path(d,'none','#9f612b',8)
    path(d,'none','#f6d178',5)
for x,y in ((593,851),(759,875),(661,875),(793,842),(625,833),(727,826)):
    circle(x,y,3,'#fce7a3','none',0)
end()
# Nori sheets, outlined individually.
path('M764 836L775 773L815 785L809 844Z','#274e44',INK,4)
path('M780 834L803 781L836 803L818 849Z','#34624b',INK,4)
for x in range(782,808,7):
    path(f'M{x} 793l-6 35','none','#6f8b57',2)
path('M801 823l16 -25m-7 36l16 -26','none','#78985c',2)
# Pork chashu, rolled with dark pink spirals.
group(transform='rotate(-17 633 840)')
ellipse(633,840,39,25,'#f6c5a0',INK,3)
ellipse(633,840,28,16,'#d28162','none',0)
path('M611 843C605 823 645 821 652 836C659 852 624 854 620 840C617 831 638 831 639 840C639 846 630 846 629 841','none','#f5c39a',5)
end()
# Egg half with golden, jammy yolk.
group(transform='rotate(22 714 827)')
path('M680 831C677 809 690 785 709 785C730 784 750 810 749 829C746 848 686 850 680 831Z',CREAM,INK,3)
ellipse(715,825,21,17,'#eeab38','#cf7b29',2)
path('M704 819Q709 812 719 815','none','#ffd466',3)
end()
# Fish cake with a real spiral rather than an ambiguous character.
group(transform='rotate(-16 751 861)')
path('M725 859L729 853L728 846L736 845L740 839L747 841L754 837L760 842L768 842L770 849L778 853L775 860L778 867L771 871L769 877L761 877L755 882L747 878L739 879L736 872L729 869Z',CREAM,INK,2.5)
path('M736 860C736 847 764 846 766 860C768 872 744 875 743 861C742 854 756 854 757 861C758 865 751 866 750 862','none','#df7e85',3.5)
end()
# Sliced scallions and sesame finish.
for x,y,rx,ry in ((666,849,10,4),(678,858,8,4),(659,861,7,4),(779,868,9,4),(796,858,7,4),(646,865,7,3),(686,841,7,4)):
    ellipse(x,y,rx,ry,'#7c9c55','#315e47',2,transform=f'rotate(-24 {x} {y})')
for x,y in ((614,867),(623,873),(692,875),(730,882),(788,845),(681,869),(808,863)):
    line(x,y,x+3,y-2,'#fff0b6',2)
# Front cabinet: panels, patterned border, brand, and little hardware.
rect(252,985,897,179,TEAL,4,INK,6)
rect(269,1000,863,143,'none',2,'#97b29c',2)
rect(275,1087,850,48,'url(#waves)',0,'none',0)
line(437,1002,437,1141,'#194e50',3)
line(963,1002,963,1141,'#194e50',3)
# Left cabinet emblem: a cheerful tiny octopus seal.
circle(352,1069,47,CREAM,INK,3)
path('M334 1067V1055C334 1035 371 1035 371 1055V1068M334 1065C319 1059 318 1085 332 1083M340 1067C329 1090 344 1097 350 1082M354 1067C350 1097 370 1096 367 1080M368 1067C384 1060 389 1083 376 1084','none',RED,8)
circle(344,1057,2.7,INK,'none',0)
circle(361,1057,2.7,INK,'none',0)
path('M349 1064q4 4 8 0','none',INK,2)
text(700,1044,'SLOW BROTH.',29,CREAM,800,4)
text(700,1082,'BIG HEART.',35,CREAM,800,4)
line(564,1105,638,1105,'#d6bc7e',2)
star(700,1105,9,'#e4b96e')
line(762,1105,836,1105,'#d6bc7e',2)
# Right cabinet medallion.
text(1049,1042,'ALWAYS',13,CREAM,600,2)
text(1049,1085,'FRESH',25,CREAM,800,2)
text(1049,1114,'SINCE 08',12,'#d6c994',600,2)
for x in (281,1120):
    for y in (1012,1130):
        circle(x,y,3,'#d7bc7d',INK,1.5)
rect(240,1152,920,19,'#c79a62',3,INK,4)
line(254,1160,1147,1160,'#ebc586',2)
# Small freestanding stool adds a human-scale invitation.
path('M164 1118L147 1205M217 1118L234 1205M157 1177H225','none',INK,10)
path('M164 1118L147 1205M217 1118L234 1205','none','#be8658',5)
ellipse(191,1116,57,18,'#b55b43',INK,5)
ellipse(191,1110,57,17,'#e38760',INK,5)
path('M153 1106Q186 1095 222 1105','none','#f2b184',3)
# A lucky cat-sized plant at the far right balances the stool.
path('M1228 1123C1194 1099 1190 1067 1199 1059C1215 1060 1229 1090 1228 1123M1234 1124C1269 1096 1275 1070 1266 1063C1248 1069 1236 1095 1234 1124M1230 1118C1218 1073 1227 1045 1237 1047C1251 1062 1245 1091 1230 1118','#759573',INK,3)
path('M1203 1121H1259L1250 1184Q1231 1195 1211 1184Z','#dd8b61',INK,4)
path('M1207 1135H1256','none','#f0bd85',4)
# Footer caption and final small graphic punctuation.
text(700,1271,'PULL UP A STOOL. STAY FOR THE SOUP.',19,INK,650,3)
text(700,1305,'THE LITTLE RAMEN BOOTH WITH A LOT OF HELPING HANDS',11,'#7c8169',600,2.5)
star(283,1263,8,RED)
star(1118,1263,8,RED)
raw('</g></svg>')
(OUT/'octo-ramen.svg').write_text('\n'.join(s))
print(f'Wrote {OUT / "octo-ramen.svg"}')
