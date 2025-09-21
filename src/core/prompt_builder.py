# src/core/prompt_builder.py

import json
import yaml
from pathlib import Path
from src.services.llm_client import call_claude

# section_mapping.yaml + layout_rules.yaml 로딩
def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

SECTION_MAPPING = load_yaml("configs/section_mapping.yaml")
LAYOUT_RULES = load_yaml("configs/layout_rules.yaml")["layouts"]

def build_prompt(section_title: str, section_text: str, mapping: dict):
    """
    섹션 텍스트 + 매핑 규칙 → LLM 프롬프트 생성
    """
    slots = mapping.get("slots", [])
    layout = mapping.get("layout", "bullet_layout")

    # layout_rules.yaml 안에서 해당 layout의 설명 + 예시 불러오기
    layout_def = LAYOUT_RULES.get(layout, {})
    description = layout_def.get("description", "")
    slot_defs = layout_def.get("slots", [])
    example = layout_def.get("example", "")

    # 슬롯 키만 추출
    slot_keys = [s["key"] for s in slot_defs]

    prompt = f"""
너는 학술 논문의 섹션을 발표용 슬라이드 형식으로 재구성하는 역할을 한다.
주어진 텍스트를 읽고, 아래 형식에 맞는 JSON을 출력하라.

## 지침
1. "layout" 키는 반드시 "{layout}"로 설정한다.
2. "slide_title" 키를 반드시 포함한다. → 해당 섹션을 대표하는 1줄 제목을 요약해 넣어라.
3. "slots"는 반드시 {slot_keys} 키를 포함해야 한다.
   - 각 key는 {description}에 맞는 내용을 담아라.
   - 내용은 발표용 자료처럼 간결하고 요약된 문장으로 작성하라.
   - 불필요하게 길게 쓰지 말고, 핵심만 담아라.
4. 반드시 JSON만 출력하라. 다른 텍스트는 출력하지 말라.

## 입력 섹션
제목: {section_title}
내용:
{section_text}

## 출력 예시
{example}
"""
    return prompt.strip()


def generate_section_content(section: dict, mapping: dict):
    """
    LLM 호출해서 slide_title + slots 채운 구조 생성
    """
    title = section.get("title", "")
    text = section.get("text", "")
    layout = mapping.get("layout", "bullet_layout")
    slots = mapping.get("slots", [])

    prompt = build_prompt(title, text, mapping)
    raw_response = call_claude(prompt)

    try:
        structured = json.loads(raw_response)
    except Exception:
        structured = {
            "layout": layout,
            "slide_title": title,
            "slots": {slot: "" for slot in slots},
        }

    return {
        "layout": structured.get("layout", layout),
        "slide_title": structured.get("slide_title", title),
        "slots": structured.get("slots", {slot: "" for slot in slots}),
        "raw_response": raw_response,
    }
