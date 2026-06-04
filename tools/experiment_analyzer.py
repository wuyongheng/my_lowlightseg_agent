import re


KNOWN_DATASETS = ["NightCity", "BDD100K-night", "ACDC", "Dark Zurich", "Cityscapes"]
KNOWN_METRICS = ["mIoU", "IoU", "mAcc", "F1", "PSNR", "SSIM"]
KNOWN_BASELINES = ["DANNet", "GCMA", "DeepLabV3+", "HRDA", "RefineNet"]


def _extract_known_terms(text: str, vocabulary: list[str]) -> list[str]:
    found = []
    for item in vocabulary:
        if item.lower() in text.lower():
            found.append(item)
    return found


def analyze_experiments(text: str) -> dict:
    datasets = _extract_known_terms(text, KNOWN_DATASETS)
    metrics = _extract_known_terms(text, KNOWN_METRICS)
    baselines = _extract_known_terms(text, KNOWN_BASELINES)

    ablations = []
    for sentence in re.split(r"[。\n\.]+", text):
        if "ablation" in sentence.lower() or "消融" in sentence:
            cleaned = sentence.strip()
            if cleaned:
                ablations.append(cleaned)

    return {
        "datasets": datasets,
        "metrics": metrics,
        "baselines": baselines,
        "ablations": ablations,
    }
