# Paper Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个可运行的第一版命令行论文阅读 Agent，支持 PDF 和 Markdown 输入，并输出包含 6 个固定部分的结构化 Markdown 阅读笔记。

**Architecture:** 采用“本地解析优先、必要时多模态增强”的混合式方案。`agent.py` 负责命令行入口和流程调度，`tools/pdf_reader.py` 负责 PDF 文本提取与质量判断，`tools/experiment_analyzer.py` 负责实验信息抽取，`tools/paper_summarizer.py` 负责生成最终 6 个模块，`prompts.py` 负责集中管理提示词模板。

**Tech Stack:** Python 3.11+, `argparse`, `pathlib`, `pypdf`, `openai`, `pytest`

---

## 文件结构与职责

- `agent.py`
  - 命令行入口
  - 参数解析
  - 根据文件类型和模式选择处理流程
  - 组织本地解析、多模态回退、结果输出
- `prompts.py`
  - 保存通用论文总结 Prompt
  - 保存研究方向关联 Prompt
  - 保存改进点 Prompt
  - 保存多模态分析 Prompt
- `tools/pdf_reader.py`
  - 读取 PDF
  - 提取全文文本
  - 保留页码级内容
  - 根据启发式规则评估解析质量
- `tools/experiment_analyzer.py`
  - 从论文内容中提取数据集、指标、基线、消融等实验信息
- `tools/paper_summarizer.py`
  - 统一组织模型输入
  - 生成固定的 6 个输出部分
  - 返回结构化结果
- `README.md`
  - 项目说明
  - 安装方式
  - 命令行示例
- `requirements.txt`
  - 运行依赖
- `.gitignore`
  - 忽略缓存、虚拟环境、输出文件
- `tests/test_agent_cli.py`
  - 测试命令行参数解析和文件路由
- `tests/test_pdf_reader.py`
  - 测试 PDF 提取质量判断逻辑
- `tests/test_experiment_analyzer.py`
  - 测试实验信息抽取
- `tests/test_paper_summarizer.py`
  - 测试结构化结果格式
- `tests/test_end_to_end.py`
  - 端到端测试 Markdown 输入到 Markdown 输出

## 预备步骤

如果当前目录还不是 Git 仓库，先执行：

```bash
git init
```

然后创建基础目录：

```bash
mkdir data
mkdir data\papers
mkdir notes
mkdir tools
mkdir tests
```

安装依赖：

```bash
python -m pip install -r requirements.txt
```

## Task 1: 建立项目骨架与 CLI 参数解析

**Files:**
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `agent.py`
- Create: `tests/test_agent_cli.py`

- [ ] **Step 1: 先写命令行参数测试**

```python
from pathlib import Path

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
```

- [ ] **Step 2: 运行测试，确认当前失败**

Run:

```bash
pytest tests/test_agent_cli.py -v
```

Expected:

```text
E   ModuleNotFoundError: No module named 'agent'
```

- [ ] **Step 3: 写最小实现，先让参数解析和输入类型识别通过**

```python
import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Low-light segmentation paper reading agent")
    parser.add_argument("--input", required=True, help="Path to a PDF paper or Markdown note")
    parser.add_argument(
        "--mode",
        choices=["default", "multimodal", "auto"],
        default="auto",
        help="Processing mode",
    )
    parser.add_argument("--output", help="Optional output markdown path")
    parser.add_argument("--topic", help="Optional research focus override")
    return parser


def detect_input_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix in {".md", ".markdown"}:
        return "markdown"
    raise ValueError(f"Unsupported input file type: {suffix}")


def main() -> None:
    parser = build_parser()
    parser.parse_args()


if __name__ == "__main__":
    main()
```

`requirements.txt`

```text
pypdf>=4.2.0
openai>=1.35.0
pytest>=8.2.0
```

`.gitignore`

```gitignore
__pycache__/
.pytest_cache/
.venv/
notes/*.md
data/papers/*.pdf
```

- [ ] **Step 4: 重新运行测试，确认通过**

Run:

```bash
pytest tests/test_agent_cli.py -v
```

Expected:

```text
3 passed
```

- [ ] **Step 5: 提交这一小步**

```bash
git add .gitignore requirements.txt agent.py tests/test_agent_cli.py
git commit -m "feat: add CLI parser and input type detection"
```

## Task 2: 打通 Markdown 输入与基础输出路径

**Files:**
- Modify: `agent.py`
- Create: `prompts.py`
- Create: `tools/paper_summarizer.py`
- Create: `tests/test_paper_summarizer.py`
- Create: `tests/test_end_to_end.py`

- [ ] **Step 1: 先写总结结果结构测试**

```python
from tools.paper_summarizer import empty_summary_template


def test_empty_summary_template_has_all_required_sections():
    summary = empty_summary_template("Example Title")
    assert summary["title"] == "Example Title"
    assert list(summary["sections"].keys()) == [
        "论文研究问题",
        "方法整体框架",
        "创新点",
        "实验设置",
        "和我的研究方向的关系",
        "可以参考的改进点",
    ]
```

`tests/test_end_to_end.py`

```python
from pathlib import Path

from agent import run


def test_run_markdown_generates_output_file(tmp_path: Path):
    input_path = tmp_path / "paper_note.md"
    input_path.write_text("# Title\n\nThis is a low-light segmentation note.", encoding="utf-8")
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
```

- [ ] **Step 2: 运行测试，确认当前失败**

Run:

```bash
pytest tests/test_paper_summarizer.py tests/test_end_to_end.py -v
```

Expected:

```text
E   ImportError
```

- [ ] **Step 3: 实现 Markdown 路径、总结模板和输出写入**

`prompts.py`

```python
SYSTEM_RESEARCH_CONTEXT = (
    "你是一个服务于低光照夜间语义分割研究的论文阅读助手。"
    "请始终从下游语义分割收益出发，不要把讨论重心放在纯图像增强。"
)


def build_summary_prompt(paper_text: str, topic: str | None = None) -> str:
    focus = topic or "低光照夜间语义分割"
    return (
        f"{SYSTEM_RESEARCH_CONTEXT}\n"
        f"研究关注点：{focus}\n"
        "请基于以下论文内容，输出六个部分：\n"
        "1. 论文研究问题\n"
        "2. 方法整体框架\n"
        "3. 创新点\n"
        "4. 实验设置\n"
        "5. 和我的研究方向的关系\n"
        "6. 可以参考的改进点\n\n"
        f"论文内容：\n{paper_text}"
    )
```

`tools/paper_summarizer.py`

```python
from collections import OrderedDict


def empty_summary_template(title: str) -> dict:
    return {
        "title": title,
        "sections": OrderedDict(
            [
                ("论文研究问题", "待模型总结。"),
                ("方法整体框架", "待模型总结。"),
                ("创新点", "待模型总结。"),
                ("实验设置", "待实验分析模块补充。"),
                ("和我的研究方向的关系", "待模型结合研究方向总结。"),
                ("可以参考的改进点", "待模型提出建议。"),
            ]
        ),
    }


def render_summary_markdown(summary: dict) -> str:
    lines = [f"# {summary['title']}", ""]
    for index, (section_name, section_body) in enumerate(summary["sections"].items(), start=1):
        lines.append(f"## {index}. {section_name}")
        lines.append(section_body)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
```

`agent.py`

```python
from pathlib import Path

from tools.paper_summarizer import empty_summary_template, render_summary_markdown


def read_markdown(path: Path) -> tuple[str, str]:
    content = path.read_text(encoding="utf-8")
    title = path.stem
    for line in content.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return title, content


def run(input_path: Path, mode: str, output_path: Path | None, topic: str | None) -> Path:
    input_type = detect_input_type(input_path)
    if input_type != "markdown":
        raise NotImplementedError("PDF path is not implemented yet")

    title, content = read_markdown(input_path)
    summary = empty_summary_template(title)
    summary["sections"]["论文研究问题"] = content[:500] or "输入内容为空。"
    output_path = output_path or Path("notes") / f"{input_path.stem}_summary.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_summary_markdown(summary), encoding="utf-8")
    return output_path
```

- [ ] **Step 4: 重新运行测试，确认 Markdown 路径贯通**

Run:

```bash
pytest tests/test_paper_summarizer.py tests/test_end_to_end.py -v
```

Expected:

```text
2 passed
```

- [ ] **Step 5: 提交这一小步**

```bash
git add agent.py prompts.py tools/paper_summarizer.py tests/test_paper_summarizer.py tests/test_end_to_end.py
git commit -m "feat: add markdown input flow and summary rendering"
```

## Task 3: 实现 PDF 文本提取与解析质量判断

**Files:**
- Create: `tools/pdf_reader.py`
- Create: `tests/test_pdf_reader.py`
- Modify: `agent.py`

- [ ] **Step 1: 先写 PDF 质量判断测试**

```python
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
```

- [ ] **Step 2: 运行测试，确认当前失败**

Run:

```bash
pytest tests/test_pdf_reader.py -v
```

Expected:

```text
E   ModuleNotFoundError: No module named 'tools.pdf_reader'
```

- [ ] **Step 3: 实现 PDF 读取与质量评估**

`tools/pdf_reader.py`

```python
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

    if len(joined) < 300:
        reasons.append("文本长度过短")

    if joined.count("\x00") > 0:
        reasons.append("存在空字节异常")

    broken_line_ratio = 0.0
    lines = [line for line in joined.splitlines() if line.strip()]
    if lines:
        short_lines = [line for line in lines if len(line.strip()) < 20]
        broken_line_ratio = len(short_lines) / len(lines)
    if broken_line_ratio > 0.6:
        reasons.append("断行过碎")

    lower_text = joined.lower()
    if "introduction" not in lower_text and "experiment" not in lower_text:
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
```

## Task 4: 实现实验信息抽取模块

- 使用规则法抽取数据集、指标、基线和消融信息
- 将结果写入“实验设置”部分

## Task 5: 接入模型总结逻辑，生成完整 6 个模块

- 增加 JSON 格式 Prompt
- 增加 `summarize_with_llm` 与结构合并逻辑
- 在未配置 `OPENAI_API_KEY` 时保持工具可运行

## Task 6: 实现 auto 模式回退与 multimodal 占位流程

- 增加 `should_use_multimodal`
- 增加模式说明与 fallback 提示

## Task 7: 做一次最小端到端验收

- 用 `sample.md` 走通 CLI
- 跑完整测试集
- 补齐空目录占位与 README 能力边界
