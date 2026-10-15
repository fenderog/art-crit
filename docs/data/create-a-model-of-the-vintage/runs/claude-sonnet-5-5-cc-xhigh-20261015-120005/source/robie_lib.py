"""Small modelling toolkit for the Robie coin bank (Blender 5, bmesh only, no operators)."""
import bpy, bmesh, math
from math import pi, sin, cos, radians
from mathutils import Vector, Quaternion

scene = bpy.context.scene
M = {}          # material library
col = None      # collection that receives the robot


def reset():
    global col
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.curves,
                bpy.data.cameras, bpy.data.lights, bpy.data.images):
        for d in list(blk):
            blk.remove(d)
    M.clear()
    col = bpy.data.collections.new('Robie')
    scene.collection.children.link(col)
    return col


# ---------------------------------------------------------------- materials
def srgb(h):
    h = h.lstrip('#')
    r, g, b = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b))


def mat(key, hexc, metal=0.0, rough=0.5, emit=None, estr=0.0, coat=0.0):
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    c = srgb(hexc)
    b.inputs['Base Color'].default_value = (*c, 1)
    b.inputs['Metallic'].default_value = metal
    b.inputs['Roughness'].default_value = rough
    if coat:
        b.inputs['Coat Weight'].default_value = coat
        b.inputs['Coat Roughness'].default_value = 0.1
    if emit:
        b.inputs['Emission Color'].default_value = (*srgb(emit), 1)
        b.inputs['Emission Strength'].default_value = estr
    m.diffuse_color = (*c, 1)
    M[key] = m
    return m


# ---------------------------------------------------------------- hierarchy
def adopt(ch, par):
    bpy.context.view_layer.update()
    ch.parent = par
    ch.matrix_parent_inverse = par.matrix_world.inverted()


def empty(name, loc=(0, 0, 0), parent=None, size=0.02):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = 'PLAIN_AXES'
    e.empty_display_size = size
    col.objects.link(e)
    e.location = loc
    if parent:
        adopt(e, parent)
    return e


# ---------------------------------------------------------------- mesh -> object
def finish(name, bm, material, loc=(0, 0, 0), rot=(0, 0, 0), quat=None, parent=None,
           bevel=0.0, seg=3, smooth=True, wn=None, sharp_angle=None):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if sharp_angle is not None:
        for e in bm.edges:
            if len(e.link_faces) == 2 and e.calc_face_angle(0) > sharp_angle:
                e.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        me.shade_smooth()
    if material:
        me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    ob.location = loc
    if quat is not None:
        ob.rotation_mode = 'QUATERNION'
        ob.rotation_quaternion = quat
    else:
        ob.rotation_euler = rot
    if bevel > 0:
        b = ob.modifiers.new('Bevel', 'BEVEL')
        b.width = bevel
        b.segments = seg
        b.limit_method = 'ANGLE'
        b.angle_limit = radians(30)
        if wn is None:
            wn = True
    if wn:
        w = ob.modifiers.new('WeightedNormal', 'WEIGHTED_NORMAL')
        w.keep_sharp = True
        w.weight = 50
    if parent:
        adopt(ob, parent)
    return ob


# ---------------------------------------------------------------- primitives
def box(name, size, loc, material, bevel=0.003, seg=3, rot=(0, 0, 0), parent=None, taper=None, quat=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
        if taper and v.co.z > 0:
            v.co.x *= taper
    return finish(name, bm, material, loc, rot, quat, parent, bevel=bevel, seg=seg)


def rounded_slab(name, w, d, h, corner, loc, material, bevel=0.003, parent=None, seg=8):
    """slab with rounded vertical corners (rounded-rectangle outline extruded along Z)."""
    bm = bmesh.new()
    pts = []
    for cx, cy, a0 in ((w / 2 - corner, d / 2 - corner, 0), (-w / 2 + corner, d / 2 - corner, 90),
                       (-w / 2 + corner, -d / 2 + corner, 180), (w / 2 - corner, -d / 2 + corner, 270)):
        for i in range(seg + 1):
            a = radians(a0 + 90 * i / seg)
            pts.append((cx + corner * cos(a), cy + corner * sin(a)))
    bot = [bm.verts.new((x, y, -h / 2)) for x, y in pts]
    top = [bm.verts.new((x, y, h / 2)) for x, y in pts]
    bm.faces.new(bot[::-1])
    bm.faces.new(top)
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    return finish(name, bm, material, loc, parent=parent, bevel=bevel)


def lathe(name, profile, material, loc=(0, 0, 0), rot=(0, 0, 0), quat=None, parent=None,
          seg=48, loop=False, sharp=35, scale=(1, 1)):
    """Surface of revolution about Z. profile = [(radius, z), ...]; ends should lie on the
    axis (r == 0) unless loop=True (closed ring profile, torus-like)."""
    bm = bmesh.new()
    rings = []
    for (r, z) in profile:
        if r < 1e-9:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * scale[0] * cos(2 * pi * k / seg),
                                        r * scale[1] * sin(2 * pi * k / seg), z)) for k in range(seg)])
    n = len(rings)
    pairs = [(i, i + 1) for i in range(n - 1)]
    if loop:
        pairs.append((n - 1, 0))
    for i, j in pairs:
        A, B = rings[i], rings[j]
        for k in range(seg):
            k2 = (k + 1) % seg
            if len(A) == 1 and len(B) == 1:
                continue
            if len(A) == 1:
                bm.faces.new((A[0], B[k2], B[k]))
            elif len(B) == 1:
                bm.faces.new((A[k], A[k2], B[0]))
            else:
                bm.faces.new((A[k], A[k2], B[k2], B[k]))
    # hard edges where the profile turns sharply
    for i in range(n):
        if len(rings[i]) == 1:
            continue
        if loop:
            a, b, c = profile[(i - 1) % n], profile[i], profile[(i + 1) % n]
        elif 0 < i < n - 1:
            a, b, c = profile[i - 1], profile[i], profile[i + 1]
        else:
            continue
        d1 = Vector((b[0] - a[0], b[1] - a[1]))
        d2 = Vector((c[0] - b[0], c[1] - b[1]))
        if d1.length < 1e-9 or d2.length < 1e-9:
            continue
        if d1.angle(d2) > radians(sharp):
            R = rings[i]
            for k in range(seg):
                e = bm.edges.get((R[k], R[(k + 1) % seg]))
                if e:
                    e.smooth = False
    return finish(name, bm, material, loc, rot, quat, parent)


def arc(r, h, n=8, start=0.0, end=pi / 2):
    """quarter-ellipse points (r cos t, h sin t) for domes"""
    return [(r * cos(start + (end - start) * i / n), h * sin(start + (end - start) * i / n)) for i in range(n + 1)]


def dome_profile(r, h, base=0.0, n=8):
    pts = [(0, base), (r, base)]
    pts += [(p[0], base + p[1]) for p in arc(r, h, n)][1:]
    pts[-1] = (0, base + h)   # arc ends on the axis
    return pts


def sphere(name, r, loc, material, parent=None, scale=(1, 1, 1), seg=24, rings=14, rot=(0, 0, 0)):
    prof = [(r * sin(pi * i / rings), -r * cos(pi * i / rings)) for i in range(rings + 1)]
    prof[0] = (0, -r)
    prof[-1] = (0, r)
    ob = lathe(name, prof, material, loc, rot, parent=None, seg=seg, sharp=170)
    ob.scale = scale
    if parent:
        adopt(ob, parent)
    return ob


def ribbed_profile(L, r, ribs, amp, per_rib=8):
    n = ribs * per_rib
    pts = [(0, 0)]
    for i in range(n + 1):
        z = L * i / n
        pts.append((r - amp * 0.5 * (1 + cos(2 * pi * ribs * i / n)), z))
    pts.append((0, L))
    return pts


def between(p0, p1):
    d = Vector(p1) - Vector(p0)
    return d.length, d.to_track_quat('Z', 'Y')


def limb(name, p0, p1, r, material, ribs=3, amp=None, parent=None):
    L, q = between(p0, p1)
    amp = r * 0.18 if amp is None else amp
    return lathe(name, ribbed_profile(L, r, ribs, amp), material, loc=p0, quat=q, parent=parent, seg=32)


# ---------------------------------------------------------------- text
def text(name, s, size, loc, rot, material, extrude=0.0005, parent=None, ax='CENTER', ay='CENTER'):
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = s
    cu.size = size
    cu.extrude = extrude
    cu.align_x = ax
    cu.align_y = ay
    tmp = bpy.data.objects.new(name + '_tmp', cu)
    col.objects.link(tmp)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    me.name = name
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    me.materials.append(material)
    if parent:
        adopt(ob, parent)
    return ob


# ---------------------------------------------------------------- 7-segment display
SEGMENTS = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc',
            '5': 'afgcd', '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg'}


def _prism(bm, pts, y0, depth, slant_c):
    """hexagonal prism in the XZ plane at y=y0 extruded towards -Y."""
    def v(p, y):
        x, z = p
        return bm.verts.new((x + 0.14 * (z - slant_c), y, z))
    back = [v(p, y0) for p in pts]
    front = [v(p, y0 - depth) for p in pts]
    bm.faces.new(front)
    bm.faces.new(back[::-1])
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((back[i], back[j], front[j], front[i]))


def _hex(cx, cz, length, t, horizontal):
    h = length / 2
    pts = [(-h, 0), (-h + t / 2, t / 2), (h - t / 2, t / 2), (h, 0), (h - t / 2, -t / 2), (-h + t / 2, -t / 2)]
    if not horizontal:
        pts = [(z, x) for (x, z) in pts]
        pts = pts[::-1]  # keep CCW after swapping axes
    return [(cx + x, cz + z) for (x, z) in pts]


def seven_seg(string, cz, y0, w=0.013, h=0.024, t=0.0028, gap=0.0055, dot_extra=0.004):
    """returns (lit_bm, ghost_bm) built for string such as '12.50'"""
    lit, ghost = bmesh.new(), bmesh.new()
    items = []
    total = 0.0
    for ch in string:
        if ch == '.':
            items.append(('.', total - gap + 0.0032))
            total += -gap + 0.0077
        else:
            items.append((ch, total + w / 2))
            total += w + gap
    total -= gap
    x_start = -total / 2
    hl, vl = w - 0.6 * t, h / 2 - 0.6 * t
    for ch, xc in items:
        cx = x_start + xc
        if ch == '.':
            d = 0.0034
            pts = [(cx - d / 2, cz - h / 2 - d / 2), (cx + d / 2, cz - h / 2 - d / 2),
                   (cx + d / 2, cz - h / 2 + d / 2), (cx - d / 2, cz - h / 2 + d / 2)]
            _prism(lit, pts, y0, 0.0008, cz)
            continue
        lit_set = SEGMENTS[ch]
        geo = {'a': (cx, cz + h / 2, hl, True), 'g': (cx, cz, hl, True), 'd': (cx, cz - h / 2, hl, True),
               'f': (cx - w / 2, cz + h / 4, vl, False), 'b': (cx + w / 2, cz + h / 4, vl, False),
               'e': (cx - w / 2, cz - h / 4, vl, False), 'c': (cx + w / 2, cz - h / 4, vl, False)}
        for k, (sx, sz, ln, hz) in geo.items():
            pts = _hex(sx, sz, ln, t, hz)
            if k in lit_set:
                _prism(lit, pts, y0, 0.0009, cz)
            else:
                _prism(ghost, pts, y0, 0.0004, cz)
    return lit, ghost
