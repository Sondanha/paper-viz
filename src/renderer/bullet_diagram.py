# src/renderer/bullet_diagram.py

from PIL import Image, ImageDraw
from .base import load_font, wrap_text

def render_bullet_diagram(section, out_path, width=1280, height=720, margin=60):
    """
    불릿 + 간단 도형 다이어그램.
    왼쪽은 불릿 포인트, 오른쪽은 큰 박스(아이디어 박스 느낌).
    """
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    body_font = load_font(size=28)

    # 왼쪽 불릿
    text = section.get("text", "")
    y = margin
    for line, w, h in wrap_text(draw, text, body_font, (width // 2) - 2*margin):
        draw.text((margin, y), f"• {line}", font=body_font, fill="black")
        y += h + 10

    # 오른쪽 박스
    box_x0 = width // 2 + margin
    box_y0 = margin
    box_x1 = width - margin
    box_y1 = height - margin
    draw.rectangle([box_x0, box_y0, box_x1, box_y1], outline="black", width=3)
    draw.text((box_x0 + 20, box_y0 + 20), "Diagram Placeholder", font=body_font, fill="gray")

    img.save(out_path)
