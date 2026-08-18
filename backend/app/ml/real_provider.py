"""Real prediction provider backed by the two trained artifacts.

Verified by direct inspection (see docs/MODEL_INTEGRATION.md):

    stunting_model.pkl     sklearn.pipeline.Pipeline(preprocessor, classifier)
                            classifier = RandomForestClassifier
    underweight_model.pkl   sklearn.pipeline.Pipeline(preprocessor, classifier)
                            classifier = XGBClassifier

Both pipelines are fully self-contained: the `preprocessor` step (a
ColumnTransformer doing median imputation + scaling for CAGE, and
most-frequent imputation + one-hot encoding for the other 19 raw MICS6
predictors) is already fitted and saved inside the pickle. Flask must
NOT re-implement or re-fit any preprocessing - it only needs to build a
single-row DataFrame with the exact raw column names/order the pipeline
expects and call it directly.

`classes_` for both classifiers is `[0, 1]`, matching the notebook's
target definition (`stunting = 1 if HAZ < -2 else 0`, `underweight = 1
if WAZ < -2 else 0`), so index 1 is unambiguously the "at risk"
probability - verified, not assumed.
"""
from __future__ import annotations

import logging
import os

import joblib
import numpy as np
import pandas as pd

from app.ml.base_provider import ModelProvider
from app.ml.explainer import build_explanation
from app.ml.feature_schema import PREDICTION_TARGETS, RAW_FEATURE_ORDER
from app.ml.types import PredictionBundle, TargetExplanation, TargetPrediction

logger = logging.getLogger(__name__)

# Verified from `classifier.classes_ == [0, 1]` on both artifacts - class 1
# is the "at risk" outcome (see module docstring).
POSITIVE_CLASS_INDEX = 1


class ModelNotAvailableError(RuntimeError):
    """Raised when production mode is requested but an artifact can't be loaded."""


class _TargetPipeline:
    """Wraps one target's trained sklearn Pipeline (preprocessor + classifier)."""

    def __init__(self, path: str, version: str, decision_threshold: float):
        if not os.path.exists(path):
            raise ModelNotAvailableError(f"Expected trained artifact at '{path}' but it was not found.")

        self.pipeline = joblib.load(path)
        if "preprocessor" not in self.pipeline.named_steps or "classifier" not in self.pipeline.named_steps:
            raise ModelNotAvailableError(
                f"Artifact at '{path}' is not the expected Pipeline(preprocessor, classifier) shape."
            )

        self.preprocessor = self.pipeline.named_steps["preprocessor"]
        self.classifier = self.pipeline.named_steps["classifier"]
        self.version = version
        self.decision_threshold = decision_threshold
        self.algorithm = type(self.classifier).__name__

        expected_features = list(getattr(self.preprocessor, "feature_names_in_", []))
        if expected_features and expected_features != RAW_FEATURE_ORDER:
            raise ModelNotAvailableError(
                f"Artifact at '{path}' expects features {expected_features}, which does not match "
                f"app.ml.feature_schema.RAW_FEATURE_ORDER ({RAW_FEATURE_ORDER}). The schema must be "
                "reconciled with the actual artifact before it can be used safely."
            )

        classes = list(getattr(self.classifier, "classes_", []))
        if classes and classes != [0, 1]:
            raise ModelNotAvailableError(
                f"Artifact at '{path}' has unexpected classes_ {classes}; expected [0, 1]. "
                "The positive-class assumption in real_provider.py must be re-verified."
            )

    def predict_proba(self, raw_df: pd.DataFrame) -> float:
        transformed = self.preprocessor.transform(raw_df)
        proba = self.classifier.predict_proba(transformed)
        return float(proba[0, POSITIVE_CLASS_INDEX])

    def explain(self, raw_df: pd.DataFrame):
        transformed = self.preprocessor.transform(raw_df)
        transformed_names = self.preprocessor.get_feature_names_out()
        return build_explanation(
            self.classifier, transformed, transformed_names, RAW_FEATURE_ORDER, POSITIVE_CLASS_INDEX
        )


class RealModelProvider(ModelProvider):
    mode = "real"

    def __init__(self, config):
        self.config = config
        self.targets: dict[str, _TargetPipeline] = {
            "stunting": _TargetPipeline(
                config.STUNTING_MODEL_PATH, config.STUNTING_MODEL_VERSION, config.STUNTING_DECISION_THRESHOLD
            ),
            "underweight": _TargetPipeline(
                config.UNDERWEIGHT_MODEL_PATH, config.UNDERWEIGHT_MODEL_VERSION, config.UNDERWEIGHT_DECISION_THRESHOLD
            ),
        }

    def _build_dataframe(self, features: dict) -> pd.DataFrame:
        """Build the single-row raw input DataFrame the pipelines expect.

        IMPORTANT: the fitted OneHotEncoder's learned categories for all 19
        categorical predictors are native numpy float64 values (e.g. 1.0,
        2.0), NOT strings - verified by inspecting `categories_` directly.
        The application layer represents category codes as strings (e.g.
        "1.0") for clean JSON/UI handling, so they MUST be converted to
        float here before reaching the pipeline. Passing strings instead
        would not raise an error - `handle_unknown="ignore"` would just
        silently zero out that feature, which was confirmed empirically
        during integration testing to change predictions without warning.
        """
        row = {}
        for key in RAW_FEATURE_ORDER:
            value = features.get(key, np.nan)
            if key != "CAGE" and value is not None and not (isinstance(value, float) and np.isnan(value)):
                value = float(value)
            row[key] = value
        return pd.DataFrame([row], columns=RAW_FEATURE_ORDER)

    def predict(self, features: dict) -> PredictionBundle:
        raw_df = self._build_dataframe(features)

        targets: list[TargetPrediction] = []
        explanations: list[TargetExplanation] = []

        for target in PREDICTION_TARGETS:
            target_pipeline = self.targets[target]
            probability = target_pipeline.predict_proba(raw_df)
            predicted_label = "at_risk" if probability >= target_pipeline.decision_threshold else "not_at_risk"

            targets.append(
                TargetPrediction(
                    target=target,
                    predicted_label=predicted_label,
                    probability=round(probability, 4),
                    decision_threshold=target_pipeline.decision_threshold,
                    model_version=target_pipeline.version,
                    algorithm=target_pipeline.algorithm,
                )
            )

            method, items, note = target_pipeline.explain(raw_df)
            explanations.append(TargetExplanation(target=target, method=method, items=items, note=note))

        return PredictionBundle(mode=self.mode, targets=targets, explanations=explanations)

    def describe(self) -> dict:
        return {
            "mode": self.mode,
            "targets": {
                target: {
                    "version": tp.version,
                    "algorithm": tp.algorithm,
                    "decisionThreshold": tp.decision_threshold,
                }
                for target, tp in self.targets.items()
            },
            "explanationMethod": "shap_local (TreeExplainer, falls back to global_importance)",
        }
