# src/renderer/flow_horizontal.py

from PIL import Image, ImageDraw
from src.renderer.base import load_font, wrap_text, draw_title_bar, draw_content_box, COLORS

def render_flow_horizontal(section, out_path, width=1280, height=720, margin=60):
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
    box_width = (width - 2 * margin - (n - 1) * 40) // n
    box_height = height - content_y - margin
    x = margin

    for i, (label, text) in enumerate(slots.items()):
        draw.rounded_rectangle(
            [x, content_y + 20, x + box_width, content_y + box_height],
            radius=15,
            fill=COLORS["content_box"],
            outline=(100, 150, 255),
            width=3,
        )
        draw.text((x + 20, content_y + 40), label, font=label_font, fill=(0, 60, 120))

        text_y = content_y + 80
        for line in wrap_text(draw, str(text), body_font, box_width - 40):
            draw.text((x + 20, text_y), line, font=body_font, fill=COLORS["text"])
            text_y += body_font.size + 6

        if i < n - 1:
            arrow_x1 = x + box_width
            arrow_x2 = arrow_x1 + 30
            arrow_y = content_y + box_height // 2
            draw.line([(arrow_x1, arrow_y), (arrow_x2, arrow_y)], fill=(0, 60, 120), width=4)
            draw.polygon(
                [(arrow_x2 + 10, arrow_y), (arrow_x2 - 5, arrow_y - 10), (arrow_x2 - 5, arrow_y + 10)],
                fill=(0, 60, 120),
            )
        x += box_width + 40

    img.save(out_path)


