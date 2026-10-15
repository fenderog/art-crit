# Build "Robie" - the Radio Shack Robotic Banker coin bank (1980s).
# Modelled in units of the body diameter (D = 1.0); the whole toy is scaled
# down to real-world size by the root empty at the end.
# Robot faces -Y (front), +X is the robot's left side, Z is up.
import bpy, bmesh, math
from mathutils import Vector, Matrix

FONT_DIR = "/System/Library/Fonts/Supplemental/"

# --------------------------------------------------------------------------
# dimensions
R = 0.5                 # body / head radius
BASE_H = 0.055          # black base puck under the body
BODY_FRONT = 0.78       # body height at the front
BODY_BACK = 0.50        # body height at the back
SLOPE = (BODY_FRONT - BODY_BACK) / (2 * R)
TILT = math.atan(SLOPE)                     # head / seam tilt (front up)
BODY_TOPC = BASE_H + (BODY_FRONT + BODY_BACK) / 2   # seam height on the axis
HEAD_H = 0.385
MOUTH_OPEN = math.radians(2.7)              # head hinged open at the back
SHOULDER_Z = 0.47
SHOULDER_R = 0.168
FOOT_X = 0.71

# --------------------------------------------------------------------------
# scene helpers
def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c

def clear_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for blocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                   bpy.data.cameras, bpy.data.lights, bpy.data.images,
                   bpy.data.worlds):
        for b in list(blocks):
            if b.users == 0:
                blocks.remove(b)

ROBOT = None

def link(ob, c=None):
    (c or ROBOT).objects.link(ob)
    return ob

def mesh_object(name, verts, faces, mats=(), face_mats=None, smooth=True,
                sharp_angle=35.0, parent=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.validate()
    for m in mats:
        me.materials.append(m)
    if face_mats:
        me.polygons.foreach_set("material_index", face_mats)
    ob = link(bpy.data.objects.new(name, me))
    if smooth:
        smooth_by_angle(ob, sharp_angle)
    if parent:
        ob.parent = parent
    return ob

def smooth_by_angle(ob, angle=35.0):
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    lim = math.radians(angle)
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        if not e.is_manifold:
            continue
        if e.calc_face_angle(0.0) > lim:
            e.smooth = False
        else:
            e.smooth = True
    bm.to_mesh(me)
    bm.free()

def bake_modifiers(ob):
    """Apply all modifiers (via evaluated copy) without operator context."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    if old.users == 0:
        bpy.data.meshes.remove(old)
    return ob

def curve_to_mesh(ob, keep_name=True):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    name = ob.name
    mats = list(ob.data.materials)
    parent, pinv = ob.parent, ob.matrix_parent_inverse.copy()
    loc, rot, scl = ob.location.copy(), ob.rotation_euler.copy(), ob.scale.copy()
    cdata = ob.data
    for c in ob.users_collection:
        c.objects.unlink(ob)
    bpy.data.objects.remove(ob)
    if cdata.users == 0:
        bpy.data.curves.remove(cdata)
    new = link(bpy.data.objects.new(name, me))
    if not me.materials:
        for m in mats:
            me.materials.append(m)
    new.parent = parent
    new.matrix_parent_inverse = pinv
    new.location, new.rotation_euler, new.scale = loc, rot, scl
    return new

# --------------------------------------------------------------------------
# materials
def material(name, color, rough=0.4, metal=0.0, coat=0.0, coat_rough=0.05,
             transmission=0.0, ior=1.45, spec=0.5):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["IOR"].default_value = ior
    b.inputs["Specular IOR Level"].default_value = spec
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Coat Roughness"].default_value = coat_rough
    b.inputs["Transmission Weight"].default_value = transmission
    m.diffuse_color = (*color, 1.0)
    m.roughness = rough
    m.metallic = metal
    return m

def srgb(r, g, b):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(r), lin(g), lin(b))

M = {}
def make_materials():
    M["yellow"] = material("Yellow Plastic", srgb(236, 198, 44), rough=0.3, coat=0.3)
    M["black"] = material("Black Plastic", srgb(12, 12, 13), rough=0.38, spec=0.4)
    M["black_matte"] = material("Black Rubber", srgb(14, 14, 15), rough=0.5)
    M["ink"] = material("Black Ink", srgb(6, 6, 7), rough=0.75, spec=0.25)
    M["interior"] = material("Dark Interior", srgb(8, 8, 9), rough=0.8)
    M["seam"] = material("Seam Shadow", srgb(70, 52, 10), rough=0.7)
    M["chrome"] = material("Eye Bezel Brass", srgb(226, 196, 132), rough=0.14, metal=1.0)
    M["eye_white"] = material("Eye White", srgb(246, 246, 242), rough=0.3, spec=0.4)
    M["pupil"] = material("Pupil Black", srgb(10, 10, 12), rough=0.12, coat=0.5)
    M["teeth"] = material("Teeth", srgb(232, 226, 200), rough=0.35)
    M["white"] = material("Print White", srgb(232, 236, 240), rough=0.45)
    M["lens"] = material("Eye Lens", (1.0, 1.0, 1.0), rough=0.0, transmission=1.0, ior=1.45)

# --------------------------------------------------------------------------
# geometry builders
def arc(cx, cz, rad, a0, a1, n):
    return [(cx + rad * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cz + rad * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]

def revolve(profile, segs=128):
    """profile: list of (r, z) from bottom pole to top pole. Returns verts,
    faces and the profile-segment index of every face."""
    verts, rings = [], []
    for r, z in profile:
        if r < 1e-9:
            rings.append([len(verts)])
            verts.append(Vector((0.0, 0.0, z)))
        else:
            ring = []
            for j in range(segs):
                a = 2 * math.pi * j / segs
                ring.append(len(verts))
                verts.append(Vector((r * math.cos(a), r * math.sin(a), z)))
            rings.append(ring)
    faces, seg = [], []
    for i in range(len(rings) - 1):
        A, B = rings[i], rings[i + 1]
        if len(A) == 1 and len(B) == 1:
            continue
        for j in range(segs):
            k = (j + 1) % segs
            if len(A) == 1:
                faces.append((A[0], B[k], B[j]))
            elif len(B) == 1:
                faces.append((A[j], A[k], B[0]))
            else:
                faces.append((A[j], A[k], B[k], B[j]))
            seg.append(i)
    return verts, faces, seg

def tube(name, pts, radius, radii=None, mats=(), res=10, bevel_res=5, parent=None,
         round_ends=()):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = bevel_res
    cu.use_fill_caps = True
    cu.resolution_u = res
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        bp = sp.bezier_points[i]
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
        bp.radius = radii[i] if radii else 1.0
    for m in mats:
        cu.materials.append(m)
    ob = link(bpy.data.objects.new(name, cu))
    if parent:
        ob.parent = parent
    ob = curve_to_mesh(ob)
    if round_ends:
        # spherical end caps instead of flat cut tube ends
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        for i in round_ends:
            r = radius * (radii[i] if radii else 1.0)
            bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=r,
                                      matrix=Matrix.Translation(pts[i]))
        bm.to_mesh(ob.data)
        bm.free()
    smooth_by_angle(ob, 50)
    return ob

def ring_tube(name, pts, radius, mats=(), bevel_res=4, parent=None):
    """Closed poly tube through the given points (already dense)."""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = bevel_res
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    sp.use_cyclic_u = True
    for m in mats:
        cu.materials.append(m)
    ob = link(bpy.data.objects.new(name, cu))
    if parent:
        ob.parent = parent
    ob = curve_to_mesh(ob)
    smooth_by_angle(ob, 60)
    return ob

def text_mesh(name, body, font, size, extrude, align_x='CENTER', align_y='CENTER',
              mats=(), spacing=1.0):
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = body
    cu.font = bpy.data.fonts.load(FONT_DIR + font, check_existing=True)
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align_x
    cu.align_y = align_y
    cu.space_character = spacing
    cu.resolution_u = 6
    for m in mats:
        cu.materials.append(m)
    ob = link(bpy.data.objects.new(name, cu))
    ob = curve_to_mesh(ob)
    return ob

def rounded_box(name, size, bevel, mats=(), segments=3, parent=None, loc=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = link(bpy.data.objects.new(name, me))
    ob.location = loc
    if bevel > 0:
        md = ob.modifiers.new("Bevel", 'BEVEL')
        md.width = bevel
        md.segments = segments
        md.limit_method = 'NONE'
        bake_modifiers(ob)
    smooth_by_angle(ob, 40)
    if parent:
        ob.parent = parent
    return ob

def polygon_slab(name, outline, z0, z1, bevel=0.0, segments=3, mats=(), parent=None):
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, z0)) for x, y in outline]
    f = bm.faces.new(vs)
    bmesh.ops.recalc_face_normals(bm, faces=[f])
    if f.normal.z > 0:
        f.normal_flip()
    ext = bmesh.ops.extrude_face_region(bm, geom=[f], use_keep_orig=True)
    top = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    for v in top:
        v.co.z = z1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = link(bpy.data.objects.new(name, me))
    if bevel > 0:
        md = ob.modifiers.new("Bevel", 'BEVEL')
        md.width = bevel
        md.segments = segments
        md.limit_method = 'ANGLE'
        md.angle_limit = math.radians(30)
        md.harden_normals = False
        bake_modifiers(ob)
    smooth_by_angle(ob, 40)
    if parent:
        ob.parent = parent
    return ob

def boolean(target, cutter, op='DIFFERENCE'):
    md = target.modifiers.new("Bool", 'BOOLEAN')
    md.operation = op
    md.object = cutter
    md.solver = 'EXACT'
    md.material_mode = 'TRANSFER'
    bake_modifiers(target)

def delete(ob):
    me = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    if me and me.users == 0:
        if isinstance(me, bpy.types.Mesh):
            bpy.data.meshes.remove(me)

# --------------------------------------------------------------------------
# parts
def build_base():
    prof = [(0, 0.0)] + arc(0.395, 0.018, 0.018, -90, 0, 5) + \
           arc(0.395, BASE_H - 0.012, 0.012, 0, 90, 4) + [(0, BASE_H)]
    v, f, _ = revolve(prof, 96)
    mesh_object("Base Puck", v, f, [M["black"]])

    # flat black plate under the body that carries the two feet
    w, d, r = 0.64, 0.22, 0.06
    pts = []
    yc = 0.07
    for cx, cy, a0 in ((w - r, d - r, 0), (-w + r, d - r, 90), (-w + r, -d + r, 180), (w - r, -d + r, 270)):
        for i in range(7):
            a = math.radians(a0 + 90 * i / 6)
            pts.append((cx + r * math.cos(a), yc + cy + r * math.sin(a)))
    polygon_slab("Base Plate", pts, 0.0, 0.036, bevel=0.006, mats=[M["black"]])

def build_body():
    rb, rt = 0.085, 0.016
    htop = BODY_TOPC - BASE_H
    prof = [(0, 0.0), (R - rb - 0.12, 0.0)] + arc(R - rb, rb, rb, -90, 0, 12) + \
           [(R, rb + 0.06), (R, htop * 0.5), (R, htop - rt - 0.02)] + \
           arc(R - rt, htop - rt, rt, 0, 90, 6) + [(R - rt - 0.02, htop), (0, htop)]
    v, f, seg = revolve(prof, 160)
    nseg = len(prof) - 1
    # top cap is the dark inside of the mouth
    mats = [1 if s >= nseg - 1 else 0 for s in seg]
    z0 = rb + 0.02
    for p in v:
        w = min(1.0, max(0.0, (p.z - z0) / (htop - z0)))
        p.z += BASE_H - SLOPE * p.y * w      # front (-y) is taller
    body = mesh_object("Body", v, f, [M["yellow"], M["interior"]], mats)

    # vertical parting lines front and back
    for i, y in enumerate((-R, R)):
        c = rounded_box("seam_cut", (0.0055, 0.016, 1.2), 0.0, mats=[M["seam"]],
                        loc=(0, y, 0.6))
        boolean(body, c)
        delete(c)
    smooth_by_angle(body, 35)
    return body

def build_shoulders():
    for side in (-1, 1):
        # collar coming out of the body, then the round cap
        prof = [(0, -0.07), (0.158, -0.07)] + [(0.158, 0.045)] + \
               arc(0.150, 0.052, 0.008, 0, 90, 3) + [(0, 0.06)]
        v, f, _ = revolve(prof, 96)
        rot = Matrix.Rotation(math.radians(90 * side), 4, 'Y')
        mw = Matrix.Translation((side * R, 0, SHOULDER_Z)) @ rot
        v = [mw @ p for p in v]
        mesh_object("Shoulder Collar " + ("L" if side > 0 else "R"), v, f, [M["yellow"]])

        rc = 0.04
        prof = [(0, 0.063)] + arc(SHOULDER_R - 0.008, 0.071, 0.008, -90, 0, 3) + \
               [(SHOULDER_R, 0.19 - rc)] + arc(SHOULDER_R - rc, 0.205 - rc, rc, 0, 90, 8) + \
               [(0, 0.205)]
        v, f, _ = revolve(prof, 96)
        v = [mw @ p for p in v]
        mesh_object("Shoulder Cap " + ("L" if side > 0 else "R"), v, f, [M["yellow"]])

def head_matrix():
    m_tilt = Matrix.Translation((0, 0, BODY_TOPC + 0.004)) @ Matrix.Rotation(-TILT, 4, 'X')
    hinge = Vector((0, R * math.cos(TILT), BODY_TOPC - R * math.sin(TILT)))
    m_open = Matrix.Translation(hinge) @ Matrix.Rotation(-MOUTH_OPEN, 4, 'X') @ Matrix.Translation(-hinge)
    return m_open @ m_tilt

def build_head():
    # head pivot empty: local frame has the head bottom centre at the origin
    piv = link(bpy.data.objects.new("Head", None))
    piv.empty_display_type = 'PLAIN_AXES'
    piv.empty_display_size = 0.3
    piv.matrix_world = head_matrix()

    rb, rt = 0.022, 0.034
    H = HEAD_H
    prof = [(0, 0.0), (R - rb - 0.02, 0.0)] + arc(R - rb, rb, rb, -90, 0, 6) + \
           [(R, H * 0.5), (R, H - rt)] + arc(R - rt, H - rt, rt, 0, 90, 10) + \
           [(0.452, H), (0.452, H - 0.014), (0, H - 0.014)]
    v, f, seg = revolve(prof, 160)
    mats = [1 if s == 0 else 0 for s in seg]
    shell = mesh_object("Head Shell", v, f, [M["yellow"], M["interior"]], mats)

    # eye sockets (chrome walls, dark floor)
    for side in (-1, 1):
        ex = side * 0.158
        prof = [(0, 0.0), (0.118, 0.0), (0.118, 0.32), (0, 0.32)]
        v, f, seg = revolve(prof, 96)
        mw = Matrix.Translation((ex, -0.30, 0.192)) @ Matrix.Rotation(math.radians(90), 4, 'X')
        v = [mw @ p for p in v]
        mats = [0 if s == 1 else 1 for s in seg]
        cut = mesh_object("eye_cut", v, f, [M["chrome"], M["interior"]], mats, smooth=False)
        boolean(shell, cut)
        delete(cut)
    # small slot on the back of the head
    cut = rounded_box("slot_cut", (0.13, 0.08, 0.014), 0.0068, mats=[M["interior"]],
                      segments=4, loc=(0, R, 0.235))
    boolean(shell, cut)
    delete(cut)
    smooth_by_angle(shell, 35)
    shell.parent = piv

    build_eyes(piv)
    build_teeth(piv)
    build_top(piv)
    return piv

def surface_y(x, r=R):
    return -math.sqrt(max(0.0, r * r - x * x))

def build_eyes(piv):
    for side in (-1, 1):
        ex, ez = side * 0.158, 0.192
        tag = "L" if side > 0 else "R"
        # eyeball
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=40, radius=0.112)
        me = bpy.data.meshes.new("Eyeball " + tag)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(M["eye_white"])
        ob = link(bpy.data.objects.new("Eyeball " + tag, me))
        ob.location = (ex, -0.35, ez)
        ob.parent = piv
        smooth_by_angle(ob, 80)
        # pupil: glossy black spherical cap, looking down and slightly inwards
        look = Vector((-side * 0.10, -0.66, -0.75)).normalized()
        q = Vector((0, 0, 1)).rotation_difference(look)
        rp, half, nr, na = 0.1135, math.radians(43), 14, 96
        verts = [q @ Vector((0, 0, rp))]
        faces = []
        for k in range(1, nr + 1):
            pa = half * k / nr
            for j in range(na):
                a = 2 * math.pi * j / na
                verts.append(q @ Vector((rp * math.sin(pa) * math.cos(a),
                                         rp * math.sin(pa) * math.sin(a), rp * math.cos(pa))))
        for j in range(na):
            faces.append((0, 1 + j, 1 + (j + 1) % na))
        for k in range(nr - 1):
            a0, a1 = 1 + k * na, 1 + (k + 1) * na
            for j in range(na):
                jj = (j + 1) % na
                faces.append((a0 + j, a1 + j, a1 + jj, a0 + jj))
        pup = mesh_object("Pupil " + tag, verts, faces, [M["pupil"]], sharp_angle=80)
        pup.location = (ex, -0.35, ez)
        pup.parent = piv

        # chrome bezel ring hugging the curved face
        pts = []
        for i in range(96):
            a = 2 * math.pi * i / 96
            x = ex + 0.124 * math.cos(a)
            z = ez + 0.124 * math.sin(a)
            pts.append((x, surface_y(x) + 0.002, z))
        ring_tube("Eye Bezel " + tag, pts, 0.0085, mats=[M["chrome"]], parent=piv)

        # clear domed lens following the curvature of the face
        nr, na = 10, 64
        verts, faces = [], []
        rl = 0.117
        for layer, off in ((0, 0.0), (1, 0.004)):
            verts.append(Vector((ex, surface_y(ex) - 0.016 + off + 0.004, ez)))
            for i in range(1, nr + 1):
                rr = rl * i / nr
                bul = 0.016 * (1 - (i / nr) ** 2)
                for j in range(na):
                    a = 2 * math.pi * j / na
                    x = ex + rr * math.cos(a)
                    z = ez + rr * math.sin(a)
                    verts.append(Vector((x, surface_y(x) - bul + off + 0.004, z)))
        per = 1 + nr * na
        for layer in (0, 1):
            o = layer * per
            flip = layer == 1
            for j in range(na):
                k = (j + 1) % na
                t = (o, o + 1 + j, o + 1 + k)
                faces.append(t[::-1] if flip else t)
            for i in range(nr - 1):
                a0 = o + 1 + i * na
                a1 = a0 + na
                for j in range(na):
                    k = (j + 1) % na
                    q = (a0 + j, a1 + j, a1 + k, a0 + k)
                    faces.append(q[::-1] if flip else q)
        # close the rim between the two layers
        r0, r1 = 1 + (nr - 1) * na, per + 1 + (nr - 1) * na
        for j in range(na):
            k = (j + 1) % na
            faces.append((r0 + j, r1 + j, r1 + k, r0 + k))
        lens = mesh_object("Eye Lens " + tag, verts, faces, [M["lens"]], sharp_angle=60)
        lens.parent = piv

def build_teeth(piv):
    for side in (-1, 1):
        t = rounded_box("Tooth " + ("L" if side > 0 else "R"), (0.040, 0.03, 0.07), 0.012,
                        mats=[M["teeth"]], segments=4, loc=(side * 0.0365, -0.455, -0.012))
        t.parent = piv

def build_top(piv):
    H = HEAD_H
    zt = H + 0.006
    prof = [(0, H - 0.014), (0.446, H - 0.014), (0.446, H - 0.0)] + \
           arc(0.438, zt - 0.008, 0.008, 0, 90, 4) + [(0, zt)]
    v, f, _ = revolve(prof, 160)
    disc = mesh_object("Top Disc", v, f, [M["black"]])
    disc.parent = piv

    # six raised pin-stripes across the lid
    rr = 0.425
    for i in range(6):
        y = -0.108 + 0.0275 * i
        half = math.sqrt(rr * rr - y * y)
        s = rounded_box("Lid Stripe %d" % i, (2 * half, 0.0045, 0.003), 0.0012,
                        mats=[M["black"]], segments=1, loc=(0, y, zt + 0.0004))
        s.parent = piv

    # Radio Shack logo, readable from the front
    def fit(ob, x0, x1, yc):
        """scale a flat text mesh to span x0..x1 and centre it on yc"""
        vs = ob.data.vertices
        xs = [v.co.x for v in vs]
        ys = [v.co.y for v in vs]
        k = (x1 - x0) / (max(xs) - min(xs))
        mx, my = min(xs), (min(ys) + max(ys)) / 2
        for v in vs:
            v.co.x = x0 + (v.co.x - mx) * k
            v.co.y = yc + (v.co.y - my) * k
        ob.location = (0, 0, zt + 0.0008)

    t1 = text_mesh("Logo Radio Shack", "Radio Shack", "Arial Bold Italic.ttf", 0.07, 0.0008,
                   align_x='LEFT', mats=[M["white"]], spacing=0.95)
    fit(t1, -0.283, 0.05, 0.143)
    t2 = text_mesh("Logo Robotic Banker", "ROBOTIC BANKER", "Arial Bold.ttf", 0.03, 0.0008,
                   align_x='LEFT', mats=[M["white"]], spacing=1.15)
    fit(t2, -0.272, 0.05, 0.094)
    # circled dollar mark
    lx, ly, lr = -0.333, 0.118, 0.041
    pts = []
    for i in range(64):
        a = 2 * math.pi * i / 64
        pts.append((lx + lr * math.cos(a), ly + lr * math.sin(a), 0.0))
    ring = ring_tube("Logo Ring", pts, 0.0036, mats=[M["white"]])
    ring.location.z = zt + 0.0006
    ring.scale = (1, 1, 0.3)
    d = text_mesh("Logo Dollar", "$", "Arial Bold.ttf", 0.07, 0.0008, mats=[M["white"]])
    d.location = (lx, ly, zt + 0.0008)
    for o in (t1, t2, ring, d):
        o.parent = piv

def build_feet():
    for side in (-1, 1):
        tag = "L" if side > 0 else "R"
        L, Wb, Wf, Hb, Hf = 0.82, 0.335, 0.23, 0.265, 0.21
        grooves = [-0.195, -0.163, -0.131]     # y positions (front is -y)
        gw = 0.0032
        ss = [-math.cos(math.pi * i / 56) for i in range(57)]
        for gy in grooves:
            for d in (-2 * gw, -gw, -0.5 * gw, 0, 0.5 * gw, gw, 2 * gw):
                ss.append(-(gy + d) / (L / 2))
        ss = sorted(set(round(s, 6) for s in ss))

        def env(s, p):
            return max(0.0, 1 - abs(s) ** p) ** (1 / p)

        def groove(s):
            y = -s * L / 2
            g = 0.0
            for gy in grooves:
                d = abs(y - gy) / gw
                if d < 1.6:
                    g = max(g, math.exp(-d * d * 2.2))
            return g

        na = 36
        verts, faces = [], []
        rings = []
        for s in ss:
            t = (s + 1) / 2
            w = (Wb / 2 + (Wf / 2 - Wb / 2) * t) * env(s, 3.0)
            h = (Hb + (Hf - Hb) * t) * env(s, 2.5)
            y = -s * L / 2
            if w < 1e-5:
                rings.append([len(verts)])
                verts.append(Vector((0, y, 0)))
                continue
            k = 1 - 0.0045 * groove(s) / max(w, h)
            ring = []
            for i in range(na + 1):
                ph = math.pi * i / na
                c, sn = math.cos(ph), math.sin(ph)
                x = w * math.copysign(abs(c) ** (2 / 2.4), c)
                z = h * abs(sn) ** (2 / 2.4)
                ring.append(len(verts))
                verts.append(Vector((x * k, y, z * k)))
            rings.append(ring)
        for a, b in zip(rings[:-1], rings[1:]):
            if len(a) == 1:
                for i in range(na):
                    faces.append((a[0], b[i], b[i + 1]))
                faces.append((a[0], b[na], b[0]))
            elif len(b) == 1:
                for i in range(na):
                    faces.append((a[i], b[0], a[i + 1]))
                faces.append((a[na], b[0], a[0]))
            else:
                for i in range(na):
                    faces.append((a[i], b[i], b[i + 1], a[i + 1]))
                faces.append((a[na], b[na], b[0], a[0]))     # flat underside
        foot = mesh_object("Foot " + tag, verts, faces, [M["yellow"]], sharp_angle=50)
        # make normals point outwards
        bm = bmesh.new()
        bm.from_mesh(foot.data)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(foot.data)
        bm.free()
        toe_in = math.radians(-side * 5)
        foot.location = (side * FOOT_X, 0.0, 0.03)
        foot.rotation_euler.z = toe_in

        # black sole following the footprint
        outline = []
        n = 80
        for i in range(n + 1):
            s = -math.cos(math.pi * i / n)
            t = (s + 1) / 2
            w = (Wb / 2 + (Wf / 2 - Wb / 2) * t) * env(s, 3.0)
            outline.append((w, -s * L / 2))
        right = outline
        left = [(-x, y) for x, y in reversed(outline[1:-1])]
        poly = right + left
        # offset the outline outwards
        off = []
        npnt = len(poly)
        for i in range(npnt):
            p0 = Vector(poly[i - 1]); p1 = Vector(poly[i]); p2 = Vector(poly[(i + 1) % npnt])
            tng = (p2 - p0).normalized()
            nrm = Vector((tng.y, -tng.x))
            if nrm.dot(p1) < 0:
                nrm = -nrm
            q = p1 + nrm * 0.012
            off.append((q.x, q.y))
        # drop near-duplicates
        clean = [off[0]]
        for p in off[1:]:
            if (Vector(p) - Vector(clean[-1])).length > 1e-4:
                clean.append(p)
        sole = polygon_slab("Sole " + tag, clean, 0.0, 0.032, bevel=0.007, mats=[M["black"]])
        sole.location = (side * FOOT_X, 0.0, 0.0)
        sole.rotation_euler.z = toe_in

def build_text_robie(body):
    t = text_mesh("ROBIE Lettering", "ROBIE", "Arial Black.ttf", 0.118, 0.0012,
                  mats=[M["ink"]], spacing=1.0)
    me = t.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    xs = [v.co.x for v in bm.verts]
    width = max(xs) - min(xs)
    theta_c = math.radians(-31)
    zc = 0.672
    rs = R + 0.0022
    for v in bm.verts:
        u, w_, h = v.co.x, v.co.z, v.co.y
        th = theta_c + u / rs
        rr = rs + w_
        v.co = Vector((rr * math.sin(th), -rr * math.cos(th), zc + h))
    bm.to_mesh(me)
    bm.free()
    t.location = (0, 0, 0)
    smooth_by_angle(t, 30)
    return width

TRAY_R = 0.222
TRAY_TAIL = 0.12
TRAY_TAIL_DIR = math.radians(-14)

def tray_matrix():
    return (Matrix.Translation((0.285, -0.69, 0.25)) @
            Matrix.Rotation(math.radians(13), 4, 'X') @
            Matrix.Rotation(math.radians(30), 4, 'Z'))

def build_arms():
    # robot's right arm (viewer's left): hook hand
    J = Vector((-0.612, -0.36, 0.20))           # wrist, where the hand starts
    arm = [(-0.60, -0.02, SHOULDER_Z), (-0.603, -0.05, SHOULDER_Z - 0.15),
           (-0.612, -0.19, 0.25), tuple(J)]
    tube("Arm R", arm, 0.039, mats=[M["black_matte"]], res=14)
    # upper finger: a C-shaped curl opening downwards, swept forward and inward
    u = Vector((0.92, -0.40, 0.0)).normalized()
    rc = 0.112
    curl = []
    for ang in (182, 150, 118, 90, 62, 34, 6, -22, -48):
        a_ = math.radians(ang)
        curl.append(J + u * (rc + rc * math.cos(a_)) + Vector((0, 0, 0.01 + rc * math.sin(a_))))
    tube("Hand R Hook", [tuple(J)] + [tuple(p) for p in curl], 0.048,
         [1.0] + [1.0] * 7 + [0.95, 0.85], mats=[M["black_matte"]], res=10, round_ends=(9,))
    # lower finger: drops to the floor and kicks forward
    leg = [tuple(J), (-0.614, -0.40, 0.14), (-0.598, -0.45, 0.08), (-0.565, -0.51, 0.056),
           (-0.53, -0.56, 0.058)]
    tube("Hand R Prong", leg, 0.048, [1.0, 1.0, 1.0, 1.0, 0.92], mats=[M["black_matte"]], res=10,
         round_ends=(4,))

    # robot's left arm (viewer's right): coin tray hand
    mt = tray_matrix()
    tip = mt @ Vector(((TRAY_R + TRAY_TAIL - 0.03) * math.cos(TRAY_TAIL_DIR),
                       (TRAY_R + TRAY_TAIL - 0.03) * math.sin(TRAY_TAIL_DIR), 0.0))
    pts = [(0.60, -0.02, SHOULDER_Z), (0.605, -0.05, SHOULDER_Z - 0.15),
           (0.655, -0.17, 0.25), (0.66, -0.32, 0.215), tuple(tip + Vector((0.035, 0.05, -0.012))),
           tuple(tip)]
    tube("Arm L", pts, 0.039, None, mats=[M["black_matte"]], res=14)
    build_tray()

def build_tray():
    # outline: round dish with a speech-bubble tail pointing at the arm
    pts = []
    n = 200
    th0 = TRAY_TAIL_DIR
    for i in range(n):
        th = 2 * math.pi * i / n
        d = math.atan2(math.sin(th - th0), math.cos(th - th0))
        bump = max(0.0, 1 - abs(d) / 0.6) ** 1.7
        r = TRAY_R + TRAY_TAIL * bump
        pts.append((r * math.cos(th), r * math.sin(th)))
    cu = bpy.data.curves.new("Coin Tray", 'CURVE')
    cu.dimensions = '2D'
    cu.fill_mode = 'BOTH'
    cu.extrude = 0.008
    cu.bevel_depth = 0.006
    cu.bevel_resolution = 3
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, (x, y) in enumerate(pts):
        sp.points[i].co = (x, y, 0, 1)
    sp.use_cyclic_u = True
    cu.materials.append(M["black_matte"])
    tray = link(bpy.data.objects.new("Coin Tray", cu))
    tray = curve_to_mesh(tray)
    smooth_by_angle(tray, 40)

    parts = [tray]
    # raised lip around the dish
    lip = []
    for i in range(128):
        a = 2 * math.pi * i / 128
        lip.append((0.212 * math.cos(a), 0.212 * math.sin(a), 0.014))
    parts.append(ring_tube("Tray Lip", lip, 0.009, mats=[M["black_matte"]]))
    # upturned flap where the hand joins the dish
    fl = []
    for i in range(21):
        a = math.radians(-62 + 104 * i / 20)
        fl.append((0.226 * math.cos(a), 0.226 * math.sin(a), 0.02 + 0.014 * math.sin(math.pi * i / 20)))
    parts.append(tube("Tray Flap", fl, 0.013, mats=[M["black_matte"]], res=4))

    # white printed ring and dollar sign
    cx = -0.02
    ring = []
    for i in range(128):
        a = 2 * math.pi * i / 128
        ring.append((cx + 0.158 * math.cos(a), 0.158 * math.sin(a), 0.0))
    pr = ring_tube("Tray Print Ring", ring, 0.0068, mats=[M["white"]])
    pr.location.z = 0.0145
    pr.scale = (1, 1, 0.12)
    parts.append(pr)
    s = text_mesh("Tray Print S", "S", "Georgia Bold.ttf", 0.25, 0.0006, mats=[M["white"]])
    s.location = (cx, 0.0, 0.0148)
    parts.append(s)
    for bx in (-0.016, 0.016):
        b = rounded_box("Tray Print Bar", (0.011, 0.245, 0.0012), 0.0, mats=[M["white"]])
        b.location = (cx + bx, 0.0, 0.0148)
        parts.append(b)

    # print reads upright when seen from the front
    prn = link(bpy.data.objects.new("Tray Print", None))
    prn.empty_display_size = 0.05
    prn.rotation_euler.z = math.radians(-30)
    for p in parts[3:]:
        p.parent = prn
    root = link(bpy.data.objects.new("Tray Hand", None))
    root.empty_display_size = 0.1
    for p in parts[:3] + [prn]:
        p.parent = root
    # place the tray in front of the body, tail pointing back at the arm
    root.matrix_world = tray_matrix()
    return root

# --------------------------------------------------------------------------
def build():
    global ROBOT
    clear_scene()
    ROBOT = coll("Robie")
    make_materials()
    build_base()
    body = build_body()
    build_text_robie(body)
    build_shoulders()
    build_head()
    build_feet()
    build_arms()
    return {"objects": len(ROBOT.all_objects)}

if __name__ == "__main__" or True:
    RESULT = build()
