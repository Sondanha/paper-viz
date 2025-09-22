# src/renderer/split.py

from PIL import Image, ImageDraw
from src.renderer.base import (
    load_font,
    wrap_text,
    draw_title_bar,
    draw_content_box,
    COLORS,
    normalize_slots,
)

def render_split_layout(section, out_path, width=1280, height=720, margin=60):
    img = Image.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(42)   # 제목 살짝 줄임
    label_font = load_font(26)
    body_font = load_font(22)

    title = section.get("slide_title", section.get("title", ""))
    slots = section.get("slots", {})

    draw_title_bar(draw, width, title, title_font)
    content_y = draw_content_box(draw, width, height)

    mid_x = width // 2
    box_height = height - content_y - margin
    subtitle_h = 40

    # Left
    left_text = slots.get("Left", {}).get("content", [])
    left_subtitle = slots.get("Left", {}).get("subtitle", "왼쪽 영역")
    left_box = [margin, content_y + 20, mid_x - 10, content_y + box_height]
    draw.rounded_rectangle(left_box, radius=15, fill=(220,240,255), outline=(100,150,255), width=3)

    draw.rounded_rectangle(
        [left_box[0] + 10, left_box[1] + 10, left_box[2] - 10, left_box[1] + 10 + subtitle_h],
        radius=8, fill=(180,210,255), outline=(80,120,200), width=2
    )
    tw = draw.textlength(left_subtitle, font=label_font)
    draw.text(((left_box[0] + left_box[2] - tw) // 2, left_box[1] + 18),
              left_subtitle, font=label_font, fill=(0,50,120))

    y = left_box[1] + 10 + subtitle_h + 15
    for point in normalize_slots(left_text):
        for wrapped in wrap_text(draw, point, body_font, mid_x - margin - 30):
            draw.text((margin + 20, y), f"- {wrapped}", font=body_font, fill=COLORS["text"])
            y += body_font.size + 14

    # Right
    right_text = slots.get("Right", {}).get("content", [])
    right_subtitle = slots.get("Right", {}).get("subtitle", "오른쪽 영역")
    right_box = [mid_x + 10, content_y + 20, width - margin, content_y + box_height]
    draw.rounded_rectangle(right_box, radius=15, fill=(255,235,210), outline=(255,150,80), width=3)

    draw.rounded_rectangle(
        [right_box[0] + 10, right_box[1] + 10, right_box[2] - 10, right_box[1] + 10 + subtitle_h],
        radius=8, fill=(255,210,160), outline=(200,120,60), width=2
    )
    tw = draw.textlength(right_subtitle, font=label_font)
    draw.text(((right_box[0] + right_box[2] - tw) // 2, right_box[1] + 18),
              right_subtitle, font=label_font, fill=(120,60,0))

    y = right_box[1] + 10 + subtitle_h + 15
    for point in normalize_slots(right_text):
        for wrapped in wrap_text(draw, point, body_font, width - mid_x - margin - 30):
            draw.text((mid_x + 30, y), f"- {wrapped}", font=body_font, fill=COLORS["text"])
            y += body_font.size + 14

    img.save(out_path)
