# src/renderer/warning_bullet.py

from PIL import Image, ImageDraw
from src.renderer.base import (
    load_font,
    wrap_text,
    draw_title_bar,
    draw_content_box,
    COLORS,
    normalize_slots,
)
def render_warning_bullet(section, out_path, width=1280, height=720, margin=60):
    img = Image.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(42)  # 제목 조금 줄임 (잘림 방지)
    label_font = load_font(26)
    body_font = load_font(22)

    title = section.get("slide_title", section.get("title", ""))
    slots = section.get("slots", {})

    draw_title_bar(draw, width, title, title_font)
    content_y = draw_content_box(draw, width, height)

    y = content_y + 20
    for label, text in slots.items():
        lines = []
        for point in normalize_slots(text):
            lines.extend(wrap_text(draw, point, body_font, width - 2 * margin - 40))

        # 동적 박스 높이
        box_h = 70 + len(lines) * (body_font.size + 10)

        # 슬롯별 색상 구분
        if label.lower().startswith("lim"):
            fill_color, outline_color = (255, 240, 240), (220, 80, 80)
        else:
            fill_color, outline_color = (255, 250, 230), (220, 180, 50)

        # 큰 박스
        draw.rounded_rectangle(
            [margin, y, width - margin, y + box_h],
            radius=15, fill=fill_color, outline=outline_color, width=3
        )

        # 서브타이틀 박스
        st_h = 36
        draw.rounded_rectangle(
            [margin + 15, y + 10, width - margin - 15, y + 10 + st_h],
            radius=8, fill=(255, 220, 220), outline=outline_color, width=2
        )
        draw.text((margin + 25, y + 15), f"⚠ {label}", font=label_font, fill=(150, 40, 40))

        # 본문
        text_y = y + 20 + st_h + 10
        for line in lines:
            draw.text((margin + 25, text_y), line, font=body_font, fill=COLORS["text"])
            text_y += body_font.size + 8

        y += box_h + 20

    img.save(out_path)
