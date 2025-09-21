# src/renderer/pil_renderer.py

from PIL import Image, ImageDraw, ImageFont

def render_bullet_layout(title: str, bullets: list[str], out_path: str):
    img = Image.new("RGB", (1280, 720), "white")
    draw = ImageDraw.Draw(img)
    font_title = ImageFont.truetype("Pretendard-Bold.ttf", 48)
    font_body = ImageFont.truetype("Pretendard-Regular.ttf", 32)

    # Title
    draw.text((60, 40), title, font=font_title, fill="black")

    # Bullets
    y = 140
    for bullet in bullets:
        draw.text((100, y), f"• {bullet}", font=font_body, fill="black")
        y += 60

    img.save(out_path)
