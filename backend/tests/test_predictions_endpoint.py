from tests.conftest import VALID_SCREENING_INPUT


def test_predictions_requires_authentication(client):
    response = client.post("/api/predictions", json={"inputData": VALID_SCREENING_INPUT})
    assert response.status_code == 401


def test_predictions_rejects_unauthorized_role(client, auth_as):
    auth_as("researcher")
    response = client.post(
        "/api/predictions",
        json={"inputData": VALID_SCREENING_INPUT},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 403


def test_predictions_returns_both_targets_for_valid_input(client, auth_as):
    auth_as("healthcare_worker")
    response = client.post(
        "/api/predictions",
        json={"inputData": VALID_SCREENING_INPUT},
        headers={"Authorization": "Bearer fake-token"},
    )
    body = response.get_json()
    assert response.status_code == 200
    assert body["success"] is True
    targets = {t["target"] for t in body["data"]["targets"]}
    assert targets == {"stunting", "underweight"}
    assert body["data"]["mode"] == "mock"


def test_predictions_rejects_invalid_input(client, auth_as):
    auth_as("healthcare_worker")
    bad_payload = dict(VALID_SCREENING_INPUT)
    del bad_payload["CAGE"]
    response = client.post(
        "/api/predictions",
        json={"inputData": bad_payload},
        headers={"Authorization": "Bearer fake-token"},
    )
    body = response.get_json()
    assert response.status_code == 422
    assert body["success"] is False
    assert "CAGE" in body["error"]["details"]
