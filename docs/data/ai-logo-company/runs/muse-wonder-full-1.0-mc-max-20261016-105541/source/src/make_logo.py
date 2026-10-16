#!/usr/bin/env python3
"""
Spora — generative AI identity.

The mark is a seed head literally *generated* the way nature generates one:
41 seeds placed by golden-angle (137.5 deg) phyllotaxis with sqrt(n) radial
growth, held inside a soft harmonic "blob" envelope (radius modulated by a
few low sine harmonics). One spore escapes the envelope: generation / emergence.

Palette is entirely warm neutrals — bone, sand, clay, taupe, bark, ink —
deliberately avoiding the blue/purple gradient cliche of AI branding.
"""
import math
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "output")

# ---------------------------------------------------------------- palette
BONE  = "#ECE6DA"
SAND  = "#D9CFBC"
CLAY  = "#B9A88F"
TAUPE = "#8D7E68"
BARK  = "#574C3E"
INK   = "#2B2721"
PAPER = "#FAF7F0"
SHEET = "#EFEAE0"
RULE  = "#DDD5C6"

FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"

# ---------------------------------------------------------------- helpers
def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def lerp_color(c1, c2, t):
    a, b = hex2rgb(c1), hex2rgb(c2)
    return "#%02X%02X%02X" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

def ramp(stops, t):
    """Piecewise-linear colour ramp through `stops`."""
    if t <= 0:
        return stops[0]
    if t >= 1:
        return stops[-1]
    pos = t * (len(stops) - 1)
    i = int(pos)
    return lerp_color(stops[i], stops[i + 1], pos - i)

BLOB_ROT = -0.30  # slight tilt so the envelope leans toward the escaping spores

def blob_points(cx, cy, R, n=72, phase=0.0):
    """Organic envelope: circle with radius modulated by low harmonics."""
    pts = []
    cos_r, sin_r = math.cos(BLOB_ROT), math.sin(BLOB_ROT)
    for i in range(n):
        th = 2 * math.pi * i / n
        r = R * (1
                 + 0.021 * math.sin(3 * th + 0.9 + phase)
                 + 0.013 * math.sin(5 * th + 2.4 + phase)
                 + 0.008 * math.cos(2 * th - 0.6 + phase))
        x, y = r * math.cos(th), r * math.sin(th)
        pts.append((cx + x * cos_r - y * sin_r, cy + x * sin_r + y * cos_r))
    return pts

def smooth_closed_path(pts):
    """Catmull-Rom -> cubic Bezier closed path."""
    n = len(pts)
    d = [f"M {pts[0][0]:.2f} {pts[0][1]:.2f}"]
    for i in range(n):
        p0, p1 = pts[i - 1], pts[i]
        p2, p3 = pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C {c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} "
                 f"{p2[0]:.2f} {p2[1]:.2f}")
    d.append("Z")
    return " ".join(d)

GOLDEN = math.pi * (3 - math.sqrt(5))   # golden angle ~137.508 deg in radians

def phyllo(cx, cy, R, n=41, max_frac=0.72, rot=-0.6):
    """Yield (x, y, dot_radius, t) for each seed, centre first."""
    max_r = R * max_frac
    for i in range(n):
        rr = max_r * math.sqrt((i + 0.5) / n)
        th = i * GOLDEN + rot
        t = rr / max_r if max_r else 0.0
        dot_r = R * (0.037 + 0.030 * t)
        yield cx + rr * math.cos(th), cy + rr * math.sin(th), dot_r, t

def mark(cx, cy, R, blob_fill, dot_stops, escape_cols, n=41, dot_scale=1.0):
    """Full colour/gradient-ramp mark as an SVG group string."""
    parts = [f'<path d="{smooth_closed_path(blob_points(cx, cy, R))}" fill="{blob_fill}"/>']
    for x, y, r, t in phyllo(cx, cy, R, n=n):
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r * dot_scale:.2f}" '
                     f'fill="{ramp(dot_stops, t)}"/>')
    # escaped spores, drifting up-right on a gentle arc
    for (dist, ang_deg, r_frac), col in zip(
            [(1.10, -44, 0.056), (1.24, -37, 0.039), (1.35, -30, 0.025)],
            escape_cols):
        a = math.radians(ang_deg)
        parts.append(f'<circle cx="{cx + dist * R * math.cos(a):.2f}" '
                     f'cy="{cy + dist * R * math.sin(a):.2f}" '
                     f'r="{R * r_frac:.2f}" fill="{col}"/>')
    return "".join(parts)

def mark_color(cx, cy, R, n=41, dot_scale=1.0):
    """Primary mark: ink envelope, bone->clay seeds, clay->bark spores."""
    return mark(cx, cy, R, INK, ["#F2EBDB", SAND, CLAY, "#A08F74"],
                [CLAY, TAUPE, BARK], n=n, dot_scale=dot_scale)

def mark_reversed(cx, cy, R, n=41, dot_scale=1.0):
    """For dark grounds: bone envelope, ink->taupe seeds, sand spores."""
    return mark(cx, cy, R, BONE, [INK, BARK, TAUPE],
                [SAND, CLAY, BONE], n=n, dot_scale=dot_scale)

def mark_mono(cx, cy, R, ink=INK, ground=BONE, n=41, dot_scale=1.0):
    """Single-colour mark: seeds knocked out to the ground colour."""
    return mark(cx, cy, R, ink, [ground, ground], [ink, ink, ink],
                n=n, dot_scale=dot_scale)

def T(x, y, s, size, fill, weight=400, ls=None, anchor="start", extra=""):
    ls_attr = f' letter-spacing="{ls}"' if ls is not None else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"'
            f'{ls_attr}{extra and " " + extra}>{s}</text>')

def wordmark(x, y, size, fill, anchor="start", dot=CLAY, weight=600, ls=-2):
    # No punctuation: the seeds in the mark already supply the dots, and a
    # typeset period renders as an off-brand square in Helvetica/Arial.
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'letter-spacing="{ls}">spora</text>')

def svg_doc(w, h, body, title, desc):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{title}">\n'
            f'<title>{title}</title>\n<desc>{desc}</desc>\n{body}\n</svg>\n')

def save(name, content):
    path = os.path.normpath(os.path.join(OUT, name))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  {name}: {len(content.encode('utf-8'))} bytes")

DESC = ("Spora logo: 41 seeds placed by golden-angle phyllotaxis inside an "
        "organic harmonic envelope, one spore escaping. Warm neutral palette.")

# ---------------------------------------------------------------- files
def primary_logo():
    body = (
        mark_color(132, 130, 92)
        + wordmark(268, 144, 88, INK)
        + T(273, 188, "GENERATIVE INTELLIGENCE", 16, TAUPE, weight=600, ls=5.5)
    )
    save("spora-logo.svg",
         svg_doc(660, 260, body, "Spora — primary logo", DESC))

def dark_logo():
    body = (
        f'<rect width="600" height="580" fill="{INK}"/>'
        + mark_reversed(300, 232, 148)
        + wordmark(300, 462, 84, BONE, anchor="middle", dot=CLAY)
        + T(303, 504, "GENERATIVE INTELLIGENCE", 15, SAND,
            weight=600, ls=5.5, anchor="middle")
    )
    save("spora-logo-dark.svg",
         svg_doc(600, 580, body, "Spora — stacked logo on ink", DESC))

def mark_only():
    body = mark_color(228, 256, 178)
    save("spora-mark.svg", svg_doc(480, 480, body, "Spora — mark", DESC))

# ---------------------------------------------------------------- brand board
def rrect(x, y, w, h, rx, fill, stroke=None, sw=1, extra=""):
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"')
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    return s + (f" {extra}" if extra else "") + "/>"

def panel_title(x, y, s, fill=INK):
    return T(x, y, s, 15, fill, weight=700, ls=3)

def construction(cx, cy, R):
    p = []
    for frac in (0.35, 0.70, 1.0):
        p.append(f'<circle cx="{cx}" cy="{cy}" r="{R * frac:.1f}" fill="none" '
                 f'stroke="{CLAY}" stroke-width="1" stroke-dasharray="4 5" opacity="0.8"/>')
    p.append(f'<line x1="{cx - R * 1.18:.0f}" y1="{cy}" x2="{cx + R * 1.18:.0f}" y2="{cy}" '
             f'stroke="{CLAY}" stroke-width="1" stroke-dasharray="4 5" opacity="0.6"/>')
    p.append(f'<line x1="{cx}" y1="{cy - R * 1.18:.0f}" x2="{cx}" y2="{cy + R * 1.18:.0f}" '
             f'stroke="{CLAY}" stroke-width="1" stroke-dasharray="4 5" opacity="0.6"/>')
    pts = list(phyllo(cx, cy, R))
    # Smooth Fermat spiral through the seeds in generation order.
    spiral = []
    s = 0.0
    while s <= 41.0:
        rr = R * 0.72 * math.sqrt(max(s, 0.0) / 41)
        th = s * GOLDEN - 0.6
        spiral.append(f"{cx + rr * math.cos(th):.1f},{cy + rr * math.sin(th):.1f}")
        s += 0.2
    p.append(f'<polyline points="{" ".join(spiral)}" fill="none" stroke="{TAUPE}" '
             f'stroke-width="1.2" opacity="0.5"/>')
    p.append(f'<path d="{smooth_closed_path(blob_points(cx, cy, R))}" fill="none" '
             f'stroke="{INK}" stroke-width="2.2"/>')
    for x, y, r, _ in pts:
        p.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{INK}"/>')
    a = math.radians(-44)
    p.append(f'<circle cx="{cx + 1.10 * R * math.cos(a):.2f}" '
             f'cy="{cy + 1.10 * R * math.sin(a):.2f}" r="{R * 0.056:.2f}" fill="{BARK}"/>')
    return "".join(p)

def brand_board():
    b = []
    b.append(f'<rect width="1600" height="1200" fill="{SHEET}"/>')

    # header
    b.append(T(56, 56, "SPORA — BRAND MARK", 16, INK, weight=700, ls=3))
    b.append(T(1544, 56, "GENERATIVE INTELLIGENCE · IDENTITY SHEET 01",
               14, TAUPE, weight=600, ls=2.5, anchor="end"))
    b.append(f'<line x1="56" y1="80" x2="1544" y2="80" stroke="{CLAY}" stroke-width="1.4"/>')

    # hero — primary lockup
    b.append(rrect(56, 106, 880, 430, 26, PAPER, RULE))
    b.append(mark_color(258, 298, 126))
    b.append(wordmark(442, 330, 112, INK, ls=-3))
    b.append(T(449, 382, "GENERATIVE INTELLIGENCE", 19, TAUPE, weight=600, ls=6))
    b.append(panel_title(92, 484, "PRIMARY LOCKUP"))
    b.append(T(92, 512, "Grown, not built — a seed head generated by golden-angle phyllotaxis.",
               16.5, TAUPE))

    # dark — reversed
    b.append(rrect(968, 106, 576, 430, 26, INK))
    b.append(mark_reversed(1256, 252, 100))
    b.append(wordmark(1256, 428, 64, BONE, anchor="middle"))
    b.append(T(1259, 464, "GENERATIVE INTELLIGENCE", 12.5, SAND,
               weight=600, ls=4.5, anchor="middle"))
    b.append(panel_title(1004, 506, "ON INK / REVERSED", fill=SAND))

    # construction
    b.append(rrect(56, 568, 500, 300, 26, PAPER, RULE))
    b.append(panel_title(92, 614, "CONSTRUCTION"))
    b.append(construction(196, 736, 80))
    labels = ["137.5° golden angle", "41 seeds · √n growth",
              "soft harmonic envelope", "released spore trail"]
    for i, s in enumerate(labels):
        y = 684 + i * 42
        b.append(f'<circle cx="320" cy="{y - 5}" r="3.4" fill="{CLAY}"/>')
        b.append(T(336, y, s, 16, BARK))

    # palette
    b.append(rrect(588, 568, 500, 300, 26, PAPER, RULE))
    b.append(panel_title(624, 614, "PALETTE — WARM NEUTRALS"))
    swatches = [("Bone", BONE), ("Sand", SAND), ("Clay", CLAY),
                ("Taupe", TAUPE), ("Bark", BARK), ("Ink", INK)]
    for i, (name, col) in enumerate(swatches):
        cx = 692 + (i % 3) * 148
        cy = 678 + (i // 3) * 108
        b.append(f'<circle cx="{cx}" cy="{cy}" r="31" fill="{col}" '
                 f'stroke="{RULE}" stroke-width="1"/>')
        b.append(T(cx, cy + 52, name, 15, INK, weight=600, anchor="middle"))
        b.append(T(cx, cy + 72, col, 12.5, TAUPE, anchor="middle"))

    # variations
    b.append(rrect(1120, 568, 424, 300, 26, PAPER, RULE))
    b.append(panel_title(1156, 614, "MARK VARIATIONS"))
    b.append(mark_mono(1204, 682, 50, ground=PAPER))
    b.append(T(1204, 762, "Mono", 14, BARK, weight=600, anchor="middle"))
    b.append(mark_color(1330, 682, 50, n=19, dot_scale=1.45))
    b.append(T(1330, 762, "Small size", 14, BARK, weight=600, anchor="middle"))
    b.append(rrect(1404, 632, 100, 100, 24, INK))
    b.append(mark_reversed(1448, 688, 33))
    b.append(T(1454, 762, "App icon", 14, BARK, weight=600, anchor="middle"))
    b.append(f'<line x1="1156" y1="786" x2="1508" y2="786" stroke="{RULE}" stroke-width="1"/>')
    for cx, R, lab in [(1192, 26, "52 px"), (1298, 17, "34 px"), (1390, 11, "22 px")]:
        b.append(mark_color(cx, 820, R, n=19 if R < 20 else 41,
                            dot_scale=1.45 if R < 20 else 1.0))
        b.append(T(cx + R + 12, 825, lab, 13, TAUPE))

    # applications
    b.append(rrect(56, 900, 1488, 244, 26, PAPER, RULE))
    b.append(panel_title(92, 946, "IN CONTEXT"))
    # dark card
    b.append(rrect(92, 970, 348, 130, 12, INK))
    b.append(mark_reversed(148, 1035, 38))
    b.append(wordmark(206, 1032, 34, BONE, ls=-1))
    b.append(T(209, 1058, "GENERATIVE INTELLIGENCE", 8.5, SAND, weight=600, ls=2.6))
    # light card
    b.append(rrect(464, 970, 348, 130, 12, BONE, RULE))
    b.append(mark_color(522, 1035, 38))
    b.append(T(580, 1024, "Ana Rivera", 20, INK, weight=600))
    b.append(T(580, 1048, "Head of Research", 14, TAUPE))
    b.append(T(580, 1072, "ana@spora.ai", 14, TAUPE))
    # web header mock
    b.append(rrect(836, 970, 672, 130, 12, "#FFFFFF", RULE))
    for i, c in enumerate([CLAY, SAND, TAUPE]):
        b.append(f'<circle cx="{862 + i * 22}" cy="994" r="6" fill="{c}"/>')
    b.append(f'<line x1="836" y1="1012" x2="1508" y2="1012" stroke="{RULE}"/>')
    b.append(mark_color(878, 1062, 22, n=19, dot_scale=1.45))
    b.append(wordmark(910, 1070, 24, INK, ls=-0.5))
    for i, wdt in enumerate([58, 74, 50]):
        b.append(rrect(1064 + i * 96, 1052, wdt, 13, 6.5, SAND))
    b.append(rrect(1372, 1042, 108, 34, 17, INK))
    b.append(T(1426, 1064, "Try Spora", 14, BONE, weight=600, anchor="middle"))

    # footer
    b.append(T(800, 1178,
               "Clear space = ¼ mark width   ·   Minimum digital 24 px (small-size mark below 36 px)   ·   Minimum print 18 mm",
               14.5, TAUPE, anchor="middle"))

    save("spora-brand-board.svg",
         svg_doc(1600, 1200, "".join(b), "Spora — identity sheet",
                 DESC + " Full identity sheet: lockups, construction, palette, variations, applications."))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("Generating Spora identity ->", os.path.normpath(OUT))
    primary_logo()
    dark_logo()
    mark_only()
    brand_board()
