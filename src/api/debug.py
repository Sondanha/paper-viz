from fastapi import APIRouter
from src.config.settings import settings

router = APIRouter(prefix="/api/debug", tags=["debug"])

@router.get("/env-check")
def env_check():
    return {
        "CLAUDE_DEFAULT_MODEL": settings.claude_model,
        "ANTHROPIC_API_KEY": "SET" if settings.claude_api_key else "MISSING"
    }