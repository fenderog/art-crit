import math
import os

def create_morphic_svg(theme="light"):
    """
    Creates the primary full brand lockup SVG.
    Company: "MORPHIC" - Generative Intelligence
    Concept: Intersecting organic fluid blobs forming an emergent continuum of thought and creativity.
    Palette: Refined neutral luxury palette (warm alabaster, bone, sand, cashmere, warm taupe, charcoal, umber).
    """
    if theme == "light":
        bg_start = "#FAF8F5"
        bg_mid = "#F2ECE4"
        bg_end = "#E5DCD2"
        text_primary = "#2A2521"
        text_secondary = "#7D7268"
        accent_line = "#B5A799"
        orbit_stroke = "#C8BCB0"
        pod1_stops = [("#3A332C", "1.0"), ("#24201C", "1.0"), ("#151311", "1.0")] # Deep Espresso/Charcoal
        pod2_stops = [("#8F8073", "0.92"), ("#736559", "0.92"), ("#564A40", "0.92")] # Warm Taupe
        pod3_stops = [("#C4B5A5", "0.95"), ("#AD9D8D", "0.95"), ("#8C7C6D", "0.95")] # Cashmere / Dune
        pod4_stops = [("#E8DFD5", "0.88"), ("#D5C9BC", "0.88"), ("#BAACA0", "0.88")] # Soft Bone / Oat
        core_stops = [("#B89F82", "0.98"), ("#8F755A", "0.98"), ("#5B4835", "1.0")] # Warm Raw Umber & Gold Ochre
        inner_void = "#FAF8F5"
        filament_white = "rgba(255, 255, 255, 0.75)"
        filament_dark = "rgba(50, 42, 36, 0.45)"
        shadow_opacity = "0.14"
        grid_opacity = "0.35"
    else: # dark theme
        bg_start = "#1A1816"
        bg_mid = "#131110"
        bg_end = "#0C0B0A"
        text_primary = "#F5F0E8"
        text_secondary = "#A3978A"
        accent_line = "#685E54"
        orbit_stroke = "#38322B"
        pod1_stops = [("#423B34", "1.0"), ("#2E2722", "1.0"), ("#1A1714", "1.0")]
        pod2_stops = [("#9B8C7E", "0.85"), ("#7B6C60", "0.85"), ("#584C42", "0.85")]
        pod3_stops = [("#C9BCAE", "0.9"), ("#AFA092", "0.9"), ("#8E7F72", "0.9")]
        pod4_stops = [("#EADFD5", "0.75"), ("#CFC2B4", "0.75"), ("#9F9184", "0.75")]
        core_stops = [("#D4B896", "0.95"), ("#AA8B6B", "0.95"), ("#6B543D", "1.0")]
        inner_void = "#1A1816"
        filament_white = "rgba(255, 255, 255, 0.85)"
        filament_dark = "rgba(215, 200, 185, 0.35)"
        shadow_opacity = "0.35"
        grid_opacity = "0.2"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="100%" height="100%">
  <defs>
    <!-- Background Gradient -->
    <radialGradient id="bgGrad_{theme}" cx="50%" cy="42%" r="70%">
      <stop offset="0%" stop-color="{bg_start}" />
      <stop offset="65%" stop-color="{bg_mid}" />
      <stop offset="100%" stop-color="{bg_end}" />
    </radialGradient>

    <!-- Organic Pod Gradients -->
    <linearGradient id="gradStone_{theme}" x1="20%" y1="10%" x2="85%" y2="90%">
      <stop offset="0%" stop-color="{pod1_stops[0][0]}" stop-opacity="{pod1_stops[0][1]}" />
      <stop offset="50%" stop-color="{pod1_stops[1][0]}" stop-opacity="{pod1_stops[1][1]}" />
      <stop offset="100%" stop-color="{pod1_stops[2][0]}" stop-opacity="{pod1_stops[2][1]}" />
    </linearGradient>

    <linearGradient id="gradTaupe_{theme}" x1="15%" y1="15%" x2="85%" y2="85%">
      <stop offset="0%" stop-color="{pod2_stops[0][0]}" stop-opacity="{pod2_stops[0][1]}" />
      <stop offset="50%" stop-color="{pod2_stops[1][0]}" stop-opacity="{pod2_stops[1][1]}" />
      <stop offset="100%" stop-color="{pod2_stops[2][0]}" stop-opacity="{pod2_stops[2][1]}" />
    </linearGradient>

    <linearGradient id="gradCashmere_{theme}" x1="10%" y1="20%" x2="90%" y2="80%">
      <stop offset="0%" stop-color="{pod3_stops[0][0]}" stop-opacity="{pod3_stops[0][1]}" />
      <stop offset="50%" stop-color="{pod3_stops[1][0]}" stop-opacity="{pod3_stops[1][1]}" />
      <stop offset="100%" stop-color="{pod3_stops[2][0]}" stop-opacity="{pod3_stops[2][1]}" />
    </linearGradient>

    <linearGradient id="gradOat_{theme}" x1="25%" y1="10%" x2="75%" y2="90%">
      <stop offset="0%" stop-color="{pod4_stops[0][0]}" stop-opacity="{pod4_stops[0][1]}" />
      <stop offset="50%" stop-color="{pod4_stops[1][0]}" stop-opacity="{pod4_stops[1][1]}" />
      <stop offset="100%" stop-color="{pod4_stops[2][0]}" stop-opacity="{pod4_stops[2][1]}" />
    </linearGradient>

    <radialGradient id="gradCore_{theme}" cx="42%" cy="38%" r="60%">
      <stop offset="0%" stop-color="{core_stops[0][0]}" stop-opacity="{core_stops[0][1]}" />
      <stop offset="55%" stop-color="{core_stops[1][0]}" stop-opacity="{core_stops[1][1]}" />
      <stop offset="100%" stop-color="{core_stops[2][0]}" stop-opacity="{core_stops[2][1]}" />
    </radialGradient>

    <!-- Natural Soft Shadow -->
    <filter id="shadowOrganic_{theme}" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="20" stdDeviation="28" flood-color="#14100D" flood-opacity="{shadow_opacity}" />
    </filter>

    <!-- Subtle Ambient Texture Mask / Pattern -->
    <pattern id="noise_{theme}" width="40" height="40" patternUnits="userSpaceOnUse">
      <circle cx="20" cy="20" r="0.6" fill="{text_secondary}" opacity="0.3" />
      <circle cx="5" cy="12" r="0.4" fill="{text_secondary}" opacity="0.2" />
      <circle cx="35" cy="28" r="0.5" fill="{text_secondary}" opacity="0.25" />
    </pattern>
  </defs>

  <!-- Background Layer -->
  <rect width="1200" height="900" fill="url(#bgGrad_{theme})" />
  <rect width="1200" height="900" fill="url(#noise_{theme})" opacity="0.8" />

  <!-- Ambient Generative Field Lines (Constellation & Growth Resonance) -->
  <g opacity="{grid_opacity}" fill="none">
    <circle cx="600" cy="360" r="320" stroke="{orbit_stroke}" stroke-width="1.2" stroke-dasharray="3 9" />
    <ellipse cx="600" cy="360" rx="390" ry="220" stroke="{orbit_stroke}" stroke-width="1" stroke-dasharray="1 8" />
    <path d="M 240,360 C 240,190 400,140 600,140 C 800,140 960,190 960,360 C 960,530 800,580 600,580 C 400,580 240,530 240,360 Z" 
          stroke="{orbit_stroke}" stroke-width="1" opacity="0.6" stroke-dasharray="6 8" />
    
    <!-- Generative Coordinate Ticks -->
    <line x1="600" y1="35" x2="600" y2="55" stroke="{accent_line}" stroke-width="1.5" />
    <line x1="600" y1="845" x2="600" y2="865" stroke="{accent_line}" stroke-width="1.5" />
    <line x1="45" y1="360" x2="65" y2="360" stroke="{accent_line}" stroke-width="1.5" />
    <line x1="1135" y1="360" x2="1155" y2="360" stroke="{accent_line}" stroke-width="1.5" />
  </g>

  <!-- Central Organic Logo Mark -->
  <g id="mark" filter="url(#shadowOrganic_{theme})" transform="translate(0, 5)">
    <!-- Base Node: The Anchor (Deep Charcoal/Espresso) -->
    <!-- Curvature: Fluid organic petal wrapping from center to bottom right -->
    <path d="M 600,355 
             C 680,390 770,455 750,525 
             C 730,585 620,585 550,545 
             C 475,500 460,420 520,375 
             Z" 
          fill="url(#gradStone_{theme})" />

    <!-- Flow Node 2: Left Dynamic Swell (Warm Taupe) -->
    <!-- Intertwining smooth morphology -->
    <path d="M 600,355 
             C 490,305 385,340 365,420 
             C 345,505 425,560 505,550 
             C 575,540 605,450 600,355 
             Z" 
          fill="url(#gradTaupe_{theme})" />

    <!-- Flow Node 3: Ascending Crest (Cashmere / Soft Dune) -->
    <!-- Rising harmonic lobe -->
    <path d="M 600,355 
             C 530,240 505,155 585,135 
             C 665,115 725,195 710,285 
             C 695,365 640,375 600,355 
             Z" 
          fill="url(#gradCashmere_{theme})" />

    <!-- Flow Node 4: Translucent Overlay Petal (Warm Bone / Oat) -->
    <!-- Creates subtle emergent volumetric overlap -->
    <path d="M 600,355 
             C 655,270 745,260 785,335 
             C 825,410 775,490 695,485 
             C 625,480 605,405 600,355 
             Z" 
          fill="url(#gradOat_{theme})" />

    <!-- Flow Node 5: The Forward Surge (Soft Luminous Alabaster) -->
    <path d="M 600,355 
             C 515,340 455,255 505,195 
             C 555,135 660,180 670,265 
             C 680,345 630,365 600,355 
             Z" 
          fill="url(#gradTaupe_{theme})" opacity="0.3" />

    <!-- The Generative Heart: Seed Core (Raw Umber & Ochre Glow) -->
    <path d="M 600,355 
             C 638,325 668,365 660,400 
             C 652,435 615,452 580,440 
             C 545,428 542,390 565,362 
             C 578,348 588,345 600,355 
             Z" 
          fill="url(#gradCore_{theme})" />

    <!-- Inner Organic Spark / Fenestration -->
    <ellipse cx="602" cy="370" rx="10" ry="14" transform="rotate(-22 602 370)" fill="{inner_void}" />

    <!-- Refined Linear Filaments (Vector currents symbolizing neural generative pathways) -->
    <path d="M 535,185 C 595,230 645,315 595,465" 
          stroke="{filament_white}" stroke-width="2" stroke-linecap="round" fill="none" />
    <path d="M 430,375 C 505,390 590,410 685,510" 
          stroke="{filament_white}" stroke-width="1.6" stroke-linecap="round" fill="none" />
    <path d="M 685,235 C 655,300 635,415 540,525" 
          stroke="{filament_dark}" stroke-width="1.4" stroke-linecap="round" stroke-dasharray="4 6" fill="none" />

    <!-- Micro Focal Points (Biological / Algorithmic Nodes) -->
    <circle cx="585" cy="135" r="3.5" fill="{accent_line}" />
    <circle cx="750" cy="525" r="3.5" fill="{accent_line}" />
    <circle cx="365" cy="420" r="3.5" fill="{accent_line}" />
    <circle cx="785" cy="335" r="3.5" fill="{accent_line}" />
  </g>

  <!-- Brand Typography Lockup -->
  <g text-anchor="middle" id="brand-typography">
    <!-- Brand Wordmark -->
    <text x="600" y="710" 
          font-family="system-ui, -apple-system, 'SF Pro Display', 'Neue Haas Grotesk', 'Helvetica Neue', sans-serif" 
          font-size="44" 
          font-weight="300" 
          letter-spacing="0.38em" 
          fill="{text_primary}">M O R P H I C</text>

    <!-- Subtitle / Category Definition -->
    <text x="600" y="750" 
          font-family="system-ui, -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif" 
          font-size="13" 
          font-weight="500" 
          letter-spacing="0.48em" 
          fill="{text_secondary}">GENERATIVE INTELLIGENCE</text>

    <!-- Refined Geometric Dividing Motif -->
    <line x1="560" y1="775" x2="640" y2="775" stroke="{accent_line}" stroke-width="1.2" stroke-linecap="round" opacity="0.8"/>
    <circle cx="600" cy="775" r="2.5" fill="{text_secondary}" />
  </g>
</svg>'''
    return svg

def create_icon_symbol_svg():
    """
    Square app icon / standalone favicon & emblem SVG (viewBox: 0 0 512 512)
    Optimized for high-impact recognition at any scale with clean organic contours.
    """
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <defs>
    <radialGradient id="iconBg" cx="45%" cy="38%" r="75%">
      <stop offset="0%" stop-color="#FBF9F6" />
      <stop offset="55%" stop-color="#F3ECE4" />
      <stop offset="100%" stop-color="#E2D7CB" />
    </radialGradient>

    <linearGradient id="iconStone" x1="15%" y1="10%" x2="85%" y2="90%">
      <stop offset="0%" stop-color="#3D3630" />
      <stop offset="50%" stop-color="#28231F" />
      <stop offset="100%" stop-color="#181513" />
    </linearGradient>

    <linearGradient id="iconTaupe" x1="10%" y1="15%" x2="90%" y2="85%">
      <stop offset="0%" stop-color="#918275" />
      <stop offset="50%" stop-color="#75675A" />
      <stop offset="100%" stop-color="#55493F" />
    </linearGradient>

    <linearGradient id="iconCashmere" x1="20%" y1="15%" x2="80%" y2="85%">
      <stop offset="0%" stop-color="#CBBCAE" />
      <stop offset="50%" stop-color="#B2A191" />
      <stop offset="100%" stop-color="#8E7E70" />
    </linearGradient>

    <linearGradient id="iconOat" x1="25%" y1="15%" x2="75%" y2="85%">
      <stop offset="0%" stop-color="#EDE4DA" />
      <stop offset="50%" stop-color="#D7C9BC" />
      <stop offset="100%" stop-color="#BDB0A3" />
    </linearGradient>

    <radialGradient id="iconCore" cx="40%" cy="36%" r="60%">
      <stop offset="0%" stop-color="#BD9E80" />
      <stop offset="55%" stop-color="#93775A" />
      <stop offset="100%" stop-color="#584533" />
    </radialGradient>

    <filter id="iconShadow" x="-25%" y="-25%" width="150%" height="150%">
      <feDropShadow dx="0" dy="16" stdDeviation="22" flood-color="#1B1612" flood-opacity="0.16" />
    </filter>

    <!-- Subtle container border -->
    <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.8" />
      <stop offset="100%" stop-color="#B0A294" stop-opacity="0.4" />
    </linearGradient>
  </defs>

  <!-- Squircle Rounded Container Canvas -->
  <rect x="16" y="16" width="480" height="480" rx="112" fill="url(#iconBg)" stroke="url(#borderGrad)" stroke-width="2.5" />

  <!-- Harmonic Guidance Rings -->
  <g opacity="0.4" stroke="#B8AAA0" stroke-width="1.2" fill="none">
    <circle cx="256" cy="256" r="185" stroke-dasharray="3 7" />
    <circle cx="256" cy="256" r="130" stroke-dasharray="2 6" opacity="0.6" />
  </g>

  <!-- The Organic Emblem (Centered at 256, 256) -->
  <g filter="url(#iconShadow)">
    <!-- Base Charcoal Node -->
    <path d="M 256,256 
             C 316,282 384,332 368,384 
             C 353,429 270,429 218,399 
             C 161,365 150,305 196,271 
             Z" 
          fill="url(#iconStone)" />

    <!-- Left Taupe Node -->
    <path d="M 256,256 
             C 173,218 94,245 79,305 
             C 64,369 124,410 184,402 
             C 237,395 260,327 256,256 
             Z" 
          fill="url(#iconTaupe)" />

    <!-- Ascending Cashmere Node -->
    <path d="M 256,256 
             C 203,169 184,105 245,90 
             C 305,75 350,135 339,203 
             C 328,263 286,271 256,256 
             Z" 
          fill="url(#iconCashmere)" />

    <!-- Right Dune/Oat Node -->
    <path d="M 256,256 
             C 298,192 365,184 396,241 
             C 426,297 388,358 328,354 
             C 275,350 260,294 256,256 
             Z" 
          fill="url(#iconOat)" />

    <!-- Generative Core Seed -->
    <path d="M 256,256 
             C 285,233 308,263 301,290 
             C 295,316 267,329 241,320 
             C 214,311 212,282 230,261 
             C 240,250 247,248 256,256 
             Z" 
          fill="url(#iconCore)" />

    <!-- Core Negative Space / Center Spark -->
    <ellipse cx="258" cy="268" rx="7.5" ry="10.5" transform="rotate(-22 258 268)" fill="#FBF9F6" />

    <!-- Vector Flow Paths -->
    <path d="M 207,128 C 252,162 290,226 252,339" 
          stroke="rgba(255, 255, 255, 0.85)" stroke-width="1.8" stroke-linecap="round" fill="none" />
    <path d="M 128,271 C 184,282 249,297 320,373" 
          stroke="rgba(255, 255, 255, 0.75)" stroke-width="1.5" stroke-linecap="round" fill="none" />
    <path d="M 320,166 C 298,215 282,301 211,384" 
          stroke="rgba(40, 32, 26, 0.45)" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="3 5" fill="none" />
  </g>
</svg>'''
    return svg

def create_brand_system_sheet_svg():
    """
    Creates a comprehensive Brand Architecture & Guidelines presentation sheet SVG (1600x1000).
    Exhibits the primary lockup, monochrome stone edition, color palette swatches with hex codes,
    typography specs, scale tests (favicon / app icon), and design rationale.
    """
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000" width="100%" height="100%">
  <defs>
    <radialGradient id="sheetBg" cx="50%" cy="30%" r="80%">
      <stop offset="0%" stop-color="#FAF7F2" />
      <stop offset="60%" stop-color="#F2EDE5" />
      <stop offset="100%" stop-color="#E5DCD2" />
    </radialGradient>

    <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.9" />
      <stop offset="100%" stop-color="#F7F3EC" stop-opacity="0.8" />
    </linearGradient>

    <linearGradient id="darkCardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#24201D" />
      <stop offset="100%" stop-color="#141210" />
    </linearGradient>

    <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#2E2620" flood-opacity="0.07" />
    </filter>

    <!-- Swatch Gradients -->
    <linearGradient id="swatchAlabaster" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FAF8F5" />
      <stop offset="100%" stop-color="#EFE9DE" />
    </linearGradient>

    <linearGradient id="swatchSand" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#E4DCD2" />
      <stop offset="100%" stop-color="#D2C5B6" />
    </linearGradient>

    <linearGradient id="swatchTaupe" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#9C8D7F" />
      <stop offset="100%" stop-color="#7B6D60" />
    </linearGradient>

    <linearGradient id="swatchUmber" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#A88E72" />
      <stop offset="100%" stop-color="#6F5841" />
    </linearGradient>

    <linearGradient id="swatchCharcoal" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#36302A" />
      <stop offset="100%" stop-color="#1C1815" />
    </linearGradient>
  </defs>

  <!-- Canvas Background -->
  <rect width="1600" height="1000" fill="url(#sheetBg)" />

  <!-- Sheet Header -->
  <g transform="translate(80, 80)">
    <text font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="600" letter-spacing="0.3em" fill="#8C7D70">BRAND IDENTITY SPECIFICATION</text>
    <text y="42" font-family="system-ui, -apple-system, sans-serif" font-size="36" font-weight="300" letter-spacing="0.2em" fill="#24201D">MORPHIC AI</text>
    <text y="72" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="400" letter-spacing="0.05em" fill="#75675A">Next-Generation Continuous Generative Intelligence System</text>
    <line x1="0" y1="95" x2="1440" y2="95" stroke="#D5C8BA" stroke-width="1.5" />
  </g>

  <!-- Left Main Card: Primary Identity Showcase (x=80, y=200, w=900, h=520) -->
  <rect x="80" y="200" width="900" height="520" rx="24" fill="url(#cardBg)" filter="url(#cardShadow)" stroke="#E8DFD5" stroke-width="1.5" />
  
  <!-- Primary Mark inside card -->
  <g transform="translate(530, 410) scale(0.85)">
    <!-- Organic shapes from core -->
    <path d="M 0,-5 C 80,30 170,95 150,165 C 130,225 20,225 -50,185 C -125,140 -140,60 -80,15 Z" fill="#2E2823" />
    <path d="M 0,-5 C -110,-55 -215,-20 -235,60 C -255,145 -175,200 -95,190 C -25,180 5,90 0,-5 Z" fill="#807266" />
    <path d="M 0,-5 C -70,-120 -95,-205 -15,-225 C 65,-245 125,-165 110,-75 C 95,5 40,15 0,-5 Z" fill="#BAABA0" />
    <path d="M 0,-5 C 55,-90 145,-100 185,-25 C 225,50 175,130 95,125 C 25,120 5,45 0,-5 Z" fill="#DFD6CC" />
    <!-- Core seed -->
    <path d="M 0,-5 C 38,-35 68,5 60,40 C 52,75 15,92 -20,80 C -55,68 -58,30 -35,2 C -22,-12 -12,-15 0,-5 Z" fill="#947B62" />
    <ellipse cx="2" cy="10" rx="9" ry="13" transform="rotate(-22 2 10)" fill="#FAF7F2" />
    <!-- Filaments -->
    <path d="M -65,-175 C -5,-130 45,-45 -5,105" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" fill="none" opacity="0.8" />
    <path d="M -170,15 C -95,30 -10,50 85,150" stroke="#FFFFFF" stroke-width="1.4" stroke-linecap="round" fill="none" opacity="0.7" />
  </g>

  <!-- Typography under Primary Mark inside Left Card -->
  <g text-anchor="middle" transform="translate(530, 630)">
    <text font-family="system-ui, -apple-system, sans-serif" font-size="34" font-weight="300" letter-spacing="0.38em" fill="#24201D">M O R P H I C</text>
    <text y="32" font-family="system-ui, -apple-system, sans-serif" font-size="11" font-weight="500" letter-spacing="0.45em" fill="#807266">GENERATIVE INTELLIGENCE</text>
  </g>

  <!-- Badge in Left Card -->
  <rect x="110" y="230" width="130" height="28" rx="6" fill="#F0E8DE" />
  <text x="175" y="249" text-anchor="middle" font-family="system-ui, sans-serif" font-size="10" font-weight="600" letter-spacing="0.15em" fill="#6A5D52">PRIMARY LOCKUP</text>

  <!-- Right Upper Card: Dark Environment / Reverse Contrast (x=1010, y=200, w=510, h=250) -->
  <rect x="1010" y="200" width="510" height="250" rx="20" fill="url(#darkCardBg)" filter="url(#cardShadow)" stroke="#38322B" stroke-width="1.2" />
  <rect x="1035" y="222" width="125" height="24" rx="5" fill="#332B25" />
  <text x="1097" y="238" text-anchor="middle" font-family="system-ui, sans-serif" font-size="9" font-weight="600" letter-spacing="0.12em" fill="#BAA898">DARK PALETTE</text>

  <!-- Dark Mark Minimal Lockup -->
  <g transform="translate(1170, 335) scale(0.48)">
    <path d="M 0,-5 C 80,30 170,95 150,165 C 130,225 20,225 -50,185 C -125,140 -140,60 -80,15 Z" fill="#3D3630" />
    <path d="M 0,-5 C -110,-55 -215,-20 -235,60 C -255,145 -175,200 -95,190 C -25,180 5,90 0,-5 Z" fill="#918174" />
    <path d="M 0,-5 C -70,-120 -95,-205 -15,-225 C 65,-245 125,-165 110,-75 C 95,5 40,15 0,-5 Z" fill="#BFB0A2" />
    <path d="M 0,-5 C 55,-90 145,-100 185,-25 C 225,50 175,130 95,125 C 25,120 5,45 0,-5 Z" fill="#EDE4DA" />
    <path d="M 0,-5 C 38,-35 68,5 60,40 C 52,75 15,92 -20,80 C -55,68 -58,30 -35,2 Z" fill="#B3977B" />
  </g>
  <g transform="translate(1310, 330)">
    <text font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="300" letter-spacing="0.32em" fill="#FAF6F0">MORPHIC</text>
    <text y="22" font-family="system-ui, -apple-system, sans-serif" font-size="8" font-weight="500" letter-spacing="0.4em" fill="#A09285">DARK MODE APPLICATION</text>
  </g>

  <!-- Right Lower Card: App Icon & Responsive Favicon (x=1010, y=470, w=510, h=250) -->
  <rect x="1010" y="470" width="510" height="250" rx="20" fill="url(#cardBg)" filter="url(#cardShadow)" stroke="#E8DFD5" stroke-width="1.5" />
  <rect x="1035" y="492" width="135" height="24" rx="5" fill="#F0E8DE" />
  <text x="1102" y="508" text-anchor="middle" font-family="system-ui, sans-serif" font-size="9" font-weight="600" letter-spacing="0.12em" fill="#6A5D52">RESPONSIVE SCALING</text>

  <!-- Large App Icon representation (100x100) -->
  <rect x="1045" y="535" width="100" height="100" rx="24" fill="#FAF8F5" stroke="#D8CCC0" stroke-width="1.5" />
  <g transform="translate(1095, 585) scale(0.24)">
    <path d="M 0,-5 C 80,30 170,95 150,165 C 130,225 20,225 -50,185 C -125,140 -140,60 -80,15 Z" fill="#2E2823" />
    <path d="M 0,-5 C -110,-55 -215,-20 -235,60 C -255,145 -175,200 -95,190 C -25,180 5,90 0,-5 Z" fill="#807266" />
    <path d="M 0,-5 C -70,-120 -95,-205 -15,-225 C 65,-245 125,-165 110,-75 C 95,5 40,15 0,-5 Z" fill="#BAABA0" />
    <path d="M 0,-5 C 38,-35 68,5 60,40 C 52,75 15,92 -20,80 Z" fill="#947B62" />
  </g>
  <text x="1095" y="655" text-anchor="middle" font-family="system-ui, sans-serif" font-size="10" font-weight="500" fill="#75675A">App Icon</text>

  <!-- Medium Icon representation (64x64) -->
  <rect x="1175" y="553" width="64" height="64" rx="16" fill="#FAF8F5" stroke="#D8CCC0" stroke-width="1.2" />
  <g transform="translate(1207, 585) scale(0.15)">
    <path d="M 0,-5 C 80,30 170,95 150,165 C 130,225 20,225 -50,185 C -125,140 -140,60 -80,15 Z" fill="#2E2823" />
    <path d="M 0,-5 C -110,-55 -215,-20 -235,60 C -255,145 -175,200 -95,190 C -25,180 5,90 0,-5 Z" fill="#807266" />
    <path d="M 0,-5 C -70,-120 -95,-205 -15,-225 C 65,-245 125,-165 110,-75 C 95,5 40,15 0,-5 Z" fill="#BAABA0" />
    <path d="M 0,-5 C 38,-35 68,5 60,40 C 52,75 15,92 -20,80 Z" fill="#947B62" />
  </g>
  <text x="1207" y="640" text-anchor="middle" font-family="system-ui, sans-serif" font-size="10" font-weight="500" fill="#75675A">64px</text>

  <!-- Small Favicon representation (32x32) -->
  <rect x="1265" y="569" width="32" height="32" rx="8" fill="#FAF8F5" stroke="#D8CCC0" stroke-width="1" />
  <g transform="translate(1281, 585) scale(0.08)">
    <path d="M 0,-5 C 80,30 170,95 150,165 C 130,225 20,225 -50,185 C -125,140 -140,60 -80,15 Z" fill="#2E2823" />
    <path d="M 0,-5 C -110,-55 -215,-20 -235,60 C -255,145 -175,200 -95,190 C -25,180 5,90 0,-5 Z" fill="#807266" />
    <path d="M 0,-5 C 38,-35 68,5 60,40 C 52,75 15,92 -20,80 Z" fill="#947B62" />
  </g>
  <text x="1281" y="625" text-anchor="middle" font-family="system-ui, sans-serif" font-size="10" font-weight="500" fill="#75675A">32px</text>

  <!-- Scale Description text -->
  <text x="1330" y="575" font-family="system-ui, sans-serif" font-size="11" font-weight="400" fill="#75675A">High legibility across</text>
  <text x="1330" y="595" font-family="system-ui, sans-serif" font-size="11" font-weight="400" fill="#75675A">retina viewports,</text>
  <text x="1330" y="615" font-family="system-ui, sans-serif" font-size="11" font-weight="400" fill="#75675A">UI navigation &amp; app tiles.</text>

  <!-- Bottom Section: Color Palette & Design Rationale (y=750, h=180) -->
  <g transform="translate(80, 755)">
    <!-- Swatch 1: Alabaster / Chalk -->
    <rect x="0" y="0" width="165" height="70" rx="12" fill="url(#swatchAlabaster)" stroke="#D8CEBF" stroke-width="1" />
    <text x="14" y="98" font-family="system-ui, sans-serif" font-size="12" font-weight="600" fill="#2A2521">ALABASTER</text>
    <text x="14" y="116" font-family="monospace" font-size="11" fill="#75675A">#FAF8F5</text>
    <text x="14" y="132" font-family="system-ui, sans-serif" font-size="10" fill="#968779">Luminous Base</text>

    <!-- Swatch 2: Sand & Dune -->
    <rect x="185" y="0" width="165" height="70" rx="12" fill="url(#swatchSand)" stroke="#C8BCAD" stroke-width="1" />
    <text x="199" y="98" font-family="system-ui, sans-serif" font-size="12" font-weight="600" fill="#2A2521">DUNE / BONE</text>
    <text x="199" y="116" font-family="monospace" font-size="11" fill="#75675A">#DCD4C7</text>
    <text x="199" y="132" font-family="system-ui, sans-serif" font-size="10" fill="#968779">Harmonic Transition</text>

    <!-- Swatch 3: Warm Taupe -->
    <rect x="370" y="0" width="165" height="70" rx="12" fill="url(#swatchTaupe)" />
    <text x="384" y="98" font-family="system-ui, sans-serif" font-size="12" font-weight="600" fill="#2A2521">WARM TAUPE</text>
    <text x="384" y="116" font-family="monospace" font-size="11" fill="#75675A">#807266</text>
    <text x="384" y="132" font-family="system-ui, sans-serif" font-size="10" fill="#968779">Secondary Flow</text>

    <!-- Swatch 4: Earth Bronze / Raw Umber -->
    <rect x="555" y="0" width="165" height="70" rx="12" fill="url(#swatchUmber)" />
    <text x="569" y="98" font-family="system-ui, sans-serif" font-size="12" font-weight="600" fill="#2A2521">RAW UMBER</text>
    <text x="569" y="116" font-family="monospace" font-size="11" fill="#75675A">#7D6650</text>
    <text x="569" y="132" font-family="system-ui, sans-serif" font-size="10" fill="#968779">Generative Core Seed</text>

    <!-- Swatch 5: Deep Charcoal Stone -->
    <rect x="740" y="0" width="165" height="70" rx="12" fill="url(#swatchCharcoal)" />
    <text x="754" y="98" font-family="system-ui, sans-serif" font-size="12" font-weight="600" fill="#2A2521">STONE CHARCOAL</text>
    <text x="754" y="116" font-family="monospace" font-size="11" fill="#75675A">#24201D</text>
    <text x="754" y="132" font-family="system-ui, sans-serif" font-size="10" fill="#968779">Structural Anchor</text>

    <!-- Rationale / Philosophy Block (x=930 to 1440) -->
    <g transform="translate(930, 0)">
      <rect x="0" y="0" width="510" height="150" rx="16" fill="#F4EDE4" stroke="#DECFC0" stroke-width="1.2" />
      <text x="25" y="32" font-family="system-ui, sans-serif" font-size="12" font-weight="600" letter-spacing="0.1em" fill="#4A3F35">DESIGN PRINCIPLES</text>
      <text x="25" y="58" font-family="system-ui, sans-serif" font-size="12" font-weight="400" fill="#6A5C50">• Organic Continuous Morphology: Replaces rigid circuits with fluid biomimetic forms.</text>
      <text x="25" y="80" font-family="system-ui, sans-serif" font-size="12" font-weight="400" fill="#6A5C50">• Emergence over Assembly: Layered translucent pods symbolize synthesis &amp; intuition.</text>
      <text x="25" y="102" font-family="system-ui, sans-serif" font-size="12" font-weight="400" fill="#6A5C50">• Calming Neutral Tones: Alabaster, warm cashmere, taupe, and deep charcoal ground</text>
      <text x="35" y="122" font-family="system-ui, sans-serif" font-size="12" font-weight="400" fill="#6A5C50">high-tech capability in organic serenity, clarity, and human warmth.</text>
    </g>
  </g>
</svg>'''
    return svg

def create_horizontal_lockup_svg():
    """
    Horizontal banner lockup SVG (1200x360) ideal for web headers, navigation, documentation.
    """
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 360" width="100%" height="100%">
  <defs>
    <linearGradient id="hBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FAF8F5" />
      <stop offset="100%" stop-color="#EDE6DD" />
    </linearGradient>

    <linearGradient id="hStone" x1="20%" y1="10%" x2="85%" y2="90%">
      <stop offset="0%" stop-color="#3A332C" />
      <stop offset="100%" stop-color="#181513" />
    </linearGradient>

    <linearGradient id="hTaupe" x1="15%" y1="15%" x2="85%" y2="85%">
      <stop offset="0%" stop-color="#8F8073" />
      <stop offset="100%" stop-color="#564A40" />
    </linearGradient>

    <linearGradient id="hCashmere" x1="10%" y1="20%" x2="90%" y2="80%">
      <stop offset="0%" stop-color="#CBBCAE" />
      <stop offset="100%" stop-color="#8E7E70" />
    </linearGradient>

    <linearGradient id="hOat" x1="25%" y1="10%" x2="75%" y2="90%">
      <stop offset="0%" stop-color="#E8DFD5" />
      <stop offset="100%" stop-color="#BAACA0" />
    </linearGradient>

    <radialGradient id="hCore" cx="42%" cy="38%" r="60%">
      <stop offset="0%" stop-color="#BD9E80" />
      <stop offset="100%" stop-color="#5B4835" />
    </radialGradient>

    <filter id="hShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="18" flood-color="#241E19" flood-opacity="0.12" />
    </filter>
  </defs>

  <rect width="1200" height="360" fill="url(#hBg)" />

  <!-- Subtle accent lines in background -->
  <line x1="120" y1="180" x2="1080" y2="180" stroke="#DFD5C8" stroke-width="1" stroke-dasharray="2 10" />

  <!-- Mark positioned on left center (cx=220, cy=180) -->
  <g transform="translate(220, 180) scale(0.62)" filter="url(#hShadow)">
    <path d="M 0,-5 C 80,30 170,95 150,165 C 130,225 20,225 -50,185 C -125,140 -140,60 -80,15 Z" fill="url(#hStone)" />
    <path d="M 0,-5 C -110,-55 -215,-20 -235,60 C -255,145 -175,200 -95,190 C -25,180 5,90 0,-5 Z" fill="url(#hTaupe)" />
    <path d="M 0,-5 C -70,-120 -95,-205 -15,-225 C 65,-245 125,-165 110,-75 C 95,5 40,15 0,-5 Z" fill="url(#hCashmere)" />
    <path d="M 0,-5 C 55,-90 145,-100 185,-25 C 225,50 175,130 95,125 C 25,120 5,45 0,-5 Z" fill="url(#hOat)" />
    <path d="M 0,-5 C 38,-35 68,5 60,40 C 52,75 15,92 -20,80 C -55,68 -58,30 -35,2 Z" fill="url(#hCore)" />
    <ellipse cx="2" cy="10" rx="9" ry="13" transform="rotate(-22 2 10)" fill="#FAF8F5" />
    <path d="M -65,-175 C -5,-130 45,-45 -5,105" stroke="rgba(255,255,255,0.8)" stroke-width="2" stroke-linecap="round" fill="none" />
    <path d="M -170,15 C -95,30 -10,50 85,150" stroke="rgba(255,255,255,0.6)" stroke-width="1.6" stroke-linecap="round" fill="none" />
  </g>

  <!-- Vertical separator -->
  <line x1="390" y1="90" x2="390" y2="270" stroke="#D3C7B9" stroke-width="1.5" stroke-linecap="round" />

  <!-- Typography Lockup on right -->
  <g transform="translate(440, 175)">
    <text font-family="system-ui, -apple-system, sans-serif" font-size="52" font-weight="300" letter-spacing="0.34em" fill="#24201D">M O R P H I C</text>
    <text y="42" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="500" letter-spacing="0.45em" fill="#786B5E">GENERATIVE INTELLIGENCE</text>
    <line x1="2" y1="64" x2="90" y2="64" stroke="#B3A292" stroke-width="2" stroke-linecap="round" />
  </g>
</svg>'''
    return svg

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    with open("output/logo-primary-light.svg", "w") as f:
        f.write(create_morphic_svg("light"))
    with open("output/logo-primary-dark.svg", "w") as f:
        f.write(create_morphic_svg("dark"))
    with open("output/logo-icon-mark.svg", "w") as f:
        f.write(create_icon_symbol_svg())
    with open("output/logo-horizontal-lockup.svg", "w") as f:
        f.write(create_horizontal_lockup_svg())
    with open("output/logo-brand-sheet.svg", "w") as f:
        f.write(create_brand_system_sheet_svg())
    print("SVG Generation completed successfully.")
