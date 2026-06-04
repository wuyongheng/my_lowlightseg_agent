from tools.paper_summarizer import empty_summary_template
from tools.paper_summarizer import merge_llm_sections_into_summary


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


def test_merge_llm_sections_into_summary_updates_known_sections():
    summary = {
        "title": "Paper",
        "sections": {
            "论文研究问题": "",
            "方法整体框架": "",
            "创新点": "",
            "实验设置": "",
            "和我的研究方向的关系": "",
            "可以参考的改进点": "",
        },
    }
    generated = {
        "论文研究问题": "解决夜间低光照语义分割性能下降问题。",
        "创新点": "引入语义引导增强模块。",
    }
    merged = merge_llm_sections_into_summary(summary, generated)
    assert merged["sections"]["论文研究问题"] == "解决夜间低光照语义分割性能下降问题。"
    assert merged["sections"]["创新点"] == "引入语义引导增强模块。"
