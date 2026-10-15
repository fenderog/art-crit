# Robie the Robotic Banker (Radio Shack, 1980s) - procedural build script.
# Units: body radius = 1.0. Robot faces -Y, +Z up. Robot's right side = -X.
import bpy, bmesh, math
from mathutils import Vector, Matrix

# ---------------------------------------------------------------- parameters
R = 1.0                          # body / head radius
TILT = math.radians(14.0)        # slope of the body's top cut (front higher)
K = math.tan(TILT)
Z0 = 1.38                        # height of the body top plane at y = 0
BODY_BOT = 0.10
FIL = 0.32                       # rounding of the body's bottom edge
TOP_BEV = 0.02
BODY_LIP = 0.035
HEAD_H = 0.66
GAP = 0.02
HINGE = math.radians(2.5)        # head opened slightly -> mouth gap at front
HEAD_YS = 1.0 / math.cos(TILT)   # head is a tilted elliptic cylinder that fits the cut
NSEG = 128
EYE_ANG = math.radians(18.0)
EYE_Z = 0.335
EYE_R = 0.245
SH_Y, SH_Z = -0.20, 0.97         # shoulder axis

FONTS = "/System/Library/Fonts/Supplemental/"
F_ROBIE = FONTS + "Futura.ttc"
F_RS = FONTS + "Arial Bold Italic.ttf"
F_SUB = FONTS + "Arial Bold.ttf"
F_DOLLAR = FONTS + "Georgia Bold.ttf"

MATS = {}


# ---------------------------------------------------------------- utilities
def srgb(r, g, b):
    def c(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (c(r), c(g), c(b))


def make_mat(name, rgb, rough=0.4, metal=0.0, coat=0.0, coat_rough=0.08):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Coat Roughness"].default_value = coat_rough
    m.diffuse_color = (*rgb, 1.0)
    m.roughness = rough
    MATS[name] = m
    return m


def make_materials():
    make_mat("Yellow_Plastic", srgb(240, 212, 66), rough=0.26, coat=0.35)
    make_mat("Black_Gloss", srgb(18, 18, 20), rough=0.36, coat=0.12, coat_rough=0.2)
    make_mat("Black_Satin", srgb(20, 20, 22), rough=0.45)
    make_mat("Black_Top", srgb(22, 22, 24), rough=0.5, coat=0.08, coat_rough=0.3)
    make_mat("Dark_Interior", srgb(6, 6, 6), rough=0.85)
    make_mat("Chrome", srgb(235, 228, 205), rough=0.10, metal=1.0)
    make_mat("Eye_White", srgb(238, 235, 228), rough=0.22, coat=0.4)
    make_mat("Pupil_Black", srgb(10, 10, 10), rough=0.15, coat=0.5)
    make_mat("Teeth_Cream", srgb(238, 228, 196), rough=0.35)
    make_mat("Decal_White", srgb(226, 236, 240), rough=0.35)
    make_mat("Print_Black", srgb(12, 12, 12), rough=0.40)
    make_mat("Ridge_Gray", srgb(52, 52, 56), rough=0.30)


def get_coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def clear_all():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                 bpy.data.cameras, bpy.data.lights, bpy.data.images):
        for b in list(coll):
            if b.users == 0:
                coll.remove(b)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)


def finish(name, bm, mats, coll, smooth=True, sharp=None, parent=None, matrix=None):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(MATS[m])
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if smooth:
        me.shade_smooth()
        if sharp is not None:
            me.set_sharp_from_angle(angle=sharp)
    else:
        me.shade_flat()
    if parent is not None:
        ob.parent = parent
    if matrix is not None:
        ob.matrix_basis = matrix
    return ob


def lathe(bm, prof, seg, matrix=None, cap_start=None, cap_end=None, closed=False):
    """Revolve profile [(rho, h, mat), ...] about local Z. Profile should run
    bottom -> outside -> top so normals face outwards."""
    rings = []
    for p in prof:
        rho, h = p[0], p[1]
        ring = []
        for i in range(seg):
            t = 2 * math.pi * i / seg
            co = Vector((rho * math.cos(t), rho * math.sin(t), h))
            if matrix is not None:
                co = matrix @ co
            ring.append(bm.verts.new(co))
        rings.append(ring)
    n = len(rings)
    for j in range(n if closed else n - 1):
        j2 = (j + 1) % n
        mi = prof[j][2] if len(prof[j]) > 2 else 0
        for i in range(seg):
            f = bm.faces.new((rings[j][i], rings[j][(i + 1) % seg],
                              rings[j2][(i + 1) % seg], rings[j2][i]))
            f.material_index = mi
    if cap_start is not None:
        f = bm.faces.new(list(reversed(rings[0])))
        f.material_index = cap_start
    if cap_end is not None:
        f = bm.faces.new(rings[-1])
        f.material_index = cap_end
    return rings


def mesh_from_object_eval(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    return bpy.data.meshes.new_from_object(ob.evaluated_get(dg))


def text_bm(body, font_path, size, offset=0.0, shear=0.0, spacing=1.0, resolution=10):
    """Flat text in the XY plane (facing +Z), bbox-centred at the origin."""
    cu = bpy.data.curves.new("tmp_txt", 'FONT')
    cu.body = body
    cu.font = bpy.data.fonts.load(font_path, check_existing=True)
    cu.size = size
    cu.offset = offset
    cu.shear = shear
    cu.space_character = spacing
    cu.resolution_u = resolution
    cu.align_x = 'CENTER'
    ob = bpy.data.objects.new("tmp_txt", cu)
    bpy.context.scene.collection.objects.link(ob)
    me = mesh_from_object_eval(ob)
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    for v in bm.verts:
        v.co.x -= cx
        v.co.y -= cy
        v.co.z = 0.0
    return bm, (max(xs) - min(xs), max(ys) - min(ys))


def add_bm(dst, src, matrix=None, mat_index=0):
    """Append bmesh src into dst (optionally transformed)."""
    vmap = {}
    for v in src.verts:
        co = v.co.copy()
        if matrix is not None:
            co = matrix @ co
        vmap[v] = dst.verts.new(co)
    for f in src.faces:
        nf = dst.faces.new([vmap[v] for v in f.verts])
        nf.material_index = mat_index
    src.free()


def tube_curve_mesh(name, pts, radius, coll, mat, res_u=16, bevel_res=6):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = res_u
    cu.bevel_depth = radius
    cu.bevel_resolution = bevel_res
    cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    ob = bpy.data.objects.new(name + "_crv", cu)
    bpy.context.scene.collection.objects.link(ob)
    me = mesh_from_object_eval(ob)
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    me.name = name
    me.materials.clear()
    me.materials.append(MATS[mat])
    obm = bpy.data.objects.new(name, me)
    coll.objects.link(obm)
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(50))
    return obm


def head_matrix():
    S = Matrix.Diagonal((1.0, HEAD_YS, 1.0, 1.0))
    yb = R * HEAD_YS
    hinge = (Matrix.Translation((0, yb, 0)) @ Matrix.Rotation(-HINGE, 4, 'X')
             @ Matrix.Translation((0, -yb, 0)))
    return (Matrix.Translation((0, 0, Z0)) @ Matrix.Rotation(-TILT, 4, 'X')
            @ Matrix.Translation((0, 0, GAP)) @ hinge @ S)


def eye_frame(side):
    a = side * EYE_ANG
    d = Vector((math.sin(a), -math.cos(a), 0.0))
    xt = Vector((math.cos(a), math.sin(a), 0.0))
    up = Vector((0.0, 0.0, 1.0))
    c = d * R + Vector((0, 0, EYE_Z))
    return Matrix(((xt.x, up.x, d.x, c.x),
                   (xt.y, up.y, d.y, c.y),
                   (xt.z, up.z, d.z, c.z),
                   (0, 0, 0, 1)))


def apply_boolean(target, cutter_objs):
    for c in cutter_objs:
        mod = target.modifiers.new("bool", 'BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.solver = 'EXACT'
        mod.material_mode = 'TRANSFER'
        mod.object = c
    me_new = mesh_from_object_eval(target)
    old = target.data
    target.modifiers.clear()
    target.data = me_new
    bpy.data.meshes.remove(old)
    me_new.name = target.name
    for c in cutter_objs:
        me = c.data
        bpy.data.objects.remove(c)
        bpy.data.meshes.remove(me)


# ---------------------------------------------------------------- body
def build_body(coll):
    bm = bmesh.new()
    # angles: uniform + extra columns either side of the front/back seams
    base = [2 * math.pi * i / NSEG for i in range(NSEG)]
    seam_angles = (math.pi / 2, 3 * math.pi / 2)
    extra = []
    for s in seam_angles:
        extra += [s - 0.006, s + 0.006]
    angles = sorted(base + extra)
    seg = len(angles)

    prof = []  # (rho, zfunc(y), mat, seam_depth)
    nf = 14
    for k in range(nf + 1):
        phi = -math.pi / 2 + (math.pi / 2) * k / nf
        z = BODY_BOT + FIL + FIL * math.sin(phi)
        prof.append((R - FIL + FIL * math.cos(phi), (lambda y, z=z: z), 0, 0.006 if k > 0 else 0.0))
    zs = BODY_BOT + FIL
    for t in (0.2, 0.4, 0.6, 0.8, 1.0):
        prof.append((R, (lambda y, t=t: zs + t * (Z0 - K * y - TOP_BEV - zs)), 0, 0.006))
    nb = 5
    for k in range(1, nb + 1):
        psi = (math.pi / 2) * k / nb
        dz = -TOP_BEV + TOP_BEV * math.sin(psi)
        prof.append((R - TOP_BEV + TOP_BEV * math.cos(psi), (lambda y, dz=dz: Z0 - K * y + dz), 0,
                     0.006 * (1 - k / nb)))
    prof.append((R - TOP_BEV - BODY_LIP, (lambda y: Z0 - K * y), 0, 0.0))

    rings = []
    for rho, zf, _, sd in prof:
        ring = []
        for t in angles:
            r = rho
            if any(abs(t - s) < 1e-9 for s in seam_angles):
                r = rho - sd
            x, y = r * math.cos(t), r * math.sin(t)
            ring.append(bm.verts.new((x, y, zf(rho * math.sin(t)))))
        rings.append(ring)
    for j in range(len(rings) - 1):
        for i in range(seg):
            f = bm.faces.new((rings[j][i], rings[j][(i + 1) % seg],
                              rings[j + 1][(i + 1) % seg], rings[j + 1][i]))
            f.material_index = prof[j][2]
    f = bm.faces.new(list(reversed(rings[0])))
    f.material_index = 0
    f = bm.faces.new(rings[-1])
    f.material_index = 1
    return finish("Robie_Body", bm, ["Yellow_Plastic", "Dark_Interior"], coll,
                  sharp=math.radians(30))


def build_base(coll):
    bm = bmesh.new()
    rb = 0.80
    prof = [(rb - 0.13, 0.0), (rb - 0.03, 0.0)]
    for k in range(1, 5):
        a = (math.pi / 2) * k / 4
        prof.append((rb - 0.03 + 0.03 * math.sin(a), 0.03 - 0.03 * math.cos(a)))
    for k in range(0, 5):
        a = (math.pi / 2) * k / 4
        prof.append((rb - 0.03 * (1 - math.cos(a)), 0.11 + 0.03 * math.sin(a)))
    prof.append((rb - 0.13, 0.14))
    lathe(bm, prof, 96, cap_start=0, cap_end=0)
    finish("Robie_Base", bm, ["Black_Gloss"], coll, sharp=math.radians(40))

    # flat base plate that joins the feet
    bm = bmesh.new()
    x0, x1, y0, y1, rc = -1.32, 1.32, -0.42, 0.55, 0.16
    outline = []
    for cx, cy, a0 in ((x1 - rc, y0 + rc, -90), (x1 - rc, y1 - rc, 0),
                       (x0 + rc, y1 - rc, 90), (x0 + rc, y0 + rc, 180)):
        for k in range(9):
            a = math.radians(a0 + 90 * k / 8)
            outline.append((cx + rc * math.cos(a), cy + rc * math.sin(a)))
    bot = [bm.verts.new((x, y, 0.0)) for x, y in outline]
    top = [bm.verts.new((x, y, 0.06)) for x, y in outline]
    n = len(outline)
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(top)
    for i in range(n):
        bm.faces.new((bot[i], bot[(i + 1) % n], top[(i + 1) % n], top[i]))
    finish("Robie_BasePlate", bm, ["Black_Satin"], coll, sharp=math.radians(40))


# ---------------------------------------------------------------- head
def build_head(coll):
    H = HEAD_H
    BB, TB, LIPB = 0.015, 0.05, 0.05
    bm = bmesh.new()
    prof = [(R - BB - LIPB, 0.0, 0), (R - BB, 0.0, 0)]
    for k in range(1, 4):
        psi = (math.pi / 2) * k / 3
        prof.append((R - BB + BB * math.sin(psi), BB - BB * math.cos(psi), 0))
    n_side = 18
    for k in range(1, n_side + 1):
        prof.append((R, BB + (H - TB - BB) * k / n_side, 0))
    for k in range(1, 7):
        psi = (math.pi / 2) * k / 6
        prof.append((R - TB + TB * math.cos(psi), H - TB + TB * math.sin(psi), 0))
    prof.append((R - 0.075, H, 0))
    prof.append((R - 0.075, H - 0.03, 0))
    lathe(bm, prof, NSEG, cap_start=1, cap_end=0)
    head = finish("Robie_Head", bm, ["Yellow_Plastic", "Dark_Interior"], coll, smooth=True)

    # --- cutters (head local space; head still has identity transform)
    cutters = []
    for side in (-1, 1):
        cbm = bmesh.new()
        M = eye_frame(side) @ Matrix.Translation((0, 0, -0.10))
        bmesh.ops.create_cone(cbm, cap_ends=True, cap_tris=False, segments=64,
                              radius1=EYE_R + 0.004, radius2=EYE_R + 0.004, depth=0.80, matrix=M)
        cutters.append(finish("cut_eye", cbm, ["Dark_Interior"], coll, smooth=False))
    # slot on the back of the head
    cbm = bmesh.new()
    bmesh.ops.create_cube(cbm, size=1.0)
    for v in cbm.verts:
        v.co = Vector((v.co.x * 0.27, v.co.y * 0.14, v.co.z * 0.045))
    edges = [e for e in cbm.edges if abs((e.verts[0].co - e.verts[1].co).y) > 0.1]
    bmesh.ops.bevel(cbm, geom=edges, offset=0.021, segments=5, affect='EDGES', clamp_overlap=True)
    bmesh.ops.translate(cbm, verts=cbm.verts, vec=(0, R, 0.50))
    cutters.append(finish("cut_slot", cbm, ["Dark_Interior"], coll, smooth=False))
    apply_boolean(head, cutters)

    # --- custom normals: perfect cylinder shading on the side wall
    me = head.data
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(35))
    cos_ = [v.co for v in me.vertices]
    loop_normals = []
    for poly in me.polygons:
        on_wall = True
        for vi in poly.vertices:
            co = cos_[vi]
            rr = math.hypot(co.x, co.y)
            if abs(rr - R) > 6e-4 or co.z < BB + 1e-4 or co.z > H - TB - 1e-4:
                on_wall = False
                break
        for li in poly.loop_indices:
            if on_wall:
                co = cos_[me.loops[li].vertex_index]
                n = Vector((co.x, co.y, 0)).normalized()
                loop_normals.append(n[:])
            else:
                loop_normals.append((0.0, 0.0, 0.0))
    me.normals_split_custom_set(loop_normals)

    head.matrix_basis = head_matrix()

    # --- black top disc
    bm = bmesh.new()
    rd = R - 0.085
    prof = [(rd - 0.006, H - 0.03), (rd, H - 0.03), (rd, H - 0.012), (rd - 0.003, H - 0.006),
            (rd - 0.008, H - 0.004)]
    lathe(bm, prof, NSEG, cap_start=0, cap_end=0)
    finish("Robie_TopDisc", bm, ["Black_Top"], coll, sharp=math.radians(40), parent=head)

    build_top_graphics(coll, head)
    build_eyes(coll, head)
    build_teeth(coll, head)
    return head


def build_top_graphics(coll, head):
    zt = HEAD_H - 0.004
    rd = R - 0.085
    # five fine ridges across the disc, in front of centre
    bm = bmesh.new()
    for k in range(5):
        y = -0.06 - 0.04 * k
        half = math.sqrt(max(rd * rd - y * y, 0)) - 0.03
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, y, zt + 0.0015)) @
                              Matrix.Diagonal((2 * half, 0.012, 0.003, 1)))
    finish("Robie_TopRidges", bm, ["Ridge_Gray"], coll, smooth=False, parent=head)

    # Radio Shack logo + text (reads from the front: top of letters toward +Y)
    bm = bmesh.new()
    x_left = -0.47
    tb, (w, h) = text_bm("Radio Shack", F_RS, 0.172)
    add_bm(bm, tb, Matrix.Translation((x_left + w / 2, 0.14, zt + 0.0012)))
    tb, (w2, h2) = text_bm("ROBOTIC BANKER", F_SUB, 0.083, spacing=1.25)
    add_bm(bm, tb, Matrix.Translation((x_left + 0.01 + w2 / 2, 0.035, zt + 0.0012)))
    # round logo: ring + small "$"
    lc = Vector((x_left - 0.15, 0.095, zt + 0.0012))
    ring = bmesh.new()
    bmesh.ops.create_circle(ring, cap_ends=False, segments=48, radius=0.12)
    outer = [v for v in ring.verts]
    inner = [ring.verts.new(v.co * (0.097 / 0.12)) for v in outer]
    n = len(outer)
    for i in range(n):
        ring.faces.new((outer[i], outer[(i + 1) % n], inner[(i + 1) % n], inner[i]))
    add_bm(bm, ring, Matrix.Translation(lc))
    tb, _ = text_bm("$", F_DOLLAR, 0.17)
    add_bm(bm, tb, Matrix.Translation(lc))
    finish("Robie_TopLogo", bm, ["Decal_White"], coll, smooth=False, parent=head)


def build_eyes(coll, head):
    for side in (-1, 1):
        M = eye_frame(side)
        # chrome bezel / sleeve (closed solid profile, revolved about eye axis)
        bm = bmesh.new()
        ro, ri = EYE_R, EYE_R - 0.03
        prof = [(ro, -0.30), (ro, -0.03), (ro - 0.002, -0.006), (ro - 0.008, 0.005),
                (ro - 0.017, 0.009), (ri + 0.006, 0.006), (ri + 0.001, -0.004), (ri, -0.02),
                (ri, -0.30)]
        lathe(bm, prof, 64, closed=True)
        for v in bm.verts:
            x = v.co.x
            v.co.z += math.sqrt(max(R * R - x * x, 0)) - R
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        finish("Robie_EyeBezel_" + ("R" if side < 0 else "L"), bm, ["Chrome"], coll,
               sharp=math.radians(45), parent=head)

        # eyeball with pupil looking down
        bm = bmesh.new()
        rb = ri - 0.006
        bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=36, radius=rb)
        for f in bm.faces:
            c = f.calc_center_median()
            ang = math.degrees(c.angle(Vector((0, 0, 1))))
            f.material_index = 1 if ang < 40.0 else 0
        rot = Matrix.Rotation(math.radians(56), 4, 'X')
        bmesh.ops.transform(bm, matrix=M @ Matrix.Translation((0, 0, -rb - 0.022)) @ rot,
                            verts=bm.verts)
        finish("Robie_Eye_" + ("R" if side < 0 else "L"), bm, ["Eye_White", "Pupil_Black"], coll,
               parent=head)



def build_teeth(coll, head):
    bm = bmesh.new()
    for sx in (-1, 1):
        t = bmesh.new()
        bmesh.ops.create_cube(t, size=1.0)
        for v in t.verts:
            v.co = Vector((v.co.x * 0.10, v.co.y * 0.06, v.co.z * 0.092))
        bmesh.ops.bevel(t, geom=list(t.edges), offset=0.016, segments=3, affect='EDGES',
                        clamp_overlap=True)
        add_bm(bm, t, Matrix.Translation((sx * 0.098, -(R - 0.052), -0.036)))
    finish("Robie_Teeth", bm, ["Teeth_Cream"], coll, sharp=math.radians(50), parent=head)


# ---------------------------------------------------------------- text on body
def build_robie_text(coll):
    tb, (w, h) = text_bm("ROBIE", F_ROBIE, 0.285, offset=0.009, spacing=1.06)
    phi_c = -math.radians(29.5)
    zc = 1.33
    off = 0.0025
    for v in tb.verts:
        u, vv, ww = v.co
        phi = phi_c + u / R
        r = R + off + ww
        v.co = Vector((r * math.sin(phi), -r * math.cos(phi), zc + vv))
    return finish("Robie_Label", tb, ["Print_Black"], coll, smooth=False)


# ---------------------------------------------------------------- shoulders
def shoulder_frame(side):
    # local Z -> world +-X, local X -> world Y, local Y -> world +-Z
    if side > 0:
        rot = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    else:
        rot = Matrix(((0, 0, -1, 0), (1, 0, 0, 0), (0, -1, 0, 0), (0, 0, 0, 1)))
    return Matrix.Translation((0, SH_Y, SH_Z)) @ rot


def build_shoulders(coll):
    for side in (-1, 1):
        M = shoulder_frame(side)
        bm = bmesh.new()
        # collar
        prof = [(0.298, 0.90), (0.298, 1.092), (0.292, 1.104), (0.281, 1.110)]
        lathe(bm, prof, 64, matrix=M, cap_start=0, cap_end=0)
        # cap
        prof = [(0.315, 1.112), (0.327, 1.126), (0.332, 1.29)]
        for k in range(1, 7):
            a = (math.pi / 2) * k / 6
            prof.append((0.332 - 0.04 + 0.04 * math.cos(a), 1.29 + 0.04 * math.sin(a)))
        lathe(bm, prof, 64, matrix=M, cap_start=0, cap_end=0)
        finish("Robie_Shoulder_" + ("R" if side < 0 else "L"), bm, ["Yellow_Plastic"], coll,
               sharp=math.radians(35))


# ---------------------------------------------------------------- arms, hook, tray
def c_hand_bm(center, U, V, N, rmaj, a0, a1, ra, rb, n_arc=56, n_sec=28, cap_steps=5):
    bm = bmesh.new()

    def frame(a):
        radial = math.cos(a) * U + math.sin(a) * V
        tang = -math.sin(a) * U + math.cos(a) * V
        return center + rmaj * radial, radial, tang

    def ring_at(p, radial, scale):
        return [bm.verts.new(p + scale * (ra * math.cos(b) * radial + rb * math.sin(b) * N))
                for b in [2 * math.pi * i / n_sec for i in range(n_sec)]]

    rings = []
    # start cap (dome)
    p, radial, tang = frame(a0)
    pole0 = bm.verts.new(p - tang * ra * 0.9)
    for k in range(1, cap_steps):
        t = k / cap_steps
        s = math.sin(t * math.pi / 2)
        rings.append(ring_at(p - tang * ra * 0.9 * math.cos(t * math.pi / 2), radial, s))
    for k in range(n_arc + 1):
        a = a0 + (a1 - a0) * k / n_arc
        p, radial, tang = frame(a)
        rings.append(ring_at(p, radial, 1.0))
    p, radial, tang = frame(a1)
    for k in range(cap_steps - 1, 0, -1):
        t = k / cap_steps
        s = math.sin(t * math.pi / 2)
        rings.append(ring_at(p + tang * ra * 0.9 * math.cos(t * math.pi / 2), radial, s))
    pole1 = bm.verts.new(p + tang * ra * 0.9)
    for j in range(len(rings) - 1):
        for i in range(n_sec):
            bm.faces.new((rings[j][i], rings[j][(i + 1) % n_sec],
                          rings[j + 1][(i + 1) % n_sec], rings[j + 1][i]))
    for i in range(n_sec):
        bm.faces.new((pole0, rings[0][(i + 1) % n_sec], rings[0][i]))
        bm.faces.new((pole1, rings[-1][i], rings[-1][(i + 1) % n_sec]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


TRAY_C = Vector((0.42, -1.40, 0.72))
TRAY_TILT = math.radians(24.0)


def tray_matrix():
    return Matrix.Translation(TRAY_C) @ Matrix.Rotation(TRAY_TILT, 4, 'X')


def build_arms(coll):
    # robot's right arm (-X) ending in a C-shaped hook hand
    hc = Vector((-1.12, -1.05, 0.33))
    N = Vector((-math.sin(math.radians(35)), -math.cos(math.radians(35)), 0.0))
    V = Vector((0, 0, 1.0))
    U = V.cross(N).normalized()
    rmaj = 0.245
    a_join = math.radians(125)
    join = hc + rmaj * (math.cos(a_join) * U + math.sin(a_join) * V)
    pts = [Vector((-1.20, -0.20, 0.95)), Vector((-1.24, -0.42, 0.78)),
           Vector((-1.28, -0.68, 0.66)), Vector((-1.27, -0.90, 0.60)), join]
    tube_curve_mesh("Robie_Arm_R", pts, 0.064, coll, "Black_Satin")
    bm = c_hand_bm(hc, U, V, N, rmaj, math.radians(14), math.radians(284), 0.078, 0.12)
    finish("Robie_HookHand", bm, ["Black_Satin"], coll, sharp=math.radians(60))

    # robot's left arm (+X) holding the coin tray
    Mt = tray_matrix()
    post_top = Mt @ Vector((0.34, 0.15, 0.0))
    post_bot = Mt @ Vector((0.34, 0.15, -0.12))
    pts = [Vector((1.20, -0.20, 0.95)), Vector((1.25, -0.42, 0.76)),
           Vector((1.28, -0.70, 0.62)), Vector((1.16, -1.02, 0.52)),
           Vector((0.92, -1.20, 0.52)), post_bot, post_top]
    tube_curve_mesh("Robie_Arm_L", pts, 0.064, coll, "Black_Satin")


def tray_outline(r0=0.46, tail_ang=math.radians(-34), tail_len=0.20, sigma=math.radians(15), n=200):
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        d = (a - tail_ang + math.pi) % (2 * math.pi) - math.pi
        rho = r0 + tail_len * math.exp(-(d / sigma) ** 2)
        pts.append((rho * math.cos(a), rho * math.sin(a)))
    return pts


def build_tray(coll):
    Mt = tray_matrix()
    T, DISH, RIM = 0.045, 0.014, 0.032
    bm = bmesh.new()
    pts = tray_outline()
    bot = [bm.verts.new((x, y, 0.0)) for x, y in pts]
    top = [bm.verts.new((x, y, T)) for x, y in pts]
    n = len(pts)
    bm.faces.new(list(reversed(bot)))
    ftop = bm.faces.new(top)
    for i in range(n):
        bm.faces.new((bot[i], bot[(i + 1) % n], top[(i + 1) % n], top[i]))
    res = bmesh.ops.inset_region(bm, faces=[ftop], thickness=RIM, depth=0.0, use_even_offset=True)
    bmesh.ops.inset_region(bm, faces=[ftop], thickness=0.006, depth=-DISH * 0.5, use_even_offset=True)
    bmesh.ops.translate(bm, verts=list(ftop.verts), vec=(0, 0, -DISH * 0.5))
    # raised lip around the tail end of the tray
    tail = math.radians(-34)
    for v in bm.verts:
        if abs(v.co.z - T) < 1e-5:
            d = (math.atan2(v.co.y, v.co.x) - tail + math.pi) % (2 * math.pi) - math.pi
            v.co.z += 0.03 * math.exp(-(d / 0.55) ** 2)
    # bevel the outer silhouette edges (top and bottom rims)
    sil = []
    topset, botset = set(top), set(bot)
    for e in bm.edges:
        a, b = e.verts
        if (a in topset and b in topset) or (a in botset and b in botset):
            sil.append(e)
    bmesh.ops.bevel(bm, geom=sil, offset=0.009, segments=2, affect='EDGES', clamp_overlap=True)
    finish("Robie_Tray", bm, ["Black_Gloss"], coll, sharp=math.radians(40), matrix=Mt)

    # white ring + dollar sign decal on the dish floor
    zf = T - DISH + 0.0015
    bm = bmesh.new()
    ring = bmesh.new()
    ro, ri = 0.345, 0.318
    outer = [ring.verts.new((ro * math.cos(a), ro * math.sin(a), 0))
             for a in [2 * math.pi * i / 96 for i in range(96)]]
    inner = [ring.verts.new(v.co * (ri / ro)) for v in outer]
    for i in range(96):
        ring.faces.new((outer[i], outer[(i + 1) % 96], inner[(i + 1) % 96], inner[i]))
    add_bm(bm, ring, Matrix.Translation((0, 0, zf)))
    sb, (sw, sh) = text_bm("S", F_DOLLAR, 0.62, offset=0.004)
    sx = 0.36 / sw
    sy = 0.48 / sh
    add_bm(bm, sb, Matrix.Translation((0, 0, zf)) @ Matrix.Diagonal((sx, sy, 1, 1)))
    for bx in (-0.046, 0.046):
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((bx, 0, zf - 0.0004)) @
                              Matrix.Diagonal((0.028, 0.57, 0.0006, 1)))
    finish("Robie_TrayDecal", bm, ["Decal_White"], coll, smooth=False, matrix=Mt)


# ---------------------------------------------------------------- feet
def _blunt(u, p):
    return max(1.0 - abs(u) ** p, 0.0) ** (1.0 / p)


def foot_profile(u):
    """u in [-1 (front), 1 (back)] -> (half width, height) factors."""
    w = _blunt(u, 3.0) * (1 - 0.18 * u) / 1.0486
    h = _blunt(u, 3.0) * (1 - 0.28 * u) / 1.091
    return w, h


def build_feet(coll):
    L, Y_FRONT, W, HF, SOLE = 1.62, -0.95, 0.31, 0.43, 0.05
    grooves = (0.37, 0.405, 0.44)
    # sample positions along length (0 = front, 1 = back)
    ss = set()
    nn = 64
    for k in range(nn + 1):
        ss.add(round((1 - math.cos(math.pi * k / nn)) / 2, 6))
    for g in grooves:
        for d in (-0.009, -0.004, 0.0, 0.004, 0.009):
            ss.add(round(g + d, 6))
    ss = sorted(ss)
    nphi = 36
    p_exp = 2.3
    for side in (-1, 1):
        xc = side * 1.30
        bm = bmesh.new()
        rings = []
        for s in ss[1:-1]:
            u = 2 * s - 1
            w, h = foot_profile(u)
            dent = 1.0
            for g in grooves:
                if abs(s - g) < 1e-6:
                    dent = 0.975
                elif abs(abs(s - g) - 0.004) < 1e-6:
                    dent = 0.99
            ring = []
            for i in range(nphi + 1):
                ph = math.pi * i / nphi
                c, sn = math.cos(ph), math.sin(ph)
                x = W * w * dent * math.copysign(abs(c) ** (2 / p_exp), c)
                z = HF * h * dent * (abs(sn) ** (2 / p_exp))
                ring.append(bm.verts.new((xc + x, Y_FRONT + s * L, SOLE + z)))
            rings.append(ring)
        pf = bm.verts.new((xc, Y_FRONT, SOLE))
        pb = bm.verts.new((xc, Y_FRONT + L, SOLE))
        for j in range(len(rings) - 1):
            for i in range(nphi):
                bm.faces.new((rings[j][i], rings[j][i + 1], rings[j + 1][i + 1], rings[j + 1][i]))
            # flat bottom strip
            bm.faces.new((rings[j][0], rings[j + 1][0], rings[j + 1][nphi], rings[j][nphi]))
        for i in range(nphi):
            bm.faces.new((pf, rings[0][i + 1], rings[0][i]))
            bm.faces.new((pb, rings[-1][i], rings[-1][i + 1]))
        bm.faces.new((pf, rings[0][0], rings[0][nphi]))
        bm.faces.new((pb, rings[-1][nphi], rings[-1][0]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        finish("Robie_Foot_" + ("R" if side < 0 else "L"), bm, ["Yellow_Plastic"], coll,
               sharp=math.radians(55))

        # black sole following the footprint
        bm = bmesh.new()
        outline = []
        for s in ss[1:-1]:
            u = 2 * s - 1
            w, _ = foot_profile(u)
            outline.append((xc + W * w + 0.012, Y_FRONT - 0.012 + s * (L + 0.024)))
        right = outline
        left = [(2 * xc - x, y) for x, y in reversed(outline)]
        poly = [(xc, Y_FRONT - 0.012)] + right + [(xc, Y_FRONT + L + 0.012)] + left
        b0 = [bm.verts.new((x, y, 0.0)) for x, y in poly]
        b1 = [bm.verts.new((x, y, SOLE + 0.004)) for x, y in poly]
        n = len(poly)
        bm.faces.new(list(reversed(b0)))
        bm.faces.new(b1)
        for i in range(n):
            bm.faces.new((b0[i], b0[(i + 1) % n], b1[(i + 1) % n], b1[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        finish("Robie_Sole_" + ("R" if side < 0 else "L"), bm, ["Black_Satin"], coll,
               sharp=math.radians(40))


# ---------------------------------------------------------------- main
def build_all():
    clear_all()
    make_materials()
    coll = get_coll("Robie")
    build_body(coll)
    build_base(coll)
    build_head(coll)
    build_robie_text(coll)
    build_shoulders(coll)
    build_arms(coll)
    build_tray(coll)
    build_feet(coll)
    return coll


if __name__ == "__main__":
    build_all()
