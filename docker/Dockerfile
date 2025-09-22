# docker/Dockerfile
FROM python:3.11-slim

# 시스템 패키지 업데이트 + Graphviz + 폰트 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    fontconfig \
    fonts-dejavu \
    fonts-liberation \
    fonts-nanum \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# requirements.txt 복사 후 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

# FastAPI 실행 (uvicorn)
EXPOSE 8010
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8010"]
