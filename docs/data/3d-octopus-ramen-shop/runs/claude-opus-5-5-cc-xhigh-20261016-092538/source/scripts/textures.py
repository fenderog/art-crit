# Procedurally generated image textures (pixels computed in Python, packed into the .blend
# so they also travel into the glTF export).
import bpy, math, random
from mathutils import Vector, noise


def _new_image(name, w, h):
    im = bpy.data.images.get(name)
    if im:
        bpy.data.images.remove(im)
    im = bpy.data.images.new(name, w, h, alpha=False)
    return im


def _finish(im, px):
    im.pixels.foreach_set(px)
    im.update()
    im.pack()
    return im


def wood_image(name, light, dark, size=256, rings=9.0, seed=0, knots=2):
    """Wood grain running along U. Periodic in U (cylindrical noise lookup)."""
    w = h = size
    px = [0.0] * (w * h * 4)
    rnd = random.Random(seed)
    off = Vector((rnd.uniform(0, 50), rnd.uniform(0, 50), rnd.uniform(0, 50)))
    knot_pos = [(rnd.random(), rnd.random()) for _ in range(knots)]
    R = 1.2
    for y in range(h):
        v = y / h
        for x in range(w):
            u = x / w
            a = 2 * math.pi * u
            p = Vector((math.cos(a) * R, math.sin(a) * R, v * 2.0)) + off
            warp = noise.noise(p * 0.7) * 0.45 + noise.noise(p * 2.5) * 0.10
            # knots bend the grain
            for (ku, kv) in knot_pos:
                du = min(abs(u - ku), 1 - abs(u - ku)) * 4.0
                dv = (v - kv)
                d2 = du * du + dv * dv * 30
                warp += 0.5 * math.exp(-d2 * 40)
            t = (v * rings + warp) % 1.0
            g = abs(t - 0.5) * 2.0
            g = g ** 4.0
            fine = noise.noise(Vector((math.cos(a) * 6, math.sin(a) * 6, v * 220)) + off) * 0.5 + 0.5
            k = min(max(0.42 * g + 0.38 * fine * fine, 0.0), 1.0)
            i = (y * w + x) * 4
            px[i] = light[0] + (dark[0] - light[0]) * k
            px[i + 1] = light[1] + (dark[1] - light[1]) * k
            px[i + 2] = light[2] + (dark[2] - light[2]) * k
            px[i + 3] = 1.0
    return _finish(_new_image(name, w, h), px)


def asphalt_image(name, base, size=256, seed=3):
    w = h = size
    px = [0.0] * (w * h * 4)
    rnd = random.Random(seed)
    off = Vector((rnd.uniform(0, 50), rnd.uniform(0, 50), 0))
    R = 1.0
    for y in range(h):
        v = y / h
        b = 2 * math.pi * v
        for x in range(w):
            u = x / w
            a = 2 * math.pi * u
            # torus-ish periodic lookup in both directions
            p = Vector((math.cos(a) * R, math.sin(a) * R + math.cos(b) * 0.0, 0)) + off
            q = Vector((math.cos(a) * 4, math.sin(a) * 4 + 7.0 * math.cos(b), 7.0 * math.sin(b))) + off
            n1 = noise.noise(q * 1.0) * 0.5 + 0.5
            n2 = noise.noise(q * 6.0) * 0.5 + 0.5
            k = 0.75 + 0.35 * n1 + 0.25 * (n2 - 0.5)
            spk = 1.0
            if rnd.random() < 0.04:
                spk = rnd.uniform(0.6, 1.5)
            i = (y * w + x) * 4
            px[i] = base[0] * k * spk
            px[i + 1] = base[1] * k * spk
            px[i + 2] = base[2] * k * spk
            px[i + 3] = 1.0
    return _finish(_new_image(name, w, h), px)


def fabric_image(name, color, size=128, seed=5):
    """Coarse woven cloth (noren)."""
    w = h = size
    px = [0.0] * (w * h * 4)
    rnd = random.Random(seed)
    for y in range(h):
        for x in range(w):
            weave = 0.92 + 0.08 * (((x // 2) + (y // 2)) % 2)
            n = 0.94 + 0.06 * rnd.random()
            # faint indigo dye unevenness
            s = 0.95 + 0.05 * math.sin(y / h * 2 * math.pi * 3 + math.sin(x / w * 2 * math.pi) * 0.7)
            k = weave * n * s
            i = (y * w + x) * 4
            px[i] = color[0] * k
            px[i + 1] = color[1] * k
            px[i + 2] = color[2] * k
            px[i + 3] = 1.0
    return _finish(_new_image(name, w, h), px)


def paper_image(name, color, size=128, seed=7):
    """Lantern paper with horizontal bamboo ribs."""
    w = h = size
    px = [0.0] * (w * h * 4)
    rnd = random.Random(seed)
    for y in range(h):
        v = y / h
        rib = math.sin(v * 2 * math.pi * 14)
        ribk = 0.78 if rib > 0.93 else 1.0
        for x in range(w):
            n = 0.93 + 0.07 * rnd.random()
            k = ribk * n
            i = (y * w + x) * 4
            px[i] = color[0] * k
            px[i + 1] = color[1] * k
            px[i + 2] = color[2] * k
            px[i + 3] = 1.0
    return _finish(_new_image(name, w, h), px)


def image_mat(name, image, rough=0.5, metal=0.0, coat=0.0, emit_image=False, emit_strength=0.0,
              bump=0.0, spec=0.5, uv_scale=None):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    p = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled'][0]
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = image
    tex.location = (-500, 200)
    tex.interpolation = 'Linear'
    nt.links.new(tex.outputs['Color'], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    p.inputs['Specular IOR Level'].default_value = spec
    if coat:
        p.inputs['Coat Weight'].default_value = coat
        p.inputs['Coat Roughness'].default_value = 0.1
    if emit_image:
        nt.links.new(tex.outputs['Color'], p.inputs['Emission Color'])
        p.inputs['Emission Strength'].default_value = emit_strength
    if bump > 0:
        bn = nt.nodes.new('ShaderNodeBump')
        bn.inputs['Strength'].default_value = bump
        bn.inputs['Distance'].default_value = 0.002
        nt.links.new(tex.outputs['Color'], bn.inputs['Height'])
        nt.links.new(bn.outputs['Normal'], p.inputs['Normal'])
        bn["render_only"] = True
    # average colour for viewport / fallback
    m["flat_color"] = [0.5, 0.5, 0.5]
    return m


def box_uv(ob, scale=1.0, grain=None, offset=None):
    """Planar box-projection UVs in object space, U follows the 'grain' axis
    (defaults to the object's longest dimension)."""
    me = ob.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers.active.data
    xs = [v.co for v in me.vertices]
    if grain is None:
        ext = [max(c[i] for c in xs) - min(c[i] for c in xs) for i in range(3)]
        grain = ext.index(max(ext))
    rnd = random.Random(hash(ob.name) & 0xffff)
    off = offset if offset is not None else (rnd.random(), rnd.random())
    for poly in me.polygons:
        n = poly.normal
        ax = max(range(3), key=lambda i: abs(n[i]))  # projection axis
        others = [i for i in range(3) if i != ax]
        if grain in others:
            ua = grain
            va = [i for i in others if i != grain][0]
        else:
            ua, va = others
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uv[li].uv = (co[ua] * scale + off[0], co[va] * scale + off[1])
