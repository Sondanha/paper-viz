# src/utils/font_loader.py
import os
import platform
from PIL import ImageFont

def load_korean_font(size=24):
    system = platform.system()

    if system == "Windows":
        font_path = "C:/Windows/Fonts/malgun.ttf"
    else:
        font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

    if not os.path.exists(font_path):
        raise FileNotFoundError(f"폰트 파일을 찾을 수 없음: {font_path}")

    return ImageFont.truetype(font_path, size)
