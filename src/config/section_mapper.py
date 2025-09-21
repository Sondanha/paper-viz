import re
import yaml 
from pathlib import Path


def load_section_mapping(path: str = "configs/section_mapping.yaml") -> dict:
    """YAML 매핑 룰 로드"""
    with open(Path(path), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def map_section(section_name: str, mapping: dict) -> dict:
    """
    섹션 이름 → 슬롯 & 레이아웃 매핑 반환
    1. exact match
    2. aliases 매칭
    3. substring/정규식 매칭
    4. default 반환
    """
    name = section_name.strip()

    # 1. exact match
    if name in mapping["sections"]:
        return mapping["sections"][name]

    # 2. alias 매칭
    for _, conf in mapping["sections"].items():
        aliases = conf.get("aliases", [])
        if name in aliases:
            return conf

    # 3. substring/정규식 매칭 (대소문자 무시)
    for key, conf in mapping["sections"].items():
        # 단어 포함 여부 확인
        if key.lower() in name.lower():
            return conf
        # 정규식 매칭 (옵션으로 확장 가능)
        regex = conf.get("regex")
        if regex and re.search(regex, name, flags=re.I):
            return conf

    # 4. fallback
    return mapping["default"]
