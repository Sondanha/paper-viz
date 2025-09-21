FROM python:3.11-slim

# 시스템 패키지 업데이트 + 필요한 툴/폰트 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    fonts-nanum \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리
WORKDIR /app

# requirements.txt 먼저 복사 → 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 실행 (FastAPI 예시)
CMD ["python", "src/main.py"]
