"""Render the finished SVG with macOS Quick Look and crop with FFmpeg.

Run `python3 make_portrait.py` first, then `python3 render_png.py`.
The temporary square canvas avoids Quick Look's non-square SVG clipping.
All temporary files stay inside the project and are removed automatically.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parent
source = root / 'output' / 'awkward-family.svg'
destination = root / 'output' / 'awkward-family.png'
svg = source.read_text()
attributes = ET.fromstring(svg).attrib
width, height = int(attributes['width']), int(attributes['height'])
side = max(width, height)
square = svg.replace(
    f'width="{width}" height="{height}" viewBox="0 0 {width} {height}"',
    f'width="{side}" height="{side}" viewBox="0 0 {side} {side}"',
    1,
)
with TemporaryDirectory(prefix='.render-', dir=root) as temporary:
    directory = Path(temporary)
    intermediate = directory / 'square.svg'
    intermediate.write_text(square)
    subprocess.run(
        ['qlmanage', '-t', '-s', str(side), '-o', str(directory), str(intermediate)],
        check=True, capture_output=True,
    )
    subprocess.run(
        ['ffmpeg', '-y', '-loglevel', 'error', '-i', str(intermediate) + '.png',
         '-vf', f'crop={width}:{height}:0:0', '-frames:v', '1',
         '-compression_level', '9', '-update', '1', str(destination)],
        check=True,
    )
assert destination.stat().st_size < 2_000_000
print(f'Wrote {destination.relative_to(root)} ({destination.stat().st_size:,} bytes)')
