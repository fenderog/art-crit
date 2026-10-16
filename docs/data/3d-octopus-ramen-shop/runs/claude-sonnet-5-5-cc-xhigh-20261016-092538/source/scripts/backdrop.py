"""Render-only surroundings (night street backdrop). Not exported to the GLB."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

COLL = "RenderOnly"
PI_2 = pi / 2


def bokeh_mat(name, hx):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sub = nt.nodes.new('ShaderNodeVectorMath')
    sub.operation = 'SUBTRACT'
    sub.inputs[1].default_value = (0.5, 0.5, 0.0)
    ln = nt.nodes.new('ShaderNodeVectorMath')
    ln.operation = 'LENGTH'
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = 0.0
    mr.inputs['From Max'].default_value = 0.5
    mr.inputs['To Min'].default_value = 1.0
    mr.inputs['To Max'].default_value = 0.0
    mr.clamp = True
    pw = nt.nodes.new('ShaderNodeMath')
    pw.operation = 'POWER'
    pw.inputs[1].default_value = 0.55
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = hexc(hx)
    em.inputs['Strength'].default_value = 2.2
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(tc.outputs['UV'], sub.inputs[0])
    nt.links.new(sub.outputs['Vector'], ln.inputs[0])
    nt.links.new(ln.outputs['Value'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], pw.inputs[0])
    nt.links.new(pw.outputs['Value'], mx.inputs['Fac'])
    nt.links.new(tr.outputs['BSDF'], mx.inputs[1])
    nt.links.new(em.outputs['Emission'], mx.inputs[2])
    nt.links.new(mx.outputs['Shader'], out.inputs['Surface'])
    m.surface_render_method = 'BLENDED'
    MATS[name] = m
    return m


def add_disc(bm, c, r, segs=24):
    uv = bm.loops.layers.uv.verify()
    ctr = bm.verts.new(c)
    ring = [bm.verts.new(c + Vector((r * cos(2 * pi * k / segs), 0, r * sin(2 * pi * k / segs)))) for k in range(segs)]
    for k in range(segs):
        f = bm.faces.new((ctr, ring[k], ring[(k + 1) % segs]))
        a0, a1 = 2 * pi * k / segs, 2 * pi * (k + 1) / segs
        f.loops[0][uv].uv = (0.5, 0.5)
        f.loops[1][uv].uv = (0.5 + 0.5 * cos(a0), 0.5 + 0.5 * sin(a0))
        f.loops[2][uv].uv = (0.5 + 0.5 * cos(a1), 0.5 + 0.5 * sin(a1))


def _link(ob, coll):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    coll.objects.link(ob)


def build(seed=4):
    coll = bpy.data.collections.get(COLL) or bpy.data.collections.new(COLL)
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    rng = random.Random(seed)
    m_ground = mat('RO_Ground', '#0c1224', rough=0.35, spec=0.6)
    m_bld = [mat('RO_Bld_A', '#18224a', rough=0.9), mat('RO_Bld_B', '#1d2752', rough=0.9), mat('RO_Bld_C', '#141c40', rough=0.9)]
    m_warm = mat('RO_Win_Warm', '#ffc46a', rough=0.5, emit='#ffb84d', emit_strength=3.0)
    m_cool = mat('RO_Win_Cool', '#a8cdff', rough=0.5, emit='#8fbfff', emit_strength=2.4)
    m_lamp = mat('RO_Lamp', '#fff0c0', rough=0.5, emit='#ffd98a', emit_strength=14.0)
    m_pole = mat('RO_Pole', '#1c2030', rough=0.6)
    m_vm = mat('RO_Vending', '#e8eef7', rough=0.4, emit='#bcd8ff', emit_strength=2.2)
    m_vm_body = mat('RO_VendingBody', '#c82a2a', rough=0.4)

    objs = []
    # ground
    g = make("RO_Ground", box(80, 60, 0.2), m_ground, loc=(0, 15, -0.24))
    objs.append(g)
    # buildings (dark silhouettes) + bokeh city lights
    x = -24.0
    k = 0
    while x < 24:
        w = rng.uniform(2.6, 5.0)
        h = rng.uniform(5.0, 11.0)
        y = 10.0 + rng.uniform(0.0, 2.5)
        bm = box(w, 2.0, h, 0.0)
        b = make(f"RO_Building_{k}", bm, rng.choice(m_bld), loc=(x + w / 2, y, h / 2 - 0.1))
        objs.append(b)
        x += w + rng.uniform(0.0, 0.2)
        k += 1
    bok = {}
    palette = [('#ffb54d', 6), ('#ff8a3d', 2), ('#ffe3a0', 3), ('#7fb8ff', 2), ('#ff9ab8', 1)]
    for hx, wgt in palette:
        bok[hx] = bmesh.new()
    weights = [hx for hx, wgt in palette for _ in range(wgt)]
    for n in range(280):
        hx = rng.choice(weights)
        r = rng.uniform(0.08, 0.28) * (1.7 if rng.random() < 0.06 else 1.0)
        px = rng.uniform(-22, 22)
        pz = abs(rng.gauss(0, 1)) * 3.2 + 0.6 + (rng.random() * 5.0 if rng.random() < 0.3 else 0)
        add_disc(bok[hx], Vector((px, 8.0 - rng.random() * 0.6, pz)), r)
    for hx, wgt in palette:
        mm = bokeh_mat('RO_Bokeh_' + hx, hx)
        objs.append(make("RO_Bokeh_" + hx, bok[hx], mm, smooth=False))
    # street lamps in the mid-ground (bokeh)
    for i, (lx, ly) in enumerate(((-5.2, 3.5), (5.6, 4.2), (-9.0, 6.0), (9.5, 6.5))):
        objs.append(make(f"RO_LampPost_{i}", cyl(0.06, 0.05, 3.4, segs=8), m_pole, loc=(lx, ly, 0)))
        objs.append(make(f"RO_Lamp_{i}", sphere(0.22, 0.22, 0.22, u=14, v=10), m_lamp, loc=(lx, ly, 3.5)))
    # a glowing vending machine on the right
    vm = group("RO_Vending")
    objs.append(vm)
    objs.append(make("RO_VM_Body", box(0.95, 0.8, 2.0, 0.03), m_vm_body, loc=(4.1, 1.0, 1.0), parent=vm))
    objs.append(make("RO_VM_Face", box(0.78, 0.04, 1.4, 0.0), m_vm, loc=(4.1, 0.58, 1.25), parent=vm))
    for r in range(3):
        for c in range(4):
            col = rng.choice([hexc('#ff6a6a'), hexc('#6ad0ff'), hexc('#ffd24a'), hexc('#7dff9a')])
            mm = mat(f"RO_Drink_{r}_{c}", col, rough=0.5, emit=col, emit_strength=0.8)
            objs.append(make(f"RO_Drink_{r}_{c}", box(0.12, 0.03, 0.2, 0.0), mm, loc=(3.88 + c * 0.15, 0.555, 1.78 - r * 0.38), parent=vm))
    for o in objs:
        _link(o, coll)
        if o.parent:
            pass
    return coll


def set_visible(visible):
    coll = bpy.data.collections.get(COLL)
    if coll:
        coll.hide_viewport = not visible
        coll.hide_render = not visible
