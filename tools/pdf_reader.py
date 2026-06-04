from pathlib import Path

from pypdf import PdfReader


def extract_pdf_pages(path: Path) -> list[str]:
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append((page.extract_text() or "").strip())
    return pages


def assess_pdf_text_quality(pages: list[str]) -> dict:
    joined = "\n".join(pages).strip()
    reasons: list[str] = []
    lower_text = joined.lower()

    has_section_signal = (
        "introduction" in lower_text
        or "experiment" in lower_text
        or "method" in lower_text
    )

    if len(joined) < 80:
        reasons.append("文本长度过短")

    if joined.count("\x00") > 0:
        reasons.append("存在空字节异常")

    lines = [line for line in joined.splitlines() if line.strip()]
    broken_line_ratio = 0.0
    if lines:
        short_lines = [line for line in lines if len(line.strip()) < 20]
        broken_line_ratio = len(short_lines) / len(lines)
    if broken_line_ratio > 0.6:
        reasons.append("断行过碎")

    if not has_section_signal:
        reasons.append("常见章节线索不足")

    return {
        "is_low_quality": len(reasons) > 0,
        "reasons": reasons,
        "text_length": len(joined),
        "page_count": len(pages),
    }


def read_pdf_document(path: Path) -> dict:
    pages = extract_pdf_pages(path)
    quality = assess_pdf_text_quality(pages)
    return {
        "title": path.stem,
        "pages": pages,
        "full_text": "\n\n".join(pages).strip(),
        "quality": quality,
    }
