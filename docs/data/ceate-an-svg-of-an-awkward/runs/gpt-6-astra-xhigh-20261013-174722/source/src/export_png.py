"""Raster companion for the SVG, using macOS Quick Look and ffmpeg.

Quick Look makes square SVG thumbnails. An expanded temporary viewBox gives
it the whole portrait, then ffmpeg removes the extra side margins losslessly.
Temporary assets stay inside the project and are removed automatically.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess

ROOT = Path(__file__).resolve().parents[1]
svg = ROOT / 'output' / 'robot_family.svg'
png = svg.with_suffix('.png')
with TemporaryDirectory(prefix='.raster-', dir=ROOT) as folder:
    folder = Path(folder)
    square = folder / 'square.svg'
    square.write_text(svg.read_text().replace(
        'width="1440" height="1640" viewBox="0 0 1440 1640"',
        'width="1640" height="1640" viewBox="-100 0 1640 1640"', 1))
    subprocess.run(['qlmanage', '-t', '-s', '1640', '-o', str(folder), str(square)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(square) + '.png',
                    '-vf', 'crop=1440:1640:100:0,format=rgb24',
                    '-compression_level', '9', '-frames:v', '1', '-update', '1', str(png)],
                   check=True)
print(png)
