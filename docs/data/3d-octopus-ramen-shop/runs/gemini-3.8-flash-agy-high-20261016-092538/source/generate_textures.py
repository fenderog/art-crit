import numpy as np
import bpy
import math

def create_noren_texture():
    w, h = 512, 256
    img_data = np.zeros((h, w, 4), dtype=np.float32)
    
    # Cream linen base
    base_color = np.array([0.95, 0.92, 0.86, 1.0], dtype=np.float32)
    img_data[:, :] = base_color
    
    # Subtle fabric grain
    rng = np.random.RandomState(42)
    noise = (rng.rand(h, w, 1) - 0.5) * 0.03
    img_data[:, :, :3] += noise
    
    # Deep indigo bottom band (lower 22%)
    band_h = int(h * 0.22)
    indigo = np.array([0.08, 0.12, 0.22, 1.0], dtype=np.float32)
    img_data[:band_h, :] = indigo
    
    # Red accent stripe right above indigo band
    stripe_h = int(h * 0.035)
    red_accent = np.array([0.88, 0.18, 0.14, 1.0], dtype=np.float32)
    img_data[band_h:band_h+stripe_h, :] = red_accent
    
    # 4 panels division vertical lines
    for p in range(1, 4):
        x = int(w * p / 4)
        img_data[:, x-1:x+2, :3] *= 0.65
        
    # Draw emblems in each panel:
    # Panel 1 (center x=64, y=140): Kanji "蛸" (Octopus)
    # Panel 2 (center x=192, y=140): Stylized Octopus Chef Logo
    # Panel 3 (center x=320, y=140): Steaming Ramen Bowl Logo
    # Panel 4 (center x=448, y=140): Kanji "拉麺" (Ramen)
    
    for y in range(h):
        for x in range(w):
            # Panel 1: Kanji 蛸
            dx1 = abs(x - 64)
            dy1 = y - 140
            if dx1 < 26 and abs(dy1) < 32:
                # Vertical spine & cross strokes
                if dx1 < 4 or abs(dy1) < 4 or abs(dy1 - 18) < 4 or abs(dy1 + 18) < 4:
                    img_data[y, x, :3] = indigo[:3]

            # Panel 2: Octopus Chef Logo
            dx2 = (x - 192) / 36.0
            dy2 = (y - 142) / 36.0
            r2 = math.sqrt(dx2*dx2 + dy2*dy2)
            if r2 < 1.0:
                # Red octopus head
                img_data[y, x, :3] = red_accent[:3]
                # White chef headband
                if abs(dy2 - 0.22) < 0.12:
                    img_data[y, x, :3] = [0.98, 0.98, 0.98]
                # Eyes
                if abs(dy2 + 0.05) < 0.18 and (abs(dx2 - 0.35) < 0.14 or abs(dx2 + 0.35) < 0.14):
                    img_data[y, x, :3] = [0.05, 0.05, 0.05]
            elif r2 < 1.35 and dy2 < -0.2:
                # Waving tentacle curls
                if math.sin(dx2 * 9.0) > 0.1:
                    img_data[y, x, :3] = red_accent[:3]
                    
            # Panel 3: Steaming Ramen Bowl Logo
            dx3 = (x - 320) / 38.0
            dy3 = (y - 138) / 38.0
            # Bowl hemisphere
            if dy3 <= 0.0 and (dx3*dx3 + dy3*dy3) < 1.0:
                img_data[y, x, :3] = indigo[:3]
                # Rim accent
                if abs(dy3) < 0.12 and abs(dx3) < 0.98:
                    img_data[y, x, :3] = red_accent[:3]
            # Golden broth
            if 0.0 < dy3 < 0.18 and abs(dx3) < 0.92:
                img_data[y, x, :3] = [0.94, 0.76, 0.28]
            # Steam plumes
            if 0.22 <= dy3 < 0.85 and abs(dx3) < 0.75:
                phase = math.sin(dy3 * 14.0 + dx3 * 5.0)
                if abs(phase - dx3 * 2.2) < 0.25:
                    img_data[y, x, :3] = red_accent[:3]
                    
            # Panel 4: Kanji 拉麺 (Ramen)
            dx4 = abs(x - 448)
            dy4 = y - 140
            if dx4 < 26 and abs(dy4) < 34:
                if dx4 < 4 or abs(dy4) < 4 or abs(dy4 - 16) < 4 or abs(dy4 + 16) < 4:
                    img_data[y, x, :3] = indigo[:3]

    if "Tex_Noren" in bpy.data.images:
        bpy.data.images.remove(bpy.data.images["Tex_Noren"])
    img = bpy.data.images.new("Tex_Noren", width=w, height=h)
    img.pixels.foreach_set(img_data.flatten())
    img.pack()
    return img

def create_lantern_texture():
    w, h = 256, 256
    img_data = np.zeros((h, w, 4), dtype=np.float32)
    
    # Rich vermilion red lantern paper
    red_paper = np.array([0.94, 0.16, 0.10, 1.0], dtype=np.float32)
    img_data[:, :] = red_paper
    
    # Horizontal bamboo rib hoops
    for y in range(h):
        rib = math.sin(y * math.pi / 10.0)
        img_data[y, :, :3] *= (0.90 + 0.10 * rib)
        
    # Top and bottom black wooden bands & brass trim
    band_h = 26
    black = np.array([0.06, 0.05, 0.05, 1.0], dtype=np.float32)
    gold = np.array([0.92, 0.78, 0.28, 1.0], dtype=np.float32)
    img_data[:band_h, :] = black
    img_data[-band_h:, :] = black
    img_data[band_h:band_h+4, :] = gold
    img_data[-band_h-4:-band_h, :] = gold
    
    # Bold black calligraphy kanji on front and back (x=64 and x=192)
    for y in range(band_h + 12, h - band_h - 12):
        for x in range(w):
            for cx in [64, 192]:
                dx = abs(x - cx)
                # Upper character "拉"
                if 142 < y < 210:
                    if dx < 6 or (dx < 32 and abs(y - 195) < 6) or (dx < 26 and abs(y - 170) < 6) or (dx < 34 and abs(y - 148) < 6):
                        img_data[y, x, :3] = black[:3]
                # Lower character "麺"
                if 48 < y < 118:
                    if dx < 6 or (dx < 32 and abs(y - 110) < 6) or (dx < 24 and abs(y - 84) < 6) or (dx < 34 and abs(y - 58) < 6):
                        img_data[y, x, :3] = black[:3]

    if "Tex_Lantern" in bpy.data.images:
        bpy.data.images.remove(bpy.data.images["Tex_Lantern"])
    img = bpy.data.images.new("Tex_Lantern", width=w, height=h)
    img.pixels.foreach_set(img_data.flatten())
    img.pack()
    return img

def create_narutomaki_texture():
    w, h = 256, 256
    img_data = np.zeros((h, w, 4), dtype=np.float32)
    
    white_base = np.array([0.97, 0.96, 0.94, 1.0], dtype=np.float32)
    pink_spiral = np.array([0.95, 0.22, 0.52, 1.0], dtype=np.float32)
    crust_pink = np.array([0.94, 0.28, 0.55, 1.0], dtype=np.float32)
    
    cx, cy = w / 2.0, h / 2.0
    max_r = w * 0.46
    
    for y in range(h):
        for x in range(w):
            dx = x - cx
            dy = y - cy
            r = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx)
            
            # Scalloped edges
            num_scallops = 14
            scallop_r = max_r * (0.95 + 0.05 * math.cos(num_scallops * angle))
            
            if r <= scallop_r:
                img_data[y, x] = white_base
                # Outer pink serrated edge
                if r > scallop_r * 0.91:
                    img_data[y, x] = crust_pink
                # Center pink spiral
                if r < max_r * 0.78:
                    theta = (angle + 4.0 * math.pi) % (2.0 * math.pi)
                    turn = (r / (max_r * 0.78)) * 2.6 * (2.0 * math.pi)
                    diff = (turn - theta) % (2.0 * math.pi)
                    if diff < 1.05 or diff > (2.0 * math.pi - 0.25):
                        img_data[y, x] = pink_spiral
            else:
                img_data[y, x] = white_base
                
    if "Tex_Naruto" in bpy.data.images:
        bpy.data.images.remove(bpy.data.images["Tex_Naruto"])
    img = bpy.data.images.new("Tex_Naruto", width=w, height=h)
    img.pixels.foreach_set(img_data.flatten())
    img.pack()
    return img

def create_chashu_texture():
    w, h = 256, 256
    img_data = np.zeros((h, w, 4), dtype=np.float32)
    
    meat_color = np.array([0.76, 0.44, 0.28, 1.0], dtype=np.float32)
    fat_color = np.array([0.95, 0.92, 0.84, 1.0], dtype=np.float32)
    crust_color = np.array([0.34, 0.16, 0.08, 1.0], dtype=np.float32)
    
    cx, cy = w / 2.0, h / 2.0
    max_r = w * 0.47
    
    rng = np.random.RandomState(101)
    noise_field = rng.rand(h, w) * 0.08
    
    for y in range(h):
        for x in range(w):
            dx = x - cx
            dy = y - cy
            r = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx)
            
            if r <= max_r:
                # Pork belly spiral marbling
                spiral = math.sin(r * 0.14 + angle * 1.5 + noise_field[y, x] * 4.0)
                if spiral > 0.30:
                    col = fat_color.copy()
                else:
                    col = meat_color.copy()
                    
                # Caramelized dark grilled rim
                if r > max_r * 0.86:
                    blend = (r - max_r * 0.86) / (max_r * 0.14)
                    col = col * (1.0 - blend) + crust_color * blend
                    
                col[:3] += (noise_field[y, x] - 0.04)
                img_data[y, x] = col
            else:
                img_data[y, x] = crust_color
                
    if "Tex_Chashu" in bpy.data.images:
        bpy.data.images.remove(bpy.data.images["Tex_Chashu"])
    img = bpy.data.images.new("Tex_Chashu", width=w, height=h)
    img.pixels.foreach_set(img_data.flatten())
    img.pack()
    return img

def create_bowl_pattern_texture():
    w, h = 512, 64
    img_data = np.zeros((h, w, 4), dtype=np.float32)
    
    red_bg = np.array([0.82, 0.14, 0.10, 1.0], dtype=np.float32)
    gold_pattern = np.array([0.96, 0.84, 0.32, 1.0], dtype=np.float32)
    
    img_data[:, :] = red_bg
    tile_w = 32
    for x in range(w):
        tx = x % tile_w
        for y in range(h):
            if y < 6 or y > h - 7:
                img_data[y, x] = gold_pattern
            elif (10 <= y <= 16 and tx < 22) or \
                 (h - 17 <= y <= h - 11 and tx > 10) or \
                 (tx < 6 and 10 <= y <= h - 11) or \
                 (26 <= tx <= 31 and 10 <= y <= h - 11) or \
                 (12 <= tx <= 20 and 24 <= y <= 40):
                img_data[y, x] = gold_pattern
                
    if "Tex_BowlBorder" in bpy.data.images:
        bpy.data.images.remove(bpy.data.images["Tex_BowlBorder"])
    img = bpy.data.images.new("Tex_BowlBorder", width=w, height=h)
    img.pixels.foreach_set(img_data.flatten())
    img.pack()
    return img
