# src/renderer/table.py

from PIL import Image, ImageDraw
from src.renderer.base import load_font, draw_title_bar, draw_content_box, COLORS

def render_table_layout(section, out_path, width=1280, height=720, margin=60):
    img = Image.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(48)
    cell_font = load_font(24)

    title = section.get("slide_title", section.get("title", ""))
    comparison = section.get("slots", {}).get("Comparison", [])

    draw_title_bar(draw, width, title, title_font)
    content_y = draw_content_box(draw, width, height)

    if not comparison:
        img.save(out_path)
        return

    rows = len(comparison)
    cols = max(len(r) for r in comparison)
    cell_w = (width - 2 * margin) // cols
    cell_h = (height - content_y - margin) // rows

    y = content_y + 20
    for r in comparison:
        x = margin
        for cell in r:
            draw.rectangle([x, y, x + cell_w, y + cell_h], outline=(180, 180, 180), width=2, fill="white")
            draw.text((x + 10, y + 10), str(cell), font=cell_font, fill=COLORS["text"])
            x += cell_w
        y += cell_h

    img.save(out_path)



