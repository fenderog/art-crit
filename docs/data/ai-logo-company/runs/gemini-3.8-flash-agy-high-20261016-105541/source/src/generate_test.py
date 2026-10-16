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
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800">
  <defs>
    <radialGradient id="bg" cx="50%" cy="50%" r="70%">
      <stop offset="0%" stop-color="#FAF8F5"/>
      <stop offset="100%" stop-color="#EDE7DE"/>
    </radialGradient>
    <linearGradient id="pGrad1" x1="20%" y1="0%" x2="80%" y2="100%">
      <stop offset="0%" stop-color="#3D3731"/>
      <stop offset="100%" stop-color="#1E1C1A"/>
    </linearGradient>
    <linearGradient id="pGrad2" x1="20%" y1="0%" x2="80%" y2="100%">
      <stop offset="0%" stop-color="#877A6C"/>
      <stop offset="100%" stop-color="#594F45"/>
    </linearGradient>
    <linearGradient id="pGrad3" x1="20%" y1="0%" x2="80%" y2="100%">
      <stop offset="0%" stop-color="#C5B8A8"/>
      <stop offset="100%" stop-color="#9C8E7E"/>
    </linearGradient>
  </defs>
  <rect width="800" height="800" fill="url(#bg)"/>
  <g transform="translate(400, 330)">
"""

    grads = ["url(#pGrad1)", "url(#pGrad2)", "url(#pGrad3)"]
    petal_base = create_sculpted_petal(scale=160)

    for i in range(3):
        ang = i * 120
        shift_r = 36
        scx = shift_r * math.cos(math.radians(ang - 40))
        scy = shift_r * math.sin(math.radians(ang - 40))
        pts = rotate_and_translate(petal_base, scx, scy, ang)
        d = catmull_rom_to_bezier(pts)
        svg += f'    <path d="{d}" fill="{grads[i]}" opacity="0.88" mix-blend-mode="multiply"/>\n'

    svg += """  </g>
  <text x="400" y="605" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" font-size="44" font-weight="500" fill="#201E1C" text-anchor="middle" letter-spacing="12">MORPHIC</text>
  <text x="400" y="645" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif" font-size="13" font-weight="400" fill="#756B60" text-anchor="middle" letter-spacing="6">GENERATIVE INTELLIGENCE</text>
</svg>"""

    with open("test_refined.svg", "w") as f:
        f.write(svg)

    subprocess.run(["sips", "-s", "format", "png", "test_refined.svg", "--out", "test_refined.png"], check=True)
    print("Done")

if __name__ == "__main__":
    main()
