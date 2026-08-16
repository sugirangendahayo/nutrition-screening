from app.ml.types import ExplanationItem, PredictionBundle, TargetExplanation, TargetPrediction
from app.services import assessment_service
from tests.fakes import FakeResult, FakeSupabase


def _sample_bundle():
    return PredictionBundle(
        mode="mock",
        model_version="dev-mock-1.0",
        targets=[
            TargetPrediction(target="stunting", predicted_label="at_risk", probability=0.71),
            TargetPrediction(target="underweight", predicted_label="not_at_risk", probability=0.22),
        ],
        explanations=[
            TargetExplanation(
                target="stunting",
                method="development_mock",
                items=[ExplanationItem("weight_kg", "Weight", 0.4, "increases_risk")],
                note="dev",
            ),
            TargetExplanation(target="underweight", method="development_mock", items=[], note="dev"),
        ],
    )


def test_ensure_model_version_creates_when_missing():
    fake = FakeSupabase()
    fake.queue("model_versions", FakeResult(data=[]))  # select finds nothing
    fake.queue("model_versions", FakeResult(data=[{"id": "mv-1"}]))  # insert returns new row

    version_id = assessment_service.ensure_model_version(fake, _sample_bundle())
    assert version_id == "mv-1"


def test_ensure_model_version_reuses_existing():
    fake = FakeSupabase()
    fake.queue("model_versions", FakeResult(data=[{"id": "mv-existing"}]))

    version_id = assessment_service.ensure_model_version(fake, _sample_bundle())
    assert version_id == "mv-existing"


def test_create_assessment_writes_predictions_and_explanations():
    fake = FakeSupabase()
    fake.queue("model_versions", FakeResult(data=[{"id": "mv-1"}]))
    fake.queue("assessments", FakeResult(data=[{"id": "assessment-1"}]))
    fake.queue("assessment_predictions", FakeResult(data=[]))
    fake.queue("prediction_explanations", FakeResult(data=[]))

    assessment_id = assessment_service.create_assessment(
        fake,
        child_id="child-1",
        performed_by="user-1",
        input_data={"weight_kg": 9.5},
        bundle=_sample_bundle(),
    )

    assert assessment_id == "assessment-1"
    assert ("table", "assessment_predictions") in fake.calls
    assert ("table", "prediction_explanations") in fake.calls


def test_shape_predictions_keys_by_target():
    rows = [
        {"target": "stunting", "predicted_label": "at_risk", "probability": 0.6},
        {"target": "underweight", "predicted_label": "not_at_risk", "probability": 0.1},
    ]
    shaped = assessment_service._shape_predictions(rows)
    assert shaped["stunting"]["predictedLabel"] == "at_risk"
    assert shaped["underweight"]["probability"] == 0.1


def test_get_child_history_shapes_rows():
    fake = FakeSupabase()
    fake.queue(
        "assessments",
        FakeResult(
            data=[
                {
                    "id": "a1",
                    "assessed_at": "2024-01-01T00:00:00Z",
                    "assessment_predictions": [
                        {"target": "stunting", "predicted_label": "not_at_risk", "probability": 0.2}
                    ],
                }
            ]
        ),
    )
    history = assessment_service.get_child_history(fake, "child-1")
    assert len(history) == 1
    assert history[0]["predictions"]["stunting"]["predictedLabel"] == "not_at_risk"
