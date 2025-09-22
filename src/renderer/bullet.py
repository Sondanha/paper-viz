# src/renderer/bullet.py

from PIL import Image, ImageDraw
from src.renderer.base import (
    load_font,
    wrap_text,
    draw_title_bar,
    draw_content_box,
    COLORS,
    normalize_slots,
)


def render_bullet_layout(section, out_path, width=1280, height=720, margin=60):
    img = Image.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(42)   # 제목 조금 줄임
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

    box_height = (height - content_y - margin - (n - 1) * 40) // n
    box_width = width - 2 * margin
    y = content_y + 20

    for i, (label, slot_data) in enumerate(slots.items()):
        # slot_data는 {"subtitle": "...", "content": [...] } 구조일 수 있음
        if isinstance(slot_data, dict):
            subtitle = slot_data.get("subtitle", label)
            content = normalize_slots(slot_data.get("content", []))
        else:
            subtitle = label
            content = normalize_slots(slot_data)

        # 큰 박스
        draw.rounded_rectangle(
            [margin, y, margin + box_width, y + box_height],
            radius=15,
            fill=COLORS["content_box"],
            outline=COLORS["content_outline"],
            width=3,
        )

        # 서브타이틀 박스
        sub_h = 40
        draw.rounded_rectangle(
            [margin + 15, y + 15, margin + box_width - 15, y + 15 + sub_h],
            radius=8, fill=(230, 240, 255), outline=(100, 150, 255), width=2
        )
        draw.text((margin + 25, y + 22), subtitle, font=subtitle_font, fill=(0, 60, 120))

        # 본문 텍스트
        text_y = y + 15 + sub_h + 10
        for point in content:
            for wrapped in wrap_text(draw, point, body_font, box_width - 40):
                draw.text((margin + 20, text_y), f"- {wrapped}", font=body_font, fill=COLORS["text"])
                text_y += body_font.size + 12

        # 화살표 (박스 간 연결)
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
