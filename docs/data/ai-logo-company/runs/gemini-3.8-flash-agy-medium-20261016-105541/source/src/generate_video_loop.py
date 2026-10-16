import math
import subprocess
import os
import shutil
from brand_engine import generate_trefoil_quads, quads_to_svg_paths

def generate_video_loop(output_path="output/logo-motion.mp4", fps=60, duration=6.0, size=720):
    total_frames = int(fps * duration) # 360 frames
    temp_dir = "src/temp_video_frames"
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"Generating {total_frames} animation frames ({fps} fps, {duration}s)...")
    
    # In 6 seconds, we complete 2 full cycles of the 3-fold symmetry period (2 * 2*pi/3 = 4*pi/3)
    # This guarantees a perfectly seamless loop from frame 359 back to frame 0!
    total_phase = 2.0 * (2.0 * math.pi / 3.0)
    
    cx, cy = size / 2.0, (size / 2.0) - 25.0
    base_scale = size * 0.108 # ~78 px
    base_ribbon_w = size * 0.048 # ~35 px
    
    for frame_idx in range(total_frames):
        progress = frame_idx / total_frames
        phase = total_phase * progress
        
        # Organic breathing:
        # Subtle organic tilt: rx in [-2.5, +2.5] deg, rz in [-3, +3] deg
        # Period of breathing is 1 full cycle across the 6 seconds
        breath_cycle = 2.0 * math.pi * progress
        rot_x = 2.8 * math.sin(breath_cycle)
        rot_z = 3.2 * math.cos(breath_cycle)
        scale_mod = base_scale * (1.0 + 0.025 * math.sin(2.0 * breath_cycle))
        
        # Generate quads
        quads = generate_trefoil_quads(
            cx=cx, cy=cy,
            scale=scale_mod,
            ribbon_w=base_ribbon_w,
            rot_x_deg=rot_x,
            rot_z_deg=rot_z,
            phase=phase,
            is_dark=True,
            num_segments=360
        )
        paths = quads_to_svg_paths(quads)
        
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">
  <defs>
    <radialGradient id="vBg" cx="50%" cy="42%" r="65%">
      <stop offset="0%" stop-color="#1B1917" />
      <stop offset="100%" stop-color="#11100F" />
    </radialGradient>
    <filter id="vShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#000" flood-opacity="0.5" />
    </filter>
  </defs>

  <rect width="{size}" height="{size}" fill="url(#vBg)" />

  <!-- Coordinate Field Rings -->
  <circle cx="{cx}" cy="{cy}" r="{size * 0.28}" fill="none" stroke="rgba(247, 242, 234, 0.07)" stroke-width="1.2" stroke-dasharray="3 5" />
  <circle cx="{cx}" cy="{cy}" r="{size * 0.34}" fill="none" stroke="rgba(247, 242, 234, 0.035)" stroke-width="1" />

  <!-- Flowing Trefoil Mark -->
  <g filter="url(#vShadow)">
    {"".join(paths)}
  </g>

  <!-- Typography -->
  <g text-anchor="middle">
    <text x="{cx}" y="{size - 85}" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', sans-serif" font-size="32" font-weight="500" letter-spacing="11" fill="#F7F2EA">KHORA</text>
    <text x="{cx}" y="{size - 52}" font-family="-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Text', sans-serif" font-size="11" font-weight="400" letter-spacing="4.5" fill="#9D9487">GENERATIVE INTELLIGENCE</text>
  </g>
</svg>"""

        frame_file = os.path.join(temp_dir, f"frame_{frame_idx:04d}.svg")
        with open(frame_file, "w") as f:
            f.write(svg)
            
    print("All frame SVGs generated. Converting to PNG via qlmanage in batches...")
    
    # Convert frames in batches of 60
    batch_size = 60
    for b in range(0, total_frames, batch_size):
        batch_files = [os.path.join(temp_dir, f"frame_{i:04d}.svg") for i in range(b, min(b + batch_size, total_frames))]
        subprocess.run(["qlmanage", "-t", "-s", str(size), "-o", temp_dir] + batch_files, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"Rendered batch {b // batch_size + 1} / {(total_frames + batch_size - 1) // batch_size}")

    # Rename .svg.png to .png
    for i in range(total_frames):
        src_p = os.path.join(temp_dir, f"frame_{i:04d}.svg.png")
        dst_p = os.path.join(temp_dir, f"frame_{i:04d}.png")
        if os.path.exists(src_p):
            os.rename(src_p, dst_p)

    print("Encoding video with ffmpeg...")
    input_pattern = os.path.join(temp_dir, "frame_%04d.png")
    subprocess.run([
        "ffmpeg", "-y",
        "-r", str(fps),
        "-i", input_pattern,
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level", "4.0",
        "-pix_fmt", "yuv420p",
        "-crf", "21",
        "-movflags", "+faststart",
        output_path
    ], check=True)

    print("Cleaning up intermediate frames...")
    shutil.rmtree(temp_dir)
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    generate_video_loop()
