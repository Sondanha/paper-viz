# src/renderer/table.py

from PIL import Image, ImageDraw
from src.renderer.base import load_font, draw_title_bar, draw_content_box, COLORS, wrap_text

def render_table_layout(section, out_path, width=1280, height=720, margin=60):
    img = Image.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(42)   # 제목 조금 줄임 → 길 경우 잘림 방지
    cell_font = load_font(22)
    header_font = load_font(26)

    title = section.get("slide_title", section.get("title", ""))
    slots = section.get("slots", {})
    comparison = slots.get("Comparison", [])
    subtitle = slots.get("Subtitle", "비교표")  # yaml에서 subtitle 받을 수 있도록

    draw_title_bar(draw, width, title, title_font)
    content_y = draw_content_box(draw, width, height)

    if not comparison:
        img.save(out_path)
        return

    # 🔹 상단 subtitle 박스 추가
    subtitle_h = 40
    draw.rounded_rectangle(
        [margin, content_y + 10, width - margin, content_y + 10 + subtitle_h],
        radius=8, fill=(230, 240, 255), outline=(100, 150, 255), width=2
    )
    tw = draw.textlength(subtitle, font=header_font)
    draw.text(((width - tw) // 2, content_y + 18), subtitle, font=header_font, fill=(0, 60, 120))

    table_y = content_y + 10 + subtitle_h + 15

    rows = len(comparison)
    cols = max(len(r) for r in comparison)
    cell_w = (width - 2 * margin) // cols
    cell_h = (height - table_y - margin) // rows

    y = table_y
    for r_idx, r in enumerate(comparison):
        x = margin
        for c_idx, cell in enumerate(r):
            if r_idx == 0:
                fill_color = (255, 240, 200)
                outline_color = (200, 150, 50)
                font = header_font
                text_fill = (80, 50, 0)
            else:
                fill_color = "white"
                outline_color = (180, 180, 180)
                font = cell_font
                text_fill = COLORS["text"]

            draw.rectangle([x, y, x + cell_w, y + cell_h],
                           outline=outline_color, width=2, fill=fill_color)

            cell_text = str(cell)
            text_y = y + 10
            for line in wrap_text(draw, cell_text, font, cell_w - 20):
                draw.text((x + 10, text_y), line, font=font, fill=text_fill)
                text_y += font.size + 8

            x += cell_w
        y += cell_h

    img.save(out_path)
