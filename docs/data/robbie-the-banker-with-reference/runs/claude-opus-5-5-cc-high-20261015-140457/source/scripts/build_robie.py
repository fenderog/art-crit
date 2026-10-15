import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler

# ---------------------------------------------------------------- reset
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    for d in list(coll):
        coll.remove(d)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
sc = bpy.context.scene
ROBOT = []


def mat(name, col, rough=0.3, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if coat:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.08
    return m


M = {
    'yellow': mat("Yellow Plastic", (0.93, 0.60, 0.012), 0.3, coat=0.3),
    'black': mat("Black Plastic", (0.010, 0.010, 0.011), 0.3, coat=0.2),
    'white': mat("White Plastic", (0.85, 0.85, 0.82), 0.25),
    'chrome': mat("Chrome", (0.9, 0.9, 0.9), 0.1, metal=1.0),
    'dark': mat("Interior Dark", (0.004, 0.004, 0.004), 0.8),
    'seam': mat("Seam", (0.25, 0.14, 0.005), 0.5),
    'topblack': mat("Top Black", (0.012, 0.012, 0.013), 0.5),
    'grey': mat("Stripe Grey", (0.05, 0.05, 0.055), 0.25),
}


def link(ob, m=None, smooth=True, robot=True):
    sc.collection.objects.link(ob)
    if m is not None:
        ob.data.materials.append(m)
    if smooth and ob.type == 'MESH':
        for p in ob.data.polygons:
            p.use_smooth = True
    if robot:
        ROBOT.append(ob)
    return ob


def lathe(name, prof, m, seg=96):
    """Revolve (r, z) profile around local Z."""
    bm = bmesh.new()
    rings = []
    for r, z in prof:
        if r < 1e-6:
            v = bm.verts.new((0, 0, z))
            rings.append([v] * seg)
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg),
                                        r * math.sin(2 * math.pi * k / seg), z)) for k in range(seg)])
    for A, B in zip(rings, rings[1:]):
        for k in range(seg):
            vs = []
            for v in (A[k], A[(k + 1) % seg], B[(k + 1) % seg], B[k]):
                if v not in vs:
                    vs.append(v)
            if len(vs) >= 3:
                bm.faces.new(vs)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me), m)


def spline(pts, n=6):
    out = []
    for i in range(len(pts) - 1):
        p0 = Vector(pts[max(i - 1, 0)]); p1 = Vector(pts[i])
        p2 = Vector(pts[i + 1]); p3 = Vector(pts[min(i + 2, len(pts) - 1)])
        for s in range(n):
            t = s / n
            v = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                       + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
            out.append(tuple(v))
    out.append(tuple(pts[-1]))
    return out


def box(name, size, loc, m, bevel=0.0, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name, me), m, smooth=False)
    ob.location = loc
    ob.rotation_euler = rot
    if bevel:
        md = ob.modifiers.new("Bevel", 'BEVEL')
        md.width = bevel
        md.segments = 3
        md.limit_method = 'NONE'
        ob.modifiers.new("WN", 'WEIGHTED_NORMAL')
    return ob


def tube(name, pts, radius, m, res=24):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = 6
    cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    sp.resolution_u = res
    ob = bpy.data.objects.new(name, cu)
    return link(ob, m)


def text(name, body, size, m, extrude=0.01, offset=0.0, align='CENTER'):
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.offset = offset
    cu.align_x = align
    cu.align_y = 'CENTER'
    ob = bpy.data.objects.new(name, cu)
    return link(ob, m, smooth=False)


def to_mesh(ob):
    """Convert curve/text object to mesh in place (keeps name, material, parent)."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    new = bpy.data.objects.new(ob.name + "_m", me)
    sc.collection.objects.link(new)
    new.parent = ob.parent
    new.matrix_world = ob.matrix_world.copy()
    nm = ob.name
    if ob in ROBOT:
        ROBOT[ROBOT.index(ob)] = new
    bpy.data.objects.remove(ob, do_unlink=True)
    new.name = nm
    return new


# ---------------------------------------------------------------- body
BODY_PROF = spline([(0, 0.09), (0.72, 0.09), (0.87, 0.13), (0.965, 0.25), (1.0, 0.45),
                    (0.995, 0.75), (0.96, 1.1), (0.935, 1.37), (0.905, 1.42), (0.5, 1.42), (0, 1.42)], 6)


def body_r(z):
    best = None
    for (r0, z0), (r1, z1) in zip(BODY_PROF, BODY_PROF[1:]):
        if r0 > 0.85 and r1 > 0.85 and min(z0, z1) <= z <= max(z0, z1) and z1 != z0:
            t = (z - z0) / (z1 - z0)
            best = r0 + (r1 - r0) * t
    return best or 0.95


lathe("Base", [(0, 0.0), (0.80, 0.0), (0.86, 0.015), (0.875, 0.06), (0.86, 0.11), (0, 0.11)], M['black'])
box("BasePlate", (2.2, 0.6, 0.035), (0, 0.3, 0.0175), M['black'], bevel=0.012)
body = lathe("Body", BODY_PROF, M['yellow'])
lathe("MouthInterior", [(0, 1.36), (0.87, 1.36), (0.87, 1.62), (0, 1.62)], M['dark'], seg=64)

# vertical seams on front and back of the body shell
for nm, sgn in (("SeamFront", -1), ("SeamBack", 1)):
    bm = bmesh.new()
    prev = None
    zs = [0.16 + i * (1.39 - 0.16) / 40 for i in range(41)]
    for z in zs:
        r = body_r(z) + 0.0015
        a = bm.verts.new((-0.006, sgn * r, z))
        b = bm.verts.new((0.006, sgn * r, z))
        if prev:
            bm.faces.new((prev[0], prev[1], b, a))
        prev = (a, b)
    me = bpy.data.meshes.new(nm)
    bm.to_mesh(me)
    bm.free()
    link(bpy.data.objects.new(nm, me), M['seam'])

# ROBIE lettering, wrapped onto the curved front
t = text("RobieLabel", "ROBIE", 0.24, M['black'], extrude=0.006, offset=0.006)
t.rotation_euler = (math.radians(90), 0, 0)
t.location = (0, 0, 1.12)
t = to_mesh(t)
t.data.transform(t.matrix_world)
t.matrix_world = Matrix.Identity(4)
for v in t.data.vertices:
    R = body_r(v.co.z)
    v.co.y = -math.sqrt(max(R * R - v.co.x ** 2, 0.01)) + (v.co.y - 0.006) + 0.002
t.data.update()

# ---------------------------------------------------------------- shoulders
for side in (-1, 1):
    sh = lathe("Shoulder_" + ("L" if side < 0 else "R"),
               spline([(0, 0), (0.18, 0), (0.18, 0.13), (0.215, 0.14), (0.228, 0.17),
                       (0.228, 0.31), (0.212, 0.345), (0.13, 0.36), (0, 0.36)], 3), M['yellow'], seg=64)
    sh.location = (side * 0.84, 0, 1.08)
    sh.rotation_euler = (0, math.radians(90 * side), 0)
    # parting line ring between collar and cap
    ring = lathe("ShoulderSeam_" + ("L" if side < 0 else "R"),
                 [(0.2285, 0.235), (0.2305, 0.24), (0.2285, 0.245)], M['seam'], seg=64)
    ring.location = sh.location
    ring.rotation_euler = sh.rotation_euler

# ---------------------------------------------------------------- feet
FOOT_PROF = spline([(0, 0.0), (0.09, 0.012), (0.145, 0.06), (0.165, 0.14), (0.172, 0.3),
                    (0.185, 0.6), (0.205, 0.95), (0.215, 1.2), (0.205, 1.42), (0.17, 1.54),
                    (0.1, 1.6), (0, 1.615)], 5)
# add two shallow rings near the back
fp = []
for r, z in FOOT_PROF:
    for gz in (0.36, 0.43):
        if abs(z - gz) < 0.018:
            r -= 0.012 * (1 - abs(z - gz) / 0.018)
    fp.append((r, z))
# densify around grooves
dense = []
for (r0, z0), (r1, z1) in zip(fp, fp[1:]):
    n = max(1, int((z1 - z0) / 0.008)) if 0.3 < z0 < 0.5 else 1
    for i in range(n):
        dense.append((r0 + (r1 - r0) * i / n, z0 + (z1 - z0) * i / n))
dense.append(fp[-1])
fp = []
for r, z in dense:
    for gz in (0.36, 0.43):
        if abs(z - gz) < 0.016:
            r = min(r, (0.172 + 0.013 * (z - 0.3) / 0.3) - 0.012 * (1 - abs(z - gz) / 0.016))
    fp.append((r, z))
for side in (-1, 1):
    f = lathe("Foot_" + ("L" if side < 0 else "R"), fp, M['yellow'], seg=64)
    f.scale = (1.12, 1.0, 1.0)
    f.location = (side * 1.06, 0.45, 0.235)
    f.rotation_euler = Euler((math.radians(90), 0, math.radians(14 * side)), 'XYZ')
    f.rotation_euler = (math.radians(90), 0, math.radians(8 * side))

# ---------------------------------------------------------------- head
HEAD_PIVOT = Vector((0, 0.9, 1.45))
head_root = bpy.data.objects.new("HeadPivot", None)
link(head_root)
head_root.location = HEAD_PIVOT
head_root.rotation_euler = (math.radians(-4.5), 0, 0)


def to_head(ob):
    ob.parent = head_root
    ob.matrix_parent_inverse = Matrix.Translation(-HEAD_PIVOT)
    return ob


head = lathe("Head", spline([(0, 1.47), (0.85, 1.47), (0.895, 1.48), (0.915, 1.52), (0.918, 1.6),
                             (0.918, 2.12), (0.91, 2.165), (0.885, 2.19), (0.80, 2.19), (0.79, 2.18), (0, 2.18)], 3),
             M['yellow'], seg=128)
to_head(head)
top = lathe("HeadTop", [(0, 2.17), (0.79, 2.17), (0.795, 2.192), (0.785, 2.2), (0, 2.2)], M['topblack'], seg=128)
to_head(top)

EYE_Z = 1.86
EYE_X = 0.285
EYE_R = 0.16
cutters = []
for side in (-1, 1):
    c = lathe("EyeCut", [(0, 0), (EYE_R, 0), (EYE_R, 0.6), (0, 0.6)], None, seg=64)
    ROBOT.remove(c)
    c.location = (side * EYE_X, -1.2, EYE_Z)
    c.rotation_euler = (math.radians(-90), 0, 0)
    cutters.append(c)
for c in cutters:
    md = head.modifiers.new("EyeHole", 'BOOLEAN')
    md.object = c
    md.solver = 'EXACT'
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(head.evaluated_get(dg))
head.modifiers.clear()
old = head.data
head.data = me
bpy.data.meshes.remove(old)
for c in cutters:
    bpy.data.objects.remove(c, do_unlink=True)

for side, nm in ((-1, "L"), (1, "R")):
    sy = -math.sqrt(0.918 ** 2 - EYE_X ** 2)
    # dark socket cup
    cup = lathe("EyeSocket_" + nm, [(0, 0.25), (EYE_R + 0.002, 0.25), (EYE_R + 0.002, -0.05)], M['dark'], seg=48)
    cup.location = (side * EYE_X, sy, EYE_Z)
    cup.rotation_euler = (math.radians(-90), 0, 0)
    to_head(cup)
    # chrome bezel ring
    bez = lathe("EyeBezel_" + nm, spline([(EYE_R - 0.012, 0.2), (EYE_R - 0.012, 0.015), (EYE_R - 0.006, -0.008),
                                          (EYE_R + 0.008, -0.012), (EYE_R + 0.016, -0.003), (EYE_R + 0.016, 0.06),
                                          (EYE_R, 0.08)], 3), M['chrome'], seg=64)
    bez.location = cup.location
    bez.rotation_euler = cup.rotation_euler
    to_head(bez)
    # eyeball with pupil looking down
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=0.142,
                                         location=(side * EYE_X, sy + 0.075, EYE_Z))
    ball = bpy.context.active_object
    ball.name = "Eyeball_" + nm
    ball.data.materials.append(M['white'])
    ball.data.materials.append(M['black'])
    for p in ball.data.polygons:
        p.use_smooth = True
        c = p.center
        d = Vector((0, -0.55, -0.83)).normalized()
        if c.normalized().dot(d) > 0.72:
            p.material_index = 1
    ROBOT.append(ball)
    to_head(ball)

# upper teeth hanging under the head lip
for i, x in enumerate((-0.14, -0.05)):
    tooth = box("Tooth_%d" % i, (0.075, 0.05, 0.11), (x, -0.85, 1.44), M['white'], bevel=0.012)
    to_head(tooth)

# coin slot at the back of the head
slot = box("CoinSlot", (0.13, 0.03, 0.028), (0, 0.912, 1.58), M['dark'], bevel=0.01)
to_head(slot)

# top deck graphics
rs = text("TopLogo", "Radio Shack", 0.115, M['white'], extrude=0.002)
rs.location = (0.06, 0.40, 2.2)
rs.data.font = bpy.data.fonts[0]
rs.data.shear = 0.25
rs.data.offset = 0.003
to_head(to_mesh(rs))
rb = text("TopSub", "ROBOTIC BANKER", 0.05, M['white'], extrude=0.002)
rb.location = (0.04, 0.29, 2.2)
to_head(to_mesh(rb))
lg = lathe("TopEmblem", [(0.055, 2.2), (0.072, 2.2), (0.072, 2.204), (0.055, 2.204)], M['white'], seg=48)
lg.location = (-0.33, 0.37, 0)
to_head(lg)
ld = text("TopEmblemMark", "$", 0.085, M['white'], extrude=0.002)
ld.location = (-0.33, 0.37, 2.2)
to_head(to_mesh(ld))
for i in range(6):
    st = box("TopStripe_%d" % i, (0.62, 0.006, 0.004), (0.05, 0.11 + i * 0.022, 2.2), M['grey'])
    to_head(st)

# ---------------------------------------------------------------- arms
tube("Arm_L", [(-1.08, -0.04, 1.0), (-1.17, -0.24, 0.84), (-1.15, -0.48, 0.68),
               (-1.07, -0.74, 0.56), (-0.98, -0.92, 0.47), (-0.86, -0.97, 0.48),
               (-0.80, -0.93, 0.58), (-0.85, -0.87, 0.64)], 0.058, M['black'])
tube("Arm_R", [(1.08, -0.04, 1.0), (1.17, -0.24, 0.84), (1.15, -0.48, 0.68),
               (1.07, -0.74, 0.56), (0.98, -0.92, 0.50), (0.90, -1.02, 0.52)], 0.058, M['black'])

# coin tray held in the right hand
tray_root = bpy.data.objects.new("TrayPivot", None)
link(tray_root)
tray_root.location = (0.48, -1.2, 0.56)
tray_root.scale = (1.12, 1.12, 1.12)
tray_root.rotation_euler = Euler((math.radians(42), 0, math.radians(-25)), 'XYZ')
tray_parts = []
tray_parts.append(lathe("TrayDish", spline([(0, -0.012), (0.29, -0.012), (0.31, 0.0), (0.315, 0.025),
                                            (0.30, 0.04), (0.285, 0.03), (0.27, 0.012), (0, 0.012)], 3),
                        M['black'], seg=96))
tab = box("TrayTab", (0.2, 0.17, 0.024), (0.3, -0.03, 0.0), M['black'], bevel=0.02, rot=(0, 0, math.radians(-20)))
tray_parts.append(tab)
tray_parts.append(lathe("TrayDisc", [(0, 0.012), (0.205, 0.012), (0.205, 0.017), (0, 0.017)], M['white'], seg=96))
dl = text("TrayDollar", "$", 0.33, M['black'], extrude=0.003, offset=0.008)
dl.location = (0, 0.01, 0.018)
tray_parts.append(to_mesh(dl))
for p in tray_parts:
    p.parent = tray_root

# convert arm curves to meshes
for nm in ("Arm_L", "Arm_R"):
    to_mesh(bpy.data.objects[nm])

# collect robot into a collection
col = bpy.data.collections.new("Robie")
sc.collection.children.link(col)
for ob in ROBOT:
    if ob.name in bpy.data.objects:
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        col.objects.link(ob)
