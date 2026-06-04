import json
import os
from collections import OrderedDict

from openai import OpenAI

from prompts import build_json_summary_prompt


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
    for index, (section_name, section_body) in enumerate(
        summary["sections"].items(),
        start=1,
    ):
        lines.append(f"## {index}. {section_name}")
        lines.append(section_body)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def merge_llm_sections_into_summary(summary: dict, generated: dict) -> dict:
    for key in summary["sections"]:
        if key in generated and generated[key]:
            summary["sections"][key] = generated[key]
    return summary


def summarize_with_llm(paper_text: str, topic: str | None = None) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {}

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=build_json_summary_prompt(paper_text, topic),
    )
    text = response.output_text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}
