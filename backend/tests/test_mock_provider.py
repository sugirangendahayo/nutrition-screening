from app.ml.mock_provider import MockModelProvider
from tests.conftest import VALID_SCREENING_INPUT


def test_predict_returns_both_targets():
    provider = MockModelProvider()
    bundle = provider.predict(VALID_SCREENING_INPUT)
    targets = {t.target for t in bundle.targets}
    assert targets == {"stunting", "underweight"}
    assert bundle.mode == "mock"


def test_probabilities_are_in_range():
    provider = MockModelProvider()
    bundle = provider.predict(VALID_SCREENING_INPUT)
    for target in bundle.targets:
        assert 0.0 <= target.probability <= 1.0
        assert target.predicted_label in ("at_risk", "not_at_risk")


def test_prediction_is_deterministic_for_same_input():
    provider = MockModelProvider()
    first = provider.predict(VALID_SCREENING_INPUT)
    second = provider.predict(VALID_SCREENING_INPUT)
    assert [t.probability for t in first.targets] == [t.probability for t in second.targets]


def test_explanation_is_clearly_marked_as_mock():
    provider = MockModelProvider()
    bundle = provider.predict(VALID_SCREENING_INPUT)
    for explanation in bundle.explanations:
        assert explanation.method == "development_mock"
        assert len(explanation.items) > 0
        assert "development" in explanation.note.lower()


def test_different_inputs_can_produce_different_scores():
    provider = MockModelProvider()
    low = dict(VALID_SCREENING_INPUT, weight_kg=5.0, height_cm=60.0, child_age_months=6)
    high = dict(VALID_SCREENING_INPUT, weight_kg=18.0, height_cm=110.0, child_age_months=55)
    bundle_low = provider.predict(low)
    bundle_high = provider.predict(high)
    assert bundle_low.to_dict() != bundle_high.to_dict()
