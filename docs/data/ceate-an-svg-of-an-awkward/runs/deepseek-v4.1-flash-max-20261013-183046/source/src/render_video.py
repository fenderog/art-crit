#!/usr/bin/env python3
"""Turn the static portrait into a short, seamlessly looping video.

The scene is parameterised through element ids in the deliverable SVG
(#drone, #kidWave, #phoneGlow).  Each frame is written as a square
wrapper SVG (so macOS Quick Look does not crop it), batch-rendered to
PNG, then encoded with ffmpeg.

Preview/intermediate only -- the importable source lives here.
"""
import math
import os
import re
import shutil
import subprocess
import sys

SRC = "src/family-portrait.svg"
FRAME_DIR = "preview/frames"
OUT = "output/family-portrait.mp4"

FPS = 15
SECONDS = 6.0


def set_attr(svg: str, elem_id: str, attr: str, value: str) -> str:
    """Set/replace an attribute on the element carrying ``elem_id``."""
    m = re.search(r'<[^>]*\bid="%s"[^>]*>' % re.escape(elem_id), svg)
    if not m:
        raise SystemExit("element not found: " + elem_id)
    tag = m.group(0)
    if re.search(r'\b%s="' % re.escape(attr), tag):
        new_tag = re.sub(r'\b%s="[^"]*"' % re.escape(attr),
                         '%s="%s"' % (attr, value), tag, count=1)
    elif tag.endswith("/>"):
        new_tag = tag[:-2] + ' %s="%s"/>' % (attr, value)
    else:
        new_tag = tag[:-1] + ' %s="%s">' % (attr, value)
    return svg[:m.start()] + new_tag + svg[m.end():]


def inner_content(svg: str) -> str:
    start = svg.index(">", svg.index("<svg")) + 1
    end = svg.rindex("</svg>")
    return svg[start:end]


def flash_alpha(phase: float) -> float:
    """A camera flash straddling the loop point, so the loop reads as
    a repeated press of the shutter."""
    d = min(phase, 1.0 - phase)
    if d < 0.07:
        return 0.85 * (1.0 - d / 0.07)
    return 0.0


def build_frame(base_inner: str, frame_idx: int, total: int) -> str:
    phase = frame_idx / total
    # gentle push-in and back out
    scale = 1.0 + 0.03 * (0.5 - 0.5 * math.cos(2 * math.pi * phase))
    # drone hovers
    drone_y = 96 + 9 * math.sin(2 * math.pi * phase)
    # kid waves twice per loop
    wave = 13 * math.sin(2 * math.pi * phase * 2)
    # phone light flickers
    glow = 0.55 + 0.30 * math.sin(2 * math.pi * phase * 3)
    alpha = flash_alpha(phase)

    inner = base_inner
    inner = set_attr(inner, "drone", "transform", "translate(640,%.2f)" % drone_y)
    inner = set_attr(inner, "kidWave", "transform", "rotate(%.2f 58 -14)" % wave)
    inner = set_attr(inner, "phoneGlow", "opacity", "%.2f" % glow)
    inner += ('\n<rect id="flash" x="0" y="0" width="1280" height="960" '
              'fill="#ffffff" opacity="%.3f"/>\n' % alpha)

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'viewBox="0 0 1280 1280" width="1280" height="1280">\n'
        '<rect width="1280" height="1280" fill="#0b1418"/>\n'
        '<g transform="translate(640,640) scale(%.4f) translate(-640,-640)">\n'
        '<g transform="translate(0,160)">\n' % scale
        + inner +
        "\n</g>\n</g>\n</svg>\n"
    )


def main() -> None:
    test = "--test" in sys.argv
    total = 3 if test else int(round(FPS * SECONDS))

    with open(SRC, "r", encoding="utf-8") as fh:
        svg = fh.read()
    base_inner = inner_content(svg)

    if os.path.isdir(FRAME_DIR):
        shutil.rmtree(FRAME_DIR)
    os.makedirs(FRAME_DIR, exist_ok=True)

    paths = []
    for i in range(total):
        p = os.path.join(FRAME_DIR, "frame_%04d.svg" % i)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(build_frame(base_inner, i, total))
        paths.append(p)

    # Batch-render every frame with Quick Look (WebKit) in one process.
    subprocess.run(["qlmanage", "-t", "-s", "1280", "-o", FRAME_DIR, *paths],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("rendered %d frames" % total)


if __name__ == "__main__":
    main()
