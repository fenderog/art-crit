"""Generate 'Loam' generative-AI logo: SVG + PNG (stdlib-only raster) + mp4 via ffmpeg."""
import math, os, struct, subprocess, zlib

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")
os.makedirs(OUT, exist_ok=True)

# Neutral palette
BONE = (232, 224, 213)
SAND = (201, 191, 174)
STONE = (138, 129, 120)
CLAY = (168, 150, 128)
MOSS = (122, 124, 108)
INK = (62, 58, 52)

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <title>Loam — generative intelligence</title>
  <rect width="800" height="800" rx="180" fill="#E8E0D5"/>
  <g transform="translate(400,340)">
    <!-- back organic blob: sand -->
    <path d="M -10,-165 C 90,-160 175,-95 168,5 C 162,105 90,175 0,172 C -95,169 -172,100 -168,0 C -164,-100 -105,-170 -10,-165 Z" fill="#C9BFAE"/>
    <!-- left lobe: clay -->
    <path d="M -140,-40 C -110,-110 -30,-150 25,-120 C 80,-90 75,-10 40,55 C 10,110 -60,150 -110,120 C -160,90 -165,20 -140,-40 Z" fill="#A89680" opacity="0.92"/>
    <!-- right lobe: stone -->
    <path d="M 140,-40 C 165,20 160,90 110,120 C 60,150 -10,110 -40,55 C -75,-10 -80,-90 -25,-120 C 30,-150 110,-110 140,-40 Z" fill="#8A8178" opacity="0.92"/>
    <!-- core seed: ink with moss halo -->
    <ellipse cx="0" cy="10" rx="72" ry="78" fill="#7A7C6C" opacity="0.55"/>
    <path d="M 0,-62 C 34,-60 58,-32 56,8 C 54,48 30,74 0,73 C -30,72 -56,46 -55,6 C -54,-34 -32,-64 0,-62 Z" fill="#3E3A34"/>
    <!-- growth nodes (generative spark) -->
    <circle cx="0" cy="-105" r="10" fill="#3E3A34"/>
    <circle cx="-72" cy="95" r="8" fill="#3E3A34"/>
    <circle cx="72" cy="95" r="8" fill="#3E3A34"/>
    <g stroke="#3E3A34" stroke-width="3" opacity="0.5" fill="none">
      <path d="M 0,-95 L 0,-72"/>
      <path d="M -64,88 L -35,60"/>
      <path d="M 64,88 L 35,60"/>
    </g>
    <!-- highlight -->
    <ellipse cx="-38" cy="-58" rx="26" ry="16" fill="#FFFFFF" opacity="0.28" transform="rotate(-30 -38 -58)"/>
  </g>
  <text x="400" y="600" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="84" letter-spacing="26" fill="#3E3A34">LOAM</text>
  <text x="400" y="648" text-anchor="middle" font-family="Georgia, serif" font-size="26" letter-spacing="8" fill="#8A8178">GENERATIVE INTELLIGENCE</text>
</svg>
"""
svg_path = os.path.join(OUT, "loam-logo.svg")
with open(svg_path, "w") as f:
    f.write(SVG)
print("wrote", svg_path, os.path.getsize(svg_path), "bytes")

# ---- PNG render (pure stdlib): soft organic blobs on bone background ----
W = H = 1000
cx, cy = W / 2, H / 2 - 60


def blob(cx_, cy_, rx, ry, wob, seed):
    """Return function(x,y)->coverage 0..1 for a wobbly ellipse with soft edge."""
    def fn(x, y):
        dx, dy = (x - cx_) / rx, (y - cy_) / ry
        r = math.hypot(dx, dy)
        ang = math.atan2(dy, dx)
        edge = 1.0 + wob * math.sin(3 * ang + seed) + 0.5 * wob * math.sin(2 * ang - seed * 1.7)
        d = (r - edge) * min(rx, ry)
        # soft edge over ~3px
        return max(0.0, min(1.0, 1.0 - d / 3.0))
    return fn


layers = [
    (blob(cx, cy, 200, 215, 0.10, 0.7), SAND),
    (blob(cx - 105, cy + 25, 120, 145, 0.16, 2.1), CLAY),
    (blob(cx + 105, cy + 25, 120, 145, 0.16, 4.2), STONE),
    (blob(cx, cy + 15, 92, 98, 0.06, 1.0), MOSS),
    (blob(cx, cy + 10, 62, 68, 0.05, 0.2), INK),
]

px = bytearray(W * H * 3)
for j in range(H):
    y = j + 0.5
    for i in range(W):
        x = i + 0.5
        r, g, b = BONE
        for fn, (cr, cg, cb) in layers:
            a = fn(x, y)
            if a > 0:
                r += (cr - r) * a
                g += (cg - g) * a
                b += (cb - b) * a
        k = (j * W + i) * 3
        px[k], px[k + 1], px[k + 2] = int(r), int(g), int(b)

# Note: PNG is the pictorial mark; the full wordmark lives in the SVG (system serif).


def write_png(path, w, h, buf):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + bytes(buf[j * w * 3:(j + 1) * w * 3]) for j in range(h))
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


# overlay simple wordmark using ffmpeg drawtext? No fonts guaranteed — skip; PNG is the mark.
png_path = os.path.join(OUT, "loam-mark.png")
write_png(png_path, W, H, px)
print("wrote", png_path, os.path.getsize(png_path), "bytes")

# ---- video: gentle breathing zoom on the PNG ----
mp4_path = os.path.join(OUT, "loam-logo.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", png_path,
                "-vf", "scale=1000:1000,zoompan=z='1+0.05*sin(2*PI*on/150)':d=150:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x720,fps=30",
                "-t", "5", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "20", mp4_path], check=True)
print("wrote", mp4_path, os.path.getsize(mp4_path), "bytes")
