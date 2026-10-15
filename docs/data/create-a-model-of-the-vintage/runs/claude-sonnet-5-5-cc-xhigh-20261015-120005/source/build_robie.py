"""Robie the Banker - electronic coin bank robot.  Run inside Blender (execute_blender_code)."""
import sys, importlib, bpy, bmesh, math
from math import pi, radians
from mathutils import Vector

DIR = '<vol>/dev/art-crit-runs/2026-10-15-120005-create-a-model-of-the-vintage/claude-sonnet-5-5-cc-xhigh-20261015-120005/work'
if DIR not in sys.path:
    sys.path.insert(0, DIR)
import robie_lib as L
importlib.reload(L)
from robie_lib import (M, mat, empty, box, rounded_slab, lathe, sphere, limb, between, text, finish,
                       dome_profile, seven_seg)

L.reset()

# ------------------------------------------------------------------ materials
mat('Body_Green', '#1b7a63', rough=0.38, coat=0.4)
mat('Head_Cream', '#efe3c4', rough=0.4, coat=0.3)
mat('Visor_Green', '#12513b', rough=0.3, coat=0.5)
mat('Gold', '#eab032', metal=0.9, rough=0.28)
mat('Chrome', '#dfe3e8', metal=1, rough=0.18)
mat('Red', '#c3231c', rough=0.3, coat=0.5)
mat('Feet_Red', '#8f1f19', rough=0.4, coat=0.3)
mat('Black', '#16171b', rough=0.45)
mat('Rubber', '#2a2c30', rough=0.85)
mat('Eye_Lens', '#ffd27a', rough=0.2, emit='#ffc04a', estr=3.0)
mat('Pupil', '#0b0b0d', rough=0.2)
mat('LED_On', '#ff3a2a', rough=0.4, emit='#ff2a18', estr=12.0)
mat('LED_Off', '#260706', rough=0.4)
mat('Glass', '#0a0e0f', rough=0.08)
mat('Coin_Gold', '#ffc83c', metal=0.85, rough=0.25)
mat('Coin_Print', '#8c5b12', metal=0.8, rough=0.35)
mat('Print_Dark', '#1a1a1a', rough=0.6)
mat('Bulb_Red', '#ff4a38', rough=0.2, emit='#ff3020', estr=2.0)

# ------------------------------------------------------------------ hierarchy
root = empty('Robie', (0, 0, 0), size=0.05)
torso = empty('Torso', (0, 0, 0.07), root)
head = empty('Head', (0, 0, 0.24), root)
arm_l = empty('Arm_L', (0.100, 0, 0.185), root)       # +X = robot's left (coin arm)
arm_r = empty('Arm_R', (-0.100, 0, 0.185), root)
leg_l = empty('Leg_L', (0.05, 0, 0.075), root)
leg_r = empty('Leg_R', (-0.05, 0, 0.075), root)

FRONT = (pi / 2, 0, 0)            # lathe +Z -> -Y (faces the viewer)
BACK = (-pi / 2, 0, 0)            # lathe +Z -> +Y

# ------------------------------------------------------------------ torso
box('Torso_Shell', (0.185, 0.13, 0.145), (0, 0, 0.1425), M['Body_Green'], bevel=0.016, seg=4,
    taper=0.92, parent=torso)
rounded_slab('Belt', 0.190, 0.135, 0.014, 0.0185, (0, 0, 0.088), M['Gold'], bevel=0.0035, parent=torso)
text('Belt_Text', 'THE BANKER', 0.0062, (0, -0.0683, 0.088), FRONT, M['Print_Dark'], parent=torso)

# chest panel with the electronic display
box('Chest_Panel', (0.125, 0.008, 0.094), (0, -0.0645, 0.150), M['Head_Cream'], bevel=0.003, parent=torso)
box('Display_Bezel', (0.100, 0.006, 0.038), (0, -0.0685, 0.173), M['Black'], bevel=0.002, parent=torso)
box('Display_Glass', (0.092, 0.0016, 0.030), (0, -0.0715, 0.173), M['Glass'], bevel=0.0005, parent=torso)
lit, ghost = seven_seg('1.25', cz=0.173, y0=-0.0723)
for b_ in (lit, ghost):
    bmesh.ops.translate(b_, vec=(0.0105, 0, 0), verts=b_.verts[:])
finish('Display_Digits', lit, M['LED_On'], parent=torso, smooth=False)
finish('Display_Ghost', ghost, M['LED_Off'], parent=torso, smooth=False)
text('Display_Dollar', '$', 0.026, (-0.0305, -0.0727, 0.1725), FRONT, M['LED_On'], extrude=0.0005, parent=torso)

for i, (x, key) in enumerate(((-0.03, 'Red'), (0.0, 'Gold'), (0.03, 'Chrome'))):
    lathe(f'Button{i}_Bezel', [(0, 0), (0.0125, 0), (0.0125, 0.0018), (0, 0.0018)], M['Black'],
          loc=(x, -0.0685, 0.1385), rot=FRONT, parent=torso, seg=32)
    lathe(f'Button{i}_Cap', dome_profile(0.0095, 0.0045, base=0.0018, n=6), M[key],
          loc=(x, -0.0685, 0.1385), rot=FRONT, parent=torso, seg=32)

box('Nameplate', (0.074, 0.003, 0.017), (0, -0.0695, 0.1125), M['Gold'], bevel=0.001, parent=torso)
text('Nameplate_Text', 'ROBIE', 0.0105, (0, -0.0711, 0.1125), FRONT, M['Print_Dark'], parent=torso)

for sx in (-1, 1):
    for z in (0.109, 0.191):
        lathe('Rivet', dome_profile(0.0025, 0.002, n=5), M['Chrome'], loc=(sx * 0.0555, -0.0685, z),
              rot=FRONT, parent=torso, seg=16)

# neck and bow tie
limb('Neck', (0, 0, 0.208), (0, 0, 0.246), 0.03, M['Chrome'], ribs=4, amp=0.004, parent=torso)
sphere('Tie_Knot', 0.0075, (0, -0.040, 0.226), M['Red'], parent=torso, scale=(1.1, 0.8, 1.15), seg=16, rings=10)
for sx in (-1, 1):
    lathe('Tie_Wing', [(0, 0), (0.0035, 0), (0.0145, 0.025), (0, 0.025)], M['Red'],
          loc=(sx * 0.004, -0.040, 0.226), rot=(0, sx * pi / 2, 0), parent=torso, seg=24, sharp=40)

# back: battery cover + coin door
box('Battery_Cover', (0.09, 0.004, 0.05), (0, 0.0665, 0.168), M['Head_Cream'], bevel=0.0015, parent=torso)
BACKTXT = (pi / 2, 0, pi)
text('Back_Title', 'ROBIE THE BANKER', 0.0064, (0, 0.0686, 0.1785), BACKTXT, M['Print_Dark'], parent=torso)
text('Back_Sub', 'ELECTRONIC COIN BANK', 0.0042, (0, 0.0686, 0.1655), BACKTXT, M['Print_Dark'], parent=torso)
for sx in (-1, 1):
    lathe('Cover_Screw', dome_profile(0.0035, 0.0022, n=5), M['Chrome'], loc=(sx * 0.038, 0.0685, 0.152),
          rot=BACK, parent=torso, seg=16)
lathe('Coin_Door_Plug', [(0, 0), (0.0235, 0), (0.0235, 0.004), (0.02, 0.0058), (0, 0.0058)], M['Rubber'],
      loc=(0, 0.0645, 0.113), rot=BACK, parent=torso, seg=40)
lathe('Coin_Door_Ring', [(0.0228, 0.0), (0.0292, 0.0), (0.0292, 0.0035), (0.0228, 0.0035)], M['Gold'],
      loc=(0, 0.0645, 0.113), rot=BACK, parent=torso, seg=40, loop=True)
box('Coin_Door_Slot', (0.026, 0.002, 0.0035), (0, 0.0705, 0.113), M['Black'], bevel=0.0007, parent=torso)

# side speaker vents on the torso
for sx in (-1, 1):
    for i in range(4):
        box('Side_Vent', (0.004, 0.05, 0.0032), (sx * 0.0895, 0.0, 0.1 + i * 0.0085), M['Black'], bevel=0.0009,
            parent=torso)

# ------------------------------------------------------------------ legs
for sx, leg in ((1, leg_l), (-1, leg_r)):
    n = 'L' if sx > 0 else 'R'
    limb(f'Leg_{n}_Tube', (sx * 0.05, 0, 0.034), (sx * 0.05, 0, 0.078), 0.016, M['Chrome'], ribs=3, amp=0.003,
         parent=leg)
    lathe(f'Ankle_{n}', [(0, 0), (0.0205, 0), (0.0205, 0.0045), (0, 0.0045)], M['Gold'],
          loc=(sx * 0.05, 0, 0.034), parent=leg, seg=32)
    box(f'Foot_{n}', (0.075, 0.115, 0.036), (sx * 0.05, -0.012, 0.018), M['Feet_Red'], bevel=0.013, seg=4,
        parent=leg)

# ------------------------------------------------------------------ head
HZ = 0.305
box('Head_Shell', (0.17, 0.12, 0.125), (0, 0, HZ), M['Head_Cream'], bevel=0.022, seg=4, parent=head)
# banker's eyeshade
box('Visor_Band', (0.176, 0.126, 0.016), (0, 0, 0.355), M['Visor_Green'], bevel=0.006, parent=head)
lathe('Visor_Brim', [(0, -0.002), (0.97, -0.002), (1.0, -0.0012), (1.0, 0.0012), (0.97, 0.002), (0, 0.002)],
      M['Visor_Green'], loc=(0, -0.062, 0.356), rot=(radians(8), 0, 0), parent=head, seg=64, scale=(0.088, 0.052),
      sharp=25)

# eyes
for sx in (-1, 1):
    x, z, y = sx * 0.034, 0.317, -0.06
    lathe('Eye_Socket', [(0, 0), (0.0245, 0), (0.0245, 0.0015), (0, 0.0015)], M['Black'], loc=(x, y, z),
          rot=FRONT, parent=head, seg=40)
    lathe('Eye_Ring', [(0.0170, 0.0012), (0.0238, 0.0012), (0.0238, 0.0035), (0.0210, 0.0052), (0.0175, 0.0052)],
          M['Chrome'], loc=(x, y, z), rot=FRONT, parent=head, seg=40, loop=True)
    lathe('Eye_Lens', dome_profile(0.0168, 0.0095, base=0.0012, n=8), M['Eye_Lens'], loc=(x, y, z),
          rot=FRONT, parent=head, seg=40)
    lathe('Eye_Pupil', dome_profile(0.0062, 0.0012, base=0.0100, n=4), M['Pupil'], loc=(x, y, z),
          rot=FRONT, parent=head, seg=24)

# mouth grille
box('Mouth_Panel', (0.078, 0.004, 0.024), (0, -0.0605, 0.272), M['Black'], bevel=0.0015, parent=head)
for i, dz in enumerate((-0.0075, -0.0025, 0.0025, 0.0075)):
    box(f'Mouth_Bar{i}', (0.066, 0.003, 0.0028), (0, -0.0630, 0.272 + dz), M['Chrome'], bevel=0.0008, parent=head)

# ears
for sx in (-1, 1):
    lathe('Ear', [(0, 0), (0.026, 0), (0.026, 0.010), (0.0225, 0.0125), (0, 0.0125)], M['Chrome'],
          loc=(sx * 0.082, 0, HZ), rot=(0, sx * pi / 2, 0), parent=head, seg=40)
    lathe('Ear_Cap', dome_profile(0.0145, 0.0045, base=0.0125, n=6), M['Gold'],
          loc=(sx * 0.082, 0, HZ), rot=(0, sx * pi / 2, 0), parent=head, seg=32)

# back of the head: vent slots and screws
for i in range(-3, 4):
    box('Head_Vent', (0.0035, 0.002, 0.042), (i * 0.0095, 0.0605, 0.298), M['Black'], bevel=0.0008, parent=head)
for sx in (-1, 1):
    for z in (0.258, 0.338):
        lathe('Head_Screw', dome_profile(0.0035, 0.002, n=5), M['Chrome'], loc=(sx * 0.052, 0.0597, z), rot=BACK,
              parent=head, seg=16)

# coin slot on the crown
TOP = HZ + 0.0625
box('Coin_Slot_Frame', (0.076, 0.024, 0.004), (0, 0.0, TOP + 0.0015), M['Gold'], bevel=0.0012, parent=head)
box('Coin_Slot', (0.062, 0.008, 0.0052), (0, 0.0, TOP + 0.0017), M['Black'], bevel=0.0006, parent=head)

# antenna
lathe('Antenna_Base', [(0, 0), (0.008, 0), (0.0065, 0.004), (0.0025, 0.006), (0, 0.006)], M['Chrome'],
      loc=(-0.05, 0.025, TOP - 0.001), parent=head, seg=24)
lathe('Antenna_Rod', [(0, 0), (0.002, 0), (0.002, 0.042), (0, 0.042)], M['Chrome'],
      loc=(-0.05, 0.025, TOP + 0.003), parent=head, seg=16)
sphere('Antenna_Bulb', 0.0085, (-0.05, 0.025, TOP + 0.050), M['Bulb_Red'], parent=head, seg=24, rings=14)

# ------------------------------------------------------------------ arms
def collar(name, p0, p1, r, length, material, parent):
    d = (Vector(p1) - Vector(p0)).normalized()
    a = Vector(p1) - d * length
    _, q = between(a, p1)
    return lathe(name, [(0, 0), (r, 0), (r, length), (0, length)], material, loc=a, quat=q, parent=parent, seg=32)


# robot's left arm (+X): raised forward, offering a gold coin
S = (0.100, 0, 0.185); E = (0.125, -0.012, 0.150); W = (0.125, -0.068, 0.137)
sphere('Shoulder_L', 0.0205, S, M['Chrome'], parent=arm_l)
limb('UpperArm_L', S, E, 0.0105, M['Chrome'], ribs=3, parent=arm_l)
sphere('Elbow_L', 0.0125, E, M['Gold'], parent=arm_l)
limb('Forearm_L', E, W, 0.0105, M['Chrome'], ribs=4, parent=arm_l)
collar('Wrist_L', E, W, 0.0128, 0.006, M['Gold'], arm_l)
box('Palm_L', (0.028, 0.02, 0.012), (0.125, -0.077, 0.136), M['Red'], bevel=0.005, seg=4, parent=arm_l)
CY, CZ = -0.077, 0.172
for k, s in enumerate((-1, 1)):
    box(f'Finger_L{k}', (0.012, 0.0035, 0.024), (0.125, CY + s * 0.004, 0.154), M['Red'], bevel=0.0016, parent=arm_l)
coin = empty('Coin', (0.125, CY, CZ), arm_l, size=0.03)
lathe('Coin_Disc', [(0, -0.0016), (0.0245, -0.0016), (0.0245, -0.002), (0.028, -0.002), (0.028, 0.002),
                    (0.0245, 0.002), (0.0245, 0.0016), (0, 0.0016)], M['Coin_Gold'],
      loc=(0.125, CY, CZ), rot=FRONT, parent=coin, seg=64, sharp=30)
text('Coin_Dollar_Front', '$', 0.034, (0.125, CY - 0.0018, CZ - 0.0005), FRONT, M['Coin_Print'], extrude=0.0006, parent=coin)
text('Coin_Dollar_Back', '$', 0.034, (0.125, CY + 0.0018, CZ - 0.0005), (pi / 2, 0, pi), M['Coin_Print'], extrude=0.0006,
     parent=coin)

# robot's right arm (-X): relaxed, open claw
S = (-0.100, 0, 0.185); E = (-0.122, -0.004, 0.146); W = (-0.126, -0.020, 0.110)
sphere('Shoulder_R', 0.0205, S, M['Chrome'], parent=arm_r)
limb('UpperArm_R', S, E, 0.0105, M['Chrome'], ribs=3, parent=arm_r)
sphere('Elbow_R', 0.0125, E, M['Gold'], parent=arm_r)
limb('Forearm_R', E, W, 0.0105, M['Chrome'], ribs=3, parent=arm_r)
collar('Wrist_R', E, W, 0.0128, 0.006, M['Gold'], arm_r)
sphere('Palm_R', 0.0135, (-0.126, -0.023, 0.101), M['Red'], parent=arm_r, scale=(1.0, 0.85, 0.8))
for k, s in enumerate((-1, 1)):
    box(f'Finger_R{k}', (0.006, 0.011, 0.026), (-0.126 + s * 0.0072, -0.023, 0.083), M['Red'], bevel=0.0018,
        rot=(0, s * radians(12), 0), parent=arm_r)

result = {'objects': len(L.col.objects)}
