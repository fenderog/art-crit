#!/usr/bin/env python3
"""Generate an organic SVG logo for a generative AI company.

Company: TERRENE — Generative Intelligence
Concept: a warm stone-like pebble holding a mycelium/neural network
(growth + computation), with sage and clay satellite blobs budding off
it like spores — a "generative bloom". Neutral earthy palette.
Standard library only.
"""
import math

# ---------- palette (neutral tones) ----------
PAPER = "#F4EFE6"
PAPER_DEEP = "#EAE2D2"
STONE = "#E3DAC6"
STONE_EDGE = "#CFC4AD"
TAUPE = "#A99B86"
TAUPE_SOFT = "#C4B9A4"
BARK = "#3B3732"
BARK_SOFT = "#5C564E"
SAGE = "#9CA48E"
SAGE_DEEP = "#75806A"
CLAY = "#C39B7A"
CLAY_DEEP = "#9C7256"
MOSS_LINE = "#77705F"
CREAM_TEXT = "#F1EAD9"
DARK_BG = "#292622"


def blob_path(cx, cy, base_r, harmonics, n=14, phase=0.0):
    """Organic closed blob as smooth path.

    harmonics: list of (amplitude, frequency, phase_offset).
    Returns SVG path string using Catmull-Rom -> Bezier smoothing.
    """
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n + phase
        r = base_r
        for amp, freq, po in harmonics:
            r += base_r * amp * math.sin(freq * t + po)
        x = cx + r * math.cos(t)
        y = cy + r * math.sin(t) * 0.94  # slightly squashed, pebble-like
        pts.append((x, y))

    # Catmull-Rom to Bezier closed spline
    d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f} "
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        c1x = p1[0] + (p2[0] - p0[0]) / 6.0
        c1y = p1[1] + (p2[1] - p0[1]) / 6.0
        c2x = p2[0] - (p3[0] - p1[0]) / 6.0
        c2y = p2[1] - (p3[1] - p1[1]) / 6.0
        d += f"C {c1x:.1f} {c1y:.1f} {c2x:.1f} {c2y:.1f} {p2[0]:.1f} {p2[1]:.1f} "
    return d + "Z"


def curved_edge(x1, y1, x2, y2, bend=0.18):
    """Gentle quadratic curve between two nodes (organic, not straight)."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1
    # perpendicular offset, direction alternates by position for variety
    side = 1 if (x1 * 0.7 + y1 * 1.3) % 2 < 1 else -1
    off = length * bend * side
    cx = mx - dy / length * off
    cy = my + dx / length * off
    return f"M {x1:.1f} {y1:.1f} Q {cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}"


def mark_group(cx, cy, scale=1.0, uid=""):
    """The logo mark: pebble + mycelium network + satellite blobs."""
    s = scale
    # Main pebble + soft inner depth blob
    main_d = blob_path(cx, cy, 172 * s,
                       [(0.055, 2, 0.6), (0.038, 3, 2.1), (0.022, 5, 4.0)],
                       n=16, phase=0.3)
    depth_d = blob_path(cx - 28 * s, cy + 30 * s, 128 * s,
                        [(0.07, 2, 1.9), (0.045, 3, 0.4), (0.02, 6, 2.6)],
                        n=14, phase=1.1)
    # Satellites (budding spores)
    sage_d = blob_path(cx + 168 * s, cy - 118 * s, 62 * s,
                       [(0.09, 2, 0.9), (0.05, 3, 3.0)], n=12, phase=0.7)
    clay_d = blob_path(cx + 178 * s, cy + 108 * s, 40 * s,
                       [(0.10, 2, 2.2), (0.05, 4, 1.0)], n=12, phase=2.0)

    # Mycelium / neural nodes (local coords around centre)
    nodes = [
        (0, 0, 11.0, BARK),        # heart
        (-72, -44, 7.5, CLAY_DEEP),
        (62, -62, 6.5, SAGE_DEEP),
        (-34, 62, 8.0, BARK_SOFT),
        (82, 32, 5.5, TAUPE),
        (-112, 22, 4.5, TAUPE),
        (18, -108, 4.5, SAGE_DEEP),
        (112, -18, 4.0, CLAY),
        (-52, -102, 3.6, TAUPE),
        (-96, -78, 3.0, TAUPE_SOFT),
        (44, 104, 4.2, CLAY_DEEP),
        (118, 74, 3.2, TAUPE_SOFT),
    ]
    edges = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 5), (1, 9),
             (2, 6), (2, 7), (3, 10), (4, 7), (4, 11), (1, 8), (8, 6)]

    parts = []
    parts.append(f'<path d="{main_d}" fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="{2*s:.1f}"/>')
    parts.append(f'<path d="{depth_d}" fill="{TAUPE}" opacity="0.28"/>')
    # faint growth-ring arcs inside pebble for an organic feel
    parts.append(
        f'<ellipse cx="{cx-10*s:.0f}" cy="{cy+6*s:.0f}" rx="{120*s:.0f}" ry="{104*s:.0f}" '
        f'fill="none" stroke="{TAUPE_SOFT}" stroke-width="{1.4*s:.1f}" opacity="0.55" '
        f'transform="rotate(-12 {cx:.0f} {cy:.0f})"/>')
    parts.append(
        f'<ellipse cx="{cx-10*s:.0f}" cy="{cy+6*s:.0f}" rx="{88*s:.0f}" ry="{74*s:.0f}" '
        f'fill="none" stroke="{TAUPE_SOFT}" stroke-width="{1.2*s:.1f}" opacity="0.45" '
        f'transform="rotate(-12 {cx:.0f} {cy:.0f})"/>')
    # tilted orbit ring — the "generative / orbital" hint
    parts.append(
        f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{150*s:.0f}" ry="{52*s:.0f}" fill="none" '
        f'stroke="{MOSS_LINE}" stroke-width="{1.6*s:.1f}" opacity="0.7" '
        f'transform="rotate(-18 {cx:.0f} {cy:.0f})" stroke-dasharray="{7*s:.0f} {6*s:.0f}"/>')

    # edges
    edge_ds = []
    for a, b in edges:
        x1, y1 = cx + nodes[a][0] * s, cy + nodes[a][1] * s
        x2, y2 = cx + nodes[b][0] * s, cy + nodes[b][1] * s
        edge_ds.append(curved_edge(x1, y1, x2, y2))
    parts.append(
        f'<g fill="none" stroke="{MOSS_LINE}" stroke-width="{2.2*s:.1f}" '
        f'stroke-linecap="round" opacity="0.85">'
        + "".join(f'<path d="{d}"/>' for d in edge_ds) + '</g>')

    # nodes
    node_els = []
    for lx, ly, r, fill in nodes:
        node_els.append(
            f'<circle cx="{cx + lx*s:.1f}" cy="{cy + ly*s:.1f}" r="{r*s:.1f}" '
            f'fill="{fill}" stroke="{PAPER}" stroke-width="{1.6*s:.1f}"/>')
    parts.append("<g>" + "".join(node_els) + "</g>")

    # satellites + spore trail
    parts.append(f'<path d="{sage_d}" fill="{SAGE}"/>')
    parts.append(f'<circle cx="{cx+152*s:.0f}" cy="{cy-134*s:.0f}" r="{7*s:.1f}" fill="{PAPER}" opacity="0.55"/>')
    parts.append(f'<path d="{clay_d}" fill="{CLAY}"/>')
    parts.append(f'<circle cx="{cx+170*s:.0f}" cy="{cy+98*s:.0f}" r="{4.5*s:.1f}" fill="{PAPER}" opacity="0.5"/>')
    spores = [(228, -52, 5.0, 0.75), (252, -28, 3.6, 0.55), (272, -6, 2.4, 0.35)]
    for lx, ly, r, op in spores:
        parts.append(
            f'<circle cx="{cx+lx*s:.0f}" cy="{cy+ly*s:.0f}" r="{r*s:.1f}" '
            f'fill="{TAUPE}" opacity="{op}"/>')

    return '<g id="mark%s">\n' % uid + "\n".join(parts) + "\n</g>"


def wordmark(x, y, title_fill, sub_fill):
    # +half letter-spacing on x compensates the trailing spacing SVG adds
    # after the last glyph so optically centred text stays centred.
    return f"""
  <text x="{x+11}" y="{y}" text-anchor="middle"
        font-family="Georgia, 'Times New Roman', serif" font-size="72"
        letter-spacing="22" fill="{title_fill}" font-weight="500">TERRENE</text>
  <g stroke="{sub_fill}" stroke-width="1" opacity="0.8">
    <line x1="{x-440}" y1="{y+52}" x2="{x-315}" y2="{y+52}"/>
    <line x1="{x+315}" y1="{y+52}" x2="{x+440}" y2="{y+52}"/>
  </g>
  <text x="{x+3.75}" y="{y+60}" text-anchor="middle"
        font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="20"
        letter-spacing="7.5" fill="{sub_fill}">GENERATIVE INTELLIGENCE</text>"""


def logo_svg(dark=False):
    bg = DARK_BG if dark else PAPER
    title_fill = CREAM_TEXT if dark else BARK
    sub_fill = TAUPE if dark else "#857A66"
    deep = "#211F1C" if dark else PAPER_DEEP
    gid = "d" if dark else "l"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000" role="img" aria-label="Terrene — Generative Intelligence logo">
  <title>Terrene — Generative Intelligence</title>
  <defs>
    <radialGradient id="bg{gid}" cx="50%" cy="42%" r="75%">
      <stop offset="0%" stop-color="{bg}"/>
      <stop offset="100%" stop-color="{deep}"/>
    </radialGradient>
  </defs>
  <rect width="1600" height="1000" fill="url(#bg{gid})"/>
  {mark_group(780, 400, 1.0, gid)}
  {wordmark(800, 760, title_fill, sub_fill)}
</svg>
"""


def mark_only_svg():
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800" role="img" aria-label="Terrene mark">
  <title>Terrene mark</title>
  <defs>
    <radialGradient id="bgm" cx="50%" cy="42%" r="80%">
      <stop offset="0%" stop-color="{PAPER}"/>
      <stop offset="100%" stop-color="{PAPER_DEEP}"/>
    </radialGradient>
  </defs>
  <rect width="800" height="800" fill="url(#bgm)"/>
  {mark_group(400, 400, 1.18, "m")}
</svg>
"""


def main():
    files = {
        "output/terrene-logo.svg": logo_svg(dark=False),
        "output/terrene-logo-dark.svg": logo_svg(dark=True),
        "output/terrene-mark.svg": mark_only_svg(),
    }
    for path, content in files.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"wrote {path} ({len(content.encode('utf-8'))} bytes)")


if __name__ == "__main__":
    main()
