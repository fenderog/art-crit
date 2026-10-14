#!/usr/bin/env python3
"""Wrap the wide artwork SVG in a square canvas so macOS Quick Look
(which crops non-square SVGs) renders the whole scene for inspection.
Preview only -- not part of the deliverable."""
import re
import sys

SRC = "src/family-portrait.svg"
OUT = "preview/square.svg"


def main() -> None:
    with open(SRC, "r", encoding="utf-8") as fh:
        svg = fh.read()
    # Inner content between the opening <svg ...> and closing </svg>.
    start = svg.index(">", svg.index("<svg")) + 1
    end = svg.rindex("</svg>")
    inner = svg[start:end]
    # 1280x960 scene centered in a 1280x1280 square (160px top/bottom).
    wrapped = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'viewBox="0 0 1280 1280" width="1280" height="1280">\n'
        '<rect width="1280" height="1280" fill="#0b1418"/>\n'
        '<g transform="translate(0,160)">\n'
        + inner +
        "\n</g>\n</svg>\n"
    )
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(wrapped)
    print("wrote", OUT)


if __name__ == "__main__":
    sys.exit(main())
