"""Tests against the actual trained artifacts.

These exercise the real `stunting_model.pkl` / `underweight_model.pkl`
directly (not a mock), verifying the integration assumptions documented in
docs/MODEL_INTEGRATION.md: feature order, classes_, decision thresholds,
correct string->float coercion for categorical codes, and that SHAP
explanations can be produced.
"""
from app.config import Config
from app.ml.feature_schema import RAW_FEATURE_ORDER
from app.ml.real_provider import RealModelProvider
from tests.conftest import VALID_SCREENING_INPUT


def _provider():
    return RealModelProvider(Config())


def test_real_provider_loads_both_artifacts():
    provider = _provider()
    assert set(provider.targets.keys()) == {"stunting", "underweight"}


def test_real_provider_uses_verified_positive_class_and_thresholds():
    provider = _provider()
    assert provider.targets["stunting"].decision_threshold == 0.5
    assert provider.targets["underweight"].decision_threshold == 0.275
    assert provider.targets["stunting"].algorithm == "RandomForestClassifier"
    assert provider.targets["underweight"].algorithm == "XGBClassifier"


def test_real_provider_predicts_both_targets():
    # VALID_SCREENING_INPUT uses string category codes (e.g. "1.0"), exactly
    # as they arrive from the validated API payload / HTML form values.
    provider = _provider()
    bundle = provider.predict(VALID_SCREENING_INPUT)

    assert bundle.mode == "real"
    targets = {t.target: t for t in bundle.targets}
    assert set(targets.keys()) == {"stunting", "underweight"}

    for target, prediction in targets.items():
        assert prediction.predicted_label in ("at_risk", "not_at_risk")
        assert prediction.probability is not None
        assert 0.0 <= prediction.probability <= 1.0
        assert prediction.decision_threshold == provider.targets[target].decision_threshold


def test_string_and_float_category_codes_produce_identical_predictions():
    """Regression test for a real bug caught during integration: the fitted
    OneHotEncoder's categories are float64, so string codes ("1.0") MUST be
    coerced to float before reaching the pipeline, or handle_unknown="ignore"
    silently zeroes the feature instead of raising an error."""
    provider = _provider()
    string_input = dict(VALID_SCREENING_INPUT)
    float_input = {k: (float(v) if k != "CAGE" else v) for k, v in VALID_SCREENING_INPUT.items()}

    bundle_from_strings = provider.predict(string_input)
    bundle_from_floats = provider.predict(float_input)

    for a, b in zip(bundle_from_strings.targets, bundle_from_floats.targets):
        assert a.probability == b.probability


def test_real_provider_produces_local_shap_explanations():
    provider = _provider()
    bundle = provider.predict(VALID_SCREENING_INPUT)

    for explanation in bundle.explanations:
        assert explanation.method == "shap_local"
        assert len(explanation.items) > 0
        # Every explained feature must be one of the real raw predictors.
        for item in explanation.items:
            assert item.feature_key in RAW_FEATURE_ORDER


def test_real_provider_rejects_missing_artifact(tmp_path):
    from app.ml.real_provider import ModelNotAvailableError

    cfg = Config()
    cfg.STUNTING_MODEL_PATH = str(tmp_path / "does_not_exist.pkl")

    try:
        RealModelProvider(cfg)
        assert False, "expected ModelNotAvailableError"
    except ModelNotAvailableError:
        pass
