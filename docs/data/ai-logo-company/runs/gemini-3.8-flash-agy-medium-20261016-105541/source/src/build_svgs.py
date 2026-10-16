import math
import os
from brand_engine import generate_trefoil_quads, quads_to_svg_paths

def build_all_svgs(out_dir="output"):
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Primary Dark Logo (800 x 800)
    # cx=400, cy=300. R_max with scale=80, ribbon_w=36 is 2.598*80 + 40 = 248 px.
    # Top edge: 300 - 248 = 52. Bottom edge: 300 + 248 = 548.
    # Text baseline at y=655 and y=695.
    quads_dark = generate_trefoil_quads(cx=400, cy=300, scale=80.0, ribbon_w=36.0, is_dark=True)
    paths_dark = quads_to_svg_paths(quads_dark)
    
    svg_primary_dark = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <defs>
    <radialGradient id="darkBgGlow" cx="50%" cy="38%" r="65%">
      <stop offset="0%" stop-color="#1B1917" />
      <stop offset="100%" stop-color="#11100F" />
    </radialGradient>
    <filter id="markShadowDark" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="16" stdDeviation="22" flood-color="#000000" flood-opacity="0.45" />
    </filter>
  </defs>

  <!-- Background -->
  <rect width="800" height="800" fill="url(#darkBgGlow)" />

  <!-- Subtle Generative Coordinate Rings -->
  <circle cx="400" cy="300" r="215" fill="none" stroke="rgba(247, 242, 234, 0.08)" stroke-width="1.2" stroke-dasharray="3 5" />
  <circle cx="400" cy="300" r="260" fill="none" stroke="rgba(247, 242, 234, 0.04)" stroke-width="1" />

  <!-- The Organic Mark -->
  <g filter="url(#markShadowDark)">
    {"".join(paths_dark)}
  </g>

  <!-- Brand Typography -->
  <g text-anchor="middle">
    <text x="400" y="650" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" font-size="36" font-weight="500" letter-spacing="12" fill="#F7F2EA">KHORA</text>
    <text x="400" y="688" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif" font-size="12" font-weight="400" letter-spacing="5" fill="#9D9487">GENERATIVE INTELLIGENCE</text>
  </g>
</svg>"""

    with open(os.path.join(out_dir, "logo-primary-dark.svg"), "w") as f:
        f.write(svg_primary_dark)

    # 2. Primary Light Logo (800 x 800)
    quads_light = generate_trefoil_quads(cx=400, cy=300, scale=80.0, ribbon_w=36.0, is_dark=False)
    paths_light = quads_to_svg_paths(quads_light)
    
    svg_primary_light = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <defs>
    <radialGradient id="lightBgGlow" cx="50%" cy="38%" r="65%">
      <stop offset="0%" stop-color="#FFFFFF" />
      <stop offset="100%" stop-color="#FAF7F2" />
    </radialGradient>
    <filter id="markShadowLight" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="16" stdDeviation="22" flood-color="#231F1C" flood-opacity="0.12" />
    </filter>
  </defs>

  <!-- Background -->
  <rect width="800" height="800" fill="url(#lightBgGlow)" />

  <!-- Subtle Generative Coordinate Rings -->
  <circle cx="400" cy="300" r="215" fill="none" stroke="rgba(35, 31, 28, 0.06)" stroke-width="1.2" stroke-dasharray="3 5" />
  <circle cx="400" cy="300" r="260" fill="none" stroke="rgba(35, 31, 28, 0.03)" stroke-width="1" />

  <!-- The Organic Mark -->
  <g filter="url(#markShadowLight)">
    {"".join(paths_light)}
  </g>

  <!-- Brand Typography -->
  <g text-anchor="middle">
    <text x="400" y="650" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" font-size="36" font-weight="500" letter-spacing="12" fill="#1E1C1A">KHORA</text>
    <text x="400" y="688" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif" font-size="12" font-weight="400" letter-spacing="5" fill="#7A7268">GENERATIVE INTELLIGENCE</text>
  </g>
</svg>"""

    with open(os.path.join(out_dir, "logo-primary-light.svg"), "w") as f:
        f.write(svg_primary_light)

    # 3. Horizontal Lockup (1000 x 300)
    # cx=170, cy=150, scale=35.0, ribbon_w=16.0
    # R_max = 2.598 * 35 + 18 = 109 px.
    # Bounds: x in [61, 279], y in [41, 259]. Fits within 300px height.
    quads_horiz = generate_trefoil_quads(cx=170, cy=150, scale=35.0, ribbon_w=16.0, is_dark=False)
    paths_horiz = quads_to_svg_paths(quads_horiz)
    
    svg_horizontal = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" width="1000" height="300">
  <defs>
    <filter id="markShadowHoriz" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#231F1C" flood-opacity="0.10" />
    </filter>
  </defs>

  <rect width="1000" height="300" fill="#FAF7F2" rx="20" />

  <!-- Mark -->
  <g filter="url(#markShadowHoriz)">
    {"".join(paths_horiz)}
  </g>

  <!-- Vertical subtle divider -->
  <line x1="335" y1="80" x2="335" y2="220" stroke="rgba(35, 31, 28, 0.12)" stroke-width="1.5" />

  <!-- Typography -->
  <g transform="translate(385, 0)">
    <text x="0" y="152" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" font-size="52" font-weight="500" letter-spacing="14" fill="#1E1C1A">KHORA</text>
    <text x="0" y="196" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif" font-size="14.5" font-weight="400" letter-spacing="6" fill="#7A7268">GENERATIVE INTELLIGENCE</text>
  </g>
</svg>"""

    with open(os.path.join(out_dir, "logo-horizontal.svg"), "w") as f:
        f.write(svg_horizontal)

    # 4. Pure Standalone Mark (600 x 600, transparent)
    # cx=300, cy=300, scale=78.0, ribbon_w=35.0
    # R_max = 2.598 * 78 + 39 = 241 px. Bounds in [59, 541].
    quads_mark = generate_trefoil_quads(cx=300, cy=300, scale=78.0, ribbon_w=35.0, is_dark=True)
    paths_mark = quads_to_svg_paths(quads_mark)
    
    svg_mark = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">
  <defs>
    <filter id="pureMarkShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="18" flood-color="#000000" flood-opacity="0.35" />
    </filter>
  </defs>
  <g filter="url(#pureMarkShadow)">
    {"".join(paths_mark)}
  </g>
</svg>"""

    with open(os.path.join(out_dir, "logo-mark.svg"), "w") as f:
        f.write(svg_mark)

    # 5. App Icon Badge (512 x 512 squircle)
    # cx=256, cy=256, scale=54.0, ribbon_w=24.0
    # R_max = 2.598 * 54 + 27 = 167 px. Bounds in [89, 423].
    quads_badge = generate_trefoil_quads(cx=256, cy=256, scale=54.0, ribbon_w=24.0, is_dark=True)
    paths_badge = quads_to_svg_paths(quads_badge)
    
    svg_badge = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="badgeBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#24211E" />
      <stop offset="50%" stop-color="#181615" />
      <stop offset="100%" stop-color="#0E0D0C" />
    </linearGradient>
    <linearGradient id="badgeBorder" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="rgba(247, 242, 234, 0.28)" />
      <stop offset="100%" stop-color="rgba(247, 242, 234, 0.06)" />
    </linearGradient>
    <filter id="badgeShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#000" flood-opacity="0.55" />
    </filter>
  </defs>

  <!-- Squircle Base -->
  <rect x="24" y="24" width="464" height="464" rx="112" fill="url(#badgeBg)" stroke="url(#badgeBorder)" stroke-width="2" />
  
  <!-- Subtle Internal Coordinate Ring -->
  <circle cx="256" cy="256" r="175" fill="none" stroke="rgba(247, 242, 234, 0.08)" stroke-width="1.2" stroke-dasharray="3 5" />

  <!-- Trefoil Mark -->
  <g filter="url(#badgeShadow)">
    {"".join(paths_badge)}
  </g>
</svg>"""

    with open(os.path.join(out_dir, "logo-badge.svg"), "w") as f:
        f.write(svg_badge)

    print("Regenerated all 5 SVGs with perfect scaling")

if __name__ == "__main__":
    build_all_svgs("output")
