import math
import subprocess
import os
import shutil

def test_flowing_loop():
    os.makedirs("src/frames", exist_ok=True)
    fps = 30
    duration = 3.0 # 3 seconds
    total_frames = int(fps * duration)
    
    scale = 92.0
    cx, cy = 250, 250
    num_segments = 360
    
    print(f"Generating {total_frames} frames...")
    
    for frame in range(total_frames):
        # Phase shift: a full period of symmetry is 2*pi / 3
        # In total_frames, shift t by exactly 2*pi / 3
        phase = (2.0 * math.pi / 3.0) * (frame / total_frames)
        
        # Subtle gentle breathing tilt:
        # rot_x breathes between -4 deg and +4 deg
        rot_x = math.radians(6.0 * math.sin(2.0 * math.pi * frame / total_frames))
        rot_z = math.radians(4.0 * math.cos(2.0 * math.pi * frame / total_frames))
        
        pts = []
        for i in range(num_segments):
            t = (2.0 * math.pi * i) / num_segments + phase
            
            x = math.sin(t) + 2.0 * math.sin(2.0 * t)
            y = math.cos(t) - 2.0 * math.cos(2.0 * t)
            z = -math.sin(3.0 * t)
            
            # Rot z
            x1 = x * math.cos(rot_z) - y * math.sin(rot_z)
            y1 = x * math.sin(rot_z) + y * math.cos(rot_z)
            z1 = z
            
            # Rot x
            x2 = x1
            y2 = y1 * math.cos(rot_x) - z1 * math.sin(rot_x)
            z2 = y1 * math.sin(rot_x) + z1 * math.cos(rot_x)
            
            px = cx + x2 * scale * 0.65
            py = cy + y2 * scale * 0.65
            pts.append({'px': px, 'py': py, 'pz': z2, 't': t, 'idx': i})

        ribbon_w = 26.0
        for i in range(num_segments):
            c = pts[i]
            n = pts[(i + 1) % num_segments]
            dx, dy = n['px'] - c['px'], n['py'] - c['py']
            L = math.hypot(dx, dy) or 1e-5
            nx, ny = -dy / L, dx / L
            w = ribbon_w * (1.0 + 0.12 * math.cos(3 * c['t']))
            c['pl'] = (c['px'] + nx * w, c['py'] + ny * w)
            c['pr'] = (c['px'] - nx * w, c['py'] - ny * w)
            c['width'] = w

        for i in range(num_segments):
            c = pts[i]
            ao_factor = 1.0
            for j in range(num_segments):
                idx_diff = abs(i - j)
                idx_diff = min(idx_diff, num_segments - idx_diff)
                if idx_diff < 40:
                    continue
                other = pts[j]
                z_diff = other['pz'] - c['pz']
                if z_diff > 0.5:
                    dist_2d = math.hypot(other['px'] - c['px'], other['py'] - c['py'])
                    thresh = (c['width'] + other['width']) * 0.75
                    if dist_2d < thresh:
                        d_norm = dist_2d / thresh
                        shadow = (1.0 - d_norm * d_norm) * 0.45 * min(1.0, z_diff / 1.5)
                        ao_factor = min(ao_factor, 1.0 - shadow)
            c['ao'] = ao_factor

        quads = []
        for i in range(num_segments):
            c = pts[i]
            n = pts[(i + 1) % num_segments]
            avg_z = (c['pz'] + n['pz']) / 2.0
            avg_ao = (c['ao'] + n['ao']) / 2.0
            zn = max(0.0, min(1.0, (avg_z + 2.0) / 4.0))
            
            # Dark mode palette: warm champagne / oat / graphite
            base_r = 52 + zn * 175
            base_g = 48 + zn * 165
            base_b = 44 + zn * 150
            r = int(base_r * avg_ao)
            g = int(base_g * avg_ao)
            b = int(base_b * avg_ao)
            col = f"#{r:02x}{g:02x}{b:02x}"
            quads.append({'z': avg_z, 'pts': [c['pl'], n['pl'], n['pr'], c['pr']], 'col': col})
            
        quads.sort(key=lambda q: q['z'])
        paths = [f'<path d="M {q["pts"][0][0]:.2f} {q["pts"][0][1]:.2f} L {q["pts"][1][0]:.2f} {q["pts"][1][1]:.2f} L {q["pts"][2][0]:.2f} {q["pts"][2][1]:.2f} L {q["pts"][3][0]:.2f} {q["pts"][3][1]:.2f} Z" fill="{q["col"]}" stroke="{q["col"]}" stroke-width="0.8" />' for q in quads]
        
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500">
  <rect width="500" height="500" fill="#121110" />
  <circle cx="250" cy="250" r="150" fill="none" stroke="rgba(245,239,230,0.06)" stroke-width="1" stroke-dasharray="2 3" />
  <g>{"".join(paths)}</g>
</svg>"""
        with open(f"src/frames/f_{frame:03d}.svg", "w") as f:
            f.write(svg)
            
    print("Frame svgs written, rendering frames to png...")
    # Convert frames using qlmanage in batch
    # Or test how fast qlmanage handles 90 frames
    subprocess.run(["qlmanage", "-t", "-s", "500", "-o", "src/frames/"] + [f"src/frames/f_{i:03d}.svg" for i in range(total_frames)], check=True)
    
    # Rename .svg.png to .png
    for i in range(total_frames):
        src_png = f"src/frames/f_{i:03d}.svg.png"
        dst_png = f"src/frames/frame_{i:03d}.png"
        if os.path.exists(src_png):
            os.rename(src_png, dst_png)
            
    # Encode with ffmpeg
    subprocess.run([
        "ffmpeg", "-y", "-r", str(fps), "-i", "src/frames/frame_%03d.png",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
        "src/test_loop.mp4"
    ], check=True)
    
    # Cleanup frames
    shutil.rmtree("src/frames")
    print("Video loop rendered to src/test_loop.mp4")

if __name__ == "__main__":
    test_flowing_loop()
