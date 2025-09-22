# src/renderer/flow_horizontal.py

from PIL import Image, ImageDraw
from src.renderer.base import (
    load_font,
    wrap_text,
    draw_title_bar,
    draw_content_box,
    COLORS,
    normalize_slots,
)


def render_flow_horizontal(section, out_path, width=1280, height=720, margin=60):
    img = Image.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(42)   # 제목 조금 줄임 (길이 대응)
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

    box_width = (width - 2 * margin - (n - 1) * 40) // n
    box_height = height - content_y - margin
    x = margin

    for i, (label, slot_data) in enumerate(slots.items()):
        # 슬롯 데이터 dict 지원 (subtitle + content)
        if isinstance(slot_data, dict):
            subtitle = slot_data.get("subtitle", label)
            content = normalize_slots(slot_data.get("content", []))
        else:
            subtitle = label
            content = normalize_slots(slot_data)

        # 큰 슬롯 박스
        draw.rounded_rectangle(
            [x, content_y + 20, x + box_width, content_y + box_height],
            radius=15,
            fill=COLORS["content_box"],
            outline=(100, 150, 255),
            width=3,
        )

        # 서브타이틀 박스
        subtitle_h = 40
        draw.rounded_rectangle(
            [x + 15, content_y + 30, x + box_width - 15, content_y + 30 + subtitle_h],
            radius=8,
            fill=(200, 220, 255),
            outline=(100, 150, 255),
            width=2,
        )
        # 가운데 정렬
        text_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        text_w = text_bbox[2] - text_bbox[0]
        draw.text(
            (x + (box_width - text_w) // 2, content_y + 35),
            subtitle,
            font=subtitle_font,
            fill=(0, 60, 120),
        )

        # 본문 텍스트 (불릿 스타일)
        text_y = content_y + 30 + subtitle_h + 15
        for point in content:
            for wrapped in wrap_text(draw, point, body_font, box_width - 40):
                draw.text((x + 20, text_y), f"- {wrapped}", font=body_font, fill=COLORS["text"])
                text_y += body_font.size + 14

        # 박스 간 화살표
        if i < n - 1:
            arrow_x1 = x + box_width
            arrow_x2 = arrow_x1 + 30
            arrow_y = content_y + (box_height // 2)
            draw.line([(arrow_x1, arrow_y), (arrow_x2, arrow_y)], fill=(0, 60, 120), width=4)
            draw.polygon(
                [(arrow_x2 + 10, arrow_y), (arrow_x2 - 5, arrow_y - 10), (arrow_x2 - 5, arrow_y + 10)],
                fill=(0, 60, 120),
            )

        x += box_width + 40

    img.save(out_path)
