"""Nutrition screening trend calculation.

The trend is derived strictly from stored assessment results for the
same child - never from invented clinical thresholds. It answers a
simple question: compared to the previous assessment, did the result
for each target get better, worse, or stay the same?
"""
from __future__ import annotations

TREND_IMPROVING = "improving"
TREND_WORSENING = "worsening"
TREND_STABLE = "stable"
TREND_INSUFFICIENT_DATA = "insufficient_data"


def _target_trend(previous_label: str, current_label: str) -> str:
    if previous_label == current_label:
        return TREND_STABLE
    if previous_label == "at_risk" and current_label == "not_at_risk":
        return TREND_IMPROVING
    if previous_label == "not_at_risk" and current_label == "at_risk":
        return TREND_WORSENING
    return TREND_STABLE


def compute_trend(history: list[dict], targets: list[str]) -> dict:
    """`history` must be a list of assessment summaries sorted ascending by
    date, each shaped like:
        {"assessedAt": str, "predictions": {"stunting": {"predictedLabel": ...}, ...}}
    """
    series = [
        {
            "assessedAt": item["assessedAt"],
            "predictions": {
                target: {
                    "predictedLabel": item["predictions"].get(target, {}).get("predictedLabel"),
                    "probability": item["predictions"].get(target, {}).get("probability"),
                }
                for target in targets
            },
        }
        for item in history
    ]

    if len(history) < 2:
        return {
            "status": TREND_INSUFFICIENT_DATA,
            "perTarget": {target: TREND_INSUFFICIENT_DATA for target in targets},
            "overall": TREND_INSUFFICIENT_DATA,
            "series": series,
        }

    previous, current = history[-2], history[-1]
    per_target = {}
    for target in targets:
        prev_label = previous["predictions"].get(target, {}).get("predictedLabel")
        curr_label = current["predictions"].get(target, {}).get("predictedLabel")
        if not prev_label or not curr_label:
            per_target[target] = TREND_INSUFFICIENT_DATA
        else:
            per_target[target] = _target_trend(prev_label, curr_label)

    values = list(per_target.values())
    if TREND_WORSENING in values:
        overall = TREND_WORSENING
    elif TREND_IMPROVING in values and TREND_WORSENING not in values:
        overall = TREND_IMPROVING
    elif all(v == TREND_INSUFFICIENT_DATA for v in values):
        overall = TREND_INSUFFICIENT_DATA
    else:
        overall = TREND_STABLE

    return {
        "status": "available",
        "perTarget": per_target,
        "overall": overall,
        "series": series,
    }
