# Shared helpers for building the octopus ramen booth scene.
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix, Euler, Quaternion, noise
from mathutils.bvhtree import BVHTree

PI = math.pi
FONT_DIR = bpy.utils.system_resource('DATAFILES', path='fonts')


def clear_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for blocks in (bpy.data.meshes, bpy.data.materials, bpy.data.curves,
                   bpy.data.lights, bpy.data.cameras, bpy.data.node_groups):
        for b in list(blocks):
            blocks.remove(b)
    for im in list(bpy.data.images):
        if im.name != 'Render Result':
            bpy.data.images.remove(im)


def get_coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def cjk_font():
    f = bpy.data.fonts.get("Noto Sans CJK SC Regular")
    if f is None:
        f = bpy.data.fonts.load(os.path.join(FONT_DIR, "Noto Sans CJK Regular.woff2"))
    return f


# ---------------------------------------------------------------- materials
def make_mat(name, color, rough=0.5, metal=0.0, emit=None, emit_strength=0.0,
             alpha=1.0, vcol=False, coat=0.0, sss=0.0, spec=0.5, transmission=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    p = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled'][0]
    p.inputs["Base Color"].default_value = (*color, 1.0)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Specular IOR Level"].default_value = spec
    if coat:
        p.inputs["Coat Weight"].default_value = coat
        p.inputs["Coat Roughness"].default_value = 0.08
    if sss:
        p.inputs["Subsurface Weight"].default_value = sss
        p.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
        p.inputs["Subsurface Scale"].default_value = 0.03
    if transmission:
        p.inputs["Transmission Weight"].default_value = transmission
    if emit is not None:
        p.inputs["Emission Color"].default_value = (*emit, 1.0)
        p.inputs["Emission Strength"].default_value = emit_strength
    if alpha < 1.0:
        p.inputs["Alpha"].default_value = alpha
        m.surface_render_method = 'BLENDED'
        m.use_transparency_overlap = True
    if vcol:
        ca = nt.nodes.new('ShaderNodeVertexColor')
        ca.layer_name = "Col"
        ca.location = (-400, 200)
        nt.links.new(ca.outputs["Color"], p.inputs["Base Color"])
    m.diffuse_color = (*color, 1.0)
    m["flat_color"] = list(color)
    return m


def principled(m):
    return [n for n in m.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled'][0]


# ---------------------------------------------------------------- objects
def obj_from_bm(name, bm, mat=None, coll=None, smooth=True, loc=None, rot=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    if mat is not None:
        if isinstance(mat, (list, tuple)):
            for mm in mat:
                me.materials.append(mm)
        else:
            me.materials.append(mat)
    if loc is not None:
        ob.location = loc
    if rot is not None:
        ob.rotation_euler = rot
    return ob


def obj_from_data(name, verts, faces, mat=None, coll=None, smooth=True, loc=None, rot=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.validate()
    me.update()
    if smooth:
        me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    if loc is not None:
        ob.location = loc
    if rot is not None:
        ob.rotation_euler = rot
    return ob


def bevel(ob, width=0.008, segs=2, harden=True):
    md = ob.modifiers.new("Bevel", 'BEVEL')
    md.width = width
    md.segments = segs
    md.limit_method = 'ANGLE'
    md.harden_normals = harden
    return md


def box(name, size, loc, mat=None, coll=None, rot=None, bev=0.006, segs=2):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, calc_uvs=True)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    ob = obj_from_bm(name, bm, mat, coll, smooth=bev > 0, loc=loc, rot=rot)
    if bev > 0:
        bevel(ob, bev, segs)
    return ob


def box_minmax(name, mn, mx, mat=None, coll=None, bev=0.006, segs=2):
    size = [mx[i] - mn[i] for i in range(3)]
    loc = [(mx[i] + mn[i]) / 2 for i in range(3)]
    return box(name, size, loc, mat, coll, bev=bev, segs=segs)


def cylinder(name, r, h, loc, mat=None, coll=None, segs=32, rot=None, r2=None, bev=0.0, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs,
                          radius1=r, radius2=r if r2 is None else r2, depth=h, calc_uvs=True)
    ob = obj_from_bm(name, bm, mat, coll, smooth=smooth, loc=loc, rot=rot)
    if bev > 0:
        bevel(ob, bev, 2)
    return ob


def sphere(name, r, loc, mat=None, coll=None, scale=(1, 1, 1), segs=24, rings=16, rot=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=r, calc_uvs=True)
    bmesh.ops.scale(bm, vec=Vector(scale), verts=bm.verts)
    return obj_from_bm(name, bm, mat, coll, smooth=True, loc=loc, rot=rot)


def lathe_data(profile, segs=32, phase=0.0):
    """Surface of revolution around Z. profile = [(r, z), ...]."""
    verts, faces, rings = [], [], []
    for (r, z) in profile:
        if r < 1e-6:
            verts.append((0.0, 0.0, z))
            rings.append([len(verts) - 1] * segs)
        else:
            idx = []
            for i in range(segs):
                a = 2 * PI * i / segs + phase
                verts.append((r * math.cos(a), r * math.sin(a), z))
                idx.append(len(verts) - 1)
            rings.append(idx)
    for k in range(len(rings) - 1):
        A, B = rings[k], rings[k + 1]
        for i in range(segs):
            j = (i + 1) % segs
            f = []
            for v in (A[i], A[j], B[j], B[i]):
                if v not in f:
                    f.append(v)
            if len(f) >= 3:
                faces.append(f)
    return verts, faces


def lathe(name, profile, loc=(0, 0, 0), mat=None, coll=None, segs=32, smooth=True, rot=None, scale=None):
    v, f = lathe_data(profile, segs)
    ob = obj_from_data(name, v, f, mat, coll, smooth, loc, rot)
    if scale:
        ob.scale = scale
    return ob


# ---------------------------------------------------------------- curves / tubes
def catmull(points, samples_per_seg=8, closed=False):
    pts = [Vector(p) for p in points]
    if closed:
        P = [pts[-1]] + pts + [pts[0], pts[1]]
        nseg = len(pts)
    else:
        P = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
        nseg = len(pts) - 1
    out = []
    for s in range(nseg):
        p0, p1, p2, p3 = P[s], P[s + 1], P[s + 2], P[s + 3]
        for i in range(samples_per_seg):
            t = i / samples_per_seg
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    if not closed:
        out.append(pts[-1].copy())
    return out


def resample(pts, n):
    """Resample polyline to n points evenly by arc length."""
    d = [0.0]
    for i in range(1, len(pts)):
        d.append(d[-1] + (pts[i] - pts[i - 1]).length)
    L = d[-1]
    out, j = [], 0
    for k in range(n):
        s = L * k / (n - 1)
        while j < len(d) - 2 and d[j + 1] < s:
            j += 1
        seg = d[j + 1] - d[j]
        t = 0.0 if seg < 1e-9 else (s - d[j]) / seg
        out.append(pts[j].lerp(pts[j + 1], min(max(t, 0), 1)))
    return out, L


def frames(pts, up=Vector((0, 0, 1))):
    """Parallel-transport frames (T, N) along polyline, N starts near 'up'."""
    n = len(pts)
    T = []
    for i in range(n):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        T.append((b - a).normalized())
    N = []
    n0 = Vector(up) - Vector(up).dot(T[0]) * T[0]
    if n0.length < 1e-4:
        n0 = T[0].orthogonal()
    N.append(n0.normalized())
    for i in range(1, n):
        q = T[i - 1].rotation_difference(T[i])
        v = q @ N[-1]
        v = v - v.dot(T[i]) * T[i]
        N.append(v.normalized())
    return T, N


def tube_data(pts, radii, ring=12, normals=None, cap_start=True, cap_end=True, twist=None, radial_fn=None):
    """Build a tube mesh along points. normals: per-point frame normal (dorsal)."""
    n = len(pts)
    if normals is None:
        T, N = frames(pts)
    else:
        T = []
        for i in range(n):
            a = pts[max(i - 1, 0)]
            b = pts[min(i + 1, n - 1)]
            T.append((b - a).normalized())
        N = []
        for i in range(n):
            v = Vector(normals[i])
            v = v - v.dot(T[i]) * T[i]
            if v.length < 1e-5:
                v = N[-1] if N else T[i].orthogonal()
            N.append(v.normalized())
    verts, faces = [], []
    for i in range(n):
        B = T[i].cross(N[i]).normalized()
        for k in range(ring):
            a = 2 * PI * k / ring + (twist[i] if twist else 0.0)
            r = radii[i]
            if radial_fn:
                r *= radial_fn(i, k, a)
            d = N[i] * math.cos(a) + B * math.sin(a)
            verts.append(tuple(pts[i] + d * r))
    for i in range(n - 1):
        for k in range(ring):
            k2 = (k + 1) % ring
            faces.append([i * ring + k, i * ring + k2, (i + 1) * ring + k2, (i + 1) * ring + k])
    if cap_start:
        verts.append(tuple(pts[0] - T[0] * radii[0] * 0.3))
        c = len(verts) - 1
        for k in range(ring):
            faces.append([c, (k + 1) % ring, k])
    if cap_end:
        verts.append(tuple(pts[-1] + T[-1] * radii[-1] * 0.6))
        c = len(verts) - 1
        base = (n - 1) * ring
        for k in range(ring):
            faces.append([base + k, base + (k + 1) % ring, c])
    return verts, faces, T, N


def tube(name, points, radius, mat=None, coll=None, ring=12, samples=6, n=None, smooth=True,
         cap=True, up=(0, 0, 1)):
    pts = catmull(points, samples)
    if n:
        pts, _ = resample(pts, n)
    if callable(radius):
        radii = [radius(i / (len(pts) - 1)) for i in range(len(pts))]
    else:
        radii = [radius] * len(pts)
    T, N = frames(pts, Vector(up))
    v, f, _, _ = tube_data(pts, radii, ring, normals=N, cap_start=cap, cap_end=cap)
    return obj_from_data(name, v, f, mat, coll, smooth)


def helix(center, axis, radius, turns, a0, pitch, n, ref=None):
    """Points of a helix around 'axis' through 'center'."""
    axis = Vector(axis).normalized()
    ref = Vector(ref) if ref is not None else axis.orthogonal()
    u = (ref - ref.dot(axis) * axis).normalized()
    w = axis.cross(u)
    out = []
    for i in range(n):
        t = i / (n - 1)
        a = a0 + 2 * PI * turns * t
        out.append(Vector(center) + (u * math.cos(a) + w * math.sin(a)) * radius + axis * pitch * turns * t)
    return out


# ---------------------------------------------------------------- text
def text_mesh(name, body, size=0.1, extrude=0.0, align_x='CENTER', align_y='CENTER', font=None,
              subdivide=0, bold=0.0):
    cu = bpy.data.curves.new(name + "_crv", 'FONT')
    cu.body = body
    cu.font = font or cjk_font()
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align_x
    cu.align_y = align_y
    cu.resolution_u = 3
    cu.offset = bold
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    bpy.context.scene.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.curves.remove(cu)
    me.name = name
    if subdivide:
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        for _ in range(subdivide):
            bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=1, use_grid_fill=True)
        bm.to_mesh(me)
        bm.free()
    return me


def text_obj(name, body, size, loc, rot=(PI / 2, 0, 0), mat=None, coll=None, extrude=0.0,
             align_x='CENTER', align_y='CENTER', bold=0.0):
    me = text_mesh(name, body, size, extrude, align_x, align_y, bold=bold)
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    if mat:
        me.materials.append(mat)
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def vertical_text(name, chars, size, spacing=1.05, mat=None, coll=None, extrude=0.0, bold=0.0):
    """Vertical Japanese text: stack glyphs top-down in XY plane (Y up). Returns a mesh object
    at origin; 'ー' is rotated to a vertical stroke."""
    bm_all = bmesh.new()
    for i, ch in enumerate(chars):
        me = text_mesh(name + f"_{i}", ch, size, extrude, bold=bold)
        bm = bmesh.new()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
        if ch in "ー-":
            bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(PI / 2, 3, 'Z'))
        bmesh.ops.translate(bm, verts=bm.verts, vec=(0, -i * size * spacing, 0))
        tmp = bpy.data.meshes.new("tmp")
        bm.to_mesh(tmp)
        bm.free()
        bm_all.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    # centre vertically
    n = len(chars)
    bmesh.ops.translate(bm_all, verts=bm_all.verts, vec=(0, (n - 1) * size * spacing / 2, 0))
    return obj_from_bm(name, bm_all, mat, coll, smooth=False)


def set_vcol(ob, fn, name="Col"):
    """Set a per-corner color attribute from fn(world_co, normal, vert_index)->(r,g,b)."""
    me = ob.data
    if name in me.color_attributes:
        me.color_attributes.remove(me.color_attributes[name])
    ca = me.color_attributes.new(name, 'BYTE_COLOR', 'POINT')
    mw = ob.matrix_world
    nm = mw.to_3x3().inverted().transposed()
    for v in me.vertices:
        c = fn(mw @ v.co, (nm @ v.normal).normalized(), v.index)
        ca.data[v.index].color = (*c, 1.0)
    me.color_attributes.active_color = ca
    return ca


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def join(objs, name=None):
    """Join mesh objects into the first one (data API, no operators)."""
    if len(objs) == 1:
        return objs[0]
    bpy.context.view_layer.update()
    base = objs[0]
    bm = bmesh.new()
    mats = []
    inv = base.matrix_world.inverted()
    for ob in objs:
        me = ob.data
        tmp = me.copy()
        tmp.transform(inv @ ob.matrix_world)
        # remap materials
        remap = []
        for m in me.materials:
            if m not in mats:
                mats.append(m)
            remap.append(mats.index(m))
        for p in tmp.polygons:
            if remap:
                p.material_index = remap[p.material_index]
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    me = bpy.data.meshes.new(name or base.name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    old = base.data
    base.data = me
    for ob in objs[1:]:
        bpy.data.objects.remove(ob, do_unlink=True)
    if old.users == 0:
        bpy.data.meshes.remove(old)
    if name:
        base.name = name
        me.name = name
    return base


def lattice_crate(name, center, w, d, h, rz, mat, coll, upside_down=False):
    """Plastic beer crate: corner posts, rails and bars with open gaps, one solid panel."""
    parts = []
    t = 0.035
    cx, cy, cz = center
    # corner posts
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(box(f"{name}_p{sx}{sy}", (t, t, h), (sx * (w / 2 - t / 2), sy * (d / 2 - t / 2), h / 2),
                             mat, coll, bev=0.006, segs=1))
    # rails around at three heights
    for z in (0.02, h * 0.5, h - 0.02):
        for sy in (-1, 1):
            parts.append(box(f"{name}_rx{z:.2f}{sy}", (w, 0.022, 0.035), (0, sy * (d / 2 - 0.011), z), mat, coll,
                             bev=0.005, segs=1))
        for sx in (-1, 1):
            parts.append(box(f"{name}_ry{z:.2f}{sx}", (0.022, d, 0.035), (sx * (w / 2 - 0.011), 0, z), mat, coll,
                             bev=0.005, segs=1))
    # vertical bars
    for k in range(1, 5):
        x = -w / 2 + k * w / 5
        for sy in (-1, 1):
            parts.append(box(f"{name}_vx{k}{sy}", (0.018, 0.02, h), (x, sy * (d / 2 - 0.01), h / 2), mat, coll,
                             bev=0.004, segs=1))
    for k in range(1, 4):
        y = -d / 2 + k * d / 4
        for sx in (-1, 1):
            parts.append(box(f"{name}_vy{k}{sx}", (0.02, 0.018, h), (sx * (w / 2 - 0.01), y, h / 2), mat, coll,
                             bev=0.004, segs=1))
    # solid panel (bottom, or top when flipped) + inner grid
    pz = h - 0.012 if upside_down else 0.012
    parts.append(box(f"{name}_panel", (w - 0.01, d - 0.01, 0.024), (0, 0, pz), mat, coll, bev=0.004, segs=1))
    for k in range(1, 5):
        parts.append(box(f"{name}_gx{k}", (0.012, d - 0.02, 0.06 if upside_down else 0.0001 + 0.06),
                         (-w / 2 + k * w / 5, 0, h - 0.04 if upside_down else 0.04), mat, coll, bev=0.0))
    for ob in parts:
        for md in list(ob.modifiers):
            ob.modifiers.remove(md)
    bpy.context.view_layer.update()
    loc0 = parts[0].location.copy()
    ob = join(parts, name)
    ob.data.transform(Matrix.Translation(loc0))
    ob.location = (cx, cy, cz)
    ob.rotation_euler = (0, 0, rz)
    return ob
