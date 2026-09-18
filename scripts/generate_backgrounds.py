import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

OUTPUT_DIR = Path("backend/templates/slides/assets/backgrounds")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 1080
HEIGHT = 1350

def create_background(idx: int):
    random.seed(idx * 777 + 42)
    
    # 1. Base gradient
    base = Image.new("RGB", (WIDTH, HEIGHT), (2, 2, 8))
    draw = ImageDraw.Draw(base)
    
    # Gradient schemes
    palettes = [
        # 1: Deep Cosmic Purple & Cyan
        {"bg_top": (16, 6, 36), "bg_bot": (3, 12, 30), "glows": [
            (250, 320, 520, (124, 58, 237, 180)),
            (880, 950, 560, (6, 182, 212, 160)),
            (540, 675, 620, (37, 99, 235, 140)),
        ], "grid": True, "stars": 190, "circles": True},
        # 2: Cyber Blue & Neon Magenta
        {"bg_top": (8, 18, 42), "bg_bot": (28, 6, 35), "glows": [
            (850, 250, 520, (236, 72, 153, 170)),
            (200, 800, 560, (37, 99, 235, 170)),
            (500, 1100, 480, (124, 58, 237, 150)),
        ], "grid": False, "stars": 220, "rings": True},
        # 3: Dark Electric Violet & Emerald Cyber
        {"bg_top": (20, 8, 40), "bg_bot": (4, 25, 25), "glows": [
            (300, 400, 550, (139, 92, 246, 170)),
            (780, 780, 500, (16, 185, 129, 130)),
            (900, 300, 420, (59, 130, 246, 140)),
        ], "grid": True, "stars": 180, "streamers": True},
        # 4: Sunset Quantum Neon (Pink / Purple / Amber)
        {"bg_top": (32, 10, 28), "bg_bot": (8, 8, 36), "glows": [
            (700, 400, 550, (244, 63, 94, 160)),
            (350, 900, 520, (124, 58, 237, 170)),
            (800, 1050, 460, (249, 115, 22, 120)),
        ], "grid": False, "stars": 200, "circles": True},
        # 5: Deep Space Matrix (Cobalt & Cyan Glow)
        {"bg_top": (5, 15, 38), "bg_bot": (2, 6, 22), "glows": [
            (540, 350, 580, (37, 99, 235, 180)),
            (180, 1000, 500, (6, 182, 212, 160)),
            (920, 800, 450, (147, 51, 234, 140)),
        ], "grid": True, "stars": 240, "rings": True},
        # 6: Ultra Violet & Dark Nebula
        {"bg_top": (24, 6, 42), "bg_bot": (6, 4, 25), "glows": [
            (250, 500, 550, (168, 85, 247, 180)),
            (820, 600, 500, (236, 72, 153, 150)),
            (400, 1150, 540, (59, 130, 246, 150)),
        ], "grid": False, "stars": 200, "streamers": True},
        # 7: Cyberpunk Prism (Cyan, Gold, Purple)
        {"bg_top": (12, 22, 36), "bg_bot": (26, 14, 12), "glows": [
            (800, 350, 500, (6, 182, 212, 170)),
            (250, 750, 550, (124, 58, 237, 160)),
            (600, 1100, 460, (234, 179, 8, 120)),
        ], "grid": True, "stars": 210, "circles": True},
        # 8: Deep Velvet Noir & Electric Rose
        {"bg_top": (26, 6, 24), "bg_bot": (8, 6, 32), "glows": [
            (350, 300, 540, (225, 29, 72, 160)),
            (750, 850, 560, (124, 58, 237, 170)),
            (200, 1150, 450, (6, 182, 212, 130)),
        ], "grid": False, "stars": 190, "rings": True},
        # 9: Quantum Blue Waves & Violet Glow
        {"bg_top": (6, 20, 44), "bg_bot": (18, 6, 36), "glows": [
            (650, 300, 560, (37, 99, 235, 180)),
            (200, 600, 500, (139, 92, 246, 170)),
            (800, 1000, 520, (6, 182, 212, 150)),
        ], "grid": True, "stars": 230, "streamers": True},
        # 10: Midnight Horizon (Neon Purple, Blue, Pink)
        {"bg_top": (18, 8, 38), "bg_bot": (4, 18, 34), "glows": [
            (500, 450, 600, (124, 58, 237, 180)),
            (880, 850, 520, (236, 72, 153, 160)),
            (180, 950, 500, (37, 99, 235, 160)),
        ], "grid": True, "stars": 260, "rings": True},
    ]
    
    cfg = palettes[(idx - 1) % len(palettes)]
    top_c = cfg["bg_top"]
    bot_c = cfg["bg_bot"]
    
    # Render vertical base gradient
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_c[0] + (bot_c[0] - top_c[0]) * ratio)
        g = int(top_c[1] + (bot_c[1] - top_c[1]) * ratio)
        b = int(top_c[2] + (bot_c[2] - top_c[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
        
    # 2. Glowing nebulae
    glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    for (gx, gy, radius, col) in cfg["glows"]:
        for step in range(radius, 0, -20):
            alpha = int((1.0 - (step / radius) ** 1.6) * col[3])
            glow_draw.ellipse(
                [gx - step, gy - step, gx + step, gy + step],
                fill=(col[0], col[1], col[2], alpha)
            )
            
    # Apply heavy blur to nebulae
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(55))
    base.paste(glow_layer, (0, 0), glow_layer)
    
    # 3. Optional Cyber Grid overlay
    if cfg.get("grid"):
        grid_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        grid_draw = ImageDraw.Draw(grid_layer)
        grid_step = 80
        for x in range(0, WIDTH, grid_step):
            grid_draw.line([(x, 0), (x, HEIGHT)], fill=(255, 255, 255, 18), width=1)
        for y in range(0, HEIGHT, grid_step):
            grid_draw.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, 18), width=1)
        base.paste(grid_layer, (0, 0), grid_layer)
        
    # 4. Optional Light Rings / Orbits
    if cfg.get("rings"):
        ring_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        ring_draw = ImageDraw.Draw(ring_layer)
        rcx, rcy = random.randint(300, 780), random.randint(350, 950)
        for rad in [260, 400, 560]:
            ring_draw.ellipse(
                [rcx - rad, rcy - rad, rcx + rad, rcy + rad],
                outline=(147, 51, 234, 45), width=2
            )
            # Add an accent arc
            ring_draw.arc(
                [rcx - rad, rcy - rad, rcx + rad, rcy + rad],
                start=random.randint(0, 180), end=random.randint(190, 360),
                fill=(6, 182, 212, 95), width=3
            )
        ring_layer = ring_layer.filter(ImageFilter.GaussianBlur(2))
        base.paste(ring_layer, (0, 0), ring_layer)

    # 5. Optional Bokeh circles
    if cfg.get("circles"):
        circ_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        circ_draw = ImageDraw.Draw(circ_layer)
        for _ in range(16):
            cx = random.randint(80, WIDTH - 80)
            cy = random.randint(80, HEIGHT - 80)
            crad = random.randint(45, 140)
            col_choice = random.choice([
                (124, 58, 237, 40),
                (37, 99, 235, 36),
                (236, 72, 153, 34),
                (6, 182, 212, 38)
            ])
            circ_draw.ellipse([cx - crad, cy - crad, cx + crad, cy + crad], fill=col_choice)
        circ_layer = circ_layer.filter(ImageFilter.GaussianBlur(14))
        base.paste(circ_layer, (0, 0), circ_layer)

    # 6. Optional Light Streamer lines
    if cfg.get("streamers"):
        str_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        str_draw = ImageDraw.Draw(str_layer)
        for _ in range(6):
            sx = random.randint(-100, WIDTH)
            sy = random.randint(0, HEIGHT // 2)
            ex = sx + random.randint(300, 600)
            ey = sy + random.randint(400, 800)
            str_draw.line([(sx, sy), (ex, ey)], fill=(124, 58, 237, 50), width=2)
            str_draw.line([(sx + 24, sy), (ex + 24, ey)], fill=(6, 182, 212, 60), width=2)
        str_layer = str_layer.filter(ImageFilter.GaussianBlur(2))
        base.paste(str_layer, (0, 0), str_layer)

    # 7. Quantum Starfield & Cosmic Dust
    star_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    star_draw = ImageDraw.Draw(star_layer)
    for _ in range(cfg["stars"]):
        sx = random.randint(0, WIDTH)
        sy = random.randint(0, HEIGHT)
        srad = random.choice([1, 1, 1, 2, 2, 3])
        brightness = random.randint(140, 255)
        tint = random.choice([
            (brightness, brightness, brightness),
            (brightness - 25, brightness - 5, brightness),
            (brightness, brightness - 35, brightness),
            (brightness - 35, brightness, brightness)
        ])
        s_alpha = random.randint(90, 230)
        star_draw.ellipse([sx - srad, sy - srad, sx + srad, sy + srad], fill=(tint[0], tint[1], tint[2], s_alpha))
        if srad >= 2 and random.random() < 0.25:
            # Cross flare
            star_draw.line([(sx - 10, sy), (sx + 10, sy)], fill=(tint[0], tint[1], tint[2], s_alpha // 2), width=1)
            star_draw.line([(sx, sy - 10), (sx, sy + 10)], fill=(tint[0], tint[1], tint[2], s_alpha // 2), width=1)

    base.paste(star_layer, (0, 0), star_layer)
    
    # Save optimized JPEG
    out_file = OUTPUT_DIR / f"bg_{idx}.jpg"
    base.save(out_file, "JPEG", quality=94)
    print(f"Generated {out_file.name} ({out_file.stat().st_size} bytes)")

def main():
    for i in range(1, 11):
        create_background(i)

if __name__ == "__main__":
    main()
