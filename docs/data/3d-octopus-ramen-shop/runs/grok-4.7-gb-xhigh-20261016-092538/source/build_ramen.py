"""Octopus chef at a night-market ramen yatai. Built entirely in Blender."""

import math
import os
import random
import traceback

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = os.getcwd()
PREVIEW = os.path.join(ROOT, "preview")
OUTPUT = os.path.join(ROOT, "output")

# ---------------------------------------------------------------------------
# Palette. Python color sockets are linear, so hex is converted.
# ---------------------------------------------------------------------------

def srgb_to_linear(u):
    return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4


def C(hex_color):
    h = hex_color.lstrip("#")
    rgb = tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    return tuple(srgb_to_linear(c) for c in rgb)


# World placement
FLOOR_Z = 0.07
COUNTER_Z = 1.02
COUNTER_Y = -0.60
MC = Vector((0.0, 0.20, 1.50))  # mantle center
BOWL = Vector((0.02, -0.56, COUNTER_Z))


def main():
    os.makedirs(PREVIEW, exist_ok=True)
    os.makedirs(OUTPUT, exist_ok=True)
    clean_scene()
    mats = make_materials()
    build_stall(mats)
    build_octopus(mats)
    build_food(mats)
    build_props(mats)
    setup_world_and_render()
    hero = add_camera("HeroCam", (1.02, -4.15, 2.05), (0.02, 0.02, 1.36), 30)
    add_camera("CloseCam", (0.78, -1.82, 1.52), (0.02, -0.12, 1.32), 50)
    add_camera("SideCam", (2.15, -2.65, 1.28), (-0.08, 0.02, 1.24), 40)
    bpy.context.scene.camera = hero
    bpy.context.view_layer.update()

    verts = 0
    faces = 0
    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        verts += len(obj.data.vertices)
        faces += len(obj.data.polygons)
        for corner in obj.bound_box:
            w = obj.matrix_world @ Vector(corner)
            mins = Vector((min(mins.x, w.x), min(mins.y, w.y), min(mins.z, w.z)))
            maxs = Vector((max(maxs.x, w.x), max(maxs.y, w.y), max(maxs.z, w.z)))
    return {
        "ok": True,
        "objects": len(bpy.data.objects),
        "verts": verts,
        "faces": faces,
        "bbox_min": [round(v, 3) for v in mins],
        "bbox_max": [round(v, 3) for v in maxs],
        "engine": bpy.context.scene.render.engine,
        "look": bpy.context.scene.view_settings.look,
        "camera": hero.name,
    }


# ---------------------------------------------------------------------------
# Scene / materials
# ---------------------------------------------------------------------------

def clean_scene():
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.curves,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.images,
    ):
        for block in list(coll):
            if block.users == 0:
                coll.remove(block)


def make_mat(
    name,
    base,
    rough=0.5,
    metal=0.0,
    spec=0.5,
    coat=0.0,
    coat_rough=0.25,
    emission=None,
    em_str=0.0,
    sss=0.0,
    sss_scale=0.04,
    sheen=0.0,
    alpha=1.0,
):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*base, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Specular IOR Level"].default_value = spec
    bsdf.inputs["Coat Weight"].default_value = coat
    bsdf.inputs["Coat Roughness"].default_value = coat_rough
    bsdf.inputs["IOR"].default_value = 1.45
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = em_str
    if sss > 0:
        bsdf.inputs["Subsurface Weight"].default_value = sss
        bsdf.inputs["Subsurface Scale"].default_value = sss_scale
        sock = bsdf.inputs["Subsurface Radius"]
        # Color socket (RGBA) in Blender 4/5.
        try:
            sock.default_value = (1.0, 0.35, 0.22, 1.0)
        except Exception:
            sock.default_value = (1.0, 0.35, 0.22)
    if sheen > 0:
        bsdf.inputs["Sheen Weight"].default_value = sheen
        bsdf.inputs["Sheen Roughness"].default_value = 0.35
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        mat.blend_method = "BLEND"
        mat.surface_render_method = "BLENDED"
    mat.diffuse_color = (*base, 1.0)
    return mat


def make_materials():
    M = {}
    M["body"] = make_mat("OctopusBody", C("#E36B52"), rough=0.38, spec=0.45, coat=0.22, coat_rough=0.28, sss=0.18, sss_scale=0.035)
    M["belly"] = make_mat("OctopusBelly", C("#F6C2AE"), rough=0.42, spec=0.35, coat=0.12, sss=0.15, sss_scale=0.03)
    M["spot"] = make_mat("OctopusSpot", C("#C44C3C"), rough=0.45, coat=0.1, sss=0.1)
    M["sucker"] = make_mat("Sucker", C("#F4A894"), rough=0.32, spec=0.5, coat=0.35, coat_rough=0.2)
    M["sucker_in"] = make_mat("SuckerInner", C("#8A3044"), rough=0.4, spec=0.4)
    M["mouth"] = make_mat("Mouth", C("#6E2430"), rough=0.45)
    M["blush"] = make_mat("Blush", C("#E88880"), rough=0.55)
    M["sclera"] = make_mat("Sclera", C("#F7F4EE"), rough=0.12, spec=0.6, coat=0.85, coat_rough=0.08)
    M["iris"] = make_mat("Iris", C("#3A2418"), rough=0.25, coat=0.4)
    M["pupil"] = make_mat("Pupil", C("#100C0A"), rough=0.2, coat=0.3)
    M["highlight"] = make_mat("EyeHighlight", C("#FFFFFF"), rough=0.1, emission=C("#FFFFFF"), em_str=3.0)
    M["hat"] = make_mat("Toque", C("#FFFDF8"), rough=0.62, spec=0.25, sheen=0.15)
    M["coat"] = make_mat("ChefCoat", C("#F4F1EA"), rough=0.58, spec=0.28, sheen=0.2)
    M["apron"] = make_mat("Apron", C("#243656"), rough=0.55, spec=0.3, sheen=0.12)
    M["scarf"] = make_mat("Neckerchief", C("#C4312E"), rough=0.48, sheen=0.15)
    M["button"] = make_mat("Button", C("#2A2624"), rough=0.35, spec=0.4)
    M["wood_l"] = make_mat("WoodLight", C("#C4925A"), rough=0.62, spec=0.3)
    M["wood_m"] = make_mat("WoodMid", C("#A56B3C"), rough=0.58, spec=0.28)
    M["wood_d"] = make_mat("WoodDark", C("#6B4228"), rough=0.55, spec=0.25)
    M["wood_w"] = make_mat("WoodWall", C("#7A4E30"), rough=0.66, spec=0.22)
    M["plinth"] = make_mat("Plinth", C("#3A3532"), rough=0.85, spec=0.15)
    M["awning_a"] = make_mat("AwningIndigo", C("#243656"), rough=0.7, sheen=0.1)
    M["awning_b"] = make_mat("AwningCream", C("#F3EDE2"), rough=0.72, sheen=0.08)
    M["noren"] = make_mat("Noren", C("#2E568C"), rough=0.62, sheen=0.22, spec=0.35)
    M["mark_w"] = make_mat("NorenWhite", C("#F4F0E6"), rough=0.5)
    M["mark_r"] = make_mat("NorenRed", C("#C4372F"), rough=0.45)
    M["sign"] = make_mat("SignBoard", C("#6B1D22"), rough=0.4, spec=0.45, coat=0.25, coat_rough=0.3)
    M["letter"] = make_mat("SignLetter", C("#F8F1E0"), rough=0.4, emission=C("#F8E2B0"), em_str=0.35)
    M["lantern"] = make_mat("LanternPaper", C("#E23A2C"), rough=0.55, emission=C("#FF7A3C"), em_str=2.4)
    M["lantern_hot"] = make_mat("LanternCore", C("#FFB15A"), rough=0.4, emission=C("#FFC07A"), em_str=6.0)
    M["black"] = make_mat("Black", C("#1A1614"), rough=0.45)
    M["metal"] = make_mat("Metal", C("#D5DDE2"), rough=0.22, metal=1.0, spec=0.5, coat=0.15)
    M["copper"] = make_mat("Copper", C("#C46B3A"), rough=0.32, metal=0.85, spec=0.5)
    M["bowl"] = make_mat("Bowl", C("#F7F4EE"), rough=0.35, spec=0.45, coat=0.35, coat_rough=0.18)
    M["bowl_blue"] = make_mat("BowlBlue", C("#1E4E8A"), rough=0.32, spec=0.5, coat=0.4, coat_rough=0.15)
    M["broth"] = make_mat("Broth", C("#D4892E"), rough=0.08, spec=0.7, coat=0.45, coat_rough=0.06)
    M["oil"] = make_mat("ChiliOil", C("#E2B04A"), rough=0.06, spec=0.6, coat=0.5, coat_rough=0.05)
    M["noodle"] = make_mat("Noodle", C("#E4B56A"), rough=0.4, spec=0.35, coat=0.2)
    M["egg_w"] = make_mat("EggWhite", C("#F6F1E4"), rough=0.35, coat=0.25, spec=0.4)
    M["yolk"] = make_mat("Yolk", C("#F0A01C"), rough=0.18, spec=0.55, coat=0.55, coat_rough=0.08)
    M["chashu"] = make_mat("Chashu", C("#D07A6A"), rough=0.4, spec=0.35, coat=0.2)
    M["fat"] = make_mat("Fat", C("#F3D0B4"), rough=0.32, spec=0.4, coat=0.25)
    M["naruto"] = make_mat("Naruto", C("#F7F4F2"), rough=0.35, spec=0.4)
    M["naruto_p"] = make_mat("NarutoPink", C("#E86B88"), rough=0.35)
    M["nori"] = make_mat("Nori", C("#1C3D30"), rough=0.55, spec=0.3)
    M["scallion"] = make_mat("Scallion", C("#3C9A48"), rough=0.45)
    M["scallion_w"] = make_mat("ScallionWhite", C("#E7E2D2"), rough=0.5)
    M["menma"] = make_mat("Menma", C("#E6C878"), rough=0.4)
    M["chili"] = make_mat("Chili", C("#C0392B"), rough=0.28, spec=0.5, coat=0.3)
    M["soy"] = make_mat("Soy", C("#3A2416"), rough=0.35, spec=0.4, coat=0.2)
    M["steam"] = make_mat("Steam", C("#E4DDD4"), rough=0.9, emission=C("#FFF4E6"), em_str=0.22, spec=0.05)
    M["menu"] = make_mat("MenuBoard", C("#1C2430"), rough=0.55)
    M["menu_line"] = make_mat("MenuLine", C("#E6D7C3"), rough=0.6)
    M["ceramic"] = make_mat("Ceramic", C("#F3F0EA"), rough=0.28, spec=0.45, coat=0.4, coat_rough=0.12)
    M["cup_blue"] = make_mat("CupBlue", C("#3E6EA8"), rough=0.3, coat=0.3)
    M["towel"] = make_mat("Towel", C("#F7F4EE"), rough=0.7, sheen=0.1)
    M["towel_s"] = make_mat("TowelStripe", C("#2C4A73"), rough=0.65)
    return M


# ---------------------------------------------------------------------------
# Mesh helpers
# ---------------------------------------------------------------------------

def activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def link_mat(obj, mat):
    if mat is None:
        return
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def finish_mesh(obj, mat=None, smooth="smooth", bevel=0.0, angle=38):
    activate(obj)
    if mat is not None:
        link_mat(obj, mat)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel > 0:
        try:
            mod = obj.modifiers.new("Bevel", "BEVEL")
            mod.width = bevel
            mod.segments = 2
            mod.limit_method = "ANGLE"
            mod.angle_limit = math.radians(45)
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception:
            if "Bevel" in obj.modifiers:
                obj.modifiers.remove(obj.modifiers["Bevel"])
    if smooth == "smooth":
        bpy.ops.object.shade_smooth()
    elif smooth == "flat":
        bpy.ops.object.shade_flat()
    else:
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle), keep_sharp_edges=False)
        except Exception:
            bpy.ops.object.shade_smooth()
    return obj


def new_mesh(name, bm, mat=None, smooth="smooth", bevel=0.0):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    return finish_mesh(obj, mat=mat, smooth=smooth, bevel=bevel)


def box(name, loc, dims, rot=(0, 0, 0), mat=None, bevel=0.0, smooth="angle"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = tuple(dims)
    return finish_mesh(obj, mat, smooth=smooth, bevel=bevel)


def cylinder(name, loc, radius, depth, rot=(0, 0, 0), mat=None, verts=24, smooth="smooth", bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot
    )
    obj = bpy.context.active_object
    obj.name = name
    return finish_mesh(obj, mat, smooth=smooth, bevel=bevel)


def uvsphere(name, loc, radius=1.0, scale=(1, 1, 1), rot=(0, 0, 0), mat=None, seg=32, ring=16, smooth="smooth"):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=seg, ring_count=ring, radius=radius, location=loc, rotation=rot
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    return finish_mesh(obj, mat, smooth=smooth)


def torus(name, loc, major, minor, rot=(0, 0, 0), mat=None, maj_seg=28, min_seg=10):
    bpy.ops.mesh.primitive_torus_add(
        align="WORLD",
        location=loc,
        rotation=rot,
        major_radius=major,
        minor_radius=minor,
        major_segments=maj_seg,
        minor_segments=min_seg,
    )
    obj = bpy.context.active_object
    obj.name = name
    return finish_mesh(obj, mat, smooth="smooth")


def cone(name, loc, r1, r2, depth, rot=(0, 0, 0), mat=None, verts=16):
    bpy.ops.mesh.primitive_cone_add(
        vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot
    )
    obj = bpy.context.active_object
    obj.name = name
    return finish_mesh(obj, mat, smooth="smooth")


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def cylinder_between(name, p0, p1, radius, mat, verts=12):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    mid = (p0 + p1) / 2
    rot = d.to_track_quat("Z", "Y").to_euler()
    return cylinder(name, mid, radius, max(d.length, 1e-4), rot=rot, mat=mat, verts=verts)


def catmull_rom(points, radii, n_per_seg=6):
    pts = [Vector(p) for p in points]
    rads = list(radii)
    n = len(pts)
    if n < 2:
        return [], []
    P = [pts[0]] + pts + [pts[-1]]
    R = [rads[0]] + rads + [rads[-1]]
    out_p, out_r = [], []
    segs = n - 1
    for i in range(segs):
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        r0, r1, r2, r3 = R[i], R[i + 1], R[i + 2], R[i + 3]
        steps = n_per_seg + (1 if i == segs - 1 else 0)
        for s in range(steps):
            if s == 0 and i > 0:
                continue
            t = s / float(n_per_seg)
            t2 = t * t
            t3 = t2 * t
            c = 0.5 * (
                (2 * p1)
                + (-p0 + p2) * t
                + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                + (-p0 + 3 * p1 - 3 * p2 + p3) * t3
            )
            r = 0.5 * (
                (2 * r1)
                + (-r0 + r2) * t
                + (2 * r0 - 5 * r1 + 4 * r2 - r3) * t2
                + (-r0 + 3 * r1 - 3 * r2 + r3) * t3
            )
            if out_p and (c - out_p[-1]).length < 1e-5:
                continue
            out_p.append(c)
            out_r.append(max(0.0035, r))
    return out_p, out_r


def tube(name, points, radii, mat, sides=12, n_per_seg=5, smooth="smooth"):
    samples, rads = catmull_rom(points, radii, n_per_seg=n_per_seg)
    if len(samples) < 2:
        return None
    tangents = []
    for i in range(len(samples)):
        if i == 0:
            t = samples[1] - samples[0]
        elif i == len(samples) - 1:
            t = samples[-1] - samples[-2]
        else:
            t = samples[i + 1] - samples[i - 1]
        tangents.append(t.normalized() if t.length > 1e-8 else Vector((0, 0, 1)))

    def perp(t):
        up = Vector((0, 0, 1))
        nrm = t.cross(up)
        if nrm.length < 1e-4:
            nrm = t.cross(Vector((0, 1, 0)))
        return nrm.normalized()

    normals = [perp(tangents[0])]
    for i in range(1, len(samples)):
        prev, cur = tangents[i - 1], tangents[i]
        axis = prev.cross(cur)
        if axis.length < 1e-6:
            nrm = normals[-1]
        else:
            axis.normalize()
            nrm = Matrix.Rotation(prev.angle(cur), 3, axis) @ normals[-1]
        nrm = nrm - cur * nrm.dot(cur)
        normals.append(nrm.normalized() if nrm.length > 1e-6 else perp(cur))

    bm = bmesh.new()
    rings = []
    for p, r, t, nrm in zip(samples, rads, tangents, normals):
        b = t.cross(nrm).normalized()
        ring = []
        for s in range(sides):
            a = (s / sides) * math.tau
            pos = p + (nrm * math.cos(a) + b * math.sin(a)) * r
            ring.append(bm.verts.new(pos))
        rings.append(ring)
    for i in range(len(rings) - 1):
        r0, r1 = rings[i], rings[i + 1]
        for s in range(sides):
            s2 = (s + 1) % sides
            bm.faces.new((r0[s], r0[s2], r1[s2], r1[s]))
    c0 = bm.verts.new(samples[0])
    c1 = bm.verts.new(samples[-1])
    for s in range(sides):
        s2 = (s + 1) % sides
        bm.faces.new((c0, rings[0][s2], rings[0][s]))
        bm.faces.new((c1, rings[-1][s], rings[-1][s2]))
    obj = new_mesh(name, bm, mat=mat, smooth=smooth)
    return obj


def _basis_from_z(z_axis):
    z = z_axis.normalized()
    tmp = Vector((0, 0, 1)) if abs(z.z) < 0.92 else Vector((0, 1, 0))
    x = z.cross(tmp).normalized()
    y = z.cross(x).normalized()
    return x, y, z


def add_suckers_for(samples, rads, aim, bm, every_dist=None):
    """Append sucker spheres into bm. Material 0 = rim, 1 = center."""
    if len(samples) < 4:
        return 0
    count = 0
    acc = 0.0
    next_at = rads[0] * 2.2
    aim = Vector(aim)
    for i in range(len(samples)):
        if i:
            acc += (samples[i] - samples[i - 1]).length
        if i < 2 or i > len(samples) - 3:
            continue
        if rads[i] < 0.016:
            continue
        if acc < next_at:
            continue
        spacing = max(rads[i] * 1.55, 0.038)
        next_at = acc + spacing
        t = samples[i] - (samples[i - 1] if i else samples[i])
        if i < len(samples) - 1:
            t = samples[i + 1] - samples[i - 1]
        if t.length < 1e-8:
            continue
        t.normalize()
        v = aim - t * aim.dot(t)
        if v.length < 1e-4:
            v = _basis_from_z(t)[0]
        v.normalize()
        side = t.cross(v).normalized()
        for sign in (-1, 1):
            ang = 0.62
            d = (v * math.cos(ang) + side * sign * math.sin(ang)).normalized()
            r = rads[i]
            pos = samples[i] + d * (r * 0.92)
            x, y, z = _basis_from_z(d)
            M = Matrix((
                (x.x, y.x, z.x, pos.x),
                (x.y, y.y, z.y, pos.y),
                (x.z, y.z, z.z, pos.z),
                (0.0, 0.0, 0.0, 1.0),
            ))
            sr = r * 0.62
            existing = set(bm.faces)
            S = Matrix.Diagonal((sr, sr, sr * 0.46, 1.0))
            bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=1.0, matrix=M @ S, calc_uvs=False)
            for f in bm.faces:
                if f not in existing:
                    f.material_index = 0
            existing = set(bm.faces)
            T = Matrix.Translation((0.0, 0.0, sr * 0.22))
            Si = Matrix.Diagonal((sr * 0.48, sr * 0.48, sr * 0.30, 1.0))
            bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=4, radius=1.0, matrix=M @ T @ Si, calc_uvs=False)
            for f in bm.faces:
                if f not in existing:
                    f.material_index = 1
            count += 1
    return count


def tentacle(name, points, radii, mats, aim, sides=12):
    samples, rads = catmull_rom(points, radii, n_per_seg=5)
    obj = tube(name, points, radii, mats["body"], sides=sides, n_per_seg=5)
    bm = bmesh.new()
    add_suckers_for(samples, rads, aim, bm)
    if len(bm.verts) == 0:
        bm.free()
        return obj
    me = bpy.data.meshes.new(name + "_suckers")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mats["sucker"])
    me.materials.append(mats["sucker_in"])
    sobj = bpy.data.objects.new(name + "_suckers", me)
    bpy.context.scene.collection.objects.link(sobj)
    finish_mesh(sobj, smooth="smooth")
    return obj


def ribbon(name, points, width0, width1, mat, thickness=0.006):
    samples, _rads = catmull_rom(points, [1.0] * len(points), n_per_seg=4)
    if len(samples) < 2:
        return None
    left, right = [], []
    for i, p in enumerate(samples):
        if i == 0:
            t = samples[1] - samples[0]
        elif i == len(samples) - 1:
            t = samples[-1] - samples[-2]
        else:
            t = samples[i + 1] - samples[i - 1]
        if t.length < 1e-8:
            t = Vector((0, 0, 1))
        t.normalize()
        side = t.cross(Vector((0, 0, 1)))
        if side.length < 1e-4:
            side = Vector((1, 0, 0))
        side.normalize()
        w = width0 + (width1 - width0) * (i / (len(samples) - 1))
        # Bias the ribbon to hang in a flat sheet facing the counter.
        left.append(p + side * w)
        right.append(p - side * w)
    grid = [[left[i], right[i]] for i in range(len(samples))]
    return grid_surface(name, grid, mat, solidify=thickness, smooth="smooth")


def grid_surface(name, rows, mat, solidify=0.0, smooth="smooth"):
    """rows: list of lists of Vectors."""
    bm = bmesh.new()
    verts = [[bm.verts.new(p) for p in row] for row in rows]
    for j in range(len(verts) - 1):
        for i in range(len(verts[0]) - 1):
            bm.faces.new((verts[j][i], verts[j][i + 1], verts[j + 1][i + 1], verts[j + 1][i]))
    obj = new_mesh(name, bm, mat=mat, smooth=smooth)
    if solidify > 0:
        activate(obj)
        mod = obj.modifiers.new("Solidify", "SOLIDIFY")
        mod.thickness = solidify
        mod.offset = 0.0
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def add_text(name, body, loc, size, mat, rot=(math.pi / 2, 0, 0), extrude=0.012):
    cu = bpy.data.curves.new(name + "_cu", "FONT")
    cu.body = body
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.size = size
    cu.extrude = extrude
    cu.bevel_depth = size * 0.012
    cu.bevel_resolution = 1
    cu.resolution_u = 3
    obj = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = Vector(loc)
    obj.rotation_euler = rot
    activate(obj)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.active_object
    obj.name = name
    return finish_mesh(obj, mat, smooth="angle", bevel=0.0)


def helix(start, end, radius, turns, n=16, phase=0.3):
    start, end = Vector(start), Vector(end)
    axis = end - start
    length = axis.length
    if length < 1e-6:
        return [start]
    a = axis.normalized()
    x, y, _z = _basis_from_z(a)
    pts = []
    for i in range(n):
        t = i / (n - 1)
        ang = phase + t * turns * math.tau
        c = start + axis * t
        pts.append(c + (x * math.cos(ang) + y * math.sin(ang)) * radius)
    return pts


def emergence(angle, z=1.08, rad=0.30):
    """angle 0 faces the customer (-Y). Positive angle goes toward +X."""
    return Vector((
        MC.x + math.sin(angle) * rad,
        MC.y - math.cos(angle) * rad,
        z,
    ))


# ---------------------------------------------------------------------------
# Stall
# ---------------------------------------------------------------------------

def build_stall(M):
    # Plinth and deck planks
    box("Plinth", (0.0, 0.05, -0.045), (4.05, 3.35, 0.09), mat=M["plinth"], bevel=0.01)
    plank_n = 16
    deck_w, deck_d = 3.55, 2.55
    gap = 0.012
    pw = (deck_w - gap * (plank_n - 1)) / plank_n
    woods = [M["wood_l"], M["wood_m"], M["wood_d"], M["wood_m"]]
    for i in range(plank_n):
        x = -deck_w / 2 + pw / 2 + i * (pw + gap)
        box(
            f"Deck_{i}",
            (x, 0.08, FLOOR_Z / 2),
            (pw, deck_d, FLOOR_Z),
            mat=woods[i % 4],
            bevel=0.0015,
        )

    # Posts and beams
    post_h = 2.48
    post_z = FLOOR_Z + post_h / 2
    posts = [(-1.52, -1.12), (1.52, -1.12), (-1.52, 1.18), (1.52, 1.18)]
    for i, (x, y) in enumerate(posts):
        box(f"Post_{i}", (x, y, post_z), (0.09, 0.09, post_h), mat=M["wood_d"], bevel=0.004)
    box("BeamFront", (0.0, -1.12, 2.36), (3.15, 0.09, 0.09), mat=M["wood_d"], bevel=0.003)
    box("BeamBack", (0.0, 1.18, 2.50), (3.15, 0.09, 0.09), mat=M["wood_d"], bevel=0.003)
    box("BeamLeft", (-1.52, 0.03, 2.43), (0.09, 2.40, 0.08), mat=M["wood_d"], bevel=0.003)
    box("BeamRight", (1.52, 0.03, 2.43), (0.09, 2.40, 0.08), mat=M["wood_d"], bevel=0.003)

    # Striped awning, sloped down toward the customer
    ang = math.atan2(0.22, 2.50)
    n = 14
    total_w = 3.25
    sw = total_w / n
    for i in range(n):
        x = -total_w / 2 + sw / 2 + i * sw
        mat = M["awning_a"] if i % 2 == 0 else M["awning_b"]
        box(
            f"Awning_{i}",
            (x, 0.02, 2.52),
            (sw * 0.985, 2.62, 0.028),
            rot=(ang, 0, 0),
            mat=mat,
            bevel=0.0,
        )
    # Fascia under the front eave
    box("Fascia", (0.0, -1.22, 2.30), (3.20, 0.06, 0.08), rot=(ang, 0, 0), mat=M["wood_d"], bevel=0.002)

    # Hanging sign sits in the open center, above the chef's hat
    box("ShopSign", (0.0, -1.34, 2.16), (1.28, 0.05, 0.32), mat=M["sign"], bevel=0.006)
    add_text("SignWord", "RAMEN", (0.0, -1.39, 2.16), 0.18, M["letter"], extrude=0.008)
    cylinder_between("SignHangL", (-0.46, -1.34, 2.32), (-0.46, -1.18, 2.42), 0.01, M["black"], verts=8)
    cylinder_between("SignHangR", (0.46, -1.34, 2.32), (0.46, -1.18, 2.42), 0.01, M["black"], verts=8)

    # Short noren, split so the center stays open for the face and the sign
    panel_w = 0.40
    for i, x in enumerate((-1.18, -0.72, 0.72, 1.18)):
        noren_panel(f"Noren_{i}", x, panel_w, 2.30, 1.98, -1.18, M["noren"])
        cz = 2.12
        cylinder(f"CrestW_{i}", (x, -1.22, cz), 0.085, 0.014, rot=(math.pi / 2, 0, 0), mat=M["mark_w"], verts=24)
        cylinder(f"CrestR_{i}", (x, -1.235, cz), 0.048, 0.014, rot=(math.pi / 2, 0, 0), mat=M["mark_r"], verts=18)

    # Lanterns
    for i, x in enumerate((-1.28, 1.28)):
        lantern(f"Lantern_{i}", Vector((x, -1.05, 1.82)), M)

    # Counter
    box("CounterTop", (0.0, COUNTER_Y, COUNTER_Z - 0.035), (2.55, 0.70, 0.07), mat=M["wood_l"], bevel=0.006)
    # Vertical front planks
    npl = 12
    fw = 2.48
    gapf = 0.008
    pw = (fw - gapf * (npl - 1)) / npl
    for i in range(npl):
        x = -fw / 2 + pw / 2 + i * (pw + gapf)
        mat = woods[(i + 1) % 4]
        box(f"FrontPlank_{i}", (x, -0.955, 0.56), (pw, 0.04, 0.78), mat=mat, bevel=0.001)
    box("CounterSideL", (-1.275, COUNTER_Y, 0.56), (0.045, 0.70, 0.78), mat=M["wood_d"], bevel=0.002)
    box("CounterSideR", (1.275, COUNTER_Y, 0.56), (0.045, 0.70, 0.78), mat=M["wood_d"], bevel=0.002)
    # Painted name band on the front
    box("NameBand", (0.0, -0.985, 0.58), (1.25, 0.025, 0.30), mat=M["sign"], bevel=0.003)
    add_text("CounterWord", "RAMEN", (0.0, -1.02, 0.58), 0.13, M["letter"], extrude=0.006)
    # Foot rail
    cylinder_between("FootRail", (-1.15, -1.08, 0.28), (1.15, -1.08, 0.28), 0.018, M["metal"], verts=12)
    cylinder_between("FootPostL", (-1.15, -1.08, FLOOR_Z), (-1.15, -1.08, 0.28), 0.016, M["metal"], verts=10)
    cylinder_between("FootPostR", (1.15, -1.08, FLOOR_Z), (1.15, -1.08, 0.28), 0.016, M["metal"], verts=10)

    # Back wall, prep counter, and side returns so the stall isn't open to a void
    box("BackWall", (0.0, 1.22, 1.22), (2.85, 0.07, 2.25), mat=M["wood_w"], bevel=0.004)
    box("SideWallL", (-1.58, 0.15, 1.28), (0.07, 2.05, 2.20), mat=M["wood_w"], bevel=0.0)
    box("SideWallR", (1.58, 0.70, 1.50), (0.07, 1.05, 1.70), mat=M["wood_w"], bevel=0.0)
    box("BackShelf", (0.0, 0.88, 0.86), (2.40, 0.48, 0.06), mat=M["wood_m"], bevel=0.004)
    box("ShelfSupport", (0.0, 1.05, 0.48), (2.40, 0.06, 0.70), mat=M["wood_d"], bevel=0.0)
    # Trim
    box("WallTrim", (0.0, 1.175, 2.05), (2.70, 0.04, 0.06), mat=M["wood_d"], bevel=0.0)

    # Menu board on the near side of the back wall
    box("Menu", (0.92, 1.16, 1.62), (0.62, 0.03, 0.78), mat=M["menu"], bevel=0.004)
    add_text("MenuTitle", "RAMEN", (0.92, 1.13, 1.90), 0.07, M["letter"], extrude=0.004)
    for i, w in enumerate((0.42, 0.36, 0.40, 0.30, 0.34)):
        z = 1.74 - i * 0.11
        box(f"MenuLine_{i}", (0.90, 1.135, z), (w, 0.012, 0.018), mat=M["menu_line"], bevel=0.0)
    cylinder("MenuDot", (0.66, 1.13, 1.74), 0.018, 0.012, rot=(math.pi / 2, 0, 0), mat=M["mark_r"], verts=12)

    # Stools
    stool(M, Vector((-0.78, -1.32, 0.0)))
    stool(M, Vector((1.05, -1.40, 0.0)))


def noren_panel(name, x_center, width, z_top, z_bot, y, mat):
    cols, rows = 7, 14
    grid = []
    for j in range(rows):
        v = j / (rows - 1)
        row = []
        for i in range(cols):
            u = i / (cols - 1)
            x = x_center + (u - 0.5) * width
            sag = 0.07 * math.sin(u * math.pi) * (v ** 1.15)
            z = z_top + (z_bot - z_top) * v - sag
            yv = y + 0.03 * math.sin(u * math.pi) * v
            # soft side taper near the hem
            row.append(Vector((x, yv, z)))
        grid.append(row)
    grid_surface(name, grid, mat, solidify=0.006, smooth="smooth")


def lantern(name, loc, M):
    uvsphere(name + "_paper", loc, radius=0.15, scale=(1.0, 1.0, 1.28), mat=M["lantern"], seg=28, ring=16)
    uvsphere(name + "_core", loc, radius=0.09, scale=(1.0, 1.0, 1.15), mat=M["lantern_hot"], seg=16, ring=10)
    for i, zoff in enumerate((-0.07, 0.02, 0.10)):
        torus(name + f"_rib{i}", loc + Vector((0, 0, zoff)), 0.138 - abs(zoff) * 0.08, 0.006, mat=M["black"], maj_seg=20, min_seg=6)
    cylinder(name + "_capT", loc + Vector((0, 0, 0.20)), 0.055, 0.045, mat=M["black"], verts=16)
    cylinder(name + "_capB", loc + Vector((0, 0, -0.20)), 0.05, 0.04, mat=M["black"], verts=16)
    cylinder_between(name + "_hook", loc + Vector((0, 0, 0.22)), loc + Vector((0, -0.08, 0.48)), 0.008, M["black"], verts=8)
    cone(name + "_tassel", loc + Vector((0, 0, -0.28)), 0.018, 0.004, 0.09, mat=M["mark_r"], verts=8)
    # Practical light
    bpy.ops.object.light_add(type="POINT", location=loc)
    L = bpy.context.active_object
    L.name = name + "_light"
    L.data.energy = 18
    L.data.color = (1.0, 0.62, 0.32)
    if hasattr(L.data, "shadow_soft_size"):
        L.data.shadow_soft_size = 0.18
    elif hasattr(L.data, "radius"):
        L.data.radius = 0.12


def stool(M, origin):
    seat_z = 0.50
    cylinder(f"StoolSeat_{origin.x:.2f}", origin + Vector((0, 0, seat_z)), 0.18, 0.045, mat=M["wood_l"], verts=20)
    torus(f"StoolRim_{origin.x:.2f}", origin + Vector((0, 0, seat_z)), 0.16, 0.012, mat=M["wood_d"], maj_seg=20, min_seg=6)
    for dx, dy in ((0.09, 0.09), (0.09, -0.09), (-0.09, 0.09), (-0.09, -0.09)):
        cylinder_between(
            f"StoolLeg_{origin.x:.2f}_{dx}_{dy}",
            origin + Vector((dx, dy, FLOOR_Z)),
            origin + Vector((dx * 0.7, dy * 0.7, seat_z - 0.02)),
            0.016,
            M["wood_d"],
            verts=8,
        )
    torus(f"StoolFoot_{origin.x:.2f}", origin + Vector((0, 0, 0.18)), 0.125, 0.01, mat=M["wood_m"], maj_seg=18, min_seg=6)


# ---------------------------------------------------------------------------
# Octopus chef
# ---------------------------------------------------------------------------

def build_octopus(M):
    build_mantle(M)
    build_eyes(M)
    build_mouth(M)
    build_clothes(M)
    build_tentacles(M)


def build_mantle(M):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=32, radius=1.0, calc_uvs=False)
    for v in bm.verts:
        x, y, z = v.co.x, v.co.y, v.co.z
        # Ellipsoid
        x *= 0.40
        y *= 0.355
        z *= 0.44
        # Teardrop: narrow the lower hemisphere so it tucks into the coat
        if z < 0:
            k = 1.0 + (z / 0.44) * 0.42  # ~0.58 at the bottom
            x *= k
            y *= k
        # Slight forehead lift
        if z > 0.05:
            z *= 1.06
        v.co.x, v.co.y, v.co.z = x, y, z
    # Move to world
    bmesh.ops.translate(bm, verts=bm.verts, vec=MC)
    me = bpy.data.meshes.new("Mantle")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M["body"])
    me.materials.append(M["belly"])
    obj = bpy.data.objects.new("Mantle", me)
    bpy.context.scene.collection.objects.link(obj)
    # Belly patch on the front, above the collar line
    for p in me.polygons:
        c = p.center
        if c.z > MC.z - 0.02 and (c.y - MC.y) < -0.08 and abs(c.x - MC.x) < 0.16 and (c.z - MC.z) < 0.16:
            p.material_index = 1
    finish_mesh(obj, smooth="smooth")

    # Spots
    spot_locals = [
        (0.22, -0.16, 0.22, 0.055),
        (-0.20, -0.20, 0.26, 0.042),
        (0.10, -0.08, 0.34, 0.048),
        (0.30, -0.02, 0.08, 0.036),
        (-0.28, -0.06, 0.12, 0.046),
        (0.16, -0.26, 0.16, 0.032),
        (-0.08, -0.10, 0.30, 0.028),
    ]
    for i, (x, y, z, r) in enumerate(spot_locals):
        pos, nrm = on_mantle((x, y, z), embed=0.97)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=r, location=pos)
        sp = bpy.context.active_object
        sp.name = f"Spot_{i}"
        sp.scale = (1.15, 1.15, 0.45)
        sp.rotation_euler = nrm.to_track_quat("Z", "Y").to_euler()
        finish_mesh(sp, M["spot"], smooth="smooth")

    # Blush
    for i, x in enumerate((-0.16, 0.16)):
        pos, nrm = on_mantle((x, -0.30, -0.02), embed=1.01)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.055, location=pos)
        sp = bpy.context.active_object
        sp.name = f"Blush_{i}"
        sp.scale = (1.0, 0.7, 0.45)
        sp.rotation_euler = nrm.to_track_quat("Z", "Y").to_euler()
        finish_mesh(sp, M["blush"], smooth="smooth")


def on_mantle(local, embed=1.0):
    v = Vector(local)
    if v.length < 1e-6:
        v = Vector((0, -1, 0))
    v.normalize()
    rx, ry, rz = 0.40, 0.34, 0.45
    # Ray-ellipsoid hit along this direction (direction is in unit sphere space).
    d = Vector((v.x * rx, v.y * ry, v.z * rz))
    nrm = Vector((d.x / (rx * rx), d.y / (ry * ry), d.z / (rz * rz)))
    if nrm.length < 1e-8:
        nrm = Vector((0, -1, 0))
    nrm.normalize()
    return MC + d * embed, nrm


def build_eyes(M):
    # Pupils aimed at the hero camera so both eyes read from the 3/4 view.
    look = Vector((1.35, -3.2, 1.45))
    for i, x in enumerate((-1.0, 1.0)):
        pos, _n = on_mantle((0.16 * x, -0.30, 0.08), embed=0.90)
        uvsphere(f"Sclera_{i}", pos, radius=0.112, scale=(1.0, 0.88, 1.14), mat=M["sclera"], seg=28, ring=16)
        view = (look - pos).normalized()
        uvsphere(f"Iris_{i}", pos + view * 0.062, radius=0.066, mat=M["iris"], seg=20, ring=12)
        uvsphere(f"Pupil_{i}", pos + view * 0.086, radius=0.046, mat=M["pupil"], seg=16, ring=10)
        # Two catchlights
        up = Vector((0, 0, 1))
        side = view.cross(up).normalized()
        uvsphere(f"Catch_{i}a", pos + view * 0.092 + up * 0.028 + side * 0.02 * (-1 if x < 0 else 1), radius=0.015, mat=M["highlight"], seg=10, ring=8)
        uvsphere(f"Catch_{i}b", pos + view * 0.088 - up * 0.012 - side * 0.018, radius=0.007, mat=M["highlight"], seg=8, ring=6)


def build_mouth(M):
    pos, nrm = on_mantle((0.0, -0.46, 0.05), embed=1.05)
    # Smile arc in the plane of the face
    side = nrm.cross(Vector((0, 0, 1))).normalized()
    up = side.cross(nrm).normalized()
    pts = []
    for i, t in enumerate((-1.0, -0.5, 0.0, 0.5, 1.0)):
        lift = 0.012 + 0.022 * (t * t)
        p = pos + side * (t * 0.105) + up * (-0.006 + lift) + nrm * (0.006 * (1 - t * t))
        pts.append(p)
    tube("Smile", pts, [0.011, 0.014, 0.016, 0.014, 0.011], M["mouth"], sides=8, n_per_seg=4)


def build_clothes(M):
    # Coat: flared cylinder, open neckline at the front
    segs = 40
    rings = 8
    z0, z1 = 0.96, 1.46
    r0, r1 = 0.48, 0.355
    bm = bmesh.new()
    grid = []
    for j in range(rings + 1):
        v = j / rings
        z = z0 + (z1 - z0) * v
        r = r0 + (r1 - r0) * (v ** 1.05)
        row = []
        for i in range(segs):
            a = (i / segs) * math.tau
            x = MC.x + math.cos(a) * r
            y = MC.y + math.sin(a) * r * 0.92
            zz = z
            front = max(0.0, -math.sin(a))
            if v > 0.78:
                zz -= 0.07 * ((v - 0.78) / 0.22) * (front ** 1.15)
            row.append(bm.verts.new((x, y, zz)))
        grid.append(row)
    for j in range(rings):
        for i in range(segs):
            i2 = (i + 1) % segs
            bm.faces.new((grid[j][i], grid[j][i2], grid[j + 1][i2], grid[j + 1][i]))
    # Caps so the coat is a solid shell over the lower mantle
    for ring, top in ((grid[0], False), (grid[-1], True)):
        c = bm.verts.new((MC.x, MC.y, ring[0].co.z))
        for i in range(segs):
            i2 = (i + 1) % segs
            if top:
                bm.faces.new((c, ring[i], ring[i2]))
            else:
                bm.faces.new((c, ring[i2], ring[i]))
    new_mesh("ChefCoat", bm, mat=M["coat"], smooth="smooth")

    torus("Collar", (MC.x, MC.y, 1.445), 0.33, 0.038, mat=M["coat"], maj_seg=32, min_seg=8)

    # Apron bib
    cols, rows = 9, 12
    grid_rows = []
    for j in range(rows):
        v = j / (rows - 1)
        z = 1.40 + (1.06 - 1.40) * v
        half = 0.10 + (0.24 - 0.10) * (v ** 0.85)
        y_front = MC.y - (0.34 + 0.08 * v)
        row = []
        for i in range(cols):
            u = i / (cols - 1)
            x = MC.x + (u - 0.5) * 2 * half
            y = y_front - math.sin(u * math.pi) * 0.025
            row.append(Vector((x, y, z)))
        grid_rows.append(row)
    grid_surface("Apron", grid_rows, M["apron"], solidify=0.01, smooth="smooth")
    # Neck strap
    torus("ApronStrap", (MC.x, MC.y - 0.02, 1.50), 0.30, 0.012, rot=(0.5, 0, 0), mat=M["apron"], maj_seg=24, min_seg=6)
    # Waist tie
    cylinder_between("ApronTie", (MC.x - 0.22, MC.y - 0.28, 1.12), (MC.x + 0.22, MC.y - 0.30, 1.10), 0.012, M["apron"], verts=8)

    # Neckerchief
    torus("ScarfBand", (MC.x, MC.y - 0.02, 1.47), 0.30, 0.022, mat=M["scarf"], maj_seg=28, min_seg=8)
    uvsphere("ScarfKnot", (MC.x, MC.y - 0.36, 1.40), radius=0.045, scale=(1.1, 0.8, 0.9), mat=M["scarf"], seg=16, ring=10)
    ribbon(
        "ScarfTailL",
        [
            (MC.x - 0.02, MC.y - 0.40, 1.36),
            (MC.x - 0.06, MC.y - 0.46, 1.24),
            (MC.x - 0.03, MC.y - 0.44, 1.10),
        ],
        0.028,
        0.045,
        M["scarf"],
    )
    ribbon(
        "ScarfTailR",
        [
            (MC.x + 0.025, MC.y - 0.40, 1.35),
            (MC.x + 0.07, MC.y - 0.44, 1.22),
            (MC.x + 0.04, MC.y - 0.40, 1.08),
        ],
        0.026,
        0.042,
        M["scarf"],
    )

    # Buttons down the viewer's right of the coat (coat's left / +X), beside the bib
    for i, z in enumerate((1.36, 1.28, 1.20, 1.12)):
        uvsphere(f"Button_{i}", (MC.x + 0.12, MC.y - 0.36, z), radius=0.016, mat=M["button"], seg=10, ring=8)

    # Toque
    cylinder("HatBand", (MC.x, MC.y - 0.02, MC.z + 0.40), 0.205, 0.10, mat=M["hat"], verts=28)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=40, ring_count=24, radius=0.30, location=(MC.x, MC.y - 0.03, MC.z + 0.58)
    )
    puff = bpy.context.active_object
    puff.name = "HatPuff"
    # Pleats in local space, then a gentle forward tilt
    for v in puff.data.vertices:
        ang = math.atan2(v.co.y, v.co.x)
        wave = 1.0 + 0.12 * math.sin(ang * 8.0)
        # Softer pleat toward the crown
        crown = max(0.0, v.co.z / 0.30)
        wave = 1.0 + (wave - 1.0) * (1.0 - 0.35 * crown)
        v.co.x *= wave
        v.co.y *= wave
    puff.scale = (1.0, 0.96, 0.74)
    puff.rotation_euler = (0.10, 0.0, 0.08)
    finish_mesh(puff, M["hat"], smooth="smooth")

    # Tenugui over the near shoulder (+X), hanging beside the coat
    cols, rows = 6, 14
    grid_rows = []
    for j in range(rows):
        v = j / (rows - 1)
        z = 1.58 + (1.02 - 1.58) * v
        y = MC.y - 0.05 + 0.10 * math.sin(v * math.pi) - 0.05 * v
        x_base = MC.x + 0.38 + 0.06 * math.sin(v * math.pi)
        row = []
        for i in range(cols):
            u = i / (cols - 1)
            x = x_base + (u - 0.5) * 0.16
            yy = y - 0.02 * math.sin(u * math.pi)
            row.append(Vector((x, yy, z)))
        grid_rows.append(row)
    grid_surface("Towel", grid_rows, M["towel"], solidify=0.008, smooth="smooth")
    # Indigo stripe across the towel
    box("TowelStripe", (MC.x + 0.40, MC.y + 0.02, 1.36), (0.17, 0.02, 0.035), mat=M["towel_s"], bevel=0.0)


def build_tentacles(M):
    # Shared aim: suckers face the hero camera (front-right) so they read.
    cam_aim = Vector((0.65, -1.0, -0.15))
    up_aim = Vector((0.4, -0.8, 0.7))
    down_aim = Vector((0.2, -0.5, -1.0))

    # 1. Ladle arm — coils around the ladle handle over the left of the bowl
    cup = Vector((-0.04, -0.50, 1.16))
    grip = Vector((-0.34, -0.16, 1.26))
    wind = helix(grip, cup + (grip - cup).normalized() * 0.16, 0.055, turns=1.25, n=18, phase=0.8)
    ladle_pts = [
        emergence(-0.55, z=1.06, rad=0.28),
        Vector((-0.22, -0.02, 1.12)),
        Vector((-0.36, -0.16, 1.20)),
    ] + wind
    ladle_r = [0.072, 0.058, 0.046] + [0.040] * (len(wind) - 1) + [0.022]
    # radii length must match points
    ladle_r = _fit_radii(ladle_pts, ladle_r, 0.07, 0.02)
    tentacle("ArmLadle", ladle_pts, ladle_r, M, cam_aim)

    # The ladle itself
    cylinder_between("LadleHandle", cup + Vector((-0.02, 0.02, 0.02)), grip + Vector((-0.06, 0.02, 0.04)), 0.011, M["metal"], verts=10)
    hemisphere("LadleCup", cup, 0.055, Vector((0.15, -0.35, -0.75)), M["metal"], scale=(1.15, 1.0, 0.85))

    # 2. Chopstick arm
    pinch = Vector((0.18, -0.42, 1.32))
    stick_top_a = pinch + Vector((0.05, 0.015, 0.09))
    stick_bot_a = Vector((0.05, -0.57, 1.095))
    wind = helix(pinch + Vector((0.05, 0.03, 0.06)), pinch + Vector((-0.015, -0.01, -0.02)), 0.046, turns=1.05, n=12, phase=1.4)
    chop_pts = [
        emergence(0.50, z=1.06, rad=0.28),
        Vector((0.28, -0.06, 1.14)),
        Vector((0.32, -0.28, 1.26)),
    ] + wind
    tentacle("ArmChop", chop_pts, _fit_radii(chop_pts, [], 0.070, 0.020), M, cam_aim)
    cylinder_between("StickA", stick_top_a, stick_bot_a, 0.0075, M["wood_d"], verts=8)
    cylinder_between(
        "StickB",
        stick_top_a + Vector((0.016, 0.006, 0.006)),
        stick_bot_a + Vector((0.014, -0.008, 0.0)),
        0.007,
        M["wood_d"],
        verts=8,
    )
    # Two wavy strands leaving the bowl and drooping from the chopsticks
    for k, phase in enumerate((0.2, 2.1)):
        a = Vector((0.02, -0.56, 1.10))
        b = pinch + Vector((-0.01, -0.03, -0.03))
        pts = []
        for i in range(7):
            t = i / 6.0
            p = a.lerp(b, t)
            p.x += math.sin(t * math.tau + phase) * 0.012
            p.y += math.cos(t * math.pi + phase) * 0.01
            p.z += math.sin(t * math.pi) * 0.045
            if t > 0.72:
                p.z -= (t - 0.72) * 0.16
            pts.append(p)
        tube(
            f"LiftedNoodle_{k}",
            pts,
            [0.0065, 0.0062, 0.006, 0.0055, 0.005, 0.0045, 0.0035],
            M["noodle"],
            sides=6,
            n_per_seg=3,
        )

    # 3. Left counter lean
    pts = [
        emergence(-1.05, z=1.02, rad=0.30),
        Vector((-0.48, -0.12, 1.10)),
        Vector((-0.62, -0.48, 1.055)),
        Vector((-0.42, -0.78, 1.07)),
        Vector((-0.28, -0.70, 1.14)),
    ]
    tentacle("ArmLeanL", pts, _fit_radii(pts, [0.068, 0.055, 0.046, 0.034, 0.018], 0.068, 0.018), M, up_aim)

    # 4. Right counter lean, toward the cutting board
    pts = [
        emergence(1.15, z=1.02, rad=0.30),
        Vector((0.55, -0.10, 1.08)),
        Vector((0.85, -0.40, 1.06)),
        Vector((0.98, -0.55, 1.08)),
        Vector((0.82, -0.62, 1.14)),
    ]
    tentacle("ArmLeanR", pts, _fit_radii(pts, [], 0.066, 0.018), M, up_aim)

    # 5. Greeting curl, high on the far side
    pts = [
        emergence(-1.7, z=1.12, rad=0.26),
        Vector((-0.62, 0.02, 1.28)),
        Vector((-0.88, -0.18, 1.55)),
        Vector((-0.78, -0.38, 1.78)),
        Vector((-0.52, -0.28, 1.84)),
        Vector((-0.58, -0.10, 1.66)),
    ]
    tentacle("ArmWave", pts, _fit_radii(pts, [], 0.064, 0.016), M, cam_aim)

    # 6. Flat coil resting on the counter, left of the bowl — suckers up
    coil = []
    c0 = Vector((-0.62, -0.58, 1.075))
    for i in range(16):
        t = i / 15
        ang = t * math.tau * 1.35 + 0.4
        rad = 0.13 * (1 - t) + 0.025
        coil.append(c0 + Vector((math.cos(ang) * rad, math.sin(ang) * rad * 0.82, 0.03 * t)))
    pts = [
        emergence(-0.25, z=1.00, rad=0.32),
        Vector((-0.40, -0.30, 1.08)),
        coil[0],
    ] + coil[1:]
    tentacle("ArmCoil", pts, _fit_radii(pts, [], 0.060, 0.016), M, up_aim)

    # 7. Drape over the front of the counter
    pts = [
        emergence(0.45, z=1.00, rad=0.33),
        Vector((0.78, -0.42, 1.10)),
        Vector((1.02, -0.78, 1.05)),
        Vector((1.08, -1.02, 0.74)),
        Vector((0.96, -1.08, 0.50)),
        Vector((0.82, -1.02, 0.38)),
    ]
    tentacle("ArmDrape", pts, _fit_radii(pts, [], 0.066, 0.016), M, Vector((0.3, -1.0, 0.1)))

    # 8. Reaches up to straighten the toque
    pts = [
        emergence(-2.05, z=1.16, rad=0.22),
        Vector((-0.55, 0.10, 1.38)),
        Vector((-0.50, -0.02, 1.68)),
        Vector((-0.28, -0.02, 1.95)),
        Vector((-0.06, 0.02, 1.90)),
    ]
    tentacle("ArmHat", pts, _fit_radii(pts, [], 0.058, 0.015), M, cam_aim)


def _fit_radii(pts, radii, r0, r1):
    n = len(pts)
    if len(radii) == n:
        return radii
    return [r0 + (r1 - r0) * (i / max(1, n - 1)) for i in range(n)]


def hemisphere(name, loc, radius, open_dir, mat, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=14, radius=radius, calc_uvs=False)
    geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
    bmesh.ops.bisect_plane(
        bm, geom=geom, plane_co=(0, 0, 0), plane_no=(0, 0, 1), clear_outer=True, clear_inner=False
    )
    # Keep z<=0, opening toward +Z. Rotate +Z to open_dir.
    q = Vector((0, 0, 1)).rotation_difference(Vector(open_dir).normalized())
    S = Matrix.Diagonal((scale[0], scale[1], scale[2], 1.0))
    R = q.to_matrix().to_4x4()
    T = Matrix.Translation(Vector(loc))
    bmesh.ops.transform(bm, verts=bm.verts, matrix=T @ R @ S)
    # Cap the rim
    boundary = [v for v in bm.verts if v.is_boundary or v.is_wire or any(e.is_boundary for e in v.link_edges)]
    # After bisect, boundary verts are those on the plane. Collect via link_edges.
    boundary = []
    for v in bm.verts:
        if any(e.is_boundary for e in v.link_edges):
            boundary.append(v)
    if len(boundary) >= 3:
        center = sum((v.co for v in boundary), Vector()) / len(boundary)
        # Sort around the cap normal
        nrm = Vector(open_dir).normalized()
        x, y, _z = _basis_from_z(nrm)
        boundary.sort(key=lambda v: math.atan2((v.co - center).dot(y), (v.co - center).dot(x)))
        c = bm.verts.new(center)
        for i in range(len(boundary)):
            try:
                bm.faces.new((c, boundary[i], boundary[(i + 1) % len(boundary)]))
            except ValueError:
                pass
    return new_mesh(name, bm, mat=mat, smooth="smooth")


# ---------------------------------------------------------------------------
# Food
# ---------------------------------------------------------------------------

def build_food(M):
    build_bowl(M)
    build_noodles(M)
    build_toppings(M)
    build_steam(M)


def build_bowl(M):
    """Thick ceramic bowl spun from a profile, sitting on the counter."""
    segs = 40
    # (radius, z) from outer foot, up the outside, over the lip, down the inside
    profile = [
        (0.055, 0.004),
        (0.095, 0.000),
        (0.150, 0.014),
        (0.185, 0.048),
        (0.198, 0.090),
        (0.190, 0.108),
        (0.172, 0.092),
        (0.158, 0.055),
        (0.120, 0.030),
        (0.070, 0.022),
    ]
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        ring = []
        for i in range(segs):
            a = (i / segs) * math.tau
            ring.append(bm.verts.new((
                BOWL.x + math.cos(a) * r,
                BOWL.y + math.sin(a) * r,
                BOWL.z + z,
            )))
        rings.append(ring)
    for j in range(len(rings) - 1):
        for i in range(segs):
            i2 = (i + 1) % segs
            bm.faces.new((rings[j][i], rings[j][i2], rings[j + 1][i2], rings[j + 1][i]))
    # Foot cap and inner bottom cap
    for ring, z, outward_down in (
        (rings[0], profile[0][1], True),
        (rings[-1], profile[-1][1], False),
    ):
        c = bm.verts.new((BOWL.x, BOWL.y, BOWL.z + z))
        for i in range(segs):
            i2 = (i + 1) % segs
            if outward_down:
                bm.faces.new((c, ring[i2], ring[i]))
            else:
                bm.faces.new((c, ring[i], ring[i2]))
    me = bpy.data.meshes.new("RamenBowl")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M["bowl"])
    me.materials.append(M["bowl_blue"])
    obj = bpy.data.objects.new("RamenBowl", me)
    bpy.context.scene.collection.objects.link(obj)
    for p in me.polygons:
        c = p.center
        rad = math.hypot(c.x - BOWL.x, c.y - BOWL.y)
        zz = c.z - BOWL.z
        if 0.055 < zz < 0.098 and rad > 0.168:
            p.material_index = 1
    finish_mesh(obj, smooth="smooth")


def build_noodles(M):
    rnd = random.Random(11)
    for n in range(12):
        pts = []
        ang = rnd.random() * math.tau
        for k in range(7):
            ang += rnd.uniform(0.45, 1.15)
            rad = rnd.uniform(0.02, 0.125)
            z = BOWL.z + 0.078 + rnd.uniform(0.0, 0.035) + k * 0.003
            pts.append((
                BOWL.x + math.cos(ang) * rad,
                BOWL.y + math.sin(ang) * rad,
                z,
            ))
        tube(f"Noodle_{n}", pts, [0.0075] * len(pts), M["noodle"], sides=6, n_per_seg=3)


def build_toppings(M):
    # Broth surface and oil slick
    bpy.ops.mesh.primitive_circle_add(
        vertices=40, radius=0.162, fill_type="NGON", location=(BOWL.x, BOWL.y, BOWL.z + 0.072)
    )
    broth = bpy.context.active_object
    broth.name = "Broth"
    finish_mesh(broth, M["broth"], smooth="smooth")
    bpy.ops.mesh.primitive_circle_add(
        vertices=24, radius=0.06, fill_type="NGON", location=(BOWL.x + 0.04, BOWL.y - 0.02, BOWL.z + 0.078)
    )
    oil = bpy.context.active_object
    oil.name = "OilSlick"
    oil.scale = (1.3, 0.8, 1)
    oil.rotation_euler = (0, 0, 0.4)
    finish_mesh(oil, M["oil"], smooth="smooth")

    # Egg, cut face toward the camera
    egg_c = Vector((BOWL.x - 0.06, BOWL.y - 0.02, BOWL.z + 0.095))
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=1.0, calc_uvs=False)
    geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, 0), plane_no=(0, 1, 0), clear_inner=True, clear_outer=False)
    boundary = [v for v in bm.verts if any(e.is_boundary for e in v.link_edges)]
    if boundary:
        center = sum((v.co for v in boundary), Vector()) / len(boundary)
        boundary.sort(key=lambda v: math.atan2(v.co.z - center.z, v.co.x - center.x))
        cvert = bm.verts.new(center)
        for i in range(len(boundary)):
            try:
                bm.faces.new((cvert, boundary[i], boundary[(i + 1) % len(boundary)]))
            except ValueError:
                pass
    open_dir = Vector((0.25, -0.85, 0.4)).normalized()
    q = Vector((0, 1, 0)).rotation_difference(open_dir)
    S = Matrix.Diagonal((0.058, 0.046, 0.052, 1.0))
    bmesh.ops.transform(bm, verts=bm.verts, matrix=Matrix.Translation(egg_c) @ q.to_matrix().to_4x4() @ S)
    new_mesh("EggWhite", bm, mat=M["egg_w"], smooth="smooth")
    uvsphere("Yolk", egg_c + open_dir * 0.012, radius=0.030, scale=(1.0, 0.72, 1.0), mat=M["yolk"], seg=18, ring=12)
    uvsphere("YolkSpec", egg_c + open_dir * 0.03 + Vector((0.008, -0.004, 0.012)), radius=0.008, mat=M["highlight"], seg=8, ring=6)

    # Chashu
    for i, off in enumerate((Vector((0.055, 0.015, 0.10)), Vector((0.03, 0.045, 0.115)))):
        loc = BOWL + off
        rot = (1.15, 0.2 * i, 0.6 + 0.4 * i)
        cylinder(f"Chashu_{i}", loc, 0.050, 0.016, rot=rot, mat=M["chashu"], verts=20)
        cylinder(f"Fat_{i}", loc + Vector((0.012, -0.008, 0.008)), 0.028, 0.010, rot=rot, mat=M["fat"], verts=14)

    # Narutomaki
    naruto_loc = BOWL + Vector((0.00, -0.09, 0.100))
    axis = Vector((0.25, -1.0, 0.45)).normalized()
    rot = axis.to_track_quat("Z", "Y").to_euler()
    cylinder("Naruto", naruto_loc, 0.040, 0.022, rot=rot, mat=M["naruto"], verts=20)
    x, y, z = _basis_from_z(axis)
    spiral = []
    for i in range(22):
        t = i / 21
        ang = t * math.tau * 1.7
        rad = 0.004 + t * 0.028
        spiral.append(naruto_loc + z * 0.012 + x * math.cos(ang) * rad + y * math.sin(ang) * rad)
    tube("NarutoSpiral", spiral, [0.004] * len(spiral), M["naruto_p"], sides=5, n_per_seg=2)

    # Nori sheet standing at the back of the bowl
    nori_rows = []
    for j in range(8):
        v = j / 7
        row = []
        for i in range(6):
            u = i / 5
            x = BOWL.x - 0.02 + (u - 0.5) * 0.10
            yv = BOWL.y + 0.10 + 0.015 * math.sin(u * math.pi)
            z = BOWL.z + 0.07 + v * 0.13
            # curl the top
            yv -= 0.03 * v * v
            x += 0.01 * math.sin(v * math.pi) 
            row.append(Vector((x, yv, z)))
        nori_rows.append(row)
    grid_surface("Nori", nori_rows, M["nori"], solidify=0.003, smooth="smooth")

    # Scallions and menma
    rnd = random.Random(5)
    for i in range(14):
        ang = rnd.random() * math.tau
        rad = rnd.uniform(0.015, 0.13)
        pos = Vector((
            BOWL.x + math.cos(ang) * rad,
            BOWL.y + math.sin(ang) * rad,
            BOWL.z + 0.085,
        ))
        white = rnd.random() < 0.35
        rot = (rnd.uniform(1.2, 1.8), rnd.uniform(-0.3, 0.3), rnd.random() * math.tau)
        cylinder(
            f"Scallion_{i}",
            pos,
            0.006,
            rnd.uniform(0.016, 0.032),
            rot=rot,
            mat=M["scallion_w"] if white else M["scallion"],
            verts=6,
        )
    for i in range(4):
        pos = BOWL + Vector((-0.02 + i * 0.018, 0.05, 0.09))
        box(f"Menma_{i}", pos, (0.012, 0.045, 0.006), rot=(0.3, 0.4, 0.8 * i), mat=M["menma"], bevel=0.0)

    # Chili paste
    uvsphere("Chili", BOWL + Vector((0.09, -0.04, 0.09)), radius=0.022, scale=(1.1, 0.9, 0.7), mat=M["chili"], seg=12, ring=8)


def build_steam(M):
    # Pot steam is added with the pot. Bowl steam is in toppings.
    pass


def build_steam_column(M, origin, prefix, scale=1.0):
    # Soft puffs, not vertical rods.
    puffs = [
        (0.00, 0.00, 0.05, 0.030),
        (0.035, -0.012, 0.11, 0.024),
        (-0.028, 0.016, 0.17, 0.018),
        (0.012, -0.008, 0.23, 0.013),
    ]
    for i, (x, y, z, r) in enumerate(puffs):
        uvsphere(
            f"{prefix}_{i}",
            origin + Vector((x * scale, y * scale, z * scale)),
            radius=r * scale,
            scale=(1.0, 0.85, 0.7),
            mat=M["steam"],
            seg=12,
            ring=8,
        )


# ---------------------------------------------------------------------------
# Props
# ---------------------------------------------------------------------------

def build_props(M):
    # Cutting board on the near side of the counter
    board = Vector((0.95, -0.48, COUNTER_Z + 0.012))
    box("CuttingBoard", board, (0.36, 0.24, 0.018), rot=(0, 0, 0.15), mat=M["wood_l"], bevel=0.002)
    cylinder_between(
        "KnifeBlade",
        board + Vector((-0.02, -0.02, 0.02)),
        board + Vector((0.10, 0.06, 0.025)),
        0.004,
        M["metal"],
        verts=6,
    )
    # Give the blade a flat body
    box(
        "KnifeFlat",
        board + Vector((0.02, 0.01, 0.016)),
        (0.16, 0.035, 0.004),
        rot=(0, 0, 0.45),
        mat=M["metal"],
        bevel=0.0,
    )
    box(
        "KnifeHandle",
        board + Vector((-0.10, -0.07, 0.02)),
        (0.09, 0.022, 0.016),
        rot=(0, 0, 0.45),
        mat=M["wood_d"],
        bevel=0.001,
    )
    rnd = random.Random(3)
    for i in range(6):
        pos = board + Vector((rnd.uniform(-0.10, 0.10), rnd.uniform(-0.06, 0.06), 0.02))
        cylinder(
            f"BoardOnion_{i}",
            pos,
            0.007,
            rnd.uniform(0.03, 0.07),
            rot=(math.pi / 2, rnd.random(), rnd.random() * 3),
            mat=M["scallion"] if i % 2 == 0 else M["scallion_w"],
            verts=6,
        )

    # Condiments on the far side of the counter
    soy = Vector((-0.95, -0.72, COUNTER_Z))
    bottle(M, soy, "Soy", M["soy"], cap=M["mark_r"])
    bottle(M, soy + Vector((0.16, 0.04, 0)), "ChiliJar", M["chili"], cap=M["button"])
    # Small ceramic cup
    cup(M, Vector((-0.70, -0.78, COUNTER_Z)), "Yunomi")

    # Resting chopsticks
    cylinder_between(
        "RestStickA",
        (-0.48, -0.80, COUNTER_Z + 0.02),
        (-0.22, -0.70, COUNTER_Z + 0.025),
        0.007,
        M["wood_d"],
        verts=6,
    )
    cylinder_between(
        "RestStickB",
        (-0.48, -0.84, COUNTER_Z + 0.02),
        (-0.22, -0.74, COUNTER_Z + 0.025),
        0.007,
        M["wood_m"],
        verts=6,
    )

    # Back-counter bowl stack and stock pot (near side so the 3/4 camera sees them)
    stack_bowls(M, Vector((0.95, 0.82, 0.89)))
    stock_pot(M, Vector((-0.85, 0.90, 0.89)))
    # Extra cups on the back shelf
    cup(M, Vector((0.45, 0.78, 0.89)), "BackCupA")
    cup(M, Vector((0.62, 0.92, 0.89)), "BackCupB")

    # A tray
    box("Tray", (-0.55, 0.78, 0.925), (0.42, 0.28, 0.02), mat=M["wood_d"], bevel=0.002)


def bottle(M, loc, name, glass_mat, cap):
    uvsphere(name + "_body", loc + Vector((0, 0, 0.07)), radius=0.045, scale=(1.0, 1.0, 1.35), mat=glass_mat, seg=18, ring=12)
    cylinder(name + "_neck", loc + Vector((0, 0, 0.145)), 0.016, 0.06, mat=glass_mat, verts=12)
    cylinder(name + "_cap", loc + Vector((0, 0, 0.185)), 0.020, 0.028, mat=cap, verts=12)
    # Spout
    cylinder_between(name + "_spout", loc + Vector((0, 0, 0.15)), loc + Vector((0, -0.05, 0.145)), 0.010, glass_mat, verts=8)


def cup(M, loc, name):
    # Small handle-less yunomi: spun profile
    segs = 18
    profile = [
        (0.028, 0.0),
        (0.038, 0.01),
        (0.040, 0.045),
        (0.036, 0.07),
        (0.034, 0.078),
        (0.030, 0.07),
    ]
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        ring = []
        for i in range(segs):
            a = i / segs * math.tau
            ring.append(bm.verts.new((loc.x + math.cos(a) * r, loc.y + math.sin(a) * r, loc.z + z)))
        rings.append(ring)
    for j in range(len(rings) - 1):
        for i in range(segs):
            i2 = (i + 1) % segs
            bm.faces.new((rings[j][i], rings[j][i2], rings[j + 1][i2], rings[j + 1][i]))
    c = bm.verts.new((loc.x, loc.y, loc.z))
    for i in range(segs):
        i2 = (i + 1) % segs
        bm.faces.new((c, rings[0][i2], rings[0][i]))
    me = bpy.data.meshes.new(name)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M["ceramic"])
    me.materials.append(M["cup_blue"])
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    for p in me.polygons:
        if abs(p.center.z - (loc.z + 0.045)) < 0.012 and math.hypot(p.center.x - loc.x, p.center.y - loc.y) > 0.034:
            p.material_index = 1
    finish_mesh(obj, smooth="smooth")


def stack_bowls(M, loc):
    for i in range(4):
        z = loc.z + i * 0.018
        torus(f"StackBowl_{i}", (loc.x, loc.y, z + 0.02), 0.07 - i * 0.002, 0.012, mat=M["bowl"], maj_seg=20, min_seg=6)
        bpy.ops.mesh.primitive_circle_add(vertices=20, radius=0.06, fill_type="NGON", location=(loc.x, loc.y, z + 0.012))
        disc = bpy.context.active_object
        disc.name = f"StackBowlDisc_{i}"
        finish_mesh(disc, M["bowl"], smooth="smooth")


def stock_pot(M, loc):
    cylinder("PotBody", loc + Vector((0, 0, 0.09)), 0.16, 0.16, mat=M["copper"], verts=28)
    cylinder("PotRim", loc + Vector((0, 0, 0.17)), 0.17, 0.02, mat=M["copper"], verts=28)
    uvsphere("PotLid", loc + Vector((0, 0, 0.20)), radius=0.15, scale=(1.0, 1.0, 0.28), mat=M["copper"], seg=24, ring=10)
    uvsphere("PotKnob", loc + Vector((0, 0, 0.25)), radius=0.028, mat=M["wood_d"], seg=12, ring=8)
    torus("PotHandleL", loc + Vector((-0.18, 0, 0.10)), 0.04, 0.008, rot=(0, math.pi / 2, 0), mat=M["metal"], maj_seg=14, min_seg=6)
    torus("PotHandleR", loc + Vector((0.18, 0, 0.10)), 0.04, 0.008, rot=(0, math.pi / 2, 0), mat=M["metal"], maj_seg=14, min_seg=6)
    box("Burner", loc + Vector((0, 0, -0.02)), (0.28, 0.28, 0.04), mat=M["black"], bevel=0.002)


# ---------------------------------------------------------------------------
# Lights, world, cameras
# ---------------------------------------------------------------------------

def setup_world_and_render():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 854
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 86
    scene.render.image_settings.color_mode = "RGB"
    scene.eevee.taa_render_samples = 48
    scene.eevee.taa_samples = 16
    try:
        scene.eevee.use_raytracing = True
        scene.eevee.ray_tracing_options.trace_max_roughness = 0.45
        scene.eevee.ray_tracing_options.resolution_scale = "2"
    except Exception:
        pass
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.exposure = 0.25
    for look in ("AgX - Medium High Contrast", "AgX - Base Contrast"):
        try:
            scene.view_settings.look = look
            break
        except Exception:
            continue

    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    math_node = nt.nodes.new("ShaderNodeMath")
    math_node.operation = "MULTIPLY_ADD"
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (*C("#1A120E"), 1)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (*C("#0E1628"), 1)
    mid = ramp.color_ramp.elements.new(0.48)
    mid.color = (*C("#243044"), 1)
    nt.links.new(geo.outputs["Normal"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["Z"], math_node.inputs[0])
    math_node.inputs[1].default_value = 0.5
    math_node.inputs[2].default_value = 0.5
    nt.links.new(math_node.outputs["Value"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.85
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    # Key, fill, rim, overhead
    area_light("Key", (-1.55, -2.15, 2.35), 90, (1.0, 0.78, 0.58), 1.8, (0.0, -0.15, 1.25))
    area_light("Fill", (2.35, -1.35, 1.55), 22, (0.70, 0.82, 1.0), 2.0, (0.0, 0.0, 1.2))
    area_light("Rim", (-0.4, 1.9, 2.15), 70, (1.0, 0.70, 0.48), 1.3, (0.0, 0.15, 1.45))
    area_light("CoolRim", (1.8, 1.4, 1.8), 28, (0.55, 0.70, 1.0), 0.8, (0.0, 0.2, 1.4))
    area_light("Overhead", (0.1, -0.35, 2.25), 12, (1.0, 0.82, 0.62), 1.4, (0.0, -0.3, 1.1))
    area_light("FoodKick", (0.35, -1.15, 1.85), 10, (1.0, 0.85, 0.65), 0.45, (0.02, -0.5, 1.1))
    area_light("Face", (0.55, -2.05, 1.72), 16, (1.0, 0.90, 0.78), 0.85, (0.0, 0.12, 1.55))


def area_light(name, loc, energy, color, size, target):
    bpy.ops.object.light_add(type="AREA", location=loc)
    L = bpy.context.active_object
    L.name = name
    L.data.energy = energy
    L.data.color = color
    L.data.shape = "RECTANGLE"
    L.data.size = size
    L.data.size_y = size * 0.72
    look_at(L, target)
    return L


def add_camera(name, loc, target, lens):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.active_object
    cam.name = name
    cam.data.lens = lens
    cam.data.clip_start = 0.05
    cam.data.clip_end = 40
    look_at(cam, target)
    return cam


try:
    result = main()
except Exception:
    result = {"ok": False, "error": traceback.format_exc()}
