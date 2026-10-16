#!/usr/bin/env python3
"""
forma — generative AI logo generator
Organic shapes, neutral tones. Pure stdlib; uses macOS `sips` for PNG
rasterisation when available, ffmpeg for the MP4 bloom animation.
Outputs are written to ../output (relative to this file's parent's parent).
"""
import math
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")
os.makedirs(OUT, exist_ok=True)

# --- palette (neutral, warm) ---
INK = "#2C2A26"        # charcoal
INK_SOFT = "#3A3732"
TAUPE = "#A99B85"
SAND = "#CDBD9E"
SAND_LIGHT = "#EDE8DD"
BONE = "#FBF9F4"
BONE2 = "#F5F1E8"
STONE = "#8B8478"
STONE_LIGHT = "#B9B0A0"
DARK_BG = "#23211E"
DARK_TAUPE = "#B8AB93"
DARK_SAND = "#8E8474"

FONT = "'Helvetica Neue', Inter, 'Segoe UI', Arial, sans-serif"

# One organic petal, pointing north — rounded bloom petal with a wide base
PETAL = (
    "M 208 246 "
    "C 196 206, 202 158, 224 136 "
    "C 234 127, 246 127, 256 137 "
    "C 274 158, 280 206, 272 246 "
    "C 254 255, 220 255, 208 246 Z"
)
# central vein of the petal
VEIN = "M 240 238 C 236 198, 237 162, 243 140"
# large soft enclosing blob (wobbly, hand-grown feel)
BLOB = (
    "M 242 52 "
    "C 298 50, 360 88, 382 152 "
    "C 404 218, 388 292, 338 340 "
    "C 288 388, 196 400, 138 356 "
    "C 80 312, 62 226, 84 156 "
    "C 106 88, 186 54, 242 52 Z"
)


def petal_group(fill, angle, sx=1.0, sy=1.0, opacity=1.0, vein_opacity=0.45, scale=1.0, extra_rot=0.0):
    """Return SVG for one petal (used with static transforms)."""
    # transform about centre 240,240: T * R * S * T-1
    tr = (
        f"translate(240 240) rotate({angle + extra_rot:.2f}) "
        f"scale({sx * scale:.4f} {sy * scale:.4f}) translate(-240 -240)"
    )
    vein = (
        f'<path d="{VEIN}" fill="none" stroke="{BONE}" stroke-width="1.6" '
        f'stroke-linecap="round" opacity="{vein_opacity}" transform="{tr}"/>'
    )
    return (
        f'<g opacity="{opacity}">'
        f'<path d="{PETAL}" fill="{fill}" transform="{tr}"/>'
        f"{vein}</g>"
    )


def mark_svg_inner(dark=False, anim=None):
    """
    Return the inner SVG for the mark (480x480 coordinate space).
    If anim is a dict, it supplies per-element scale/opacity/rotation for a frame.
    anim keys: blob_s, blob_o, p1_s,p1_o,p1_r, p2_s..., seed_s, seed_o, nodes_o
    """
    if dark:
        c_blob, c1, c2, c3 = "#2E2B27", BONE2, DARK_TAUPE, DARK_SAND
        c_seed_ring, c_seed_dot, c_dot = DARK_BG, BONE2, BONE2
    else:
        c_blob, c1, c2, c3 = SAND_LIGHT, INK, TAUPE, SAND
        c_seed_ring, c_seed_dot, c_dot = BONE, INK, INK

    if anim is None:
        # static mark
        blob = f'<path d="{BLOB}" fill="{c_blob}"/>'
        petals = (
            petal_group(c3, 238, sx=1.04, sy=0.96, vein_opacity=0.55, scale=1.55)
            + petal_group(c2, 122, sx=0.94, sy=1.02, vein_opacity=0.40, scale=1.55)
            + petal_group(c1, 0, sx=1.0, sy=1.0, vein_opacity=0.50, scale=1.55)
        )
        seed = (
            f'<circle cx="240" cy="240" r="22" fill="{c_seed_ring}"/>'
            f'<circle cx="240" cy="240" r="9" fill="{c_seed_dot}"/>'
            f'<circle cx="243.5" cy="236.5" r="3" fill="{TAUPE}"/>'
        )
        nodes = (
            f'<circle cx="404" cy="118" r="4.5" fill="{c2}" opacity="0.9"/>'
            f'<circle cx="76" cy="118" r="3" fill="{STONE}" opacity="0.7"/>'
        )
        connectors = ""
        return blob + connectors + petals + nodes + seed

    # animated frame
    bs, bo = anim.get("blob_s", 1.0), anim.get("blob_o", 1.0)
    blob_tr = f"translate(240 240) scale({bs:.4f}) translate(-240 -240)"
    blob = f'<g opacity="{bo:.3f}"><path d="{BLOB}" fill="{c_blob}" transform="{blob_tr}"/></g>'

    def apet(fill, angle, key_s, key_o, key_r, sx, sy, vo):
        s = anim.get(key_s, 1.0)
        o = anim.get(key_o, 1.0)
        r = anim.get(key_r, 0.0)
        return petal_group(fill, angle, sx=sx, sy=sy, vein_opacity=vo, scale=s * 1.55, opacity=o, extra_rot=r)

    petals = (
        apet(c3, 238, "p3_s", "p3_o", "p3_r", 1.04, 0.96, 0.55)
        + apet(c2, 122, "p2_s", "p2_o", "p2_r", 0.94, 1.02, 0.40)
        + apet(c1, 0, "p1_s", "p1_o", "p1_r", 1.0, 1.0, 0.50)
    )
    ss, so = anim.get("seed_s", 1.0), anim.get("seed_o", 1.0)
    seed_tr = f"translate(240 240) scale({ss:.4f}) translate(-240 -240)"
    seed = (
        f'<g opacity="{so:.3f}" transform="{seed_tr}">'
        f'<circle cx="240" cy="240" r="22" fill="{c_seed_ring}"/>'
        f'<circle cx="240" cy="240" r="9" fill="{c_seed_dot}"/>'
        f'<circle cx="243.5" cy="236.5" r="3" fill="{TAUPE}"/></g>'
    )
    no = anim.get("nodes_o", 1.0)
    nodes = (
        f'<g opacity="{no:.3f}">'
        f'<circle cx="404" cy="118" r="4.5" fill="{c2}"/>'
        f'<circle cx="76" cy="118" r="3" fill="{STONE}"/></g>'
    )
    connectors = ""
    return blob + connectors + petals + nodes + seed


def svg_primary(dark=False, width=1240, height=440):
    bg = DARK_BG if dark else BONE
    word = BONE2 if dark else INK
    tag = "#A79E90" if dark else STONE
    rule = DARK_TAUPE if dark else SAND
    inner = mark_svg_inner(dark=dark)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 1240 440" role="img" aria-labelledby="t d">
  <title id="t">forma — generative intelligence</title>
  <desc id="d">Three organic petals blooming from a central seed inside a soft wobbly blob, in warm neutral tones.</desc>
  <rect width="1240" height="440" fill="{bg}"/>
  <g transform="translate(52 32) scale(0.7833)">{inner}</g>
  <text x="478" y="232" font-family="{FONT}" font-size="118" font-weight="560" letter-spacing="-3.5" fill="{word}">forma</text>
  <rect x="482" y="262" width="54" height="3" rx="1.5" fill="{rule}"/>
  <text x="482" y="300" font-family="{FONT}" font-size="16" font-weight="600" letter-spacing="6.2" fill="{tag}">GENERATIVE INTELLIGENCE</text>
  <text x="482" y="338" font-family="{FONT}" font-size="14.5" font-weight="400" letter-spacing="0.4" fill="{tag}" opacity="0.85">Organic systems for generative AI</text>
</svg>
"""


def svg_mark(width=480, height=480, dark=False):
    inner = mark_svg_inner(dark=dark)
    bg = f'<rect width="480" height="480" fill="{DARK_BG}"/>' if dark else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 480 480" role="img" aria-labelledby="t d">
  <title id="t">forma mark</title>
  <desc id="d">Organic generative bloom mark in neutral tones.</desc>
  {bg}{inner}
</svg>
"""


def svg_stacked(width=720, height=760):
    inner = mark_svg_inner(dark=False)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 720 760" role="img" aria-labelledby="t d">
  <title id="t">forma — stacked lockup</title>
  <desc id="d">Generative bloom mark above the forma wordmark.</desc>
  <rect width="720" height="760" fill="{BONE}"/>
  <g transform="translate(120 36)">{inner}</g>
  <text x="360" y="612" text-anchor="middle" font-family="{FONT}" font-size="92" font-weight="560" letter-spacing="-2.5" fill="{INK}">forma</text>
  <rect x="333" y="634" width="54" height="3" rx="1.5" fill="{SAND}"/>
  <text x="360" y="672" text-anchor="middle" font-family="{FONT}" font-size="13.5" font-weight="600" letter-spacing="5.4" fill="{STONE}">GENERATIVE INTELLIGENCE</text>
</svg>
"""


def write_svg(name, content):
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote {p} ({len(content)} bytes)")
    return p


def svg_to_png(svg_path, png_path, w, h):
    """Rasterise SVG to PNG. Prefer macOS sips (accurate text), else note skip."""
    if shutil.which("sips") is None:
        print("  sips not found — skipping PNG (SVG remains the master)")
        return False
    # sips renders at the SVG's intrinsic size; write a temp SVG sized w x h
    with open(svg_path, encoding="utf-8") as f:
        data = f.read()
    # replace first width/height occurrence with target size
    import re
    data2 = re.sub(r'width="[^"]+"', f'width="{w}"', data, count=1)
    data2 = re.sub(r'height="[^"]+"', f'height="{h}"', data2, count=1)
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False, encoding="utf-8") as tf:
        tf.write(data2)
        tmp = tf.name
    try:
        r = subprocess.run(["sips", "-s", "format", "png", tmp, "--out", png_path],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(png_path):
            print("  sips failed:", r.stdout[-300:], r.stderr[-300:])
            return False
        print(f"  png {png_path} ({os.path.getsize(png_path)} bytes)")
        return True
    finally:
        os.unlink(tmp)


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def ease_out_back(t, s=1.35):
    t = max(0.0, min(1.0, t))
    return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2


def clamp01(x):
    return max(0.0, min(1.0, x))


def frame_state(t):
    """t in [0,1] over the whole animation -> anim dict."""
    # blob 0.00-0.35, petals staggered, seed, nodes, hold
    blob_p = ease_out_cubic(clamp01(t / 0.32))
    def petal(start, dur=0.38):
        p = clamp01((t - start) / dur)
        return ease_out_back(p), ease_out_cubic(p), (1 - ease_out_cubic(p)) * -14
    s1, o1, r1 = petal(0.22)
    s2, o2, r2 = petal(0.38)
    s3, o3, r3 = petal(0.54)
    seed_p = clamp01((t - 0.78) / 0.22)
    return {
        "blob_s": 0.72 + 0.28 * blob_p, "blob_o": blob_p,
        "p1_s": max(0.001, s1), "p1_o": o1, "p1_r": r1,
        "p2_s": max(0.001, s2), "p2_o": o2, "p2_r": r2,
        "p3_s": max(0.001, s3), "p3_o": o3, "p3_r": r3,
        "seed_s": max(0.001, ease_out_back(seed_p)), "seed_o": ease_out_cubic(seed_p),
        "nodes_o": ease_out_cubic(clamp01((t - 0.82) / 0.18)),
    }


def svg_frame(t, size=1080):
    st = frame_state(t)
    inner = mark_svg_inner(dark=False, anim=st)
    # wordmark fades in near the end
    wp = ease_out_cubic(clamp01((t - 0.80) / 0.20))
    wy = 872 - 14 * wp
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 1080 1080">
  <rect width="1080" height="1080" fill="{BONE}"/>
  <g transform="translate(180 92) scale(1.5)">{inner}</g>
  <g opacity="{wp:.3f}">
    <text x="540" y="{wy:.1f}" text-anchor="middle" font-family="{FONT}" font-size="92" font-weight="560" letter-spacing="-2.5" fill="{INK}">forma</text>
    <rect x="513" y="{wy + 18:.1f}" width="54" height="3" rx="1.5" fill="{SAND}"/>
    <text x="540" y="{wy + 52:.1f}" text-anchor="middle" font-family="{FONT}" font-size="13.5" font-weight="600" letter-spacing="5.4" fill="{STONE}">GENERATIVE INTELLIGENCE</text>
  </g>
</svg>
"""


def build_animation(fps=20, seconds=5.0, size=900):
    if shutil.which("sips") is None or shutil.which("ffmpeg") is None:
        print("animation skipped: need sips + ffmpeg")
        return None
    frames = int(fps * seconds)
    tmpdir = tempfile.mkdtemp(prefix="forma-frames-")
    print(f"animation: {frames} frames @ {fps}fps in {tmpdir}")
    try:
        for i in range(frames):
            # ease timeline: fast bloom then a gentle hold (duplicate end via t curve)
            t = i / max(1, frames - 1)
            t = min(1.0, t / 0.88) if t < 0.88 else 1.0  # hold last ~12%
            svg_p = os.path.join(tmpdir, f"f{i:03d}.svg")
            png_p = os.path.join(tmpdir, f"f{i:03d}.png")
            with open(svg_p, "w", encoding="utf-8") as f:
                f.write(svg_frame(t, size=size))
            r = subprocess.run(["sips", "-s", "format", "png", svg_p, "--out", png_p],
                               capture_output=True, text=True)
            if r.returncode != 0:
                print("  frame render failed", i, r.stderr[-200:])
                return None
            os.unlink(svg_p)
        out_mp4 = os.path.join(OUT, "forma-logo-animation.mp4")
        cmd = ["ffmpeg", "-y", "-framerate", str(fps), "-i", os.path.join(tmpdir, "f%03d.png"),
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
               "-movflags", "+faststart", "-vf", "scale=900:900", out_mp4]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print("  ffmpeg failed:", r.stderr[-600:])
            return None
        print(f"  mp4 {out_mp4} ({os.path.getsize(out_mp4)} bytes)")
        return out_mp4
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
        print("  frames cleaned up")


def main():
    p1 = write_svg("forma-logo.svg", svg_primary(dark=False))
    p2 = write_svg("forma-mark.svg", svg_mark())
    p3 = write_svg("forma-logo-dark.svg", svg_primary(dark=True))
    # PNG exports (retina-ish sizes, aspect preserved by intrinsic resize)
    svg_to_png(p1, os.path.join(OUT, "forma-logo.png"), 2480, 880)
    svg_to_png(p2, os.path.join(OUT, "forma-mark.png"), 1200, 1200)
    build_animation()
    print("done ->", OUT)
    for n in sorted(os.listdir(OUT)):
        fp = os.path.join(OUT, n)
        print(f"  {n:28s} {os.path.getsize(fp):>8d} bytes")


if __name__ == "__main__":
    main()
