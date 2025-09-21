# src/core/pipeline.py

from pathlib import Path
import re

from src.core import fetch_arxiv, preprocess, prompt_builder
from src.config.section_mapper import load_section_mapping, map_section
from src.renderer.templates import render_section


def sanitize_filename(name: str) -> str:
    """파일명에 쓸 수 없는 문자 제거"""
    return re.sub(r'[^0-9a-zA-Z가-힣_]+', '_', name).strip("_")


def run_pipeline(arxiv_id: str, out_dir="tests/output"):
    # 1. PDF, TEX 가져오기
    pdf_bytes = fetch_arxiv.fetch_pdf(arxiv_id)
    tex_files = fetch_arxiv.fetch_eprint_tex(arxiv_id)  # 여러 .tex 그대로 dict

    # 2. 섹션별 전처리
    sections = preprocess.preprocess_tex_files(tex_files)

    # 3. 섹션 매핑 룰 불러오기
    mapping_rules = load_section_mapping()

    # 4. 섹션별 처리
    results = []
    paper_dir = Path(out_dir) / arxiv_id
    paper_dir.mkdir(parents=True, exist_ok=True)

    for sec in sections:
        # (a) 섹션 매핑 룰 적용 (section_mapping.yaml 기반)
        mapped = map_section(sec["title"], mapping_rules)
        sec_info = {
            "order": sec["order"],
            "title": sec["title"],
            "text": sec["text"],
            "layout": mapped["layout"],
            "slots": mapped["slots"],  # 초기 슬롯 구조 (LLM 참고용)
        }

        # (b) LLM 호출 → 구조화 JSON
        structured = prompt_builder.generate_section_content(sec_info, mapped)

        # (c) 파일명: 번호_섹션명.png
        safe_title = sanitize_filename(sec["title"])
        filename = f"{sec['order']}_{safe_title}.png"
        out_path = paper_dir / filename

        # (d) 렌더링
        render_section(structured, out_path)

        results.append({
            "order": sec["order"],
            "title": sec["title"],
            "layout": structured.get("layout"),
            "slide_title": structured.get("slide_title"),
            "file": str(out_path),
            "raw_response": structured.get("raw_response", ""),
        })

    return {
        "pdf_size": len(pdf_bytes),
        "sections": results,
        "output_dir": str(paper_dir)
    }
