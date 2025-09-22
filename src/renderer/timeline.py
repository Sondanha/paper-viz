# src/renderer/timeline.py

from PIL import Image, ImageDraw
from src.renderer.base import (
    load_font,
    draw_title_bar,
    draw_content_box,
    COLORS,
    normalize_slots,
    wrap_text,
)

def render_timeline(section, out_path, width=1280, height=720, margin=60):
    img = Image.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(42)  # 제목 조금 줄여서 잘림 방지
    body_font = load_font(22)
    label_font = load_font(22)

    title = section.get("slide_title", section.get("title", ""))
    steps = section.get("slots", {}).get("FutureWork", [])

    draw_title_bar(draw, width, title, title_font)
    content_y = draw_content_box(draw, width, height)

    if not steps:
        img.save(out_path)
        return

    steps = normalize_slots(steps)

    n = len(steps)
    spacing = (width - 2 * margin) // max(1, (n - 1))
    y = content_y + (height - content_y) // 2

    for i, step in enumerate(steps):
        x = margin + i * spacing

        # 서브타이틀 추출 (":" 기준 split → 앞부분만)
        subtitle = step.split(":")[0].strip() if ":" in step else f"단계 {i+1}"

        # 노드 (원)
        draw.ellipse([x - 20, y - 20, x + 20, y + 20],
                     fill=(255, 204, 0), outline=(150, 120, 30), width=3)

        # 서브타이틀 박스 (노드 위쪽)
        box_w, box_h = 180, 50
        draw.rounded_rectangle(
            [x - box_w//2, y - 80, x + box_w//2, y - 30],
            radius=8, fill=(255, 240, 200), outline=(200, 150, 50), width=2
        )
        # 텍스트 가운데 정렬
        tw = draw.textlength(subtitle, font=label_font)
        draw.text((x - tw//2, y - 68), subtitle, font=label_font, fill=(80, 50, 0))

        # 본문 텍스트 (노드 아래)
        text_y = y + 35
        for wrapped in wrap_text(draw, step, body_font, 200):
            draw.text((x - 90, text_y), wrapped, font=body_font, fill=COLORS["text"])
            text_y += body_font.size + 8

        # 연결선
        if i < n - 1:
            nx = margin + (i + 1) * spacing
            draw.line([(x + 20, y), (nx - 20, y)], fill=(150, 120, 30), width=4)
            draw.polygon([(nx - 20, y), (nx - 30, y - 10), (nx - 30, y + 10)],
                         fill=(150, 120, 30))

    img.save(out_path)
