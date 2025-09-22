# src\api\main.py

from fastapi import FastAPI
from src.api import health, viz

app = FastAPI(
    title="Viz API",
    description="논문 PDF → 섹션별 슬라이드 PNG 변환 서비스",
    version="0.1.0",
)

# 라우트 등록
app.include_router(health.router)
app.include_router(viz.router)
