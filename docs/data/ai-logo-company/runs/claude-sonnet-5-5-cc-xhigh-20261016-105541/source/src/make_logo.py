"""Builds the "loam" logo set: a morphing-pebble mark plus a hand-built monoline wordmark.

Run from anywhere:  python3 -I src/make_logo.py <output-dir>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blobs import blob_points, lerp_points, smooth_path, spline_samples  # noqa: E402

# Neutral, warm-grey palette ------------------------------------------------
BONE = "#F3EFE8"
INK = "#2A2623"
INK_DEEP = "#1C1917"
LIGHT_RINGS = ["#2A2623", "#5E544A", "#8C7F70", "#B5A793", "#D6CBB9", "#EDE6DA"]
DARK_RINGS = ["#38322D", "#5E544A", "#8C7F70", "#B5A793", "#D6CBB9", "#F0E9DC"]

# Mark ------------------------------------------------------------------------
MARK_BOX = 512  # mark lives in a 512 x 512 box, centred on (256, 256)


def _bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def mark_paths(rings):
    """Six nested pebbles. Each is the same seed shape morphed a little further toward a
    second seed shape (a walk through 'latent space'), shrunk, and drifted off-centre."""
    a = blob_points(256, 256, 190, 176, rot=-0.3, n=7, amp=0.16, seed=3)
    b = blob_points(256, 256, 190, 176, rot=-0.3, n=7, amp=0.16, seed=14)
    # centre the silhouette in the box
    x0, y0, x1, y1 = _bbox(spline_samples(a))
    dx, dy = 256 - (x0 + x1) / 2, 256 - (y0 + y1) / 2
    steps = len(rings)
    out = []
    for i in range(steps):
        t = i / (steps - 1)
        s = 1 - 0.84 * t ** 0.95
        pts = lerp_points(a, b, t * 0.9)
        cx, cy = 256 + dx + 34 * t, 256 + dy + 26 * t
        pts = [(cx + (x - 256) * s, cy + (y - 256) * s) for x, y in pts]
        out.append((smooth_path(pts), rings[i]))
        if i == 0:
            bbox = _bbox(spline_samples(pts))
    return out, bbox


def mark_group(rings, transform=""):
    paths = "".join(f'<path d="{d}" fill="{c}"/>' for d, c in mark_paths(rings)[0])
    t = f' transform="{transform}"' if transform else ""
    return f'<g id="mark"{t}>{paths}</g>'


# Wordmark --------------------------------------------------------------------
# Monoline letters drawn on centre-lines with round caps/joins, baseline at y = 0.
XH = 118      # centre-line x-height
SW = 24       # stroke width
ASC = 196     # centre-line ascender height of the "l"
R = XH / 2    # bowl radius


def _f(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


# optical side-bearing gaps between centre-lines: straight|round, round|round, straight|straight
GAP_LO, GAP_OA, GAP_AM = 52, 46, 66


def wordmark_paths():
    """Returns (list of path d-strings, advance width of centre-lines)."""
    paths = []
    x = 0.0
    # l
    paths.append(f"M{_f(x)} {_f(-ASC)}V0")
    # o
    x += GAP_LO + R
    paths.append(f"M{_f(x - R)} {_f(-R)}a{_f(R)} {_f(R)} 0 1 0 {_f(2 * R)} 0a{_f(R)} {_f(R)} 0 1 0 {_f(-2 * R)} 0Z")
    cx_o = x
    # a  (single-storey: bowl + stem)
    x = cx_o + R + GAP_OA + R
    paths.append(f"M{_f(x - R)} {_f(-R)}a{_f(R)} {_f(R)} 0 1 0 {_f(2 * R)} 0a{_f(R)} {_f(R)} 0 1 0 {_f(-2 * R)} 0Z")
    paths.append(f"M{_f(x + R)} {_f(-XH)}V0")
    cx_a = x
    # m  (stem + two shoulders)
    r = R * 0.9
    x0 = cx_a + R + GAP_AM
    paths.append(f"M{_f(x0)} {_f(-XH)}V0")
    paths.append(f"M{_f(x0)} {_f(-XH + r)}a{_f(r)} {_f(r)} 0 0 1 {_f(2 * r)} 0V0")
    paths.append(f"M{_f(x0 + 2 * r)} {_f(-XH + r)}a{_f(r)} {_f(r)} 0 0 1 {_f(2 * r)} 0V0")
    return paths, x0 + 4 * r


def wordmark_group(color, transform=""):
    paths, _ = wordmark_paths()
    t = f' transform="{transform}"' if transform else ""
    body = "".join(f'<path d="{d}"/>' for d in paths)
    return (f'<g id="wordmark"{t} fill="none" stroke="{color}" stroke-width="{SW}" '
            f'stroke-linecap="round" stroke-linejoin="round">{body}</g>')


# Documents -------------------------------------------------------------------
TITLE = "Loam: generative AI"
DESC = "A pebble of nested, morphing organic rings in warm neutral tones, beside the lowercase wordmark loam."


def doc(w, h, bg, body, title=TITLE, desc=DESC):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-labelledby="t d"><title id="t">{title}</title><desc id="d">{desc}</desc>'
            f'<rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>\n')


def lockup(bg, rings, ink):
    W, H = 1280, 480
    paths, adv = wordmark_paths()
    # visual extents of the wordmark (centre-line + half stroke)
    word_w = adv + SW
    mark_size = 320
    bx0, by0, bx1, by1 = mark_paths(rings)[1]
    scale = mark_size / (bx1 - bx0)
    mark_h = (by1 - by0) * scale
    space = 70
    total = mark_size + space + word_w
    left = (W - total) / 2
    mark_x = left - bx0 * scale
    mark_y = H / 2 - mark_h / 2 - by0 * scale
    # baseline sits so the x-height band is centred on the mark's centre of mass
    base = H / 2 + (XH + SW) / 2 - SW / 2 + 6
    word_x = left + mark_size + space + SW / 2
    body = (mark_group(rings, f"translate({_f(mark_x)} {_f(mark_y)}) scale({scale:.4f})")
            + wordmark_group(ink, f"translate({_f(word_x)} {_f(base)})"))
    return doc(W, H, bg, body)


def mark_only(bg, rings):
    S = 512
    return doc(S, S, bg, mark_group(rings), title="Loam mark",
               desc="A pebble of nested, morphing organic rings in warm neutral tones.")


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    (out / "loam-logo.svg").write_text(lockup(BONE, LIGHT_RINGS, INK))
    (out / "loam-logo-dark.svg").write_text(lockup(INK_DEEP, DARK_RINGS, "#EDE6DA"))
    (out / "loam-mark.svg").write_text(mark_only(BONE, LIGHT_RINGS))
