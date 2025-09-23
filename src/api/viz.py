# src/api/viz.py

import shutil
from fastapi.responses import FileResponse
from fastapi import APIRouter
from pathlib import Path
from src.core.pipeline import run_pipeline

router = APIRouter(prefix="/api/viz-api", tags=["viz"])

@router.post("/generate-zip/{arxiv_id}")
def generate_zip(arxiv_id: str):
    """
    arXiv ID 받아서 PNG 전부 생성 → ZIP으로 묶어서 반환
    """
    result = run_pipeline(arxiv_id, out_dir="/tmp")
    out_dir = Path(result["output_dir"])
    zip_path = out_dir.with_suffix(".zip")

    # zip 파일 생성
    shutil.make_archive(out_dir, "zip", out_dir)

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=f"{arxiv_id}.zip"
    )
