"""Real prediction provider, backed by trained artifact(s) on disk.

Supports two artifact layouts, selected via `MODEL_MODE`:

    dual_model
        Two separate model files, one per target:
        STUNTING_MODEL_PATH, UNDERWEIGHT_MODEL_PATH

    single_multioutput
        One model file (MODEL_PATH) that produces predictions for both
        targets at once (e.g. a MultiOutputClassifier or a model with two
        output columns).

An optional shared PREPROCESSOR_PATH artifact (e.g. a fitted
ColumnTransformer) is applied to the raw input before it reaches the
model(s), for architectures where preprocessing was fit separately from
the estimator during training.

IMPORTANT: this module intentionally does not assume specific feature
names, encodings, or output conventions beyond what is documented in
`docs/MODEL_INTEGRATION.md`. When the real artifact is supplied, it must
be inspected and this module (and the assumptions below) validated
against it before enabling ML_MODEL_STATUS=production.
"""
from __future__ import annotations

import logging
import os

import joblib
import numpy as np
import pandas as pd

from app.ml.base_provider import ModelProvider
from app.ml.explainer import build_explanation
from app.ml.feature_schema import FEATURE_FIELDS, PREDICTION_TARGETS, get_fields_by_key
from app.ml.types import PredictionBundle, TargetExplanation, TargetPrediction

logger = logging.getLogger(__name__)

FEATURE_KEYS = [f.key for f in FEATURE_FIELDS]


class ModelNotAvailableError(RuntimeError):
    """Raised when production mode is requested but no valid artifact is loaded."""


def _positive_class_index(classes) -> int:
    """Best-effort detection of which class index represents 'at risk'.

    Assumes the common scikit-learn convention where classes are sorted
    and the positive class is encoded as 1 / "1" / "at_risk", which is
    typically the last entry. This MUST be verified against the actual
    trained artifact - see docs/MODEL_INTEGRATION.md.
    """
    classes_list = list(classes)
    for candidate in (1, "1", "at_risk", "yes", True):
        if candidate in classes_list:
            return classes_list.index(candidate)
    return len(classes_list) - 1


class _TargetModel:
    def __init__(self, path: str):
        self.path = path
        self.estimator = joblib.load(path)
        self.positive_index = None
        if hasattr(self.estimator, "classes_"):
            self.positive_index = _positive_class_index(self.estimator.classes_)

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        if hasattr(self.estimator, "predict_proba"):
            proba = self.estimator.predict_proba(df)
            index = self.positive_index if self.positive_index is not None else proba.shape[1] - 1
            return proba[:, index]
        # Fall back to hard predictions if the estimator has no predict_proba.
        preds = self.estimator.predict(df)
        return np.asarray([1.0 if p in (1, "1", "at_risk", True) else 0.0 for p in preds])


class RealModelProvider(ModelProvider):
    mode = "real"

    def __init__(self, config):
        self.version = config.MODEL_VERSION
        self.config = config
        self._fields_by_key = get_fields_by_key()
        self.preprocessor = None
        self.background_df: pd.DataFrame | None = None
        self.models: dict[str, _TargetModel] = {}
        self._load(config)

    def _load(self, config):
        if config.PREPROCESSOR_PATH and os.path.exists(config.PREPROCESSOR_PATH):
            self.preprocessor = joblib.load(config.PREPROCESSOR_PATH)

        if config.BACKGROUND_DATA_PATH and os.path.exists(config.BACKGROUND_DATA_PATH):
            self.background_df = joblib.load(config.BACKGROUND_DATA_PATH)

        if config.MODEL_MODE == "dual_model":
            for target, path in (
                ("stunting", config.STUNTING_MODEL_PATH),
                ("underweight", config.UNDERWEIGHT_MODEL_PATH),
            ):
                if not os.path.exists(path):
                    raise ModelNotAvailableError(
                        f"Expected trained artifact for '{target}' at '{path}' but it was not found."
                    )
                self.models[target] = _TargetModel(path)
        elif config.MODEL_MODE == "single_multioutput":
            if not os.path.exists(config.MODEL_PATH):
                raise ModelNotAvailableError(
                    f"Expected trained artifact at '{config.MODEL_PATH}' but it was not found."
                )
            shared = _TargetModel(config.MODEL_PATH)
            for target in PREDICTION_TARGETS:
                self.models[target] = shared
        else:
            raise ModelNotAvailableError(f"Unsupported MODEL_MODE '{config.MODEL_MODE}'.")

    def _build_dataframe(self, features: dict) -> pd.DataFrame:
        row = {key: features.get(key, np.nan) for key in FEATURE_KEYS}
        return pd.DataFrame([row], columns=FEATURE_KEYS)

    def _predict_proba_fn(self, target_model: _TargetModel):
        def fn(df: pd.DataFrame) -> np.ndarray:
            data = df
            if self.preprocessor is not None:
                data = self.preprocessor.transform(df)
            return target_model.predict_proba(data)

        return fn

    def predict(self, features: dict) -> PredictionBundle:
        input_df = self._build_dataframe(features)

        targets: list[TargetPrediction] = []
        explanations: list[TargetExplanation] = []

        for target in PREDICTION_TARGETS:
            target_model = self.models[target]
            predict_fn = self._predict_proba_fn(target_model)

            data_for_model = input_df
            if self.preprocessor is not None:
                data_for_model = self.preprocessor.transform(input_df)
            probability = float(target_model.predict_proba(data_for_model)[0])
            predicted_label = "at_risk" if probability >= 0.5 else "not_at_risk"

            targets.append(
                TargetPrediction(
                    target=target,
                    predicted_label=predicted_label,
                    probability=round(probability, 4),
                )
            )

            method, items, note = build_explanation(
                model=target_model.estimator,
                predict_proba_fn=predict_fn,
                input_df=input_df,
                background_df=self.background_df,
            )
            explanations.append(
                TargetExplanation(target=target, method=method, items=items, note=note)
            )

        return PredictionBundle(
            mode=self.mode,
            model_version=self.version,
            targets=targets,
            explanations=explanations,
        )

    def describe(self) -> dict:
        return {
            "mode": self.mode,
            "version": self.version,
            "modelMode": self.config.MODEL_MODE,
            "targets": list(PREDICTION_TARGETS),
            "explanationMethod": "shap_local (falls back to global_importance)" if self.background_df is not None else "global_importance",
            "hasBackgroundSample": self.background_df is not None,
            "hasSharedPreprocessor": self.preprocessor is not None,
        }
