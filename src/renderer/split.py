# src/renderer/split.py

from PIL import Image, ImageDraw
from src.renderer.base import load_font, wrap_text, draw_title_bar, draw_content_box, COLORS

def render_split_layout(section, out_path, width=1280, height=720, margin=60):
    img = Image.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(48)
    body_font = load_font(24)

    title = section.get("slide_title", section.get("title", ""))
    slots = section.get("slots", {})
    left_text = slots.get("Left", "(왼쪽 없음)")
    right_text = slots.get("Right", "(오른쪽 없음)")

    draw_title_bar(draw, width, title, title_font)
    content_y = draw_content_box(draw, width, height)

    mid_x = width // 2
    box_height = height - content_y - margin

    # 왼쪽 박스
    draw.rounded_rectangle(
        [margin, content_y + 20, mid_x - 10, content_y + box_height],
        radius=15, fill=(220, 240, 255), outline=(100, 150, 255), width=3
    )
    y = content_y + 40
    for line in wrap_text(draw, left_text, body_font, mid_x - margin - 30):
        draw.text((margin + 20, y), line, font=body_font, fill=COLORS["text"])
        y += body_font.size + 6

    # 오른쪽 박스
    draw.rounded_rectangle(
        [mid_x + 10, content_y + 20, width - margin, content_y + box_height],
        radius=15, fill=(255, 235, 210), outline=(255, 150, 80), width=3
    )
    y = content_y + 40
    for line in wrap_text(draw, right_text, body_font, width - mid_x - margin - 30):
        draw.text((mid_x + 30, y), line, font=body_font, fill=COLORS["text"])
        y += body_font.size + 6

    img.save(out_path)




