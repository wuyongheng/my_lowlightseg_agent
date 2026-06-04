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


def build_json_summary_prompt(paper_text: str, topic: str | None = None) -> str:
    focus = topic or "低光照夜间语义分割"
    return (
        f"{SYSTEM_RESEARCH_CONTEXT}\n"
        f"研究聚焦：{focus}\n"
        "请只输出 JSON 对象，不要输出额外说明。JSON 必须包含以下键："
        "论文研究问题、方法整体框架、创新点、实验设置、和我的研究方向的关系、可以参考的改进点。"
        f"\n论文内容如下：\n{paper_text}"
    )


def build_multimodal_prompt(topic: str | None = None) -> str:
    focus = topic or "低光照夜间语义分割"
    return (
        "请结合 PDF 页面中的图、表、方法框架图和正文内容，"
        "输出六个固定部分的结构化论文总结。"
        f"研究焦点为：{focus}。"
    )
