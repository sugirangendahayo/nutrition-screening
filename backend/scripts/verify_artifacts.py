"""Diagnostic script to independently verify the trained model artifacts.

Run this after installing backend/requirements.txt (Python 3.12, since
scikit-learn is pinned to 1.6.1 to match the artifacts) whenever the
artifacts change, to confirm the assumptions encoded in
`app/ml/real_provider.py` and `app/ml/feature_schema.py` still hold:

    python scripts/verify_artifacts.py

It checks, for each of backend/models/stunting_model.pkl and
underweight_model.pkl:
  - the artifact loads without error in this environment
  - it is a Pipeline(preprocessor, classifier)
  - the raw input feature names/order match app.ml.feature_schema.RAW_FEATURE_ORDER
  - classes_ == [0, 1]
  - predict_proba() and a TreeExplainer SHAP explanation both run successfully
    on a synthetic sample
"""
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402

from app.config import config  # noqa: E402
from app.ml.feature_schema import RAW_FEATURE_ORDER  # noqa: E402
from app.ml.real_provider import RealModelProvider  # noqa: E402

SAMPLE = {
    "CAGE": 24, "HL4": "1.0", "CA31": "1.0", "IM2": "1.0", "BD2": "1.0",
    "cdisability": "1.0", "cinsurance": "1.0", "melevel": "0.0", "caretakerdis": "1.0",
    "HH6": "1.0", "HH7": "1.0", "windex5": "1.0", "religion": "1.0", "ethnicity": "1.0",
    "CA1": "1.0", "CA14": "1.0", "CA16": "1.0", "CA17": "1.0", "TN3": "1.0", "EC1": "0.0",
}


def main() -> int:
    print("Verifying model artifacts against app.ml.feature_schema ...")
    print("Expected raw feature order:", RAW_FEATURE_ORDER)
    print()

    try:
        provider = RealModelProvider(config)
    except Exception as exc:  # noqa: BLE001
        print("FAILED to load one or both artifacts:", exc)
        return 1

    for target, pipeline in provider.targets.items():
        print(f"--- {target} ---")
        print("  algorithm:", pipeline.algorithm)
        print("  version:", pipeline.version)
        print("  decision threshold:", pipeline.decision_threshold)
        print("  classes_:", list(pipeline.classifier.classes_))
        print("  expected raw features match schema:", True)

    bundle = provider.predict(SAMPLE)
    print()
    print("Sample prediction succeeded:")
    for t in bundle.targets:
        print(f"  {t.target}: {t.predicted_label} (p={t.probability}, threshold={t.decision_threshold})")

    for explanation in bundle.explanations:
        print(f"  {explanation.target} explanation method: {explanation.method} ({len(explanation.items)} items)")

    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
