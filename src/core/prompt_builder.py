# src/core/prompt_builder.py

import json, re
import yaml
from pathlib import Path
from src.services.llm_client import call_claude

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


SECTION_MAPPING = load_yaml("configs/section_mapping.yaml")
LAYOUT_RULES = load_yaml("configs/layout_rules.yaml")["layouts"]

def normalize_slots_by_layout(layout, structured_slots):
    """레이아웃별 슬롯 키를 강제 보장"""
    clean_slots = {}

    # ✅ slots가 list로 들어올 때 dict로 보정
    if isinstance(structured_slots, list):
        fixed = {}
        for idx, slot in enumerate(structured_slots):
            if isinstance(slot, dict):
                key = slot.get("subtitle") or f"Slot{idx+1}"
                fixed[key] = slot
            else:
                fixed[f"Slot{idx+1}"] = {"subtitle": f"Slot{idx+1}", "content": [str(slot)]}
        structured_slots = fixed

    if layout == "flow_horizontal":
        clean_slots["Problem"] = structured_slots.get("Problem") or {
            "subtitle": "문제", "content": []
        }
        clean_slots["Approach"] = structured_slots.get("Approach") or {
            "subtitle": "접근", "content": []
        }
        clean_slots["Result"] = structured_slots.get("Result") or {
            "subtitle": "성과", "content": []
        }

    elif layout == "split_layout":
        clean_slots["Left"] = structured_slots.get("Left") or {
            "subtitle": "왼쪽", "content": []
        }
        clean_slots["Right"] = structured_slots.get("Right") or {
            "subtitle": "오른쪽", "content": []
        }

    elif layout == "bullet_diagram":
        clean_slots["Points"] = structured_slots.get("Points") or {
            "subtitle": "핵심", "content": []
        }
        clean_slots["Diagram"] = structured_slots.get("Diagram") or {
            "subtitle": "구조", "content": []
        }

    elif layout == "table_layout":
        clean_slots["Comparison"] = structured_slots.get("Comparison") or {
            "subtitle": "비교", "content": []
        }

    elif layout == "warning_bullet":
        clean_slots["Limitation"] = structured_slots.get("Limitation") or {
            "subtitle": "한계", "content": []
        }
        clean_slots["Insight"] = structured_slots.get("Insight") or {
            "subtitle": "통찰", "content": []
        }

    elif layout == "composite_layout":
        clean_slots["Contribution"] = structured_slots.get("Contribution") or {
            "subtitle": "기여", "content": []
        }
        clean_slots["Limitation"] = structured_slots.get("Limitation") or {
            "subtitle": "한계", "content": []
        }
        clean_slots["FutureWork"] = structured_slots.get("FutureWork") or {
            "subtitle": "연구", "content": []
        }

    elif layout == "timeline":
        clean_slots["FutureWork"] = structured_slots.get("FutureWork") or {
            "subtitle": "단계", "content": []
        }
    elif layout == "bullet_diagram":
        if isinstance(structured_slots, list):
            # LLM이 잘못 list를 뱉으면 → 전부 Points로 몰아넣고 Diagram은 빈 값
            points_content = []
            for slot in structured_slots:
                if isinstance(slot, dict):
                    points_content.extend(slot.get("content", []))
                elif isinstance(slot, str):
                    points_content.append(slot)
            clean_slots["Points"] = {"subtitle": "핵심", "content": points_content}
            clean_slots["Diagram"] = {"subtitle": "구조", "content": []}
        else:
            clean_slots["Points"] = structured_slots.get("Points") or {"subtitle": "핵심", "content": []}
            clean_slots["Diagram"] = structured_slots.get("Diagram") or {"subtitle": "구조", "content": []}
    else:
        # ✅ dict 보장
        clean_slots = structured_slots if isinstance(structured_slots, dict) else {}

    return clean_slots

def build_prompt(section_title: str, section_text: str, mapping: dict):
    slots = mapping.get("slots", [])
    layout = mapping.get("layout", "bullet_layout")

    layout_def = LAYOUT_RULES.get(layout, {})
    slot_defs = layout_def.get("slots", [])
    example = layout_def.get("example", "")

    # 슬롯 상세 설명 구성
    slot_instructions = []
    for s in slot_defs:
        key = s["key"]
        subtitle = s.get("subtitle", "")
        stype = s.get("type", "text")

        if stype == "diagram":
            slot_instructions.append(
                f'- "{key}" 키: 반드시 객체로 작성. '
                f'{{"subtitle": "{subtitle or "구조"}", "content": ["Graphviz DOT 코드 줄 단위 배열"]}} 형태. '
                f'⚠ 반드시 digraph 문법 사용 (digraph {{ ... }}). '
                f'⚠ 노드 이름은 영문 단어만 (예: Input, CNN, Head, BBox, NMS, Output). 한글 금지. '
                f'⚠ label 속성 사용 금지, 노드 이름 자체로 의미 표현. '
                f'⚠ 단순 직선 체인(예: Input -> A -> B -> Output) 금지. '
                f'⚠ 반드시 병렬 분기(branch), 여러 입력의 병합(merge), 또는 루프(loop) 중 하나 이상을 포함할 것. '
                f'⚠ 최소 5개 이상의 노드 사용. '
                f'⚠ 섹션 텍스트의 실제 개념/구성 요소를 반영하여 흐름도를 설계할 것. '
            )

        elif layout in ["split_layout", "composite_layout"]:
            slot_instructions.append(
                f'- "{key}" 키: 반드시 객체로 작성. '
                f'{{"subtitle": "{subtitle or "주제"}", "content": ["짧고 간결한 문장 여러 개 (최소 4~5개 이상)"]}} 형태. '
                f'⚠ 각 문장은 섹션 텍스트의 서로 다른 핵심 포인트를 반드시 반영할 것. '
                f'⚠ 단순 반복이나 추상적 표현(예: "중요하다", "필요하다")는 금지. '
                f'⚠ 실제 기여, 한계, 향후 연구 방향을 논리적으로 기술.'
            )

        elif stype == "table":
            slot_instructions.append(
                f'- "{key}" 키: 반드시 객체로 작성하고 '
                f'{{{{"subtitle": "{subtitle or "표"}", "content": [["헤더1","헤더2"],["값1","값2"]]}}}} 형태로 출력.'
            )
        elif stype == "timeline":
            slot_instructions.append(
                f'- "{key}" 키: 반드시 객체로 작성하고 '
                f'{{{{"subtitle": "{subtitle or "단계"}", "content": ["단계1","단계2"]}}}} 형태로 출력.'
            )
        else:
            slot_instructions.append(
                f'- "{key}" 키: 반드시 객체로 작성하고 '
                f'{{{{"subtitle": "{subtitle or "주제"}", "content": ["간결한 불릿 문장들"]}}}} 형태로 출력.'
            )

    # ⚠ bullet_diagram 전용 강제 스키마 추가
    extra_schema_hint = ""
    if layout == "bullet_diagram":
        extra_schema_hint = """
⚠ "slots"는 반드시 객체(dict) 형식이어야 한다.
⚠ 반드시 "Points"와 "Diagram" 두 개의 키만 포함해야 한다.
⚠ 절대 배열(list)로 작성하지 말라.

예시 스키마:
{
  "layout": "bullet_diagram",
  "slide_title": "슬라이드 제목",
  "slots": {
    "Points": {"subtitle": "핵심", "content": ["포인트1", "포인트2"]},
    "Diagram": {"subtitle": "구조", "content": ["digraph { Input -> CNN -> Output; }"]}
  }
}
"""

    prompt = f"""
너는 학술 논문의 섹션을 발표용 슬라이드 형식으로 재구성하는 역할을 한다.
주어진 텍스트를 읽고, 아래 형식에 맞는 JSON을 출력하라.

## 지침
1. "layout" 키는 반드시 "{layout}"로 설정한다.
2. "slide_title" 키는 반드시 포함한다.
   - 섹션 제목을 그대로 사용하지 말 것.
   - 섹션의 핵심 내용을 반영하여 한국어로 짧은 한 문장으로 요약할 것.
   - 영어 병기는 하지 말 것 (슬라이드 제목은 한국어만).
3. "slots"는 반드시 다음 키를 포함해야 하며, 각 키 값은 {{"subtitle": "...", "content": [...]}} 구조여야 한다:
{chr(10).join(slot_instructions)}

{extra_schema_hint}

4. 모든 텍스트는 한국어로 작성하되, content 안의 주요 기술 용어(모델명, 알고리즘명 등)는 반드시 한국어+영문 병기로 표기할 것.
   예: "합성곱 신경망 (CNN)", "You Only Look Once (YOLO)"
5. 반드시 JSON만 출력하라. 다른 텍스트나 설명, 코드 블록(````json`, `````)은 절대 포함하지 말라.

## 입력 섹션
제목: {section_title}
내용:
{section_text}

## 출력 예시
{example}
"""
    return prompt.strip()



def clean_diagram_content(content):
    if not content:
        return []

    if isinstance(content, str):
        # 백틱 코드블록 제거
        text = re.sub(r"^```(?:json)?", "", content.strip(), flags=re.MULTILINE)
        text = re.sub(r"```$", "", text.strip(), flags=re.MULTILINE)

        # 혹시 문자열이 JSON 통째로 들어온 경우 → 다시 파싱해서 content만 추출
        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and "content" in obj:
                return obj["content"]
        except Exception:
            pass

        # 그냥 DOT 코드라면 줄 단위 배열로 반환
        return [line for line in text.splitlines() if line.strip()]

    if isinstance(content, list):
        new_lines = []
        for line in content:
            if not isinstance(line, str):
                continue
            line = re.sub(r"^```(?:json)?", "", line)
            line = re.sub(r"```", "", line)
            if line.strip():
                new_lines.append(line)
        return new_lines

    return []


def generate_section_content(section: dict, mapping: dict):
    title = section.get("title", "")
    text = section.get("text", "")
    layout = mapping.get("layout", "bullet_layout")

    prompt = build_prompt(title, text, mapping)
    raw_response = call_claude(prompt)

    # ✅ 백틱 제거
    cleaned_response = re.sub(r"^```(?:json)?", "", raw_response.strip(), flags=re.MULTILINE)
    cleaned_response = re.sub(r"```$", "", cleaned_response.strip(), flags=re.MULTILINE)

    debug_dir = Path("tests/output/_debug")
    debug_dir.mkdir(parents=True, exist_ok=True)
    sec_title = title.replace(" ", "_")

    (debug_dir / f"{sec_title}_raw.json").write_text(raw_response, encoding="utf-8")
    (debug_dir / f"{sec_title}_cleaned.json").write_text(cleaned_response, encoding="utf-8")

    try:
        structured = json.loads(cleaned_response)
    except Exception as e:
        (debug_dir / f"{sec_title}_parse_error.txt").write_text(
            f"{type(e).__name__}: {e}\n--- cleaned_response ---\n{cleaned_response}",
            encoding="utf-8"
        )
        structured = {
            "layout": layout,
            "slide_title": title,
            "slots": {},
        }

    (debug_dir / f"{sec_title}_parsed.json").write_text(
        json.dumps(structured, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    structured_slots = structured.get("slots", {})
    clean_slots = normalize_slots_by_layout(layout, structured_slots)

    for k, v in clean_slots.items():
        if isinstance(v, dict) and "content" in v and k.lower() == "diagram":
            v["content"] = clean_diagram_content(v.get("content", []))

    return {
        "layout": structured.get("layout", layout),
        "slide_title": structured.get("slide_title", title),
        "slots": clean_slots,
        "raw_response": raw_response,
    }


