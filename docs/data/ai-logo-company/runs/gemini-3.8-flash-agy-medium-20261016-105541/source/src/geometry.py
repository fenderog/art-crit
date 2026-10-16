import math

def get_trefoil_geometry(num_t=480, num_cross=16, scale=95.0, cx=400, cy=320, rot_x_deg=0, rot_z_deg=0):
    """
    Generate 3D ribbon surface grid for trefoil knot.
    num_t: number of slices along curve
    num_cross: number of vertices across the ribbon width
    """
    rot_x = math.radians(rot_x_deg)
    rot_z = math.radians(rot_z_deg)
    
    # Base curve points and frame
    centerline = []
    for i in range(num_t):
        t = (2.0 * math.pi * i) / num_t
        
        # Trefoil knot
        x = math.sin(t) + 2.0 * math.sin(2.0 * t)
        y = math.cos(t) - 2.0 * math.cos(2.0 * t)
        z = -math.sin(3.0 * t)
        
        # Tangent vector (derivative)
        dx_dt = math.cos(t) + 4.0 * math.cos(2.0 * t)
        dy_dt = -math.sin(t) + 4.0 * math.sin(2.0 * t)
        dz_dt = -3.0 * math.cos(3.0 * t)
        
        # Rotate coordinates
        # Rot z
        x1 = x * math.cos(rot_z) - y * math.sin(rot_z)
        y1 = x * math.sin(rot_z) + y * math.cos(rot_z)
        z1 = z
        
        dx1 = dx_dt * math.cos(rot_z) - dy_dt * math.sin(rot_z)
        dy1 = dx_dt * math.sin(rot_z) + dy_dt * math.cos(rot_z)
        dz1 = dz_dt
        
        # Rot x
        x2 = x1
        y2 = y1 * math.cos(rot_x) - z1 * math.sin(rot_x)
        z2 = y1 * math.sin(rot_x) + z1 * math.cos(rot_x)
        
        dx2 = dx1
        dy2 = dy1 * math.cos(rot_x) - dz1 * math.sin(rot_x)
        dz2 = dy1 * math.sin(rot_x) + dz1 * math.cos(rot_x)
        
        # Normalize tangent
        t_len = math.sqrt(dx2*dx2 + dy2*dy2 + dz2*dz2) or 1.0
        tx, ty, tz = dx2 / t_len, dy2 / t_len, dz2 / t_len
        
        # In the projection plane (Z pointing at viewer),
        # we want the ribbon normal to lie mainly in the screen plane
        # Ribbon width vector in 2D screen plane is perpendicular to (tx, ty)
        t_xy_len = math.sqrt(tx*tx + ty*ty) or 1.0
        # Normal across ribbon width:
        wx = -ty / t_xy_len
        wy = tx / t_xy_len
        wz = 0.0
        
        # Surface normal (pointing out of ribbon face):
        # cross(T, W)
        nx = ty * wz - tz * wy
        ny = tz * wx - tx * wz
        nz = tx * wy - ty * wx
        n_len = math.sqrt(nx*nx + ny*ny + nz*nz) or 1.0
        nx, ny, nz = nx / n_len, ny / n_len, nz / n_len
        if nz < 0:
            nx, ny, nz = -nx, -ny, -nz # point towards viewer
            
        centerline.append({
            't': t,
            'pos': (cx + x2 * scale, cy + y2 * scale, z2 * scale),
            'tangent': (tx, ty, tz),
            'width_dir': (wx, wy, wz),
            'surf_normal': (nx, ny, nz),
            'raw_z': z2,
        })
        
    return centerline

print("Geometry module loaded")
