#!/usr/bin/env python3
"""
Octopus Ramen Chef Artwork Generator (Polished Masterpiece Edition)
Produces an elaborate, vibrant, highly-polished SVG vector artwork and high-res PNG
of an octopus chef multitasking at a traditional Japanese ramen booth (yatai).
"""

import math
import os
import subprocess

WIDTH = 1200
HEIGHT = 900

# ---------------------------------------------------------------------------
# Vector Math & Curve Utilities
# ---------------------------------------------------------------------------

def cubic_bezier(p0, p1, p2, p3, t):
    it = 1.0 - t
    x = it**3 * p0[0] + 3*it**2*t * p1[0] + 3*it*t**2 * p2[0] + t**3 * p3[0]
    y = it**3 * p0[1] + 3*it**2*t * p1[1] + 3*it*t**2 * p2[1] + t**3 * p3[1]
    return (x, y)

def cubic_bezier_deriv(p0, p1, p2, p3, t):
    it = 1.0 - t
    dx = 3*it**2 * (p1[0] - p0[0]) + 6*it*t * (p2[0] - p1[0]) + 3*t**2 * (p3[0] - p2[0])
    dy = 3*it**2 * (p1[1] - p0[1]) + 6*it*t * (p2[1] - p1[1]) + 3*t**2 * (p3[1] - p2[1])
    return (dx, dy)

def build_spine_samples(segments, samples_per_seg=40):
    total_pts = []
    num_segs = len(segments)
    for seg_idx, (p0, p1, p2, p3) in enumerate(segments):
        start_i = 0 if seg_idx == 0 else 1
        for i in range(start_i, samples_per_seg + 1):
            t = i / float(samples_per_seg)
            t_global = (seg_idx + t) / float(num_segs)
            pos = cubic_bezier(p0, p1, p2, p3, t)
            dx, dy = cubic_bezier_deriv(p0, p1, p2, p3, t)
            length = math.hypot(dx, dy)
            if length < 1e-6:
                nx, ny = 0.0, 1.0
                tx, ty = 1.0, 0.0
                angle = 0.0
            else:
                tx, ty = dx / length, dy / length
                nx, ny = -ty, tx
                angle = math.degrees(math.atan2(dy, dx))
            total_pts.append({
                'pos': pos,
                'tangent': (tx, ty),
                'normal': (nx, ny),
                't_global': t_global,
                'angle': angle
            })
    return total_pts

def generate_tentacle(segments, w_start=44, w_end=9, sucker_side=1, num_suckers=11, samples_per_seg=40):
    """
    Builds a beautifully curved, tapered octopus tentacle.
    sucker_side: 1 for left of normal, -1 for right of normal.
    """
    spine = build_spine_samples(segments, samples_per_seg)
    n = len(spine)
    
    left_edge = []
    right_edge = []
    underbelly_edge = []
    highlight_edge = []
    
    for i, pt in enumerate(spine):
        x, y = pt['pos']
        nx, ny = pt['normal']
        t = pt['t_global']
        
        # Calculate width
        w = w_start * (1.0 - (t ** 1.15)) + w_end * (t ** 0.8)
            
        lx = x + nx * (w * 0.5)
        ly = y + ny * (w * 0.5)
        rx = x - nx * (w * 0.5)
        ry = y - ny * (w * 0.5)
        
        left_edge.append((lx, ly))
        right_edge.append((rx, ry))
        
        # Underbelly ribbon along sucker side
        ub_factor = 0.55
        if sucker_side > 0:
            ub_x = x + nx * (w * 0.5 * ub_factor)
            ub_y = y + ny * (w * 0.5 * ub_factor)
        else:
            ub_x = x - nx * (w * 0.5 * ub_factor)
            ub_y = y - ny * (w * 0.5 * ub_factor)
        underbelly_edge.append((ub_x, ub_y))
        
        # Dorsal highlight along opposite edge
        hl_factor = 0.30
        if sucker_side > 0:
            hx = x - nx * (w * 0.5 * hl_factor)
            hy = y - ny * (w * 0.5 * hl_factor)
        else:
            hx = x + nx * (w * 0.5 * hl_factor)
            hy = y + ny * (w * 0.5 * hl_factor)
        highlight_edge.append((hx, hy))

    # Outer tentacle path
    path_d = [f"M {left_edge[0][0]:.1f} {left_edge[0][1]:.1f}"]
    for lx, ly in left_edge[1:]:
        path_d.append(f"L {lx:.1f} {ly:.1f}")
    tip_pt = spine[-1]['pos']
    path_d.append(f"Q {tip_pt[0]:.1f} {tip_pt[1]:.1f} {right_edge[-1][0]:.1f} {right_edge[-1][1]:.1f}")
    for rx, ry in reversed(right_edge[:-1]):
        path_d.append(f"L {rx:.1f} {ry:.1f}")
    path_d.append("Z")
    main_path = " ".join(path_d)

    # Underbelly ribbon
    ub_path_d = []
    if sucker_side > 0:
        ub_path_d.append(f"M {left_edge[0][0]:.1f} {left_edge[0][1]:.1f}")
        for lx, ly in left_edge[1:]:
            ub_path_d.append(f"L {lx:.1f} {ly:.1f}")
        ub_path_d.append(f"L {underbelly_edge[-1][0]:.1f} {underbelly_edge[-1][1]:.1f}")
        for ux, uy in reversed(underbelly_edge[:-1]):
            ub_path_d.append(f"L {ux:.1f} {uy:.1f}")
    else:
        ub_path_d.append(f"M {right_edge[0][0]:.1f} {right_edge[0][1]:.1f}")
        for rx, ry in right_edge[1:]:
            ub_path_d.append(f"L {rx:.1f} {ry:.1f}")
        ub_path_d.append(f"L {underbelly_edge[-1][0]:.1f} {underbelly_edge[-1][1]:.1f}")
        for ux, uy in reversed(underbelly_edge[:-1]):
            ub_path_d.append(f"L {ux:.1f} {uy:.1f}")
    ub_path_d.append("Z")
    underbelly_path = " ".join(ub_path_d)

    # Dorsal highlight curve
    hl_start = int(n * 0.12)
    hl_end = int(n * 0.85)
    hl_path_d = [f"M {highlight_edge[hl_start][0]:.1f} {highlight_edge[hl_start][1]:.1f}"]
    for hx, hy in highlight_edge[hl_start + 1 : hl_end]:
        hl_path_d.append(f"L {hx:.1f} {hy:.1f}")
    highlight_path = " ".join(hl_path_d)

    # Suction cups
    suckers = []
    step = (n - 14) / float(num_suckers + 1)
    for s_idx in range(1, num_suckers + 1):
        idx = int(7 + s_idx * step)
        if idx >= n - 2:
            break
        pt = spine[idx]
        t = pt['t_global']
        w = w_start * (1.0 - (t ** 1.15)) + w_end * (t ** 0.8)
        
        if sucker_side > 0:
            ex = left_edge[idx][0]
            ey = left_edge[idx][1]
            out_nx, out_ny = pt['normal'][0], pt['normal'][1]
        else:
            ex = right_edge[idx][0]
            ey = right_edge[idx][1]
            out_nx, out_ny = -pt['normal'][0], -pt['normal'][1]
            
        sucker_r = max(4.0, w * 0.38)
        cx = ex + out_nx * (sucker_r * 0.40)
        cy = ey + out_ny * (sucker_r * 0.40)
        norm_angle = math.degrees(math.atan2(out_ny, out_nx))
        
        suckers.append({
            'cx': cx,
            'cy': cy,
            'rx': sucker_r,
            'ry': sucker_r * 0.72,
            'angle': norm_angle
        })

    return {
        'main_path': main_path,
        'underbelly_path': underbelly_path,
        'highlight_path': highlight_path,
        'suckers': suckers,
        'tip': spine[-1]['pos'],
        'base': spine[0]['pos']
    }

def render_tentacle_svg(t_data, tentacle_id):
    """Generates the SVG group for a tentacle including volume, underbelly, suckers, highlight."""
    xml = [f'<g id="tentacle-{tentacle_id}">']
    # Ambient shadow
    xml.append(f'  <path d="{t_data["main_path"]}" fill="none" stroke="#4a040b" stroke-width="7" opacity="0.45"/>')
    # Main outer skin
    xml.append(f'  <path d="{t_data["main_path"]}" fill="url(#grad-octo-red)" stroke="#7a0712" stroke-width="2.5" stroke-linejoin="round"/>')
    # Underbelly strip
    xml.append(f'  <path d="{t_data["underbelly_path"]}" fill="url(#grad-octo-peach)" opacity="0.96"/>')
    # Boundary line
    xml.append(f'  <path d="{t_data["underbelly_path"]}" fill="none" stroke="#e07a5f" stroke-width="1.2" opacity="0.6"/>')
    # Dorsal highlight
    xml.append(f'  <path d="{t_data["highlight_path"]}" fill="none" stroke="#ff998a" stroke-width="3.2" stroke-linecap="round" opacity="0.75"/>')
    
    # Suction cups
    for s in t_data['suckers']:
        cx, cy = s['cx'], s['cy']
        rx, ry = s['rx'], s['ry']
        ang = s['angle']
        xml.append(f'  <g transform="translate({cx:.1f},{cy:.1f}) rotate({ang:.1f})">')
        xml.append(f'    <ellipse cx="0" cy="0" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#grad-sucker-rim)" stroke="#d9384e" stroke-width="1.6"/>')
        inner_rx = rx * 0.58
        inner_ry = ry * 0.55
        xml.append(f'    <ellipse cx="0" cy="0" rx="{inner_rx:.1f}" ry="{inner_ry:.1f}" fill="url(#grad-sucker-pit)"/>')
        xml.append(f'    <ellipse cx="{-inner_rx*0.28:.1f}" cy="{-inner_ry*0.28:.1f}" rx="{inner_rx*0.28:.1f}" ry="{inner_ry*0.22:.1f}" fill="#ffffff" opacity="0.85"/>')
        xml.append('  </g>')
        
    xml.append('</g>')
    return "\n".join(xml)

# ---------------------------------------------------------------------------
# SVG Definitions & Gradients
# ---------------------------------------------------------------------------

def build_defs():
    return """
  <defs>
    <!-- Sky Background -->
    <linearGradient id="grad-sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#070a14"/>
      <stop offset="60%" stop-color="#12162a"/>
      <stop offset="100%" stop-color="#1c162e"/>
    </linearGradient>

    <!-- Filters -->
    <filter id="glow-lantern-red" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="24" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="glow-lantern-amber" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="24" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="glow-flame" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="12" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="steam-blur" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="8"/>
    </filter>

    <filter id="subtle-shadow" x="-15%" y="-15%" width="130%" height="130%">
      <feDropShadow dx="0" dy="5" stdDeviation="5" flood-color="#04060a" flood-opacity="0.55"/>
    </filter>

    <filter id="bowl-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="16" stdDeviation="12" flood-color="#000000" flood-opacity="0.85"/>
    </filter>

    <!-- Octopus Head Gradient -->
    <radialGradient id="grad-octo-head" cx="44%" cy="36%" r="60%">
      <stop offset="0%" stop-color="#ff7b69"/>
      <stop offset="25%" stop-color="#f43f3f"/>
      <stop offset="65%" stop-color="#c81e26"/>
      <stop offset="90%" stop-color="#931019"/>
      <stop offset="100%" stop-color="#6b060d"/>
    </radialGradient>

    <!-- Tentacle Red Gradient -->
    <linearGradient id="grad-octo-red" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ff6154"/>
      <stop offset="45%" stop-color="#e2222a"/>
      <stop offset="85%" stop-color="#a8121d"/>
      <stop offset="100%" stop-color="#730911"/>
    </linearGradient>

    <!-- Underbelly Peach Gradient -->
    <linearGradient id="grad-octo-peach" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#fff8f2"/>
      <stop offset="50%" stop-color="#fed7aa"/>
      <stop offset="100%" stop-color="#fba86c"/>
    </linearGradient>

    <!-- Suction Cup Rim -->
    <linearGradient id="grad-sucker-rim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="60%" stop-color="#ffeedb"/>
      <stop offset="100%" stop-color="#fed7aa"/>
    </linearGradient>

    <!-- Suction Cup Pit -->
    <radialGradient id="grad-sucker-pit" cx="45%" cy="45%" r="52%">
      <stop offset="0%" stop-color="#f43f5e"/>
      <stop offset="70%" stop-color="#be123c"/>
      <stop offset="100%" stop-color="#881337"/>
    </radialGradient>

    <!-- Eyes -->
    <radialGradient id="grad-iris" cx="38%" cy="38%" r="62%">
      <stop offset="0%" stop-color="#451e12"/>
      <stop offset="60%" stop-color="#1e0b05"/>
      <stop offset="100%" stop-color="#0a0302"/>
    </radialGradient>

    <!-- Yatai Wood Architecture -->
    <linearGradient id="grad-roof" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#3c2114"/>
      <stop offset="50%" stop-color="#26130b"/>
      <stop offset="100%" stop-color="#170a05"/>
    </linearGradient>

    <linearGradient id="grad-beam" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#46281a"/>
      <stop offset="40%" stop-color="#643c29"/>
      <stop offset="75%" stop-color="#46281a"/>
      <stop offset="100%" stop-color="#2a160d"/>
    </linearGradient>

    <linearGradient id="grad-counter" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#f5af5e"/>
      <stop offset="10%" stop-color="#db8a36"/>
      <stop offset="60%" stop-color="#a4551a"/>
      <stop offset="100%" stop-color="#642f0c"/>
    </linearGradient>

    <linearGradient id="grad-counter-bevel" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffdfa4"/>
      <stop offset="100%" stop-color="#db8a36"/>
    </linearGradient>

    <linearGradient id="grad-counter-apron" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#351a0b"/>
      <stop offset="100%" stop-color="#140803"/>
    </linearGradient>

    <linearGradient id="grad-noren" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#18233d"/>
      <stop offset="65%" stop-color="#121a2e"/>
      <stop offset="100%" stop-color="#0a0e1c"/>
    </linearGradient>

    <!-- Lantern Glow Gradients -->
    <radialGradient id="grad-lantern-glow-red" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ff7525" stop-opacity="0.88"/>
      <stop offset="45%" stop-color="#e11d48" stop-opacity="0.42"/>
      <stop offset="100%" stop-color="#991b1b" stop-opacity="0"/>
    </radialGradient>

    <linearGradient id="grad-lantern-red" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#991b1b"/>
      <stop offset="25%" stop-color="#dc2626"/>
      <stop offset="50%" stop-color="#fca5a5"/>
      <stop offset="75%" stop-color="#dc2626"/>
      <stop offset="100%" stop-color="#7f1d1d"/>
    </linearGradient>

    <radialGradient id="grad-lantern-glow-amber" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#fde047" stop-opacity="0.88"/>
      <stop offset="45%" stop-color="#f59e0b" stop-opacity="0.42"/>
      <stop offset="100%" stop-color="#b45309" stop-opacity="0"/>
    </radialGradient>

    <linearGradient id="grad-lantern-amber" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#b45309"/>
      <stop offset="25%" stop-color="#f59e0b"/>
      <stop offset="50%" stop-color="#fef3c7"/>
      <stop offset="75%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#92400e"/>
    </linearGradient>

    <!-- Bowl & Food -->
    <radialGradient id="grad-bowl-outer" cx="45%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#2a303c"/>
      <stop offset="45%" stop-color="#14181f"/>
      <stop offset="85%" stop-color="#090b0e"/>
      <stop offset="100%" stop-color="#040507"/>
    </radialGradient>

    <radialGradient id="grad-broth" cx="50%" cy="38%" r="56%">
      <stop offset="0%" stop-color="#fbbf24"/>
      <stop offset="30%" stop-color="#d97706"/>
      <stop offset="75%" stop-color="#8a3b0a"/>
      <stop offset="100%" stop-color="#3d1602"/>
    </radialGradient>

    <radialGradient id="grad-egg-yolk" cx="38%" cy="35%" r="62%">
      <stop offset="0%" stop-color="#fef08a"/>
      <stop offset="25%" stop-color="#f59e0b"/>
      <stop offset="70%" stop-color="#ea580c"/>
      <stop offset="100%" stop-color="#be3e0a"/>
    </radialGradient>

    <linearGradient id="grad-chashu-meat" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#e08838"/>
      <stop offset="50%" stop-color="#b85a1a"/>
      <stop offset="100%" stop-color="#7c340a"/>
    </linearGradient>

    <!-- Metal Equipment -->
    <linearGradient id="grad-stockpot" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#556275"/>
      <stop offset="25%" stop-color="#8898ac"/>
      <stop offset="45%" stop-color="#f1f5f9"/>
      <stop offset="60%" stop-color="#cbd5e1"/>
      <stop offset="85%" stop-color="#556275"/>
      <stop offset="100%" stop-color="#283341"/>
    </linearGradient>

    <!-- Blowtorch Flame -->
    <linearGradient id="grad-flame-core" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="60%" stop-color="#0284c7"/>
      <stop offset="100%" stop-color="#0369a1" stop-opacity="0"/>
    </linearGradient>

    <linearGradient id="grad-flame-outer" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#fde047"/>
      <stop offset="35%" stop-color="#f97316"/>
      <stop offset="75%" stop-color="#dc2626"/>
      <stop offset="100%" stop-color="#991b1b" stop-opacity="0"/>
    </linearGradient>

    <!-- Menu Board Gradient -->
    <linearGradient id="grad-kifuda" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#e3be88"/>
      <stop offset="50%" stop-color="#c5995e"/>
      <stop offset="100%" stop-color="#a3763c"/>
    </linearGradient>
  </defs>
"""

# ---------------------------------------------------------------------------
# Background & Booth Architecture
# ---------------------------------------------------------------------------

def build_background():
    xml = ['<!-- BACKGROUND & ENVIRONMENT -->', '<g id="background">']
    xml.append(f'  <rect width="{WIDTH}" height="{HEIGHT}" fill="url(#grad-sky)"/>')
    
    # Warm twilight bokeh circles
    bokeh_pts = [
        (130, 160, 26, "#ffaa44", 0.14),
        (280, 120, 20, "#ffdd77", 0.16),
        (450, 90, 32, "#38bdf8", 0.08),
        (750, 90, 24, "#ff9955", 0.12),
        (920, 130, 30, "#ffaa44", 0.15),
        (1080, 170, 22, "#ff5544", 0.12),
        (210, 270, 38, "#ff8833", 0.10),
        (990, 280, 36, "#ffaa33", 0.10)
    ]
    for bx, by, br, bc, bo in bokeh_pts:
        xml.append(f'  <circle cx="{bx}" cy="{by}" r="{br}" fill="{bc}" opacity="{bo}" filter="url(#steam-blur)"/>')

    # Yatai Back Wall (Vertical Cedar Planks)
    xml.append('  <!-- Back Wood Wall Planks -->')
    xml.append('  <g id="back-wall">')
    for px in range(70, 1131, 46):
        xml.append(f'    <rect x="{px}" y="110" width="44" height="550" fill="#29150b"/>')
        xml.append(f'    <rect x="{px}" y="110" width="3" height="550" fill="#3b1e11" opacity="0.45"/>')
        xml.append(f'    <line x1="{px+45}" y1="110" x2="{px+45}" y2="660" stroke="#140803" stroke-width="2"/>')
    xml.append('  </g>')

    # Kitchen Backsplash behind stove
    xml.append('  <rect x="150" y="370" width="260" height="260" fill="#313b49" opacity="0.65"/>')
    xml.append('  <rect x="150" y="370" width="260" height="8" fill="#475569"/>')

    # Menu Plaques (Kifuda) hanging on the back wall
    menu_items = [
        (330, 220, "濃厚豚骨", "950円"),
        (400, 220, "秘伝醤油", "880円"),
        (780, 220, "旨辛味噌", "920円"),
        (850, 220, "替玉一玉", "100円"),
    ]
    for mx, my, title, price in menu_items:
        xml.append(f'  <g transform="translate({mx}, {my})" filter="url(#subtle-shadow)">')
        xml.append('    <rect x="-24" y="0" width="48" height="140" rx="3" fill="url(#grad-kifuda)" stroke="#633e17" stroke-width="2"/>')
        xml.append('    <circle cx="0" cy="12" r="3.5" fill="#351c0a"/>')
        xml.append('    <line x1="0" y1="0" x2="0" y2="12" stroke="#7a1f0d" stroke-width="2"/>')
        xml.append('    <rect x="-16" y="112" width="14" height="14" rx="2" fill="#b91c1c"/>')
        xml.append('    <rect x="-14" y="114" width="10" height="10" fill="none" stroke="#fca5a5" stroke-width="1"/>')
        for i, char in enumerate(title):
            xml.append(f'    <text x="0" y="{42 + i*20}" font-family="Hiragino Sans, Meiryo, sans-serif" font-weight="900" font-size="14" fill="#251004" text-anchor="middle">{char}</text>')
        xml.append(f'    <text x="14" y="123" font-family="Hiragino Sans, sans-serif" font-weight="700" font-size="9" fill="#522708" text-anchor="end">{price}</text>')
        xml.append('  </g>')

    # Upper Shelf with Sake Cask & Bowls
    xml.append('  <g id="upper-shelf">')
    xml.append('    <rect x="740" y="380" width="270" height="14" fill="#3e2110" stroke="#1f0e04" stroke-width="2"/>')
    # Sake barrel
    xml.append('    <g transform="translate(930, 315)">')
    xml.append('      <rect x="-35" y="0" width="70" height="65" rx="6" fill="#ded0ba" stroke="#4d3416" stroke-width="3"/>')
    xml.append('      <line x1="-35" y1="18" x2="35" y2="18" stroke="#36220f" stroke-width="4"/>')
    xml.append('      <line x1="-35" y1="47" x2="35" y2="47" stroke="#36220f" stroke-width="4"/>')
    xml.append('      <circle cx="0" cy="32" r="16" fill="#b91c1c"/>')
    xml.append('      <text x="0" y="38" font-family="Hiragino Sans, sans-serif" font-weight="bold" font-size="16" fill="#ffffff" text-anchor="middle">酒</text>')
    xml.append('    </g>')
    # Bowls on shelf
    for idx, (bx, by, col) in enumerate([(770, 350, "#1e293b"), (770, 362, "#0f172a"), (770, 374, "#334155"),
                                         (830, 355, "#b45309"), (830, 368, "#78350f"), (830, 378, "#92400e")]):
        xml.append(f'    <path d="M {bx-24} {by} Q {bx} {by+12} {bx+24} {by} L {bx+18} {by+12} L {bx-18} {by+12} Z" fill="{col}" stroke="#0a0a0a" stroke-width="1.5"/>')
    xml.append('  </g>')

    # Right Prep & Grill Counter Table (X: 800 to 1020, Y: 440 to 625)
    xml.append('  <!-- Right Side Kitchen Prep Station -->')
    xml.append('  <g id="right-prep-table">')
    xml.append('    <rect x="800" y="440" width="220" height="185" fill="#242f3d" stroke="#131b24" stroke-width="2"/>')
    xml.append('    <rect x="795" y="435" width="230" height="10" rx="2" fill="#475569" stroke="#334155" stroke-width="1.5"/>')
    # Wooden cutting/grill board resting on prep table
    xml.append('    <ellipse cx="890" cy="442" rx="55" ry="14" fill="#a16207" stroke="#713f12" stroke-width="2"/>')
    xml.append('    <ellipse cx="890" cy="440" rx="50" ry="11" fill="#ca8a04" opacity="0.8"/>')
    xml.append('  </g>')

    # Boiling Stockpot Station on Left
    xml.append('  <!-- Simmering Stockpot Station -->')
    xml.append('  <g id="stockpot" filter="url(#subtle-shadow)">')
    xml.append('    <rect x="170" y="580" width="180" height="45" fill="#182230" stroke="#0a0f16" stroke-width="2"/>')
    xml.append('    <ellipse cx="260" cy="582" rx="65" ry="6" fill="#38bdf8" opacity="0.8" filter="url(#steam-blur)"/>')
    xml.append('    <rect x="185" y="460" width="150" height="120" rx="6" fill="url(#grad-stockpot)" stroke="#2b3644" stroke-width="2.5"/>')
    xml.append('    <path d="M 185 490 C 165 490 165 520 185 520" fill="none" stroke="#cbd5e1" stroke-width="8" stroke-linecap="round"/>')
    xml.append('    <path d="M 335 490 C 355 490 355 520 335 520" fill="none" stroke="#cbd5e1" stroke-width="8" stroke-linecap="round"/>')
    xml.append('    <ellipse cx="260" cy="460" rx="75" ry="18" fill="#475569" stroke="#334155" stroke-width="2"/>')
    xml.append('    <ellipse cx="260" cy="462" rx="70" ry="14" fill="url(#grad-broth)"/>')
    xml.append('    <rect x="225" y="457" width="25" height="6" rx="3" fill="#22c55e" transform="rotate(-15, 225, 457)"/>')
    xml.append('    <rect x="265" y="460" width="30" height="6" rx="3" fill="#16a34a" transform="rotate(20, 265, 460)"/>')
    xml.append('    <ellipse cx="250" cy="465" rx="10" ry="6" fill="#fed7aa" opacity="0.8"/>')
    for bub_x, bub_y, bub_r in [(235, 462, 3), (255, 459, 4), (280, 464, 3.5), (270, 468, 2.5)]:
        xml.append(f'    <circle cx="{bub_x}" cy="{bub_y}" r="{bub_r}" fill="#fde68a" opacity="0.85"/>')
    xml.append('  </g>')

    # Steam from Cauldron
    xml.append('  <g id="pot-steam" opacity="0.55" filter="url(#steam-blur)">')
    xml.append('    <path d="M 220 440 C 200 380 240 320 220 260 C 200 200 260 160 240 110" fill="none" stroke="#ffffff" stroke-width="26" stroke-linecap="round"/>')
    xml.append('    <path d="M 270 430 C 300 370 260 300 290 240 C 320 180 280 140 310 90" fill="none" stroke="#e0f2fe" stroke-width="20" stroke-linecap="round"/>')
    xml.append('  </g>')

    xml.append('</g>')
    return "\n".join(xml)

# ---------------------------------------------------------------------------
# Counter Structure
# ---------------------------------------------------------------------------

def build_counter():
    xml = ['<!-- COUNTER STRUCTURE -->', '<g id="counter-structure">']
    xml.append('  <rect x="0" y="670" width="1200" height="230" fill="url(#grad-counter-apron)"/>')
    for px in range(0, 1201, 36):
        xml.append(f'    <line x1="{px}" y1="670" x2="{px}" y2="900" stroke="#0d0502" stroke-width="2.5"/>')
        xml.append(f'    <line x1="{px+2}" y1="670" x2="{px+2}" y2="900" stroke="#351a0b" stroke-width="1.5" opacity="0.4"/>')

    xml.append('  <!-- Hinoki Counter Slab -->')
    xml.append('  <polygon points="0,630 1200,630 1200,675 0,675" fill="url(#grad-counter)"/>')
    xml.append('  <polygon points="0,625 1200,625 1200,632 0,632" fill="url(#grad-counter-bevel)"/>')
    xml.append('  <line x1="0" y1="625" x2="1200" y2="625" stroke="#ffedd5" stroke-width="2.5" opacity="0.85"/>')
    xml.append('  <line x1="0" y1="632" x2="1200" y2="632" stroke="#78350f" stroke-width="2"/>')
    for gy in [642, 654, 664]:
        xml.append(f'  <line x1="0" y1="{gy}" x2="1200" y2="{gy}" stroke="#78350f" stroke-width="1.2" opacity="0.25"/>')

    xml.append('</g>')
    return "\n".join(xml)

# ---------------------------------------------------------------------------
# Roof, Noren & Glowing Lanterns
# ---------------------------------------------------------------------------

def build_yatai_roof_and_noren():
    xml = ['<!-- YATAI ROOF, LANTERNS, & NOREN -->', '<g id="roof-structure">']
    
    for col_x in [60, 1080]:
        xml.append(f'  <rect x="{col_x}" y="70" width="50" height="600" fill="url(#grad-beam)" stroke="#170903" stroke-width="3"/>')
        xml.append(f'  <rect x="{col_x-2}" y="190" width="54" height="14" fill="#334155" stroke="#0f172a" stroke-width="1.5"/>')

    xml.append('  <rect x="30" y="80" width="1140" height="34" fill="url(#grad-beam)" stroke="#170903" stroke-width="3"/>')
    for bx in [150, 370, 600, 830, 1050]:
        xml.append(f'  <polygon points="{bx-12},114 {bx+12},114 {bx},138" fill="#351a0b" stroke="#140803" stroke-width="2"/>')

    xml.append('  <polygon points="10,30 1190,30 1200,85 0,85" fill="url(#grad-roof)" stroke="#140803" stroke-width="3"/>')
    for rx in range(25, 1195, 36):
        xml.append(f'  <line x1="{rx+8}" y1="32" x2="{rx}" y2="83" stroke="#4a2815" stroke-width="3.5"/>')
        xml.append(f'  <circle cx="{rx}" cy="84" r="5" fill="#26130b" stroke="#140803" stroke-width="1.5"/>')

    xml.append('  <!-- Noren Hanging Curtain -->')
    xml.append('  <g id="noren" filter="url(#subtle-shadow)">')
    xml.append('    <rect x="90" y="115" width="1020" height="10" rx="4" fill="#ca8a04" stroke="#68390e" stroke-width="1.5"/>')
    
    panels = [
        (120, 180, "元"),
        (320, 180, "祖"),
        (520, 180, "蛸"),
        (720, 180, "八"),
        (920, 180, "麺")
    ]
    for px, pw, char in panels:
        xml.append(f'    <rect x="{px+22}" y="108" width="14" height="15" rx="3" fill="#18233d" stroke="#0a0e1c" stroke-width="1.5"/>')
        xml.append(f'    <rect x="{px+pw-36}" y="108" width="14" height="15" rx="3" fill="#18233d" stroke="#0a0e1c" stroke-width="1.5"/>')
        panel_d = f"M {px} 122 L {px+pw} 122 L {px+pw} 225 Q {px+pw*0.5} 238 {px} 225 Z"
        xml.append(f'    <path d="{panel_d}" fill="url(#grad-noren)" stroke="#070a14" stroke-width="2"/>')
        wave_y = 208
        for wx in range(px + 14, px + pw - 8, 24):
            xml.append(f'    <path d="M {wx-10} {wave_y} A 10 10 0 0 1 {wx+10} {wave_y}" fill="none" stroke="#f8fafc" stroke-width="2" opacity="0.85"/>')
            xml.append(f'    <path d="M {wx-6} {wave_y} A 6 6 0 0 1 {wx+6} {wave_y}" fill="none" stroke="#f8fafc" stroke-width="1.5" opacity="0.85"/>')
        
        cx_noren = px + pw * 0.5
        if char == "蛸":
            xml.append(f'    <circle cx="{cx_noren}" cy="168" r="28" fill="none" stroke="#ffffff" stroke-width="3"/>')
            xml.append(f'    <circle cx="{cx_noren}" cy="168" r="24" fill="none" stroke="#ffffff" stroke-width="1.2" stroke-dasharray="4,3"/>')
            xml.append(f'    <path d="M {cx_noren-14} 168 C {cx_noren-14} 153 {cx_noren+14} 153 {cx_noren+14} 168 C {cx_noren+14} 178 {cx_noren-14} 178 Z" fill="#ef4444"/>')
            xml.append(f'    <circle cx="{cx_noren-5}" cy="165" r="2.5" fill="#ffffff"/>')
            xml.append(f'    <circle cx="{cx_noren+5}" cy="165" r="2.5" fill="#ffffff"/>')
            xml.append(f'    <circle cx="{cx_noren-5}" cy="165" r="1.2" fill="#000000"/>')
            xml.append(f'    <circle cx="{cx_noren+5}" cy="165" r="1.2" fill="#000000"/>')
            xml.append(f'    <path d="M {cx_noren-10} 177 Q {cx_noren-6} 183 {cx_noren-2} 177 Q {cx_noren+2} 183 {cx_noren+6} 177 Q {cx_noren+10} 183 {cx_noren+12} 177" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round"/>')
        else:
            xml.append(f'    <circle cx="{cx_noren}" cy="168" r="24" fill="none" stroke="#ffffff" stroke-width="2.5" opacity="0.9"/>')
            xml.append(f'    <text x="{cx_noren}" y="176" font-family="Hiragino Sans, Meiryo, sans-serif" font-weight="900" font-size="22" fill="#ffffff" text-anchor="middle">{char}</text>')
    xml.append('  </g>')

    # LEFT LANTERN (Red - Ramen)
    xml.append('  <!-- Left Glowing Paper Lantern -->')
    xml.append('  <g id="left-lantern">')
    xml.append('    <circle cx="190" cy="275" r="120" fill="url(#grad-lantern-glow-red)" filter="url(#glow-lantern-red)"/>')
    xml.append('    <line x1="190" y1="80" x2="190" y2="215" stroke="#182230" stroke-width="2.5"/>')
    xml.append('    <ellipse cx="190" cy="217" rx="30" ry="7" fill="#18181b" stroke="#09090b" stroke-width="2"/>')
    xml.append('    <rect x="166" y="207" width="48" height="10" rx="3" fill="#27272a"/>')
    xml.append('    <path d="M 166 220 C 130 245 130 305 166 330 L 214 330 C 250 305 250 245 214 220 Z" fill="url(#grad-lantern-red)" stroke="#7f1d1d" stroke-width="2.5"/>')
    for ry in [240, 260, 280, 300, 315]:
        xml.append(f'    <ellipse cx="190" cy="{ry}" rx="{48 - abs(ry-275)*0.38:.1f}" ry="6" fill="none" stroke="#7f1d1d" stroke-width="1.8" opacity="0.75"/>')
    xml.append('    <text x="190" y="266" font-family="Hiragino Sans, Meiryo, sans-serif" font-weight="900" font-size="28" fill="#18181b" text-anchor="middle" stroke="#ffffff" stroke-width="1" paint-order="stroke fill">拉</text>')
    xml.append('    <text x="190" y="300" font-family="Hiragino Sans, Meiryo, sans-serif" font-weight="900" font-size="28" fill="#18181b" text-anchor="middle" stroke="#ffffff" stroke-width="1" paint-order="stroke fill">麺</text>')
    xml.append('    <ellipse cx="190" cy="331" rx="28" ry="6" fill="#18181b" stroke="#09090b" stroke-width="2"/>')
    xml.append('    <line x1="190" y1="337" x2="190" y2="380" stroke="#991b1b" stroke-width="4" stroke-linecap="round"/>')
    xml.append('    <circle cx="190" cy="341" r="4" fill="#fbbf24"/>')
    xml.append('  </g>')

    # RIGHT LANTERN (Amber - Tako-Hachi)
    xml.append('  <!-- Right Glowing Paper Lantern -->')
    xml.append('  <g id="right-lantern">')
    xml.append('    <circle cx="1010" cy="275" r="120" fill="url(#grad-lantern-glow-amber)" filter="url(#glow-lantern-amber)"/>')
    xml.append('    <line x1="1010" y1="80" x2="1010" y2="215" stroke="#182230" stroke-width="2.5"/>')
    xml.append('    <ellipse cx="1010" cy="217" rx="30" ry="7" fill="#18181b" stroke="#09090b" stroke-width="2"/>')
    xml.append('    <rect x="986" y="207" width="48" height="10" rx="3" fill="#27272a"/>')
    xml.append('    <path d="M 986 220 C 950 245 950 305 986 330 L 1034 330 C 1070 305 1070 245 1034 220 Z" fill="url(#grad-lantern-amber)" stroke="#92400e" stroke-width="2.5"/>')
    for ry in [240, 260, 280, 300, 315]:
        xml.append(f'    <ellipse cx="1010" cy="{ry}" rx="{48 - abs(ry-275)*0.38:.1f}" ry="6" fill="none" stroke="#92400e" stroke-width="1.8" opacity="0.75"/>')
    xml.append('    <text x="1010" y="266" font-family="Hiragino Sans, Meiryo, sans-serif" font-weight="900" font-size="28" fill="#18181b" text-anchor="middle" stroke="#ffffff" stroke-width="1" paint-order="stroke fill">蛸</text>')
    xml.append('    <text x="1010" y="300" font-family="Hiragino Sans, Meiryo, sans-serif" font-weight="900" font-size="28" fill="#18181b" text-anchor="middle" stroke="#ffffff" stroke-width="1" paint-order="stroke fill">八</text>')
    xml.append('    <ellipse cx="1010" cy="331" rx="28" ry="6" fill="#18181b" stroke="#09090b" stroke-width="2"/>')
    xml.append('    <line x1="1010" y1="337" x2="1010" y2="380" stroke="#b45309" stroke-width="4" stroke-linecap="round"/>')
    xml.append('    <circle cx="1010" cy="341" r="4" fill="#fbbf24"/>')
    xml.append('  </g>')

    # Center Warm Hanging Incandescent Bulb
    xml.append('  <circle cx="600" cy="180" r="160" fill="url(#grad-lantern-glow-amber)" opacity="0.45" filter="url(#glow-flame)"/>')
    xml.append('  <line x1="600" y1="80" x2="600" y2="175" stroke="#0f172a" stroke-width="2"/>')
    xml.append('  <rect x="595" y="172" width="10" height="8" fill="#334155"/>')
    xml.append('  <ellipse cx="600" cy="185" rx="7" ry="10" fill="#fef08a" opacity="0.95"/>')
    xml.append('  <circle cx="600" cy="185" r="4" fill="#ffffff"/>')

    xml.append('</g>')
    return "\n".join(xml)

# ---------------------------------------------------------------------------
# Octopus Chef Head, Face & Attire
# ---------------------------------------------------------------------------

def build_octopus_chef(tentacles_rendered):
    xml = ['<!-- THE HERO: OCTOPUS CHEF (TAKO-SAN) -->', '<g id="chef-tako">']

    # All tentacles rendered behind body, coat & bowl
    xml.append('  <!-- Action Tentacles -->')
    for tid in [1, 2, 4, 5, 3, 6, 7, 8]:
        xml.append(tentacles_rendered[tid])

    # Chef Torso & Happi Coat
    xml.append('  <!-- Chef Torso & Uniform -->')
    xml.append('  <g id="chef-body-outfit">')
    # Happi coat navy body
    xml.append('    <path d="M 520 460 C 475 520 470 610 495 655 L 705 655 C 730 610 725 520 680 460 Z" fill="#18233d" stroke="#0a0e1c" stroke-width="3"/>')
    # White collar lapels crossed right over left
    xml.append('    <polygon points="530,460 575,460 635,620 595,620" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>')
    xml.append('    <polygon points="670,460 625,460 565,620 605,620" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>')
    # White apron front
    xml.append('    <path d="M 535 540 L 665 540 L 675 655 L 525 655 Z" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>')
    # Embroidered red crest on apron
    xml.append('    <circle cx="600" cy="595" r="16" fill="none" stroke="#ef4444" stroke-width="2"/>')
    xml.append('    <text x="600" y="601" font-family="Hiragino Sans, Meiryo, sans-serif" font-weight="900" font-size="14" fill="#ef4444" text-anchor="middle">蛸</text>')
    xml.append('  </g>')

    # Chef Head Mantle (Center 600, 360)
    xml.append('  <!-- Head / Mantle -->')
    xml.append('  <g id="chef-head">')
    xml.append('    <ellipse cx="600" cy="385" rx="104" ry="114" fill="#4d050c" opacity="0.55"/>')
    # Bulbous organic mantle shape
    xml.append('    <path d="M 505 380 C 495 300 535 240 600 240 C 665 240 705 300 695 380 C 690 440 660 475 600 475 C 540 475 510 440 505 380 Z" fill="url(#grad-octo-head)" stroke="#6e0710" stroke-width="3"/>')
    xml.append('    <path d="M 555 270 C 580 255 620 255 645 270 C 620 262 580 262 555 270 Z" fill="#ffa89b" opacity="0.6"/>')

    # Rosy Blushing Cheeks
    xml.append('    <ellipse cx="530" cy="425" rx="18" ry="11" fill="#fb7185" opacity="0.75" filter="url(#steam-blur)"/>')
    xml.append('    <ellipse cx="670" cy="425" rx="18" ry="11" fill="#fb7185" opacity="0.75" filter="url(#steam-blur)"/>')
    xml.append('    <line x1="523" y1="422" x2="527" y2="428" stroke="#be123c" stroke-width="2" stroke-linecap="round"/>')
    xml.append('    <line x1="529" y1="421" x2="533" y2="427" stroke="#be123c" stroke-width="2" stroke-linecap="round"/>')
    xml.append('    <line x1="667" y1="422" x2="671" y2="428" stroke="#be123c" stroke-width="2" stroke-linecap="round"/>')
    xml.append('    <line x1="673" y1="421" x2="677" y2="427" stroke="#be123c" stroke-width="2" stroke-linecap="round"/>')

    # Big Expressive Anime Eyes
    xml.append('    <g id="left-eye">')
    xml.append('      <ellipse cx="555" cy="385" rx="21" ry="25" fill="#ffffff" stroke="#250d03" stroke-width="3"/>')
    xml.append('      <ellipse cx="557" cy="385" rx="15" ry="20" fill="url(#grad-iris)"/>')
    xml.append('      <circle cx="552" cy="376" r="6.5" fill="#ffffff"/>')
    xml.append('      <circle cx="563" cy="393" r="3.2" fill="#ffffff" opacity="0.85"/>')
    xml.append('      <path d="M 552 390 L 553 393 L 556 394 L 553 395 L 552 398 L 551 395 L 548 394 L 551 393 Z" fill="#ffedd5"/>')
    xml.append('      <path d="M 532 376 C 545 362 568 362 578 375" fill="none" stroke="#250d03" stroke-width="5" stroke-linecap="round"/>')
    xml.append('      <path d="M 535 358 C 550 346 570 353 580 361" fill="none" stroke="#5c060d" stroke-width="4.5" stroke-linecap="round"/>')
    xml.append('    </g>')

    xml.append('    <g id="right-eye">')
    xml.append('      <ellipse cx="645" cy="385" rx="21" ry="25" fill="#ffffff" stroke="#250d03" stroke-width="3"/>')
    xml.append('      <ellipse cx="643" cy="385" rx="15" ry="20" fill="url(#grad-iris)"/>')
    xml.append('      <circle cx="640" cy="376" r="6.5" fill="#ffffff"/>')
    xml.append('      <circle cx="649" cy="393" r="3.2" fill="#ffffff" opacity="0.85"/>')
    xml.append('      <path d="M 648 390 L 649 393 L 652 394 L 649 395 L 648 398 L 647 395 L 644 394 L 647 393 Z" fill="#ffedd5"/>')
    xml.append('      <path d="M 622 375 C 632 362 655 362 668 376" fill="none" stroke="#250d03" stroke-width="5" stroke-linecap="round"/>')
    xml.append('      <path d="M 620 361 C 630 353 650 346 665 358" fill="none" stroke="#5c060d" stroke-width="4.5" stroke-linecap="round"/>')
    xml.append('    </g>')

    # Exuberant Chef Smile
    xml.append('    <g id="chef-mouth">')
    xml.append('      <path d="M 576 430 Q 600 464 624 430 Q 600 422 576 430 Z" fill="#881337" stroke="#4c0519" stroke-width="2.5"/>')
    xml.append('      <path d="M 584 444 Q 600 436 616 444 Q 600 462 584 444 Z" fill="#fb7185"/>')
    xml.append('      <path d="M 572 427 Q 574 433 576 436" fill="none" stroke="#5c060d" stroke-width="2.5" stroke-linecap="round"/>')
    xml.append('      <path d="M 628 427 Q 626 433 624 436" fill="none" stroke="#5c060d" stroke-width="2.5" stroke-linecap="round"/>')
    xml.append('    </g>')

    # Twisted Nejiri-Hachimaki Chef Headband
    xml.append('    <!-- Nejiri-Hachimaki Twisted Rope -->')
    xml.append('    <g id="hachimaki">')
    hm_pts = [
        (506, 355), (524, 343), (544, 335), (566, 329), (590, 326),
        (614, 326), (638, 329), (660, 335), (680, 343), (698, 355)
    ]
    for i in range(len(hm_pts)-1):
        x1, y1 = hm_pts[i]
        x2, y2 = hm_pts[i+1]
        midx, midy = (x1+x2)*0.5, (y1+y2)*0.5
        col = "#f8fafc" if i % 2 == 0 else "#2563eb"
        ang = math.degrees(math.atan2(y2-y1, x2-x1))
        xml.append(f'      <ellipse cx="{midx}" cy="{midy}" rx="12" ry="9" transform="rotate({ang:.1f}, {midx}, {midy})" fill="{col}" stroke="#0f172a" stroke-width="2"/>')
    
    xml.append('      <g transform="translate(702, 354)">')
    xml.append('        <circle cx="0" cy="0" r="11" fill="#f8fafc" stroke="#0f172a" stroke-width="2.5"/>')
    xml.append('        <path d="M -7 -6 L 7 6" stroke="#2563eb" stroke-width="3.5"/>')
    xml.append('        <path d="M 5 -4 C 28 -20 40 -45 58 -38 C 46 -15 28 -4 9 6 Z" fill="#ffffff" stroke="#0f172a" stroke-width="2.5"/>')
    xml.append('        <path d="M 7 4 C 32 12 50 30 62 52 C 40 38 24 24 6 12 Z" fill="#2563eb" stroke="#0f172a" stroke-width="2.5"/>')
    xml.append('      </g>')
    xml.append('    </g>')

    xml.append('  </g>')
    xml.append('</g>')
    return "\n".join(xml)

# ---------------------------------------------------------------------------
# Chef Props, Culinary Equipment & Particle Effects
# ---------------------------------------------------------------------------

def build_props_and_actions():
    xml = ['<!-- CHEF PROPS, ACTIONS & PARTICLES -->', '<g id="props-and-actions">']

    # 1. TOP-LEFT: Tebo Noodle Strainer Basket & Flying Ramen Noodles
    xml.append('  <!-- Prop 1: Tebo Noodle Basket & Water Splash -->')
    xml.append('  <g id="prop-tebo" filter="url(#subtle-shadow)">')
    xml.append('    <path d="M 370 145 L 320 205" stroke="#78350f" stroke-width="10" stroke-linecap="round"/>')
    xml.append('    <path d="M 370 145 L 320 205" stroke="#f59e0b" stroke-width="3" stroke-linecap="round"/>')
    xml.append('    <ellipse cx="305" cy="225" rx="26" ry="13" fill="#64748b" stroke="#334155" stroke-width="2.5" transform="rotate(-25, 305, 225)"/>')
    xml.append('    <g transform="translate(305, 225) rotate(-25)">')
    xml.append('      <path d="M -23 0 L -17 48 C -16 58 16 58 17 48 L 23 0 Z" fill="#94a3b8" stroke="#475569" stroke-width="2" opacity="0.85"/>')
    xml.append('      <line x1="-19" y1="16" x2="19" y2="16" stroke="#475569" stroke-width="1.2"/>')
    xml.append('      <line x1="-16" y1="32" x2="16" y2="32" stroke="#475569" stroke-width="1.2"/>')
    xml.append('      <line x1="-11" y1="45" x2="11" y2="45" stroke="#475569" stroke-width="1.2"/>')
    xml.append('    </g>')
    noodle_curves = [
        "M 305 215 C 290 160 330 120 310 70",
        "M 315 220 C 335 155 285 110 335 60",
        "M 295 220 C 270 170 315 130 280 85",
        "M 310 225 C 345 175 355 130 365 90",
        "M 320 230 C 365 180 325 140 345 100",
        "M 290 225 C 260 180 295 140 270 110",
    ]
    for nc in noodle_curves:
        xml.append(f'    <path d="{nc}" fill="none" stroke="#f59e0b" stroke-width="3.8" stroke-linecap="round"/>')
        xml.append(f'    <path d="{nc}" fill="none" stroke="#fef08a" stroke-width="1.8" stroke-linecap="round"/>')
    drops = [(280, 100, 3.8), (325, 80, 4.2), (345, 115, 3.2), (265, 130, 3.8), (365, 70, 3.0), (300, 50, 3.5)]
    for dx, dy, dr in drops:
        xml.append(f'    <circle cx="{dx}" cy="{dy}" r="{dr}" fill="#e0f2fe" opacity="0.95"/>')
        xml.append(f'    <circle cx="{dx-dr*0.3:.1f}" cy="{dy-dr*0.3:.1f}" r="{dr*0.35:.1f}" fill="#ffffff"/>')
    xml.append('  </g>')

    # 2. MID-LEFT: Wooden Broth Ladle & Cascading Tonkotsu Broth
    xml.append('  <!-- Prop 2: Wooden Broth Ladle & Soup Stream -->')
    xml.append('  <g id="prop-ladle" filter="url(#subtle-shadow)">')
    xml.append('    <path d="M 215 420 L 255 455" stroke="#78350f" stroke-width="8.5" stroke-linecap="round"/>')
    xml.append('    <ellipse cx="260" cy="460" rx="17" ry="13" fill="#92400e" stroke="#451a03" stroke-width="2.5" transform="rotate(30, 260, 460)"/>')
    xml.append('    <ellipse cx="260" cy="458" rx="13" ry="9" fill="url(#grad-broth)" transform="rotate(30, 260, 458)"/>')
    xml.append('    <path d="M 268 463 Q 275 490 270 525" fill="none" stroke="#d97706" stroke-width="5.5" stroke-linecap="round"/>')
    xml.append('    <path d="M 268 463 Q 275 490 270 525" fill="none" stroke="#fef08a" stroke-width="2.0" stroke-linecap="round"/>')
    xml.append('  </g>')

    # 3. LOWER-LEFT: Nakiri Cleaver, Board & Sliced Negi
    xml.append('  <!-- Prop 3: Nakiri Knife & Scallion Prep -->')
    xml.append('  <g id="prop-cutting-board">')
    xml.append('    <ellipse cx="320" cy="655" rx="68" ry="25" fill="#d97706" stroke="#78350f" stroke-width="3"/>')
    xml.append('    <ellipse cx="320" cy="653" rx="60" ry="21" fill="#fde68a" stroke="#b45309" stroke-width="1.5" opacity="0.9"/>')
    xml.append('    <path d="M 270 653 Q 320 647 370 653" stroke="#16a34a" stroke-width="8" stroke-linecap="round"/>')
    xml.append('    <path d="M 265 656 Q 315 650 365 656" stroke="#22c55e" stroke-width="7" stroke-linecap="round"/>')
    # Nakiri Cleaver
    xml.append('    <g transform="translate(340, 640) rotate(-22)">')
    xml.append('      <rect x="-10" y="28" width="14" height="35" rx="3" fill="#3e1a05" stroke="#1c0a02" stroke-width="2"/>')
    xml.append('      <rect x="-9" y="22" width="12" height="6" fill="#94a3b8"/>')
    xml.append('      <polygon points="-8,-25 18,-25 18,22 -8,22" fill="#cbd5e1" stroke="#475569" stroke-width="2"/>')
    xml.append('      <line x1="17" y1="-25" x2="17" y2="22" stroke="#ffffff" stroke-width="2"/>')
    xml.append('    </g>')
    for ring_x, ring_y in [(350, 653), (360, 649), (368, 657), (376, 651), (384, 655)]:
        xml.append(f'    <ellipse cx="{ring_x}" cy="{ring_y}" rx="4.8" ry="3.6" fill="#86efac" stroke="#15803d" stroke-width="1.6"/>')
        xml.append(f'    <ellipse cx="{ring_x}" cy="{ring_y}" rx="2.2" ry="1.6" fill="#f0fdf4"/>')
    xml.append('  </g>')

    # 4. TOP-RIGHT: Culinary Blowtorch & Flaming Torch Jet
    xml.append('  <!-- Prop 4: Culinary Blowtorch & Flaming Torch Jet -->')
    xml.append('  <g id="prop-blowtorch" filter="url(#subtle-shadow)">')
    xml.append('    <g transform="translate(980, 260) rotate(135)">')
    xml.append('      <rect x="-16" y="-12" width="32" height="68" rx="7" fill="#0284c7" stroke="#0369a1" stroke-width="2.5"/>')
    xml.append('      <rect x="-13" y="6" width="26" height="22" fill="#ffffff" opacity="0.85"/>')
    xml.append('      <text x="0" y="21" font-family="sans-serif" font-weight="bold" font-size="9" fill="#0284c7" text-anchor="middle">GAS</text>')
    xml.append('      <rect x="-8" y="-24" width="16" height="12" fill="#f59e0b" stroke="#78350f" stroke-width="1.5"/>')
    xml.append('      <path d="M -6 -24 L -18 -34 L -12 -40 L 0 -30 Z" fill="#94a3b8" stroke="#475569" stroke-width="1.5"/>')
    xml.append('      <polygon points="-18,-34 -28,-42 -24,-47 -14,-39" fill="#64748b"/>')
    xml.append('    </g>')
    # Fiery Torch Jet
    xml.append('    <g transform="translate(930, 305) rotate(135)" filter="url(#glow-flame)">')
    xml.append('      <path d="M 0 0 C -16 28 -22 65 0 102 C 22 65 16 28 0 0 Z" fill="url(#grad-flame-outer)" opacity="0.88"/>')
    xml.append('      <path d="M 0 5 C -8 22 -9 48 0 70 C 9 48 8 22 0 5 Z" fill="url(#grad-flame-core)"/>')
    xml.append('      <ellipse cx="0" cy="20" rx="3.5" ry="13" fill="#ffffff"/>')
    xml.append('    </g>')
    # Glowing sizzle sparks
    sparks = [(890, 345), (875, 360), (905, 365), (860, 350), (885, 380)]
    for sx, sy in sparks:
        xml.append(f'    <circle cx="{sx}" cy="{sy}" r="2.2" fill="#fef08a" filter="url(#glow-flame)"/>')
    # Wire grill rack with sizzling chashu on the prep counter
    xml.append('    <g id="sear-station" transform="translate(885, 395)">')
    xml.append('      <rect x="-38" y="0" width="76" height="16" rx="3" fill="#64748b" stroke="#334155" stroke-width="2"/>')
    xml.append('      <ellipse cx="0" cy="0" rx="28" ry="15" fill="#b45309" stroke="#78350f" stroke-width="2"/>')
    xml.append('      <ellipse cx="0" cy="0" rx="20" ry="10" fill="#fde68a" stroke="#d97706" stroke-width="1.5"/>')
    xml.append('      <line x1="-14" y1="-4" x2="14" y2="4" stroke="#451a03" stroke-width="3" stroke-linecap="round"/>')
    xml.append('      <line x1="-9" y1="2" x2="16" y2="-3" stroke="#451a03" stroke-width="2.5" stroke-linecap="round"/>')
    xml.append('    </g>')
    xml.append('  </g>')

    # 5. MID-RIGHT: Saibashi Chopsticks Plating Ramen Egg
    xml.append('  <!-- Prop 5: Saibashi Chopsticks Plating Ramen Egg -->')
    xml.append('  <g id="prop-chopsticks" filter="url(#subtle-shadow)">')
    xml.append('    <path d="M 830 405 L 740 485" stroke="#ca8a04" stroke-width="5" stroke-linecap="round"/>')
    xml.append('    <path d="M 834 409 L 744 491" stroke="#ca8a04" stroke-width="5" stroke-linecap="round"/>')
    xml.append('    <path d="M 832 405 Q 836 400 842 403" fill="none" stroke="#dc2626" stroke-width="3" stroke-linecap="round"/>')
    xml.append('    <g transform="translate(730, 497) rotate(-20)">')
    xml.append('      <ellipse cx="0" cy="0" rx="16" ry="12" fill="#78350f"/>')
    xml.append('      <ellipse cx="0" cy="0" rx="14" ry="10" fill="#fef08a"/>')
    xml.append('      <ellipse cx="-2" cy="0" rx="8" ry="6" fill="url(#grad-egg-yolk)"/>')
    xml.append('      <ellipse cx="-4" cy="-2" rx="2.5" ry="1.8" fill="#ffffff" opacity="0.9"/>')
    xml.append('    </g>')
    xml.append('  </g>')

    # 6. LOWER-RIGHT: Wooden Spice Shaker & Sesame Shower
    xml.append('  <!-- Prop 6: Spice Shaker & Sesame Sprinkle -->')
    xml.append('  <g id="prop-shaker" filter="url(#subtle-shadow)">')
    xml.append('    <g transform="translate(900, 495) rotate(-135)">')
    xml.append('      <rect x="-14" y="-30" width="28" height="50" rx="4" fill="#92400e" stroke="#451a03" stroke-width="2.5"/>')
    xml.append('      <rect x="-16" y="-35" width="32" height="7" rx="2" fill="#78350f" stroke="#451a03" stroke-width="1.5"/>')
    xml.append('      <circle cx="0" cy="-10" r="8" fill="#b91c1c"/>')
    xml.append('      <text x="0" y="-6" font-family="Hiragino Sans, sans-serif" font-weight="bold" font-size="8" fill="#ffffff" text-anchor="middle">七味</text>')
    xml.append('      <polygon points="-4,20 4,20 0,30" fill="#ca8a04"/>')
    xml.append('    </g>')
    seeds = [
        (840, 545, "#fde68a"), (830, 560, "#dc2626"), (850, 565, "#fde68a"),
        (825, 580, "#fde68a"), (845, 590, "#dc2626"), (835, 605, "#fde68a"),
        (815, 585, "#fef08a"), (820, 615, "#dc2626"), (805, 610, "#fde68a")
    ]
    for seed_x, seed_y, seed_col in seeds:
        xml.append(f'    <ellipse cx="{seed_x}" cy="{seed_y}" rx="2.6" ry="1.6" fill="{seed_col}" transform="rotate(35, {seed_x}, {seed_y})"/>')
    xml.append('  </g>')

    xml.append('</g>')
    return "\n".join(xml)

# ---------------------------------------------------------------------------
# The Grand Ramen Bowl Centerpiece
# ---------------------------------------------------------------------------

def build_grand_ramen_bowl():
    xml = ['<!-- THE SHOWPIECE: ULTIMATE RAMEN BOWL -->', '<g id="grand-ramen-bowl" filter="url(#bowl-shadow)">']
    
    cx = 600
    cy = 715
    
    # 1. Ceramic Bowl Body
    bowl_body_d = f"""
      M {cx-180} {cy-25}
      C {cx-185} {cy+50} {cx-115} {cy+105} {cx-80} {cy+108}
      L {cx+80} {cy+108}
      C {cx+115} {cy+105} {cx+185} {cy+50} {cx+180} {cy-25}
      Z
    """
    xml.append(f'  <path d="{bowl_body_d}" fill="url(#grad-bowl-outer)" stroke="#090d14" stroke-width="3.5"/>')
    
    # Ceramic Tenmoku Glaze Specular Highlight
    xml.append(f'  <path d="M {cx-150} {cy+10} C {cx-140} {cy+60} {cx-100} {cy+95} {cx-60} {cy+104}" fill="none" stroke="#475569" stroke-width="6" opacity="0.35" stroke-linecap="round"/>')

    # Bowl Foot Ring
    xml.append(f'  <rect x="{cx-80}" y="{cy+106}" width="160" height="16" rx="4" fill="#0f172a" stroke="#020617" stroke-width="2.5"/>')
    xml.append(f'  <line x1="{cx-75}" y1="{cy+118}" x2="{cx+75}" y2="{cy+118}" stroke="#334155" stroke-width="2"/>')

    # Traditional Gold Raimon Spiral Pattern along rim
    xml.append('  <!-- Raimon Gold Rim Pattern -->')
    for rx in range(cx-154, cx+155, 28):
        xml.append(f'  <path d="M {rx-8} {cy-10} L {rx+8} {cy-10} L {rx+8} {cy+2} L {rx-3} {cy+2} L {rx-3} {cy-4} L {rx+3} {cy-4}" fill="none" stroke="#f59e0b" stroke-width="1.8"/>')

    # Bowl Inner Rim Ellipses
    xml.append(f'  <ellipse cx="{cx}" cy="{cy-25}" rx="180" ry="48" fill="#1e293b" stroke="#f59e0b" stroke-width="3"/>')
    xml.append(f'  <ellipse cx="{cx}" cy="{cy-25}" rx="174" ry="45" fill="#0a0d14"/>')

    # 2. Rich Tonkotsu Broth Surface
    xml.append(f'  <ellipse cx="{cx}" cy="{cy-22}" rx="170" ry="42" fill="url(#grad-broth)"/>')

    # Glistening Circular Oil Pearls (Chiyu)
    oil_pearls = [
        (cx-120, cy-32, 6.5), (cx-95, cy-40, 8.5), (cx-65, cy-46, 5.5), (cx-35, cy-38, 7.5),
        (cx+10, cy-42, 6.5), (cx+55, cy-46, 9.5), (cx+95, cy-38, 7.5), (cx+125, cy-30, 8.5),
        (cx-130, cy-18, 5.5), (cx-75, cy-15, 6.5), (cx+65, cy-16, 7.5), (cx+120, cy-14, 6.5),
        (cx-45, cy-10, 8.5), (cx+35, cy-10, 6.5), (cx-85, cy-25, 10.5), (cx+85, cy-25, 9.5)
    ]
    for ox, oy, orad in oil_pearls:
        xml.append(f'  <circle cx="{ox}" cy="{oy}" r="{orad}" fill="#fef08a" opacity="0.38"/>')
        xml.append(f'  <circle cx="{ox-orad*0.3:.1f}" cy="{oy-orad*0.3:.1f}" r="{orad*0.3:.1f}" fill="#ffffff" opacity="0.85"/>')

    # Wavy Ramen Noodles submerged in broth
    noodle_strands = [
        f"M {cx-140} {cy-25} Q {cx-95} {cy-10} {cx-50} {cy-25} T {cx-10} {cy-22} T {cx+45} {cy-25}",
        f"M {cx-115} {cy-15} Q {cx-75} {cy-32} {cx-30} {cy-15} T {cx+25} {cy-18} T {cx+80} {cy-15}",
        f"M {cx-85} {cy-35} Q {cx-45} {cy-20} {cx} {cy-35} T {cx+55} {cy-32} T {cx+110} {cy-35}",
        f"M {cx-65} {cy-8} Q {cx-25} {cy-25} {cx+20} {cy-8} T {cx+75} {cy-10} T {cx+130} {cy-8}",
    ]
    for ns in noodle_strands:
        xml.append(f'  <path d="{ns}" fill="none" stroke="#f59e0b" stroke-width="4.2" stroke-linecap="round"/>')
        xml.append(f'  <path d="{ns}" fill="none" stroke="#fef08a" stroke-width="1.8" stroke-linecap="round"/>')

    # 3. Sumptuous Toppings
    # TOPPING A: Crisp Nori Seaweed (Back Left)
    xml.append('  <!-- Nori Seaweed Sheets -->')
    xml.append(f'  <g transform="translate({cx-95}, {cy-88}) rotate(-18)">')
    xml.append('    <rect x="-25" y="0" width="50" height="78" rx="3" fill="#142419" stroke="#0a140d" stroke-width="2"/>')
    xml.append('    <rect x="-23" y="2" width="46" height="74" fill="#1b2e21" opacity="0.7"/>')
    xml.append('  </g>')
    xml.append(f'  <g transform="translate({cx-65}, {cy-93}) rotate(-8)">')
    xml.append('    <rect x="-25" y="0" width="50" height="84" rx="3" fill="#142419" stroke="#0a140d" stroke-width="2"/>')
    xml.append('    <rect x="-23" y="2" width="46" height="80" fill="#1b2e21" opacity="0.7"/>')
    xml.append('  </g>')

    # TOPPING B: Two Slices of Rolled Chashu Pork (Right)
    xml.append('  <!-- Rolled Chashu Pork Slices -->')
    xml.append(f'  <g transform="translate({cx+80}, {cy-35}) rotate(15)">')
    xml.append('    <ellipse cx="0" cy="0" rx="40" ry="25" fill="#78350f" stroke="#451a03" stroke-width="2.5"/>')
    xml.append('    <ellipse cx="0" cy="0" rx="36" ry="21" fill="url(#grad-chashu-meat)"/>')
    xml.append('    <path d="M -24 0 C -24 -13 24 -13 24 0 C 24 11 -16 11 -16 0 C -16 -6 13 -6 13 0" fill="none" stroke="#fef3c7" stroke-width="4.8" stroke-linecap="round"/>')
    xml.append('    <line x1="-16" y1="-8" x2="16" y2="8" stroke="#451a03" stroke-width="3" stroke-linecap="round"/>')
    xml.append('  </g>')

    xml.append(f'  <g transform="translate({cx+65}, {cy-14}) rotate(-5)">')
    xml.append('    <ellipse cx="0" cy="0" rx="42" ry="27" fill="#78350f" stroke="#451a03" stroke-width="2.5"/>')
    xml.append('    <ellipse cx="0" cy="0" rx="38" ry="23" fill="#d97706"/>')
    xml.append('    <path d="M -26 0 C -26 -15 26 -15 26 0 C 26 13 -17 13 -17 0 C -17 -7 15 -7 15 0" fill="none" stroke="#fef3c7" stroke-width="5.2" stroke-linecap="round"/>')
    xml.append('    <line x1="-19" y1="-5" x2="19" y2="5" stroke="#451a03" stroke-width="3.5" stroke-linecap="round"/>')
    xml.append('    <line x1="-13" y1="4" x2="13" y2="-4" stroke="#451a03" stroke-width="2.5" stroke-linecap="round"/>')
    xml.append('  </g>')

    # TOPPING C: Ajitsuke Tamago (Seasoned Egg Half - Left)
    xml.append('  <!-- Halved Seasoned Ramen Egg -->')
    xml.append(f'  <g transform="translate({cx-68}, {cy-15}) rotate(-12)">')
    xml.append('    <ellipse cx="0" cy="0" rx="34" ry="25" fill="#78350f" stroke="#451a03" stroke-width="2"/>')
    xml.append('    <ellipse cx="0" cy="0" rx="30" ry="22" fill="#fef08a"/>')
    xml.append('    <ellipse cx="-4" cy="0" rx="20" ry="15" fill="url(#grad-egg-yolk)"/>')
    xml.append('    <ellipse cx="-8" cy="-4" rx="5.5" ry="3.8" fill="#ffffff" opacity="0.9"/>')
    xml.append('  </g>')

    # TOPPING D: Menma Bamboo Shoots (Upper Center)
    xml.append('  <!-- Menma Bamboo Shoots -->')
    menma_bars = [
        (cx-20, cy-50, 15), (cx-10, cy-54, 25), (cx+5, cy-52, 10), (cx+20, cy-54, -5)
    ]
    for mx, my, mang in menma_bars:
        xml.append(f'  <rect x="{mx-15}" y="{my-4}" width="30" height="9" rx="2" fill="#ca8a04" stroke="#854d0e" stroke-width="1.5" transform="rotate({mang}, {mx}, {my})"/>')

    # TOPPING E: Narutomaki Fish Cake
    xml.append('  <!-- Narutomaki Fish Cake -->')
    xml.append(f'  <g transform="translate({cx-15}, {cy-25})">')
    xml.append('    <path d="M 0 -19 C 5 -19 6 -16 11 -16 C 16 -16 18 -12 19 -8 C 21 -2 19 2 19 8 C 18 12 15 16 11 16 C 6 16 5 19 0 19 C -5 19 -6 16 -11 16 C -15 16 -18 12 -19 8 C -21 2 -19 -2 -19 -8 C -18 -12 -16 -16 -11 -16 C -6 -16 -5 -19 0 -19 Z" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>')
    xml.append('    <path d="M 0 -11 C 7 -11 11 -7 11 0 C 11 7 6 11 0 11 C -6 11 -9 7 -9 1 C -9 -4 -5 -7 0 -7 C 3 -7 5 -4 5 0" fill="none" stroke="#f43f5e" stroke-width="3.2" stroke-linecap="round"/>')
    xml.append('  </g>')

    # TOPPING F: Fresh Sliced Scallions (Negi)
    xml.append('  <!-- Fresh Negi Scallion Pile -->')
    negi_mound = [
        (cx, cy-22), (cx-8, cy-26), (cx+12, cy-24), (cx+4, cy-28), (cx-14, cy-20),
        (cx+8, cy-18), (cx-2, cy-16), (cx+16, cy-20), (cx-6, cy-32), (cx+6, cy-32),
        (cx-12, cy-28), (cx+2, cy-24)
    ]
    for nx, ny in negi_mound:
        xml.append(f'  <ellipse cx="{nx}" cy="{ny}" rx="5.8" ry="4.2" fill="#86efac" stroke="#15803d" stroke-width="1.6"/>')
        xml.append(f'  <ellipse cx="{nx}" cy="{ny}" rx="2.6" ry="1.9" fill="#f0fdf4"/>')

    # Toasted Sesame Seeds
    for sx, sy in [(cx-35, cy-18), (cx-28, cy-32), (cx+30, cy-28), (cx+48, cy-18), (cx-2, cy-8), (cx+25, cy-8)]:
        xml.append(f'  <ellipse cx="{sx}" cy="{sy}" rx="2.2" ry="1.3" fill="#fef08a" stroke="#d97706" stroke-width="0.8"/>')

    # Fragrant Rising Steam
    xml.append('  <!-- Fragrant Bowl Steam -->')
    xml.append('  <g id="bowl-steam" opacity="0.65" filter="url(#steam-blur)">')
    xml.append(f'    <path d="M {cx-40} {cy-40} C {cx-75} {cy-120} {cx-25} {cy-180} {cx-65} {cy-250}" fill="none" stroke="#ffffff" stroke-width="16" stroke-linecap="round"/>')
    xml.append(f'    <path d="M {cx+35} {cy-40} C {cx+70} {cy-110} {cx+5} {cy-170} {cx+45} {cy-240}" fill="none" stroke="#e0f2fe" stroke-width="18" stroke-linecap="round"/>')
    xml.append(f'    <path d="M {cx} {cy-45} C {cx-25} {cy-95} {cx+25} {cy-150} {cx-12} {cy-210}" fill="none" stroke="#ffffff" stroke-width="12" stroke-linecap="round"/>')
    xml.append('  </g>')

    xml.append('</g>')
    return "\n".join(xml)

# ---------------------------------------------------------------------------
# Countertop Accessories
# ---------------------------------------------------------------------------

def build_counter_props():
    xml = ['<!-- COUNTER FOREGROUND ACCESSORIES -->', '<g id="counter-props">']

    # Right: Chopstick Rest & Hashi
    xml.append('  <g id="chopsticks" transform="translate(870, 660)" filter="url(#subtle-shadow)">')
    xml.append('    <ellipse cx="0" cy="0" rx="15" ry="7" fill="#3b82f6" stroke="#1d4ed8" stroke-width="2"/>')
    xml.append('    <path d="M -65 5 L 90 -5" stroke="#78350f" stroke-width="5" stroke-linecap="round"/>')
    xml.append('    <path d="M -65 11 L 90 1" stroke="#b45309" stroke-width="5" stroke-linecap="round"/>')
    xml.append('    <line x1="-65" y1="5" x2="-20" y2="2" stroke="#d97706" stroke-width="3.2"/>')
    xml.append('    <line x1="-65" y1="11" x2="-20" y2="8" stroke="#d97706" stroke-width="3.2"/>')
    xml.append('  </g>')

    # Left: Chili Oil Dish
    xml.append('  <g id="condiment-saucer" transform="translate(340, 700)" filter="url(#subtle-shadow)">')
    xml.append('    <ellipse cx="0" cy="0" rx="26" ry="11" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>')
    xml.append('    <ellipse cx="0" cy="0" rx="21" ry="8" fill="#b91c1c"/>')
    xml.append('    <circle cx="-5" cy="-2" r="3.2" fill="#f87171" opacity="0.8"/>')
    xml.append('    <circle cx="5" cy="1" r="2.8" fill="#facc15" opacity="0.9"/>')
    xml.append('  </g>')

    # Bottom Ambient Vignette
    xml.append('  <rect x="0" y="860" width="1200" height="40" fill="#000000" opacity="0.45"/>')

    xml.append('</g>')
    return "\n".join(xml)

# ---------------------------------------------------------------------------
# Master Artwork Generation
# ---------------------------------------------------------------------------

def generate_complete_artwork():
    print("Generating 8 Dynamic Tentacle Geometries...")
    
    # 1. Tentacle 1 (Top-Left: Noodle Toss / Tebo Strainer)
    t1_segments = [
        ((570, 390), (480, 360), (390, 310), (330, 250)),
        ((330, 250), (280, 190), (290, 130), (340, 100)),
        ((340, 100), (370, 85), (410, 110), (385, 155))
    ]
    t1_data = generate_tentacle(t1_segments, w_start=44, w_end=11, sucker_side=1, num_suckers=11)

    # 2. Tentacle 2 (Mid-Left: Broth Ladle)
    t2_segments = [
        ((570, 480), (480, 470), (380, 450), (300, 440)),
        ((300, 440), (220, 430), (195, 395), (225, 430))
    ]
    t2_data = generate_tentacle(t2_segments, w_start=42, w_end=12, sucker_side=-1, num_suckers=9)

    # 3. Tentacle 3 (Lower-Left: Knife & Scallions)
    t3_segments = [
        ((580, 560), (490, 580), (410, 600), (360, 625)),
        ((360, 625), (300, 650), (300, 695), (340, 675))
    ]
    t3_data = generate_tentacle(t3_segments, w_start=40, w_end=12, sucker_side=1, num_suckers=8)

    # 4. Tentacle 4 (Top-Right: Blowtorch)
    t4_segments = [
        ((630, 390), (720, 360), (830, 310), (890, 250)),
        ((890, 250), (940, 190), (990, 210), (980, 260))
    ]
    t4_data = generate_tentacle(t4_segments, w_start=44, w_end=11, sucker_side=-1, num_suckers=11)

    # 5. Tentacle 5 (Mid-Right: Chopsticks)
    t5_segments = [
        ((630, 480), (720, 470), (820, 450), (880, 410)),
        ((880, 410), (930, 370), (880, 360), (830, 390))
    ]
    t5_data = generate_tentacle(t5_segments, w_start=42, w_end=12, sucker_side=1, num_suckers=9)

    # 6. Tentacle 6 (Lower-Right: Spice Shaker)
    t6_segments = [
        ((620, 560), (710, 580), (810, 580), (870, 550)),
        ((870, 550), (920, 530), (930, 485), (890, 495))
    ]
    t6_data = generate_tentacle(t6_segments, w_start=40, w_end=12, sucker_side=-1, num_suckers=8)

    # 7. Tentacle 7 (Foreground Left: Framing Bowl on outside)
    # Starts under apron at (570, 580), curves cleanly outward to the left of the bowl
    t7_segments = [
        ((570, 580), (480, 610), (390, 650), (350, 710)),
        ((350, 710), (330, 770), (380, 830), (440, 810))
    ]
    t7_data = generate_tentacle(t7_segments, w_start=42, w_end=12, sucker_side=1, num_suckers=10)

    # 8. Tentacle 8 (Foreground Right: Framing Bowl on outside)
    # Starts under apron at (630, 580), curves cleanly outward to the right of the bowl
    t8_segments = [
        ((630, 580), (720, 610), (810, 650), (850, 710)),
        ((850, 710), (870, 770), (820, 830), (760, 810))
    ]
    t8_data = generate_tentacle(t8_segments, w_start=42, w_end=12, sucker_side=-1, num_suckers=10)

    tentacles_rendered = {
        1: render_tentacle_svg(t1_data, 1),
        2: render_tentacle_svg(t2_data, 2),
        3: render_tentacle_svg(t3_data, 3),
        4: render_tentacle_svg(t4_data, 4),
        5: render_tentacle_svg(t5_data, 5),
        6: render_tentacle_svg(t6_data, 6),
        7: render_tentacle_svg(t7_data, 7),
        8: render_tentacle_svg(t8_data, 8),
    }

    print("Assembling SVG layers...")
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">',
        build_defs(),
        build_background(),
        build_counter(),
        build_yatai_roof_and_noren(),
        build_octopus_chef(tentacles_rendered),
        build_props_and_actions(),
        build_grand_ramen_bowl(),
        build_counter_props(),
        '</svg>'
    ]
    
    return "\n".join(svg_parts)

def main():
    os.makedirs("./output", exist_ok=True)
    svg_path = "./output/octopus_ramen_chef.svg"
    png_path = "./output/octopus_ramen_chef.png"

    print("Rendering updated masterpiece...")
    svg_content = generate_complete_artwork()

    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Saved SVG to {svg_path} ({len(svg_content):,} bytes)")

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless",
        f"--screenshot={png_path}",
        "--window-size=1200,900",
        "--default-background-color=000000",
        f"file://{os.path.abspath(svg_path)}"
    ]
    print("Executing Chrome headless screenshot...")
    subprocess.run(cmd, capture_output=True, text=True)
    
    if os.path.exists(png_path):
        size = os.path.getsize(png_path)
        print(f"Generated {png_path} ({size:,} bytes)")
    else:
        print("Chrome render failed, falling back to qlmanage...")
        subprocess.run(f"qlmanage -t -s 1200 -o ./output {svg_path}", shell=True)
        if os.path.exists("./output/octopus_ramen_chef.svg.png"):
            os.rename("./output/octopus_ramen_chef.svg.png", png_path)

if __name__ == "__main__":
    main()
