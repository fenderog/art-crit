#!/usr/bin/env python3
"""Optional PNG export using macOS Quick Look and ffmpeg, with no dependencies.

Quick Look makes a square thumbnail of SVGs. Give it an explicitly square canvas
and then crop away the temporary side margins, preserving the entire poster.
All temporary files stay inside the project and are removed after export.
"""
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
subprocess.run(['python3', str(ROOT/'src/generate.py')], check=True)
svg_path = ROOT/'output/octo-ramen.svg'
svg = svg_path.read_text(encoding='utf-8')
ET.fromstring(svg)  # Validate the delivered SVG, not just the thumbnail.
with tempfile.TemporaryDirectory(prefix='.render-', dir=ROOT) as work:
    work = Path(work)
    square = work/'poster-square.svg'
    square.write_text(svg.replace(
        'width="1440" height="1560" viewBox="0 0 1440 1560"',
        'width="1560" height="1560" viewBox="-60 0 1560 1560"', 1), encoding='utf-8')
    subprocess.run(['qlmanage','-t','-s','1560','-o',str(work),str(square)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(work/'poster-square.svg.png'),
                    '-vf','crop=1440:1560:60:0','-frames:v','1',
                    '-compression_level','9',str(ROOT/'output/octo-ramen.png')], check=True)
for p in sorted((ROOT/'output').iterdir()):
    assert p.stat().st_size < 2_000_000, f'{p.name} exceeds 2 MB'
    print(f'{p.name}: {p.stat().st_size:,} bytes')
