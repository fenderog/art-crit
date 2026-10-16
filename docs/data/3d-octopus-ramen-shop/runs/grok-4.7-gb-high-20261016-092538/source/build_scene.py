"""Stylized octopus chef at a night ramen booth. Built entirely with bpy."""

import math
import random

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

rng = random.Random(16)

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

HEAD = Vector((0.0, 0.60, 1.30))
SX, SY, SZ = 0.46, 0.40, 0.50
COUNTER_Z = 0.90
BOWL_C = Vector((-0.05, 0.34, COUNTER_Z + 0.028))
BOWL_SCALE = 1.05

# ---------------------------------------------------------------------------
# Scene reset
# ---------------------------------------------------------------------------

def purge_scene():
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in list(bpy.data.collections):
        bpy.data.collections.remove(coll)
    for datablock in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.curves,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.images,
    ):
        for block in list(datablock):
            if block.users == 0:
                datablock.remove(block)


def collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


ROOTS = {}


def make_empty(name, parent_name=None):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.12
    collection("RamenShop").objects.link(obj)
    if parent_name is not None:
        obj.parent = ROOTS[parent_name]
    ROOTS[name] = obj
    return obj


# ---------------------------------------------------------------------------
# Materials (sRGB inputs converted to linear)
# ---------------------------------------------------------------------------

def srgb(c):
    def f(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4

    return tuple(f(x) for x in c)


def new_mat(name, color, rough=0.5, metal=0.0, emit=None, emit_str=0.0, coat=0.0, spec=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    col = srgb(color)
    bsdf.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit is not None:
        em = srgb(emit)
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (em[0], em[1], em[2], 1.0)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emit_str
    if coat and "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = coat
        if "Coat Roughness" in bsdf.inputs:
            bsdf.inputs["Coat Roughness"].default_value = 0.18
    if spec is not None and "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = spec
    return mat


MATS = {}


def M(key):
    return MATS[key]


def build_materials():
    pairs = {
        "skin": dict(color=(0.96, 0.58, 0.46), rough=0.42, coat=0.22),
        "belly": dict(color=(0.99, 0.78, 0.70), rough=0.4, coat=0.18),
        "spot": dict(color=(0.82, 0.40, 0.34), rough=0.48),
        "sucker": dict(color=(0.99, 0.80, 0.74), rough=0.35, coat=0.3),
        "sucker_in": dict(color=(0.86, 0.48, 0.55), rough=0.32, coat=0.25),
        "eye_white": dict(color=(0.97, 0.97, 0.96), rough=0.12, coat=0.55),
        "iris": dict(color=(0.28, 0.14, 0.09), rough=0.22, coat=0.4),
        "pupil": dict(color=(0.02, 0.015, 0.018), rough=0.25),
        "highlight": dict(color=(1, 1, 1), rough=0.1, emit=(1, 1, 1), emit_str=2.2),
        "blush": dict(color=(0.95, 0.55, 0.58), rough=0.55),
        "mouth": dict(color=(0.55, 0.16, 0.22), rough=0.4),
        "mouth_in": dict(color=(0.28, 0.07, 0.10), rough=0.55),
        "hat": dict(color=(0.97, 0.95, 0.91), rough=0.72),
        "hat_band": dict(color=(0.93, 0.90, 0.84), rough=0.65),
        "scarf": dict(color=(0.78, 0.16, 0.16), rough=0.48),
        "apron": dict(color=(0.95, 0.94, 0.90), rough=0.68),
        "apron_trim": dict(color=(0.75, 0.18, 0.18), rough=0.5),
        "wood": dict(color=(0.72, 0.46, 0.26), rough=0.62),
        "wood_dark": dict(color=(0.48, 0.29, 0.16), rough=0.58),
        "wood_lite": dict(color=(0.82, 0.60, 0.36), rough=0.55),
        "plank_a": dict(color=(0.62, 0.40, 0.24), rough=0.7),
        "plank_b": dict(color=(0.54, 0.34, 0.20), rough=0.72),
        "plaster": dict(color=(0.90, 0.82, 0.70), rough=0.85),
        "trim": dict(color=(0.36, 0.20, 0.12), rough=0.5),
        "noren": dict(color=(0.13, 0.22, 0.48), rough=0.62),
        "noren_red": dict(color=(0.72, 0.12, 0.14), rough=0.55),
        "paper": dict(color=(0.96, 0.93, 0.86), rough=0.7),
        "ink": dict(color=(0.12, 0.07, 0.05), rough=0.45),
        "awning_red": dict(color=(0.75, 0.14, 0.13), rough=0.6),
        "awning_cream": dict(color=(0.94, 0.88, 0.76), rough=0.62),
        "lantern": dict(color=(1.0, 0.42, 0.12), rough=0.35, emit=(1.0, 0.45, 0.14), emit_str=6.0),
        "lantern_dark": dict(color=(0.08, 0.05, 0.04), rough=0.4),
        "metal": dict(color=(0.72, 0.70, 0.66), rough=0.28, metal=1.0),
        "metal_dark": dict(color=(0.35, 0.33, 0.32), rough=0.35, metal=1.0),
        "pot": dict(color=(0.55, 0.52, 0.48), rough=0.32, metal=0.85),
        "ceramic": dict(color=(0.96, 0.93, 0.88), rough=0.28, coat=0.45),
        "cobalt": dict(color=(0.16, 0.28, 0.62), rough=0.32, coat=0.35),
        "broth": dict(color=(0.78, 0.42, 0.12), rough=0.14, coat=0.65, spec=0.6),
        "oil": dict(color=(0.95, 0.72, 0.22), rough=0.08, coat=0.8),
        "noodle": dict(color=(0.96, 0.86, 0.58), rough=0.38, coat=0.25),
        "egg": dict(color=(0.97, 0.94, 0.86), rough=0.35, coat=0.2),
        "yolk": dict(color=(0.95, 0.62, 0.08), rough=0.22, coat=0.55),
        "chashu": dict(color=(0.72, 0.36, 0.26), rough=0.42, coat=0.28),
        "fat": dict(color=(0.95, 0.78, 0.66), rough=0.4, coat=0.2),
        "nori": dict(color=(0.08, 0.18, 0.13), rough=0.45, coat=0.15),
        "scallion": dict(color=(0.25, 0.62, 0.28), rough=0.5),
        "scallion_w": dict(color=(0.93, 0.92, 0.82), rough=0.5),
        "naruto": dict(color=(0.96, 0.94, 0.90), rough=0.4),
        "naruto_pink": dict(color=(0.90, 0.38, 0.52), rough=0.38),
        "menma": dict(color=(0.93, 0.78, 0.42), rough=0.45),
        "steam": dict(color=(0.95, 0.93, 0.90), rough=0.9, emit=(1, 0.96, 0.90), emit_str=0.55),
        "cushion": dict(color=(0.70, 0.12, 0.14), rough=0.55),
        "tea": dict(color=(0.45, 0.28, 0.12), rough=0.18, coat=0.4),
        "glass": dict(color=(0.85, 0.92, 0.9), rough=0.08, coat=0.3, spec=0.5),
        "chili": dict(color=(0.72, 0.12, 0.08), rough=0.3, coat=0.35),
        "soy": dict(color=(0.18, 0.10, 0.06), rough=0.25, coat=0.3),
        "stone": dict(color=(0.42, 0.40, 0.38), rough=0.85),
        "sign_letters": dict(color=(0.98, 0.94, 0.86), rough=0.45),
        "knife_handle": dict(color=(0.35, 0.18, 0.10), rough=0.45),
    }
    for name, kw in pairs.items():
        MATS[name] = new_mat(name, **kw)


# ---------------------------------------------------------------------------
# Mesh helpers
# ---------------------------------------------------------------------------

def finish(name, bm, mat, col_name, parent_name, smooth=True):
    bm.normal_update()
    if len(bm.faces):
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.validate(verbose=False)
    mesh.update()
    if mesh.polygons:
        mesh.polygons.foreach_set("use_smooth", [smooth] * len(mesh.polygons))
    obj = bpy.data.objects.new(name, mesh)
    if mat is not None:
        if isinstance(mat, (list, tuple)):
            for m in mat:
                obj.data.materials.append(m)
        else:
            obj.data.materials.append(mat)
    collection(col_name).objects.link(obj)
    if parent_name is not None:
        obj.parent = ROOTS[parent_name]
    return obj


def transform_bm(bm, matrix):
    bm.verts.ensure_lookup_table()
    bmesh.ops.transform(bm, matrix=matrix, verts=list(bm.verts))


def track_z(direction):
    return direction.to_track_quat("Z", "Y").to_matrix().to_4x4()


def uv_sphere(name, radius, loc, mat, col, parent, scale=(1, 1, 1), u=32, v=16, smooth=True, rot=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=radius)
    for vert in bm.verts:
        vert.co.x *= scale[0]
        vert.co.y *= scale[1]
        vert.co.z *= scale[2]
    matrix = Matrix.Translation(Vector(loc))
    if rot is not None:
        matrix = matrix @ rot.to_matrix().to_4x4()
    transform_bm(bm, matrix)
    return finish(name, bm, mat, col, parent, smooth)


def cylinder(name, p0, p1, radius, mat, col, parent, segs=16, smooth=True, r1=None, r2=None):
    p0 = Vector(p0)
    p1 = Vector(p1)
    direction = p1 - p0
    length = direction.length
    if length < 1e-6:
        return None
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segs,
        radius1=radius if r1 is None else r1,
        radius2=radius if r2 is None else r2,
        depth=length,
    )
    matrix = Matrix.Translation((p0 + p1) / 2.0) @ track_z(direction)
    transform_bm(bm, matrix)
    return finish(name, bm, mat, col, parent, smooth)


def box(name, loc, size, mat, col, parent, rot=None, smooth=False):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for vert in bm.verts:
        vert.co.x *= size[0]
        vert.co.y *= size[1]
        vert.co.z *= size[2]
    matrix = Matrix.Translation(Vector(loc))
    if rot is not None:
        matrix = matrix @ rot.to_matrix().to_4x4()
    transform_bm(bm, matrix)
    return finish(name, bm, mat, col, parent, smooth)


def torus(name, major, minor, loc, mat, col, parent, rot=None, major_seg=28, minor_seg=10):
    bm = bmesh.new()
    rings = []
    for i in range(major_seg):
        ang = 2.0 * math.pi * i / major_seg
        ca, sa = math.cos(ang), math.sin(ang)
        ring = []
        for j in range(minor_seg):
            bang = 2.0 * math.pi * j / minor_seg
            rad = major + minor * math.cos(bang)
            z = minor * math.sin(bang)
            ring.append(bm.verts.new((rad * ca, rad * sa, z)))
        rings.append(ring)
    for i in range(major_seg):
        i2 = (i + 1) % major_seg
        for j in range(minor_seg):
            j2 = (j + 1) % minor_seg
            bm.faces.new((rings[i][j], rings[i2][j], rings[i2][j2], rings[i][j2]))
    matrix = Matrix.Translation(Vector(loc))
    if rot is not None:
        matrix = matrix @ rot.to_matrix().to_4x4()
    transform_bm(bm, matrix)
    return finish(name, bm, mat, col, parent, True)


def lathe(name, profile, mat, col, parent, loc=(0, 0, 0), segments=40, scale=1.0, rot=None, smooth=True):
    bm = bmesh.new()
    rings = []
    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        ca, sa = math.cos(ang), math.sin(ang)
        ring = []
        for radius, z in profile:
            ring.append(bm.verts.new((radius * ca, radius * sa, z)))
        rings.append(ring)
    n = len(profile)
    for i in range(segments):
        i2 = (i + 1) % segments
        for j in range(n - 1):
            bm.faces.new((rings[i][j], rings[i2][j], rings[i2][j + 1], rings[i][j + 1]))
    matrix = Matrix.Translation(Vector(loc))
    if rot is not None:
        matrix = matrix @ rot.to_matrix().to_4x4()
    if scale != 1.0:
        matrix = matrix @ Matrix.Diagonal((scale, scale, scale, 1.0))
    transform_bm(bm, matrix)
    return finish(name, bm, mat, col, parent, smooth)


def hemisphere(name, radius, loc, mat, col, parent, direction="UP", u=28, v=14, scale=(1, 1, 1), rot_extra=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=radius)
    bm.faces.ensure_lookup_table()
    doomed = [f for f in bm.faces if f.calc_center_median().z < -1e-5]
    if doomed:
        bmesh.ops.delete(bm, geom=doomed, context="FACES")
    boundary = [e for e in bm.edges if e.is_boundary]
    if boundary:
        bmesh.ops.holes_fill(bm, edges=boundary, sides=0)
    for vert in bm.verts:
        if direction == "DOWN":
            vert.co.z *= -1
        vert.co.x *= scale[0]
        vert.co.y *= scale[1]
        vert.co.z *= scale[2]
    matrix = Matrix.Translation(Vector(loc))
    if rot_extra is not None:
        matrix = matrix @ rot_extra.to_matrix().to_4x4()
    transform_bm(bm, matrix)
    return finish(name, bm, mat, col, parent, True)


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def shape_unit(p):
    """Deform a unit-sphere point into the mantle. Shared by mesh and sockets."""
    p = Vector(p).normalized()
    z = p.z
    t = smoothstep((z + 0.9) / 1.55)
    k = 0.56 + 0.44 * t
    p.x *= k
    p.y *= k * (1.10 if p.y < 0.0 else 0.90)
    if z > 0.15:
        p.z += 0.08 * (z - 0.15)
    return p


def mantle_point(direction, lift=0.0):
    p = shape_unit(direction)
    p.x = p.x * SX
    p.y = p.y * SY
    p.z = p.z * SZ
    if lift:
        p += Vector(direction).normalized() * lift
    return HEAD + p


def catmull(points, samples_per_seg=8):
    pts = [Vector(p) for p in points]
    if len(pts) < 2:
        return pts
    ext = [pts[0] * 2.0 - pts[1]] + pts + [pts[-1] * 2.0 - pts[-2]]
    out = []
    segs = len(pts) - 1
    for i in range(segs):
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        steps = samples_per_seg if i < segs - 1 else samples_per_seg + 1
        for s in range(steps):
            t = s / samples_per_seg
            t2 = t * t
            t3 = t2 * t
            q = 0.5 * (
                (2.0 * p1)
                + (-p0 + p2) * t
                + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2
                + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3
            )
            out.append(q)
    return out


def tube(name, points, rad0, rad1, mat, col, parent, sides=12, lumps=0.0, seed=0.0):
    pts = [Vector(p) for p in points]
    frames_t = []
    frames_n = []
    frames_b = []
    t0 = (pts[1] - pts[0]).normalized()
    up = Vector((0.0, 0.0, 1.0))
    if abs(t0.dot(up)) > 0.85:
        up = Vector((0.0, 1.0, 0.0))
    n0 = t0.cross(up).normalized()
    b0 = t0.cross(n0).normalized()
    frames_t.append(t0)
    frames_n.append(n0)
    frames_b.append(b0)
    for i in range(1, len(pts)):
        nxt = pts[min(i + 1, len(pts) - 1)]
        prv = pts[i - 1]
        tangent = (nxt - prv)
        if tangent.length < 1e-8:
            tangent = frames_t[-1].copy()
        tangent.normalize()
        prev_t = frames_t[-1]
        axis = prev_t.cross(tangent)
        if axis.length > 1e-6:
            axis.normalize()
            ang = prev_t.angle(tangent)
            rot = Matrix.Rotation(ang, 3, axis)
            normal = rot @ frames_n[-1]
        else:
            normal = frames_n[-1].copy()
        normal = (normal - tangent * normal.dot(tangent))
        if normal.length < 1e-6:
            normal = frames_n[-1].copy()
        normal.normalize()
        bitangent = tangent.cross(normal).normalized()
        frames_t.append(tangent)
        frames_n.append(normal)
        frames_b.append(bitangent)

    def radius_at(t):
        base = rad1 + (rad0 - rad1) * ((1.0 - t) ** 1.25)
        if lumps:
            base *= 1.0 + lumps * math.sin(t * 22.0 + seed)
        return max(0.006, base)

    bm = bmesh.new()
    rings = []
    last = len(pts) - 1
    for i, p in enumerate(pts):
        t = i / last
        r = radius_at(t)
        normal = frames_n[i]
        bitangent = frames_b[i]
        ring = []
        for s in range(sides):
            ang = 2.0 * math.pi * s / sides
            pos = p + (normal * math.cos(ang) + bitangent * math.sin(ang)) * r
            ring.append(bm.verts.new(pos))
        rings.append(ring)
    for i in range(last):
        for s in range(sides):
            s2 = (s + 1) % sides
            bm.faces.new((rings[i][s], rings[i][s2], rings[i + 1][s2], rings[i + 1][s]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    obj = finish(name, bm, mat, col, parent, True)
    return obj, pts, frames_t, frames_n, frames_b, radius_at


def add_suckers(name, pts, frames_t, radius_at, prefer, mat_out, mat_in, col, parent, count=7):
    """Flattened discs along the belly of a tentacle. One mesh, two materials."""
    bm = bmesh.new()
    last = len(pts) - 1
    prefer = Vector(prefer)
    made = 0
    for k in range(count):
        t = 0.14 + 0.78 * (k / max(1, count - 1))
        idx = min(last, max(0, int(round(t * last))))
        tangent = frames_t[idx]
        belly = prefer - tangent * prefer.dot(tangent)
        if belly.length < 1e-4:
            belly = Vector((0.0, 0.0, -1.0))
            belly = belly - tangent * belly.dot(tangent)
        if belly.length < 1e-4:
            continue
        belly.normalize()
        r = radius_at(t)
        center = pts[idx] + belly * (r * 0.86)
        tmp = Vector((0.0, 0.0, 1.0)) if abs(belly.z) < 0.9 else Vector((1.0, 0.0, 0.0))
        x_axis = belly.cross(tmp).normalized()
        y_axis = belly.cross(x_axis).normalized()
        cup_r = r * 0.78
        for which, rad, push, mat_index in (
            (0, cup_r, r * 0.02, 0),
            (1, cup_r * 0.48, r * 0.10, 1),
        ):
            local = bmesh.new()
            bmesh.ops.create_uvsphere(local, u_segments=12, v_segments=8, radius=rad)
            vert_map = []
            for vert in local.verts:
                flattened = Vector((vert.co.x, vert.co.y, vert.co.z * 0.32))
                world = center + x_axis * flattened.x + y_axis * flattened.y + belly * (flattened.z + push)
                vert_map.append(bm.verts.new(world))
            local.faces.ensure_lookup_table()
            local.verts.ensure_lookup_table()
            index = {v: i for i, v in enumerate(local.verts)}
            for face in local.faces:
                try:
                    nf = bm.faces.new([vert_map[index[v]] for v in face.verts])
                    nf.material_index = mat_index
                except ValueError:
                    pass
            local.free()
        made += 1
    if made == 0:
        bm.free()
        return None
    return finish(name, bm, (mat_out, mat_in), col, parent, True)


def arc_tube(name, center, normal, x_axis, radius, tube_r, a0, a1, mat, col, parent, n=10):
    normal = Vector(normal).normalized()
    x_axis = Vector(x_axis).normalized()
    y_axis = normal.cross(x_axis).normalized()
    pts = []
    for i in range(n):
        t = i / (n - 1)
        ang = a0 + (a1 - a0) * t
        pts.append(center + x_axis * (math.cos(ang) * radius) + y_axis * (math.sin(ang) * radius))
    obj, *_ = tube(name, pts, tube_r, tube_r, mat, col, parent, sides=8)
    return obj


# ---------------------------------------------------------------------------
# Octopus
# ---------------------------------------------------------------------------

def build_octopus():
    col = "Octopus"
    parent = "OctopusChef"

    # Mantle
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=32, radius=1.0)
    for vert in bm.verts:
        p = shape_unit(vert.co)
        vert.co = Vector((p.x * SX, p.y * SY, p.z * SZ)) + HEAD
    finish("Mantle", bm, M("skin"), col, parent, True)

    # Paler underside
    belly_at = mantle_point((0.0, -0.55, -0.72), lift=0.01)
    uv_sphere(
        "Belly",
        0.20,
        belly_at,
        M("belly"),
        col,
        parent,
        scale=(1.15, 0.72, 0.85),
        u=28,
        v=16,
    )

    # Spots
    spot_dirs = [
        (0.95, -0.15, 0.45),
        (-1.05, -0.05, 0.50),
        (0.45, 0.25, 0.85),
        (-0.35, 0.40, 0.70),
        (1.05, -0.20, -0.15),
        (-0.95, 0.20, -0.05),
    ]
    for i, d in enumerate(spot_dirs):
        pos = mantle_point(d, lift=0.012)
        scl = 0.045 + (i % 3) * 0.012
        uv_sphere(
            f"Spot_{i}",
            scl,
            pos,
            M("spot"),
            col,
            parent,
            scale=(1.0, 0.55, 0.85),
            u=12,
            v=8,
        )

    # Eyes bedded into the front of the mantle, both looking down into the bowl.
    eye_dirs = [Vector((0.38, -1.0, 0.22)), Vector((-0.38, -1.0, 0.22))]
    bowl_look = BOWL_C + Vector((0.0, -0.02, 0.18))
    for i, d in enumerate(eye_dirs):
        side = "L" if d.x > 0 else "R"
        outward = Vector(d).normalized()
        # Bulge the eye out of the head so the iris sits on the visible front.
        center = mantle_point(d, lift=0.01) + outward * 0.03
        eye_r = 0.094
        uv_sphere(f"EyeWhite_{side}", eye_r, center, M("eye_white"), col, parent, u=28, v=16)
        inward_x = -0.72 if d.x > 0 else 0.72
        gaze = (outward * 1.15 + Vector((inward_x, -0.02, -0.5))).normalized()
        uv_sphere(f"Iris_{side}", 0.056, center + gaze * 0.048, M("iris"), col, parent, u=20, v=12)
        uv_sphere(f"Pupil_{side}", 0.034, center + gaze * 0.066, M("pupil"), col, parent, u=16, v=10)
        catch_dir = (outward + Vector((-0.45, -0.05, 0.7))).normalized()
        uv_sphere(f"Catch_{side}", 0.018, center + catch_dir * 0.082, M("highlight"), col, parent, u=10, v=8)
        # blush
        blush_at = mantle_point((d.x * 1.15, -0.95, -0.22), lift=0.008)
        uv_sphere(
            f"Blush_{side}",
            0.055,
            blush_at,
            M("blush"),
            col,
            parent,
            scale=(1.2, 0.45, 0.7),
            u=14,
            v=8,
        )

    # Small open smile, high enough to clear the bowl and the tentacles.
    mouth_c = mantle_point((0.0, -1.0, -0.02), lift=0.012)
    arc_tube(
        "Smile",
        mouth_c,
        Vector((0.0, -1.0, 0.15)),
        Vector((1.0, 0.0, 0.0)),
        0.055,
        0.012,
        math.radians(210),
        math.radians(330),
        M("mouth"),
        col,
        parent,
        n=10,
    )
    uv_sphere(
        "MouthInner",
        0.028,
        mouth_c + Vector((0.0, 0.012, -0.008)),
        M("mouth_in"),
        col,
        parent,
        scale=(1.05, 0.45, 0.62),
        u=14,
        v=8,
    )

    # Hat — toque planted on the crown, tipped forward and a little to the side
    crown = mantle_point((0.0, -0.08, 1.0), lift=0.0)
    hat_pivot = crown + Vector((0.0, 0.0, -0.02))
    tilt = Euler((math.radians(11), math.radians(-13), math.radians(5)), "XYZ").to_matrix().to_4x4()
    hat_xf = Matrix.Translation(hat_pivot) @ tilt @ Matrix.Translation(-hat_pivot)

    # brim
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=32, radius1=0.32, radius2=0.32, depth=0.04
    )
    transform_bm(bm, Matrix.Translation(hat_pivot + Vector((0, 0, 0.02))))
    transform_bm(bm, hat_xf)
    finish("HatBrim", bm, M("hat"), col, parent, True)

    # pleated crown — short, so the toque clears the awning
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=40, radius1=0.23, radius2=0.25, depth=0.26
    )
    for vert in bm.verts:
        ang = math.atan2(vert.co.y, vert.co.x)
        rad = math.hypot(vert.co.x, vert.co.y)
        if rad > 1e-4:
            height_t = (vert.co.z + 0.13) / 0.26
            amp = 0.010 + 0.010 * max(0.0, height_t)
            nr = rad + amp * math.cos(ang * 10.0)
            vert.co.x = math.cos(ang) * nr
            vert.co.y = math.sin(ang) * nr
    transform_bm(bm, Matrix.Translation(hat_pivot + Vector((0, 0, 0.17))))
    transform_bm(bm, hat_xf)
    finish("HatCrown", bm, M("hat"), col, parent, True)

    # soft top
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=0.24)
    for vert in bm.verts:
        vert.co.z *= 0.5
    transform_bm(bm, Matrix.Translation(hat_pivot + Vector((0, 0, 0.30))))
    transform_bm(bm, hat_xf)
    finish("HatTop", bm, M("hat"), col, parent, True)

    # red band at the brim
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=28, radius1=0.325, radius2=0.325, depth=0.026
    )
    transform_bm(bm, Matrix.Translation(hat_pivot + Vector((0, 0, 0.055))))
    transform_bm(bm, hat_xf)
    finish("HatRibbon", bm, M("scarf"), col, parent, True)

    # Bandana wrapped across the front of the mantle, not a ring through the head.
    scarf_z = HEAD.z - 0.20
    scarf_pts = []
    for i in range(16):
        t = i / 15.0
        ang = math.radians(205 + t * 130)
        scarf_pts.append(
            (
                math.cos(ang) * 0.30,
                HEAD.y - 0.06 + math.sin(ang) * 0.10,
                scarf_z + math.sin(t * math.pi) * 0.02,
            )
        )
    tube("Scarf", scarf_pts, 0.026, 0.020, M("scarf"), col, parent, sides=8)
    knot = mantle_point((0.0, -1.0, -0.42), lift=0.02)
    uv_sphere("ScarfKnot", 0.038, knot, M("scarf"), col, parent, scale=(0.85, 0.7, 0.75), u=14, v=10)
    for sx, nm in ((-0.028, "A"), (0.030, "B")):
        box(
            f"ScarfTail_{nm}",
            (knot.x + sx, knot.y - 0.008, knot.z - 0.055),
            (0.032, 0.01, 0.08),
            M("scarf"),
            col,
            parent,
            rot=Euler((math.radians(16), math.radians(10 if sx > 0 else -10), 0), "XYZ"),
        )

    # Apron bib
    bib_c = mantle_point((0.0, -1.0, -0.72), lift=0.035)
    box(
        "Apron",
        (bib_c.x, bib_c.y, bib_c.z - 0.02),
        (0.34, 0.02, 0.30),
        M("apron"),
        col,
        parent,
        rot=Euler((math.radians(8), 0, 0), "XYZ"),
    )
    box(
        "ApronPocket",
        (bib_c.x, bib_c.y - 0.012, bib_c.z - 0.08),
        (0.14, 0.018, 0.09),
        M("apron"),
        col,
        parent,
    )
    # little red bowl mark on the pocket
    uv_sphere(
        "ApronMark",
        0.028,
        (bib_c.x, bib_c.y - 0.02, bib_c.z - 0.08),
        M("apron_trim"),
        col,
        parent,
        scale=(1.0, 0.35, 1.0),
        u=12,
        v=8,
    )
    build_tentacles()


def build_tentacles():
    col = "Octopus"
    parent = "OctopusChef"
    # Each tentacle starts tucked under the mantle.
    under = HEAD + Vector((0.0, 0.02, -0.30))

    def root(dx, dy):
        return under + Vector((dx, dy, 0.0))

    specs = [
        # name, controls, rad0, rad1, sucker preferred direction, count, lumps
        (
            "Wave",
            [
                root(-0.10, -0.02),
                Vector((-0.22, 0.42, 1.06)),
                Vector((-0.42, 0.22, 1.20)),
                Vector((-0.64, 0.02, 1.36)),
                Vector((-0.82, -0.16, 1.50)),
                Vector((-0.90, -0.32, 1.56)),
                Vector((-0.74, -0.40, 1.48)),
                Vector((-0.60, -0.30, 1.36)),
            ],
            0.058,
            0.014,
            Vector((0.0, -1.0, -0.15)),
            8,
        ),
        (
            "Chopsticks",
            [
                root(-0.16, -0.06),
                Vector((-0.28, 0.40, 1.02)),
                Vector((-0.32, 0.32, 1.10)),
                Vector((-0.22, 0.28, 1.18)),
                Vector((-0.12, 0.30, 1.24)),
            ],
            0.052,
            0.016,
            Vector((0.0, -0.4, -1.0)),
            6,
        ),
        (
            "Ladle",
            [
                root(0.16, -0.04),
                Vector((0.30, 0.46, 1.00)),
                Vector((0.34, 0.36, 1.06)),
                Vector((0.22, 0.32, 1.14)),
                Vector((0.14, 0.34, 1.18)),
            ],
            0.052,
            0.016,
            Vector((0.0, -0.3, -1.0)),
            6,
        ),
        (
            "DrapeL",
            [
                root(-0.20, 0.02),
                Vector((-0.38, 0.42, 0.97)),
                Vector((-0.54, 0.28, 0.94)),
                Vector((-0.60, 0.12, 0.915)),
                Vector((-0.52, 0.02, 0.84)),
                Vector((-0.42, -0.02, 0.74)),
                Vector((-0.34, 0.04, 0.78)),
            ],
            0.060,
            0.016,
            Vector((0.0, -1.0, -0.25)),
            8,
        ),
        (
            "DrapeR",
            [
                root(0.20, 0.04),
                Vector((0.42, 0.46, 0.97)),
                Vector((0.66, 0.32, 0.935)),
                Vector((0.80, 0.16, 0.915)),
                Vector((0.74, 0.04, 0.82)),
                Vector((0.62, 0.02, 0.72)),
                Vector((0.54, 0.08, 0.77)),
            ],
            0.058,
            0.015,
            Vector((0.2, -1.0, -0.2)),
            7,
        ),
        (
            "Coil",
            [
                root(0.08, 0.10),
                Vector((0.28, 0.72, 0.98)),
                Vector((0.52, 0.82, 0.95)),
                Vector((0.66, 0.68, 0.93)),
                Vector((0.52, 0.58, 0.925)),
                Vector((0.40, 0.68, 0.95)),
            ],
            0.048,
            0.018,
            Vector((0.0, 0.0, -1.0)),
            5,
        ),
        (
            "HugBowl",
            [
                root(-0.02, -0.08),
                Vector((-0.06, 0.46, 0.98)),
                Vector((-0.08, 0.40, 0.95)),
                Vector((-0.12, 0.36, 0.98)),
                Vector((-0.16, 0.33, 1.02)),
            ],
            0.050,
            0.022,
            Vector((0.0, -1.0, 0.2)),
            5,
        ),
        (
            "Back",
            [
                root(0.06, 0.12),
                Vector((0.22, 0.86, 1.05)),
                Vector((0.40, 0.98, 1.22)),
                Vector((0.30, 1.08, 1.36)),
                Vector((0.12, 1.02, 1.30)),
            ],
            0.046,
            0.014,
            Vector((0.0, 1.0, -0.2)),
            5,
        ),
    ]

    tips = {}
    for name, controls, rad0, rad1, prefer, count in specs:
        sampled = catmull(controls, samples_per_seg=7)
        obj, pts, frames_t, frames_n, frames_b, radius_at = tube(
            f"Tentacle_{name}",
            sampled,
            rad0,
            rad1,
            M("skin"),
            col,
            parent,
            sides=12,
            lumps=0.045,
            seed=hash(name) % 7,
        )
        add_suckers(
            f"Suckers_{name}",
            pts,
            frames_t,
            radius_at,
            prefer,
            M("sucker"),
            M("sucker_in"),
            col,
            parent,
            count=count,
        )
        tips[name] = pts[-1]
    return tips


# ---------------------------------------------------------------------------
# Booth
# ---------------------------------------------------------------------------

def build_booth():
    col = "Booth"
    parent = "RamenBooth"

    # Floor — interior planks plus a stone apron in front
    bm = bmesh.new()

    def append_box(bm, loc, size, mat_index):
        tmp = bmesh.new()
        bmesh.ops.create_cube(tmp, size=1.0)
        for vert in tmp.verts:
            vert.co.x = vert.co.x * size[0] + loc[0]
            vert.co.y = vert.co.y * size[1] + loc[1]
            vert.co.z = vert.co.z * size[2] + loc[2]
        tmp.verts.ensure_lookup_table()
        tmp.faces.ensure_lookup_table()
        mapping = [bm.verts.new(v.co) for v in tmp.verts]
        index = {v: i for i, v in enumerate(tmp.verts)}
        for face in tmp.faces:
            nf = bm.faces.new([mapping[index[v]] for v in face.verts])
            nf.material_index = mat_index
        tmp.free()

    # wooden deck
    x = -1.28
    i = 0
    while x < 1.28:
        w = 0.18
        append_box(bm, (x + w / 2, 0.35, 0.04), (w - 0.008, 2.15, 0.08), i % 2)
        x += w
        i += 1
    floor = finish("FloorPlanks", bm, (M("plank_a"), M("plank_b")), col, parent, False)

    # stone threshold toward the customer
    box("Threshold", (0.0, -0.85, 0.025), (2.7, 0.55, 0.05), M("stone"), col, parent)

    # Counter carcass
    box("CounterBody", (0.0, 0.55, 0.50), (2.05, 0.78, 0.78), M("wood_dark"), col, parent)
    box("CounterTop", (0.0, 0.50, COUNTER_Z - 0.025), (2.22, 0.96, 0.06), M("wood"), col, parent)
    # front lip highlight
    box("CounterLip", (0.0, 0.035, COUNTER_Z - 0.01), (2.22, 0.03, 0.09), M("wood_lite"), col, parent)
    # inset front panel and vertical battens so the front isn't one blank plane
    box("CounterPanel", (0.0, 0.175, 0.48), (1.7, 0.02, 0.52), M("wood"), col, parent)
    for i, x in enumerate((-0.78, -0.39, 0.0, 0.39, 0.78)):
        box(f"Batten_{i}", (x, 0.155, 0.48), (0.035, 0.03, 0.64), M("trim"), col, parent)
    # toe kick
    box("ToeKick", (0.0, 0.22, 0.06), (1.9, 0.70, 0.08), M("trim"), col, parent)

    # Posts
    for sx in (-1.12, 1.12):
        for sy, tag in ((-0.02, "F"), (1.22, "B")):
            cylinder(
                f"Post_{tag}_{'L' if sx < 0 else 'R'}",
                (sx, sy, 0.0),
                (sx, sy, 2.62),
                0.045,
                M("wood_dark"),
                col,
                parent,
                segs=12,
            )

    # Back wall, wide enough that the hero view doesn't fall off into the void
    box("BackWall", (0.0, 1.32, 1.30), (4.4, 0.08, 2.60), M("plaster"), col, parent)
    # Wings close the night gap on either side of the hero view
    box("WingL", (-1.95, 0.55, 1.25), (0.08, 1.7, 2.5), M("plaster"), col, parent)
    box("WingR", (1.95, 0.55, 1.25), (0.08, 1.7, 2.5), M("plaster"), col, parent)
    box("BackTrimTop", (0.0, 1.28, 2.55), (3.45, 0.10, 0.08), M("trim"), col, parent)
    box("BackTrimBottom", (0.0, 1.28, 0.10), (2.4, 0.10, 0.16), M("trim"), col, parent)
    # wood wainscot
    box("Wainscot", (0.0, 1.27, 0.55), (2.2, 0.04, 0.85), M("wood_dark"), col, parent)

    # Low side walls
    for sx, tag in ((-1.18, "L"), (1.18, "R")):
        box(f"SideWall_{tag}", (sx, 0.62, 0.55), (0.06, 1.15, 1.05), M("plaster"), col, parent)
        box(f"SideTrim_{tag}", (sx, 0.62, 1.05), (0.08, 1.18, 0.06), M("trim"), col, parent)

    # Awning stripes, sagging toward the street
    stripe_w = 2.30 / 8.0
    for i in range(8):
        x = -1.15 + stripe_w * (i + 0.5)
        mat = M("awning_red") if i % 2 == 0 else M("awning_cream")
        # a sagging sheet as a bent grid
        bm = bmesh.new()
        segs_y = 8
        grid = []
        for iy in range(segs_y + 1):
            ty = iy / segs_y
            y = 1.25 + (-0.20 - 1.25) * ty
            sag = math.sin(ty * math.pi) * 0.045
            z = 2.58 + (2.40 - 2.58) * ty - sag
            row = []
            for ix, fx in ((0, -0.5), (1, 0.5)):
                row.append(bm.verts.new((x + fx * (stripe_w - 0.01), y, z)))
            grid.append(row)
        for iy in range(segs_y):
            bm.faces.new((grid[iy][0], grid[iy][1], grid[iy + 1][1], grid[iy + 1][0]))
        # thickness
        extruded = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
        verts = [g for g in extruded["geom"] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=verts, vec=(0.0, 0.0, 0.015))
        finish(f"Awning_{i}", bm, mat, col, parent, False)

    # Valance flaps under the front lip
    for i in range(8):
        x = -1.15 + stripe_w * (i + 0.5)
        mat = M("awning_cream") if i % 2 == 0 else M("awning_red")
        # short hanging cloth with a little wave
        bm = bmesh.new()
        top = 2.32
        h = 0.16
        w = stripe_w * 0.78
        segs = 4
        grid = []
        for iz in range(segs + 1):
            tz = iz / segs
            z = top - h * tz
            wave = math.sin(tz * math.pi) * 0.02
            row = [
                bm.verts.new((x - w / 2, -0.20 - wave, z)),
                bm.verts.new((x + w / 2, -0.20 - wave, z)),
            ]
            grid.append(row)
        for iz in range(segs):
            bm.faces.new((grid[iz][0], grid[iz][1], grid[iz + 1][1], grid[iz + 1][0]))
        extruded = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
        verts = [g for g in extruded["geom"] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=verts, vec=(0.0, -0.008, 0.0))
        finish(f"Valance_{i}", bm, mat, col, parent, False)

    # Noren rod
    cylinder(
        "NorenRod",
        (-1.08, -0.02, 1.84),
        (1.08, -0.02, 1.84),
        0.018,
        M("trim"),
        col,
        parent,
        segs=10,
    )

    # Noren panels — wide center opening so the chef's face reads
    panels = [
        (-0.96, 0.26),
        (-0.66, 0.24),
        (0.66, 0.24),
        (0.96, 0.26),
    ]
    for i, (cx, w) in enumerate(panels):
        bm = bmesh.new()
        top = 1.82
        h = 0.46
        segs = 8
        grid = []
        for iz in range(segs + 1):
            tz = iz / segs
            z = top - h * tz
            # cloth bow
            wave = math.sin(tz * math.pi) * 0.035
            side = math.sin(tz * math.pi * 2.0) * 0.01
            row = [
                bm.verts.new((cx - w / 2, -0.03 - wave, z)),
                bm.verts.new((cx + w / 2, -0.03 - wave + side, z)),
            ]
            grid.append(row)
        for iz in range(segs):
            bm.faces.new((grid[iz][0], grid[iz][1], grid[iz + 1][1], grid[iz + 1][0]))
        extruded = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
        verts = [g for g in extruded["geom"] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=verts, vec=(0.0, -0.01, 0.0))
        finish(f"Noren_{i}", bm, M("noren"), col, parent, True)
        # red hem
        box(
            f"NorenHem_{i}",
            (cx, -0.045, top - h + 0.02),
            (w * 0.96, 0.012, 0.045),
            M("noren_red"),
            col,
            parent,
        )
        # white mon
        uv_sphere(
            f"Mon_{i}",
            0.055,
            (cx, -0.055, top - 0.16),
            M("paper"),
            col,
            parent,
            scale=(1.0, 0.28, 1.0),
            u=16,
            v=10,
        )
        uv_sphere(
            f"MonDot_{i}",
            0.022,
            (cx, -0.062, top - 0.16),
            M("noren_red"),
            col,
            parent,
            scale=(1.0, 0.4, 1.0),
            u=12,
            v=8,
        )

    # RAMEN sign board hanging under the awning, above the opening
    board_z = 2.04
    board_y = -0.24
    box("SignBoard", (0.0, board_y, board_z), (0.78, 0.03, 0.22), M("trim"), col, parent)
    box("SignFace", (0.0, board_y - 0.012, board_z), (0.72, 0.012, 0.16), M("wood_dark"), col, parent)
    build_block_text(
        "RAMEN",
        origin=Vector((-0.30, board_y - 0.022, board_z - 0.055)),
        cell=0.020,
        depth=0.012,
        mat=M("sign_letters"),
        col=col,
        parent=parent,
        name="SignLetters",
    )

    # Lanterns framing the entrance
    for sx, tag in ((-1.28, "L"), (1.28, "R")):
        build_lantern(f"Lantern_{tag}", Vector((sx, -0.10, 1.42)), col, parent)
        # hanger
        cylinder(
            f"LanternCord_{tag}",
            (sx, -0.10, 1.68),
            (sx, -0.08, 2.38),
            0.006,
            M("trim"),
            col,
            parent,
            segs=6,
        )

    # Stools
    for sx, tag in ((-0.48, "L"), (0.55, "R")):
        build_stool(f"Stool_{tag}", Vector((sx, -0.58, 0.0)), col, parent)

    # Back shelf and kitchen bits
    box("Shelf", (0.0, 1.18, 1.28), (1.9, 0.28, 0.04), M("wood"), col, parent)
    # stacked bowls on the left of the shelf
    stack_bowls(Vector((-0.72, 1.16, 1.31)), col, parent)
    # stock pot
    build_pot(Vector((0.62, 1.05, COUNTER_Z)), col, parent)
    # cutting board
    box("CuttingBoard", (-0.62, 0.78, COUNTER_Z + 0.012), (0.36, 0.24, 0.02), M("wood_lite"), col, parent)
    # negi on the board
    for i in range(4):
        y0 = 0.70 + (i % 2) * 0.06
        x0 = -0.74 + i * 0.06
        cylinder(
            f"Negi_{i}",
            (x0, y0, COUNTER_Z + 0.028),
            (x0 + 0.10, y0 + 0.04, COUNTER_Z + 0.04),
            0.012,
            M("scallion") if i % 2 == 0 else M("scallion_w"),
            col,
            parent,
            segs=8,
        )
    # knife
    box(
        "KnifeBlade",
        (-0.55, 0.86, COUNTER_Z + 0.03),
        (0.16, 0.028, 0.006),
        M("metal"),
        col,
        parent,
        rot=Euler((0, 0, math.radians(-8)), "XYZ"),
    )
    box(
        "KnifeHandle",
        (-0.42, 0.88, COUNTER_Z + 0.032),
        (0.07, 0.02, 0.012),
        M("knife_handle"),
        col,
        parent,
        rot=Euler((0, 0, math.radians(-8)), "XYZ"),
    )

    # Condiment tray on the right of the counter
    box("Tray", (0.72, 0.38, COUNTER_Z + 0.012), (0.28, 0.18, 0.015), M("wood_lite"), col, parent)
    # soy dispenser
    cylinder(
        "SoyBottle",
        (0.64, 0.36, COUNTER_Z + 0.02),
        (0.64, 0.36, COUNTER_Z + 0.13),
        0.028,
        M("soy"),
        col,
        parent,
        segs=12,
    )
    uv_sphere(
        "SoyCap",
        0.022,
        (0.64, 0.36, COUNTER_Z + 0.145),
        M("noren_red"),
        col,
        parent,
        u=12,
        v=8,
    )
    # chili jar
    cylinder(
        "ChiliJar",
        (0.74, 0.40, COUNTER_Z + 0.02),
        (0.74, 0.40, COUNTER_Z + 0.09),
        0.026,
        M("ceramic"),
        col,
        parent,
        segs=12,
    )
    cylinder(
        "ChiliFill",
        (0.74, 0.40, COUNTER_Z + 0.035),
        (0.74, 0.40, COUNTER_Z + 0.078),
        0.022,
        M("chili"),
        col,
        parent,
        segs=12,
    )
    # spice shaker
    cylinder(
        "Shaker",
        (0.82, 0.34, COUNTER_Z + 0.02),
        (0.82, 0.34, COUNTER_Z + 0.10),
        0.02,
        M("ceramic"),
        col,
        parent,
        segs=10,
    )
    uv_sphere("ShakerCap", 0.018, (0.82, 0.34, COUNTER_Z + 0.112), M("metal"), col, parent, u=10, v=8)

    # tea cup
    lathe(
        "Yunomi",
        [
            (0.004, 0.0),
            (0.038, 0.005),
            (0.042, 0.02),
            (0.040, 0.055),
            (0.046, 0.07),
            (0.044, 0.078),
            (0.036, 0.072),
            (0.034, 0.02),
            (0.004, 0.012),
        ],
        M("ceramic"),
        col,
        parent,
        loc=(-0.55, 0.22, COUNTER_Z),
        segments=20,
        scale=1.0,
    )
    cylinder(
        "Tea",
        (-0.55, 0.22, COUNTER_Z + 0.02),
        (-0.55, 0.22, COUNTER_Z + 0.055),
        0.032,
        M("tea"),
        col,
        parent,
        segs=16,
    )

    # crate of negi beside the stall (camera-left foreground interest, low)
    box("Crate", (-1.42, 0.15, 0.16), (0.28, 0.22, 0.22), M("wood"), col, parent)
    box("CrateRim", (-1.42, 0.15, 0.27), (0.30, 0.24, 0.03), M("wood_dark"), col, parent)
    for i in range(5):
        cylinder(
            f"CrateNegi_{i}",
            (-1.50 + i * 0.035, 0.12, 0.28),
            (-1.46 + i * 0.03, 0.10 + (i % 2) * 0.04, 0.52),
            0.011,
            M("scallion"),
            col,
            parent,
            segs=6,
        )

    # a plain menu board on the back wall — the hero sign already says RAMEN
    box("MenuBoard", (-0.78, 1.22, 1.70), (0.28, 0.02, 0.40), M("wood_dark"), col, parent)
    for i, z in enumerate((1.82, 1.72, 1.62)):
        box(
            f"MenuLine_{i}",
            (-0.78, 1.20, z),
            (0.18, 0.008, 0.012),
            M("paper"),
            col,
            parent,
        )


def build_lantern(name, loc, col, parent):
    profile = [
        (0.02, 0.0),
        (0.055, 0.02),
        (0.10, 0.07),
        (0.125, 0.14),
        (0.125, 0.20),
        (0.09, 0.28),
        (0.045, 0.33),
        (0.02, 0.35),
    ]
    lathe(name, profile, M("lantern"), col, parent, loc=loc, segments=24, smooth=True)
    # black caps
    uv_sphere(f"{name}_Top", 0.04, loc + Vector((0, 0, 0.34)), M("lantern_dark"), col, parent, scale=(1.1, 1.1, 0.6), u=12, v=8)
    uv_sphere(f"{name}_Bot", 0.035, loc + Vector((0, 0, 0.01)), M("lantern_dark"), col, parent, scale=(1.2, 1.2, 0.5), u=12, v=8)
    # ribs
    for z in (0.10, 0.18, 0.26):
        torus(
            f"{name}_Rib_{int(z*100)}",
            0.118 if z < 0.2 else 0.095,
            0.006,
            loc + Vector((0, 0, z)),
            M("lantern_dark"),
            col,
            parent,
            major_seg=16,
            minor_seg=6,
        )


def build_stool(name, loc, col, parent):
    # seat
    cylinder(
        f"{name}_Post",
        loc + Vector((0, 0, 0.02)),
        loc + Vector((0, 0, 0.50)),
        0.035,
        M("wood_dark"),
        col,
        parent,
        segs=10,
    )
    cylinder(
        f"{name}_Seat",
        loc + Vector((0, 0, 0.50)),
        loc + Vector((0, 0, 0.55)),
        0.16,
        M("wood"),
        col,
        parent,
        segs=20,
    )
    cylinder(
        f"{name}_Cushion",
        loc + Vector((0, 0, 0.55)),
        loc + Vector((0, 0, 0.59)),
        0.15,
        M("cushion"),
        col,
        parent,
        segs=20,
    )
    # foot ring
    torus(
        f"{name}_Ring",
        0.11,
        0.01,
        loc + Vector((0, 0, 0.18)),
        M("metal_dark"),
        col,
        parent,
        major_seg=16,
        minor_seg=6,
    )
    # splayed feet
    for i in range(4):
        ang = i * math.pi / 2.0 + 0.4
        foot = loc + Vector((math.cos(ang) * 0.14, math.sin(ang) * 0.14, 0.0))
        cylinder(
            f"{name}_Foot_{i}",
            loc + Vector((0, 0, 0.08)),
            foot,
            0.016,
            M("wood_dark"),
            col,
            parent,
            segs=6,
        )


def stack_bowls(loc, col, parent):
    profile = bowl_profile(0.72)
    for i in range(4):
        lathe(
            f"StackBowl_{i}",
            profile,
            M("ceramic"),
            col,
            parent,
            loc=loc + Vector((0, 0, i * 0.035)),
            segments=20,
            scale=1.0,
        )


def bowl_profile(scale=1.0):
    raw = [
        (0.002, 0.0),
        (0.055, 0.012),
        (0.105, 0.04),
        (0.145, 0.085),
        (0.162, 0.125),
        (0.188, 0.155),
        (0.198, 0.175),
        (0.180, 0.188),
        (0.162, 0.170),
        (0.148, 0.12),
        (0.105, 0.055),
        (0.045, 0.03),
        (0.002, 0.028),
    ]
    return [(r * scale, z * scale) for r, z in raw]


def build_pot(loc, col, parent):
    profile = [
        (0.01, 0.0),
        (0.12, 0.02),
        (0.145, 0.06),
        (0.15, 0.18),
        (0.16, 0.21),
        (0.145, 0.23),
        (0.13, 0.20),
        (0.125, 0.06),
        (0.01, 0.03),
    ]
    lathe("StockPot", profile, M("pot"), col, parent, loc=loc, segments=24)
    # lid
    hemisphere(
        "PotLid",
        0.145,
        loc + Vector((0, 0, 0.22)),
        M("pot"),
        col,
        parent,
        direction="UP",
        scale=(1.0, 1.0, 0.45),
        u=20,
        v=10,
    )
    uv_sphere("PotKnob", 0.025, loc + Vector((0, 0, 0.30)), M("trim"), col, parent, u=10, v=8)
    # side handles
    for sx, tag in ((-1, "L"), (1, "R")):
        torus(
            f"PotHandle_{tag}",
            0.04,
            0.008,
            loc + Vector((sx * 0.16, 0.0, 0.14)),
            M("metal_dark"),
            col,
            parent,
            rot=Euler((0, math.radians(90), 0), "XYZ"),
            major_seg=12,
            minor_seg=6,
        )
    # resting ladle in the pot
    cylinder(
        "PotLadle",
        loc + Vector((0.05, -0.02, 0.18)),
        loc + Vector((0.16, -0.16, 0.40)),
        0.008,
        M("wood_lite"),
        col,
        parent,
        segs=8,
    )


# ---------------------------------------------------------------------------
# Block letters (one mesh)
# ---------------------------------------------------------------------------

GLYPHS = {
    "A": [" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "H": ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "I": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"],
    "M": ["#   #", "## ##", "# # #", "#   #", "#   #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    "S": [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
    "U": ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "Y": ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
    " ": ["     ", "     ", "     ", "     ", "     ", "     ", "     "],
}


def build_block_text(text, origin, cell, depth, mat, col, parent, name):
    bm = bmesh.new()
    cursor_x = 0.0
    rows = 7
    for ch in text:
        glyph = GLYPHS.get(ch, GLYPHS[" "])
        cols = len(glyph[0])
        for r, row in enumerate(glyph):
            for c, bit in enumerate(row):
                if bit != "#":
                    continue
                # glyph row 0 is the top
                x = origin.x + cursor_x + (c + 0.5) * cell
                z = origin.z + (rows - 1 - r + 0.5) * cell
                y = origin.y
                tmp = bmesh.new()
                bmesh.ops.create_cube(tmp, size=1.0)
                for vert in tmp.verts:
                    vert.co.x = vert.co.x * cell * 0.88 + x
                    vert.co.y = vert.co.y * depth + y
                    vert.co.z = vert.co.z * cell * 0.88 + z
                tmp.verts.ensure_lookup_table()
                tmp.faces.ensure_lookup_table()
                mapping = [bm.verts.new(v.co) for v in tmp.verts]
                index = {v: i for i, v in enumerate(tmp.verts)}
                for face in tmp.faces:
                    bm.faces.new([mapping[index[v]] for v in face.verts])
                tmp.free()
        cursor_x += (cols + 1) * cell
    if not len(bm.verts):
        bm.free()
        return None
    return finish(name, bm, mat, col, parent, False)


# ---------------------------------------------------------------------------
# Ramen
# ---------------------------------------------------------------------------

def build_ramen():
    col = "Ramen"
    parent = "RamenSet"
    loc = BOWL_C

    lathe(
        "Bowl",
        bowl_profile(1.0),
        M("ceramic"),
        col,
        parent,
        loc=loc,
        segments=36,
        scale=BOWL_SCALE,
    )
    # cobalt band
    torus(
        "BowlBand",
        0.168 * BOWL_SCALE,
        0.012 * BOWL_SCALE,
        loc + Vector((0, 0, 0.10 * BOWL_SCALE)),
        M("cobalt"),
        col,
        parent,
        major_seg=28,
        minor_seg=8,
    )
    torus(
        "BowlBand2",
        0.150 * BOWL_SCALE,
        0.006 * BOWL_SCALE,
        loc + Vector((0, 0, 0.078 * BOWL_SCALE)),
        M("cobalt"),
        col,
        parent,
        major_seg=24,
        minor_seg=6,
    )

    broth_z = loc.z + 0.118 * BOWL_SCALE
    cylinder(
        "Broth",
        (loc.x, loc.y, broth_z - 0.008),
        (loc.x, loc.y, broth_z + 0.004),
        0.150 * BOWL_SCALE,
        M("broth"),
        col,
        parent,
        segs=28,
    )
    # oil eyes
    for i in range(6):
        ang = i / 6.0 * math.tau + 0.3
        rad = 0.04 + (i % 3) * 0.03
        ox = loc.x + math.cos(ang) * rad
        oy = loc.y + math.sin(ang) * rad * 0.85
        cylinder(
            f"Oil_{i}",
            (ox, oy, broth_z + 0.004),
            (ox, oy, broth_z + 0.010),
            0.012 + (i % 2) * 0.006,
            M("oil"),
            col,
            parent,
            segs=10,
        )

    # noodle nest
    for s in range(4):
        pts = []
        turns = 2.1 + s * 0.25
        phase = s * 1.7
        for i in range(30):
            t = i / 29.0
            ang = phase + t * turns * math.tau
            rad = (0.03 + 0.075 * math.sin(t * math.pi)) * (0.85 + 0.12 * s)
            rad *= BOWL_SCALE
            z = broth_z + 0.015 + 0.10 * math.sin(t * math.pi) + 0.01 * math.sin(ang * 2.0 + s)
            x = loc.x + math.cos(ang) * rad
            y = loc.y + math.sin(ang) * rad * 0.82
            pts.append((x, y, z))
        tube(
            f"Noodle_{s}",
            catmull(pts, 3),
            0.013,
            0.010,
            M("noodle"),
            col,
            parent,
            sides=7,
        )

    # chopsticks gripped near the end of that tentacle, dipping into the bowl
    grip = Vector((-0.12, 0.30, 1.24))
    into = Vector((-0.02, 0.34, broth_z + 0.01))
    direction = (into - grip).normalized()
    back = grip - direction * 0.05
    for i, offset in enumerate((-0.008, 0.008)):
        side = Vector((1.0, 0.0, 0.0)) * offset
        # slight splay
        splay = Vector((offset * 1.6, 0.0, 0.0))
        cylinder(
            f"Chopstick_{i}",
            back + side,
            into + splay,
            0.0055,
            M("wood_lite"),
            col,
            parent,
            segs=6,
        )

    # noodles lifted on the chopsticks and falling back into the bowl
    lift_pts_sets = [
        [
            grip + Vector((0.0, 0.0, -0.02)),
            Vector((-0.08, 0.30, 1.12)),
            Vector((-0.04, 0.32, broth_z + 0.03)),
            Vector((0.00, 0.36, broth_z + 0.01)),
        ],
        [
            grip + Vector((0.015, 0.005, -0.03)),
            Vector((-0.02, 0.28, 1.08)),
            Vector((0.04, 0.33, broth_z + 0.025)),
            Vector((0.06, 0.38, broth_z + 0.005)),
        ],
        [
            grip + Vector((-0.01, -0.005, -0.015)),
            Vector((-0.10, 0.26, 1.06)),
            Vector((-0.06, 0.30, broth_z + 0.02)),
        ],
    ]
    for i, ctrl in enumerate(lift_pts_sets):
        tube(
            f"NoodleLift_{i}",
            catmull(ctrl, 5),
            0.009,
            0.007,
            M("noodle"),
            col,
            parent,
            sides=6,
        )

    # ladle: handle from the ladle-tentacle tip down into the broth, cup at the end
    ladle_top = Vector((0.14, 0.34, 1.18))
    ladle_cup = Vector((0.05, 0.30, broth_z + 0.09))
    cylinder("LadleHandle", ladle_top, ladle_cup, 0.008, M("wood_lite"), col, parent, segs=8)
    hemisphere(
        "LadleCup",
        0.048,
        ladle_cup + Vector((0, 0, -0.005)),
        M("metal"),
        col,
        parent,
        direction="DOWN",
        scale=(1.05, 0.85, 0.7),
        u=16,
        v=10,
    )

    # egg, front-left of the bowl so the camera sees the yolk
    egg_loc = loc + Vector((-0.07, -0.075, 0.185))
    hemisphere(
        "Egg",
        0.055,
        egg_loc,
        M("egg"),
        col,
        parent,
        direction="DOWN",
        scale=(1.05, 0.9, 0.85),
        rot_extra=Euler((math.radians(-28), math.radians(12), math.radians(8)), "XYZ"),
        u=20,
        v=12,
    )
    uv_sphere(
        "Yolk",
        0.028,
        egg_loc + Vector((-0.008, -0.02, 0.028)),
        M("yolk"),
        col,
        parent,
        scale=(1.0, 1.0, 0.72),
        u=16,
        v=10,
    )

    # chashu slices, center-right
    for i in range(3):
        ang = math.radians(-18 + i * 16)
        pos = loc + Vector((0.045 + i * 0.014, 0.015 - i * 0.008, 0.175 + i * 0.008))
        cylinder(
            f"Chashu_{i}",
            pos,
            pos + Vector((0, 0, 0.014)),
            0.048 - i * 0.004,
            M("chashu"),
            col,
            parent,
            segs=16,
        )
        cylinder(
            f"Fat_{i}",
            pos + Vector((0, 0, -0.002)),
            pos + Vector((0, 0, 0.004)),
            0.052 - i * 0.004,
            M("fat"),
            col,
            parent,
            segs=16,
        )

    # narutomaki standing so the spiral faces the customer
    cake = loc + Vector((0.085, -0.055, 0.185))
    cylinder(
        "Naruto",
        cake + Vector((0, 0.012, 0)),
        cake + Vector((0, -0.012, 0)),
        0.038,
        M("naruto"),
        col,
        parent,
        segs=18,
    )
    # pink spiral on the near face
    spiral = []
    face = cake + Vector((0, -0.016, 0))
    for i in range(22):
        t = i / 21.0
        ang = t * 3.4 * math.pi
        rad = 0.004 + t * 0.026
        spiral.append((face.x + math.cos(ang) * rad, face.y, face.z + math.sin(ang) * rad))
    tube("NarutoSpiral", spiral, 0.0045, 0.0035, M("naruto_pink"), col, parent, sides=5)

    # nori sheet standing at the back of the bowl
    bm = bmesh.new()
    nori_c = loc + Vector((-0.01, 0.07, 0.20))
    segs_x, segs_z = 6, 8
    grid = []
    for iz in range(segs_z + 1):
        row = []
        tz = iz / segs_z
        for ix in range(segs_x + 1):
            tx = ix / segs_x
            x = (tx - 0.5) * 0.09
            z = (tz - 0.05) * 0.13
            curve = math.sin(tx * math.pi) * 0.012
            row.append(bm.verts.new((nori_c.x + x, nori_c.y + curve, nori_c.z + z)))
        grid.append(row)
    for iz in range(segs_z):
        for ix in range(segs_x):
            bm.faces.new(
                (grid[iz][ix], grid[iz][ix + 1], grid[iz + 1][ix + 1], grid[iz + 1][ix])
            )
    extruded = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
    verts = [g for g in extruded["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=verts, vec=(0.0, 0.004, 0.0))
    finish("Nori", bm, M("nori"), col, parent, True)

    # scallions
    for i in range(12):
        ang = rng.random() * math.tau
        rad = 0.02 + rng.random() * 0.11
        x = loc.x + math.cos(ang) * rad
        y = loc.y + math.sin(ang) * rad * 0.8
        h = 0.012 + rng.random() * 0.016
        yaw = rng.random() * math.pi
        p0 = Vector((x, y, broth_z + 0.07))
        p1 = p0 + Vector((math.cos(yaw) * h, math.sin(yaw) * h, 0.006))
        cylinder(
            f"Scallion_{i}",
            p0,
            p1,
            0.0045,
            M("scallion") if i % 3 else M("scallion_w"),
            col,
            parent,
            segs=5,
        )

    # menma
    for i in range(3):
        box(
            f"Menma_{i}",
            loc + Vector((0.01 + i * 0.016, 0.04, 0.185)),
            (0.012, 0.028, 0.035),
            M("menma"),
            col,
            parent,
            rot=Euler((math.radians(20), math.radians(10 * i), math.radians(-15 + i * 12)), "XYZ"),
        )

    # wooden geta under the bowl
    cylinder(
        "Geta",
        (loc.x, loc.y, COUNTER_Z),
        (loc.x, loc.y, loc.z),
        0.155,
        M("wood"),
        col,
        parent,
        segs=20,
    )

    # steam puffs over the bowl and the pot
    for i in range(3):
        origin = loc + Vector(((-0.04 + i * 0.045), -0.01 + (i % 2) * 0.02, 0.16))
        steam_column(f"SteamBowl_{i}", origin, 0.42, col, parent, n=4, scale=0.055)
    steam_column("SteamPot", Vector((0.62, 1.02, COUNTER_Z + 0.36)), 0.28, col, parent, n=3, scale=0.04)


def steam_column(name, origin, height, col, parent, n=4, scale=0.04):
    origin = Vector(origin)
    for i in range(n):
        t = (i + 1) / (n + 0.4)
        z = origin.z + height * t
        wobble = Vector((math.sin(t * 7.0 + origin.x) * 0.025, math.cos(t * 5.0) * 0.02, 0.0))
        r = scale * (1.2 - t)
        uv_sphere(
            f"{name}_{i}",
            r,
            origin + wobble + Vector((0, 0, height * t)) - Vector((0, 0, origin.z)) * 0 + Vector((0, 0, 0)),
            M("steam"),
            col,
            parent,
            scale=(1.0, 0.85, 0.7),
            u=10,
            v=8,
        )
        # fix: the expression above is messy but the z is `origin.z` ignored.
        # Reposition properly — sphere was placed with a confused z. Override by
        # rebuilding location: we already passed a location. Let's just set it cleanly
        # by not doing the mess. (Handled below if needed.)


# The steam helper above has a muddled location expression. Replace objects' mesh
# is harder after the fact, so build steam directly here and ignore that function
# body by redefining it before use. Python uses the function as it exists at call
# time, and build_ramen() is called after this redefinition if we redefine now.

def steam_column(name, origin, height, col, parent, n=4, scale=0.04):
    origin = Vector(origin)
    for i in range(n):
        t = (i + 1) / (n + 0.5)
        wobble = Vector(
            (
                math.sin(t * 6.5 + origin.x * 3.0) * 0.03,
                math.cos(t * 5.0 + i) * 0.02,
                0.0,
            )
        )
        center = Vector((origin.x, origin.y, origin.z)) + wobble
        center.z = origin.z + height * t
        r = scale * (1.25 - 0.85 * t)
        uv_sphere(
            f"{name}_{i}",
            max(0.012, r),
            center,
            M("steam"),
            col,
            parent,
            scale=(1.0, 0.8, 0.65),
            u=10,
            v=8,
        )


# ---------------------------------------------------------------------------
# Lights, world, cameras
# ---------------------------------------------------------------------------

def aim(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_area(name, loc, energy, color, size, target):
    light = bpy.data.lights.new(name, "AREA")
    light.energy = energy
    light.color = color
    light.shape = "RECTANGLE"
    light.size = size
    light.size_y = size
    obj = bpy.data.objects.new(name, light)
    obj.location = Vector(loc)
    collection("Lights").objects.link(obj)
    aim(obj, target)
    return obj


def add_point(name, loc, energy, color, soft=0.15):
    light = bpy.data.lights.new(name, "POINT")
    light.energy = energy
    light.color = color
    if hasattr(light, "shadow_soft_size"):
        light.shadow_soft_size = soft
    obj = bpy.data.objects.new(name, light)
    obj.location = Vector(loc)
    collection("Lights").objects.link(obj)
    return obj


def add_camera(name, loc, target, lens, scale_key=False):
    cam = bpy.data.cameras.new(name)
    cam.lens = lens
    cam.clip_start = 0.05
    cam.clip_end = 40.0
    obj = bpy.data.objects.new(name, cam)
    obj.location = Vector(loc)
    collection("Cameras").objects.link(obj)
    aim(obj, target)
    if scale_key:
        bpy.context.scene.camera = obj
    return obj


def build_lights_and_cameras():
    scene = bpy.context.scene
    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg is None:
        bg = world.node_tree.nodes.new("ShaderNodeBackground")
    # night alley, warm enough that the stall still separates
    bg.inputs["Color"].default_value = srgb((0.22, 0.16, 0.18)) + (1.0,)
    bg.inputs["Strength"].default_value = 0.55

    target = (0.0, 0.35, 1.12)
    add_area("Key", (-1.35, -1.55, 2.15), 280, srgb((1.0, 0.86, 0.72)), 2.4, target)
    add_area("Fill", (1.6, -1.15, 1.55), 70, srgb((0.70, 0.80, 1.0)), 2.8, target)
    add_area("Rim", (0.2, 1.9, 2.0), 140, srgb((1.0, 0.72, 0.48)), 1.4, (0.0, 0.55, 1.35))
    add_area("CounterBounce", (0.0, -0.4, 0.35), 40, srgb((1.0, 0.75, 0.55)), 1.6, (0.0, 0.4, 1.0))
    # practicals inside the lanterns (these export as punctual lights)
    add_point("LanternLight_L", (-1.28, -0.10, 1.48), 35, srgb((1.0, 0.62, 0.32)), 0.25)
    add_point("LanternLight_R", (1.28, -0.10, 1.48), 35, srgb((1.0, 0.62, 0.32)), 0.25)
    add_point("KitchenLight", (0.2, 1.0, 1.7), 18, srgb((1.0, 0.78, 0.55)), 0.3)

    add_camera("Cam_Hero", (-1.85, -2.25, 1.86), (0.06, 0.42, 1.30), 43, scale_key=True)
    add_camera("Cam_Close", (-0.88, -1.22, 1.40), (-0.02, 0.40, 1.18), 52)
    add_camera("Cam_Side", (1.7, -1.9, 1.55), (-0.05, 0.45, 1.18), 42)

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    ee = scene.eevee
    ee.taa_render_samples = 48
    ee.taa_samples = 16
    if hasattr(ee, "use_raytracing"):
        ee.use_raytracing = True
    if hasattr(ee, "use_shadows"):
        ee.use_shadows = True
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    scene.view_settings.exposure = 0.28


def bounds():
    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    faces = 0
    meshes = 0
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        meshes += 1
        faces += len(obj.data.polygons)
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            mins.x = min(mins.x, world.x)
            mins.y = min(mins.y, world.y)
            mins.z = min(mins.z, world.z)
            maxs.x = max(maxs.x, world.x)
            maxs.y = max(maxs.y, world.y)
            maxs.z = max(maxs.z, world.z)
    return {
        "meshes": meshes,
        "faces": faces,
        "min": [round(mins.x, 3), round(mins.y, 3), round(mins.z, 3)],
        "max": [round(maxs.x, 3), round(maxs.y, 3), round(maxs.z, 3)],
    }


def main():
    purge_scene()
    make_empty("RamenShop")
    make_empty("OctopusChef", "RamenShop")
    make_empty("RamenBooth", "RamenShop")
    make_empty("RamenSet", "RamenShop")
    build_materials()
    build_octopus()
    build_booth()
    build_ramen()
    build_lights_and_cameras()
    bpy.context.view_layer.update()
    return bounds()


result = main()
