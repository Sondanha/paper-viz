from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
from pathlib import Path

from src.core.pipeline import run_pipeline

router = APIRouter(prefix="/api/viz-api", tags=["viz"])


@router.post("/generate/{arxiv_id}")
def generate(arxiv_id: str):
    """
    arXiv ID를 받아서 파이프라인 실행 → 섹션별 PNG 생성
    캐시가 있으면 기존 파일 재사용
    """
    result = run_pipeline(arxiv_id, out_dir="/tmp")

    sections = [
        {
            "order": s.get("order"),
            "title": s.get("title"),
            "layout": s.get("layout"),
            "slide_title": s.get("slide_title"),
            "preview": s["image_base64"],  # 프론트에서 즉시 미리보기
            "download_url": f"/api/viz-api/download/{arxiv_id}/{Path(s['file']).name}"
        }
        for s in result["sections"]
    ]

    return {
        "arxiv_id": arxiv_id,
        "pdf_size": result.get("pdf_size"),
        "sections": sections,
    }


@router.get("/download/{arxiv_id}/{filename}")
def download(arxiv_id: str, filename: str, background: BackgroundTasks):
    """
    생성된 PNG 다운로드 (다운로드 후 파일 삭제)
    """
    path = Path(f"/tmp/{arxiv_id}") / filename
    if not path.exists():
        return {"error": "File not found"}

    def cleanup(file_path: Path):
        try:
            file_path.unlink()
            # 폴더 비었으면 폴더도 삭제
            if not any(file_path.parent.iterdir()):
                file_path.parent.rmdir()
        except Exception as e:
            print(f"Cleanup failed: {e}")

    background.add_task(cleanup, path)

    return FileResponse(path, media_type="image/png", filename=filename)
