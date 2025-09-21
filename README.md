```bash
project-root/
│
├─ 📂src/
│  ├─ 📂api/                # FastAPI 라우터
│  │  ├─ arxiv.py           # 논문번호 입력 → fetch + preprocess
│  │  ├─ visualize.py       # 섹션 → 시각화 이미지 반환
│  │  └─ health.py          # /healthz
│  │
│  ├─ 📂services/
│  │  ├─ fetch_arxiv.py      # ✅
│  │  ├─ preprocess.py       # ✅
│  │  ├─ orchestrator.py     # 전체 워크플로 관리 (1~7 단계 실행)
│  │  ├─ postprocess.py      # LLM dot 코드 후처리
│  │  ├─ graphviz_service.py # Graphviz 호출, BytesIO로 이미지 반환
│  │  └─ cache.py            # dict 기반 인메모리 캐시
│  │
│  ├─ 📂clients/
│  │  └─ llm_client.py      # Claude API 호출 래퍼
│  │
│  ├─ main.py               # FastAPI 진입점
│  └─ config.py             # 환경변수 로딩 (API 키 등)
│
├─ 📂tests/                  # pytest 유닛 테스트
│  ├─ test_preprocess.py
│  ├─ test_orchestrator.py
│  └─ test_graphviz.py
│
├─ 📂docker/
│  ├─ Dockerfile
│  └─ requirements.txt
│
├─ .env.example              # CLAUDE_API_KEY=...
├─ .gitignore
└─ README.md

```
