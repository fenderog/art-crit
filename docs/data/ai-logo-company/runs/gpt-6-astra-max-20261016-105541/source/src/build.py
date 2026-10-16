#!/usr/bin/env python3
"""Build the Loam logo assets. Python standard library only.

Run from any directory: python3 /path/to/src/build.py
On macOS, sips renders the PNG preview. Elsewhere, the preview stays SVG.
All visible lettering is outlined; the exported SVGs need no installed fonts.
"""
from pathlib import Path
from html import escape
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

# Warm neutrals. Flat fills are intentional: this identity must also work in print.
PAPER = "#F3F0E8"
INK = "#373A32"
BARK = "#494C41"
TAUPE = "#B4AB99"
STONE = "#848575"
SECONDARY = "#6B6E60"

# One organic frond, repeated at 120-degree intervals around its growing point.
# The repeated concave/convex gesture suggests unfurling leaves and generation.
FROND = (
    "M128 128 "
    "C107 95 82 87 63 105 "
    "C43 124 44 155 66 181 "
    "C33 172 15 146 18 115 "
    "C21 80 52 57 89 57 "
    "C125 56 153 87 145 116 "
    "C142 125 136 128 128 128Z"
)

# Original lowercase wordmark outlines. The round o/a echo the symbol's bowls;
# the hooked l and single-storey a give the lettering a quieter, organic voice.
WORDMARK = {
    "l": "M0 0 H25 V139 C25 152 30 157 40 157 H49 V179 H35 C12 179 0 166 0 142Z",
    "o": (
        "M136 40 C177 40 202 69 202 109 C202 150 177 180 136 180 "
        "C95 180 70 151 70 110 C70 70 95 40 136 40Z "
        "M136 63 C110 63 95 79 95 110 C95 140 111 157 136 157 "
        "C162 157 177 140 177 110 C177 80 162 63 136 63Z"
    ),
    "a": (
        "M285 40 C304 40 322 49 332 64 V44 H356 V176 H332 V155 "
        "C319 172 302 180 282 180 C245 180 219 150 219 110 "
        "C219 69 245 40 285 40Z "
        "M286 63 C261 63 245 82 245 110 C245 139 261 157 286 157 "
        "C312 157 333 137 333 110 C333 83 313 63 286 63Z"
    ),
    "m": (
        "M382 176 V44 H406 V63 C415 48 429 40 447 40 "
        "C468 40 485 49 492 67 C504 49 519 40 540 40 "
        "C571 40 590 61 590 96 V176 H565 V101 "
        "C565 75 555 64 537 64 C517 64 503 79 503 104 V176 H478 V101 "
        "C478 75 468 64 450 64 C428 64 407 80 407 105 V176Z"
    ),
}
DESCRIPTOR = json.loads((ROOT / "src" / "descriptor.json").read_text())


def symbol() -> str:
    """Keep separate, editable paths; there are no masks or background cutouts."""
    return "\n".join(
        f'<path fill="{color}" transform="rotate({angle} 128 128)" d="{FROND}"/>'
        for angle, color in ((0, BARK), (120, TAUPE), (240, STONE))
    )


def lockup() -> str:
    letters = "\n".join(
        f'<path id="letter-{letter}" d="{path}"/>'
        for letter, path in WORDMARK.items()
    )
    descriptor = "\n".join(f'<path d="{p}"/>' for p in DESCRIPTOR["paths"])
    return (
        '<g id="symbol" transform="scale(1.2)">\n' + symbol() + '\n</g>\n'
        f'<g id="wordmark" fill="{INK}" fill-rule="evenodd" '
        'transform="translate(333 44) scale(.9)">\n' + letters + '\n</g>\n'
        f'<g id="descriptor" fill="{SECONDARY}" transform="translate(333 258)">\n'
        + descriptor + '\n</g>'
    )


def svg(width: int, height: int, viewbox: str, title: str, description: str, body: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="{viewbox}" '
        'role="img" aria-labelledby="logo-title logo-description">\n'
        f'<title id="logo-title">{escape(title)}</title>\n'
        f'<desc id="logo-description">{escape(description)}</desc>\n'
        + body + '\n</svg>\n'
    )


TITLE = "loam — generative intelligence"
DESCRIPTION = (
    "An organic logo for a generative AI company. Three curling fronds in bark, "
    "taupe and stone meet in a growing whorl, beside an original charcoal "
    "lowercase wordmark. The descriptor reads GENERATIVE INTELLIGENCE."
)

# Compact, transparent production lockup, with clear space on all four sides.
(OUT / "loam-logo.svg").write_text(svg(
    960, 350, "0 0 960 350", TITLE, DESCRIPTION,
    '<g transform="translate(38 17)">\n' + lockup() + '\n</g>'
))

# Standalone symbol. This offset centers its optical bounding box in the square.
(OUT / "loam-symbol.svg").write_text(svg(
    512, 512, "0 0 256 256", "loam — standalone symbol",
    "Three curling organic fronds in warm neutral tones on a transparent background.",
    '<g id="symbol" transform="translate(9.1155 -3.4594)">\n' + symbol() + '\n</g>'
))

# Presentation image: deliberately quiet, with generous warm-ivory clear space.
preview = svg(
    2400, 1500, "0 0 1440 900", TITLE, DESCRIPTION,
    f'<rect width="1440" height="900" fill="{PAPER}"/>\n'
    '<g transform="translate(278 292)">\n' + lockup() + '\n</g>'
)
if shutil.which("sips"):
    render_dir = ROOT / ".render"
    render_dir.mkdir(exist_ok=True)
    temporary = render_dir / "loam-preview.svg"
    try:
        temporary.write_text(preview)
        subprocess.run(
            ["sips", "-s", "format", "png", str(temporary),
             "--out", str(OUT / "loam-preview.png")],
            check=True, stdout=subprocess.DEVNULL,
        )
    finally:
        temporary.unlink(missing_ok=True)
        if not any(render_dir.iterdir()):
            render_dir.rmdir()
else:
    (OUT / "loam-preview.svg").write_text(preview)

for path in sorted(OUT.iterdir()):
    if path.is_file():
        assert path.stat().st_size < 2_000_000, f"File too large: {path}"
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size:,} bytes")
