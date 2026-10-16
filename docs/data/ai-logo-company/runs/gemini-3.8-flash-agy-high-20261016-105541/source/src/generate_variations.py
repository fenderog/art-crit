import math
import subprocess

def catmull_rom_to_bezier(points):
    d = []
    n = len(points)
    pts = [points[-1]] + points + [points[0], points[1]]
    for i in range(1, n + 1):
        p0, p1, p2, p3 = pts[i-1], pts[i], pts[i+1], pts[i+2]
        cp1x = p1[0] + (p2[0] - p0[0]) / 6.0
        cp1y = p1[1] + (p2[1] - p0[1]) / 6.0
        cp2x = p2[0] - (p3[0] - p1[0]) / 6.0
        cp2y = p2[1] - (p3[1] - p1[1]) / 6.0
        if i == 1:
            d.append(f"M {p1[0]:.2f} {p1[1]:.2f}")
        d.append(f"C {cp1x:.2f} {cp1y:.2f}, {cp2x:.2f} {cp2y:.2f}, {p2[0]:.2f} {p2[1]:.2f}")
    d.append("Z")
    return " ".join(d)

def create_sculpted_petal(scale=1.0):
    base_points = [
        (0.00, -1.18),   # graceful apex
        (0.28, -0.95),   # upper right curve
        (0.56, -0.48),   # shoulder
        (0.68,  0.08),   # full belly
        (0.52,  0.62),   # lower sweep
        (0.18,  0.92),   # bottom rounded base
        (-0.12, 0.85),   # bottom left turnaround
        (-0.30, 0.52),   # lower inner flank
        (-0.42, 0.10),   # inner waist
        (-0.35, -0.38),  # inner neck
        (-0.18, -0.82),  # leading into apex
    ]
    return [(x * scale, y * scale) for x, y in base_points]

def rotate_and_translate(points, cx, cy, angle_deg):
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    return [(cx + (px * cos_a - py * sin_a), cy + (px * sin_a + py * cos_a)) for px, py in points]

def main():
    petal_base = create_sculpted_petal(scale=135)

    # Variant 1: Refined Balanced Neutrals
    g1 = """
    <linearGradient id="v1_g1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38322C"/><stop offset="100%" stop-color="#1A1816"/>
    </linearGradient>
    <linearGradient id="v1_g2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#6E6255"/><stop offset="100%" stop-color="#483F36"/>
    </linearGradient>
    <linearGradient id="v1_g3" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#A19383"/><stop offset="100%" stop-color="#736657"/>
    </linearGradient>
"""
    p1 = ""
    grads1 = ["url(#v1_g1)", "url(#v1_g2)", "url(#v1_g3)"]
    for i in range(3):
        ang = i * 120
        scx = 32 * math.cos(math.radians(ang - 40))
        scy = 32 * math.sin(math.radians(ang - 40))
        pts = rotate_and_translate(petal_base, scx, scy, ang)
        d = catmull_rom_to_bezier(pts)
        p1 += f'    <path d="{d}" fill="{grads1[i]}" opacity="0.86" mix-blend-mode="multiply"/>\n'

    svg1 = f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
  <defs>{g1}</defs>
  <rect width="600" height="600" fill="#FAF8F5"/>
  <g transform="translate(300, 260)">{p1}</g>
  <text x="300" y="490" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" font-size="34" font-weight="500" fill="#201E1C" text-anchor="middle" letter-spacing="10">MORPHIC</text>
  <text x="300" y="525" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif" font-size="11" font-weight="400" fill="#756B60" text-anchor="middle" letter-spacing="5">GENERATIVE INTELLIGENCE</text>
</svg>"""

    with open("var1.svg", "w") as f:
        f.write(svg1)
    subprocess.run(["sips", "-s", "format", "png", "var1.svg", "--out", "var1.png"], check=True)

    # Variant 2: With delicate internal contours
    p2 = p1
    for i in range(3):
        ang = i * 120
        scx = 32 * math.cos(math.radians(ang - 40))
        scy = 32 * math.sin(math.radians(ang - 40))
        for scale_c, op in [(0.75, 0.45), (0.52, 0.65)]:
            p_c = create_sculpted_petal(scale=135 * scale_c)
            pts_c = rotate_and_translate(p_c, scx, scy, ang)
            d_c = catmull_rom_to_bezier(pts_c)
            p2 += f'    <path d="{d_c}" fill="none" stroke="#FAF8F5" stroke-width="1.5" stroke-opacity="{op}"/>\n'

    svg2 = f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
  <defs>{g1}</defs>
  <rect width="600" height="600" fill="#FAF8F5"/>
  <g transform="translate(300, 260)">{p2}</g>
  <text x="300" y="490" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" font-size="34" font-weight="500" fill="#201E1C" text-anchor="middle" letter-spacing="10">MORPHIC</text>
  <text x="300" y="525" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif" font-size="11" font-weight="400" fill="#756B60" text-anchor="middle" letter-spacing="5">GENERATIVE INTELLIGENCE</text>
</svg>"""
    with open("var2.svg", "w") as f:
        f.write(svg2)
    subprocess.run(["sips", "-s", "format", "png", "var2.svg", "--out", "var2.png"], check=True)

    # Variant 3: Dark Mode
    g3 = """
    <linearGradient id="v3_g1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F2ECE1"/><stop offset="100%" stop-color="#C7BBA8"/>
    </linearGradient>
    <linearGradient id="v3_g2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#C2B4A0"/><stop offset="100%" stop-color="#8F816E"/>
    </linearGradient>
    <linearGradient id="v3_g3" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#807261"/><stop offset="100%" stop-color="#554A3D"/>
    </linearGradient>
"""
    p3 = ""
    grads3 = ["url(#v3_g1)", "url(#v3_g2)", "url(#v3_g3)"]
    for i in range(3):
        ang = i * 120
        scx = 32 * math.cos(math.radians(ang - 40))
        scy = 32 * math.sin(math.radians(ang - 40))
        pts = rotate_and_translate(petal_base, scx, scy, ang)
        d = catmull_rom_to_bezier(pts)
        p3 += f'    <path d="{d}" fill="{grads3[i]}" opacity="0.88" mix-blend-mode="screen"/>\n'

    svg3 = f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
  <defs>{g3}</defs>
  <rect width="600" height="600" fill="#141312"/>
  <g transform="translate(300, 260)">{p3}</g>
  <text x="300" y="490" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" font-size="34" font-weight="500" fill="#F0EBE1" text-anchor="middle" letter-spacing="10">MORPHIC</text>
  <text x="300" y="525" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif" font-size="11" font-weight="400" fill="#998D7E" text-anchor="middle" letter-spacing="5">GENERATIVE INTELLIGENCE</text>
</svg>"""
    with open("var3.svg", "w") as f:
        f.write(svg3)
    subprocess.run(["sips", "-s", "format", "png", "var3.svg", "--out", "var3.png"], check=True)
    print("All variants generated successfully!")

if __name__ == "__main__":
    main()
