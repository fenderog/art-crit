import math

def calculate_trefoil_segments(num_segments=360, rot_x_deg=24, rot_z_deg=30, scale=88.0, cx=400, cy=320):
    knot_pts = []
    rot_x = math.radians(rot_x_deg)
    rot_z = math.radians(rot_z_deg)
    
    for i in range(num_segments):
        t = (2 * math.pi * i) / num_segments
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
        
        px = cx + x2 * scale
        py = cy + y2 * scale
        knot_pts.append({
            'idx': i,
            't': t,
            'px': px,
            'py': py,
            'pz': z2,
            'x': x2,
            'y': y2,
        })
    return knot_pts

print("Calculated segments")
