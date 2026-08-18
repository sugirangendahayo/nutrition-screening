"""Finds input values that push the trained models toward "at_risk", purely
empirically, by querying the actual trained pipelines - for use when
demoing/testing the screening workflow with a guaranteed high-risk case.

This does NOT encode any clinical assumption about what causes stunting or
underweight. It reports what the trained model responds to (a greedy,
one-field-at-a-time search: for each raw feature, try every valid option and
keep whichever maximizes the target's predicted probability, holding the
rest fixed). Treat the result the same way the app treats "Model Feature
Importance": useful for testing, not a clinical claim - see
docs/MODEL_INFO.md and docs/MODEL_INTEGRATION.md.

Run (from backend/, with the venv activated):

    python scripts/find_high_risk_input.py
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import config  # noqa: E402
from app.ml.feature_schema import FEATURE_FIELDS, RAW_FEATURE_ORDER  # noqa: E402
from app.ml.real_provider import RealModelProvider  # noqa: E402

BASELINE = {
    "CAGE": 24, "HL4": "1.0", "CA31": "1.0", "IM2": "1.0", "BD2": "1.0",
    "cdisability": "1.0", "cinsurance": "1.0", "melevel": "0.0", "caretakerdis": "1.0",
    "HH6": "1.0", "HH7": "1.0", "windex5": "1.0", "religion": "1.0", "ethnicity": "1.0",
    "CA1": "1.0", "CA14": "1.0", "CA16": "1.0", "CA17": "1.0", "TN3": "1.0", "EC1": "0.0",
}

FIELDS_BY_KEY = {f.key: f for f in FEATURE_FIELDS}
TARGETS = ["stunting", "underweight"]


def probability_for(provider: RealModelProvider, target: str, features: dict) -> float:
    # Call predict_proba directly (bypassing provider.predict(), which also
    # computes a full SHAP explanation for both targets on every call) -
    # this search makes hundreds of predictions, and SHAP is by far the
    # most expensive part of a normal prediction.
    raw_df = provider._build_dataframe(features)
    return provider.targets[target].predict_proba(raw_df)


def optimize_for_target(provider: RealModelProvider, target: str) -> dict:
    best = dict(BASELINE)

    # CAGE is the only numeric field - sweep the full valid range (months).
    best_prob, best_age = -1.0, best["CAGE"]
    for age in range(0, 60):
        prob = probability_for(provider, target, dict(best, CAGE=age))
        if prob > best_prob:
            best_prob, best_age = prob, age
    best["CAGE"] = best_age

    # Every categorical field: try each option the model was actually
    # trained on (from feature_schema, which mirrors the fitted
    # OneHotEncoder's learned categories), keep whichever maximizes this
    # target's probability, holding everything else fixed.
    for key in RAW_FEATURE_ORDER:
        if key == "CAGE":
            continue
        field = FIELDS_BY_KEY[key]
        best_prob, best_value = -1.0, best[key]
        for option in field.options:
            prob = probability_for(provider, target, dict(best, **{key: option.value}))
            if prob > best_prob:
                best_prob, best_value = prob, option.value
        best[key] = best_value

    return best


def main() -> int:
    provider = RealModelProvider(config)

    print("Baseline probabilities (arbitrary starting point):")
    for target in TARGETS:
        print(f"  {target:12s}: {probability_for(provider, target, BASELINE):.4f}")

    for target in TARGETS:
        optimized = optimize_for_target(provider, target)
        prob = probability_for(provider, target, optimized)
        threshold = provider.targets[target].decision_threshold

        print(f"\n{'=' * 70}")
        print(f"Input maximizing {target.upper()} risk (fill the form with these values)")
        print(f"{'=' * 70}")
        for key in RAW_FEATURE_ORDER:
            print(f"  {key:15s} = {optimized[key]}")
        status = "AT RISK" if prob >= threshold else "not at risk (could not cross threshold this way)"
        print(f"\n  -> {target} probability: {prob:.4f}  (threshold {threshold})  [{status}]")

        other = TARGETS[1] if target == TARGETS[0] else TARGETS[0]
        other_prob = probability_for(provider, other, optimized)
        other_threshold = provider.targets[other].decision_threshold
        other_status = "ALSO at risk" if other_prob >= other_threshold else "not at risk"
        print(f"  -> {other} probability with this same input: {other_prob:.4f}  [{other_status}]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
