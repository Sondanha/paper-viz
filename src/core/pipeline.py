# src/core/pipeline.py

from pathlib import Path
import re
import base64

from src.core import fetch_arxiv, preprocess, prompt_builder
from src.config.section_mapper import load_section_mapping, map_section
from src.renderer.templates import render_section
from src.config.settings import settings   


def sanitize_filename(name: str) -> str:
    """파일명에 쓸 수 없는 문자 제거"""
    return re.sub(r'[^0-9a-zA-Z가-힣_]+', '_', name).strip("_")


def run_pipeline(arxiv_id: str, out_dir: str | None = None):
    # ✅ 환경변수에서 기본 출력 경로 가져오기
    base_dir = Path(out_dir or settings.debug_dir)
    paper_dir = base_dir / arxiv_id

    # 이미 생성된 캐시 있으면 그대로 재사용
    if paper_dir.exists():
        results = []
        for file in sorted(paper_dir.glob("*.png")):
            with open(file, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            order = int(file.stem.split("_")[0]) if "_" in file.stem else -1
            results.append({
                "order": order,
                "title": file.stem,
                "file": str(file),
                "image_base64": encoded,
            })
        return {"pdf_size": None, "sections": results, "output_dir": str(paper_dir)}

    # 1. PDF, TEX 가져오기
    pdf_bytes = fetch_arxiv.fetch_pdf(arxiv_id)
    tex_files = fetch_arxiv.fetch_eprint_tex(arxiv_id)

    # 2. 섹션별 전처리
    sections = preprocess.preprocess_tex_files(tex_files)

    # 3. 섹션 매핑 룰 불러오기
    mapping_rules = load_section_mapping()

    # 4. 출력 디렉토리 생성
    paper_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for sec in sections:
        mapped = map_section(sec["title"], mapping_rules)
        sec_info = {
            "order": sec["order"],
            "title": sec["title"],
            "text": sec["text"],
            "layout": mapped["layout"],
            "slots": mapped["slots"],
        }

        structured = prompt_builder.generate_section_content(sec_info, mapped)

        safe_title = sanitize_filename(sec["title"])
        filename = f"{sec['order']}_{safe_title}.png"
        out_path = paper_dir / filename

        render_section(structured, out_path)

        with open(out_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")

        results.append({
            "order": sec["order"],
            "title": sec["title"],
            "layout": structured.get("layout"),
            "slide_title": structured.get("slide_title"),
            "file": str(out_path),
            "image_base64": encoded,
            "raw_response": structured.get("raw_response", ""),
        })

    return {
        "pdf_size": len(pdf_bytes),
        "sections": results,
        "output_dir": str(paper_dir)
    }
