import math
import subprocess
import os

def render_sculptural_trefoil(filename="src/proto_trefoil.svg", is_dark=False):
    """
    Parametric sculptural organic trefoil knot / ribbon loop.
    Rendered with volumetric lighting, soft shadows, warm neutral tones.
    """
    # Palette
    if is_dark:
        bg = "#151413"
        txt_main = "#F5EFE6"
        txt_sub = "#9E968B"
        base_col = (180, 168, 154) # warm stone
    else:
        bg = "#FAF7F2"
        txt_main = "#1E1C1A"
        txt_sub = "#7D756C"
        base_col = (60, 54, 48) # deep warm charcoal/umber

    cx, cy = 400, 320
    
    # Trefoil knot parametrization:
    # x(t) = sin(t) + 2*sin(2t)
    # y(t) = cos(t) - 2*cos(2t)
    # z(t) = -sin(3t)
    
    num_segments = 360
    # We sample points along the curve
    knot_pts = []
    scale = 88.0
    
    # 3D rotation angles for pleasant viewing perspective
    # isometric-like tilt: rotate around X by 22 deg, Z by 30 deg
    rot_x = math.radians(22)
    rot_z = math.radians(30)
    
    for i in range(num_segments):
        t = (2 * math.pi * i) / num_segments
        # Trefoil formula
        x = math.sin(t) + 2.0 * math.sin(2.0 * t)
        y = math.cos(t) - 2.0 * math.cos(2.0 * t)
        z = -math.sin(3.0 * t)
        
        # Apply rot_z
        x1 = x * math.cos(rot_z) - y * math.sin(rot_z)
        y1 = x * math.sin(rot_z) + y * math.cos(rot_z)
        z1 = z
        
        # Apply rot_x
        x2 = x1
        y2 = y1 * math.cos(rot_x) - z1 * math.sin(rot_x)
        z2 = y1 * math.sin(rot_x) + z1 * math.cos(rot_x)
        
        px = cx + x2 * scale
        py = cy + y2 * scale
        knot_pts.append({
            'idx': i,
            't': t,
            'px': px,
            'py': py,
            'pz': z2,
            'nx': -math.cos(t) - 4.0 * math.cos(2.0 * t), # tangent approx
            'ny': math.sin(t) - 4.0 * math.sin(2.0 * t),
        })

    # Let's inspect the z range to sort polygons for back-to-front rendering (Painter's algorithm)
    # Or divide the trefoil into 3 overlapping continuous lobes (since trefoil has 3-fold symmetry)
    # Each lobe spans 120 degrees of t, e.g. [0, 2pi/3], [2pi/3, 4pi/3], [4pi/3, 2pi]
    # At each crossing, one branch clearly passes in front of the other.
    
    # Let's check ribbon width:
    # A ribbon can be formed by offsetting normal to tangent in 2D or 3D
    # Normal in 2D: (-ny, nx) normalized
    ribbon_width = 38.0
    
    # Compute left and right edge points
    quads = []
    for i in range(num_segments):
        curr = knot_pts[i]
        nxt = knot_pts[(i + 1) % num_segments]
        
        dx = nxt['px'] - curr['px']
        dy = nxt['py'] - curr['py']
        length = math.hypot(dx, dy)
        if length == 0:
            length = 1e-5
        
        # normal vector
        norm_x = -dy / length
        norm_y = dx / length
        
        # Width modulation: slightly thicker at lobes, sleeker at crossings
        w = ribbon_width * (1.0 + 0.22 * math.sin(3 * curr['t'] + 1.2))
        
        p_left = (curr['px'] + norm_x * w, curr['py'] + norm_y * w)
        p_right = (curr['px'] - norm_x * w, curr['py'] - norm_y * w)
        curr['p_left'] = p_left
        curr['p_right'] = p_right
        
    for i in range(num_segments):
        curr = knot_pts[i]
        nxt = knot_pts[(i + 1) % num_segments]
        avg_z = (curr['pz'] + nxt['pz']) / 2.0
        
        # Lighting calculation: light source from top-left (dx=-1, dy=-1, dz=1.5)
        # Tangent vector and normal vector
        t = curr['t']
        
        # Neutral tone shading based on depth and angle
        # z2 ranges roughly from -2 to +2
        z_norm = (avg_z + 2.0) / 4.0 # 0 to 1
        z_norm = max(0.0, min(1.0, z_norm))
        
        if is_dark:
            # highlight on front, shadow on back
            # Front: warm champagne/sand #DED4C5, Back: deep charcoal #3A3530
            r = int(55 + z_norm * 165)
            g = int(50 + z_norm * 155)
            b = int(45 + z_norm * 140)
        else:
            # Front: deep warm graphite #2B2724, Back: soft taupe/sand #9E9385
            # In light mode, front can be darker or lighter with shadow
            # Let's give front a rich warm slate (#2C2825) with soft lighting
            r = int(145 - z_norm * 95)
            g = int(135 - z_norm * 90)
            b = int(125 - z_norm * 85)
            
        color_hex = f"#{r:02x}{g:02x}{b:02x}"
        
        quads.append({
            'avg_z': avg_z,
            'pts': [curr['p_left'], nxt['p_left'], nxt['p_right'], curr['p_right']],
            'color': color_hex,
            'z_norm': z_norm,
        })
        
    # Sort quads back to front
    quads.sort(key=lambda q: q['avg_z'])
    
    quad_paths = []
    for q in quads:
        pts = q['pts']
        d = f"M {pts[0][0]:.2f} {pts[0][1]:.2f} L {pts[1][0]:.2f} {pts[1][1]:.2f} L {pts[2][0]:.2f} {pts[2][1]:.2f} L {pts[3][0]:.2f} {pts[3][1]:.2f} Z"
        quad_paths.append(f'<path d="{d}" fill="{q["color"]}" stroke="{q["color"]}" stroke-width="0.8" />')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <defs>
    <filter id="shadowT" x="-15%" y="-15%" width="130%" height="130%">
      <feDropShadow dx="0" dy="14" stdDeviation="20" flood-color="#000" flood-opacity="{'0.3' if is_dark else '0.1'}" />
    </filter>
  </defs>
  <rect width="800" height="800" fill="{bg}" />
  
  <!-- Subtle generative orbital rings -->
  <circle cx="{cx}" cy="{cy}" r="225" fill="none" stroke="{'rgba(240,230,215,0.08)' if is_dark else 'rgba(50,45,40,0.06)'}" stroke-width="1.2" stroke-dasharray="3 4" />
  <circle cx="{cx}" cy="{cy}" r="275" fill="none" stroke="{'rgba(240,230,215,0.04)' if is_dark else 'rgba(50,45,40,0.04)'}" stroke-width="1" />

  <g filter="url(#shadowT)">
    {"".join(quad_paths)}
  </g>

  <!-- Brand Typography -->
  <g text-anchor="middle">
    <text x="400" y="650" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', 'Helvetica Neue', sans-serif" font-size="34" font-weight="500" letter-spacing="11" fill="{txt_main}">KHORA</text>
    <text x="400" y="685" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Text', 'Helvetica Neue', sans-serif" font-size="12" font-weight="400" letter-spacing="4.5" fill="{txt_sub}">GENERATIVE INTELLIGENCE</text>
  </g>
</svg>"""

    with open(filename, "w") as f:
        f.write(svg)
    print(f"Generated {filename}")

render_sculptural_trefoil("src/proto_trefoil_light.svg", is_dark=False)
render_sculptural_trefoil("src/proto_trefoil_dark.svg", is_dark=True)
