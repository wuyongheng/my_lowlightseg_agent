from tools.experiment_analyzer import analyze_experiments


def test_analyze_experiments_extracts_dataset_metric_and_baseline():
    paper_text = """
    Experiments. We evaluate on NightCity and BDD100K-night.
    The metric is mIoU.
    We compare against DANNet and GCMA.
    Ablation studies evaluate the semantic guidance module.
    """
    result = analyze_experiments(paper_text)
    assert "NightCity" in result["datasets"]
    assert "mIoU" in result["metrics"]
    assert "DANNet" in result["baselines"]
    assert "semantic guidance module" in " ".join(result["ablations"])
