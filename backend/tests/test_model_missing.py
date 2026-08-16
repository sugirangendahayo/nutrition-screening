import pytest

from app import create_app
from app.config import Config
from tests.conftest import VALID_SCREENING_INPUT


@pytest.fixture
def production_app_without_model():
    cfg = Config()
    cfg.ML_MODEL_STATUS = "production"
    cfg.MODEL_MODE = "dual_model"
    cfg.STUNTING_MODEL_PATH = "models/does_not_exist_stunting.joblib"
    cfg.UNDERWEIGHT_MODEL_PATH = "models/does_not_exist_underweight.joblib"
    flask_app = create_app(cfg)
    flask_app.config.update(TESTING=True)
    return flask_app


def test_model_info_reports_unavailable(production_app_without_model, mocker):
    client = production_app_without_model.test_client()
    mocker.patch(
        "app.utils.auth.load_current_user",
        return_value={"id": "u1", "role": "administrator", "full_name": "Admin", "email": "a@a.com", "facility": None},
    )
    response = client.get("/api/model/info", headers={"Authorization": "Bearer fake"})
    body = response.get_json()
    assert response.status_code == 200
    assert body["data"]["available"] is False
    assert "not found" in body["data"]["error"].lower()


def test_predictions_endpoint_returns_503_when_model_missing(production_app_without_model, mocker):
    client = production_app_without_model.test_client()
    mocker.patch(
        "app.utils.auth.load_current_user",
        return_value={"id": "u1", "role": "healthcare_worker", "full_name": "HW", "email": "a@a.com", "facility": None},
    )
    response = client.post(
        "/api/predictions",
        json={"inputData": VALID_SCREENING_INPUT},
        headers={"Authorization": "Bearer fake"},
    )
    assert response.status_code == 503
