# tests/run_pipeline.py
import json
from pathlib import Path
from src.core.pipeline import run_pipeline

OUTPUT_DIR = Path("tests/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    print("🚀 Running pipeline for YOLO")
    out1 = run_pipeline("1506.02640")  # YOLO
    out1_path = OUTPUT_DIR / "yolo.json"
    with open(out1_path, "w", encoding="utf-8") as f:
        json.dump(out1, f, indent=2, ensure_ascii=False)
    print(f"✅ YOLO 결과 저장됨: {out1_path}")

    print("🚀 Running pipeline for Transformer")
    out2 = run_pipeline("1706.03762")  # Transformer
    out2_path = OUTPUT_DIR / "transformer.json"
    with open(out2_path, "w", encoding="utf-8") as f:
        json.dump(out2, f, indent=2, ensure_ascii=False)
    print(f"✅ Transformer 결과 저장됨: {out2_path}")
