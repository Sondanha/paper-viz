# src/api/viz.py

from fastapi import APIRouter
from pathlib import Path

from src.core.pipeline import run_pipeline

router = APIRouter(prefix="/api/viz-api", tags=["viz"])

@router.post("/generate/{arxiv_id}")
def generate(arxiv_id: str):
    """
    arXiv ID를 받아서 파이프라인 실행 → 섹션별 PNG 생성
    """
    result = run_pipeline(arxiv_id, out_dir="tests/output")

    sections = [
        {
            "order": s["order"],
            "title": s["title"],
            "layout": s["layout"],
            "file": Path(s["file"]).as_posix()
        }
        for s in result["sections"]
    ]

    return {
        "arxiv_id": arxiv_id,
        "pdf_size": result["pdf_size"],
        "output_dir": result["output_dir"],
        "sections": sections,
    }
