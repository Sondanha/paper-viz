# src/renderer/composite.py

from PIL import Image, ImageDraw
from src.renderer.base import (
    load_font,
    wrap_text,
    draw_title_bar,
    draw_content_box,
    COLORS,
    normalize_slots,
)


def render_composite_layout(section, out_path, width=1280, height=720, margin=60):
    img = Image.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(42)
    subtitle_font = load_font(26)
    body_font = load_font(24)

    title = section.get("slide_title", section.get("title", ""))
    slots = section.get("slots", {})

    draw_title_bar(draw, width, title, title_font)
    content_y = draw_content_box(draw, width, height)

    n = len(slots)
    if n == 0:
        img.save(out_path)
        return

    box_width = (width - 2 * margin - (n - 1) * 20) // n
    box_height = height - content_y - margin
    x = margin

    color_map = {
        "Contribution": ((255, 240, 200), (200, 150, 50)),
        "Limitation": ((255, 220, 220), (200, 80, 80)),
        "FutureWork": ((220, 240, 255), (80, 120, 200)),
    }

    for label, slot_data in slots.items():
        if isinstance(slot_data, dict):
            subtitle = slot_data.get("subtitle", label)
            content = normalize_slots(slot_data.get("content", []))
        else:
            subtitle = label
            content = normalize_slots(slot_data)

        draw.rounded_rectangle(
            [x, content_y + 20, x + box_width, content_y + box_height],
            radius=15, fill=COLORS["content_box"], outline=COLORS["content_outline"], width=3
        )

        fill_color, outline_color = color_map.get(label, ((255, 230, 180), (200, 150, 50)))
        subtitle_h = 40
        draw.rounded_rectangle(
            [x + 15, content_y + 30, x + box_width - 15, content_y + 30 + subtitle_h],
            radius=10, fill=fill_color, outline=outline_color, width=2
        )
        draw.text((x + 25, content_y + 35), subtitle, font=subtitle_font, fill=(60, 40, 0))

        text_y = content_y + 30 + subtitle_h + 15
        for point in content:
            for line in wrap_text(draw, point, body_font, box_width - 40):
                draw.text((x + 20, text_y), f"- {line}", font=body_font, fill=COLORS["text"])
                text_y += body_font.size + 10

        x += box_width + 20

    img.save(out_path)
