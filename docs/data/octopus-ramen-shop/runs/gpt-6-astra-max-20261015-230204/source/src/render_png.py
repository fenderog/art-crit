#!/usr/bin/env python3
"""Rasterize the finished SVG using the macOS renderer already on this machine.
Quick Look's SVG thumbnailer uses square bounds, so render on a temporary square
canvas and losslessly crop the unused right edge. All intermediates stay inside
this project and are automatically removed.
"""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
svg = (ROOT / 'output/eight-arms-ramen.svg').read_text()
square = svg.replace('width="1400" height="1600" viewBox="0 0 1400 1600"',
                     'width="1600" height="1600" viewBox="0 0 1600 1600"', 1)
with tempfile.TemporaryDirectory(prefix='.render-', dir=ROOT) as tmp:
    tmp = Path(tmp)
    source = tmp / 'square.svg'
    source.write_text(square)
    subprocess.run(['qlmanage', '-t', '-s', '1600', '-o', str(tmp), str(source)],
                   check=True, stdout=subprocess.DEVNULL)
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                    '-i', str(tmp/'square.svg.png'), '-vf', 'crop=1400:1600:0:0',
                    '-frames:v', '1', '-update', '1', '-compression_level', '9',
                    str(ROOT/'output/eight-arms-ramen.png')], check=True)
print('Created output/eight-arms-ramen.png (1400 × 1600)')
