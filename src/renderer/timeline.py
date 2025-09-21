# src/renderer/timeline.py

from PIL import Image, ImageDraw
from src.renderer.base import load_font, draw_title_bar, draw_content_box, COLORS

def render_timeline(section, out_path, width=1280, height=720, margin=60):
    img = Image.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(48)
    body_font = load_font(24)

    title = section.get("slide_title", section.get("title", ""))
    steps = section.get("slots", {}).get("FutureWork", [])

    draw_title_bar(draw, width, title, title_font)
    content_y = draw_content_box(draw, width, height)

    if not steps:
        img.save(out_path)
        return

    n = len(steps)
    spacing = (width - 2 * margin) // (n - 1)
    y = content_y + (height - content_y) // 2

    for i, step in enumerate(steps):
        x = margin + i * spacing
        draw.ellipse([x - 20, y - 20, x + 20, y + 20], fill=(255, 204, 0), outline=(150, 120, 30), width=3)
        draw.text((x - 40, y + 30), step, font=body_font, fill=COLORS["text"])
        if i < n - 1:
            nx = margin + (i + 1) * spacing
            draw.line([(x + 20, y), (nx - 20, y)], fill=(150, 120, 30), width=4)

    img.save(out_path)

