"""Selects the active ModelProvider based on application configuration."""
from __future__ import annotations

import logging

from app.ml.base_provider import ModelProvider
from app.ml.mock_provider import MockModelProvider
from app.ml.real_provider import ModelNotAvailableError, RealModelProvider

logger = logging.getLogger(__name__)

_provider: ModelProvider | None = None
_provider_error: str | None = None


def init_provider(config) -> None:
    """Called once at app startup to build the singleton provider."""
    global _provider, _provider_error
    _provider_error = None

    if config.ML_MODEL_STATUS == "production":
        try:
            _provider = RealModelProvider(config)
            logger.info(
                "Loaded real model providers: stunting=%s underweight=%s",
                config.STUNTING_MODEL_VERSION,
                config.UNDERWEIGHT_MODEL_VERSION,
            )
            return
        except ModelNotAvailableError as exc:
            _provider_error = str(exc)
            logger.error(
                "ML_MODEL_STATUS=production but the model(s) could not be loaded: %s", exc
            )
            _provider = None
            return

    _provider = MockModelProvider(version=config.MOCK_MODEL_VERSION)
    logger.warning(
        "Running with the DEVELOPMENT MOCK model provider. Predictions are not "
        "real ML results. Set ML_MODEL_STATUS=production with valid artifacts "
        "to use the trained models."
    )


def get_provider() -> ModelProvider | None:
    return _provider


def get_provider_error() -> str | None:
    return _provider_error
