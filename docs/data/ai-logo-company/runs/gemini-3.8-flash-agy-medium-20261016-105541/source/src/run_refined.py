import math
from generate_prototypes import catmull_rom_to_bezier

def test_botanical_aperture(filename="src/proto_d.svg"):
    """
    Refined 3-form organic aperture.
    Sleek, botanical, fluid curves like a blooming calla lily or river pebble vortex.
    """
    cx, cy = 400, 320
    
    # Let's define one sleek petal:
    # Starts at center inner rim (r=28, theta=30),
    # swoops outwards smoothly along inner flank: (r=80, theta=45), (r=150, theta=70),
    # reaches outer crest: (r=210, theta=105), (r=220, theta=125), (r=190, theta=150),
    # sweeps back along outer boundary: (r=130, theta=175), (r=70, theta=185), (r=30, theta=150),
    # smoothly connects back to inner rim: (r=18, theta=90)
    petal_pts = [
        (24, 30),
        (75, 42),
        (145, 68),
        (195, 98),
        (215, 128),
        (190, 155),
        (140, 172),
        (90, 168),
        (50, 140),
        (24, 85),
    ]
    
    def get_petal(rot):
        pts = []
        for r, deg in petal_pts:
            rad = math.radians(deg + rot)
            pts.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
        return catmull_rom_to_bezier(pts)

    p1 = get_petal(0)
    p2 = get_petal(120)
    p3 = get_petal(240)
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <defs>
    <linearGradient id="d1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#36322E" />
      <stop offset="50%" stop-color="#554E47" />
      <stop offset="100%" stop-color="#7A7066" />
    </linearGradient>
    <linearGradient id="d2" x1="100%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#4A443E" />
      <stop offset="50%" stop-color="#6E655C" />
      <stop offset="100%" stop-color="#9C9184" />
    </linearGradient>
    <linearGradient id="d3" x1="50%" y1="100%" x2="50%" y2="0%">
      <stop offset="0%" stop-color="#24211E" />
      <stop offset="50%" stop-color="#423C36" />
      <stop offset="100%" stop-color="#6B6258" />
    </linearGradient>
    <filter id="shadowD" x="-15%" y="-15%" width="130%" height="130%">
      <feDropShadow dx="0" dy="10" stdDeviation="16" flood-color="#1E1C1A" flood-opacity="0.12" />
    </filter>
  </defs>
  <rect width="800" height="800" fill="#F8F5F0" />
  
  <!-- Subtle ambient halo -->
  <circle cx="{cx}" cy="{cy}" r="220" fill="none" stroke="rgba(120, 110, 100, 0.08)" stroke-width="1.5" stroke-dasharray="4 6" />
  <circle cx="{cx}" cy="{cy}" r="260" fill="none" stroke="rgba(120, 110, 100, 0.05)" stroke-width="1" />

  <g filter="url(#shadowD)">
    <path d="{p1}" fill="url(#d1)" opacity="0.95" style="mix-blend-mode: multiply;" />
    <path d="{p2}" fill="url(#d2)" opacity="0.95" style="mix-blend-mode: multiply;" />
    <path d="{p3}" fill="url(#d3)" opacity="0.95" style="mix-blend-mode: multiply;" />
  </g>
  
  <!-- Central generative jewel / pearl -->
  <circle cx="{cx}" cy="{cy}" r="15" fill="#C9A37A" />
  <circle cx="{cx - 3}" cy="{cy - 3}" r="4" fill="#E8D5BF" opacity="0.7" />

  <text x="400" y="650" font-family="system-ui, -apple-system, sans-serif" font-size="34" font-weight="500" letter-spacing="11" fill="#1C1A18" text-anchor="middle">FORMA</text>
  <text x="400" y="685" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="400" letter-spacing="4.5" fill="#787168" text-anchor="middle">GENERATIVE INTELLIGENCE</text>
</svg>"""
    with open(filename, "w") as f:
        f.write(svg)

def test_pebble_synthesis(filename="src/proto_e.svg"):
    """
    Refined Proto B: The Noguchi Synthesis.
    Two sculpted river pebbles embracing with organic negative space.
    One in deep warm charcoal, one in luminous warm taupe/sand.
    """
    cx, cy = 400, 320
    
    # Left pebble: a soft, beautiful organic bean/pebble
    pts_left = [
        (cx - 30, cy - 200),
        (cx - 130, cy - 160),
        (cx - 195, cy - 70),
        (cx - 205, cy + 40),
        (cx - 160, cy + 140),
        (cx - 80, cy + 195),
        (cx + 10, cy + 190),
        (cx - 20, cy + 100),
        (cx - 50, cy + 10),
        (cx - 40, cy - 80),
        (cx - 10, cy - 160),
    ]
    
    # Right pebble: complementary organic sweep embracing the left
    pts_right = [
        (cx + 20, cy - 190),
        (cx + 120, cy - 160),
        (cx + 190, cy - 80),
        (cx + 205, cy + 20),
        (cx + 165, cy + 130),
        (cx + 85, cy + 190),
        (cx + 20, cy + 200),
        (cx + 5, cy + 130),
        (cx + 35, cy + 40),
        (cx + 30, cy - 50),
        (cx + 10, cy - 130),
    ]
    
    p_left = catmull_rom_to_bezier(pts_left)
    p_right = catmull_rom_to_bezier(pts_right)
    
    # Core seed nestled between them
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <defs>
    <linearGradient id="pLeftGrad" x1="20%" y1="0%" x2="80%" y2="100%">
      <stop offset="0%" stop-color="#262320" />
      <stop offset="100%" stop-color="#48423C" />
    </linearGradient>
    <linearGradient id="pRightGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#7C7164" />
      <stop offset="100%" stop-color="#B2A595" />
    </linearGradient>
    <filter id="shadowE" x="-15%" y="-15%" width="130%" height="130%">
      <feDropShadow dx="0" dy="12" stdDeviation="18" flood-color="#141210" flood-opacity="0.14" />
    </filter>
  </defs>
  <rect width="800" height="800" fill="#F8F6F2" />
  
  <g filter="url(#shadowE)">
    <path d="{p_left}" fill="url(#pLeftGrad)" />
    <path d="{p_right}" fill="url(#pRightGrad)" opacity="0.95" style="mix-blend-mode: multiply;" />
  </g>
  
  <circle cx="{cx}" cy="{cy}" r="15" fill="#BF9B75" />
  <circle cx="{cx - 2}" cy="{cy - 2}" r="4" fill="#F0E3D3" opacity="0.75" />

  <text x="400" y="650" font-family="system-ui, -apple-system, sans-serif" font-size="34" font-weight="500" letter-spacing="11" fill="#1C1A18" text-anchor="middle">LATENT</text>
  <text x="400" y="685" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="400" letter-spacing="4.5" fill="#787168" text-anchor="middle">ORGANIC INTELLIGENCE</text>
</svg>"""
    with open(filename, "w") as f:
        f.write(svg)

test_botanical_aperture()
test_pebble_synthesis()
print("Generated proto_d and proto_e")
