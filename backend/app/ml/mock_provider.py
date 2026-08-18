"""Development/mock prediction provider.

WHY THIS EXISTS
----------------
The real trained model artifact is not available yet. This provider lets
the entire application - form, validation, prediction, explanation,
storage, history, trends, reports - be built and tested end-to-end
without waiting for it.

WHAT IT IS NOT
---------------
This is NOT a clinical model. It does not implement WHO growth
standards, z-scores, or any validated nutrition-science formula. It is a
small, deterministic, seeded linear toy function of the submitted form
values, used purely so that different inputs produce different (but
reproducible) outputs during development and demos.

Every response produced by this provider is tagged `mode: "mock"` and
the explanation method is tagged `development_mock` so the frontend can
- and must - display a clear "Development Mode" indicator and avoid
presenting the output as a real ML result.
"""
from __future__ import annotations

import hashlib
import math

from app.ml.base_provider import ModelProvider
from app.ml.feature_schema import FEATURE_FIELDS, PREDICTION_TARGETS, InputType, get_fields_by_key
from app.ml.types import ExplanationItem, PredictionBundle, TargetExplanation, TargetPrediction

_DEFAULT_NUMERIC_RANGE = (0.0, 100.0)


def _stable_weight(seed_text: str) -> float:
    """Deterministic pseudo-random value in [-1, 1] derived from a string."""
    digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    as_int = int(digest[:8], 16)
    return (as_int / 0xFFFFFFFF) * 2 - 1


def _normalize_value(field, raw_value) -> float:
    if field.input_type == InputType.NUMBER:
        lo, hi = field.min, field.max
        if lo is None or hi is None or hi == lo:
            lo, hi = _DEFAULT_NUMERIC_RANGE
        value = float(raw_value)
        return max(0.0, min(1.0, (value - lo) / (hi - lo)))

    options = [opt.value for opt in field.options]
    if not options:
        return 0.0
    try:
        index = options.index(raw_value)
    except ValueError:
        return 0.0
    if len(options) == 1:
        return 0.0
    return index / (len(options) - 1)


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


class MockModelProvider(ModelProvider):
    mode = "mock"

    def __init__(self, version: str = "dev-mock-1.0"):
        self.version = version
        self._fields_by_key = get_fields_by_key()

    def _score_target(self, target: str, features: dict) -> tuple[float, list[ExplanationItem]]:
        terms: list[tuple[str, float]] = []
        total = 0.0

        for field in FEATURE_FIELDS:
            if field.key not in features:
                continue
            weight = _stable_weight(f"{target}:{field.key}")
            normalized = _normalize_value(field, features[field.key])
            contribution = weight * normalized
            total += contribution
            terms.append((field.key, contribution))

        bias = _stable_weight(f"{target}:bias") * 0.3
        probability = _sigmoid(total + bias)

        terms.sort(key=lambda item: abs(item[1]), reverse=True)
        items = [
            ExplanationItem(
                feature_key=key,
                feature_label=self._fields_by_key[key].label,
                contribution=round(value, 4),
                direction="increases_risk" if value > 0 else ("decreases_risk" if value < 0 else "neutral"),
            )
            for key, value in terms[:8]
        ]
        return probability, items

    def predict(self, features: dict) -> PredictionBundle:
        targets: list[TargetPrediction] = []
        explanations: list[TargetExplanation] = []

        for target in PREDICTION_TARGETS:
            probability, items = self._score_target(target, features)
            threshold = 0.5
            predicted_label = "at_risk" if probability >= threshold else "not_at_risk"
            targets.append(
                TargetPrediction(
                    target=target,
                    predicted_label=predicted_label,
                    probability=round(probability, 4),
                    decision_threshold=threshold,
                    model_version=self.version,
                    algorithm="development-mock (deterministic seeded function)",
                )
            )
            explanations.append(
                TargetExplanation(
                    target=target,
                    method="development_mock",
                    items=items,
                    note=(
                        "Development mode: this explanation reflects a placeholder "
                        "statistical function used for workflow testing only, not the "
                        "trained model or any validated nutrition-science formula."
                    ),
                )
            )

        return PredictionBundle(
            mode=self.mode,
            targets=targets,
            explanations=explanations,
        )

    def describe(self) -> dict:
        return {
            "mode": self.mode,
            "targets": {
                target: {
                    "version": self.version,
                    "algorithm": "development-mock (deterministic seeded function)",
                    "decisionThreshold": 0.5,
                }
                for target in PREDICTION_TARGETS
            },
            "explanationMethod": "development_mock",
            "note": (
                "No trained model artifact is currently loaded. Predictions are "
                "generated by a development placeholder and must not be used for "
                "real nutrition screening decisions."
            ),
        }
