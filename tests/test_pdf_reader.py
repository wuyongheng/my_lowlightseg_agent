from tools.pdf_reader import assess_pdf_text_quality


def test_assess_pdf_text_quality_marks_short_text_as_low_quality():
    result = assess_pdf_text_quality(["short text"])
    assert result["is_low_quality"] is True
    assert "文本长度过短" in result["reasons"]


def test_assess_pdf_text_quality_marks_clean_text_as_usable():
    pages = [
        "Introduction\nThis paper studies low-light semantic segmentation with a two-stage pipeline.",
        "Experiments\nWe evaluate on NightCity with mIoU and compare with baseline models.",
    ]
    result = assess_pdf_text_quality(pages)
    assert result["is_low_quality"] is False
