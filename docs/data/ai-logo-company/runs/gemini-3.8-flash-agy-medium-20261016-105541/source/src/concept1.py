import math
import subprocess
import os

def generate_concept_1(filename="concept_aperture.svg", is_dark=False):
    """
    Concept 1: The 'Morphogenesis' Nexus / Organic Bloom
    Three intertwined, smooth organic teardrop / pebble lobes arranged in rotational harmony
    with a central emerging nucleus, plus delicate concentric generative vector contours.
    """
    if is_dark:
        bg_col = "#141312"
        surface_col = "#1C1B19"
        text_primary = "#F2ECE4"
        text_secondary = "#9C948A"
        contour_col = "rgba(230, 220, 205, 0.12)"
        
        # Gradients for petals (warm stone, taupe, soft sand, muted bronze)
        grad_p1_start = "#D9CEC1"
        grad_p1_end = "#8A7D70"
        
        grad_p2_start = "#B8ADA0"
        grad_p2_end = "#665C52"
        
        grad_p3_start = "#E2D9CC"
        grad_p3_end = "#9E9182"
        
        nucleus_fill = "#FAF6F0"
        nucleus_glow = "rgba(250, 246, 240, 0.25)"
    else:
        bg_col = "#FAF8F5"
        surface_col = "#F3EFEA"
        text_primary = "#1E1C1A"
        text_secondary = "#7D756C"
        contour_col = "rgba(30, 28, 26, 0.08)"
        
        # Gradients for light mode
        grad_p1_start = "#38332E"
        grad_p1_end = "#695F56"
        
        grad_p2_start = "#544B42"
        grad_p2_end = "#85796E"
        
        grad_p3_start = "#292522"
        grad_p3_end = "#4D443C"
        
        nucleus_fill = "#C29B75"  # warm subtle ochre/terracotta stone
        nucleus_glow = "rgba(194, 155, 117, 0.2)"

    petal_pts_polar = [
        (45, 10),
        (120, 15),
        (205, 42),
        (230, 75),
        (215, 108),
        (170, 135),
        (115, 145),
        (65, 125),
        (35, 75),
        (25, 30),
    ]
    
    def polar_to_cart(r, deg, rot=0, cx=400, cy=350):
        rad = math.radians(deg + rot)
        return cx + r * math.cos(rad), cy + r * math.sin(rad)
    
    def make_petal_path(rot_deg, cx=400, cy=350):
        pts = [polar_to_cart(r, d, rot=rot_deg, cx=cx, cy=cy) for r, d in petal_pts_polar]
        n = len(pts)
        d_str = [f"M {pts[0][0]:.2f} {pts[0][1]:.2f}"]
        for i in range(n):
            p0 = pts[(i - 1) % n]
            p1 = pts[i]
            p2 = pts[(i + 1) % n]
            p3 = pts[(i + 2) % n]
            cp1x = p1[0] + (p2[0] - p0[0]) / 4.8
            cp1y = p1[1] + (p2[1] - p0[1]) / 4.8
            cp2x = p2[0] - (p3[0] - p1[0]) / 4.8
            cp2y = p2[1] - (p3[1] - p1[1]) / 4.8
            d_str.append(f"C {cp1x:.2f} {cp1y:.2f}, {cp2x:.2f} {cp2y:.2f}, {p2[0]:.2f} {p2[1]:.2f}")
        d_str.append("Z")
        return " ".join(d_str)

    contour_paths = []
    for ring_idx, (scale, base_r, amp1, amp2) in enumerate([
        (1.0, 270, 0.08, 0.05),
        (1.0, 315, 0.06, 0.04),
        (1.0, 360, 0.05, 0.03),
    ]):
        ring_pts = []
        num_seg = 72
        for s in range(num_seg):
            ang = (2 * math.pi * s) / num_seg
            r = base_r * (1.0 + amp1 * math.sin(3 * ang + 0.4 * ring_idx) + amp2 * math.cos(2 * ang - 0.3 * ring_idx))
            ring_pts.append((400 + r * math.cos(ang), 350 + r * math.sin(ang)))
        n_p = len(ring_pts)
        d_r = [f"M {ring_pts[0][0]:.2f} {ring_pts[0][1]:.2f}"]
        for i in range(n_p):
            p0 = ring_pts[(i - 1) % n_p]
            p1 = ring_pts[i]
            p2 = ring_pts[(i + 1) % n_p]
            p3 = ring_pts[(i + 2) % n_p]
            cp1x = p1[0] + (p2[0] - p0[0]) / 6.0
            cp1y = p1[1] + (p2[1] - p0[1]) / 6.0
            cp2x = p2[0] - (p3[0] - p1[0]) / 6.0
            cp2y = p2[1] - (p3[1] - p1[1]) / 6.0
            d_r.append(f"C {cp1x:.2f} {cp1y:.2f}, {cp2x:.2f} {cp2y:.2f}, {p2[0]:.2f} {p2[1]:.2f}")
        d_r.append("Z")
        contour_paths.append(" ".join(d_r))

    p1 = make_petal_path(0)
    p2 = make_petal_path(120)
    p3 = make_petal_path(240)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <defs>
    <radialGradient id="bgGlow" cx="50%" cy="45%" r="65%">
      <stop offset="0%" stop-color="{surface_col}" stop-opacity="1" />
      <stop offset="100%" stop-color="{bg_col}" stop-opacity="1" />
    </radialGradient>

    <linearGradient id="gradP1" x1="20%" y1="0%" x2="80%" y2="100%">
      <stop offset="0%" stop-color="{grad_p1_start}" />
      <stop offset="100%" stop-color="{grad_p1_end}" />
    </linearGradient>

    <linearGradient id="gradP2" x1="100%" y1="10%" x2="0%" y2="90%">
      <stop offset="0%" stop-color="{grad_p2_start}" />
      <stop offset="100%" stop-color="{grad_p2_end}" />
    </linearGradient>

    <linearGradient id="gradP3" x1="40%" y1="100%" x2="70%" y2="0%">
      <stop offset="0%" stop-color="{grad_p3_start}" />
      <stop offset="100%" stop-color="{grad_p3_end}" />
    </linearGradient>

    <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>

    <filter id="subtleShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000" flood-opacity="{'0.25' if is_dark else '0.08'}" />
    </filter>
  </defs>

  <!-- Background -->
  <rect width="800" height="800" fill="url(#bgGlow)" />

  <!-- Generative topographic contours -->
  <g fill="none" stroke="{contour_col}" stroke-width="1.2" stroke-dasharray="3 3">
    {"".join(f'<path d="{cp}" />' for cp in contour_paths)}
  </g>

  <!-- Petals Group -->
  <g filter="url(#subtleShadow)">
    <!-- Petal 1 -->
    <path d="{p1}" fill="url(#gradP1)" opacity="0.95" style="mix-blend-mode: {'screen' if is_dark else 'multiply'};" />
    <!-- Petal 2 -->
    <path d="{p2}" fill="url(#gradP2)" opacity="0.95" style="mix-blend-mode: {'screen' if is_dark else 'multiply'};" />
    <!-- Petal 3 -->
    <path d="{p3}" fill="url(#gradP3)" opacity="0.95" style="mix-blend-mode: {'screen' if is_dark else 'multiply'};" />
  </g>

  <!-- Central generative nucleus / seed -->
  <circle cx="400" cy="350" r="32" fill="{nucleus_glow}" filter="url(#softGlow)" />
  <circle cx="400" cy="350" r="14" fill="{nucleus_fill}" />

  <!-- Typography -->
  <g text-anchor="middle">
    <!-- Brand Name -->
    <text x="400" y="660" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', 'Helvetica Neue', sans-serif" font-size="34" font-weight="500" letter-spacing="10" fill="{text_primary}">MORPHIC</text>
    
    <!-- Tagline -->
    <text x="400" y="695" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Inter', 'Helvetica Neue', sans-serif" font-size="11.5" font-weight="400" letter-spacing="4.5" fill="{text_secondary}">GENERATIVE INTELLIGENCE</text>
  </g>
</svg>"""

    with open(filename, "w") as f:
        f.write(svg)
    print(f"Written {filename}")

if __name__ == "__main__":
    generate_concept_1("src/concept_light.svg", is_dark=False)
    generate_concept_1("src/concept_dark.svg", is_dark=True)
