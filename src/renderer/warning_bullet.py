# src/renderer/warning_bullet.py

from PIL import Image, ImageDraw
from src.renderer.base import load_font, wrap_text, draw_title_bar, draw_content_box, COLORS

def render_warning_bullet(section, out_path, width=1280, height=720, margin=60):
    img = Image.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(48)
    label_font = load_font(28)
    body_font = load_font(24)

    title = section.get("slide_title", section.get("title", ""))
    slots = section.get("slots", {})

    draw_title_bar(draw, width, title, title_font)
    content_y = draw_content_box(draw, width, height)

    y = content_y + 20
    for label, text in slots.items():
        draw.rounded_rectangle(
            [margin, y, width - margin, y + 120],
            radius=15, fill=(255, 245, 245), outline=(255, 100, 100), width=3
        )
        draw.text((margin + 20, y + 10), f"⚠ {label}", font=label_font, fill=(180, 30, 30))

        text_y = y + 50
        for line in wrap_text(draw, str(text), body_font, width - 2 * margin - 40):
            draw.text((margin + 20, text_y), line, font=body_font, fill=COLORS["text"])
            text_y += body_font.size + 6
        y += 140

    img.save(out_path)

