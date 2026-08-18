from app.ml.types import ExplanationItem, PredictionBundle, TargetExplanation, TargetPrediction
from app.services import assessment_service
from tests.fakes import FakeResult, FakeSupabase


def _sample_bundle():
    return PredictionBundle(
        mode="real",
        targets=[
            TargetPrediction(
                target="stunting",
                predicted_label="at_risk",
                probability=0.71,
                decision_threshold=0.5,
                model_version="car-mics6-stunting-rf-v1",
                algorithm="RandomForestClassifier",
            ),
            TargetPrediction(
                target="underweight",
                predicted_label="not_at_risk",
                probability=0.22,
                decision_threshold=0.275,
                model_version="car-mics6-underweight-xgb-v1",
                algorithm="XGBClassifier",
            ),
        ],
        explanations=[
            TargetExplanation(
                target="stunting",
                method="shap_local",
                items=[ExplanationItem("windex5", "Household wealth quintile", 0.4, "increases_risk")],
                note="local",
            ),
            TargetExplanation(target="underweight", method="shap_local", items=[], note="local"),
        ],
    )


def test_ensure_model_version_creates_when_missing():
    fake = FakeSupabase()
    fake.queue("model_versions", FakeResult(data=[]))  # select finds nothing
    fake.queue("model_versions", FakeResult(data=[{"id": "mv-1"}]))  # insert returns new row

    bundle = _sample_bundle()
    version_id = assessment_service.ensure_model_version(fake, bundle.targets[0], bundle.mode)
    assert version_id == "mv-1"


def test_ensure_model_version_reuses_existing():
    fake = FakeSupabase()
    fake.queue("model_versions", FakeResult(data=[{"id": "mv-existing"}]))

    bundle = _sample_bundle()
    version_id = assessment_service.ensure_model_version(fake, bundle.targets[0], bundle.mode)
    assert version_id == "mv-existing"


def test_create_assessment_writes_predictions_and_explanations():
    fake = FakeSupabase()
    fake.queue("assessments", FakeResult(data=[{"id": "assessment-1"}]))
    # ensure_model_version is called once per target (stunting, underweight)
    fake.queue("model_versions", FakeResult(data=[{"id": "mv-stunting"}]))
    fake.queue("model_versions", FakeResult(data=[{"id": "mv-underweight"}]))
    fake.queue("assessment_predictions", FakeResult(data=[]))
    fake.queue("prediction_explanations", FakeResult(data=[]))

    assessment_id = assessment_service.create_assessment(
        fake,
        child_id="child-1",
        performed_by="user-1",
        input_data={"CAGE": 24},
        bundle=_sample_bundle(),
    )

    assert assessment_id == "assessment-1"
    assert ("table", "assessment_predictions") in fake.calls
    assert ("table", "prediction_explanations") in fake.calls


def test_shape_predictions_keys_by_target():
    rows = [
        {
            "target": "stunting",
            "predicted_label": "at_risk",
            "probability": 0.6,
            "decision_threshold": 0.5,
            "model_versions": {"version": "car-mics6-stunting-rf-v1", "mode": "real", "algorithm": "RandomForestClassifier"},
        },
        {
            "target": "underweight",
            "predicted_label": "not_at_risk",
            "probability": 0.1,
            "decision_threshold": 0.275,
            "model_versions": {"version": "car-mics6-underweight-xgb-v1", "mode": "real", "algorithm": "XGBClassifier"},
        },
    ]
    shaped = assessment_service._shape_predictions(rows)
    assert shaped["stunting"]["predictedLabel"] == "at_risk"
    assert shaped["stunting"]["modelVersion"] == "car-mics6-stunting-rf-v1"
    assert shaped["underweight"]["probability"] == 0.1
    assert shaped["underweight"]["decisionThreshold"] == 0.275


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
                        {
                            "target": "stunting",
                            "predicted_label": "not_at_risk",
                            "probability": 0.2,
                            "decision_threshold": 0.5,
                            "model_versions": {"version": "v1", "mode": "real", "algorithm": "RandomForestClassifier"},
                        }
                    ],
                }
            ]
        ),
    )
    history = assessment_service.get_child_history(fake, "child-1")
    assert len(history) == 1
    assert history[0]["predictions"]["stunting"]["predictedLabel"] == "not_at_risk"
