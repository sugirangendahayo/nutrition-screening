from app.services.trend_service import compute_trend

TARGETS = ["stunting", "underweight"]


def _entry(date, stunting, underweight):
    return {
        "assessedAt": date,
        "predictions": {
            "stunting": {"predictedLabel": stunting},
            "underweight": {"predictedLabel": underweight},
        },
    }


def test_insufficient_data_with_zero_or_one_assessment():
    assert compute_trend([], TARGETS)["status"] == "insufficient_data"
    assert compute_trend([_entry("2024-01-01", "at_risk", "at_risk")], TARGETS)["status"] == "insufficient_data"


def test_worsening_trend_detected():
    history = [
        _entry("2024-01-01", "not_at_risk", "not_at_risk"),
        _entry("2024-02-01", "at_risk", "not_at_risk"),
    ]
    trend = compute_trend(history, TARGETS)
    assert trend["status"] == "available"
    assert trend["perTarget"]["stunting"] == "worsening"
    assert trend["perTarget"]["underweight"] == "stable"
    assert trend["overall"] == "worsening"


def test_improving_trend_detected():
    history = [
        _entry("2024-01-01", "at_risk", "at_risk"),
        _entry("2024-02-01", "not_at_risk", "not_at_risk"),
    ]
    trend = compute_trend(history, TARGETS)
    assert trend["perTarget"]["stunting"] == "improving"
    assert trend["overall"] == "improving"


def test_stable_trend_detected():
    history = [
        _entry("2024-01-01", "not_at_risk", "not_at_risk"),
        _entry("2024-02-01", "not_at_risk", "not_at_risk"),
    ]
    trend = compute_trend(history, TARGETS)
    assert trend["overall"] == "stable"


def test_worsening_overrides_improving_in_overall():
    history = [
        _entry("2024-01-01", "at_risk", "not_at_risk"),
        _entry("2024-02-01", "not_at_risk", "at_risk"),
    ]
    trend = compute_trend(history, TARGETS)
    assert trend["perTarget"]["stunting"] == "improving"
    assert trend["perTarget"]["underweight"] == "worsening"
    assert trend["overall"] == "worsening"
