from app.services import report_service
from tests.fakes import FakeResult, FakeSupabase


def test_list_reports_shapes_rows():
    fake = FakeSupabase()
    fake.queue(
        "reports",
        FakeResult(
            data=[
                {
                    "id": "r1",
                    "assessment_id": "a1",
                    "child_id": "c1",
                    "report_type": "assessment_summary",
                    "created_at": "2024-01-01T00:00:00Z",
                    "children": {"child_code": "CH-2024-00001"},
                    "assessments": {"assessed_at": "2024-01-01T00:00:00Z"},
                }
            ]
        ),
    )
    reports = report_service.list_reports(fake)
    assert reports[0]["childCode"] == "CH-2024-00001"
    assert reports[0]["assessmentId"] == "a1"


def test_build_assessment_report_returns_none_when_missing():
    fake = FakeSupabase()
    fake.queue("assessments", FakeResult(data=[]))
    report = report_service.build_assessment_report(fake, "missing-id")
    assert report is None


def test_build_assessment_report_summarizes_input():
    fake = FakeSupabase()
    fake.queue(
        "assessments",
        FakeResult(
            data=[
                {
                    "id": "a1",
                    "child_id": "c1",
                    "performed_by": "u1",
                    "input_data": {"CAGE": 24, "HL4": "1.0"},
                    "notes": None,
                    "assessed_at": "2024-01-01T00:00:00Z",
                    "children": {"id": "c1", "child_code": "CH-2024-00001", "sex": "male"},
                    "profiles": {"full_name": "Jane Doe"},
                    "assessment_predictions": [],
                    "prediction_explanations": [],
                }
            ]
        ),
    )
    fake.queue("assessments", FakeResult(data=[]))  # get_child_history

    report = report_service.build_assessment_report(fake, "a1")
    labels = {item["label"] for item in report["inputSummary"]}
    assert "Child age" in labels
    assert "Sex" in labels
    assert report["assessment"]["performedByName"] == "Jane Doe"
    assert report["trend"]["status"] == "insufficient_data"
