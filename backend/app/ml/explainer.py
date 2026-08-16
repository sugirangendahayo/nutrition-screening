"""Explanation generation for real trained models.

Prefers a local (per-prediction) explanation using SHAP. If SHAP cannot
be computed (no background sample configured, incompatible model, or an
error at runtime) it falls back to the model's global feature
importance / coefficients, clearly labeled as such. It never fabricates
numbers - every value returned has a concrete technical origin.
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from app.ml.feature_schema import get_fields_by_key
from app.ml.types import ExplanationItem

logger = logging.getLogger(__name__)

TOP_N = 8

GLOBAL_IMPORTANCE_NOTE = (
    "Model Feature Importance: shows which predictors are generally most "
    "influential for this model overall. It is not specific to this child's "
    "individual result and does not establish causation."
)

LOCAL_EXPLANATION_NOTE = (
    "Local explanation (SHAP): shows the estimated contribution of each "
    "predictor to this specific prediction. Positive values push the "
    "prediction toward 'at risk'; negative values push it toward 'not at "
    "risk'. It does not establish causation."
)


def _to_items(pairs: list[tuple[str, float]]) -> list[ExplanationItem]:
    fields_by_key = get_fields_by_key()
    items = []
    for key, value in pairs[:TOP_N]:
        label = fields_by_key[key].label if key in fields_by_key else key
        items.append(
            ExplanationItem(
                feature_key=key,
                feature_label=label,
                contribution=round(float(value), 4),
                direction="increases_risk" if value > 0 else ("decreases_risk" if value < 0 else "neutral"),
            )
        )
    return items


def explain_with_shap(predict_proba_fn, background_df: pd.DataFrame, input_df: pd.DataFrame):
    """Attempt a local SHAP explanation. Returns (method, items) or None."""
    try:
        import shap

        explainer = shap.Explainer(predict_proba_fn, background_df)
        explanation = explainer(input_df)

        values = explanation.values
        # Binary classifiers explained via a proba-returning callable may
        # yield shape (n_samples, n_features, n_classes). We want the
        # positive ("at risk") class, conventionally the last one.
        if values.ndim == 3:
            values = values[0, :, -1]
        else:
            values = values[0]

        pairs = list(zip(input_df.columns.tolist(), values.tolist()))
        pairs.sort(key=lambda item: abs(item[1]), reverse=True)
        return "shap_local", _to_items(pairs), LOCAL_EXPLANATION_NOTE
    except Exception:  # noqa: BLE001 - any SHAP failure should gracefully fall back
        logger.exception("SHAP local explanation failed; falling back to global importance.")
        return None


def explain_with_global_importance(model, feature_names: list[str]):
    estimator = model
    if hasattr(model, "named_steps"):
        estimator = list(model.named_steps.values())[-1]

    importances = None
    if hasattr(estimator, "feature_importances_"):
        importances = np.asarray(estimator.feature_importances_, dtype=float)
    elif hasattr(estimator, "coef_"):
        coef = np.asarray(estimator.coef_, dtype=float)
        importances = np.abs(coef[0]) if coef.ndim > 1 else np.abs(coef)

    if importances is None or len(importances) != len(feature_names):
        return None

    pairs = list(zip(feature_names, importances.tolist()))
    pairs.sort(key=lambda item: abs(item[1]), reverse=True)
    return "global_importance", _to_items(pairs), GLOBAL_IMPORTANCE_NOTE


def build_explanation(
    model,
    predict_proba_fn,
    input_df: pd.DataFrame,
    background_df: pd.DataFrame | None,
):
    """Return (method, items, note) using the best available technique."""
    if background_df is not None and len(background_df) > 0:
        result = explain_with_shap(predict_proba_fn, background_df, input_df)
        if result is not None:
            return result

    fallback = explain_with_global_importance(model, input_df.columns.tolist())
    if fallback is not None:
        return fallback

    return "unavailable", [], (
        "No explanation method is currently available for this model. Add a "
        "background sample to enable SHAP, or use a model exposing "
        "feature_importances_/coef_."
    )
