# src/core/fetch_arxiv.py
import io
import tarfile
import requests
import re

ARXIV_PDF_URL = "https://arxiv.org/pdf/{id}.pdf"
ARXIV_EPRINT_URL = "https://arxiv.org/e-print/{id}"


def fetch_pdf(arxiv_id: str) -> bytes:
    """PDF bytes 다운로드."""
    url = ARXIV_PDF_URL.format(id=arxiv_id)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content


def fetch_eprint_tex(arxiv_id: str) -> dict[str, str]:
    """
    e-print tar 아카이브에서 .tex만 dict로 반환.
    key: 파일명, value: 텍스트
    """
    url = ARXIV_EPRINT_URL.format(id=arxiv_id)
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    tex_files: dict[str, str] = {}
    with tarfile.open(fileobj=io.BytesIO(resp.content), mode="r:*") as tar:
        for member in tar.getmembers():
            if not member.isfile() or not member.name.endswith(".tex"):
                continue
            f = tar.extractfile(member)
            if f is None:
                continue
            raw = f.read()
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("latin-1", errors="ignore")
            tex_files[member.name] = text
    return tex_files


def merge_tex_files(tex_files: dict[str, str]) -> str:
    """
    여러 tex 파일일 경우 논문 전개 순서에 맞춰 합침.
    - main 후보(ms.tex, main.tex, paper.tex)가 있으면 먼저
    - 나머지는 알파벳순
    - 하나면 그대로 반환
    """
    if not tex_files:
        return ""

    if len(tex_files) == 1:
        return next(iter(tex_files.values()))

    main_candidates = ["ms.tex", "main.tex", "paper.tex"]
    ordered = []
    seen = set()

    # 메인 후보 먼저
    for candidate in main_candidates:
        if candidate in tex_files:
            ordered.append(tex_files[candidate])
            seen.add(candidate)
            break

    # 나머지 알파벳순
    for fname in sorted(tex_files.keys()):
        if fname not in seen:
            ordered.append(tex_files[fname])

    return "\n\n".join(ordered)


def fetch_all(arxiv_id: str) -> tuple[bytes, str]:
    """
    PDF bytes와 하나로 합쳐진 TEX 문자열 반환.
    """
    pdf_bytes = fetch_pdf(arxiv_id)
    tex_files = fetch_eprint_tex(arxiv_id)
    merged_tex = merge_tex_files(tex_files)
    return pdf_bytes, merged_tex, tex_files
