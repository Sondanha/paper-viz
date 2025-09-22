# src\renderer\bullet_diagram.py

from PIL import Image as PILImage, ImageDraw
from .base import load_font, wrap_text, normalize_slots, draw_title_bar, draw_content_box, COLORS
import tempfile, subprocess, re, hashlib, platform
from pathlib import Path


def _rgb_to_hex(rgb_tuple):
    r, g, b = rgb_tuple
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def _get_korean_font():
    """OS별 기본 한글 폰트 선택"""
    system = platform.system()
    if system == "Windows":
        return "Malgun Gothic"
    else:
        return "NanumGothic"

def sanitize_dot(code: str) -> str:
    if isinstance(code, list):
        cleaned = []
        for line in code:
            if not isinstance(line, str):
                continue
            line = re.sub(r"```(?:json)?", "", line)
            line = re.sub(r"```", "", line)
            if line.strip():
                cleaned.append(line.strip())
        code = "\n".join(cleaned)

    elif isinstance(code, str):
        code = re.sub(r"```(?:json)?", "", code)
        code = re.sub(r"```", "", code).strip()
    else:
        code = ""

    if not code:
        return """digraph {
  rankdir=LR;
  node [shape=box, style=filled, fillcolor=lightgray, fontname="Arial"];
  input;
  cnn;
  output;
  input -> cnn -> output;
}"""

    # ✅ 안전 장치: digraph {} 가 없으면 강제로 감싸기
    if "digraph" not in code:
        code = "digraph {\n  rankdir=LR;\n" + code + "\n}"

    # ✅ 스타일 주입: fontname, shape, fillcolor 등
    if "node [" not in code:
        code = code.replace("digraph {", 
            'digraph {\n  rankdir=LR;\n  node [shape=box, style=filled, fillcolor=white, color=gray40, fontname="Arial"];'
        )

    return code




def render_bullet_diagram(section, out_path, width=1280, height=720, margin=60):
    img = PILImage.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(42)
    subtitle_font = load_font(26)
    body_font = load_font(24)

    title = section.get("slide_title", section.get("title", ""))
    slots = section.get("slots", {}) or {}

    # 제목 + 본문
    draw_title_bar(draw, width, title, title_font)
    content_y = draw_content_box(draw, width, height)

    # 상단 불릿
    points_data = slots.get("Points") or {}
    points_subtitle = (points_data.get("subtitle") or "").strip()
    points = normalize_slots(points_data.get("content", []))

    y = content_y + 20
    if points_subtitle:
        draw.rounded_rectangle(
            [margin, y, width - margin, y + 40],
            radius=8, fill=(230, 240, 255), outline=(100, 150, 255), width=2,
        )
        draw.text((margin + 20, y + 8), points_subtitle, font=subtitle_font, fill=(0, 60, 120))
        y += 50

    for line in points:
        for wrapped in wrap_text(draw, line, body_font, width - 2 * margin):
            draw.text((margin + 30, y), f"- {wrapped}", font=body_font, fill=COLORS["text"])
            y += body_font.size + 12

    # 하단 다이어그램
    diagram_data = slots.get("Diagram") or {}
    diagram_code_raw = diagram_data.get("content", "")
    diagram_subtitle = (diagram_data.get("subtitle") or "").strip()

    box_y0 = y + 20
    box_x0, box_x1 = margin, width - margin
    box_y1 = height - margin
    max_w = box_x1 - box_x0 - 20
    max_h = box_y1 - box_y0 - 20

    draw.rounded_rectangle(
        [box_x0, box_y0, box_x1, box_y1],
        radius=15, outline=COLORS["content_outline"], width=3, fill=COLORS["content_box"],
    )

    if diagram_subtitle:
        sub_rect = [box_x0 + 10, box_y0 + 10, box_x1 - 10, box_y0 + 50]
        draw.rounded_rectangle(sub_rect, radius=8, fill=(255, 230, 200), outline=(200, 150, 50), width=2)
        draw.text((box_x0 + 20, box_y0 + 18), diagram_subtitle, font=subtitle_font, fill=(100, 70, 0))
        box_y0 += 60

    def _render_dot(dot_code: str):
        safe_code = sanitize_dot(dot_code if dot_code else "")
        with tempfile.TemporaryDirectory() as tmpdir:
            dot_path = Path(tmpdir) / "diagram.dot"
            png_path = Path(tmpdir) / "diagram.png"
            dot_path.write_text(safe_code, encoding="utf-8")
            subprocess.run(["dot", "-Tpng", str(dot_path), "-o", str(png_path)], check=True)
            with PILImage.open(png_path) as diagram_img:
                diagram_img = diagram_img.copy()
            diagram_img.thumbnail((max_w, max_h))
            paste_x = box_x0 + (max_w - diagram_img.width) // 2
            paste_y = box_y0 + (max_h - diagram_img.height) // 2
            img.paste(diagram_img, (paste_x, paste_y))

    try:
        _render_dot(diagram_code_raw)
    except Exception:
        _render_dot("")

    img.save(out_path)
