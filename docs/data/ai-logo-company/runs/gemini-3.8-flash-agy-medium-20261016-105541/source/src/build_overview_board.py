import math
import os
import subprocess
import shutil
from brand_engine import generate_trefoil_quads, quads_to_svg_paths

def build_presentation_board():
    W, H = 1600, 1600
    
    # 1. Dark hero card (690 x 520): center at (345, 240), scale=60, ribbon_w=27
    q_dark = generate_trefoil_quads(cx=345, cy=240, scale=60.0, ribbon_w=27.0, is_dark=True)
    p_dark = "".join(quads_to_svg_paths(q_dark))
    
    # 2. Light hero card (690 x 520): center at (345, 240), scale=60, ribbon_w=27
    q_light = generate_trefoil_quads(cx=345, cy=240, scale=60.0, ribbon_w=27.0, is_dark=False)
    p_light = "".join(quads_to_svg_paths(q_light))
    
    # 3. Schematic mark in morphology card: center at (345, 255), scale=42, ribbon_w=19
    q_schem = generate_trefoil_quads(cx=345, cy=255, scale=42.0, ribbon_w=19.0, is_dark=False)
    p_schem = "".join(quads_to_svg_paths(q_schem))
    
    # 4. App badge in system card: center at (60, 60), scale=18, ribbon_w=8.0
    q_badge = generate_trefoil_quads(cx=60, cy=60, scale=18.0, ribbon_w=8.0, is_dark=True)
    p_badge = "".join(quads_to_svg_paths(q_badge))

    # Swatches data
    swatches = [
        ("Warm Alabaster", "#FAF7F2", "#1E1C1A", "Light Canvas &amp; Sheen"),
        ("Raw Oat", "#DFD5C6", "#2C2825", "Luminous Highlight"),
        ("Mineral Sand", "#BDB1A2", "#2C2825", "Midtone Transition"),
        ("Smoked Driftwood", "#7D7366", "#FAF7F2", "Ambient Balance"),
        ("Warm Umber", "#34302C", "#FAF7F2", "Occlusion Shadow"),
        ("Deep Obsidian", "#121110", "#FAF7F2", "Dark Ground &amp; Void"),
    ]
    
    swatch_svg = []
    swatch_w = 190
    swatch_h = 100
    for idx, (name, hex_code, txt_c, role) in enumerate(swatches):
        col_idx = idx % 3
        row_idx = idx // 3
        sx = 36 + col_idx * 205
        sy = 125 + row_idx * 115
        swatch_svg.append(f"""
        <g transform="translate({sx}, {sy})">
          <rect width="{swatch_w}" height="{swatch_h}" rx="12" fill="{hex_code}" stroke="rgba(0,0,0,0.06)" stroke-width="1" />
          <text x="16" y="32" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="13" font-weight="600" fill="{txt_c}">{name}</text>
          <text x="16" y="55" font-family="'SF Mono', Menlo, monospace" font-size="12" font-weight="500" fill="{txt_c}" opacity="0.85">{hex_code}</text>
          <text x="16" y="80" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="10.5" font-weight="400" fill="{txt_c}" opacity="0.7">{role}</text>
        </g>
        """)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <filter id="boardCardShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="12" stdDeviation="18" flood-color="#1E1C1A" flood-opacity="0.06" />
    </filter>
    <filter id="markShadowD" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#000" flood-opacity="0.45" />
    </filter>
    <filter id="markShadowL" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#231F1C" flood-opacity="0.12" />
    </filter>
  </defs>

  <!-- Master Canvas Background: Architectural Oat/Linen -->
  <rect width="{W}" height="{H}" fill="#F4EFEA" />

  <!-- Top Header Bar -->
  <g transform="translate(80, 80)">
    <text x="0" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="12" font-weight="600" letter-spacing="4.5" fill="#8C8275">BRAND SYSTEM &amp; SPECIFICATION</text>
    <text x="0" y="42" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="38" font-weight="600" letter-spacing="9" fill="#1C1A18">KHORA AI</text>
    <text x="360" y="42" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="16" font-weight="400" fill="#756D62">/   Generative Intelligence • Organic Topology • Neutral Harmonics</text>
  </g>
  <line x1="80" y1="150" x2="1520" y2="150" stroke="rgba(35, 31, 28, 0.12)" stroke-width="1.5" />

  <!-- ================= ROW 1: PRIMARY LOCKUPS ================= -->
  
  <!-- Dark Mode Hero Card (Left) -->
  <g transform="translate(80, 185)" filter="url(#boardCardShadow)">
    <rect width="690" height="520" rx="22" fill="#121110" />
    <circle cx="345" cy="240" r="185" fill="none" stroke="rgba(247, 242, 234, 0.08)" stroke-width="1.2" stroke-dasharray="3 5" />
    <circle cx="345" cy="240" r="225" fill="none" stroke="rgba(247, 242, 234, 0.04)" stroke-width="1" />
    
    <g filter="url(#markShadowD)">
      {p_dark}
    </g>
    
    <text x="345" y="450" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="30" font-weight="500" letter-spacing="10" fill="#F7F2EA" text-anchor="middle">KHORA</text>
    <text x="345" y="480" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="11" font-weight="400" letter-spacing="4" fill="#9D9487" text-anchor="middle">PRIMARY DARK LOCKUP</text>
  </g>

  <!-- Light Mode Hero Card (Right) -->
  <g transform="translate(830, 185)" filter="url(#boardCardShadow)">
    <rect width="690" height="520" rx="22" fill="#FAF7F2" stroke="rgba(35, 31, 28, 0.06)" stroke-width="1" />
    <circle cx="345" cy="240" r="185" fill="none" stroke="rgba(35, 31, 28, 0.06)" stroke-width="1.2" stroke-dasharray="3 5" />
    <circle cx="345" cy="240" r="225" fill="none" stroke="rgba(35, 31, 28, 0.03)" stroke-width="1" />
    
    <g filter="url(#markShadowL)">
      {p_light}
    </g>
    
    <text x="345" y="450" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="30" font-weight="500" letter-spacing="10" fill="#1E1C1A" text-anchor="middle">KHORA</text>
    <text x="345" y="480" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="11" font-weight="400" letter-spacing="4" fill="#7A7268" text-anchor="middle">PRIMARY LIGHT LOCKUP</text>
  </g>

  <!-- ================= ROW 2: PALETTE & MORPHOLOGY ================= -->

  <!-- Left: Neutral Color System & Typography -->
  <g transform="translate(80, 745)">
    <rect width="690" height="770" rx="22" fill="#FAF7F2" filter="url(#boardCardShadow)" />
    <text x="40" y="46" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="12" font-weight="600" letter-spacing="3.5" fill="#8C8275">TONAL PALETTE</text>
    <text x="40" y="76" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="22" font-weight="600" fill="#1C1A18">Architectural Warm Neutrals</text>
    <text x="40" y="102" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="13" fill="#756D62">Tactile mineral tones inspired by raw stone, porcelain, and sumi ink.</text>
    
    <!-- Swatches -->
    <g transform="translate(4, 0)">
      {"".join(swatch_svg)}
    </g>

    <!-- Typography Specifications Divider -->
    <line x1="40" y1="390" x2="650" y2="390" stroke="rgba(35, 31, 28, 0.1)" stroke-width="1" />
    
    <text x="40" y="430" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="12" font-weight="600" letter-spacing="3.5" fill="#8C8275">TYPOGRAPHIC SYSTEM</text>
    
    <text x="40" y="480" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="34" font-weight="500" letter-spacing="12" fill="#1E1C1A">KHORA</text>
    <text x="40" y="512" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="13" font-weight="400" letter-spacing="4.5" fill="#7A7268">GENERATIVE INTELLIGENCE</text>
    
    <g transform="translate(40, 560)" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="13" fill="#585148">
      <text x="0" y="0">• Wordmark: Bespoke Geometric Humanist Sans, optical kerning +12%</text>
      <text x="0" y="26">• Subtitle Descriptor: Precision Monospace/Technical Sans, tracking +4.5</text>
      <text x="0" y="52">• Clearspace: Minimum 1.5× mark radius perimeter on all collateral</text>
      <text x="0" y="78">• Hierarchy: High contrast pairing of warm charcoal with muted driftwood</text>
      <text x="0" y="104">• Scale Range: Fully legible from 16px favicon up to monumental signage</text>
    </g>
  </g>

  <!-- Right: Topology & System Adaptation -->
  <g transform="translate(830, 745)">
    <rect width="690" height="770" rx="22" fill="#FAF7F2" filter="url(#boardCardShadow)" />
    
    <text x="40" y="46" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="12" font-weight="600" letter-spacing="3.5" fill="#8C8275">TOPOLOGY &amp; MORPHOLOGY</text>
    <text x="40" y="76" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="22" font-weight="600" fill="#1C1A18">The Continuous Latent Trefoil</text>

    <!-- Schematic Illustration -->
    <g>
      <!-- Construction geometric overlays -->
      <circle cx="345" cy="255" r="125" fill="none" stroke="#C49A74" stroke-width="1.2" stroke-dasharray="3 4" opacity="0.65" />
      <circle cx="345" cy="255" r="155" fill="none" stroke="#8C8275" stroke-width="0.8" stroke-dasharray="4 4" opacity="0.4" />
      
      <!-- 120 deg symmetry lines -->
      <line x1="345" y1="255" x2="345" y2="120" stroke="#C49A74" stroke-width="1.2" stroke-dasharray="3 4" opacity="0.55" />
      <line x1="345" y1="255" x2="462" y2="322" stroke="#C49A74" stroke-width="1.2" stroke-dasharray="3 4" opacity="0.55" />
      <line x1="345" y1="255" x2="228" y2="322" stroke="#C49A74" stroke-width="1.2" stroke-dasharray="3 4" opacity="0.55" />
      
      {p_schem}
    </g>

    <g transform="translate(40, 420)" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="12.5" fill="#585148">
      <text x="0" y="0">• Infinite 1-manifold: Continuous G2 curvature modeling latent manifold transitions</text>
      <text x="0" y="24">• Three-fold rotational harmony: Triad of Prompt, Representation, and Synthesis</text>
      <text x="0" y="48">• Analytical ambient occlusion: Volumetric depth without rigid tech clichés</text>
      <text x="0" y="72">• Central focal void: The formless Chôra / Latent space of emergent potential</text>
    </g>

    <!-- Divider -->
    <line x1="40" y1="520" x2="650" y2="520" stroke="rgba(35, 31, 28, 0.1)" stroke-width="1" />

    <!-- System Adaptation -->
    <text x="40" y="556" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="12" font-weight="600" letter-spacing="3.5" fill="#8C8275">SYSTEM ADAPTATION</text>
    <text x="40" y="582" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="18" font-weight="600" fill="#1C1A18">App Icon &amp; Favicon Badge</text>

    <!-- Mini Squircle Icon -->
    <g transform="translate(40, 615)">
      <rect width="120" height="120" rx="30" fill="#121110" stroke="rgba(247,242,234,0.18)" stroke-width="1.5" />
      <g>
        {p_badge}
      </g>
    </g>

    <g transform="translate(190, 645)" font-family="-apple-system, BlinkMacSystemFont, 'Inter', sans-serif" font-size="13" fill="#585148">
      <text x="0" y="0" font-weight="600" fill="#1C1A18">Continuous Curvature Squircle</text>
      <text x="0" y="24">Engineered for iOS / macOS system docks,</text>
      <text x="0" y="46">high-density mobile screens, and social</text>
      <text x="0" y="68">brand avatars across all digital surfaces.</text>
    </g>
  </g>
</svg>"""

    with open("src/presentation_board.svg", "w") as f:
        f.write(svg)
        
    print("Presentation SVG board created at src/presentation_board.svg")
    subprocess.run(["qlmanage", "-t", "-s", "1600", "-o", "src/", "src/presentation_board.svg"], check=True)
    
    src_png = "src/presentation_board.svg.png"
    dst_png = "output/brand-overview.png"
    if os.path.exists(src_png):
        shutil.copyfile(src_png, dst_png)
        print(f"Copied {src_png} to {dst_png}")

if __name__ == "__main__":
    build_presentation_board()
