"""The eight arms, each interacting with something in the booth."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import layout as L
import octopus as O

OX, OY = L.OCT_X, L.OCT_Y


def root_pt(deg, rad=0.16, z=1.06):
    a = radians(deg)
    return Vector((OX + rad * cos(a), OY + rad * sin(a), z))


def axis_under(a0, a1, s_lo, s_hi, reach=0.075):
    """under_fn: points close to the (a0..a1) segment face the axis."""
    d = (a1 - a0)
    ln = d.length
    d = d / ln

    def fn(i, p):
        s = (p - a0).dot(d)
        c = a0 + d * s
        dist = (p - c).length
        if s_lo <= s <= s_hi and dist < reach:
            w = smoothstep(reach, reach * 0.55, dist)
            return (w, c - p)
        return (0.0, Vector((0, 0, 1)))
    return fn


def twist_ramp(t0, t1, ang):
    def fn(u):
        return ang * smoothstep(t0, t1, u)
    return fn


def spiral(center, r_a, r_b, turns, theta0, plane='xy', direction=1, n_per_turn=10):
    pts = []
    n = max(4, int(turns * n_per_turn))
    for i in range(n + 1):
        f = i / n
        th = theta0 + direction * 2 * pi * turns * f
        r = r_a + (r_b - r_a) * f
        a, b = r * cos(th), r * sin(th)
        if plane == 'xy':
            pts.append(center + Vector((a, b, 0)))
        else:
            pts.append(center + Vector((a, 0, b)))
    return pts


def build(root, M):
    arms = {}
    # --- tebo (noodle strainer) arm -------------------------------------------------------------
    S, D = L.TEBO_S, L.TEBO_DIR
    wrap = wrap_pts(S + D * 0.20, D, 0.046, 2.2, 0.27, phase=pi, ref=(-1, 0, 0))
    ctrl = [root_pt(195), Vector((-0.34, 0.20, 1.12)), Vector((-0.52, 0.10, 1.28)),
            Vector((-0.70, 0.10, 1.42))] + wrap
    ua = axis_under(S + D * 0.16, S + D * 0.52, 0.0, 0.40)
    arms['tebo'] = build_arm_safe("Arm_Tebo", ctrl, root, M, under=(0, -1, 0), under_fn=ua)

    # --- ladle arm ------------------------------------------------------------------------------
    S, D = L.LADLE_S, L.LADLE_DIR
    wrap = wrap_pts(S + D * 0.20, D, 0.046, 2.0, 0.24, phase=0.5, ref=(0, 1, 0))
    ctrl = [root_pt(150), Vector((-0.30, 0.46, 1.12)), Vector((-0.50, 0.62, 1.30)),
            Vector((-0.68, 0.70, 1.48))] + wrap
    ua = axis_under(S + D * 0.16, S + D * 0.50, 0.0, 0.40)
    arms['ladle'] = build_arm_safe("Arm_Ladle", ctrl, root, M, under=(0, -1, 0), under_fn=ua)

    # --- knife arm ------------------------------------------------------------------------------
    H0, H1 = L.KNIFE_H0, L.KNIFE_H1
    D = (H1 - H0).normalized()
    wrap = wrap_pts(H0 + D * 0.02, D, 0.038, 2.0, 0.13, phase=pi / 2, ref=(0, 0, 1))
    ctrl = [root_pt(22), Vector((0.34, 0.42, 1.18)), Vector((0.62, 0.40, 1.50)), Vector((0.90, 0.22, 1.66)),
            Vector((1.10, -0.10, 1.56))] + wrap
    ua = axis_under(H0 - D * 0.04, H1, 0.0, 0.2)
    arms['knife'] = build_arm_safe("Arm_Knife", ctrl, root, M, under=(0, -1, 0), under_fn=ua)

    # --- bowl arm: coil under the held bowl -----------------------------------------------------
    tilt = Matrix.Rotation(radians(18), 3, 'X')
    nrm = tilt @ Vector((0, 0, 1))
    c = L.HELD_BOWL + tilt @ Vector((0, 0, -0.018))
    coil = [c + tilt @ (p - c) for p in spiral(c, 0.10, 0.012, 1.45, radians(35), plane='xy', direction=1)]
    ctrl = [root_pt(308), Vector((0.20, 0.02, 1.10)), Vector((0.40, -0.10, 1.20)), Vector((0.62, -0.08, 1.34)),
            Vector((0.80, -0.20, 1.50)), coil[0] + Vector((0.07, 0.03, -0.02))] + coil
    ua = lambda i, p: ((1.0, nrm) if (p - c).length < 0.13 and (p - c).dot(nrm) > -0.03 else (0.0, nrm))
    arms['bowl'] = build_arm_safe("Arm_Bowl", ctrl, root, M, r1=0.017, under=(0, -1, 0), under_fn=ua)

    # --- waving arm -----------------------------------------------------------------------------
    cc = Vector((0.70, 0.45, 2.20))
    curl = spiral(cc, 0.085, 0.022, 1.25, radians(-70), plane='xz', direction=-1)
    ctrl = [root_pt(80), Vector((0.15, 0.62, 1.2)), Vector((0.42, 0.72, 1.55)), Vector((0.58, 0.68, 1.90)),
            curl[0] + Vector((0.0, 0.1, -0.12))] + curl
    arms['wave'] = build_arm_safe("Arm_Wave", ctrl, root, M, under=(0, -1, 0), twist=twist_ramp(0.55, 0.85, pi))

    # --- draping arms ---------------------------------------------------------------------------
    def drape(name, deg, xs, curl_dir, tw0=0.62, tw1=0.82):
        x0, x1, x2 = xs
        end = Vector((x2, -1.09, 0.70))
        cen = end + Vector((curl_dir * 0.075, -0.0, -0.10))
        curl = spiral(Vector((cen.x, -1.10, cen.z)), 0.085, 0.02, 1.3, radians(180 if curl_dir > 0 else 0), plane='xz',
                      direction=-curl_dir)
        ctrl = [root_pt(deg), Vector((x0 * 0.4, 0.0, 1.10)), Vector((x0, -0.30, 1.09)), Vector((x1, -0.62, 1.085)),
                Vector((x2, -0.90, 1.07)), Vector((x2, -1.02, 1.02)), Vector((x2, -1.07, 0.88)), end] + curl
        return build_arm_safe(name, ctrl, root, M, under=(0, 0, -1), twist=twist_ramp(tw0, tw1, pi))

    arms['d1'] = drape("Arm_Drape1", 238, (-0.30, -0.40, -0.44), -1)
    arms['d2'] = drape("Arm_Drape2", 272, (0.06, 0.16, 0.14), 1)

    # --- relaxed arm resting on the counter toward the left customer bowl ------------------------
    ctrl = [root_pt(215), Vector((-0.30, 0.10, 1.09)), Vector((-0.50, -0.12, 1.085)), Vector((-0.66, -0.34, 1.075)),
            Vector((-0.80, -0.50, 1.06))] + spiral(Vector((-0.80, -0.62, 1.04)), 0.115, 0.02, 1.4, radians(90),
                                                   plane='xy', direction=1)
    arms['rest'] = build_arm_safe("Arm_Rest", ctrl, root, M, under=(0, 0, -1), twist=twist_ramp(0.7, 0.9, pi))
    return arms


def build_arm_safe(name, ctrl, root, M, **kw):
    skin, suck, total, cnt = O.build_arm(name, ctrl, root, M, **kw)
    return {'skin': skin, 'suckers': suck, 'length': total, 'n_suckers': cnt}
