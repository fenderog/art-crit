#!/usr/bin/env python3
"""
generate_art.py - Generates a masterpiece SVG illustration of an octopus chef at a ramen booth.
"""

import math
import os
import subprocess
import shutil

def pt_str(p):
    return f"{p[0]:.2f},{p[1]:.2f}"

def cubic_point(p0, p1, p2, p3, t):
    mt = 1 - t
    x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
    y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
    return (x, y)

def cubic_tangent(p0, p1, p2, p3, t):
    mt = 1 - t
    dx = 3 * mt**2 * (p1[0] - p0[0]) + 6 * mt * t * (p2[0] - p1[0]) + 3 * t**2 * (p3[0] - p2[0])
    dy = 3 * mt**2 * (p1[1] - p0[1]) + 6 * mt * t * (p2[1] - p1[1]) + 3 * t**2 * (p3[1] - p2[1])
    l = math.hypot(dx, dy)
    if l == 0:
        return (1.0, 0.0)
    return (dx / l, dy / l)

def sample_multi_bezier(segments, num_samples=60):
    total_segs = len(segments)
    pts = []
    tans = []
    for i in range(num_samples + 1):
        global_t = (i / num_samples) * total_segs
        seg_idx = min(int(global_t), total_segs - 1)
        local_t = global_t - seg_idx
        if seg_idx == total_segs - 1 and local_t > 1.0:
            local_t = 1.0
        p0, p1, p2, p3 = segments[seg_idx]
        pts.append(cubic_point(p0, p1, p2, p3, local_t))
        tans.append(cubic_tangent(p0, p1, p2, p3, local_t))
    return pts, tans

def make_spline_tentacle(segments, start_w, end_w, flip_suckers=False, num_suckers=10, sucker_scale=1.0):
    num_samples = 60
    spine, tangents = sample_multi_bezier(segments, num_samples=num_samples)
    normals = []
    widths = []

    for i in range(num_samples + 1):
        t = i / num_samples
        tan = tangents[i]
        norm = (-tan[1], tan[0])
        w = start_w * ((1.0 - t * 0.88) ** 0.85) + end_w * (t * 0.88)
        normals.append(norm)
        widths.append(w)

    left_side = []
    right_side = []
    for i in range(num_samples + 1):
        pt = spine[i]
        norm = normals[i]
        w = widths[i]
        left_side.append((pt[0] + norm[0] * w * 0.5, pt[1] + norm[1] * w * 0.5))
        right_side.append((pt[0] - norm[0] * w * 0.5, pt[1] - norm[1] * w * 0.5))

    d = [f"M {pt_str(left_side[0])}"]
    for pt in left_side[1:]:
        d.append(f"L {pt_str(pt)}")
    tip_tan = tangents[-1]
    tip_pt = spine[-1]
    tip_ext = (tip_pt[0] + tip_tan[0] * end_w * 0.45, tip_pt[1] + tip_tan[1] * end_w * 0.45)
    d.append(f"Q {pt_str(tip_ext)} {pt_str(right_side[-1])}")
    for pt in reversed(right_side[:-1]):
        d.append(f"L {pt_str(pt)}")
    d.append("Z")
    body_path = " ".join(d)

    # Dorsal Highlight stripe
    d_hi = []
    hi_sign = 1.0 if flip_suckers else -1.0
    for i in range(num_samples + 1):
        pt = spine[i]
        norm = normals[i]
        w = widths[i]
        p_edge = (pt[0] + hi_sign * norm[0] * (w * 0.38), pt[1] + hi_sign * norm[1] * (w * 0.38))
        if i == 0:
            d_hi.append(f"M {pt_str(p_edge)}")
        else:
            d_hi.append(f"L {pt_str(p_edge)}")
    for i in reversed(range(num_samples + 1)):
        pt = spine[i]
        norm = normals[i]
        w = widths[i]
        p_in = (pt[0] + hi_sign * norm[0] * (w * 0.12), pt[1] + hi_sign * norm[1] * (w * 0.12))
        d_hi.append(f"L {pt_str(p_in)}")
    d_hi.append("Z")
    hi_path = " ".join(d_hi)

    # Ventral Underbelly stripe
    d_under = []
    sign = -1.0 if flip_suckers else 1.0
    for i in range(num_samples + 1):
        pt = spine[i]
        norm = normals[i]
        w = widths[i]
        p_edge = (pt[0] + sign * norm[0] * (w * 0.49), pt[1] + sign * norm[1] * (w * 0.49))
        if i == 0:
            d_under.append(f"M {pt_str(p_edge)}")
        else:
            d_under.append(f"L {pt_str(p_edge)}")
    for i in reversed(range(num_samples + 1)):
        pt = spine[i]
        norm = normals[i]
        w = widths[i]
        p_in = (pt[0] + sign * norm[0] * (w * 0.08), pt[1] + sign * norm[1] * (w * 0.08))
        d_under.append(f"L {pt_str(p_in)}")
    d_under.append("Z")
    under_path = " ".join(d_under)

    # Suction cups along ventral edge
    suckers = []
    sucker_ts = [0.12 + 0.80 * (k / (num_suckers - 1)) for k in range(num_suckers)]
    for t_s in sucker_ts:
        idx_float = t_s * num_samples
        idx_low = min(int(idx_float), num_samples - 1)
        interp = idx_float - idx_low
        pt_a, pt_b = spine[idx_low], spine[min(idx_low + 1, num_samples)]
        tan_a, tan_b = tangents[idx_low], tangents[min(idx_low + 1, num_samples)]
        w_a, w_b = widths[idx_low], widths[min(idx_low + 1, num_samples)]

        pt = (pt_a[0] + (pt_b[0] - pt_a[0]) * interp, pt_a[1] + (pt_b[1] - pt_a[1]) * interp)
        tan = (tan_a[0] + (tan_b[0] - tan_a[0]) * interp, tan_a[1] + (tan_b[1] - tan_a[1]) * interp)
        l = math.hypot(tan[0], tan[1]) or 1.0
        tan = (tan[0] / l, tan[1] / l)
        norm = (-tan[1], tan[0])
        w = w_a + (w_b - w_a) * interp

        edge_pt = (pt[0] + sign * norm[0] * (w * 0.47), pt[1] + sign * norm[1] * (w * 0.47))
        s_radius = max(3.5, (w * 0.32) * sucker_scale)
        angle = math.degrees(math.atan2(sign * norm[1], sign * norm[0]))
        suckers.append({
            'cx': edge_pt[0],
            'cy': edge_pt[1],
            'rx': s_radius * 1.15,
            'ry': s_radius * 0.75,
            'angle': angle
        })

    return body_path, under_path, hi_path, suckers

def render_tentacle_svg(t_data, body_grad="url(#tentacleGrad)", under_grad="url(#suckerRimGrad)"):
    body_p, under_p, hi_p, suckers = t_data
    parts = []
    parts.append(f'<path d="{body_p}" fill="{body_grad}" stroke="#4a040b" stroke-width="3.5" stroke-linejoin="round"/>')
    parts.append(f'<path d="{under_p}" fill="{under_grad}" opacity="0.85"/>')
    parts.append(f'<path d="{hi_p}" fill="#ff9999" opacity="0.4" filter="url(#softBlur)"/>')
    for s in suckers:
        rot = f'transform="rotate({s["angle"]:.1f} {s["cx"]:.1f} {s["cy"]:.1f})"'
        parts.append(f'<g {rot}>')
        parts.append(f'<ellipse cx="{s["cx"]:.1f}" cy="{s["cy"]:.1f}" rx="{s["rx"]:.1f}" ry="{s["ry"]:.1f}" fill="url(#suckerOuterGrad)" stroke="#781d24" stroke-width="1.8"/>')
        parts.append(f'<ellipse cx="{s["cx"]+s["rx"]*0.14:.1f}" cy="{s["cy"]:.1f}" rx="{s["rx"]*0.56:.1f}" ry="{s["ry"]*0.54:.1f}" fill="url(#suckerPitGrad)"/>')
        parts.append(f'<circle cx="{s["cx"]-s["rx"]*0.28:.1f}" cy="{s["cy"]-s["ry"]*0.22:.1f}" r="{max(1.2, s["ry"]*0.26):.1f}" fill="#ffffff" opacity="0.9"/>')
        parts.append('</g>')
    return "\n".join(parts)

def build_scene():
    w, h = 1600, 1200
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="100%" height="100%">')

    # DEFS
    svg.append('<defs>')

    # Filters
    svg.append('''
    <filter id="softBlur" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3.5"/>
    </filter>
    <filter id="glowFilter" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="10" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="lanternGlowFilter" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="32" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="dropShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="3" dy="6" stdDeviation="4.5" flood-color="#050811" flood-opacity="0.6"/>
    </filter>
    <filter id="deepShadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="12" stdDeviation="10" flood-color="#020617" flood-opacity="0.8"/>
    </filter>
    <filter id="steamFilter" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8"/>
    </filter>
    ''')

    # Gradients
    svg.append('''
    <!-- Background Night Sky -->
    <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#050811"/>
      <stop offset="40%" stop-color="#0c1222"/>
      <stop offset="75%" stop-color="#19153e"/>
      <stop offset="100%" stop-color="#280e54"/>
    </linearGradient>

    <!-- Wood Textures -->
    <linearGradient id="roofWoodGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1a0f09"/>
      <stop offset="60%" stop-color="#2b1810"/>
      <stop offset="100%" stop-color="#140b07"/>
    </linearGradient>
    <linearGradient id="roofTileGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#28170e"/>
      <stop offset="50%" stop-color="#422619"/>
      <stop offset="100%" stop-color="#1f110a"/>
    </linearGradient>
    <linearGradient id="beamGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#361f12"/>
      <stop offset="35%" stop-color="#4e2f1b"/>
      <stop offset="80%" stop-color="#25140b"/>
      <stop offset="100%" stop-color="#140a06"/>
    </linearGradient>
    <linearGradient id="counterTopGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#f6a96c"/>
      <stop offset="15%" stop-color="#de8740"/>
      <stop offset="65%" stop-color="#a45c27"/>
      <stop offset="100%" stop-color="#643311"/>
    </linearGradient>
    <linearGradient id="counterFrontGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#4d2711"/>
      <stop offset="40%" stop-color="#311809"/>
      <stop offset="100%" stop-color="#150803"/>
    </linearGradient>
    <linearGradient id="slatWoodGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#24160e"/>
      <stop offset="50%" stop-color="#382418"/>
      <stop offset="100%" stop-color="#1a0f09"/>
    </linearGradient>
    <linearGradient id="menuWoodGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#fde68a"/>
      <stop offset="15%" stop-color="#f59e0b"/>
      <stop offset="85%" stop-color="#b45309"/>
      <stop offset="100%" stop-color="#78350f"/>
    </linearGradient>

    <!-- Lantern Gradients -->
    <radialGradient id="lanternRadial" cx="45%" cy="38%" r="66%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="20%" stop-color="#fef08a"/>
      <stop offset="45%" stop-color="#ef4444"/>
      <stop offset="80%" stop-color="#b91c1c"/>
      <stop offset="100%" stop-color="#550505"/>
    </radialGradient>
    <radialGradient id="lanternHalo" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.55"/>
      <stop offset="45%" stop-color="#ea580c" stop-opacity="0.3"/>
      <stop offset="75%" stop-color="#dc2626" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#dc2626" stop-opacity="0"/>
    </radialGradient>

    <!-- Noren Indigo Curtain -->
    <linearGradient id="norenGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1d3557"/>
      <stop offset="50%" stop-color="#152744"/>
      <stop offset="100%" stop-color="#0c182c"/>
    </linearGradient>

    <!-- Octopus Flesh & Skin - Radiant Coral Crimson -->
    <linearGradient id="tentacleGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ff7b7b"/>
      <stop offset="35%" stop-color="#e63946"/>
      <stop offset="75%" stop-color="#c1121f"/>
      <stop offset="100%" stop-color="#6a040f"/>
    </linearGradient>
    <radialGradient id="octopusHeadGrad" cx="42%" cy="36%" r="78%">
      <stop offset="0%" stop-color="#ff9999"/>
      <stop offset="30%" stop-color="#ff4d4d"/>
      <stop offset="70%" stop-color="#e63946"/>
      <stop offset="92%" stop-color="#bd1023"/>
      <stop offset="100%" stop-color="#8a0014"/>
    </radialGradient>
    <linearGradient id="suckerRimGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffe6d9"/>
      <stop offset="100%" stop-color="#fbcfe8"/>
    </linearGradient>
    <radialGradient id="suckerOuterGrad" cx="35%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="45%" stop-color="#fed7aa"/>
      <stop offset="85%" stop-color="#f472b6"/>
      <stop offset="100%" stop-color="#be185d"/>
    </radialGradient>
    <radialGradient id="suckerPitGrad" cx="45%" cy="45%" r="55%">
      <stop offset="0%" stop-color="#9d174d"/>
      <stop offset="70%" stop-color="#700934"/>
      <stop offset="100%" stop-color="#470420"/>
    </radialGradient>

    <!-- Eye Gradients -->
    <radialGradient id="eyeIris" cx="40%" cy="38%" r="55%">
      <stop offset="0%" stop-color="#fef9c3"/>
      <stop offset="35%" stop-color="#f59e0b"/>
      <stop offset="75%" stop-color="#b45309"/>
      <stop offset="100%" stop-color="#3d1302"/>
    </radialGradient>

    <!-- Chef Hat & Headband -->
    <linearGradient id="toqueGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="50%" stop-color="#f8fafc"/>
      <stop offset="85%" stop-color="#e2e8f0"/>
      <stop offset="100%" stop-color="#cbd5e1"/>
    </linearGradient>
    <linearGradient id="hachimakiGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="40%" stop-color="#f8fafc"/>
      <stop offset="75%" stop-color="#e2e8f0"/>
      <stop offset="100%" stop-color="#cbd5e1"/>
    </linearGradient>
    <linearGradient id="apronGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="65%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#020617"/>
    </linearGradient>
    <linearGradient id="trayWoodGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2d1a10"/>
      <stop offset="60%" stop-color="#1c0f08"/>
      <stop offset="100%" stop-color="#0a0503"/>
    </linearGradient>

    <!-- Metal Stockpot & Knife -->
    <linearGradient id="potSteelGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#334155"/>
      <stop offset="12%" stop-color="#94a3b8"/>
      <stop offset="32%" stop-color="#f1f5f9"/>
      <stop offset="55%" stop-color="#cbd5e1"/>
      <stop offset="80%" stop-color="#64748b"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <radialGradient id="potBrothGrad" cx="50%" cy="45%" r="55%">
      <stop offset="0%" stop-color="#fef9c3"/>
      <stop offset="25%" stop-color="#fde047"/>
      <stop offset="60%" stop-color="#ca8a04"/>
      <stop offset="90%" stop-color="#854d0e"/>
      <stop offset="100%" stop-color="#451a03"/>
    </radialGradient>
    <linearGradient id="bladeGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="35%" stop-color="#f1f5f9"/>
      <stop offset="70%" stop-color="#cbd5e1"/>
      <stop offset="100%" stop-color="#64748b"/>
    </linearGradient>

    <!-- Centerpiece Ramen Bowl Gradients -->
    <linearGradient id="bowlOuterGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#334155"/>
      <stop offset="20%" stop-color="#1e293b"/>
      <stop offset="70%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#020617"/>
    </linearGradient>
    <radialGradient id="ramenBrothGrad" cx="48%" cy="45%" r="55%">
      <stop offset="0%" stop-color="#fef08a"/>
      <stop offset="24%" stop-color="#eab308"/>
      <stop offset="58%" stop-color="#ca8a04"/>
      <stop offset="85%" stop-color="#854d0e"/>
      <stop offset="100%" stop-color="#3a1301"/>
    </radialGradient>
    <radialGradient id="eggYolkGrad" cx="36%" cy="34%" r="62%">
      <stop offset="0%" stop-color="#fffbeb"/>
      <stop offset="18%" stop-color="#fde047"/>
      <stop offset="52%" stop-color="#f97316"/>
      <stop offset="85%" stop-color="#c2410c"/>
      <stop offset="100%" stop-color="#831843"/>
    </radialGradient>
    <linearGradient id="eggWhiteGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#fffbeb"/>
      <stop offset="45%" stop-color="#fef08a"/>
      <stop offset="85%" stop-color="#e2cf9d"/>
      <stop offset="100%" stop-color="#c4a572"/>
    </linearGradient>
    <radialGradient id="chashuGrad" cx="42%" cy="42%" r="56%">
      <stop offset="0%" stop-color="#fed7aa"/>
      <stop offset="30%" stop-color="#f97316"/>
      <stop offset="68%" stop-color="#c2410c"/>
      <stop offset="90%" stop-color="#7c2d12"/>
      <stop offset="100%" stop-color="#3d1302"/>
    </radialGradient>
    <linearGradient id="noriGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#1b2923"/>
      <stop offset="50%" stop-color="#0f1a15"/>
      <stop offset="100%" stop-color="#070c09"/>
    </linearGradient>
    <linearGradient id="steamGrad" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.6"/>
      <stop offset="55%" stop-color="#ffffff" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#e0f2fe" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="soupPourGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.85"/>
      <stop offset="50%" stop-color="#fef08a" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#d97706" stop-opacity="0.85"/>
    </linearGradient>
    ''')

    # Patterns
    svg.append('''
    <pattern id="raimonPattern" width="24" height="12" patternUnits="userSpaceOnUse">
      <path d="M 2 2 H 14 V 10 H 6 V 6 H 10" fill="none" stroke="#dc2626" stroke-width="2.2" stroke-linecap="square"/>
      <path d="M 14 10 H 22 V 2 H 18" fill="none" stroke="#fbbf24" stroke-width="2.2" stroke-linecap="square"/>
    </pattern>
    <pattern id="wavePattern" width="40" height="20" patternUnits="userSpaceOnUse">
      <path d="M 0 20 A 20 20 0 0 1 40 20 M 5 20 A 15 15 0 0 1 35 20 M 10 20 A 10 10 0 0 1 30 20" fill="none" stroke="#38bdf8" stroke-width="1.2" opacity="0.35"/>
      <path d="M 20 10 A 20 20 0 0 1 60 10 M 25 10 A 15 15 0 0 1 55 10" fill="none" stroke="#38bdf8" stroke-width="1.2" opacity="0.35"/>
    </pattern>
    ''')

    svg.append('</defs>')

    # -------------------------------------------------------------
    # 1. BACKGROUND & ENVIRONMENT
    # -------------------------------------------------------------
    svg.append('<!-- BACKGROUND -->')
    svg.append(f'<rect width="{w}" height="{h}" fill="url(#skyGrad)"/>')

    bokeh_lights = [
        (200, 240, 48, "#fbbf24", 0.16), (280, 180, 28, "#f43f5e", 0.18),
        (350, 260, 38, "#38bdf8", 0.14), (520, 190, 52, "#fbbf24", 0.15),
        (650, 230, 32, "#a855f7", 0.18), (950, 200, 42, "#f97316", 0.15),
        (1120, 250, 36, "#ec4899", 0.16), (1240, 190, 50, "#fbbf24", 0.19),
        (1380, 240, 32, "#38bdf8", 0.16), (1480, 170, 42, "#f43f5e", 0.18)
    ]
    svg.append('<g id="bokeh" filter="url(#glowFilter)">')
    for bx, by, br, bc, bo in bokeh_lights:
        svg.append(f'<circle cx="{bx}" cy="{by}" r="{br}" fill="{bc}" opacity="{bo}"/>')
    svg.append('</g>')

    # Stall backdrop: vertical wooden slats
    svg.append('<g id="stallBackdrop">')
    for sx in range(160, 1440, 28):
        svg.append(f'<rect x="{sx}" y="190" width="22" height="640" fill="url(#slatWoodGrad)" stroke="#110804" stroke-width="1.2"/>')
        svg.append(f'<line x1="{sx+2}" y1="190" x2="{sx+2}" y2="830" stroke="#5a3d2c" stroke-width="0.8" opacity="0.6"/>')
    svg.append('</g>')

    # Authentic Wooden Menu Plaques (Kifuda 木札)
    menu_items = [
        (480, 370, "極上豚骨"),
        (540, 370, "特製拉麺"),
        (1020, 370, "自家製麺"),
        (1080, 370, "味玉追加")
    ]
    svg.append('<!-- HANGING WOODEN MENU PLAQUES -->')
    for mx, my, mtext in menu_items:
        svg.append(f'<g filter="url(#dropShadow)">')
        svg.append(f'<line x1="{mx+18}" y1="{my-20}" x2="{mx+18}" y2="{my}" stroke="#dc2626" stroke-width="2"/>')
        svg.append(f'<rect x="{mx}" y="{my}" width="36" height="135" rx="4" fill="url(#menuWoodGrad)" stroke="#451a03" stroke-width="2"/>')
        svg.append(f'<circle cx="{mx+18}" cy="{my+10}" r="3" fill="#1e293b"/>')
        for c_idx, char in enumerate(mtext):
            svg.append(f'<text x="{mx+18}" y="{my+36+c_idx*26}" font-family="serif, Klee One, sans-serif" font-weight="900" font-size="20" fill="#18181b" text-anchor="middle">{char}</text>')
        svg.append('</g>')

    # Timber Columns & Beams
    svg.append('<!-- TIMBER COLUMNS -->')
    svg.append('<rect x="110" y="80" width="55" height="980" fill="url(#beamGrad)" stroke="#0b0502" stroke-width="3" filter="url(#dropShadow)"/>')
    svg.append('<line x1="116" y1="80" x2="116" y2="1060" stroke="#8d5635" stroke-width="1.5" opacity="0.6"/>')
    svg.append('<rect x="1435" y="80" width="55" height="980" fill="url(#beamGrad)" stroke="#0b0502" stroke-width="3" filter="url(#dropShadow)"/>')
    svg.append('<line x1="1441" y1="80" x2="1441" y2="1060" stroke="#8d5635" stroke-width="1.5" opacity="0.6"/>')

    # Cross timber beam
    svg.append('<rect x="80" y="145" width="1440" height="45" fill="url(#beamGrad)" stroke="#0b0502" stroke-width="3" filter="url(#dropShadow)"/>')
    svg.append('<line x1="80" y1="149" x2="1520" y2="149" stroke="#8d5635" stroke-width="2" opacity="0.7"/>')
    for jx in [137, 440, 800, 1160, 1462]:
        svg.append(f'<rect x="{jx-16}" y="142" width="32" height="52" fill="#1e293b" stroke="#0f172a" stroke-width="2"/>')
        svg.append(f'<circle cx="{jx}" cy="154" r="4" fill="#64748b" stroke="#0f172a" stroke-width="1.2"/>')
        svg.append(f'<circle cx="{jx}" cy="182" r="4" fill="#64748b" stroke="#0f172a" stroke-width="1.2"/>')

    # Yatai Slanted Roof Awning
    svg.append('<!-- ROOF AWNING -->')
    svg.append('<polygon points="40,30 1560,30 1600,145 0,145" fill="url(#roofWoodGrad)" stroke="#0b0502" stroke-width="3"/>')
    for rx in range(30, 1580, 52):
        svg.append(f'<polygon points="{rx+10},30 {rx+46},30 {rx+56},145 {rx-2},145" fill="url(#roofTileGrad)" stroke="#0e0704" stroke-width="1.5"/>')
        svg.append(f'<line x1="{rx+28}" y1="35" x2="{rx+27}" y2="140" stroke="#784528" stroke-width="1.5" opacity="0.5"/>')
    svg.append('<rect x="0" y="140" width="1600" height="15" fill="#180e08" stroke="#060302" stroke-width="2"/>')
    svg.append('<line x1="0" y1="142" x2="1600" y2="142" stroke="#9a5a35" stroke-width="1.8"/>')

    # Bamboo hanging pole
    svg.append('<rect x="130" y="194" width="1340" height="12" rx="4" fill="#d97706" stroke="#451a03" stroke-width="2"/>')
    for bx in range(160, 1460, 70):
        svg.append(f'<line x1="{bx}" y1="194" x2="{bx}" y2="206" stroke="#78350f" stroke-width="2"/>')

    # Noren Curtains
    svg.append('<!-- NOREN CURTAINS -->')
    noren_x_positions = [
        (165, 230), (415, 230), (665, 230), (915, 230), (1165, 230)
    ]
    noren_labels = ["拉", "麺", "蛸", "吉", "堂"]
    for idx, (nx, nw) in enumerate(noren_x_positions):
        svg.append(f'<rect x="{nx+25}" y="188" width="18" height="14" rx="3" fill="#cbd5e1" stroke="#334155" stroke-width="1.5"/>')
        svg.append(f'<rect x="{nx+nw-43}" y="188" width="18" height="14" rx="3" fill="#cbd5e1" stroke="#334155" stroke-width="1.5"/>')
        svg.append(f'<g filter="url(#dropShadow)">')
        svg.append(f'<path d="M {nx} 202 L {nx+nw} 202 L {nx+nw} 360 Q {nx+nw*0.5} 370 {nx} 360 Z" fill="url(#norenGrad)" stroke="#091124" stroke-width="2.5"/>')
        svg.append(f'<path d="M {nx} 280 L {nx+nw} 280 L {nx+nw} 360 Q {nx+nw*0.5} 370 {nx} 360 Z" fill="url(#wavePattern)"/>')
        svg.append(f'<path d="M {nx} 346 L {nx+nw} 346 L {nx+nw} 352 L {nx} 352 Z" fill="#ffffff" opacity="0.85"/>')
        cx_noren = nx + nw / 2
        svg.append(f'<circle cx="{cx_noren}" cy="{265}" r="32" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.9"/>')
        svg.append(f'<circle cx="{cx_noren}" cy="{265}" r="27" fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0.7"/>')
        svg.append(f'<text x="{cx_noren}" y="276" font-family="serif, Klee One, sans-serif" font-weight="900" font-size="28" fill="#ffffff" text-anchor="middle" opacity="0.95">{noren_labels[idx]}</text>')
        svg.append(f'<path d="M {nx+nw-12} 202 L {nx+nw} 202 L {nx+nw} 360 L {nx+nw-12} 359 Z" fill="#020617" opacity="0.45"/>')
        svg.append('</g>')

    # Fairy lights
    svg.append('<!-- FAIRY LIGHTS STRING -->')
    svg.append('<path d="M 120 180 Q 400 225 800 190 Q 1200 225 1480 180" fill="none" stroke="#334155" stroke-width="2"/>')
    for tx in [200, 310, 440, 570, 700, 800, 920, 1050, 1180, 1310, 1420]:
        ty = 180 + 26 * math.sin((tx - 120) / 1360 * math.pi)
        svg.append(f'<circle cx="{tx}" cy="{ty+6}" r="14" fill="#fbbf24" opacity="0.25" filter="url(#glowFilter)"/>')
        svg.append(f'<circle cx="{tx}" cy="{ty+6}" r="6" fill="#fef08a" stroke="#d97706" stroke-width="1.2"/>')
        svg.append(f'<rect x="{tx-2}" y="{ty}" width="4" height="4" fill="#475569"/>')

    # Hanging Red Paper Lanterns (Chōchin)
    def draw_lantern(cx, cy, kanji_list, scale=1.08):
        lw = 88 * scale
        lh = 150 * scale
        parts = []
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{lw*2.1}" fill="url(#lanternHalo)" filter="url(#lanternGlowFilter)"/>')
        parts.append(f'<path d="M {cx-15*scale} {cy-lh-22*scale} L {cx+15*scale} {cy-lh-22*scale} L {cx+10*scale} {cy-lh} L {cx-10*scale} {cy-lh} Z" fill="#181512" stroke="#000" stroke-width="1.5"/>')
        parts.append(f'<path d="M {cx} {cy-lh-22*scale} L {cx} {cy-lh-48*scale}" stroke="#000" stroke-width="3" stroke-linecap="round"/>')
        parts.append(f'<rect x="{cx-38*scale}" y="{cy-lh}" width="{76*scale}" height="{15*scale}" rx="{3*scale}" fill="#18181b" stroke="#000" stroke-width="2"/>')
        parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{lw}" ry="{lh*0.96}" fill="url(#lanternRadial)" stroke="#3b0505" stroke-width="3" filter="url(#dropShadow)"/>')
        for r_offset in [-0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75]:
            ry_val = cy + (lh * 0.96) * r_offset
            rx_val = lw * math.sqrt(max(0.01, 1.0 - r_offset * r_offset))
            parts.append(f'<ellipse cx="{cx}" cy="{ry_val}" rx="{rx_val*0.98}" ry="{4.2*scale}" fill="none" stroke="#7f1d1d" stroke-width="1.8" opacity="0.75"/>')
        font_sz = int(50 * scale)
        if len(kanji_list) == 2:
            parts.append(f'<text x="{cx}" y="{cy-lh*0.12}" font-family="serif, Klee One, sans-serif" font-weight="900" font-size="{font_sz}" fill="#111827" text-anchor="middle">{kanji_list[0]}</text>')
            parts.append(f'<text x="{cx}" y="{cy+lh*0.42}" font-family="serif, Klee One, sans-serif" font-weight="900" font-size="{font_sz}" fill="#111827" text-anchor="middle">{kanji_list[1]}</text>')
        parts.append(f'<rect x="{cx-36*scale}" y="{cy+lh*0.93}" width="{72*scale}" height="{15*scale}" rx="{3*scale}" fill="#18181b" stroke="#000" stroke-width="2"/>')
        parts.append(f'<circle cx="{cx}" cy="{cy+lh*0.93+18*scale}" r="{6.5*scale}" fill="#eab308" stroke="#78350f" stroke-width="1.5"/>')
        parts.append(f'<path d="M {cx-9*scale} {cy+lh*0.93+22*scale} L {cx+9*scale} {cy+lh*0.93+22*scale} L {cx+15*scale} {cy+lh*0.93+80*scale} L {cx-15*scale} {cy+lh*0.93+80*scale} Z" fill="#b91c1c" stroke="#3b0505" stroke-width="1.8"/>')
        parts.append(f'<line x1="{cx-4*scale}" y1="{cy+lh*0.93+22*scale}" x2="{cx-6*scale}" y2="{cy+lh*0.93+80*scale}" stroke="#ef4444" stroke-width="1.2"/>')
        parts.append(f'<line x1="{cx+4*scale}" y1="{cy+lh*0.93+22*scale}" x2="{cx+6*scale}" y2="{cy+lh*0.93+80*scale}" stroke="#ef4444" stroke-width="1.2"/>')
        return "\n".join(parts)

    svg.append('<!-- HANGING LANTERNS -->')
    svg.append(draw_lantern(235, 340, ["拉", "麺"]))
    svg.append(draw_lantern(1365, 340, ["蛸", "吉"]))

    # -------------------------------------------------------------
    # 2. ALL 8 TENTACLES (Origins tucked behind body)
    # -------------------------------------------------------------
    svg.append('<!-- TENTACLES LAYER -->')

    # TENTACLE 1 (Top Left): S-curve lifting noodle basket high in air (*yugiri* flick!)
    t1_seg1 = ((750, 650), (580, 550), (440, 430), (370, 310))
    t1_seg2 = ((370, 310), (320, 230), (380, 150), (450, 190))
    t1_data = make_spline_tentacle([t1_seg1, t1_seg2], start_w=62, end_w=20, flip_suckers=False, num_suckers=11, sucker_scale=1.0)
    svg.append('<g id="tentacle1">')
    svg.append(render_tentacle_svg(t1_data))
    tb_cx, tb_cy = 450, 190
    svg.append(f'<line x1="{tb_cx-30}" y1="{tb_cy+30}" x2="{tb_cx+55}" y2="{tb_cy-40}" stroke="#78350f" stroke-width="14" stroke-linecap="round"/>')
    svg.append(f'<line x1="{tb_cx-30}" y1="{tb_cy+30}" x2="{tb_cx+55}" y2="{tb_cy-40}" stroke="#d97706" stroke-width="8" stroke-linecap="round"/>')
    svg.append(f'<path d="M {tb_cx-25} {tb_cy+25} L {tb_cx-85} {tb_cy-10} L {tb_cx-115} {tb_cy+55} L {tb_cx-55} {tb_cy+90} Z" fill="#94a3b8" fill-opacity="0.35" stroke="#cbd5e1" stroke-width="3"/>')
    svg.append(f'<ellipse cx="{tb_cx-55}" cy="{tb_cy+8}" rx="34" ry="15" fill="#334155" stroke="#e2e8f0" stroke-width="3"/>')
    for ml in range(-20, 40, 10):
        svg.append(f'<line x1="{tb_cx-80+ml}" y1="{tb_cy-5}" x2="{tb_cx-55+ml}" y2="{tb_cy+70}" stroke="#cbd5e1" stroke-width="1.2" opacity="0.6"/>')

    # Flying golden noodles
    svg.append('<g id="flyingNoodles" stroke="#facc15" stroke-linecap="round" fill="none">')
    noodle_paths = [
        "M 390 190 Q 340 130 380 70 Q 420 30 470 50 Q 520 80 500 130 Q 470 190 530 220",
        "M 385 200 Q 320 140 350 80 Q 400 40 450 55 Q 500 75 510 120 Q 520 180 560 200",
        "M 395 180 Q 360 110 410 60 Q 460 25 500 45 Q 540 70 535 120 Q 530 170 580 210",
        "M 400 195 Q 340 120 380 65 Q 430 20 490 40 Q 550 60 555 110 Q 555 160 600 190",
        "M 380 185 Q 310 125 335 75 Q 380 30 430 45 Q 480 60 485 105 Q 490 150 515 195",
        "M 410 205 Q 430 140 470 100 Q 520 70 560 90 Q 600 120 580 170 Q 560 210 610 240",
        "M 370 195 Q 290 130 320 80 Q 360 40 400 55 Q 440 70 450 115",
    ]
    for np in noodle_paths:
        svg.append(f'<path d="{np}" stroke-width="4.5"/>')
        svg.append(f'<path d="{np}" stroke="#fef08a" stroke-width="2.2"/>')
    water_drops = [
        (340, 110, 4), (380, 50, 4.5), (430, 20, 5), (480, 25, 4),
        (530, 40, 4.5), (560, 70, 3.5), (580, 120, 5), (600, 170, 4),
        (500, 15, 3), (410, 15, 4), (300, 90, 3.5), (320, 160, 4)
    ]
    for wdx, wdy, wdr in water_drops:
        svg.append(f'<circle cx="{wdx}" cy="{wdy}" r="{wdr}" fill="#ffffff" filter="url(#glowFilter)"/>')
        svg.append(f'<circle cx="{wdx}" cy="{wdy}" r="{wdr*0.6}" fill="#93c5fd"/>')
    svg.append('</g>')
    svg.append('</g>')

    # TENTACLE 5 (Top Right): Slicing scallions with gleaming Santoku knife
    t5_seg1 = ((850, 650), (1000, 540), (1150, 440), (1200, 320))
    t5_seg2 = ((1200, 320), (1230, 230), (1160, 160), (1100, 210))
    t5_data = make_spline_tentacle([t5_seg1, t5_seg2], start_w=62, end_w=22, flip_suckers=True, num_suckers=11, sucker_scale=1.0)
    svg.append('<g id="tentacle5">')
    svg.append(render_tentacle_svg(t5_data))
    k_cx, k_cy = 1100, 210
    svg.append(f'<path d="M {k_cx+45} {k_cy-25} L {k_cx-15} {k_cy+25}" stroke="#271306" stroke-width="16" stroke-linecap="round"/>')
    svg.append(f'<path d="M {k_cx+45} {k_cy-25} L {k_cx-15} {k_cy+25}" stroke="#8c4b22" stroke-width="10" stroke-linecap="round"/>')
    svg.append(f'<circle cx="{k_cx-18}" cy="{k_cy+28}" r="8" fill="#94a3b8" stroke="#334155" stroke-width="2"/>')
    svg.append(f'<path d="M {k_cx-20} {k_cy+30} L {k_cx-125} {k_cy+135} Q {k_cx-155} {k_cy+120} {k_cx-155} {k_cy+80} L {k_cx-45} {k_cy-5} Z" fill="url(#bladeGrad)" stroke="#334155" stroke-width="2.5" filter="url(#dropShadow)"/>')
    svg.append(f'<path d="M {k_cx-125} {k_cy+135} Q {k_cx-155} {k_cy+120} {k_cx-155} {k_cy+80}" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round"/>')
    svg.append(f'<g transform="translate({k_cx-145}, {k_cy+110})" filter="url(#glowFilter)">')
    svg.append('<polygon points="0,-18 5,-5 18,0 5,5 0,18 -5,5 -18,0 -5,-5" fill="#ffffff"/>')
    svg.append('</g>')
    negi_cuts = [
        (1010, 280, 15, 9, 35), (980, 320, 16, 9, -20), (940, 270, 12, 7, 50),
        (1050, 250, 15, 8, -40), (1020, 210, 14, 8, 15), (960, 220, 13, 7, -60)
    ]
    for nx, ny, nrx, nry, nrot in negi_cuts:
        svg.append(f'<g transform="translate({nx},{ny}) rotate({nrot})">')
        svg.append(f'<ellipse cx="0" cy="0" rx="{nrx}" ry="{nry}" fill="#22c55e" stroke="#15803d" stroke-width="2.5"/>')
        svg.append(f'<ellipse cx="0" cy="0" rx="{nrx*0.62}" ry="{nry*0.6}" fill="#bbf7d0"/>')
        svg.append(f'<ellipse cx="0" cy="0" rx="{nrx*0.3}" ry="{nry*0.3}" fill="#166534"/>')
        svg.append('</g>')
    svg.append('</g>')

    # TENTACLE 2 (Mid-Left High): Ladle pouring broth
    t2_seg1 = ((740, 680), (600, 590), (500, 500), (530, 420))
    t2_seg2 = ((530, 420), (560, 360), (650, 400), (610, 490))
    t2_data = make_spline_tentacle([t2_seg1, t2_seg2], start_w=56, end_w=20, flip_suckers=True, num_suckers=9, sucker_scale=1.0)
    svg.append('<g id="tentacle2">')
    svg.append(render_tentacle_svg(t2_data))
    ld_cx, ld_cy = 610, 490
    svg.append(f'<line x1="{ld_cx-75}" y1="{ld_cy-65}" x2="{ld_cx+35}" y2="{ld_cy+25}" stroke="#78350f" stroke-width="9" stroke-linecap="round"/>')
    svg.append(f'<line x1="{ld_cx-75}" y1="{ld_cy-65}" x2="{ld_cx+35}" y2="{ld_cy+25}" stroke="#d97706" stroke-width="5" stroke-linecap="round"/>')
    svg.append(f'<g transform="translate({ld_cx+35},{ld_cy+25}) rotate(35)">')
    svg.append('<ellipse cx="0" cy="0" rx="34" ry="24" fill="#8c5022" stroke="#451a03" stroke-width="3"/>')
    svg.append('<ellipse cx="-4" cy="-2" rx="28" ry="18" fill="url(#potBrothGrad)"/>')
    svg.append('</g>')
    svg.append('<path d="M 650 525 Q 685 620 720 740" fill="none" stroke="url(#soupPourGrad)" stroke-width="11" stroke-linecap="round" filter="url(#glowFilter)"/>')
    svg.append('<path d="M 650 525 Q 685 620 720 740" fill="none" stroke="#ffffff" stroke-width="3.8" stroke-linecap="round" opacity="0.8"/>')
    for spy in [560, 610, 660, 710]:
        svg.append(f'<circle cx="{645+(spy-525)*0.32+((spy%24)-12)}" cy="{spy}" r="3.5" fill="#fef08a" filter="url(#glowFilter)"/>')
    svg.append('</g>')

    # TENTACLE 6 (Mid-Right High): Shaking Shichimi Togarashi shaker
    t6_seg1 = ((860, 680), (1030, 600), (1170, 530), (1250, 450))
    t6_seg2 = ((1250, 450), (1290, 390), (1240, 330), (1180, 380))
    t6_data = make_spline_tentacle([t6_seg1, t6_seg2], start_w=56, end_w=20, flip_suckers=False, num_suckers=9, sucker_scale=1.0)
    svg.append('<g id="tentacle6">')
    svg.append(render_tentacle_svg(t6_data))
    sh_cx, sh_cy = 1180, 380
    svg.append(f'<g transform="translate({sh_cx},{sh_cy}) rotate(-35)">')
    svg.append('<polygon points="-16,-40 16,-40 22,25 -22,25" fill="#a16207" stroke="#451a03" stroke-width="2.5"/>')
    svg.append('<polygon points="-10,-40 10,-40 14,25 -14,25" fill="#ca8a04"/>')
    svg.append('<rect x="-14" y="25" width="28" height="12" rx="3" fill="#dc2626" stroke="#7f1d1d" stroke-width="2"/>')
    svg.append('<rect x="-5" y="37" width="10" height="6" fill="#991b1b"/>')
    svg.append('<rect x="-10" y="-22" width="20" height="34" fill="#fef08a" stroke="#78350f" stroke-width="1"/>')
    svg.append('<text x="0" y="-8" font-family="serif" font-weight="900" font-size="11" fill="#b91c1c" text-anchor="middle">七</text>')
    svg.append('<text x="0" y="6" font-family="serif" font-weight="900" font-size="11" fill="#b91c1c" text-anchor="middle">味</text>')
    svg.append('</g>')
    chili_dots = [
        (1145, 430), (1155, 445), (1135, 455), (1160, 470), (1140, 485),
        (1150, 500), (1130, 510), (1165, 525), (1145, 540), (1155, 555)
    ]
    for cdx, cdy in chili_dots:
        svg.append(f'<circle cx="{cdx}" cy="{cdy}" r="2.8" fill="#ef4444"/>')
        svg.append(f'<circle cx="{cdx+3}" cy="{cdy+4}" r="1.8" fill="#f97316"/>')
        svg.append(f'<circle cx="{cdx-4}" cy="{cdy+8}" r="1.5" fill="#1c1917"/>')
    svg.append('</g>')

    # TENTACLE 3 (Mid-Left Low): Stirring stockpot with wooden paddle
    t3_seg1 = ((730, 710), (590, 710), (480, 660), (420, 630))
    t3_seg2 = ((420, 630), (360, 610), (330, 670), (370, 720))
    t3_data = make_spline_tentacle([t3_seg1, t3_seg2], start_w=58, end_w=22, flip_suckers=False, num_suckers=9, sucker_scale=1.0)
    svg.append('<g id="tentacle3">')
    svg.append(render_tentacle_svg(t3_data))
    sp_cx, sp_cy = 370, 720
    svg.append(f'<g transform="translate({sp_cx},{sp_cy}) rotate(25)">')
    svg.append('<rect x="-10" y="-85" width="20" height="150" rx="6" fill="#8c5022" stroke="#451a03" stroke-width="3"/>')
    svg.append('<rect x="-14" y="20" width="28" height="60" rx="8" fill="#a16207" stroke="#451a03" stroke-width="3"/>')
    svg.append('</g>')
    svg.append('</g>')

    # TENTACLE 8 (Far Right): Welcoming wave / "No. 1" curl
    t8_seg1 = ((870, 710), (1040, 690), (1190, 670), (1250, 600))
    t8_seg2 = ((1250, 600), (1290, 540), (1220, 490), (1180, 540))
    t8_data = make_spline_tentacle([t8_seg1, t8_seg2], start_w=58, end_w=22, flip_suckers=False, num_suckers=10, sucker_scale=1.1)
    svg.append('<g id="tentacle8">')
    svg.append(render_tentacle_svg(t8_data))
    svg.append(f'<g transform="translate(1200, 470)" filter="url(#glowFilter)">')
    svg.append('<polygon points="0,-16 4,-4 16,0 4,4 0,16 -4,4 -16,0 -4,-4" fill="#fbbf24"/>')
    svg.append('</g>')
    svg.append('</g>')

    # TENTACLE 4 (Bottom-Left Counter): Wiping counter with cleaning towel
    t4_seg1 = ((740, 750), (640, 810), (540, 810), (480, 820))
    t4_seg2 = ((480, 820), (420, 830), (370, 810), (400, 850))
    t4_data = make_spline_tentacle([t4_seg1, t4_seg2], start_w=56, end_w=22, flip_suckers=True, num_suckers=9, sucker_scale=1.0)
    svg.append('<g id="tentacle4">')
    svg.append(render_tentacle_svg(t4_data))
    fcx, fcy = 400, 855
    svg.append(f'<path d="M {fcx-35} {fcy-15} Q {fcx} {fcy-25} {fcx+45} {fcy-10} L {fcx+40} {fcy+20} Q {fcx} {fcy+30} {fcx-40} {fcy+15} Z" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2.5" filter="url(#dropShadow)"/>')
    svg.append(f'<path d="M {fcx-30} {fcy} Q {fcx} {fcy-10} {fcx+35} {fcy+5}" fill="none" stroke="#94a3b8" stroke-width="2"/>')
    for glx, gly in [(340, 840), (460, 865), (410, 825)]:
        svg.append(f'<g transform="translate({glx},{gly})" filter="url(#glowFilter)">')
        svg.append('<polygon points="0,-10 3,-3 10,0 3,3 0,10 -3,3 -10,0 -3,-3" fill="#ffffff"/>')
        svg.append('</g>')
    svg.append('</g>')

    # TENTACLE 7 (Front Right): Placing Narutomaki slice with cooking chopsticks
    t7_seg1 = ((850, 750), (950, 770), (1010, 830), (970, 870))
    t7_seg2 = ((970, 870), (940, 910), (890, 890), (870, 840))
    t7_data = make_spline_tentacle([t7_seg1, t7_seg2], start_w=56, end_w=20, flip_suckers=False, num_suckers=9, sucker_scale=1.0)
    svg.append('<g id="tentacle7">')
    svg.append(render_tentacle_svg(t7_data))
    ch_tip_x, ch_tip_y = 870, 840
    svg.append(f'<line x1="{ch_tip_x+55}" y1="{ch_tip_y-45}" x2="{ch_tip_x-60}" y2="{ch_tip_y+30}" stroke="#78350f" stroke-width="5" stroke-linecap="round"/>')
    svg.append(f'<line x1="{ch_tip_x+55}" y1="{ch_tip_y-45}" x2="{ch_tip_x-60}" y2="{ch_tip_y+30}" stroke="#d97706" stroke-width="2.5" stroke-linecap="round"/>')
    svg.append(f'<line x1="{ch_tip_x+65}" y1="{ch_tip_y-38}" x2="{ch_tip_x-55}" y2="{ch_tip_y+37}" stroke="#78350f" stroke-width="4.5" stroke-linecap="round"/>')
    svg.append(f'<line x1="{ch_tip_x+65}" y1="{ch_tip_y-38}" x2="{ch_tip_x-55}" y2="{ch_tip_y+37}" stroke="#d97706" stroke-width="2.2" stroke-linecap="round"/>')
    svg.append(f'<g transform="translate({ch_tip_x-58},{ch_tip_y+34}) rotate(-20)" filter="url(#dropShadow)">')
    svg.append('<circle cx="0" cy="0" r="19" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.8"/>')
    svg.append('<path d="M 0 0 Q 6 3 5 8 Q 3 13 -4 12 Q -11 10 -10 2 Q -9 -7 0 -9 Q 11 -10 14 -1 Q 16 9 8 15 Q -1 19 -9 14" fill="none" stroke="#ec4899" stroke-width="3.5" stroke-linecap="round"/>')
    svg.append('</g>')
    svg.append('</g>')

    # -------------------------------------------------------------
    # 3. CHEF BODY, HEAD, TOQUE BLANCHE & EXPRESSIVE FACE
    # (Covers the tentacle roots seamlessly!)
    # -------------------------------------------------------------
    svg.append('<!-- MASTER OCTOPUS CHEF -->')
    svg.append('<g id="octopusChef">')

    # Chef Uniform / Happi coat & Apron (Maekake)
    svg.append('<path d="M 670 630 Q 800 610 930 630 L 970 860 L 630 860 Z" fill="url(#apronGrad)" stroke="#090d16" stroke-width="3" filter="url(#dropShadow)"/>')
    svg.append('<path d="M 720 625 L 800 735 L 760 745 L 700 635 Z" fill="#ffffff" stroke="#cbd5e1" stroke-width="2.5"/>')
    svg.append('<path d="M 880 625 L 790 745 L 830 755 L 900 635 Z" fill="#ffffff" stroke="#cbd5e1" stroke-width="2.5"/>')
    svg.append('<polygon points="785,645 815,645 800,695" fill="#dc2626"/>')
    # White cotton belt cord
    svg.append('<rect x="650" y="755" width="300" height="15" rx="4" fill="#f1f5f9" stroke="#94a3b8" stroke-width="2"/>')
    svg.append('<circle cx="800" cy="762" r="13" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>')
    svg.append('<path d="M 795 775 L 785 840 L 800 840 L 805 775 Z" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>')
    svg.append('<path d="M 805 775 L 815 835 L 800 835 L 795 775 Z" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>')
    # White circular emblem on Apron: 「蛸」(Tako)
    svg.append('<circle cx="800" cy="700" r="28" fill="none" stroke="#ffffff" stroke-width="2.5" opacity="0.9"/>')
    svg.append('<text x="800" y="711" font-family="serif" font-weight="900" font-size="28" fill="#ffffff" text-anchor="middle" opacity="0.95">蛸</text>')

    # Plump Bulbous Octopus Head (Mantle)
    hcx, hcy = 800, 460
    svg.append(f'<g filter="url(#dropShadow)">')
    svg.append(f'<path d="M {hcx-150} {hcy+95} C {hcx-185} {hcy+15} {hcx-170} {hcy-125} {hcx} {hcy-135} C {hcx+170} {hcy-125} {hcx+185} {hcy+15} {hcx+150} {hcy+95} C {hcx+115} {hcy+145} {hcx-115} {hcy+145} {hcx-150} {hcy+95} Z" fill="url(#octopusHeadGrad)" stroke="#4d000b" stroke-width="4"/>')
    # Volumetric light sheens
    svg.append(f'<ellipse cx="{hcx-35}" cy="{hcy-75}" rx="72" ry="40" fill="#ffffff" opacity="0.35" filter="url(#softBlur)"/>')
    svg.append(f'<path d="M {hcx-135} {hcy-50} C {hcx-155} {hcy} {hcx-145} {hcy+50} {hcx-115} {hcy+85}" fill="none" stroke="#fecaca" stroke-width="8" opacity="0.38" filter="url(#softBlur)"/>')
    svg.append('</g>')

    # Tall Pleated White Chef's Hat (Toque Blanche) fitted naturally on top of head
    svg.append('<!-- CHEF TOQUE BLANCHE -->')
    svg.append(f'<g filter="url(#dropShadow)">')
    hat_bx, hat_by = hcx, hcy - 110
    top_w, top_h = 120, 160
    # Billowing puffy crown of hat
    svg.append(f'<path d="M {hat_bx-96} {hat_by} C {hat_bx-top_w} {hat_by-60} {hat_bx-top_w+10} {hat_by-top_h} {hat_bx-45} {hat_by-top_h-18} C {hat_bx-20} {hat_by-top_h-28} {hat_bx+20} {hat_by-top_h-28} {hat_bx+45} {hat_by-top_h-18} C {hat_bx+top_w-10} {hat_by-top_h} {hat_bx+top_w} {hat_by-60} {hat_bx+96} {hat_by} Z" fill="url(#toqueGrad)" stroke="#334155" stroke-width="3"/>')
    # Elegant vertical fabric pleats
    for px_off in [-65, -40, -15, 15, 40, 65]:
        svg.append(f'<path d="M {hat_bx+px_off} {hat_by} Q {hat_bx+px_off*1.12} {hat_by-80} {hat_bx+px_off*0.75} {hat_by-top_h-12}" fill="none" stroke="#cbd5e1" stroke-width="2.5"/>')
    # Fitted base band of toque
    svg.append(f'<path d="M {hat_bx-96} {hat_by} Q {hat_bx} {hat_by+12} {hat_bx+96} {hat_by} L {hat_bx+94} {hat_by+28} Q {hat_bx} {hat_by+40} {hat_bx-94} {hat_by+28} Z" fill="#ffffff" stroke="#334155" stroke-width="3"/>')
    svg.append(f'<path d="M {hat_bx-94} {hat_by+14} Q {hat_bx} {hat_by+26} {hat_bx+94} {hat_by+14}" fill="none" stroke="#d97706" stroke-width="3"/>')
    svg.append('</g>')

    # Chef's Headband (Nejiri-Hachimaki) - Clean, Crisp & Iconic with Red Sun Crest
    svg.append('<!-- HACHIMAKI HEADBAND -->')
    svg.append('<g id="hachimaki" filter="url(#dropShadow)">')
    svg.append(f'<path d="M {hcx-152} {hcy-8} Q {hcx} {hcy+15} {hcx+152} {hcy-8} L {hcx+149} {hcy+26} Q {hcx} {hcy+46} {hcx-149} {hcy+26} Z" fill="url(#hachimakiGrad)" stroke="#334155" stroke-width="3"/>')
    svg.append(f'<path d="M {hcx-130} {hcy+8} Q {hcx} {hcy+28} {hcx+130} {hcy+8}" fill="none" stroke="#e2e8f0" stroke-width="2"/>')
    svg.append(f'<circle cx="{hcx}" cy="{hcy+20}" r="14" fill="#dc2626" stroke="#991b1b" stroke-width="1.5"/>')
    # Knot and fluttering ribbon tails
    svg.append(f'<g transform="translate({hcx+148},{hcy+8})">')
    svg.append('<circle cx="6" cy="4" r="14" fill="#f8fafc" stroke="#334155" stroke-width="2.5"/>')
    svg.append('<path d="M 0 0 Q 6 12 12 4" fill="none" stroke="#dc2626" stroke-width="2.5"/>')
    svg.append('<path d="M 14 0 Q 45 -25 75 -15 Q 55 5 20 12 Z" fill="#ffffff" stroke="#334155" stroke-width="2"/>')
    svg.append('<path d="M 18 -1 Q 45 -18 70 -12" fill="none" stroke="#dc2626" stroke-width="2.5"/>')
    svg.append('<path d="M 12 10 Q 50 25 80 18 Q 55 35 15 22 Z" fill="#f1f5f9" stroke="#334155" stroke-width="2"/>')
    svg.append('<path d="M 16 12 Q 50 25 75 20" fill="none" stroke="#0284c7" stroke-width="2.5"/>')
    svg.append('</g>')
    svg.append('</g>')

    # Expressive Chef Face
    def draw_chef_eye(ex, ey, flip=False):
        parts = []
        parts.append(f'<ellipse cx="{ex}" cy="{ey}" rx="31" ry="35" fill="#ffffff" stroke="#3b070c" stroke-width="3"/>')
        iris_x = ex + (-3 if flip else 3)
        parts.append(f'<ellipse cx="{iris_x}" cy="{ey+2}" rx="21" ry="24" fill="url(#eyeIris)"/>')
        parts.append(f'<ellipse cx="{iris_x}" cy="{ey+3}" rx="12" ry="14" fill="#18181b"/>')
        parts.append(f'<circle cx="{iris_x-7}" cy="{ey-5}" r="7" fill="#ffffff"/>')
        parts.append(f'<circle cx="{iris_x+6}" cy="{ey+7}" r="3.5" fill="#ffffff"/>')
        parts.append(f'<circle cx="{iris_x-5}" cy="{ey+10}" r="2.2" fill="#ffffff"/>')
        sign = 1 if not flip else -1
        parts.append(f'<path d="M {ex-29*sign} {ey-8} Q {ex-8*sign} {ey-25} {ex+29*sign} {ey-12}" fill="none" stroke="#3b070c" stroke-width="5.2" stroke-linecap="round"/>')
        parts.append(f'<path d="M {ex-27*sign} {ey-29} Q {ex} {ey-43} {ex+27*sign} {ey-29}" fill="none" stroke="#1f0306" stroke-width="4.8" stroke-linecap="round"/>')
        return "\n".join(parts)

    svg.append('<!-- CHEF EYES -->')
    svg.append(draw_chef_eye(hcx-58, hcy+75, flip=False))
    svg.append(draw_chef_eye(hcx+58, hcy+75, flip=True))

    # Blushing Cheeks
    svg.append(f'<ellipse cx="{hcx-96}" cy="{hcy+100}" rx="24" ry="14" fill="#ff4d6d" opacity="0.5" filter="url(#softBlur)"/>')
    svg.append(f'<ellipse cx="{hcx+96}" cy="{hcy+100}" rx="24" ry="14" fill="#ff4d6d" opacity="0.5" filter="url(#softBlur)"/>')
    for bx_off in [-104, -96, -88]:
        svg.append(f'<line x1="{hcx+bx_off}" y1="{hcy+95}" x2="{hcx+bx_off+8}" y2="{hcy+105}" stroke="#b91c1c" stroke-width="1.8" stroke-linecap="round"/>')
    for bx_off in [88, 96, 104]:
        svg.append(f'<line x1="{hcx+bx_off}" y1="{hcy+95}" x2="{hcx+bx_off+8}" y2="{hcy+105}" stroke="#b91c1c" stroke-width="1.8" stroke-linecap="round"/>')

    # Smiling Mouth & Cute Chef Mustache
    svg.append('<!-- CHEF MOUTH & MUSTACHE -->')
    svg.append(f'<path d="M {hcx-28} {hcy+112} Q {hcx} {hcy+152} {hcx+28} {hcy+112} Z" fill="#7f1d1d" stroke="#3b070c" stroke-width="3" stroke-linejoin="round"/>')
    svg.append(f'<path d="M {hcx-18} {hcy+128} Q {hcx} {hcy+118} {hcx+18} {hcy+128} Q {hcx} {hcy+150} {hcx-18} {hcy+128} Z" fill="#fb7185"/>')
    svg.append(f'<path d="M {hcx} {hcy+110} Q {hcx-22} {hcy+106} {hcx-36} {hcy+98} Q {hcx-26} {hcy+116} {hcx} {hcy+113}" fill="#991b1b" stroke="#450a0a" stroke-width="2"/>')
    svg.append(f'<path d="M {hcx} {hcy+110} Q {hcx+22} {hcy+106} {hcx+36} {hcy+98} Q {hcx+26} {hcy+116} {hcx} {hcy+113}" fill="#991b1b" stroke="#450a0a" stroke-width="2"/>')

    svg.append('</g>') # End octopusChef

    # -------------------------------------------------------------
    # 4. KITCHEN EQUIPMENT & COUNTERTOP DECK
    # -------------------------------------------------------------
    svg.append('<!-- KITCHEN DECK & EQUIPMENT -->')

    # Stove Burner Ring on Left Deck
    svg.append('<ellipse cx="325" cy="850" rx="145" ry="32" fill="#18181b" stroke="#090d16" stroke-width="3"/>')
    svg.append('<ellipse cx="325" cy="850" rx="130" ry="26" fill="#27272a" stroke="#f97316" stroke-width="1.5" opacity="0.6"/>')

    # Giant Stainless Steel Broth Stockpot
    pot_x, pot_y, pot_w, pot_h = 190, 640, 270, 220
    svg.append('<g id="brothStockpot" filter="url(#deepShadow)">')
    svg.append(f'<rect x="{pot_x}" y="{pot_y}" width="{pot_w}" height="{pot_h}" rx="22" fill="url(#potSteelGrad)" stroke="#1e293b" stroke-width="3.5"/>')
    svg.append(f'<path d="M {pot_x-16} {pot_y+50} Q {pot_x-36} {pot_y+80} {pot_x-16} {pot_y+110}" fill="none" stroke="#64748b" stroke-width="10" stroke-linecap="round"/>')
    svg.append(f'<path d="M {pot_x-16} {pot_y+50} Q {pot_x-36} {pot_y+80} {pot_x-16} {pot_y+110}" fill="none" stroke="#cbd5e1" stroke-width="4" stroke-linecap="round"/>')
    svg.append(f'<ellipse cx="{pot_x+pot_w/2}" cy="{pot_y}" rx="{pot_w/2+6}" ry="36" fill="url(#potSteelGrad)" stroke="#1e293b" stroke-width="3.5"/>')
    svg.append(f'<ellipse cx="{pot_x+pot_w/2}" cy="{pot_y}" rx="{pot_w/2-8}" ry="30" fill="url(#potBrothGrad)"/>')
    # Floating leeks & ginger
    svg.append(f'<g transform="translate({pot_x+70},{pot_y-4}) rotate(18)">')
    svg.append('<rect x="0" y="0" width="70" height="12" rx="4" fill="#22c55e" stroke="#15803d" stroke-width="1.8"/>')
    svg.append('<line x1="20" y1="2" x2="68" y2="2" stroke="#86efac" stroke-width="2"/>')
    svg.append('</g>')
    svg.append(f'<ellipse cx="{pot_x+180}" cy="{pot_y+6}" rx="18" ry="11" fill="#fef08a" stroke="#ca8a04" stroke-width="1.8"/>')
    for bbx, bby, bbr in [(pot_x+100, pot_y-8, 9), (pot_x+135, pot_y+10, 12), (pot_x+205, pot_y-5, 8), (pot_x+80, pot_y+8, 7)]:
        svg.append(f'<ellipse cx="{bbx}" cy="{bby}" rx="{bbr}" ry="{bbr*0.65}" fill="#fef9c3" stroke="#eab308" stroke-width="1.5" opacity="0.85"/>')
        svg.append(f'<circle cx="{bbx-bbr*0.3}" cy="{bby-bbr*0.2}" r="{bbr*0.25}" fill="#ffffff"/>')
    svg.append('</g>')

    # Billowing Steam from Stockpot (Curling up to the left around lantern)
    svg.append('<g id="potSteam" filter="url(#steamFilter)">')
    steam_plumes = [
        "M 260 630 Q 210 530 250 440 Q 290 350 220 260 Q 170 180 250 100",
        "M 330 620 Q 370 520 300 420 Q 250 330 310 230 Q 360 150 300 80",
        "M 390 630 Q 430 540 360 440 Q 300 350 370 250 Q 420 170 380 100"
    ]
    for sp in steam_plumes:
        svg.append(f'<path d="{sp}" fill="none" stroke="url(#steamGrad)" stroke-width="38" stroke-linecap="round"/>')
        svg.append(f'<path d="{sp}" fill="none" stroke="#ffffff" stroke-width="14" stroke-linecap="round" opacity="0.45"/>')
    svg.append('</g>')

    # Solid Cedar Countertop Slab (Proper perspective deck)
    c_y = 820
    svg.append('<!-- COUNTERTOP -->')
    svg.append(f'<polygon points="40,{c_y} 1560,{c_y} 1600,{c_y+115} 0,{c_y+115}" fill="url(#counterTopGrad)" stroke="#1a0d06" stroke-width="3" filter="url(#dropShadow)"/>')
    for gy in [c_y+25, c_y+55, c_y+85]:
        svg.append(f'<path d="M 20 {gy} Q 400 {gy-6} 800 {gy} Q 1200 {gy+6} 1580 {gy}" fill="none" stroke="#fcd34d" stroke-width="1.8" opacity="0.45"/>')
    svg.append(f'<rect x="0" y="{c_y+115}" width="1600" height="265" fill="url(#counterFrontGrad)" stroke="#0c0502" stroke-width="3"/>')
    for fx in range(120, 1500, 180):
        svg.append(f'<rect x="{fx}" y="{c_y+135}" width="150" height="215" fill="#25130a" stroke="#0e0603" stroke-width="2.5"/>')
        svg.append(f'<rect x="{fx+10}" y="{c_y+145}" width="130" height="195" fill="#180b06" stroke="#3d2112" stroke-width="1.5"/>')
    svg.append(f'<line x1="0" y1="{c_y+116}" x2="1600" y2="{c_y+116}" stroke="#ffedd5" stroke-width="3.5" opacity="0.9"/>')

    # Prep Area on Right Counter:
    # Cutting Board
    cb_x, cb_y, cb_w, cb_h = 1060, 840, 240, 60
    svg.append('<g id="cuttingBoard" filter="url(#dropShadow)">')
    svg.append(f'<polygon points="{cb_x+20},{cb_y} {cb_x+cb_w-20},{cb_y} {cb_x+cb_w},{cb_y+cb_h} {cb_x},{cb_y+cb_h}" fill="#b45309" stroke="#451a03" stroke-width="3"/>')
    svg.append(f'<polygon points="{cb_x+23},{cb_y+4} {cb_x+cb_w-23},{cb_y+4} {cb_x+cb_w-5},{cb_y+cb_h-4} {cb_x+5},{cb_y+cb_h-4}" fill="#d97706"/>')
    for cs_off in [30, 60, 90]:
        svg.append(f'<ellipse cx="{cb_x+75+cs_off}" cy="{cb_y+28}" rx="22" ry="14" fill="url(#chashuGrad)" stroke="#451a03" stroke-width="2"/>')
        svg.append(f'<ellipse cx="{cb_x+75+cs_off}" cy="{cb_y+28}" rx="12" ry="7" fill="#ffedd5" opacity="0.8"/>')
    for scx, scy in [(cb_x+50, cb_y+35), (cb_x+58, cb_y+28), (cb_x+65, cb_y+38), (cb_x+42, cb_y+40), (cb_x+55, cb_y+44)]:
        svg.append(f'<ellipse cx="{scx}" cy="{scy}" rx="6" ry="4" fill="#22c55e" stroke="#15803d" stroke-width="1"/>')
    svg.append('</g>')

    # Stack of Clean Ceramic Bowls
    sb_x, sb_y = 1330, 840
    svg.append('<g id="stackedBowls" filter="url(#dropShadow)">')
    for b_lvl in range(3):
        cur_y = sb_y - b_lvl * 18
        svg.append(f'<ellipse cx="{sb_x}" cy="{cur_y+16}" rx="54" ry="18" fill="url(#bowlOuterGrad)" stroke="#090d16" stroke-width="2.5"/>')
        svg.append(f'<ellipse cx="{sb_x}" cy="{cur_y}" rx="52" ry="16" fill="#f8fafc" stroke="#dc2626" stroke-width="3"/>')
    svg.append('</g>')

    # Condiments
    cr_x, cr_y = 1000, 825
    svg.append('<g id="condiments" filter="url(#dropShadow)">')
    svg.append(f'<path d="M {cr_x-15} {cr_y-30} L {cr_x+15} {cr_y-30} L {cr_x+22} {cr_y+15} L {cr_x-22} {cr_y+15} Z" fill="#f8fafc" stroke="#334155" stroke-width="2"/>')
    svg.append(f'<rect x="{cr_x-12}" y="{cr_y-38}" width="24" height="8" rx="2" fill="#991b1b" stroke="#450a0a" stroke-width="1.5"/>')
    svg.append(f'<path d="M {cr_x-18} {cr_y-15} L {cr_x-30} {cr_y-25}" stroke="#ffffff" stroke-width="6" stroke-linecap="round"/>')
    svg.append(f'<circle cx="{cr_x}" cy="{cr_y-5}" r="10" fill="#3b82f6" opacity="0.8"/>')
    svg.append(f'<text x="{cr_x}" y="{cr_y-1}" font-family="sans-serif" font-weight="900" font-size="9" fill="#ffffff" text-anchor="middle">油</text>')
    svg.append('</g>')

    # Mini Golden Lucky Cat (Maneki-Neko)
    cat_x, cat_y = 1450, 825
    svg.append('<g id="manekiNeko" filter="url(#dropShadow)">')
    svg.append(f'<ellipse cx="{cat_x}" cy="{cat_y+15}" rx="22" ry="26" fill="#fbbf24" stroke="#78350f" stroke-width="2"/>')
    svg.append(f'<circle cx="{cat_x}" cy="{cat_y-12}" r="19" fill="#fbbf24" stroke="#78350f" stroke-width="2"/>')
    svg.append(f'<polygon points="{cat_x-16},{cat_y-20} {cat_x-8},{cat_y-34} {cat_x-2},{cat_y-24}" fill="#fbbf24" stroke="#78350f" stroke-width="1.5"/>')
    svg.append(f'<polygon points="{cat_x-14},{cat_y-22} {cat_x-9},{cat_y-31} {cat_x-4},{cat_y-24}" fill="#ef4444"/>')
    svg.append(f'<polygon points="{cat_x+2},{cat_y-24} {cat_x+8},{cat_y-34} {cat_x+16},{cat_y-20}" fill="#fbbf24" stroke="#78350f" stroke-width="1.5"/>')
    svg.append(f'<polygon points="{cat_x+4},{cat_y-24} {cat_x+9},{cat_y-31} {cat_x+14},{cat_y-22}" fill="#ef4444"/>')
    svg.append(f'<rect x="{cat_x-14}" y="{cat_y+3}" width="28" height="6" rx="2" fill="#dc2626"/>')
    svg.append(f'<circle cx="{cat_x}" cy="{cat_y+9}" r="5" fill="#fde047" stroke="#78350f" stroke-width="1.2"/>')
    svg.append(f'<ellipse cx="{cat_x-18}" cy="{cat_y-18}" rx="8" ry="14" fill="#fbbf24" stroke="#78350f" stroke-width="2" transform="rotate(-20 {cat_x-18} {cat_y-18})"/>')
    svg.append(f'<circle cx="{cat_x-20}" cy="{cat_y-28}" r="6" fill="#ffffff" stroke="#78350f" stroke-width="1.5"/>')
    svg.append(f'<path d="M {cat_x-10} {cat_y-13} Q {cat_x-6} {cat_y-17} {cat_x-2} {cat_y-13}" fill="none" stroke="#451a03" stroke-width="1.8" stroke-linecap="round"/>')
    svg.append(f'<path d="M {cat_x+2} {cat_y-13} Q {cat_x+6} {cat_y-17} {cat_x+10} {cat_y-13}" fill="none" stroke="#451a03" stroke-width="1.8" stroke-linecap="round"/>')
    svg.append(f'<ellipse cx="{cat_x}" cy="{cat_y-8}" rx="2" ry="1.5" fill="#ef4444"/>')
    svg.append(f'<circle cx="{cat_x-12}" cy="{cat_y-7}" r="4" fill="#f43f5e" opacity="0.6"/>')
    svg.append(f'<circle cx="{cat_x+12}" cy="{cat_y-7}" r="4" fill="#f43f5e" opacity="0.6"/>')
    svg.append('</g>')

    # -------------------------------------------------------------
    # 5. CENTERPIECE: THE HERO RAMEN BOWL & SERVING TRAY
    # -------------------------------------------------------------
    rb_cx, rb_cy = 760, 870
    rb_rx, rb_ry = 220, 120
    svg.append('<!-- HERO RAMEN BOWL & TRAY -->')
    svg.append('<g id="heroRamenStation" filter="url(#deepShadow)">')

    # Traditional Japanese Lacquer Serving Tray (Obon お盆) under bowl
    tray_w, tray_h = 570, 245
    svg.append(f'<ellipse cx="{rb_cx}" cy="{rb_cy+75}" rx="{tray_w*0.52}" ry="{tray_h*0.48}" fill="url(#trayWoodGrad)" stroke="#dc2626" stroke-width="4"/>')
    svg.append(f'<ellipse cx="{rb_cx}" cy="{rb_cy+75}" rx="{tray_w*0.48}" ry="{tray_h*0.44}" fill="#140a05" stroke="#78350f" stroke-width="2"/>')

    # Ceramic Chopstick Rest (Hashioki) and Wooden Chopsticks on front of tray
    h_x, h_y = rb_cx, rb_cy + 165
    svg.append(f'<ellipse cx="{h_x}" cy="{h_y}" rx="14" ry="7" fill="#f87171" stroke="#991b1b" stroke-width="1.5"/>')
    svg.append(f'<line x1="{h_x-120}" y1="{h_y-2}" x2="{h_x+120}" y2="{h_y-2}" stroke="#78350f" stroke-width="5" stroke-linecap="round"/>')
    svg.append(f'<line x1="{h_x-120}" y1="{h_y-2}" x2="{h_x+120}" y2="{h_y-2}" stroke="#d97706" stroke-width="2.5" stroke-linecap="round"/>')
    svg.append(f'<line x1="{h_x-120}" y1="{h_y+3}" x2="{h_x+120}" y2="{h_y+3}" stroke="#78350f" stroke-width="4" stroke-linecap="round"/>')
    svg.append(f'<line x1="{h_x-120}" y1="{h_y+3}" x2="{h_x+120}" y2="{h_y+3}" stroke="#d97706" stroke-width="2" stroke-linecap="round"/>')

    # Ceramic Donburi Bowl Body
    svg.append(f'<path d="M {rb_cx-rb_rx} {rb_cy} C {rb_cx-rb_rx*0.88} {rb_cy+150} {rb_cx-rb_rx*0.45} {rb_cy+180} {rb_cx} {rb_cy+180} C {rb_cx+rb_rx*0.45} {rb_cy+180} {rb_cx+rb_rx*0.88} {rb_cy+150} {rb_cx+rb_rx} {rb_cy} Z" fill="url(#bowlOuterGrad)" stroke="#020617" stroke-width="4"/>')
    svg.append(f'<ellipse cx="{rb_cx}" cy="{rb_cy+177}" rx="{rb_rx*0.42}" ry="16" fill="#1e293b" stroke="#090d16" stroke-width="2.5"/>')

    # Rim with Raimon Greek fret pattern
    svg.append(f'<ellipse cx="{rb_cx}" cy="{rb_cy}" rx="{rb_rx}" ry="{rb_ry}" fill="#dc2626" stroke="#991b1b" stroke-width="4"/>')
    svg.append(f'<ellipse cx="{rb_cx}" cy="{rb_cy}" rx="{rb_rx-6}" ry="{rb_ry-4}" fill="none" stroke="url(#raimonPattern)" stroke-width="12"/>')
    svg.append(f'<ellipse cx="{rb_cx}" cy="{rb_cy}" rx="{rb_rx-15}" ry="{rb_ry-10}" fill="#0f172a" stroke="#ffffff" stroke-width="2"/>')

    # Broth Surface
    svg.append(f'<ellipse cx="{rb_cx}" cy="{rb_cy}" rx="{rb_rx-18}" ry="{rb_ry-12}" fill="url(#ramenBrothGrad)"/>')

    # Broth oil rings
    oil_spots = [
        (rb_cx-80, rb_cy-20, 14, 8), (rb_cx-110, rb_cy+15, 18, 10),
        (rb_cx+90, rb_cy-25, 20, 11), (rb_cx+120, rb_cy+20, 15, 9),
        (rb_cx-30, rb_cy+45, 22, 12), (rb_cx+40, rb_cy+50, 16, 9)
    ]
    for ox, oy, orx, ory in oil_spots:
        svg.append(f'<ellipse cx="{ox}" cy="{oy}" rx="{orx}" ry="{ory}" fill="#fef08a" opacity="0.45" filter="url(#softBlur)"/>')
        svg.append(f'<ellipse cx="{ox}" cy="{oy}" rx="{orx*0.7}" ry="{ory*0.7}" fill="#facc15" opacity="0.6"/>')

    # Wavy noodles in broth
    svg.append('<g id="bowlNoodles" stroke="#eab308" stroke-linecap="round" fill="none">')
    noodle_in_bowl = [
        f"M {rb_cx-120} {rb_cy-10} Q {rb_cx-80} {rb_cy+40} {rb_cx-20} {rb_cy+15} Q {rb_cx+40} {rb_cy-10} {rb_cx+100} {rb_cy+10}",
        f"M {rb_cx-100} {rb_cy+15} Q {rb_cx-50} {rb_cy-25} {rb_cx} {rb_cy+25} Q {rb_cx+60} {rb_cy+45} {rb_cx+120} {rb_cy+5}",
        f"M {rb_cx-130} {rb_cy+10} Q {rb_cx-70} {rb_cy+50} {rb_cx-10} {rb_cy+35} Q {rb_cx+50} {rb_cy+20} {rb_cx+90} {rb_cy+35}",
        f"M {rb_cx-80} {rb_cy-30} Q {rb_cx-30} {rb_cy+10} {rb_cx+20} {rb_cy-20} Q {rb_cx+80} {rb_cy-10} {rb_cx+110} {rb_cy-20}",
        f"M {rb_cx-110} {rb_cy-5} Q {rb_cx-40} {rb_cy+30} {rb_cx+10} {rb_cy+5} Q {rb_cx+70} {rb_cy-15} {rb_cx+130} {rb_cy+15}",
    ]
    for nb in noodle_in_bowl:
        svg.append(f'<path d="{nb}" stroke-width="5"/>')
        svg.append(f'<path d="{nb}" stroke="#fef08a" stroke-width="2.2"/>')
    svg.append('</g>')

    # Crisp Nori Sheet
    svg.append('<g id="noriSheet" filter="url(#dropShadow)">')
    svg.append(f'<polygon points="{rb_cx-165},{rb_cy-110} {rb_cx-95},{rb_cy-135} {rb_cx-60},{rb_cy-15} {rb_cx-130},{rb_cy+10}" fill="url(#noriGrad)" stroke="#050a08" stroke-width="2.5"/>')
    svg.append(f'<polygon points="{rb_cx-162},{rb_cy-105} {rb_cx-98},{rb_cy-130} {rb_cx-65},{rb_cy-18} {rb_cx-128},{rb_cy+6}" fill="#0d1b14" opacity="0.6"/>')
    for spk_x, spk_y in [(-130, -80), (-110, -100), (-90, -60), (-120, -40), (-80, -30)]:
        svg.append(f'<circle cx="{rb_cx+spk_x}" cy="{rb_cy+spk_y}" r="2.5" fill="#2d4a3e" opacity="0.7"/>')
    svg.append('</g>')

    # 2 Chashu Pork Slices
    c1_x, c1_y = rb_cx - 55, rb_cy - 25
    svg.append(f'<g id="chashu1" filter="url(#dropShadow)">')
    svg.append(f'<ellipse cx="{c1_x}" cy="{c1_y}" rx="48" ry="32" fill="url(#chashuGrad)" stroke="#451a03" stroke-width="2.5"/>')
    svg.append(f'<path d="M {c1_x-28} {c1_y-8} Q {c1_x} {c1_y-20} {c1_x+25} {c1_y-6} Q {c1_x+28} {c1_y+16} {c1_x-5} {c1_y+18} Q {c1_x-22} {c1_y+10} {c1_x-10} {c1_y-4}" fill="none" stroke="#ffedd5" stroke-width="4.5" stroke-linecap="round"/>')
    svg.append(f'<ellipse cx="{c1_x+4}" cy="{c1_y+4}" rx="8" ry="5" fill="#fed7aa"/>')
    svg.append(f'<path d="M {c1_x-44} {c1_y} Q {c1_x-35} {c1_y-25} {c1_x} {c1_y-30}" fill="none" stroke="#2a0802" stroke-width="4"/>')
    svg.append('</g>')

    c2_x, c2_y = rb_cx - 20, rb_cy - 10
    svg.append(f'<g id="chashu2" filter="url(#dropShadow)">')
    svg.append(f'<ellipse cx="{c2_x}" cy="{c2_y}" rx="46" ry="30" fill="url(#chashuGrad)" stroke="#451a03" stroke-width="2.5"/>')
    svg.append(f'<path d="M {c2_x-26} {c2_y-8} Q {c2_x} {c2_y-18} {c2_x+24} {c2_y-6} Q {c2_x+26} {c2_y+15} {c2_x-4} {c2_y+16} Q {c2_x-20} {c2_y+8} {c2_x-8} {c2_y-4}" fill="none" stroke="#ffedd5" stroke-width="4" stroke-linecap="round"/>')
    svg.append(f'<ellipse cx="{c2_x+4}" cy="{c2_y+4}" rx="7" ry="4" fill="#fed7aa"/>')
    svg.append(f'<path d="M {c2_x+25} {c2_y-18} Q {c2_x+42} {c2_y} {c2_x+36} {c2_y+18}" fill="none" stroke="#2a0802" stroke-width="3.5"/>')
    svg.append('</g>')

    # Bamboo Shoots (Menma)
    svg.append('<g id="menma" filter="url(#dropShadow)">')
    for m_off, m_rot in [(0, -10), (14, 5), (28, -5)]:
        svg.append(f'<g transform="translate({rb_cx+30+m_off},{rb_cy-35}) rotate({m_rot})">')
        svg.append('<rect x="-8" y="-22" width="16" height="44" rx="4" fill="#d97706" stroke="#78350f" stroke-width="2"/>')
        svg.append('<line x1="-3" y1="-18" x2="-3" y2="18" stroke="#fde68a" stroke-width="2"/>')
        svg.append('</g>')
    svg.append('</g>')

    # 2 Ajitsuke Tamago (Marinated Ramen Egg) Halves
    e1_cx, e1_cy = rb_cx + 85, rb_cy + 5
    svg.append(f'<g id="egg1" filter="url(#dropShadow)">')
    svg.append(f'<ellipse cx="{e1_cx}" cy="{e1_cy}" rx="38" ry="28" fill="url(#eggWhiteGrad)" stroke="#92400e" stroke-width="2.5"/>')
    svg.append(f'<ellipse cx="{e1_cx-4}" cy="{e1_cy}" rx="22" ry="17" fill="url(#eggYolkGrad)" stroke="#c2410c" stroke-width="1.8"/>')
    svg.append(f'<ellipse cx="{e1_cx-10}" cy="{e1_cy-5}" rx="7" ry="4" fill="#ffffff" opacity="0.85"/>')
    svg.append(f'<circle cx="{e1_cx+4}" cy="{e1_cy+5}" r="3" fill="#ffffff" opacity="0.65"/>')
    svg.append('</g>')

    e2_cx, e2_cy = rb_cx + 50, rb_cy + 35
    svg.append(f'<g id="egg2" filter="url(#dropShadow)">')
    svg.append(f'<ellipse cx="{e2_cx}" cy="{e2_cy}" rx="36" ry="26" fill="url(#eggWhiteGrad)" stroke="#92400e" stroke-width="2.5"/>')
    svg.append(f'<ellipse cx="{e2_cx-3}" cy="{e2_cy}" rx="20" ry="15" fill="url(#eggYolkGrad)" stroke="#c2410c" stroke-width="1.8"/>')
    svg.append(f'<ellipse cx="{e2_cx-8}" cy="{e2_cy-4}" rx="6" ry="3.5" fill="#ffffff" opacity="0.85"/>')
    svg.append('</g>')

    # Narutomaki in bowl
    n_cx, n_cy = rb_cx - 70, rb_cy + 25
    svg.append(f'<g id="narutoInBowl" filter="url(#dropShadow)">')
    svg.append(f'<ellipse cx="{n_cx}" cy="{n_cy}" rx="24" ry="16" fill="#ffffff" stroke="#e2e8f0" stroke-width="2"/>')
    svg.append(f'<path d="M {n_cx} {n_cy} Q {n_cx+7} {n_cy+3} {n_cx+6} {n_cy+7} Q {n_cx+3} {n_cy+11} {n_cx-5} {n_cy+10} Q {n_cx-12} {n_cy+8} {n_cx-11} {n_cy+1} Q {n_cx-10} {n_cy-6} {n_cx} {n_cy-7} Q {n_cx+12} {n_cy-8} {n_cx+15} {n_cy-1} Q {n_cx+17} {n_cy+7} {n_cx+9} {n_cy+12}" fill="none" stroke="#ec4899" stroke-width="3.2" stroke-linecap="round"/>')
    svg.append('</g>')

    # Scallion (Negi) Mountain
    svg.append('<g id="scallionPile" filter="url(#dropShadow)">')
    for scx_off, scy_off in [
        (0, 0), (-14, -8), (12, -6), (-6, -14), (8, -12),
        (-22, 4), (18, 6), (-8, 8), (10, 10), (0, -18),
        (-16, -18), (14, -16), (-28, -4), (24, -2), (-2, 14),
        (-12, 12), (16, 14), (-4, -6), (6, 2), (-18, 2)
    ]:
        gx = rb_cx - 10 + scx_off
        gy = rb_cy + 15 + scy_off
        svg.append(f'<g transform="translate({gx},{gy})">')
        svg.append('<ellipse cx="0" cy="0" rx="9" ry="5.5" fill="#22c55e" stroke="#15803d" stroke-width="1.8"/>')
        svg.append('<ellipse cx="0" cy="0" rx="5" ry="3" fill="#bbf7d0"/>')
        svg.append('</g>')
    svg.append('</g>')

    # Sesame Seeds
    sesame_pts = [
        (rb_cx-40, rb_cy+40), (rb_cx-60, rb_cy+50), (rb_cx+20, rb_cy+55),
        (rb_cx-15, rb_cy+60), (rb_cx+70, rb_cy+40), (rb_cx-80, rb_cy-5),
        (rb_cx+110, rb_cy-5), (rb_cx-30, rb_cy-35), (rb_cx+5, rb_cy-30)
    ]
    for ssx, ssy in sesame_pts:
        svg.append(f'<ellipse cx="{ssx}" cy="{ssy}" rx="2.5" ry="1.5" fill="#fef9c3" stroke="#ca8a04" stroke-width="0.8"/>')

    # Ceramic Spoon (Renge)
    svg.append('<g id="rengeSpoon" filter="url(#dropShadow)">')
    svg.append(f'<path d="M {rb_cx-145} {rb_cy+75} Q {rb_cx-175} {rb_cy+90} {rb_cx-195} {rb_cy+70} L {rb_cx-188} {rb_cy+60} Q {rb_cx-168} {rb_cy+80} {rb_cx-140} {rb_cy+65} Z" fill="#ffffff" stroke="#cbd5e1" stroke-width="2"/>')
    svg.append(f'<path d="M {rb_cx-188} {rb_cy+66} Q {rb_cx-170} {rb_cy+82} {rb_cx-142} {rb_cy+70}" fill="none" stroke="#dc2626" stroke-width="3"/>')
    svg.append(f'<ellipse cx="{rb_cx-135}" cy="{rb_cy+65}" rx="24" ry="14" fill="#ffffff" stroke="#cbd5e1" stroke-width="2" transform="rotate(-15 {rb_cx-135} {rb_cy+65})"/>')
    svg.append(f'<ellipse cx="{rb_cx-134}" cy="{rb_cy+66}" rx="18" ry="9" fill="url(#ramenBrothGrad)" transform="rotate(-15 {rb_cx-135} {rb_cy+65})"/>')
    svg.append('</g>')

    svg.append('</g>') # End heroRamenStation

    # -------------------------------------------------------------
    # 6. AROMATIC BILLOWING STEAM (Framing the chef, face clear!)
    # -------------------------------------------------------------
    svg.append('<!-- RAMEN BOWL STEAM (FRAMING CURVES) -->')
    svg.append('<g id="bowlSteam" filter="url(#steamFilter)">')
    bowl_steam_paths = [
        f"M {rb_cx-60} {rb_cy-40} Q {rb_cx-140} {rb_cy-160} {rb_cx-170} {rb_cy-280} Q {rb_cx-190} {rb_cy-400} {rb_cx-130} {rb_cy-520}",
        f"M {rb_cx+60} {rb_cy-40} Q {rb_cx+140} {rb_cy-160} {rb_cx+180} {rb_cy-280} Q {rb_cx+200} {rb_cy-400} {rb_cx+150} {rb_cy-520}",
    ]
    for bsp in bowl_steam_paths:
        svg.append(f'<path d="{bsp}" fill="none" stroke="url(#steamGrad)" stroke-width="28" stroke-linecap="round"/>')
        svg.append(f'<path d="{bsp}" fill="none" stroke="#ffffff" stroke-width="10" stroke-linecap="round" opacity="0.4"/>')
    svg.append('</g>')

    # Vignette border
    svg.append('<!-- VIGNETTE BORDER -->')
    svg.append(f'<rect width="{w}" height="{h}" fill="none" stroke="#000000" stroke-width="12" opacity="0.55"/>')

    svg.append('</svg>')
    return "\n".join(svg)

def main():
    os.makedirs("output", exist_ok=True)
    svg_content = build_scene()
    out_svg = "output/octopus_chef_ramen_booth.svg"
    out_png = "output/octopus_chef_ramen_booth.png"

    with open(out_svg, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated SVG: {out_svg} ({len(svg_content)} bytes)")

    # Render PNG using macOS built-in QuickLook engine
    try:
        subprocess.run(["qlmanage", "-t", "-s", "1600", "-o", "/tmp", out_svg], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        tmp_png = f"/tmp/{os.path.basename(out_svg)}.png"
        if os.path.exists(tmp_png):
            shutil.copy2(tmp_png, out_png); os.remove(tmp_png)
            print(f"Successfully rendered high-res PNG: {out_png} ({os.path.getsize(out_png)} bytes)")
    except Exception as e:
        print(f"Note on PNG rendering: {e}")

if __name__ == "__main__":
    main()
