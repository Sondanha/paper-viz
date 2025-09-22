# src\core\preprocess.py

import re
from pathlib import Path

def clean_tex_single(text: str) -> str:
    """단일 tex: 기존 로직"""
    text = re.sub(r"%.*", "", text)
    text = re.sub(r"\\begin{figure}.*?\\end{figure}", " [FIGURE] ", text, flags=re.S)
    text = re.sub(r"\\begin{table}.*?\\end{table}", " [TABLE] ", text, flags=re.S)
    text = re.sub(r"\\begin{equation}.*?\\end{equation}", " [EQUATION] ", text, flags=re.S)
    text = re.sub(r"\\\[.*?\\\]", " [EQUATION] ", text, flags=re.S)
    text = re.sub(r"\$.*?\$", " [EQUATION] ", text)
    text = re.sub(r"\\cite\{[^}]*\}", "", text)
    text = re.sub(r"\\ref\{[^}]*\}", "", text)
    text = re.sub(r"\\label\{[^}]*\}", "", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:{[^}]*})?", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_tex_multi(text: str) -> str:
    """여러 tex: citation/eq 살려두는 개선 로직"""
    text = re.sub(r"%.*", "", text)
    text = re.sub(r"\\begin{figure}.*?\\end{figure}", " [FIGURE] ", text, flags=re.S)
    text = re.sub(r"\\begin{table}.*?\\end{table}", " [TABLE] ", text, flags=re.S)
    text = re.sub(r"\\begin{equation}.*?\\end{equation}", " [EQUATION_BLOCK] ", text, flags=re.S)
    text = re.sub(r"\\\[.*?\\\]", " [EQUATION_BLOCK] ", text, flags=re.S)

    # citation → placeholder
    text = re.sub(r"\\cite[p|t]?\{[^}]*\}", " [CITATION] ", text)

    # inline eq
    def inline_eq_replacer(match):
        content = match.group(0).strip("$")
        if len(content) < 10:
            return f"[EQ:{content}]"
        return "[EQUATION]"
    text = re.sub(r"\$(.+?)\$", inline_eq_replacer, text)

    text = re.sub(r"\\ref\{[^}]*\}", "", text)
    text = re.sub(r"\\label\{[^}]*\}", "", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:{[^}]*})?", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_sections_from_single(tex_content: str) -> list[dict]:
    """단일 tex → 섹션 분리"""
    sections = []
    pattern = r"\\section\*?\{([^}]*)\}"
    matches = list(re.finditer(pattern, tex_content))

    if not matches:
        return [{
            "order": 0,
            "title": "FULL_TEXT",
            "file": "single.tex",
            "text": clean_tex_single(tex_content),
        }]

    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(tex_content)
        section_text = tex_content[start:end]
        sections.append({
            "order": i,
            "title": title if title else f"Section {i}",
            "file": "single.tex",
            "text": clean_tex_single(section_text),
        })
    return sections


def preprocess_tex_files(tex_files: dict[str, str]) -> list[dict]:
    """단일 vs 여러 tex 구분"""
    if len(tex_files) == 1:
        sole_file, content = next(iter(tex_files.items()))
        return split_sections_from_single(content)
    else:
        sections = []
        for i, (fname, content) in enumerate(sorted(tex_files.items())):
            title = Path(fname).stem.replace("_", " ").title()
            sections.append({
                "order": i,
                "title": title,
                "file": fname,
                "text": clean_tex_multi(content),
            })
        return sections
