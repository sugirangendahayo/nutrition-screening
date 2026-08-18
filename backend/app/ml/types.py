"""Shared data shapes returned by any ModelProvider implementation."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class TargetPrediction:
    target: str  # "stunting" | "underweight"
    predicted_label: str  # "at_risk" | "not_at_risk"
    probability: float | None  # probability of the "at_risk" class, 0-1
    decision_threshold: float  # probability cutoff used to derive predicted_label
    model_version: str
    algorithm: str

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "predictedLabel": self.predicted_label,
            "probability": self.probability,
            "decisionThreshold": self.decision_threshold,
            "modelVersion": self.model_version,
            "algorithm": self.algorithm,
        }


@dataclass
class ExplanationItem:
    feature_key: str
    feature_label: str
    contribution: float  # signed local contribution, or normalized global importance
    direction: str  # "increases_risk" | "decreases_risk" | "neutral"

    def to_dict(self) -> dict:
        return {
            "featureKey": self.feature_key,
            "featureLabel": self.feature_label,
            "contribution": self.contribution,
            "direction": self.direction,
        }


@dataclass
class TargetExplanation:
    target: str
    method: str  # "shap_local" | "global_importance" | "development_mock" | "unavailable"
    items: list[ExplanationItem] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "method": self.method,
            "items": [item.to_dict() for item in self.items],
            "note": self.note,
        }


@dataclass
class PredictionBundle:
    mode: str  # "mock" | "real"
    targets: list[TargetPrediction]
    explanations: list[TargetExplanation]
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "targets": [t.to_dict() for t in self.targets],
            "explanations": [e.to_dict() for e in self.explanations],
            "generatedAt": self.generated_at,
        }
