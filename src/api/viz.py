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

    # zip 파일은 /tmp/{arxiv_id}.zip 으로 고정
    zip_path = out_dir.parent / f"{arxiv_id}.zip"

    # shutil.make_archive는 확장자 없는 경로를 받아야 함
    shutil.make_archive(str(zip_path.with_suffix("")), "zip", out_dir)

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=f"{arxiv_id}.zip"
    )

