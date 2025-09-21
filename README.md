# paper-viz

논문 PDF에서 섹션을 뽑아 **LLM으로 슬라이드 콘텐츠(JSON)** 를 생성하고, **Renderer(Pillow/Graphviz)** 로 발표용 PNG를 만든다.
최종 산출물은 섹션 단위의 가로형 슬라이드 이미지 묶음.

## 기능 개요

- **전처리**: arXiv에서 PDF/TEX 가져와 섹션 텍스트 추출
- **매핑**: `configs/section_mapping.yaml`에 따라 섹션→슬롯/레이아웃 결정
- **LLM**: `configs/layout_rules.yaml` 가이드에 맞춰 `slide_title` + `slots` JSON 생성
- **렌더링**: 레이아웃별 템플릿으로 발표 스타일 PNG 렌더
- **결과**: `tests/output/{arxiv_id}/{order}_{section}.png`

## 디렉터리

```bash
src/
  core/
    pipeline.py         # 파이프라인 진입점
    preprocess.py       # 섹션 추출/정리
    fetch_arxiv.py      # arXiv 다운로드
    prompt_builder.py   # LLM 프롬프트/파싱
  renderer/
    base.py             # 폰트/색/공통 드로잉 유틸
    templates.py        # layout → renderer 매핑
    bullet.py           # bullet_layout (세로 step)
    flow_horizontal.py  # flow_horizontal (좌→우 흐름)
    split.py            # split_layout (좌/우 비교)
    table.py            # table_layout (비교 테이블)
    composite.py        # composite_layout (병렬 블록)
    warning_bullet.py   # warning_bullet (제한/주의)
    timeline.py         # timeline (가로 타임라인)
  services/
    llm_client.py       # Anthropic(Claude) 호출
  config/
    settings.py         # .env 로딩(Pydantic Settings)
    section_mapper.py   # 섹션명→매핑 로직
  api/
    main.py             # FastAPI 엔드포인트
    viz.py              # 파이프라인 호출 래퍼
configs/
  section_mapping.yaml  # 섹션명→{slots, layout}
  layout_rules.yaml     # 레이아웃 지침/예시(JSON)
tests/
  test_pipeline_run.py  # 통합 실행 테스트
```

## 설치

```bash
# 가상환경 권장
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

## 환경 변수(.env)

```env
ANTHROPIC_API_KEY=sk-...
CLAUDE_DEFAULT_MODEL=claude-3-haiku-20240307
CLAUDE_MAX_TOKENS=4096
CLAUDE_TEMPERATURE=0.2
```

> Pydantic Settings가 위 키들을 읽어서 `settings.py`로 주입한다.

## 실행 예시(파이프라인 단독)

```bash
python -c "from src.core.pipeline import run_pipeline; print(run_pipeline('1506.02640')['output_dir'])"
# 출력: tests/output/1506.02640
```

## 테스트

```bash
pytest -s tests/test_pipeline_run.py
```

## API

개발 서버:

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

엔드포인트(예시):

- `GET /health` → 헬스체크
- `POST /api/v1/generate` → `{ "arxiv_id": "1506.02640" }` 를 받아 PNG들을 생성하고 경로/메타를 반환
  실제 서비스 라우팅이 `/api/viz-api/generate` 로 붙는 환경에서는 게이트웨이/리버스 프록시에서 경로 매핑.

## LLM 출력 스키마(예)

LLM은 반드시 아래 형태(JSON only)로 응답한다.

```json
{
  "layout": "bullet_layout",
  "slide_title": "YOLO의 핵심 아이디어",
  "slots": {
    "Step1": "작은 객체 탐지에 취약",
    "Step2": "End-to-End 구조로 학습",
    "Step3": "하나의 CNN으로 동시 예측"
  }
}
```

레이아웃별 요구 슬롯/시각화 지침은 `configs/layout_rules.yaml` 참고.

## 시각화 가이드(요약)

- 공통: 상단 타이틀 바, 밝은 배경(연노랑), 내용 박스(흰색+연노랑 테두리)
- `bullet_layout`: 세로 step, 각 박스 상단 라벨, 박스 사이 ↓ 화살표
- `flow_horizontal`: 좌→우 박스+→ 화살표
- `split_layout`: 좌/우 비교 박스(색상 대비)
- `table_layout`: 행렬 테이블(헤더 강조)
- `composite_layout`: 3개 병렬 블록
- `warning_bullet`: 경고 테마(연분홍, 아이콘)
- `timeline`: 가로선+노드+단계 레이블

## 트러블슈팅

- **폰트 깨짐**: OS별 기본 폰트 경로는 `renderer/base.py`의 `FONT_CANDIDATES`에서 우선 탐색. 없으면 시스템 기본 폰트로 폴백.
- **레이아웃 키 에러**: `renderer/templates.py`의 `LAYOUT_RENDERERS` 에 alias(`composite` vs `composite_layout`)가 등록되어 있어야 함.
- **LLM이 예시만 반환**: `prompt_builder.py`가 예시는 참고용이며 실제 내용으로 채우라고 강제. 그래도 실패하면 Fallback으로 빈 슬롯과 섹션 제목 사용.

---
