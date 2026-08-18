"""Prints, directly from the trained model artifacts, the exact 20 raw input
features and the global feature importances aggregated back to those raw
features.

This reproduces every number documented in docs/MODEL_INFO.md ("Exact Raw
Input Features" and "Global Feature Importance Observed") straight from the
`.pkl` files, live - nothing here is hard-coded or looked up from a document.
Use this to show an audience exactly where the raw MICS6 codes and the
feature-importance percentages come from.

Run (from backend/, with the venv activated):

    python scripts/show_feature_importance.py
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib  # noqa: E402

from app.config import config  # noqa: E402
from app.ml.feature_schema import RAW_FEATURE_ORDER  # noqa: E402


def show(label: str, path: str) -> None:
    pipeline = joblib.load(path)
    preprocessor = pipeline.named_steps["preprocessor"]
    classifier = pipeline.named_steps["classifier"]

    print("=" * 72)
    print(label)
    print("=" * 72)
    print("Artifact file:", path)
    print("Algorithm:", type(classifier).__name__)

    print("\n1) Raw input features expected by this model")
    print("   (read directly from preprocessor.feature_names_in_):")
    for i, name in enumerate(preprocessor.feature_names_in_, start=1):
        print(f"     {i:2d}. {name}")

    matches_schema = list(preprocessor.feature_names_in_) == RAW_FEATURE_ORDER
    print(f"\n   Matches app.ml.feature_schema.RAW_FEATURE_ORDER: {matches_schema}")

    # The preprocessor one-hot-encodes 19 of the 20 raw features, expanding
    # them into ~73 transformed columns named e.g. "cat__windex5_3.0". To
    # report importance per ORIGINAL raw predictor (not per one-hot column),
    # sum the transformed columns that belong to each raw feature - the same
    # aggregation app.ml.explainer.py uses for the in-app explanation.
    transformed_names = preprocessor.get_feature_names_out()
    importances = classifier.feature_importances_

    aggregated: dict[str, float] = {key: 0.0 for key in RAW_FEATURE_ORDER}
    for name, importance in zip(transformed_names, importances):
        prefix, _, rest = name.partition("__")
        if prefix == "num" and rest in aggregated:
            aggregated[rest] += importance
        elif prefix == "cat":
            for key in RAW_FEATURE_ORDER:
                if rest == key or rest.startswith(f"{key}_"):
                    aggregated[key] += importance
                    break

    ranked = sorted(aggregated.items(), key=lambda kv: kv[1], reverse=True)

    print("\n2) Global feature importance")
    print("   (classifier.feature_importances_, aggregated back to raw")
    print("   features, highest first):")
    for name, value in ranked:
        print(f"     {name:15s} {value * 100:5.2f}%")
    print()


def main() -> int:
    show("STUNTING MODEL (Random Forest)", config.STUNTING_MODEL_PATH)
    show("UNDERWEIGHT MODEL (XGBoost)", config.UNDERWEIGHT_MODEL_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
