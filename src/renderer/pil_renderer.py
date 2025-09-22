# src/renderer/pil_renderer.py

from PIL import Image, ImageDraw, ImageFont
from .base import wrap_text, normalize_slots

def render_bullet_layout(title: str, bullets: list[str] | str, out_path: str,
                         width=1280, height=720, margin=60):
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("Pretendard-Bold.ttf", 48)
        font_body = ImageFont.truetype("Pretendard-Regular.ttf", 32)
    except OSError:
        # Pretendard 없으면 기본 폰트 fallback
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

    # Title
    draw.text((margin, margin), title, font=font_title, fill="black")

    # Bullets
    y = margin + 80
    for point in normalize_slots(bullets):
        for wrapped in wrap_text(draw, point, font_body, width - 2 * margin):
            draw.text((margin + 40, y), f"• {wrapped}", font=font_body, fill="black")
            y += font_body.size + 14  # 줄간격 넉넉히

    img.save(out_path)
