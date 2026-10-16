import math
import subprocess
import os
import shutil

# --- Brand Configuration & Palette ---
# Neutral Tones Palette:
# Obsidian Dark: #121110
# Graphite Mid-Dark: #1E1C1A
# Charcoal Shadow: #2C2825
# Smoked Umber / Driftwood: #554D45
# Warm Taupe: #7D7366
# Mineral Sand: #A39788
# Raw Oat / Linen: #CEBFAC
# Warm Alabaster / Chalk: #FAF7F2
# Clay / Terracotta Pearl Accent: #C49A74

def generate_trefoil_quads(
    cx=400, cy=320, scale=95.0, ribbon_w=42.0,
    rot_x_deg=0.0, rot_z_deg=0.0, phase=0.0,
    is_dark=True, num_segments=480
):
    rot_x = math.radians(rot_x_deg)
    rot_z = math.radians(rot_z_deg)
    
    pts = []
    for i in range(num_segments):
        t = (2.0 * math.pi * i) / num_segments + phase
        x = math.sin(t) + 2.0 * math.sin(2.0 * t)
        y = math.cos(t) - 2.0 * math.cos(2.0 * t)
        z = -math.sin(3.0 * t)
        
        # Rot z
        x1 = x * math.cos(rot_z) - y * math.sin(rot_z)
        y1 = x * math.sin(rot_z) + y * math.cos(rot_z)
        z1 = z
        
        # Rot x
        x2 = x1
        y2 = y1 * math.cos(rot_x) - z1 * math.sin(rot_x)
        z2 = y1 * math.sin(rot_x) + z1 * math.cos(rot_x)
        
        pts.append({
            'px': cx + x2 * scale,
            'py': cy + y2 * scale,
            'pz': z2,
            't': t,
            'idx': i
        })

    for i in range(num_segments):
        c = pts[i]
        n = pts[(i + 1) % num_segments]
        dx, dy = n['px'] - c['px'], n['py'] - c['py']
        L = math.hypot(dx, dy) or 1e-5
        nx, ny = -dy / L, dx / L
        # Subtle organic swell at the outer crests, sleek at intersections
        w = ribbon_w * (1.0 + 0.12 * math.cos(3.0 * c['t']))
        c['pl'] = (c['px'] + nx * w, c['py'] + ny * w)
        c['pr'] = (c['px'] - nx * w, c['py'] - ny * w)
        c['width'] = w

    # Analytical Ambient Occlusion
    for i in range(num_segments):
        c = pts[i]
        ao_factor = 1.0
        for j in range(num_segments):
            idx_diff = abs(i - j)
            idx_diff = min(idx_diff, num_segments - idx_diff)
            if idx_diff < 42:
                continue
            other = pts[j]
            z_diff = other['pz'] - c['pz']
            if z_diff > 0.55:
                dist_2d = math.hypot(other['px'] - c['px'], other['py'] - c['py'])
                thresh = (c['width'] + other['width']) * 0.78
                if dist_2d < thresh:
                    d_norm = dist_2d / thresh
                    shadow = (1.0 - d_norm * d_norm) * 0.48 * min(1.0, z_diff / 1.4)
                    ao_factor = min(ao_factor, 1.0 - shadow)
        c['ao'] = ao_factor

    quads = []
    for i in range(num_segments):
        c = pts[i]
        n = pts[(i + 1) % num_segments]
        avg_z = (c['pz'] + n['pz']) / 2.0
        avg_ao = (c['ao'] + n['ao']) / 2.0
        zn = max(0.0, min(1.0, (avg_z + 2.0) / 4.0)) # normalized z [0, 1]
        
        if is_dark:
            # Dark mode: Front strands catch warm oat/alabaster sheen (#DFD5C6),
            # Back strands sink into smoked warm charcoal (#34302C)
            base_r = 50 + zn * 175
            base_g = 46 + zn * 165
            base_b = 42 + zn * 150
            r = int(base_r * avg_ao)
            g = int(base_g * avg_ao)
            b = int(base_b * avg_ao)
        else:
            # Light mode: Front strands are rich warm graphite (#25221F),
            # Back strands are warm taupe/driftwood (#988D7E)
            base_r = 152 - zn * 114
            base_g = 141 - zn * 106
            base_b = 129 - zn * 98
            r = int(base_r * avg_ao)
            g = int(base_g * avg_ao)
            b = int(base_b * avg_ao)
            
        col = f"#{r:02x}{g:02x}{b:02x}"
        quads.append({
            'z': avg_z,
            'pts': [c['pl'], n['pl'], n['pr'], c['pr']],
            'col': col
        })

    quads.sort(key=lambda q: q['z'])
    return quads

def quads_to_svg_paths(quads):
    return [
        f'<path d="M {q["pts"][0][0]:.2f} {q["pts"][0][1]:.2f} L {q["pts"][1][0]:.2f} {q["pts"][1][1]:.2f} L {q["pts"][2][0]:.2f} {q["pts"][2][1]:.2f} L {q["pts"][3][0]:.2f} {q["pts"][3][1]:.2f} Z" fill="{q["col"]}" stroke="{q["col"]}" stroke-width="0.75" />'
        for q in quads
    ]

print("Trefoil generator ready")
