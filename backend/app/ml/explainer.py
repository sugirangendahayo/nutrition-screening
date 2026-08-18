"""Explanation generation for the trained stunting/underweight pipelines.

Both supplied artifacts are `sklearn.pipeline.Pipeline(preprocessor, classifier)`
where `classifier` is a tree ensemble (RandomForestClassifier or
XGBClassifier) and `preprocessor` is a ColumnTransformer that one-hot
encodes 19 of the 20 raw predictors, expanding them into 73 transformed
columns (verified by direct inspection - see docs/MODEL_INTEGRATION.md).

This module:
1. Prefers a LOCAL, per-prediction explanation via `shap.TreeExplainer`,
   which is exact and fast for tree ensembles and requires no background
   sample.
2. Aggregates the transformed (one-hot) SHAP values back to their
   original raw predictor (e.g. all `cat__windex5_*` columns collapse
   into one `windex5` contribution) so the UI can show "windex5
   contributed X" instead of exposing one-hot internals to the user.
3. Falls back to the classifier's global `feature_importances_`
   (similarly aggregated) if SHAP cannot be computed, clearly labeled as
   general model importance rather than a per-child explanation.
"""
from __future__ import annotations

import logging

import numpy as np

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


def _raw_feature_groups(transformed_names, raw_keys: list[str]) -> dict[str, list[int]]:
    """Map each raw predictor to the indices of its transformed columns.

    Transformed names follow the ColumnTransformer convention observed in
    the artifacts: "num__<raw>" for the numeric feature, "cat__<raw>_<code>"
    for one-hot encoded categorical columns.
    """
    groups: dict[str, list[int]] = {key: [] for key in raw_keys}
    for idx, name in enumerate(transformed_names):
        prefix, _, rest = name.partition("__")
        matched = None
        if prefix == "num" and rest in groups:
            matched = rest
        elif prefix == "cat":
            for key in raw_keys:
                if rest == key or rest.startswith(f"{key}_"):
                    matched = key
                    break
        if matched:
            groups[matched].append(idx)
    return groups


def _aggregate_to_raw_features(transformed_names, values, raw_keys: list[str]) -> dict[str, float]:
    groups = _raw_feature_groups(transformed_names, raw_keys)
    return {key: float(sum(values[i] for i in idxs)) for key, idxs in groups.items() if idxs}


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


def explain_with_tree_shap(classifier, transformed_input, transformed_names, raw_keys, positive_index: int):
    """Local SHAP explanation via TreeExplainer. Returns (method, items, note) or None."""
    try:
        import shap

        explainer = shap.TreeExplainer(classifier)
        raw_shap = explainer.shap_values(transformed_input)

        if isinstance(raw_shap, list):
            # Some tree ensembles return one array per class.
            values = np.asarray(raw_shap[positive_index])[0]
        else:
            arr = np.asarray(raw_shap)
            # RandomForestClassifier (via shap 0.5x) -> shape (n, n_features, n_classes)
            # XGBClassifier binary -> shape (n, n_features), already for the positive class
            values = arr[0, :, positive_index] if arr.ndim == 3 else arr[0]

        aggregated = _aggregate_to_raw_features(transformed_names, values, raw_keys)
        pairs = sorted(aggregated.items(), key=lambda item: abs(item[1]), reverse=True)
        return "shap_local", _to_items(pairs), LOCAL_EXPLANATION_NOTE
    except Exception:  # noqa: BLE001 - any SHAP failure should gracefully fall back
        logger.exception("SHAP TreeExplainer failed; falling back to global importance.")
        return None


def explain_with_global_importance(classifier, transformed_names, raw_keys):
    importances = getattr(classifier, "feature_importances_", None)
    if importances is None:
        coef = getattr(classifier, "coef_", None)
        if coef is None:
            return None
        coef_arr = np.asarray(coef)
        importances = np.abs(coef_arr[0]) if coef_arr.ndim > 1 else np.abs(coef_arr)

    if len(importances) != len(transformed_names):
        return None

    aggregated = _aggregate_to_raw_features(transformed_names, importances, raw_keys)
    pairs = sorted(aggregated.items(), key=lambda item: abs(item[1]), reverse=True)
    return "global_importance", _to_items(pairs), GLOBAL_IMPORTANCE_NOTE


def build_explanation(classifier, transformed_input, transformed_names, raw_keys, positive_index: int):
    """Return (method, items, note) using the best available technique."""
    result = explain_with_tree_shap(classifier, transformed_input, transformed_names, raw_keys, positive_index)
    if result is not None:
        return result

    result = explain_with_global_importance(classifier, transformed_names, raw_keys)
    if result is not None:
        return result

    return "unavailable", [], (
        "No explanation method is currently available for this model."
    )
