import math
import subprocess
import os

def create_mobius_organic(filename="src/concept_mobius.svg", is_dark=True):
    """
    Concept: The Continuous Latent Loop / Morphic Ribbon
    A continuous organic band that sweeps in a dynamic figure-8 / trefoil in 3D perspective,
    with varying organic thickness, subtle shading, and warm neutral tones.
    """
    # Palette
    bg = "#121110" if is_dark else "#FAF7F2"
    txt_col = "#EDE8DF" if is_dark else "#1A1918"
    sub_col = "#948D83" if is_dark else "#78726A"
    
    # We can model a smooth 3D space curve:
    # x(t) = R * (sin(t) + 2*sin(2t)) / 3 ... or trefoil knot projected with smooth organic volume
    # Or 3 overlapping organic ribbon folds
    # Let's create an interlocking 3-fold organic ribbon (trefoil / triquetra) with sculptural depth
    # Parametric trefoil knot:
    # x(t) = sin(t) + 2*sin(2t)
    # y(t) = cos(t) - 2*cos(2t)
    # z(t) = -sin(3t)
    
    steps = 300
    points = []
    scale = 90
    cx, cy = 400, 340
    
    for i in range(steps):
        t = (2 * math.pi * i) / steps
        # smooth trefoil
        x = math.sin(t) + 2.0 * math.sin(2.0 * t)
        y = math.cos(t) - 2.0 * math.cos(2.0 * t)
        z = -math.sin(3.0 * t)
        
        # isometric tilt
        # rotate around X by 25 deg, Z by 15 deg
        rx = 0.4
        rz = 0.2
        
        # apply rotation
        x1 = x * math.cos(rz) - y * math.sin(rz)
        y1 = x * math.sin(rz) + y * math.cos(rz)
        z1 = z
        
        x2 = x1
        y2 = y1 * math.cos(rx) - z1 * math.sin(rx)
        z2 = y1 * math.sin(rx) + z1 * math.cos(rx)
        
        px = cx + x2 * scale
        py = cy + y2 * scale * 0.95
        points.append((px, py, z2, t))
        
    # We can construct overlapping ribbon segments sorted by depth or split into 3 continuous organic petals
    # Let's inspect another approach:
    # 3 distinct flowing organic ribbons that sweep inward like calligraphy or flowing silk / clay ribbons.
    pass

def create_sculptural_zen_aperture(filename="src/concept_zen.svg", is_dark=False):
    """
    Concept: The 'Latent Seed' / Organic Zen Core
    Layered, asymmetric, flowing pebble contours that create an organic lens / aperture.
    Pure elegance, architectural, timeless.
    """
    bg = "#FAF8F5" if not is_dark else "#151413"
    txt = "#1D1B1A" if not is_dark else "#F3EFE9"
    sub = "#7D756C" if not is_dark else "#9C9489"
    
    # 5 nested organic pebble contours, each rotating and breathing with subtle organic perturbation
    # Colors:
    # Outer to inner in warm neutral tones:
    # 1. Warm stone (#E5DFD6 / dark: #262422)
    # 2. Taupe oat (#CFC6B8 / dark: #383430)
    # 3. Muted clay umber (#A89C8C / dark: #524B44)
    # 4. Rich warm graphite / dark stone (#695E54 / dark: #80766B)
    # 5. Core pearl (#2E2925 / dark: #E8E0D5)
    pass
