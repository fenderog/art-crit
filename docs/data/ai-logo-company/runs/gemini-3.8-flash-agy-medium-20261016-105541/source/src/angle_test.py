import math
import subprocess
import os

def render_trefoil_angles(angles=[(0, 0, "flat"), (18, 20, "subtle"), (25, 30, "tilted")]):
    for rx, rz, label in angles:
        cx, cy = 400, 320
        scale = 90.0
        num_segments = 360
        rot_x = math.radians(rx)
        rot_z = math.radians(rz)
        
        pts = []
        for i in range(num_segments):
            t = (2 * math.pi * i) / num_segments
            x = math.sin(t) + 2.0 * math.sin(2.0 * t)
            y = math.cos(t) - 2.0 * math.cos(2.0 * t)
            z = -math.sin(3.0 * t)
            
            x1 = x * math.cos(rot_z) - y * math.sin(rot_z)
            y1 = x * math.sin(rot_z) + y * math.cos(rot_z)
            z1 = z
            
            x2 = x1
            y2 = y1 * math.cos(rot_x) - z1 * math.sin(rot_x)
            z2 = y1 * math.sin(rot_x) + z1 * math.cos(rot_x)
            
            pts.append({'px': cx + x2 * scale, 'py': cy + y2 * scale, 'pz': z2, 't': t})
            
        ribbon_w = 40.0
        quads = []
        for i in range(num_segments):
            c = pts[i]
            n = pts[(i + 1) % num_segments]
            dx, dy = n['px'] - c['px'], n['py'] - c['py']
            L = math.hypot(dx, dy) or 1e-5
            nx, ny = -dy / L, dx / L
            w = ribbon_w * (1.0 + 0.18 * math.sin(3 * c['t'] + 1.2))
            c['pl'] = (c['px'] + nx * w, c['py'] + ny * w)
            c['pr'] = (c['px'] - nx * w, c['py'] - ny * w)
            
        for i in range(num_segments):
            c = pts[i]
            n = pts[(i + 1) % num_segments]
            avg_z = (c['pz'] + n['pz']) / 2.0
            zn = max(0.0, min(1.0, (avg_z + 2.0) / 4.0))
            # Dark mode neutral palette
            r = int(55 + zn * 170)
            g = int(50 + zn * 160)
            b = int(45 + zn * 145)
            col = f"#{r:02x}{g:02x}{b:02x}"
            quads.append({'z': avg_z, 'pts': [c['pl'], n['pl'], n['pr'], c['pr']], 'col': col})
            
        quads.sort(key=lambda q: q['z'])
        paths = [f'<path d="M {q["pts"][0][0]:.2f} {q["pts"][0][1]:.2f} L {q["pts"][1][0]:.2f} {q["pts"][1][1]:.2f} L {q["pts"][2][0]:.2f} {q["pts"][2][1]:.2f} L {q["pts"][3][0]:.2f} {q["pts"][3][1]:.2f} Z" fill="{q["col"]}" stroke="{q["col"]}" stroke-width="0.8" />' for q in quads]
        
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <rect width="800" height="800" fill="#151413" />
  <g>{ "".join(paths) }</g>
  <text x="400" y="650" font-family="system-ui, -apple-system, sans-serif" font-size="34" font-weight="500" letter-spacing="11" fill="#F5EFE6" text-anchor="middle">KHORA</text>
  <text x="400" y="685" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="400" letter-spacing="4.5" fill="#9E968B" text-anchor="middle">GENERATIVE INTELLIGENCE</text>
</svg>"""
        with open(f"src/angle_{label}.svg", "w") as f:
            f.write(svg)

render_trefoil_angles()
print("Rendered angle variations")
