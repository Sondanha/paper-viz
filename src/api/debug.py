from fastapi import APIRouter
import os

router = APIRouter(prefix="/api/debug", tags=["debug"])

@router.get("/env-check")
def env_check():
    """
    현재 컨테이너 환경변수 상태 확인 (보안상 키 값은 직접 노출하지 않음)
    """
    return {
        "ANTHROPIC_MODEL": os.environ.get("ANTHROPIC_MODEL"),
        "ANTHROPIC_API_KEY": "SET" if os.environ.get("ANTHROPIC_API_KEY") else "MISSING"
    }
