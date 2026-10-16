"""The octopus chef: mantle, face, toque, neckerchief and eight suckered arms."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import layout as L

OX, OY = L.OCT_X, L.OCT_Y
SY = 0.95   # front/back squash of the mantle

# colours (linear rgba)
C_TOP = hexc('#d0360b')
C_MID = hexc('#ee5a14')
C_BELLY = hexc('#f58a46')
C_SPOT = hexc('#a5220c')
C_FRECKLE = hexc('#f4845a')


def body_profile():
    ctrl = [(0.0, 0.86), (0.16, 0.88), (0.30, 0.95), (0.335, 1.03), (0.29, 1.12), (0.285, 1.24),
            (0.335, 1.40), (0.405, 1.56), (0.440, 1.72), (0.425, 1.88), (0.36, 2.03), (0.23, 2.14),
            (0.0, 2.19)]
    pts, _ = spline([(r, 0, z) for r, z in ctrl], 70, per=14)
    prof = [(max(p.x, 0.004), p.z) for p in pts]
    prof[0] = (0.0, prof[0][1])
    prof[-1] = (0.0, prof[-1][1])
    return prof


PROF = body_profile()


def body_radius(z):
    best = PROF[0]
    for i in range(len(PROF) - 1):
        (r0, z0), (r1, z1) = PROF[i], PROF[i + 1]
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0) if z1 > z0 else 0
            return r0 + (r1 - r0) * t
    return 0.0


def surf_y(x, z, off=0.0):
    """Front (-Y) surface of the mantle at (x, z)."""
    r = body_radius(z)
    q = max(0.0, 1 - (x / r) ** 2) if r > 1e-6 else 0.0
    return OY - SY * r * sqrt(q) - off


def skin_color(p):
    z = p.z
    c = mixc(C_MID, C_TOP, 0.75 * smoothstep(1.55, 2.12, z))
    front = max(0.0, -(p.y - OY) / 0.38) * smoothstep(1.0, 1.35, z) * (1 - smoothstep(1.7, 2.0, z))
    c = mixc(c, C_BELLY, 0.28 * front)
    n = noise.noise(Vector((p.x * 11 + 3, p.y * 11, p.z * 11)))
    if n > 0.30:
        c = mixc(c, C_SPOT, min(1.0, (n - 0.30) * 4) * 0.55)
    n2 = noise.noise(Vector((p.x * 17 - 5, p.y * 17 + 9, p.z * 17)))
    if n2 > 0.45:
        c = mixc(c, C_FRECKLE, min(1.0, (n2 - 0.45) * 5) * 0.3)
    return c


def build_body(root, M):
    pts, _ = spline([(r, 0, z) for r, z in PROF[::2]] + [(0.0, 0, PROF[-1][1])], 120, per=6)
    prof = [(max(p.x, 0.003), p.z) for p in pts]
    prof[0] = (0.0, prof[0][1])
    prof[-1] = (0.0, prof[-1][1])
    bm = lathe(prof, segs=176, sy=SY)
    bm.normal_update()
    for v in bm.verts:
        c = v.co + Vector((OX, OY, 0))
        n = noise.noise(c * 34.0) * 0.0032 + noise.noise(c * 71.0) * 0.0014
        fade = 1.0 - smoothstep(1.86, 1.98, c.z)   # no bumps under the hat
        v.co += v.normal * n * fade
    paint(bm, lambda co, nrm: skin_color(co + Vector((OX, OY, 0))))
    return make("Octopus_Mantle", bm, M['skin'], loc=(OX, OY, 0), parent=root)


# ----------------------------------------------------------------------------- face
def build_face(root, M):
    z_eye = 1.65
    for s in (-1, 1):
        ex = s * 0.185
        ey = surf_y(ex, z_eye) + 0.034
        R = 0.118
        yaw = s * radians(16)
        pitch = radians(-4)
        # eye frame: +Y local axis points to the front (-Y world)
        base = Matrix.Translation(Vector((OX + ex, ey, z_eye))) @ Euler((0, 0, yaw), 'XYZ').to_matrix().to_4x4()
        # sclera
        bm = sphere(R, R, R, u=32, v=20)
        ob = make(f"Eye_{'L' if s < 0 else 'R'}", bm, M['sclera'], parent=root)
        ob.matrix_world = base
        # iris + pupil built as caps facing -Y
        def cap(ang_deg, rad, sx=1.0, sz=1.0, name='cap', mt=None, zshift=0.0):
            segs = 28
            prof = []
            steps = 5
            bmx = bmesh.new()
            rings = []
            for i in range(steps + 1):
                a = radians(ang_deg) * i / steps
                ring = []
                if i == 0:
                    rings.append([bmx.verts.new((0, -rad, 0))])
                    continue
                for k in range(segs):
                    th = 2 * pi * k / segs
                    d = Vector((sin(a) * cos(th) * sx, -cos(a), sin(a) * sin(th) * sz))
                    d.normalize()
                    ring.append(bmx.verts.new(d * rad))
                rings.append(ring)
            for i in range(steps):
                a_, b_ = rings[i], rings[i + 1]
                for k in range(segs):
                    k2 = (k + 1) % segs
                    if len(a_) == 1:
                        bmx.faces.new((a_[0], b_[k], b_[k2]))
                    else:
                        bmx.faces.new((a_[k], a_[k2], b_[k2], b_[k]))
            return bmx
        iris = cap(47, R * 1.004, name='iris')
        oi = make(f"Iris_{'L' if s < 0 else 'R'}", iris, M['iris'], parent=root)
        oi.matrix_world = base
        pup = cap(22, R * 1.012, sx=1.45, sz=0.9, name='pupil')
        op = make(f"Pupil_{'L' if s < 0 else 'R'}", pup, M['pupil'], parent=root)
        op.matrix_world = base
        # glints
        for (gx, gz, gr) in ((-0.032 * s, 0.034, 0.0155), (0.030 * s, -0.030, 0.0075)):
            g = sphere(gr, gr * 0.8, gr, u=12, v=8)
            og = make(f"Glint_{'L' if s < 0 else 'R'}", g, M['glint'], parent=root)
            og.matrix_world = base @ Matrix.Translation(Vector((gx, -R * 0.985 + 0.0, gz)))
        # upper eyelid (skin coloured shell, clipped by a tilted plane)
        lid = sphere(R * 1.045, R * 1.045, R * 1.045, u=32, v=20)
        tilt = radians(-8) * s   # inner corner slightly lower
        n_local = Vector((0, 0, 1))
        n_local = Matrix.Rotation(tilt, 3, 'Y') @ n_local
        co = n_local * (R * 0.64)
        geom = list(lid.verts) + list(lid.edges) + list(lid.faces)
        bmesh.ops.bisect_plane(lid, geom=geom, plane_co=co, plane_no=n_local, clear_inner=True)
        edges = [e for e in lid.edges if e.is_boundary]
        if edges:
            try:
                bmesh.ops.contextual_create(lid, geom=edges)
            except Exception:
                pass
        bmesh.ops.recalc_face_normals(lid, faces=lid.faces[:])
        for v in lid.verts:
            v.co = v.co
        ol = make(f"Eyelid_{'L' if s < 0 else 'R'}", lid, M['skin_plain'], parent=root)
        ol.matrix_world = base

    # cheeks
    for s in (-1, 1):
        cx = s * 0.265
        cz = 1.50
        cy = surf_y(cx, cz) + 0.006
        bm = sphere(0.045, 0.012, 0.03, u=16, v=10)
        ob = make(f"Cheek_{'L' if s < 0 else 'R'}", bm, M['blush'], parent=root)
        ob.location = (OX + cx, cy, cz)
        ob.rotation_euler = (0, 0, s * radians(48))

    # mouth: small smile
    pts = []
    for i in range(9):
        t = i / 8
        x = (t - 0.5) * 0.17
        z = 1.355 - 0.05 * (1 - (2 * t - 1) ** 2) * -1 * -1
        z = 1.345 - 0.028 * (1 - (2 * t - 1) ** 2)
        pts.append(Vector((OX + x, surf_y(x, z) + 0.004, z)))
    bm = wire(pts, 0.0075, sides=6, n=30)
    make("Smile", bm, M['mouth'], parent=root)

    # handlebar moustache
    for s in (-1, 1):
        ctrl = []
        base = [(0.012, 0.000), (0.070, -0.022), (0.135, -0.026), (0.195, -0.004), (0.232, 0.036), (0.225, 0.080),
                (0.195, 0.090)]
        for (dx, dz) in base:
            x = s * dx
            z = 1.445 + dz
            ctrl.append(Vector((OX + x, surf_y(x, z) + 0.012 + (0.01 if dx > 0.14 else 0.0), z)))
        pts, tot = spline(ctrl, 46, per=12)
        rad = [0.002 + 0.034 * (1 - i / 45) ** 0.6 * (0.55 + 0.45 * sin(pi * min(1, i / 14))) for i in range(46)]
        rad = [max(0.006, r) for r in rad]
        bm, fr = tube(pts, rad, sides=10, under=(0, 0, 1))
        make(f"Moustache_{'L' if s < 0 else 'R'}", bm, M['moustache'], parent=root)


# ----------------------------------------------------------------------------- hat & scarf
def build_toque(root, M):
    # band + pleated puff as one lathe, rotated slightly for jauntiness
    prof = [(0.0, 1.950), (0.397, 1.950), (0.409, 1.965), (0.411, 2.02), (0.385, 2.24), (0.395, 2.255),
            (0.42, 2.30), (0.47, 2.37), (0.485, 2.46), (0.46, 2.55), (0.40, 2.63), (0.31, 2.69), (0.17, 2.715),
            (0.0, 2.72)]
    pts, _ = spline([(r, 0, z) for r, z in prof], 80, per=10)
    pr = [(max(p.x, 0.003), p.z) for p in pts]
    pr[0] = (0.0, pr[0][1])
    pr[-1] = (0.0, pr[-1][1])
    bm = lathe(pr, segs=96)
    for v in bm.verts:
        r = sqrt(v.co.x ** 2 + v.co.y ** 2)
        if r > 0.01 and v.co.z > 2.26:
            th = math.atan2(v.co.y, v.co.x)
            amp = 0.04 * smoothstep(2.26, 2.38, v.co.z) * (1 - 0.6 * smoothstep(2.55, 2.7, v.co.z))
            f = 1 + amp * sin(14 * th)
            v.co.x *= f
            v.co.y *= f
    paint(bm, lambda co, n: hexc('#fff7ea') if co.z > 2.26 else mixc(hexc('#fff7ea'), hexc('#e9dcc8'), 0.4))
    ob = make("Toque", bm, M['hat'], parent=root, sharp=None)
    # tilt about the head top
    piv = Vector((OX, OY, 2.0))
    ob.location = (OX, OY, 0)
    R = Matrix.Translation(piv) @ Euler((radians(-4), radians(4.5), 0), 'XYZ').to_matrix().to_4x4() @ Matrix.Translation(-piv)
    ob.matrix_world = R @ Matrix.Translation(Vector((OX, OY, 0)))
    # hat band stripe (thin red ring)
    bm = torus(0.405, 0.0075, segs=64, sides=8)
    ob2 = make("Toque_Stripe", bm, M['red'], parent=root)
    ob2.matrix_world = R @ Matrix.Translation(Vector((OX, OY, 2.075)))


def build_scarf(root, M):
    zc = 1.19
    r = body_radius(zc) + 0.012
    bm = torus(r, 0.034, segs=64, sides=12, sy=SY)
    ob = make("Neckerchief", bm, M['scarf'], loc=(OX, OY, zc), rot=(radians(-6), 0, 0), parent=root)
    # knot + tails at the front
    ky = surf_y(0.0, zc) - 0.034
    bm = sphere(0.045, 0.04, 0.04, u=16, v=10)
    make("Scarf_Knot", bm, M['scarf'], loc=(OX, ky - 0.0, zc - 0.01), parent=root)
    for s in (-1, 1):
        tail = [Vector((OX + s * 0.02, ky - 0.02, zc - 0.02)), Vector((OX + s * 0.05, ky - 0.03, zc - 0.08)),
                Vector((OX + s * 0.07, ky - 0.03, zc - 0.15))]
        pts, _ = spline(tail, 14)
        rad = [0.02 * (1 - 0.5 * i / 13) for i in range(14)]
        bm, _fr = tube(pts, rad, sides=8, under=(0, -1, 0), flat=0.5)
        make(f"Scarf_Tail_{'L' if s < 0 else 'R'}", bm, M['scarf'], parent=root)


# ----------------------------------------------------------------------------- arms
def sucker_proto():
    prof = [(1.02, -0.12), (1.05, 0.08), (1.0, 0.26), (0.88, 0.36), (0.72, 0.30), (0.55, 0.12), (0.30, 0.04),
            (0.0, 0.02)]
    return prof


def arm_color_fn(tip_mix=0.25):
    def fn(i, ca, sa, co):
        belly = smoothstep(0.05, 0.9, ca)
        c = mixc(C_MID, C_BELLY, belly * 0.4)
        c = mixc(c, C_TOP, 0.5 * smoothstep(-0.2, -0.95, ca))
        n = noise.noise(Vector((co.x * 13 + 7, co.y * 13, co.z * 13)))
        if n > 0.32:
            c = mixc(c, C_SPOT, min(1.0, (n - 0.32) * 4) * 0.5)
        return c
    return fn


def build_arm(name, ctrl, root, M, r0=0.09, r1=0.011, power=1.15, under=(0, -1, 0), twist=0.0,
              sucker_from=0.10, sucker_to=0.97, rows_angle=36, under_fn=None):
    dense = cr_dense(ctrl, 22)
    total_est = sum((dense[i + 1] - dense[i]).length for i in range(len(dense) - 1))
    n = max(40, int(total_est / 0.0085))
    pts, total = resample(dense, n)
    rad = [r1 + (r0 - r1) * (1 - i / (n - 1)) ** power for i in range(n)]
    bm, fr = tube(pts, rad, sides=16, under=under, twist=twist, color_fn=arm_color_fn(), cap_start=True,
                  under_fn=under_fn, bump=lambda pos, r: r * 0.04 * noise.noise(pos * 38.0))
    skin = make(name, bm, M['skin'], parent=root)
    # suckers
    sbm = bmesh.new()
    prof = sucker_proto()
    proto = lathe(prof, segs=12)
    s = sucker_from * total
    k = 0
    cnt = 0
    while s < sucker_to * total:
        f = s / total * (n - 1)
        i0 = min(int(f), n - 2)
        fl = f - i0
        p = fr[i0][0].lerp(fr[i0 + 1][0], fl)
        T = fr[i0][1].lerp(fr[i0 + 1][1], fl).normalized()
        N = fr[i0][2].lerp(fr[i0 + 1][2], fl).normalized()
        B = T.cross(N)
        r = rad[i0] + (rad[i0 + 1] - rad[i0]) * fl
        two = r > 0.032
        if two:
            ang = radians(rows_angle) * (1 if k % 2 == 0 else -1)
            sr = 0.40 * r
        else:
            ang = 0.0
            sr = 0.50 * r
        d = N * cos(ang) + B * sin(ang)
        Zx = d
        Xx = T - d * T.dot(d)
        Xx.normalize()
        Yx = Zx.cross(Xx)
        Mx = Matrix((Xx, Yx, Zx)).transposed().to_4x4()
        Mx.translation = p + d * (r * 0.985)
        Ms = Mx @ Matrix.Diagonal(Vector((sr, sr, sr * 0.85, 1)))
        src = proto.copy()
        add_bm(sbm, src, Ms)
        k += 1
        cnt += 1
        s += (0.95 if two else 1.9) * r * (1.0 if two else 1.0)
    proto.free()
    sk = make(name + "_Suckers", sbm, M['sucker'], parent=root)
    return skin, sk, total, cnt


def octo_mats():
    return {
        'skin': mat('Octo_Skin', '#ffffff', rough=0.42, spec=0.5, vcol='Color', coat=0.12),
        'skin_plain': mat('Octo_SkinPlain', '#e04a10', rough=0.42, spec=0.5, coat=0.12),
        'sclera': mat('Eye_White', '#fffaf0', rough=0.2, coat=0.3),
        'iris': mat('Eye_Iris', '#f0a31c', rough=0.3),
        'pupil': mat('Eye_Pupil', '#08080c', rough=0.35),
        'glint': mat('Eye_Glint', '#ffffff', rough=0.1, emit='#ffffff', emit_strength=2.0),
        'blush': mat('Octo_Blush', '#ff6f86', rough=0.6),
        'mouth': mat('Octo_Mouth', '#5e1a18', rough=0.4),
        'moustache': mat('Octo_Moustache', '#3b1f14', rough=0.55),
        'hat': mat('Chef_Hat', '#ffffff', rough=0.85, vcol='Color'),
        'red': mat('Chef_Red', '#c8202a', rough=0.5),
        'scarf': mat('Chef_Scarf', '#d0242c', rough=0.7),
        'sucker': mat('Octo_Sucker', '#f9c4ae', rough=0.35, spec=0.5, coat=0.2),
    }
