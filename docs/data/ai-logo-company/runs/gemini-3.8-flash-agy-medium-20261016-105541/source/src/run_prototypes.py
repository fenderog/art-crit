import math
import subprocess
import os
from generate_prototypes import catmull_rom_to_bezier

def render_proto_a():
    # 3-lobe sweeping organic ribbon vortex
    cx, cy = 400, 330
    
    # Let's craft an organic leaf / ribbon lobe that looks like a graceful curved brushstroke
    # Head near center (r=45, angle=20), sweeps out in a dynamic curved arc to r=220, angle=95,
    # rounds smoothly, and tapers along the inner flank.
    lobe_poly = [
        (35, 10),
        (85, 30),
        (160, 65),
        (210, 100),
        (225, 135),
        (205, 165),
        (150, 175),
        (100, 150),
        (65, 110),
        (40, 60),
    ]
    def make_path(rot):
        pts = []
        for r, deg in lobe_poly:
            rad = math.radians(deg + rot)
            pts.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
        return catmull_rom_to_bezier(pts)

    p1, p2, p3 = make_path(0), make_path(120), make_path(240)
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <defs>
    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3A3530" />
      <stop offset="100%" stop-color="#6E645A" />
    </linearGradient>
    <linearGradient id="g2" x1="100%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#554C44" />
      <stop offset="100%" stop-color="#8C8074" />
    </linearGradient>
    <linearGradient id="g3" x1="50%" y1="100%" x2="50%" y2="0%">
      <stop offset="0%" stop-color="#282421" />
      <stop offset="100%" stop-color="#5A5148" />
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#000" flood-opacity="0.08" />
    </filter>
  </defs>
  <rect width="800" height="800" fill="#F8F6F2" />
  <g filter="url(#shadow)">
    <path d="{p1}" fill="url(#g1)" opacity="0.9" style="mix-blend-mode: multiply;" />
    <path d="{p2}" fill="url(#g2)" opacity="0.9" style="mix-blend-mode: multiply;" />
    <path d="{p3}" fill="url(#g3)" opacity="0.9" style="mix-blend-mode: multiply;" />
  </g>
  <circle cx="{cx}" cy="{cy}" r="16" fill="#C5A078" />
  <text x="400" y="650" font-family="system-ui, -apple-system, sans-serif" font-size="34" font-weight="500" letter-spacing="10" fill="#1F1D1A" text-anchor="middle">MORPHIC</text>
  <text x="400" y="685" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="400" letter-spacing="4" fill="#7E766D" text-anchor="middle">GENERATIVE INTELLIGENCE</text>
</svg>"""
    with open("src/proto_a.svg", "w") as f:
        f.write(svg)

def render_proto_b():
    # Organic Dyad / Dual Embracing Fluid Droplets (Synthesis / Latent Coalescence)
    cx, cy = 400, 330
    
    # A graceful, sweeping teardrop / river-stone embryo
    # Shape 1
    pts1 = [
        (cx - 30, cy - 210),
        (cx + 90, cy - 190),
        (cx + 170, cy - 110),
        (cx + 190, cy + 10),
        (cx + 140, cy + 120),
        (cx + 40, cy + 190),
        (cx - 60, cy + 170),
        (cx - 80, cy + 90),
        (cx - 30, cy + 10),
        (cx + 40, cy - 60),
        (cx + 20, cy - 140),
    ]
    # Shape 2 rotated 180 and scaled / slightly shifted for organic dialogue
    pts2 = []
    for x, y in pts1:
        # 180 rotation around cx, cy
        dx = x - cx
        dy = y - cy
        pts2.append((cx - dx * 0.92, cy - dy * 0.92))
    
    p1 = catmull_rom_to_bezier(pts1)
    p2 = catmull_rom_to_bezier(pts2)
    
    # Concentric latent field ripples
    ripples = []
    for r_base in [230, 260, 290]:
        r_pts = []
        for a in range(60):
            ang = 2 * math.pi * a / 60
            r = r_base * (1 + 0.05 * math.sin(2 * ang + 0.8) + 0.03 * math.cos(3 * ang))
            r_pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        ripples.append(catmull_rom_to_bezier(r_pts))

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <defs>
    <linearGradient id="dyad1" x1="10%" y1="0%" x2="90%" y2="100%">
      <stop offset="0%" stop-color="#2D2925" />
      <stop offset="100%" stop-color="#584F45" />
    </linearGradient>
    <linearGradient id="dyad2" x1="90%" y1="100%" x2="10%" y2="0%">
      <stop offset="0%" stop-color="#8A7D6E" />
      <stop offset="100%" stop-color="#BFB2A2" />
    </linearGradient>
    <filter id="shadowB" x="-15%" y="-15%" width="130%" height="130%">
      <feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#000" flood-opacity="0.1" />
    </filter>
  </defs>
  <rect width="800" height="800" fill="#FAF7F2" />
  
  <g fill="none" stroke="rgba(35,32,29,0.08)" stroke-width="1.2" stroke-dasharray="2 3">
    {"".join(f'<path d="{rp}" />' for rp in ripples)}
  </g>

  <g filter="url(#shadowB)">
    <path d="{p1}" fill="url(#dyad1)" opacity="0.94" />
    <path d="{p2}" fill="url(#dyad2)" opacity="0.88" style="mix-blend-mode: multiply;" />
  </g>

  <circle cx="{cx + 15}" cy="{cy - 10}" r="14" fill="#C29B72" />
  
  <text x="400" y="650" font-family="system-ui, -apple-system, sans-serif" font-size="34" font-weight="500" letter-spacing="10" fill="#1F1D1A" text-anchor="middle">LATENT</text>
  <text x="400" y="685" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="400" letter-spacing="4" fill="#7E766D" text-anchor="middle">SYNTHETIC COGNITION</text>
</svg>"""
    with open("src/proto_b.svg", "w") as f:
        f.write(svg)

render_proto_a()
render_proto_b()
print("Rendered proto_a and proto_b")
