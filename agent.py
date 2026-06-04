import argparse
import os
from pathlib import Path

from tools.experiment_analyzer import analyze_experiments
from tools.pdf_reader import read_pdf_document
from tools.paper_summarizer import (
    empty_summary_template,
    merge_llm_sections_into_summary,
    render_summary_markdown,
    summarize_with_llm,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Low-light segmentation paper reading agent"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a PDF paper or Markdown note",
    )
    parser.add_argument(
        "--mode",
        choices=["default", "multimodal", "auto"],
        default="auto",
        help="Processing mode",
    )
    parser.add_argument(
        "--output",
        help="Optional output markdown path",
    )
    parser.add_argument(
        "--topic",
        help="Optional research focus override",
    )
    return parser


def detect_input_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix in {".md", ".markdown"}:
        return "markdown"
    raise ValueError(f"Unsupported input file type: {suffix}")


def read_markdown(path: Path) -> tuple[str, str]:
    content = path.read_text(encoding="utf-8")
    title = path.stem
    for line in content.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return title, content


def should_use_multimodal(mode: str, quality: dict | None) -> bool:
    if mode == "multimodal":
        return True
    if mode == "auto" and quality and quality["is_low_quality"]:
        return True
    return False


def multimodal_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def run(
    input_path: Path,
    mode: str,
    output_path: Path | None,
    topic: str | None,
) -> Path:
    input_type = detect_input_type(input_path)

    if input_type == "markdown":
        title, content = read_markdown(input_path)
        quality = None
    elif input_type == "pdf":
        document = read_pdf_document(input_path)
        title = document["title"]
        content = document["full_text"]
        quality = document["quality"]
    else:
        raise ValueError(f"Unsupported input type: {input_type}")

    experiments = analyze_experiments(content)
    summary = empty_summary_template(title)
    summary["sections"]["论文研究问题"] = content[:500] or "输入内容为空。"
    summary["sections"]["实验设置"] = (
        f"数据集：{', '.join(experiments['datasets']) or '未识别'}；"
        f"指标：{', '.join(experiments['metrics']) or '未识别'}；"
        f"基线：{', '.join(experiments['baselines']) or '未识别'}；"
        f"消融：{' | '.join(experiments['ablations']) or '未识别'}。"
    )

    use_multimodal = should_use_multimodal(mode, quality)
    if use_multimodal and not multimodal_available():
        summary["sections"]["方法整体框架"] = (
            "检测到当前文档更适合多模态分析，但环境中未配置可用模型凭据，已退回本地文本总结。"
        )

    generated_sections = summarize_with_llm(content, topic)
    summary = merge_llm_sections_into_summary(summary, generated_sections)

    if quality and quality["is_low_quality"] and not use_multimodal:
        summary["sections"]["方法整体框架"] = "PDF 文本解析质量较低，建议结合多模态模式复查。"

    final_output_path = output_path or Path("notes") / f"{input_path.stem}_summary.md"
    final_output_path.parent.mkdir(parents=True, exist_ok=True)
    final_output_path.write_text(
        render_summary_markdown(summary),
        encoding="utf-8",
    )
    return final_output_path


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run(
        input_path=Path(args.input),
        mode=args.mode,
        output_path=Path(args.output) if args.output else None,
        topic=args.topic,
    )


if __name__ == "__main__":
    main()
