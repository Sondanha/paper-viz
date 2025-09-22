# src/renderer/base.py

import os
import platform
from PIL import ImageFont, ImageDraw

# 기본 폰트 후보 (OS별)
FONT_CANDIDATES = {
    "Windows": [
        "C:/Windows/Fonts/malgun.ttf",
        "arial.ttf",
    ],
    "Darwin": [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ],
    "Linux": [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
}

# 색상 팔레트 (노란색 계열)
COLORS = {
    "background": (255, 253, 240),     # 연노랑 배경
    "title_bar": (255, 204, 0),        # 진한 노랑 포인트
    "title_text": (0, 0, 0),           # 검정
    "content_box": (255, 255, 255),    # 흰 박스
    "content_outline": (230, 200, 50), # 연노랑 테두리
    "text": (0, 0, 0),                 # 기본 텍스트 = 검정
}

def load_font(size=24):
    """시스템별 폰트 로드"""
    system = platform.system()
    for path in FONT_CANDIDATES.get(system, []):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def normalize_slots(data):
    """
    슬롯 데이터를 리스트 형태로 정규화.
    - 문자열이면 줄 단위 분할
    - 리스트면 그대로 flatten
    - 단, "End-to-End" 같은 단어는 분리하지 않음
    """
    if isinstance(data, str):
        # 줄 단위 split
        lines = [line.strip() for line in data.split("\n") if line.strip()]
        # 불릿 처리: "- " 또는 "* " 로 시작하는 경우만 제거
        cleaned = []
        for line in lines:
            if line.startswith("- "):
                cleaned.append(line[2:].strip())
            elif line.startswith("* "):
                cleaned.append(line[2:].strip())
            else:
                cleaned.append(line)
        return cleaned

    elif isinstance(data, list):
        out = []
        for x in data:
            out.extend(normalize_slots(x))
        return out

    return []



def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int, line_spacing: int = 14):
    """텍스트 줄바꿈 처리
    - normalize_slots에서 1차 분리된 문자열이 들어옴
    - 여전히 폭 초과 시 줄바꿈
    """
    words = str(text).split()
    lines, line = [], ""

    for word in words:
        test_line = f"{line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            line = test_line
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)

    # 각 줄 반환 (줄간격은 draw 단계에서 활용)
    return lines



def draw_title_bar(draw, width, title, title_font, bar_height=80):
    """상단 타이틀 바 (노란색 계열)"""
    draw.rectangle([0, 0, width, bar_height], fill=COLORS["title_bar"])
    bbox = draw.textbbox((0, 0), title, font=title_font)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, 20), title, font=title_font, fill=COLORS["title_text"])


def draw_content_box(draw, width, height, bar_height=80, margin=40):
    """본문 영역 박스 (흰색 박스 + 연노랑 테두리)"""
    draw.rounded_rectangle(
        [margin, bar_height + 20, width - margin, height - margin],
        radius=20,
        fill=COLORS["content_box"],
        outline=COLORS["content_outline"],
        width=3
    )
    return bar_height + 40



