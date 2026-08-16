from app.services.dashboard_service import get_dashboard_summary
from tests.fakes import FakeResult, FakeSupabase


def test_dashboard_summary_reports_no_data_when_empty():
    fake = FakeSupabase()
    fake.queue("children", FakeResult(data=[], count=0))
    fake.queue("assessments", FakeResult(data=[], count=0))
    fake.queue("assessment_predictions", FakeResult(data=[]))
    fake.queue("assessments", FakeResult(data=[]))  # recent list

    summary = get_dashboard_summary(fake)
    assert summary["hasData"] is False
    assert summary["childrenAssessed"] == 0
    assert summary["recentAssessments"] == []


def test_dashboard_summary_counts_at_risk_predictions():
    fake = FakeSupabase()
    fake.queue("children", FakeResult(data=[], count=3))
    fake.queue("assessments", FakeResult(data=[], count=2))
    fake.queue(
        "assessment_predictions",
        FakeResult(
            data=[
                {"target": "stunting", "predicted_label": "at_risk"},
                {"target": "stunting", "predicted_label": "not_at_risk"},
                {"target": "underweight", "predicted_label": "at_risk"},
            ]
        ),
    )
    fake.queue(
        "assessments",
        FakeResult(
            data=[
                {
                    "id": "a1",
                    "assessed_at": "2024-01-01T00:00:00Z",
                    "children": {"child_code": "CH-2024-00001"},
                    "assessment_predictions": [
                        {"target": "stunting", "predicted_label": "at_risk", "probability": 0.8}
                    ],
                }
            ]
        ),
    )

    summary = get_dashboard_summary(fake)
    assert summary["hasData"] is True
    assert summary["childrenAssessed"] == 3
    assert summary["assessmentsThisMonth"] == 2
    assert summary["stuntingAtRiskThisMonth"] == 1
    assert summary["underweightAtRiskThisMonth"] == 1
    assert summary["recentAssessments"][0]["childCode"] == "CH-2024-00001"
