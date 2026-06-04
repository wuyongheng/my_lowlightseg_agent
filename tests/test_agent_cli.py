from pathlib import Path

import agent
from agent import build_parser, detect_input_type


def test_build_parser_accepts_required_input():
    parser = build_parser()
    args = parser.parse_args(["--input", "data/papers/sample.pdf"])
    assert args.input == "data/papers/sample.pdf"
    assert args.mode == "auto"
    assert args.output is None


def test_detect_input_type_supports_pdf_and_markdown():
    assert detect_input_type(Path("paper.pdf")) == "pdf"
    assert detect_input_type(Path("note.md")) == "markdown"


def test_detect_input_type_rejects_unknown_suffix():
    try:
        detect_input_type(Path("paper.txt"))
    except ValueError as exc:
        assert "Unsupported input file type" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported suffix")


def test_should_enable_multimodal_when_auto_and_quality_is_low():
    quality = {"is_low_quality": True, "reasons": ["文本长度过短"]}
    assert agent.should_use_multimodal("auto", quality) is True


def test_should_not_enable_multimodal_when_default_mode():
    quality = {"is_low_quality": True, "reasons": ["文本长度过短"]}
    assert agent.should_use_multimodal("default", quality) is False
