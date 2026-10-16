import math
import subprocess
import os

def catmull_rom_to_bezier(pts, closed=True):
    """Convert points to smooth cubic bezier path string"""
    n = len(pts)
    if n < 3:
        return ""
    d = [f"M {pts[0][0]:.2f} {pts[0][1]:.2f}"]
    limit = n if closed else n - 1
    for i in range(limit):
        p0 = pts[(i - 1) % n] if closed else pts[max(0, i - 1)]
        p1 = pts[i]
        p2 = pts[(i + 1) % n] if closed else pts[min(n - 1, i + 1)]
        p3 = pts[(i + 2) % n] if closed else pts[min(n - 1, i + 2)]
        
        cp1x = p1[0] + (p2[0] - p0[0]) / 5.2
        cp1y = p1[1] + (p2[1] - p0[1]) / 5.2
        cp2x = p2[0] - (p3[0] - p1[0]) / 5.2
        cp2y = p2[1] - (p3[1] - p1[1]) / 5.2
        
        d.append(f"C {cp1x:.2f} {cp1y:.2f}, {cp2x:.2f} {cp2y:.2f}, {p2[0]:.2f} {p2[1]:.2f}")
    if closed:
        d.append("Z")
    return " ".join(d)

# Prototype A: Sculpted 3-Ribbon Vortex with organic taper & overlapping depth
def prototype_a_ribbons():
    # One sweeping organic ribbon defined by outer and inner curves
    # We define the centerline and width profile, or control points for the outer and inner boundary
    # Outer boundary from tail to head, inner boundary returning from head to tail
    # Centered at (400, 330)
    cx, cy = 400, 330
    
    # Let's define the ribbon as an outer sweep and inner sweep
    # Outer points in polar relative to lobe center:
    lobe_poly = [
        # tip / beak
        (25, 45),
        # outer crest
        (95, 60),
        (175, 75),
        (235, 110),
        (255, 150),
        (230, 195),
        (170, 225),
        (105, 230),
        # tucking inward
        (50, 195),
        (20, 140),
        (35, 95),
    ]
    # Let's rotate this lobe 3 times: 0, 120, 240
    def get_lobe_svg(rot_deg):
        pts = []
        for r, deg in lobe_poly:
            rad = math.radians(deg + rot_deg)
            pts.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
        return catmull_rom_to_bezier(pts, closed=True)

    p1 = get_lobe_svg(0)
    p2 = get_lobe_svg(120)
    p3 = get_lobe_svg(240)
    return p1, p2, p3

# Prototype B: Two Embracing Fluid Droplets / Organic Dyad ("Symbiosis / Synthesis")
def prototype_b_dyad(cx=400, cy=330):
    # Two organic yin-yang style flowing teardrop bodies, but asymmetrical and pebble-like
    # Droplet 1: Large sweeping pebble from top-right down to bottom-left
    pts1 = [
        (cx + 40, cy - 180),
        (cx + 140, cy - 130),
        (cx + 190, cy - 30),
        (cx + 170, cy + 80),
        (cx + 90, cy + 160),
        (cx - 20, cy + 180),
        (cx - 110, cy + 130),
        (cx - 70, cy + 40),
        (cx - 10, cy - 20),
        (cx + 10, cy - 110),
    ]
    # Droplet 2: Complementary organic droplet nested inside / interlocking
    pts2 = [
        (cx - 40, cy + 180),
        (cx - 140, cy + 130),
        (cx - 190, cy + 30),
        (cx - 170, cy - 80),
        (cx - 90, cy - 160),
        (cx + 20, cy - 180),
        (cx + 110, cy - 130),
        (cx + 70, cy - 40),
        (cx + 10, cy + 20),
        (cx - 10, cy + 110),
    ]
    return catmull_rom_to_bezier(pts1), catmull_rom_to_bezier(pts2)

# Prototype C: The Generative Seed / Harmonic Shell
# 4 smooth organic spiral petals unfurling in golden-ratio progression
def prototype_c_spiral(cx=400, cy=330):
    petals = []
    # 4 petals rotated by 90 deg, with organic curvature
    for k in range(4):
        rot = k * 90
        # shape points
        pts = [
            (20, 0),
            (70, 30),
            (145, 45),
            (205, 25),
            (225, -20),
            (195, -65),
            (130, -85),
            (65, -60),
            (25, -25),
        ]
        world_pts = []
        for r, deg in pts:
            rad = math.radians(deg + rot)
            world_pts.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
        petals.append(catmull_rom_to_bezier(world_pts))
    return petals

print("Prototypes initialized")
