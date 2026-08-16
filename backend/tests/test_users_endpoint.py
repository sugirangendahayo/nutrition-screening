from unittest.mock import MagicMock

from tests.fakes import FakeResult, FakeSupabase


def test_list_users_requires_admin(client, auth_as):
    auth_as("healthcare_worker")
    response = client.get("/api/users", headers={"Authorization": "Bearer fake"})
    assert response.status_code == 403


def test_create_user_requires_admin(client, auth_as):
    auth_as("nutrition_officer")
    response = client.post(
        "/api/users",
        json={"email": "a@a.com", "fullName": "A", "role": "healthcare_worker"},
        headers={"Authorization": "Bearer fake"},
    )
    assert response.status_code == 403


def test_create_user_rejects_invalid_role(client, auth_as, mocker):
    auth_as("administrator")
    fake = FakeSupabase()
    mocker.patch("app.routes.users.get_supabase", return_value=fake)

    response = client.post(
        "/api/users",
        json={"email": "a@a.com", "fullName": "A", "role": "not-a-role"},
        headers={"Authorization": "Bearer fake"},
    )
    assert response.status_code == 422


def test_create_user_succeeds_for_admin(client, auth_as, mocker):
    auth_as("administrator")
    fake = FakeSupabase()
    fake.queue("profiles", FakeResult(data=[{"id": "new-user-id"}]))
    fake.auth = MagicMock()
    fake.auth.admin.create_user.return_value = MagicMock(user=MagicMock(id="new-user-id"))
    mocker.patch("app.routes.users.get_supabase", return_value=fake)

    response = client.post(
        "/api/users",
        json={"email": "new@example.com", "fullName": "New User", "role": "healthcare_worker"},
        headers={"Authorization": "Bearer fake"},
    )
    body = response.get_json()
    assert response.status_code == 201
    assert body["data"]["email"] == "new@example.com"
    assert "temporaryPassword" in body["data"]
