from pathlib import Path

from agent import run


def test_run_markdown_generates_output_file(tmp_path: Path):
    input_path = tmp_path / "paper_note.md"
    input_path.write_text(
        "# Title\n\nThis is a low-light segmentation note.",
        encoding="utf-8",
    )
    output_path = tmp_path / "result.md"

    run(
        input_path=input_path,
        mode="default",
        output_path=output_path,
        topic=None,
    )

    content = output_path.read_text(encoding="utf-8")
    assert "# Title" in content
    assert "## 1. 论文研究问题" in content
    assert "## 6. 可以参考的改进点" in content
