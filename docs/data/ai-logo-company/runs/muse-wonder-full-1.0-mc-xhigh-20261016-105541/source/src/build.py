#!/usr/bin/env python3
"""Build all Morpha deliverables into ./output/.

SVG files are generated directly. PNG/GIF renders rasterize those SVGs
with macOS `sips` (system SVG renderer) and assemble animation with
ffmpeg. Intermediate frames live in /tmp and are deleted afterwards.
"""
import os, shutil, subprocess, sys

sys.path.insert(0, "src")
from logo import *
import brandsheet

OUT = "output"
TMP = "/tmp/morpha_build"
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

def write(name, text):
    path = os.path.join(OUT, name)
    open(path, "w").write(text)
    print(f"{path}  ({os.path.getsize(path)} bytes)")

def rasterize(svg_text, out_name, tmp_name):
    """SVG (with explicit width/height) -> PNG in output/, via sips."""
    src = os.path.join(TMP, tmp_name)
    open(src, "w").write(svg_text)
    dst = os.path.join(OUT, out_name)
    subprocess.run(["sips", "-s", "format", "png", src, "--out", dst],
                   check=True, capture_output=True)
    print(f"{dst}  ({os.path.getsize(dst)} bytes)")

# --------------------------------------------------------------- SVG set
write("morpha-mark.svg", mark_svg())
write("morpha-logo-horizontal.svg", horizontal_svg())
write("morpha-logo-stacked.svg", stacked_svg())
write("morpha-logo-mono.svg", horizontal_svg(INK, INK, INK))
write("morpha-logo-reversed.svg", horizontal_svg(BONE, CLAY, STONE, wm_col=BONE))

# ----------------------------------------------------------------- PNGs
rasterize(brandsheet.sheet_svg(), "morpha-brand-sheet.png", "sheet.svg")
rasterize(brandsheet.appicon_svg(), "morpha-app-icon.png", "appicon.svg")

# ------------------------------------------------------------ animated GIF
FRAMES, FPS = 48, 16
fdir = os.path.join(TMP, "frames")
os.makedirs(fdir, exist_ok=True)
for i in range(FRAMES):
    src = os.path.join(fdir, f"f{i:03d}.svg")
    open(src, "w").write(brandsheet.frame_svg(i / FRAMES))
    subprocess.run(["sips", "-s", "format", "png", src, "--out", src[:-4] + ".png"],
                   check=True, capture_output=True)
    os.remove(src)
gif = os.path.join(OUT, "morpha-animated.gif")
palette = os.path.join(TMP, "palette.png")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                "-i", os.path.join(fdir, "f%03d.png"),
                "-vf", "palettegen=stats_mode=diff:max_colors=96", palette], check=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                "-i", os.path.join(fdir, "f%03d.png"), "-i", palette,
                "-lavfi", "paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle",
                "-loop", "0", gif], check=True)
print(f"{gif}  ({os.path.getsize(gif)} bytes)")

shutil.rmtree(TMP)
print("done — intermediates removed")
