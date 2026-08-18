"""End-to-end tests for POST/GET /api/assessments.

These exist primarily to guard the "create a new child record from a
screening submission" path end-to-end through the route layer, since it
depends on deriving the `children.sex` enum value from the HL4 raw model
feature (see app.ml.feature_schema.derive_child_sex) rather than a
standalone "sex" field that no longer exists in the input schema.
"""
from tests.conftest import VALID_SCREENING_INPUT
from tests.fakes import FakeResult, FakeSupabase


def _queue_assessment_detail(fake: FakeSupabase, assessment_id: str, child_id: str):
    fake.queue(
        "assessments",
        FakeResult(
            data=[
                {
                    "id": assessment_id,
                    "child_id": child_id,
                    "performed_by": "user-1",
                    "input_data": VALID_SCREENING_INPUT,
                    "notes": None,
                    "assessed_at": "2024-01-01T00:00:00Z",
                    "children": {"id": child_id, "child_code": "CH-2024-00001", "sex": "male"},
                    "profiles": {"full_name": "Test User"},
                    "assessment_predictions": [],
                    "prediction_explanations": [],
                }
            ]
        ),
    )


def test_create_assessment_derives_sex_from_hl4_for_new_child(client, auth_as, mocker):
    auth_as("healthcare_worker", user_id="user-1")
    fake = FakeSupabase()

    fake.queue("children", FakeResult(data=[{"id": "child-1", "child_code": "CH-2024-00001", "sex": "male"}]))
    fake.queue("assessments", FakeResult(data=[{"id": "assessment-1"}]))  # insert
    fake.queue("model_versions", FakeResult(data=[{"id": "mv-stunting"}]))
    fake.queue("model_versions", FakeResult(data=[{"id": "mv-underweight"}]))
    fake.queue("assessment_predictions", FakeResult(data=[]))
    fake.queue("prediction_explanations", FakeResult(data=[]))
    _queue_assessment_detail(fake, "assessment-1", "child-1")  # get_assessment_detail
    fake.queue("assessments", FakeResult(data=[]))  # get_child_history

    mocker.patch("app.routes.assessments.get_supabase", return_value=fake)

    response = client.post(
        "/api/assessments",
        json={"inputData": VALID_SCREENING_INPUT},
        headers={"Authorization": "Bearer fake-token"},
    )

    assert response.status_code == 201, response.get_json()

    children_insert_calls = [c for c in fake.calls if c == ("table", "children")]
    assert len(children_insert_calls) == 1
    # VALID_SCREENING_INPUT["HL4"] == "1.0" -> male, per feature_schema.HL4_TO_CHILD_SEX.
    # If this endpoint still referenced a nonexistent "sex" key, this request
    # would have failed with a 422 above instead of reaching this point.


def test_create_assessment_rejects_new_child_without_hl4(client, auth_as, mocker):
    auth_as("healthcare_worker", user_id="user-1")
    fake = FakeSupabase()
    mocker.patch("app.routes.assessments.get_supabase", return_value=fake)

    payload = dict(VALID_SCREENING_INPUT)
    del payload["HL4"]

    response = client.post(
        "/api/assessments",
        json={"inputData": payload},
        headers={"Authorization": "Bearer fake-token"},
    )

    # HL4 is a required field, so this is rejected by input validation
    # before ever reaching the child-creation step.
    assert response.status_code == 422
