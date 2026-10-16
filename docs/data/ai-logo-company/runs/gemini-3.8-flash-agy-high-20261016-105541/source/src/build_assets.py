import math
import subprocess
import os

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

def get_mark_svg_paths(scale=180, mode="light", shift_factor=0.237):
    petal_base = create_sculpted_petal(scale=scale)
    shift_r = scale * shift_factor
    
    paths = []
    if mode == "light":
        grads_ref = ["url(#morphicLightG1)", "url(#morphicLightG2)", "url(#morphicLightG3)"]
        opacity = "0.86"
        blend = "mix-blend-mode: multiply;"
    else:
        grads_ref = ["url(#morphicDarkG1)", "url(#morphicDarkG2)", "url(#morphicDarkG3)"]
        opacity = "0.88"
        blend = "mix-blend-mode: screen;"
        
    for i in range(3):
        ang = i * 120
        scx = shift_r * math.cos(math.radians(ang - 40))
        scy = shift_r * math.sin(math.radians(ang - 40))
        pts = rotate_and_translate(petal_base, scx, scy, ang)
        d = catmull_rom_to_bezier(pts)
        paths.append(f'<path d="{d}" fill="{grads_ref[i]}" opacity="{opacity}" style="{blend}"/>')
    return "\n    ".join(paths)

def get_gradient_defs():
    return """
    <!-- Neutral Tones Gradient Definitions -->
    <linearGradient id="morphicLightG1" x1="15%" y1="0%" x2="85%" y2="100%">
      <stop offset="0%" stop-color="#3A342E"/>
      <stop offset="100%" stop-color="#1B1917"/>
    </linearGradient>
    <linearGradient id="morphicLightG2" x1="15%" y1="0%" x2="85%" y2="100%">
      <stop offset="0%" stop-color="#706456"/>
      <stop offset="100%" stop-color="#4A4137"/>
    </linearGradient>
    <linearGradient id="morphicLightG3" x1="15%" y1="0%" x2="85%" y2="100%">
      <stop offset="0%" stop-color="#A69887"/>
      <stop offset="100%" stop-color="#756858"/>
    </linearGradient>

    <linearGradient id="morphicDarkG1" x1="15%" y1="0%" x2="85%" y2="100%">
      <stop offset="0%" stop-color="#F2ECE1"/>
      <stop offset="100%" stop-color="#C7BBA8"/>
    </linearGradient>
    <linearGradient id="morphicDarkG2" x1="15%" y1="0%" x2="85%" y2="100%">
      <stop offset="0%" stop-color="#C2B4A0"/>
      <stop offset="100%" stop-color="#8F816E"/>
    </linearGradient>
    <linearGradient id="morphicDarkG3" x1="15%" y1="0%" x2="85%" y2="100%">
      <stop offset="0%" stop-color="#807261"/>
      <stop offset="100%" stop-color="#554A3D"/>
    </linearGradient>
"""

def generate_primary_svg(filepath):
    # 1000x1000 Primary Lockup
    mark_paths = get_mark_svg_paths(scale=210, mode="light")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">
  <defs>{get_gradient_defs()}
  </defs>
  <!-- Background Canvas: Warm Alabaster -->
  <rect width="1000" height="1000" fill="#FAF8F5"/>
  
  <!-- Organic Mark -->
  <g transform="translate(500, 420)">
    {mark_paths}
  </g>
  
  <!-- Wordmark -->
  <text x="500" y="780" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" font-size="54" font-weight="500" fill="#1F1D1A" text-anchor="middle" letter-spacing="16">MORPHIC</text>
  <text x="500" y="835" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif" font-size="16" font-weight="400" fill="#756B60" text-anchor="middle" letter-spacing="8">GENERATIVE INTELLIGENCE</text>
</svg>"""
    with open(filepath, "w") as f:
        f.write(svg)

def generate_horizontal_svg(filepath):
    # 1200x400 Horizontal Lockup
    mark_paths = get_mark_svg_paths(scale=115, mode="light")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="400" viewBox="0 0 1200 400">
  <defs>{get_gradient_defs()}
  </defs>
  <!-- Background Canvas: Warm Alabaster -->
  <rect width="1200" height="400" fill="#FAF8F5"/>
  
  <!-- Organic Mark -->
  <g transform="translate(240, 200)">
    {mark_paths}
  </g>
  
  <!-- Wordmark Left-Aligned -->
  <g transform="translate(450, 0)">
    <text x="0" y="202" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" font-size="56" font-weight="500" fill="#1F1D1A" letter-spacing="14">MORPHIC</text>
    <text x="2" y="254" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif" font-size="15" font-weight="400" fill="#756B60" letter-spacing="7">GENERATIVE INTELLIGENCE</text>
  </g>
</svg>"""
    with open(filepath, "w") as f:
        f.write(svg)

def generate_isolated_mark_svg(filepath):
    # 512x512 Pure Vector Glyphs on Transparent Background
    mark_paths = get_mark_svg_paths(scale=155, mode="light")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <defs>{get_gradient_defs()}
  </defs>
  <!-- Transparent Canvas with Isolated Organic Mark -->
  <g transform="translate(256, 256)">
    {mark_paths}
  </g>
</svg>"""
    with open(filepath, "w") as f:
        f.write(svg)

def generate_dark_mode_svg(filepath):
    # 1000x1000 Dark Mode Lockup
    mark_paths = get_mark_svg_paths(scale=210, mode="dark")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">
  <defs>{get_gradient_defs()}
  </defs>
  <!-- Background Canvas: Deep Basalt -->
  <rect width="1000" height="1000" fill="#141312"/>
  
  <!-- Organic Mark with Luminous Screen Blend -->
  <g transform="translate(500, 420)">
    {mark_paths}
  </g>
  
  <!-- Wordmark Inverted -->
  <text x="500" y="780" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" font-size="54" font-weight="500" fill="#F5F2EC" text-anchor="middle" letter-spacing="16">MORPHIC</text>
  <text x="500" y="835" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif" font-size="16" font-weight="400" fill="#9E9283" text-anchor="middle" letter-spacing="8">GENERATIVE INTELLIGENCE</text>
</svg>"""
    with open(filepath, "w") as f:
        f.write(svg)

def generate_brand_sheet_svg(filepath):
    # 2400x1350 Master Brand Specification Sheet
    mark_large = get_mark_svg_paths(scale=190, mode="light")
    mark_dark_small = get_mark_svg_paths(scale=80, mode="dark")
    mark_light_small = get_mark_svg_paths(scale=80, mode="light")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1350" viewBox="0 0 2400 1350">
  <defs>{get_gradient_defs()}
    <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="12" stdDeviation="20" flood-color="#141312" flood-opacity="0.06"/>
    </filter>
  </defs>
  
  <!-- Background Canvas -->
  <rect width="2400" height="1350" fill="#F4F1EB"/>
  
  <!-- Subtle Grid Pattern -->
  <g opacity="0.15" stroke="#706456" stroke-width="0.75" stroke-dasharray="3 9">
    <line x1="120" y1="0" x2="120" y2="1350"/>
    <line x1="840" y1="0" x2="840" y2="1350"/>
    <line x1="1560" y1="0" x2="1560" y2="1350"/>
    <line x1="2280" y1="0" x2="2280" y2="1350"/>
    <line x1="0" y1="180" x2="2400" y2="180"/>
    <line x1="0" y1="780" x2="2400" y2="780"/>
    <line x1="0" y1="1230" x2="2400" y2="1230"/>
  </g>

  <!-- Header -->
  <g transform="translate(120, 110)">
    <text x="0" y="0" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', Arial, sans-serif" font-size="28" font-weight="600" fill="#1F1D1A" letter-spacing="4">MORPHIC LABS</text>
    <text x="320" y="0" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', Arial, sans-serif" font-size="14" font-weight="500" fill="#706456" letter-spacing="3">/ BRAND IDENTITY SYSTEM &amp; DESIGN SPECIFICATION</text>
    <text x="0" y="28" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', Arial, sans-serif" font-size="13" font-weight="400" fill="#8C7F6E" letter-spacing="1.5">ORGANIC MORPHOGENESIS IN GENERATIVE ARTIFICIAL INTELLIGENCE • DESIGN SPEC v1.0</text>
  </g>

  <!-- Left Card: Primary Mark & Geometry -->
  <rect x="120" y="180" width="1000" height="760" rx="16" fill="#FAF8F5" filter="url(#cardShadow)"/>
  
  <!-- Geometry Construction Guides -->
  <g transform="translate(620, 520)">
    <!-- Reference Construction Circles -->
    <circle cx="0" cy="0" r="235" fill="none" stroke="#DCD3C5" stroke-width="1" stroke-dasharray="4 6"/>
    <circle cx="0" cy="0" r="160" fill="none" stroke="#DCD3C5" stroke-width="1" stroke-dasharray="2 4"/>
    <circle cx="0" cy="0" r="85" fill="none" stroke="#DCD3C5" stroke-width="1" stroke-dasharray="2 4"/>
    
    <!-- Rotational Axes (120 deg) -->
    <line x1="0" y1="-260" x2="0" y2="260" stroke="#E3DACF" stroke-width="1"/>
    <line x1="-225" y1="130" x2="225" y2="-130" stroke="#E3DACF" stroke-width="1"/>
    <line x1="-225" y1="-130" x2="225" y2="130" stroke="#E3DACF" stroke-width="1"/>
    
    <!-- Organic Mark -->
    {mark_large}
    
    <!-- Geometric Labels -->
    <circle cx="0" cy="0" r="4" fill="#3A342E"/>
    <path d="M 0 0 L -110 -150 L -180 -150" fill="none" stroke="#A89B8B" stroke-width="1.2"/>
    <circle cx="-110" cy="-150" r="2.5" fill="#A89B8B"/>
    <text x="-185" y="-146" font-family="-apple-system, Arial, sans-serif" font-size="12" font-weight="600" fill="#4A4137" letter-spacing="1" text-anchor="end">CHIRAL NEXUS • 120°</text>
  </g>
  
  <text x="620" y="860" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', Arial, sans-serif" font-size="34" font-weight="500" fill="#1F1D1A" text-anchor="middle" letter-spacing="12">MORPHIC</text>
  <text x="620" y="895" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', Arial, sans-serif" font-size="12" font-weight="400" fill="#756B60" text-anchor="middle" letter-spacing="6">GENERATIVE INTELLIGENCE</text>

  <!-- Right Upper Card: Curated Neutral Palette -->
  <rect x="1160" y="180" width="1120" height="380" rx="16" fill="#FAF8F5" filter="url(#cardShadow)"/>
  <text x="1200" y="235" font-family="-apple-system, Arial, sans-serif" font-size="15" font-weight="600" fill="#1F1D1A" letter-spacing="2">01 • CURATED NEUTRAL COLOR SYSTEM</text>
  <text x="1200" y="260" font-family="-apple-system, Arial, sans-serif" font-size="12" font-weight="400" fill="#706456">Organic earth tones and warm mineral gradients calibrated for high-intellect resonance.</text>

  <!-- Color Swatches -->
  <g transform="translate(1200, 290)">
    <!-- Swatch 1 -->
    <rect x="0" y="0" width="160" height="130" rx="8" fill="#141312"/>
    <text x="12" y="170" font-family="-apple-system, Arial, sans-serif" font-size="13" font-weight="600" fill="#1F1D1A">Basalt Dark</text>
    <text x="12" y="190" font-family="-apple-system, Arial, sans-serif" font-size="11" fill="#706456">#141312 • Canvas Dark</text>

    <!-- Swatch 2 -->
    <rect x="175" y="0" width="160" height="130" rx="8" fill="#1F1D1A"/>
    <text x="187" y="170" font-family="-apple-system, Arial, sans-serif" font-size="13" font-weight="600" fill="#1F1D1A">Charcoal Umber</text>
    <text x="187" y="190" font-family="-apple-system, Arial, sans-serif" font-size="11" fill="#706456">#1F1D1A • Primary Text</text>

    <!-- Swatch 3 -->
    <rect x="350" y="0" width="160" height="130" rx="8" fill="#4A4137"/>
    <text x="362" y="170" font-family="-apple-system, Arial, sans-serif" font-size="13" font-weight="600" fill="#1F1D1A">Earth Graphite</text>
    <text x="362" y="190" font-family="-apple-system, Arial, sans-serif" font-size="11" fill="#706456">#4A4137 • Deep Shadow</text>

    <!-- Swatch 4 -->
    <rect x="525" y="0" width="160" height="130" rx="8" fill="#706456"/>
    <text x="537" y="170" font-family="-apple-system, Arial, sans-serif" font-size="13" font-weight="600" fill="#1F1D1A">Warm Taupe</text>
    <text x="537" y="190" font-family="-apple-system, Arial, sans-serif" font-size="11" fill="#706456">#706456 • Secondary</text>

    <!-- Swatch 5 -->
    <rect x="700" y="0" width="160" height="130" rx="8" fill="#A69887"/>
    <text x="712" y="170" font-family="-apple-system, Arial, sans-serif" font-size="13" font-weight="600" fill="#1F1D1A">Travertine Sand</text>
    <text x="712" y="190" font-family="-apple-system, Arial, sans-serif" font-size="11" fill="#706456">#A69887 • Highlight Lobe</text>

    <!-- Swatch 6 -->
    <rect x="875" y="0" width="160" height="130" rx="8" fill="#FAF8F5" stroke="#E0D7CB" stroke-width="1.5"/>
    <text x="887" y="170" font-family="-apple-system, Arial, sans-serif" font-size="13" font-weight="600" fill="#1F1D1A">Alabaster</text>
    <text x="887" y="190" font-family="-apple-system, Arial, sans-serif" font-size="11" fill="#706456">#FAF8F5 • Canvas Light</text>
  </g>

  <!-- Right Middle Card: Application Environments -->
  <rect x="1160" y="590" width="1120" height="350" rx="16" fill="#FAF8F5" filter="url(#cardShadow)"/>
  <text x="1200" y="640" font-family="-apple-system, Arial, sans-serif" font-size="15" font-weight="600" fill="#1F1D1A" letter-spacing="2">02 • APPLICATION ENVIRONMENTS (LIGHT &amp; DARK)</text>

  <!-- Dark Mode Preview Card -->
  <rect x="1200" y="665" width="500" height="235" rx="12" fill="#141312"/>
  <g transform="translate(1330, 782)">{mark_dark_small}</g>
  <text x="1460" y="780" font-family="-apple-system, BlinkMacSystemFont, Arial, sans-serif" font-size="28" font-weight="500" fill="#F5F2EC" letter-spacing="8">MORPHIC</text>
  <text x="1462" y="808" font-family="-apple-system, BlinkMacSystemFont, Arial, sans-serif" font-size="10" font-weight="400" fill="#9E9283" letter-spacing="4">GENERATIVE INTELLIGENCE</text>
  <text x="1220" y="880" font-family="-apple-system, Arial, sans-serif" font-size="10" fill="#695E50" letter-spacing="1">DARK THEME INTERFACE LOCKUP</text>

  <!-- App Icon Preview -->
  <g transform="translate(1760, 665)">
    <rect x="0" y="0" width="220" height="235" rx="12" fill="#EDE7DD"/>
    <rect x="50" y="30" width="120" height="120" rx="28" fill="#FAF8F5" filter="url(#cardShadow)"/>
    <g transform="translate(110, 90) scale(0.48)">{mark_light_small}</g>
    <text x="110" y="185" font-family="-apple-system, Arial, sans-serif" font-size="12" font-weight="600" fill="#1F1D1A" text-anchor="middle">iOS / App Icon</text>
    <text x="110" y="205" font-family="-apple-system, Arial, sans-serif" font-size="10" fill="#706456" text-anchor="middle">Squircle Matrix</text>
  </g>

  <!-- App Icon Dark Preview -->
  <g transform="translate(2020, 665)">
    <rect x="0" y="0" width="220" height="235" rx="12" fill="#24211E"/>
    <rect x="50" y="30" width="120" height="120" rx="28" fill="#141312" stroke="#3A332B" stroke-width="1"/>
    <g transform="translate(110, 90) scale(0.48)">{mark_dark_small}</g>
    <text x="110" y="185" font-family="-apple-system, Arial, sans-serif" font-size="12" font-weight="600" fill="#F5F2EC" text-anchor="middle">Favicon / Terminal</text>
    <text x="110" y="205" font-family="-apple-system, Arial, sans-serif" font-size="10" fill="#9E9283" text-anchor="middle">OLED Silhouette</text>
  </g>

  <!-- Bottom Panel: Design Philosophy & Typography Specs -->
  <rect x="120" y="970" width="2160" height="250" rx="16" fill="#FAF8F5" filter="url(#cardShadow)"/>
  <g transform="translate(160, 1015)">
    <text x="0" y="0" font-family="-apple-system, Arial, sans-serif" font-size="15" font-weight="600" fill="#1F1D1A" letter-spacing="2">03 • CONCEPT &amp; MORPHOMETRIC PHILOSOPHY</text>
    <text x="0" y="30" font-family="-apple-system, Arial, sans-serif" font-size="13" font-weight="400" fill="#4A4137" line-height="1.6">
      The MORPHIC identity embodies generative synthesis through fluid biomorphic topology. Three sculpted organic lobes coalesce around a dynamic negative-space nexus,
    </text>
    <text x="0" y="52" font-family="-apple-system, Arial, sans-serif" font-size="13" font-weight="400" fill="#4A4137">
      symbolizing the trinity of generative AI: Latent Space representation, Diffusion-driven morphogenesis, and Emergent synthetic cognition.
    </text>
    <text x="0" y="74" font-family="-apple-system, Arial, sans-serif" font-size="13" font-weight="400" fill="#4A4137">
      Rather than cold mechanical geometry or ephemeral digital clichés, MORPHIC uses timeless organic contours and warm neutral minerals (basalt, taupe, sand, alabaster)
    </text>
    <text x="0" y="96" font-family="-apple-system, Arial, sans-serif" font-size="13" font-weight="400" fill="#4A4137">
      to reflect artificial intelligence as a natural evolutionary continuum of the living universe.
    </text>
  </g>

  <g transform="translate(1360, 1015)">
    <text x="0" y="0" font-family="-apple-system, Arial, sans-serif" font-size="15" font-weight="600" fill="#1F1D1A" letter-spacing="2">04 • TYPOGRAPHIC ARCHITECTURE</text>
    <text x="0" y="30" font-family="-apple-system, Arial, sans-serif" font-size="12" font-weight="600" fill="#706456" letter-spacing="1">PRIMARY WORDMARK:</text>
    <text x="180" y="30" font-family="-apple-system, Arial, sans-serif" font-size="12" fill="#1F1D1A">SF Pro Display / Geometric Humanist • Medium 500 • Tracking +14 • Optical Kerning</text>
    
    <text x="0" y="60" font-family="-apple-system, Arial, sans-serif" font-size="12" font-weight="600" fill="#706456" letter-spacing="1">SUB-DESCRIPTOR:</text>
    <text x="180" y="60" font-family="-apple-system, Arial, sans-serif" font-size="12" fill="#1F1D1A">SF Pro Text / Neutral Grotesque • Regular 400 • Tracking +7 • All Caps</text>

    <text x="0" y="90" font-family="-apple-system, Arial, sans-serif" font-size="12" font-weight="600" fill="#706456" letter-spacing="1">CURVATURE CONTINUITY:</text>
    <text x="180" y="90" font-family="-apple-system, Arial, sans-serif" font-size="12" fill="#1F1D1A">G2 Continuous Catmull-Rom Cubic Bézier Splines • 3-Fold Chiral Symmetry</text>
  </g>
  
  <!-- Footer -->
  <text x="120" y="1285" font-family="-apple-system, Arial, sans-serif" font-size="12" fill="#8C7F6E">© MORPHIC LABS INC. • CONFIDENTIAL &amp; PROPRIETARY • GENERATIVE AI SYSTEMS</text>
  <text x="2280" y="1285" font-family="-apple-system, Arial, sans-serif" font-size="12" fill="#8C7F6E" text-anchor="end">SVG SPECIFICATION RELEASE • ALL RIGHTS RESERVED</text>
</svg>"""
    with open(filepath, "w") as f:
        f.write(svg)

def build_all():
    os.makedirs("output", exist_ok=True)
    os.makedirs("src", exist_ok=True)
    
    print("Generating vector SVG assets...")
    generate_primary_svg("output/logo_primary.svg")
    generate_horizontal_svg("output/logo_horizontal.svg")
    generate_isolated_mark_svg("output/logo_mark_isolated.svg")
    generate_dark_mode_svg("output/logo_dark_mode.svg")
    generate_brand_sheet_svg("brand_sheet_temp.svg")
    
    print("Rendering high-resolution raster assets...")
    subprocess.run(["sips", "-s", "format", "png", "output/logo_primary.svg", "--out", "output/logo_primary.png"], check=True)
    subprocess.run(["sips", "-s", "format", "png", "output/logo_dark_mode.svg", "--out", "output/logo_dark_mode.png"], check=True)
    subprocess.run(["sips", "-s", "format", "png", "brand_sheet_temp.svg", "--out", "output/brand_sheet.png"], check=True)
    
    if os.path.exists("brand_sheet_temp.svg"):
        os.remove("brand_sheet_temp.svg")
        
    print("Static assets build complete!")

if __name__ == "__main__":
    build_all()
