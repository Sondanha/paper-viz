# src/renderer/bullet.py

from PIL import Image, ImageDraw
from src.renderer.base import (
    load_font,
    wrap_text,
    draw_title_bar,
    draw_content_box,
    COLORS,
)

def render_bullet_layout(section, out_path, width=1280, height=720, margin=60):
    img = Image.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(48)
    label_font = load_font(28)
    body_font = load_font(24)

    title = section.get("slide_title", section.get("title", ""))
    slots = section.get("slots", {})

    draw_title_bar(draw, width, title, title_font)
    content_y = draw_content_box(draw, width, height)

    n = len(slots)
    box_height = (height - content_y - margin - (n - 1) * 40) // n
    box_width = width - 2 * margin
    y = content_y + 20

    for i, (label, text) in enumerate(slots.items()):
        draw.rounded_rectangle(
            [margin, y, margin + box_width, y + box_height],
            radius=15,
            fill=COLORS["content_box"],
            outline=COLORS["content_outline"],
            width=3,
        )
        draw.text((margin + 20, y + 15), label, font=label_font, fill=(120, 80, 0))

        text_y = y + 60
        for line in wrap_text(draw, str(text), body_font, box_width - 40):
            draw.text((margin + 20, text_y), line, font=body_font, fill=COLORS["text"])
            text_y += body_font.size + 6

        if i < n - 1:
            arrow_x = width // 2
            arrow_y1 = y + box_height
            arrow_y2 = arrow_y1 + 30
            draw.line([(arrow_x, arrow_y1), (arrow_x, arrow_y2)], fill=(150, 120, 30), width=4)
            draw.polygon(
                [(arrow_x, arrow_y2 + 10), (arrow_x - 10, arrow_y2 - 5), (arrow_x + 10, arrow_y2 - 5)],
                fill=(150, 120, 30),
            )
        y += box_height + 40

    img.save(out_path)



