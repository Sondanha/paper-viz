from src.core.pipeline import run_pipeline


def test_pipeline_run():
    arxiv_id = "1506.02640"
    out_dir = "tests/output"

    # 파이프라인 실행
    result = run_pipeline(arxiv_id, out_dir=out_dir)

    # 기본 결과 검증
    assert "pdf_size" in result
    assert result["pdf_size"] > 0
    assert "sections" in result
    assert len(result["sections"]) > 0

    print(f"\n📄 PDF size: {result['pdf_size']} bytes")
    print(f"📂 Output dir: {result['output_dir']}")

    for sec in result["sections"]:
        print(f"\n--- Section {sec['order']} ---")
        print(f"Title       : {sec['title']}")
        print(f"Slide Title : {sec.get('slide_title')}")
        print(f"Layout      : {sec['layout']}")
        print(f"File        : {sec['file']}")

        raw = sec.get("raw_response", "")
        if raw:
            # raw_response가 너무 길면 앞부분만 보여주기
            print(f"Raw Response (preview): {raw[:200]}...")
