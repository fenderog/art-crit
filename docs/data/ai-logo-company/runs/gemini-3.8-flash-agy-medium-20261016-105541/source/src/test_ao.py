import math
import subprocess

def test_ao_shading():
    scale = 92.0
    cx, cy = 400, 320
    num_segments = 480
    rot_x = 0
    rot_z = 0
    
    pts = []
    for i in range(num_segments):
        t = (2 * math.pi * i) / num_segments
        x = math.sin(t) + 2.0 * math.sin(2.0 * t)
        y = math.cos(t) - 2.0 * math.cos(2.0 * t)
        z = -math.sin(3.0 * t)
        
        px = cx + x * scale
        py = cy + y * scale
        pts.append({'px': px, 'py': py, 'pz': z, 't': t, 'idx': i})

    # Ribbon width with subtle organic breathing:
    # Slightly wider at the outer turns (t where |z| is low), sleek at crossings
    ribbon_w = 42.0
    for i in range(num_segments):
        c = pts[i]
        n = pts[(i + 1) % num_segments]
        dx, dy = n['px'] - c['px'], n['py'] - c['py']
        L = math.hypot(dx, dy) or 1e-5
        nx, ny = -dy / L, dx / L
        # Width modulation
        w = ribbon_w * (1.0 + 0.12 * math.cos(3 * c['t']))
        c['pl'] = (c['px'] + nx * w, c['py'] + ny * w)
        c['pr'] = (c['px'] - nx * w, c['py'] - ny * w)
        c['width'] = w
        c['nx'] = nx
        c['ny'] = ny

    # Ambient occlusion:
    # For each segment i, look for other segments j where:
    # 1. |i - j| > 40 (not adjacent along curve)
    # 2. pts[j]['pz'] > pts[i]['pz'] + 0.5 (j is significantly in front of i)
    # 3. 2D distance between (px, py) is less than (w_i + w_j) * 0.9
    for i in range(num_segments):
        c = pts[i]
        ao_factor = 1.0
        for j in range(num_segments):
            # check index distance along closed loop
            idx_diff = abs(i - j)
            idx_diff = min(idx_diff, num_segments - idx_diff)
            if idx_diff < 50:
                continue
            other = pts[j]
            z_diff = other['pz'] - c['pz']
            if z_diff > 0.6: # other is in front of c
                dist_2d = math.hypot(other['px'] - c['px'], other['py'] - c['py'])
                thresh = (c['width'] + other['width']) * 0.75
                if dist_2d < thresh:
                    # Occurred under a crossing strand!
                    # Smooth hermite falloff
                    d_norm = dist_2d / thresh
                    # Shadow intensity
                    shadow = (1.0 - d_norm * d_norm) * 0.45 * min(1.0, z_diff / 1.5)
                    ao_factor = min(ao_factor, 1.0 - shadow)
        c['ao'] = ao_factor

    # Let's render both dark and light modes with this AO!
    for mode in ['dark', 'light']:
        quads = []
        is_dark = (mode == 'dark')
        bg = "#121110" if is_dark else "#FAF7F2"
        txt_main = "#F5EFE6" if is_dark else "#1A1816"
        txt_sub = "#9E968B" if is_dark else "#787168"
        
        for i in range(num_segments):
            c = pts[i]
            n = pts[(i + 1) % num_segments]
            avg_z = (c['pz'] + n['pz']) / 2.0
            avg_ao = (c['ao'] + n['ao']) / 2.0
            
            zn = max(0.0, min(1.0, (avg_z + 2.0) / 4.0)) # 0 to 1
            
            if is_dark:
                # Dark mode: Front strands catch warm oat/champagne light (#D8CDC0),
                # Back strands sink into warm charcoal/slate (#36322E),
                # AO deepens it further.
                base_r = 50 + zn * 175
                base_g = 46 + zn * 165
                base_b = 42 + zn * 150
                
                # Apply AO
                r = int(base_r * avg_ao)
                g = int(base_g * avg_ao)
                b = int(base_b * avg_ao)
            else:
                # Light mode: Front strands are elegant deep charcoal/smoked bronze (#282420),
                # Back strands are warm stone/taupe (#968B7D).
                # AO darkens the shadowed region under the crossing
                base_r = 150 - zn * 110
                base_g = 140 - zn * 104
                base_b = 130 - zn * 98
                
                # Apply AO
                r = int(base_r * avg_ao)
                g = int(base_g * avg_ao)
                b = int(base_b * avg_ao)
                
            col = f"#{r:02x}{g:02x}{b:02x}"
            quads.append({'z': avg_z, 'pts': [c['pl'], n['pl'], n['pr'], c['pr']], 'col': col})
            
        quads.sort(key=lambda q: q['z'])
        paths = [f'<path d="M {q["pts"][0][0]:.2f} {q["pts"][0][1]:.2f} L {q["pts"][1][0]:.2f} {q["pts"][1][1]:.2f} L {q["pts"][2][0]:.2f} {q["pts"][2][1]:.2f} L {q["pts"][3][0]:.2f} {q["pts"][3][1]:.2f} Z" fill="{q["col"]}" stroke="{q["col"]}" stroke-width="0.8" />' for q in quads]
        
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <defs>
    <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="18" flood-color="#000" flood-opacity="{'0.35' if is_dark else '0.08'}" />
    </filter>
  </defs>
  <rect width="800" height="800" fill="{bg}" />
  
  <!-- Subtle generative latent halo -->
  <circle cx="{cx}" cy="{cy}" r="225" fill="none" stroke="{'rgba(245,239,230,0.08)' if is_dark else 'rgba(30,28,26,0.05)'}" stroke-width="1.2" stroke-dasharray="3 4" />
  <circle cx="{cx}" cy="{cy}" r="265" fill="none" stroke="{'rgba(245,239,230,0.04)' if is_dark else 'rgba(30,28,26,0.03)'}" stroke-width="1" />

  <g filter="url(#softGlow)">
    {"".join(paths)}
  </g>

  <!-- Typography -->
  <text x="400" y="650" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', 'Helvetica Neue', sans-serif" font-size="34" font-weight="500" letter-spacing="12" fill="{txt_main}" text-anchor="middle">KHORA</text>
  <text x="400" y="685" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Text', 'Helvetica Neue', sans-serif" font-size="12" font-weight="400" letter-spacing="4.5" fill="{txt_sub}" text-anchor="middle">GENERATIVE INTELLIGENCE</text>
</svg>"""
        with open(f"src/ao_{mode}.svg", "w") as f:
            f.write(svg)
            
    print("AO rendering completed")

if __name__ == "__main__":
    test_ao_shading()
