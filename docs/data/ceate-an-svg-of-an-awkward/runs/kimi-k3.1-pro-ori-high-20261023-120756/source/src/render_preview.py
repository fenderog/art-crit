from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parent.parent
svg = (root / "src/portrait.svg").read_text()
html = f"<!doctype html><style>*{{margin:0}}svg{{display:block;width:1600px;height:1200px}}</style>{svg}"
with tempfile.TemporaryDirectory(dir=root) as tmp:
    page = Path(tmp) / "preview.html"
    page.write_text(html)
    subprocess.run([
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
        f"--screenshot={root / 'preview.png'}", "--window-size=1600,1200", page.as_uri(),
    ], check=True, capture_output=True)
subprocess.run([
    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(root / "preview.png"),
    "-vf", "scale=1200:-1", "-q:v", "3", str(root / "preview.jpg"),
], check=True)
(root / "preview.png").unlink()
