import sys, math, random, importlib
sys.path.insert(0, "<vol>/dev/art-crit-runs/2026-10-15-130449-robbie-the-banker-with-reference/claude-sonnet-5-5-cc-xhigh-20261015-130449/work/scripts")
import robbie_lib as L
importlib.reload(L)
import bpy
from mathutils import Vector

random.seed(7)
L.clear_scene()
L.new_collection("Robbie")

# ------------------------------------------------------------------ materials
green = L.make_mat("Green Enamel", (0.01, 0.105, 0.042), 0.15, 0.28, {"Coat Weight": 0.5, "Coat Roughness": 0.1})
black = L.make_mat("Black Enamel", (0.012, 0.012, 0.014), 0.0, 0.22, {"Coat Weight": 0.5})
chrome = L.make_mat("Chrome", (0.88, 0.89, 0.92), 1.0, 0.16)
steel = L.make_mat("Brushed Steel", (0.62, 0.64, 0.68), 1.0, 0.34)
satin = L.make_mat("Satin Aluminium", (0.80, 0.81, 0.84), 1.0, 0.30)
gun = L.make_mat("Gunmetal", (0.18, 0.19, 0.22), 0.9, 0.38)
gold = L.make_mat("Gold", (1.0, 0.62, 0.15), 1.0, 0.2)
cream = L.make_mat("Cream Enamel", (0.80, 0.72, 0.55), 0.0, 0.42)
red = L.make_mat("Red Enamel", (0.36, 0.008, 0.014), 0.0, 0.25, {"Coat Weight": 0.6})
burlap = L.make_mat("Burlap", (0.40, 0.26, 0.12), 0.0, 0.95)
white = L.make_mat("Eye White", (0.92, 0.92, 0.88), 0.0, 0.08, {"Coat Weight": 0.6})
pupil = L.make_mat("Pupil", (0.01, 0.01, 0.012), 0.0, 0.05)
glass = L.make_mat("Monocle Glass", (0.85, 0.95, 1.0), 0.0, 0.02, alpha=0.18)
glass.surface_render_method = 'BLENDED'
darkgreen = L.make_mat("Deep Green", (0.01, 0.07, 0.03), 0.0, 0.3)

root = L.group("Robbie_the_Banker")
L.use(root)

# ------------------------------------------------------------------ base
g = L.group("Base", root); L.use(g)
ZB = 3.2
L.box("Base Plate Black", (25.4, 14.4, 0.6), (0, 0, 0.3), black, bevel=0.2)
L.box("Base Block Green", (24, 13, 2.4), (0, 0, 1.8), green, bevel=0.5, seg=4)
L.box("Base Gold Inlay", (21.6, 11.0, 0.18), (0, 0, 3.0), gold, bevel=0.05, seg=1)
L.box("Base Top Panel", (20.8, 10.2, 0.25), (0, 0, 3.075), darkgreen, bevel=0.06, seg=1)
L.text_mesh("Base Name Plate", "ROBBIE", 1.5, (0, -6.5 - 0.02, 1.75), gold, extrude=0.06)
for sx in (-1, 1):
    L.cyl("Base Rivet", 0.35, 0.3, (sx * 11.0, -5.6, 1.9), gold, rot=(90, 0, 0), seg=16, bevel=0.06)
    L.cyl("Base Rivet", 0.35, 0.3, (sx * 11.0, 5.6, 1.9), gold, rot=(90, 0, 0), seg=16, bevel=0.06)
# bottom coin-trap plug
L.cyl("Coin Trap Plug", 2.4, 0.4, (0, 0, -0.1), red, seg=40, bevel=0.1)
L.torus("Coin Trap Ring", 2.5, 0.18, (0, 0, -0.05), gold, seg=40, rseg=8)

# ------------------------------------------------------------------ legs
g = L.group("Legs", root); L.use(g)
for sx, nm in ((-1, "L"), (1, "R")):
    x = sx * 3.3
    L.box(f"Shoe {nm}", (4.8, 7.4, 2.1), (x, -1.0, ZB + 1.05), black, bevel=0.9, seg=5)
    L.box(f"Shoe Toe Cap {nm}", (4.5, 2.6, 0.5), (x, -3.6, ZB + 1.9), gun, bevel=0.2)
    L.cyl(f"Ankle Cuff {nm}", 1.45, 0.9, (x, 0, ZB + 2.3), gun, bevel=0.15)
    L.cyl(f"Leg {nm}", 1.05, 4.6, (x, 0, ZB + 4.8), chrome, seg=32)
    for i in range(5):
        L.torus(f"Leg Pleat {nm}", 1.05, 0.3, (x, 0, ZB + 3.3 + i * 0.85), steel, seg=32, rseg=10)
    L.cyl(f"Knee Sleeve {nm}", 1.3, 0.7, (x, 0, ZB + 7.3), gun, bevel=0.12)

# ------------------------------------------------------------------ torso
g = L.group("Torso", root); L.use(g)
L.box("Hips", (9.8, 6.2, 1.9), (0, 0, 9.5), gun, bevel=0.5, seg=3)
TZ0, TZ1 = 10.2, 20.2
TC = (TZ0 + TZ1) / 2
L.box("Torso Jacket", (11.2, 7.4, TZ1 - TZ0), (0, 0, TC), green, bevel=1.3, seg=6)
L.box("Belt", (11.6, 7.8, 1.1), (0, 0, 10.95), black, bevel=0.25)
L.box("Belt Buckle", (2.8, 0.35, 1.6), (0, -3.95, 10.95), gold, bevel=0.15)
L.box("Belt Buckle Inner", (1.7, 0.36, 0.8), (0, -3.98, 10.95), black, bevel=0.05, seg=1)
L.box("Shirt Front", (4.6, 0.45, 7.8), (0, -3.85, 15.55), cream, bevel=0.12)
for sx in (-1, 1):
    L.box("Lapel", (1.6, 0.55, 7.8), (sx * 3.45, -3.95, 15.6), black, bevel=0.15, rot=(0, sx * 11, 0))
# medallion
L.cyl("Dollar Medallion", 1.9, 0.35, (0, -4.15, 17.3), gold, rot=(90, 0, 0), seg=48, bevel=0.1)
L.cyl("Dollar Medallion Face", 1.45, 0.2, (0, -4.32, 17.3), darkgreen, rot=(90, 0, 0), seg=48)
L.text_mesh("Dollar Sign", "$", 2.3, (0, -4.46, 17.3), gold, extrude=0.06)
for i, z in enumerate((14.7, 13.5, 12.3)):
    L.sph("Shirt Button", 0.42, (0, -4.05, z), gold, scale=(1, 0.55, 1), seg=20, rings=10)
# shoulder rivets
for sx in (-1, 1):
    for z in (11.8, 18.8):
        L.sph("Jacket Rivet", 0.38, (sx * 5.2, -3.85, z), gold, scale=(1, 0.6, 1), seg=16, rings=8)
# neck + bow tie
L.cyl("Neck", 1.7, 2.6, (0, 0, 20.9), gun, bevel=0.1)
L.torus("Neck Ring", 1.75, 0.3, (0, 0, 20.1), steel, seg=32, rseg=10)
for sx in (-1, 1):
    L.cyl("Bow Tie Wing", 1.55, 2.8, (sx * 1.9, -4.35, 19.3), red, r2=0.35,
          rot=(0, -sx * 90, 0), seg=32, scale=(1, 1, 0.55))
L.sph("Bow Tie Knot", 0.75, (0, -4.4, 19.3), red, scale=(1, 0.8, 1.1), seg=24, rings=12)

# ------------------------------------------------------------------ head
g = L.group("Head", root); L.use(g)
HZ0, HZ1 = 21.4, 31.8
HC = (HZ0 + HZ1) / 2
HW, HD = 12.2, 9.2
L.box("Head", (HW, HD, HZ1 - HZ0), (0, 0, HC), steel, bevel=1.6, seg=6)
# face plate (slightly inset rim)
L.box("Face Plate", (10.8, 0.25, 9.2), (0, -HD / 2 - 0.02, 26.5), satin, bevel=0.45, seg=3)
FY = -HD / 2 - 0.15           # front of face plate
for sx in (-1, 1):
    ex = sx * 2.75
    ez = 28.2
    L.sph("Eye White", 1.7, (ex, FY - 0.15, ez), white, scale=(1, 0.5, 1), seg=32, rings=16)
    L.sph("Pupil", 0.95, (ex + 0.3, FY - 0.78, ez - 0.05), pupil, scale=(1, 0.4, 1), seg=24, rings=12)
    L.sph("Eye Highlight", 0.27, (ex - 0.05, FY - 1.12, ez + 0.4), white, scale=(1, 0.4, 1), seg=12, rings=6)
    L.tube("Eyebrow", [(ex - sx * 1.9, FY - 0.3, ez + 2.35 - sx * 0.0), (ex - sx * 0.6, FY - 0.35, ez + 2.75),
                       (ex + sx * 0.9, FY - 0.35, ez + 2.6), (ex + sx * 2.0, FY - 0.3, ez + 2.1)],
           [0.25, 0.42, 0.38, 0.2], black, sides=10, n=6)
    L.torus("Eye Rim", 1.8, 0.24, (ex, FY - 0.1, ez), gold, rot=(90, 0, 0), seg=40, rseg=10)
# monocle on the viewer's-right eye
mx, mz = 2.75, 28.2
L.torus("Monocle Ring", 2.25, 0.22, (mx, FY - 0.45, mz), gold, rot=(90, 0, 0), seg=48, rseg=10)
L.cyl("Monocle Glass", 2.2, 0.06, (mx, FY - 0.55, mz), glass, rot=(90, 0, 0), seg=48)
L.sph("Monocle Loop", 0.3, (mx + 1.65, FY - 0.45, mz - 1.65), gold, seg=12, rings=8)
chain = [(mx + 1.7, FY - 0.55, mz - 1.7), (5.2, FY - 0.55, 25.2), (5.9, -4.95, 23.0),
         (5.7, -4.9, 21.2), (4.9, -4.8, 19.9), (4.0, -4.7, 19.0)]
L.tube("Monocle Chain", chain, [0.13] * len(chain), gold, sides=8, n=6)
L.sph("Chain Pin", 0.5, (3.9, -4.65, 19.0), gold, scale=(1, 0.6, 1), seg=16, rings=8)
# nose
L.sph("Nose", 0.95, (0, FY - 0.55, 26.0), red, scale=(1, 0.85, 1), seg=24, rings=12)
# mustache
mxs = [-4.9, -4.55, -3.8, -2.6, -1.2, 0.0, 1.2, 2.6, 3.8, 4.55, 4.9]
mzs = [26.0, 25.3, 24.75, 24.4, 24.25, 24.6, 24.25, 24.4, 24.75, 25.3, 26.0]
mr = [0.1, 0.24, 0.38, 0.52, 0.62, 0.48, 0.62, 0.52, 0.38, 0.24, 0.1]
L.tube("Mustache", [(x, FY - 0.45, z) for x, z in zip(mxs, mzs)], mr, black, sides=12, n=8)
# mouth grille
L.box("Mouth Recess", (4.6, 0.3, 1.3), (0, FY - 0.0, 22.8), black, bevel=0.3)
for i in range(3):
    L.box("Mouth Bar", (4.2, 0.3, 0.16), (0, FY - 0.2, 22.45 + i * 0.35), chrome, bevel=0.05, seg=1)
# ears
for sx in (-1, 1):
    L.cyl("Ear", 1.9, 1.0, (sx * (HW / 2 + 0.4), 0, HC), gun, rot=(0, 90, 0), bevel=0.25)
    L.cyl("Ear Knob", 0.8, 0.5, (sx * (HW / 2 + 1.1), 0, HC), gold, rot=(0, 90, 0), seg=24, bevel=0.1)
# head rivets
for sx in (-1, 1):
    for z in (22.4, 30.8):
        L.sph("Head Rivet", 0.35, (sx * 5.2, FY + 0.05, z), gold, scale=(1, 0.6, 1), seg=16, rings=8)

# ------------------------------------------------------------------ back details
g = L.group("Back Details", root); L.use(g)
BY = 3.7
L.box("Coin Door Frame", (5.8, 0.35, 6.8), (0, BY + 0.1, 15.4), gold, bevel=0.2)
L.box("Coin Door", (4.9, 0.4, 5.9), (0, BY + 0.14, 15.4), darkgreen, bevel=0.2)
L.cyl("Keyhole Escutcheon", 0.75, 0.3, (0, BY + 0.4, 15.4), gold, rot=(90, 0, 0), seg=24, bevel=0.06)
L.cyl("Keyhole", 0.28, 0.32, (0, BY + 0.45, 15.5), black, rot=(90, 0, 0), seg=16)
L.box("Keyhole Slot", (0.18, 0.32, 0.8), (0, BY + 0.45, 15.0), black, bevel=0.0)
for sx in (-1, 1):
    for z in (12.9, 17.9):
        L.sph("Door Screw", 0.32, (sx * 2.2, BY + 0.36, z), gold, scale=(1, 0.5, 1), seg=14, rings=8)
L.box("Back Vent Panel", (7.2, 0.3, 5.2), (0, HD / 2 + 0.08, 26.4), gun, bevel=0.3)
for i in range(6):
    L.box("Vent Slot", (5.4, 0.32, 0.2), (0, HD / 2 + 0.2, 24.7 + i * 0.68), black, bevel=0.04, seg=1)
for sx in (-1, 1):
    for dz in (-2.2, 2.2):
        L.sph("Panel Screw", 0.3, (sx * 3.2, HD / 2 + 0.24, 26.4 + dz), chrome, scale=(1, 0.5, 1), seg=14, rings=8)
L.cyl("Hip Back Bumper", 1.1, 0.4, (0, 3.2, 9.5), gold, rot=(90, 0, 0), seg=24, bevel=0.08)

# ------------------------------------------------------------------ top hat
HATZ = HZ1
hat = L.group("Top Hat", root, loc=(0, 0, HATZ))
L.use(hat)
L.cyl("Hat Brim", 7.2, 0.65, (0, 0, HATZ + 0.325), black, bevel=0.22, seg=64)
L.cyl("Hat Brim Underside Trim", 5.3, 0.2, (0, 0, HATZ + 0.1), gun, seg=48)
crown = L.cyl("Hat Crown", 4.55, 8.0, (0, 0, HATZ + 4.5), black, r2=4.95, bevel=0.35, bseg=3, seg=64)
L.cyl("Hat Band", 4.68, 1.7, (0, 0, HATZ + 1.55), red, r2=4.72, seg=64, bevel=0.1)
L.box("Hat Buckle", (2.0, 0.3, 1.9), (0, -4.78, HATZ + 1.55), gold, bevel=0.1)
L.box("Hat Buckle Inner", (1.1, 0.32, 1.0), (0, -4.8, HATZ + 1.55), red, bevel=0.04, seg=1)
bezel = L.box("Coin Slot Bezel", (6.6, 2.4, 0.3), (0, 0, HATZ + 8.55), gold, bevel=0.15)
cutter = L.box("SlotCutter", (4.6, 0.6, 2.6), (0, 0, HATZ + 8.5), black, bevel=0.0)
L.boolean_cut(crown, cutter)
L.boolean_cut(bezel, cutter)
hat.rotation_euler = (math.radians(2.5), math.radians(-5), math.radians(3))

# ------------------------------------------------------------------ arms
def arm(side, pts, name):
    S, E, H = [Vector(p) for p in pts]
    L.sph(f"Shoulder {name}", 1.9, S, chrome, seg=32, rings=16)
    L.limb(f"Upper Arm {name}", S, E, 1.0, chrome, seg=32)
    for t in (0.3, 0.45, 0.6, 0.75):
        p = S.lerp(E, t)
        d = (E - S).normalized()
        o = L.torus(f"Arm Pleat {name}", 1.0, 0.27, tuple(p), steel, seg=32, rseg=10)
        o.rotation_euler = Vector((0, 0, 1)).rotation_difference(d).to_euler()
    L.sph(f"Elbow {name}", 1.45, E, gun, seg=32, rings=16)
    L.limb(f"Forearm {name}", E, H, 0.95, chrome, seg=32)
    for t in (0.3, 0.45, 0.6):
        p = E.lerp(H, t)
        d = (H - E).normalized()
        o = L.torus(f"Forearm Pleat {name}", 0.95, 0.26, tuple(p), steel, seg=32, rseg=10)
        o.rotation_euler = Vector((0, 0, 1)).rotation_difference(d).to_euler()
    L.cyl(f"Cuff {name}", 1.35, 1.0, tuple(E.lerp(H, 0.92)), cream, bevel=0.15).rotation_euler = \
        Vector((0, 0, 1)).rotation_difference((H - E).normalized()).to_euler()

# --- viewer's-right arm: raised, holding a big coin
g = L.group("Arm Coin", root); L.use(g)
S1, E1, H1 = (7.0, 0, 18.6), (10.9, -1.0, 14.4), (10.3, -4.4, 21.0)
arm(1, (S1, E1, H1), "Coin")
L.sph("Hand Coin", 1.5, (10.2, -4.6, 21.6), gun, scale=(1.0, 0.85, 1.0), seg=24, rings=12)
CX, CY, CZ = 10.2, -5.7, 24.0
L.limb("Finger Back", (9.6, -4.7, 21.9), (9.7, -5.2, CZ - 1.2), 0.42, chrome, seg=16)
L.limb("Finger Front", (10.8, -4.9, 21.9), (10.7, -6.3, CZ - 1.1), 0.42, chrome, seg=16)
c = L.coin("Held Coin", (CX, CY, CZ), 2.0, gold, rot=(90, 0, 0), h=0.4)
L.text_mesh("Held Coin Dollar", "$", 1.7, (CX, CY - 0.22, CZ), gold, extrude=0.04)

# --- viewer's-left arm: holding out a tray with coins
g = L.group("Arm Tray", root); L.use(g)
S2, E2, H2 = (-7.0, 0, 18.6), (-10.7, -1.2, 14.2), (-9.6, -7.6, 13.4)
arm(-1, (S2, E2, H2), "Tray")
L.sph("Hand Tray", 1.5, (-9.4, -8.3, 13.6), gun, scale=(1.1, 1.1, 0.7), seg=24, rings=12)
TX, TY, TZ = -9.3, -9.8, 14.15
L.cyl("Tray", 3.4, 0.3, (TX, TY, TZ), gold, r2=3.7, bevel=0.08, seg=56)
L.torus("Tray Rim", 3.6, 0.22, (TX, TY, TZ + 0.12), gold, seg=56, rseg=8)
L.cyl("Tray Stem", 0.8, 0.9, (TX, TY + 0.2, TZ - 0.4), gun, seg=20)
for i in range(3):
    L.coin("Tray Coin", (TX + random.uniform(-0.1, 0.1), TY + random.uniform(-0.1, 0.1), TZ + 0.45 + i * 0.36),
           1.6, gold, rot=(0, 0, random.uniform(0, 360)))
L.coin("Tray Coin Tilted", (TX + 1.0, TY + 1.9, TZ + 0.55), 1.6, gold, rot=(32, 8, 20))

# ------------------------------------------------------------------ props: sack and coin stacks
g = L.group("Props", root); L.use(g)
SX, SY = -8.3, 2.6
L.sph("Money Sack", 3.3, (SX, SY, ZB + 3.2), burlap, scale=(1, 0.95, 1.05), seg=40, rings=20)
L.cyl("Money Sack Neck", 2.0, 2.2, (SX, SY, ZB + 6.0), burlap, r2=1.1, seg=32)
L.cyl("Money Sack Ruffle", 1.1, 1.6, (SX, SY, ZB + 7.6), burlap, r2=2.3, seg=32)
L.torus("Money Sack Tie", 1.25, 0.28, (SX, SY, ZB + 6.7), red, seg=32, rseg=8)
L.text_mesh("Sack Dollar", "$", 3.6, (SX, SY - 3.2, ZB + 3.4), darkgreen, extrude=0.06)
# coin stacks
for (x, y, n, r) in ((7.6, 1.4, 8, 1.6), (10.0, -0.9, 5, 1.6), (9.7, 3.7, 3, 1.6), (4.7, 5.0, 2, 1.6)):
    for i in range(n):
        L.coin("Stack Coin", (x + random.uniform(-0.1, 0.1), y + random.uniform(-0.1, 0.1), ZB + 0.17 + i * 0.35),
               r, gold, rot=(0, 0, random.uniform(0, 360)))
L.coin("Leaning Coin", (7.6 + 1.0, 1.4 - 2.2, ZB + 1.5), 1.6, gold, rot=(72, 0, 12))
L.coin("Floor Coin A", (8.6, -4.6, ZB + 0.17), 1.6, gold, rot=(0, 0, 30))
L.coin("Floor Coin B", (6.2, -3.2, ZB + 0.17), 1.6, gold, rot=(0, 0, 110))

# ------------------------------------------------------------------ bake modifiers, drop cutter
bpy.context.view_layer.update()
for ob in list(bpy.data.objects):
    if ob.type == 'MESH' and ob.name != "SlotCutter":
        L.bake_modifiers(ob)
bpy.data.objects.remove(bpy.data.objects["SlotCutter"], do_unlink=True)

# stats
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
result = {"objects": len(meshes), "tris": sum(len(o.data.polygons) for o in meshes)}
