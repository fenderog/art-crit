#!/usr/bin/env python3
"""Build final logo files into ./output/ (SVG set + PNG marks + motion MP4 frames).

Geometry is shared with src/render.py so SVG and raster marks match.
Run: python3 src/build.py
"""
import math, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from render import blob_polygon, render_mark, write_png, INK, PAPER, STONE_DARK

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
OUT = os.path.normpath(OUT)

# Same lobe table as render.py (design space 640)
LOBES = [
    ((318, 208), 104, (0.07, 0.045, 0.02), 0.4, "#7A746C", "#B2A99B"),
    ((208, 340), 118, (0.06, 0.05, 0.018), 2.3, "#92897C", "#C4BAAA"),
    ((392, 364), 94, (0.075, 0.04, 0.022), 4.2, "#B6AB98", "#DED7C9"),
    ((428, 246), 40, (0.06, 0.04, 0.02), 1.1, "#8C8478", "#BAB1A2"),
]
LOBES_DARK = [
    ((318, 208), 104, (0.07, 0.045, 0.02), 0.4, "#B2A99B", "#7A746C"),
    ((208, 340), 118, (0.06, 0.05, 0.018), 2.3, "#C4BAAA", "#92897C"),
    ((392, 364), 94, (0.075, 0.04, 0.022), 4.2, "#DED7C9", "#B6AB98"),
    ((428, 246), 40, (0.06, 0.04, 0.02), 1.1, "#BAB1A2", "#8C8478"),
]

def smooth_path(pts):
    """Catmull-Rom -> cubic Bezier closed smooth path."""
    n = len(pts)
    d = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for i in range(n):
        p0 = pts[(i - 1) % n]; p1 = pts[i]; p2 = pts[(i + 1) % n]; p3 = pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d.append(f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}")
    return " ".join(d) + " Z"

def mark_group(dark=False, gid="m"):
    lobes = LOBES_DARK if dark else LOBES
    parts = [f'<g id="{gid}">']
    for i, ((cx, cy), r, wob, ph, top, bottom) in enumerate(lobes):
        pts = blob_polygon(cx, cy, r, wob, phase=ph, n=72)
        parts.append(
            f'<path d="{smooth_path(pts)}" fill="url(#g{i}{gid})" fill-opacity="0.96"/>')
    seed = blob_polygon(318, 308, 19, (0.05, 0.04, 0.02), phase=1.2, n=48)
    paper = "#24221F" if dark else "#F3F0E9"
    nucleus = "#EAE4D8" if dark else "#24221F"
    spore = "#D8D1C4" if dark else "#5C5852"
    parts.append(f'<path d="{smooth_path(seed)}" fill="{paper}"/>')
    parts.append(f'<circle cx="321" cy="305" r="7.5" fill="{nucleus}"/>')
    parts.append(f'<circle cx="486" cy="176" r="11" fill="{spore}" fill-opacity="0.9"/>')
    parts.append("</g>")
    defs = ["<defs>"]
    for i, ((cx, cy), r, wob, ph, top, bottom) in enumerate(lobes):
        defs.append(
            f'<linearGradient id="g{i}{gid}" gradientUnits="userSpaceOnUse" '
            f'x1="{cx}" y1="{cy-r}" x2="{cx}" y2="{cy+r}">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>')
    defs.append("</defs>")
    return "".join(defs) + "".join(parts)

FONT = "Avenir Next, Futura, 'Helvetica Neue', Helvetica, Arial, sans-serif"

def svg_primary():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="520" viewBox="0 0 1240 520" role="img" aria-label="forma — generative intelligence">
  <title>forma — Generative Intelligence</title>
  <rect width="1240" height="520" fill="#F3F0E9"/>
  <g transform="translate(28,28) scale(0.725)">{mark_group(False, "p")}</g>
  <text x="545" y="268" font-family="{FONT}" font-size="122" font-weight="500" letter-spacing="1" fill="#24221F">forma</text>
  <rect x="550" y="298" width="54" height="3" rx="1.5" fill="#A79E93"/>
  <text x="550" y="342" font-family="{FONT}" font-size="24" font-weight="500" letter-spacing="8" fill="#7A746C">GENERATIVE INTELLIGENCE</text>
  <text x="550" y="392" font-family="{FONT}" font-size="21" font-weight="400" letter-spacing="0.4" fill="#928B81">Intelligence that grows, adapts and creates.</text>
</svg>
'''

def svg_dark():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="520" viewBox="0 0 1240 520" role="img" aria-label="forma — generative intelligence">
  <title>forma — Generative Intelligence</title>
  <rect width="1240" height="520" fill="#24221F"/>
  <g transform="translate(28,28) scale(0.725)">{mark_group(True, "d")}</g>
  <text x="545" y="268" font-family="{FONT}" font-size="122" font-weight="500" letter-spacing="1" fill="#F3F0E9">forma</text>
  <rect x="550" y="298" width="54" height="3" rx="1.5" fill="#A79E93"/>
  <text x="550" y="342" font-family="{FONT}" font-size="24" font-weight="500" letter-spacing="8" fill="#B8B0A2">GENERATIVE INTELLIGENCE</text>
  <text x="550" y="392" font-family="{FONT}" font-size="21" font-weight="400" letter-spacing="0.4" fill="#9A937F">Intelligence that grows, adapts and creates.</text>
</svg>
'''

def svg_mark(dark=False):
    bg = "#24221F" if dark else "none"
    bgrect = f'<rect width="640" height="640" fill="{bg}"/>' if dark else ""
    gid = "kd" if dark else "k"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="640" viewBox="0 0 640 640" role="img" aria-label="forma mark">
  <title>forma mark</title>
  {bgrect}
  {mark_group(dark, gid)}
</svg>
'''

def main():
    os.makedirs(OUT, exist_ok=True)
    files = {
        "forma-logo-primary.svg": svg_primary(),
        "forma-logo-dark.svg": svg_dark(),
        "forma-logo-mark.svg": svg_mark(False),
        "forma-logo-mark-dark.svg": svg_mark(True),
    }
    for name, text in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(text)
        print(name, len(text))
    # PNG marks via the shared rasterizer
    for name, dark in (("forma-mark-light.png", False), ("forma-mark-dark.png", True)):
        img, w, h = render_mark(1200, SS=2, dark=dark)
        n = write_png(os.path.join(OUT, name), img, w, h)
        print(name, w, h, n)
    # Motion: breathing mark, mark-only frames -> mp4 (frames kept out of output)
    tmp = "/tmp/forma_frames"
    os.makedirs(tmp, exist_ok=True)
    fps, secs = 24, 5
    total = fps * secs
    for i in range(total):
        morph = i / total
        img, w, h = render_mark(640, SS=1, dark=False, morph=morph)
        write_png(os.path.join(tmp, f"f{i:03d}.png"), img, w, h)
        if i % 24 == 0:
            print("frame", i)
    out_mp4 = os.path.join(OUT, "forma-logo-motion.mp4")
    subprocess.run(["ffmpeg", "-y", "-framerate", str(fps), "-i", os.path.join(tmp, "f%03d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                    "-movflags", "+faststart", out_mp4], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("mp4", os.path.getsize(out_mp4))

if __name__ == "__main__":
    main()
