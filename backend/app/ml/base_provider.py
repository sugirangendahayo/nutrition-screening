"""Abstract interface every prediction backend must implement.

    ModelProvider
        |
        +-- MockModelProvider    (development, no trained artifact required)
        |
        +-- RealModelProvider    (loads the trained .pkl / .joblib artifact)

The rest of the application (routes, services) only ever depends on this
interface, so switching from mock to real predictions - or upgrading the
real model later - never requires touching the API or frontend.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.ml.types import PredictionBundle


class ModelProvider(ABC):
    mode: str
    version: str

    @abstractmethod
    def predict(self, features: dict) -> PredictionBundle:
        """Run inference for both targets and produce an explanation.

        `features` is a dict of already-validated values keyed by the
        feature schema's field keys (see `app.ml.feature_schema`).
        """
        raise NotImplementedError

    @abstractmethod
    def describe(self) -> dict:
        """Metadata surfaced by GET /api/model/info."""
        raise NotImplementedError
