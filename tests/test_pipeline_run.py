# tests/test_pipeline_run.py
import json
import subprocess
from pathlib import Path

from src.core.pipeline import run_pipeline
from src.core.prompt_builder import normalize_slots_by_layout, clean_diagram_content
from src.renderer.bullet_diagram import sanitize_dot


def _safe_name(s: str) -> str:
    return s.replace(" ", "_")


def _validate_dot(dot_lines, artifacts_dir: Path, label: str):
    # 문자열이면 강제로 줄배열로
    if isinstance(dot_lines, str):
        dot_text = dot_lines
        lines = [ln for ln in dot_text.splitlines() if ln.strip()]
    else:
        lines = [ln for ln in dot_lines if isinstance(ln, str)]
        dot_text = "\n".join(lines)

    # 1차 검증: 백틱과 코드블록 흔적
    assert "```" not in dot_text, f"[{label}] 백틱이 아직 살아있다.\n앞부분: {dot_text[:200]}"

    # 2차 검증: 최소 문법
    assert "digraph" in dot_text, f"[{label}] 'digraph' 없음. DOT 아님.\n앞부분: {dot_text[:200]}"

    # 아티팩트 기록
    raw_dot = artifacts_dir / f"{label}_raw.dot"
    raw_dot.write_text(dot_text, encoding="utf-8")

    # sanitize 전/후를 모두 Graphviz로 컴파일해본다.
    sanitized_text = sanitize_dot(dot_text)
    san_dot = artifacts_dir / f"{label}_sanitized.dot"
    san_dot.write_text(sanitized_text, encoding="utf-8")

    for kind, path in [("raw", raw_dot), ("sanitized", san_dot)]:
        png = artifacts_dir / f"{label}_{kind}.png"
        try:
            subprocess.run(
                ["dot", "-Tpng", str(path), "-o", str(png)],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or b"").decode("utf-8", "ignore")
            dot_preview = path.read_text(encoding="utf-8")
            raise AssertionError(
                f"[{label}] Graphviz 실패 ({kind}).\n"
                f"---- DOT ----\n{dot_preview}\n"
                f"---- STDERR ----\n{stderr}"
            )


def test_pipeline_run_diagnostic(tmp_path):
    arxiv_id = "1506.02640"
    out_dir = Path("tests/output")

    # 파이프라인 실행
    result = run_pipeline(arxiv_id, out_dir=out_dir)

    # 기본 검증
    assert result.get("pdf_size", 0) > 0
    assert len(result.get("sections", [])) > 0

    # 섹션 단위 아티팩트 폴더
    diag_root = Path(result["output_dir"]) / "_diag"
    diag_root.mkdir(parents=True, exist_ok=True)

    for sec in result["sections"]:
        order = sec["order"]
        title = sec["title"]
        sec_key = f"{order}_{_safe_name(title)}"
        sec_dir = diag_root / sec_key
        sec_dir.mkdir(parents=True, exist_ok=True)

        # prompt_builder가 저장한 파싱 전/후 파일 로드
        # 주의: prompt_builder는 tests/output/_debug/{제목_밑줄}_parsed.json로 저장함
        debug_dir = Path("tests/output/_debug")
        parsed_path = debug_dir / f"{_safe_name(title)}_parsed.json"
        raw_path = debug_dir / f"{_safe_name(title)}_raw.json"

        # 없으면 스킵하되, 뭘 놓쳤는지 남긴다
        if not parsed_path.exists():
            (sec_dir / "WARN_NO_PARSED_TXT.txt").write_text(
                "parsed.json이 없음. prompt_builder 단계에서 저장이 안 됨.", encoding="utf-8"
            )
            continue

        structured = json.loads(parsed_path.read_text(encoding="utf-8"))
        (sec_dir / "10_structured_from_parsed.json").write_text(
            json.dumps(structured, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        if raw_path.exists():
            (sec_dir / "00_raw_llm_response.json").write_text(
                raw_path.read_text(encoding="utf-8"), encoding="utf-8"
            )

        layout = structured.get("layout", "bullet_layout")
        slots = structured.get("slots", {}) or {}

        # 레이아웃 정규화
        normalized = normalize_slots_by_layout(layout, slots)
        (sec_dir / "20_normalized_slots.json").write_text(
            json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # Diagram 슬롯이 없으면 스킵
        diagram = normalized.get("Diagram")
        if not isinstance(diagram, dict):
            (sec_dir / "SKIP_NO_DIAGRAM.txt").write_text("Diagram 슬롯 없음", encoding="utf-8")
            continue

        before = diagram.get("content", [])
        (sec_dir / "30_diagram_content_before.json").write_text(
            json.dumps(before, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # 백틱/코드블록/중첩 JSON 제거
        after = clean_diagram_content(before)
        (sec_dir / "40_diagram_content_after.json").write_text(
            json.dumps(after, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # 실제 DOT 유효성 검증 + Graphviz 렌더 테스트
        if after:
            _validate_dot(after, sec_dir, "diagram")

    # 파이프라인 자체는 끝까지 돌았는지만 본다
    assert True
