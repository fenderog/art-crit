import math
import os
import shutil
import subprocess
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath("."))
from build_assets import create_sculpted_petal, rotate_and_translate, catmull_rom_to_bezier, get_gradient_defs

def ease_out_quart(x):
    return 1.0 - (1.0 - x) ** 4

def ease_in_out_sine(x):
    return -(math.cos(math.pi * x) - 1.0) / 2.0

def generate_animation_frames():
    temp_dir = "temp_frames"
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 180  # 6.0 seconds at 30 fps
    fps = 30
    width, height = 1080, 1080
    
    print(f"Generating {total_frames} animation frames...")
    
    for f in range(total_frames):
        t = f / float(total_frames)  # 0.0 to 1.0
        
        # Phase 1: Reveal (frames 0 to 45, 0.0s to 1.5s)
        # Phase 2: Morphogenesis breathing (frames 45 to 135, 1.5s to 4.5s)
        # Phase 3: Brand hold (frames 135 to 165, 4.5s to 5.5s)
        # Phase 4: Gentle loop dissolve (frames 165 to 180, 5.5s to 6.0s)
        
        # Calculate petal scale, rotation, and morph
        if f < 45:
            p1 = f / 45.0
            e1 = ease_out_quart(p1)
            scale = 210.0 * (0.05 + 0.95 * e1)
            global_rot = -45.0 * (1.0 - e1)
            opacity_petals = 0.86 * min(1.0, e1 * 1.5)
            ripple_scale = 50 + 320 * e1
            ripple_opacity = max(0.0, (1.0 - e1) * 0.45)
            
            text_opacity = 0.0
            sub_opacity = 0.0
            text_track = 8.0
        elif f < 135:
            p2 = (f - 45) / 90.0
            # Respiration wave
            wave = math.sin(p2 * 2.0 * math.pi)
            scale = 210.0 * (1.0 + 0.045 * wave)
            global_rot = 3.0 * math.sin(p2 * 2.0 * math.pi - math.pi / 3.0)
            opacity_petals = 0.86
            ripple_opacity = 0.0
            ripple_scale = 0.0
            
            # Text fades in between frame 45 and 85
            p_text = min(1.0, (f - 45) / 40.0)
            text_opacity = ease_in_out_sine(p_text)
            text_track = 8.0 + 8.0 * text_opacity
            
            p_sub = min(1.0, max(0.0, (f - 60) / 40.0))
            sub_opacity = ease_in_out_sine(p_sub)
        elif f < 165:
            # Hold lockup in serene stability
            p3 = (f - 135) / 30.0
            damp = 1.0 - p3
            wave = math.sin(p3 * math.pi) * damp
            scale = 210.0 * (1.0 + 0.015 * wave)
            global_rot = 0.5 * wave
            opacity_petals = 0.86
            ripple_opacity = 0.0
            ripple_scale = 0.0
            
            text_opacity = 1.0
            sub_opacity = 1.0
            text_track = 16.0
        else:
            # Gentle dissolve back to neutral void for perfect loop
            p4 = (f - 165) / 15.0
            e4 = ease_in_out_sine(p4)
            scale = 210.0 * (1.0 - 0.08 * e4)
            global_rot = 2.0 * e4
            opacity_petals = 0.86 * (1.0 - e4)
            text_opacity = 1.0 - e4
            sub_opacity = 1.0 - e4
            text_track = 16.0
            ripple_opacity = 0.0
            ripple_scale = 0.0

        # Build dynamic petals
        petal_paths = []
        grads_ref = ["url(#morphicLightG1)", "url(#morphicLightG2)", "url(#morphicLightG3)"]
        
        for i in range(3):
            # Dynamic individual petal phase for organic life
            petal_wave = 0.0
            if 45 <= f < 135:
                phase_i = ((f - 45) / 90.0) * 2.0 * math.pi + i * (2.0 * math.pi / 3.0)
                petal_wave = 0.03 * math.sin(phase_i)
            
            cur_scale = scale * (1.0 + petal_wave)
            petal_base = create_sculpted_petal(scale=cur_scale)
            
            ang = i * 120 + global_rot
            shift_r = cur_scale * 0.237
            scx = shift_r * math.cos(math.radians(ang - 40))
            scy = shift_r * math.sin(math.radians(ang - 40))
            pts = rotate_and_translate(petal_base, scx, scy, ang)
            d = catmull_rom_to_bezier(pts)
            petal_paths.append(f'<path d="{d}" fill="{grads_ref[i]}" opacity="{opacity_petals:.3f}" style="mix-blend-mode: multiply;"/>')
            
        petals_str = "\n    ".join(petal_paths)
        
        # Ripple circle
        ripple_str = ""
        if ripple_opacity > 0.005:
            ripple_str = f'<circle cx="540" cy="450" r="{ripple_scale:.1f}" fill="none" stroke="#DCD3C5" stroke-width="1.5" stroke-opacity="{ripple_opacity:.3f}" stroke-dasharray="3 6"/>'
            ripple_str += f'<circle cx="540" cy="450" r="{ripple_scale*0.6:.1f}" fill="none" stroke="#DCD3C5" stroke-width="1.2" stroke-opacity="{ripple_opacity*0.7:.3f}"/>'

        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>{get_gradient_defs()}
  </defs>
  <rect width="{width}" height="{height}" fill="#FAF8F5"/>
  {ripple_str}
  <g transform="translate(540, 450)">
    {petals_str}
  </g>
  <text x="540" y="820" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" font-size="56" font-weight="500" fill="#1F1D1A" text-anchor="middle" letter-spacing="{text_track:.2f}" opacity="{text_opacity:.3f}">MORPHIC</text>
  <text x="540" y="875" font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif" font-size="16" font-weight="400" fill="#756B60" text-anchor="middle" letter-spacing="8" opacity="{sub_opacity:.3f}">GENERATIVE INTELLIGENCE</text>
</svg>"""

        svg_path = os.path.join(temp_dir, f"frame_{f:04d}.svg")
        png_path = os.path.join(temp_dir, f"frame_{f:04d}.png")
        
        with open(svg_path, "w") as sf:
            sf.write(svg_content)
            
        subprocess.run(["sips", "-s", "format", "png", svg_path, "--out", png_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        os.remove(svg_path)
        
        if (f + 1) % 30 == 0:
            print(f"Rendered {f + 1}/{total_frames} frames...")

    print("Encoding video with ffmpeg...")
    output_mp4 = "output/logo_animation.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", os.path.join(temp_dir, "frame_%04d.png"),
        "-c:v", "libx264",
        "-profile:v", "high",
        "-pix_fmt", "yuv420p",
        "-crf", "20",
        "-movflags", "+faststart",
        output_mp4
    ]
    subprocess.run(cmd, check=True)
    
    # Cleanup temporary frames
    shutil.rmtree(temp_dir)
    print("Animation completed successfully and temp frames cleaned up!")

if __name__ == "__main__":
    generate_animation_frames()
