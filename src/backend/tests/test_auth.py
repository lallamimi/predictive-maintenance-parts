import pytest


@pytest.mark.django_db
def test_register_returns_tokens(api_client):
    response = api_client.post(
        "/api/auth/register/",
        {"username": "nouveluser", "email": "n@example.com", "password": "motdepasse123", "role": "technicien"},
        format="json",
    )
    assert response.status_code == 201
    data = response.json()
    assert "access" in data and "refresh" in data
    assert data["user"]["username"] == "nouveluser"


@pytest.mark.django_db
def test_register_password_too_short_is_rejected(api_client):
    response = api_client.post(
        "/api/auth/register/",
        {"username": "u2", "email": "u2@example.com", "password": "abc", "role": "technicien"},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_with_valid_credentials(api_client, technicien):
    response = api_client.post(
        "/api/auth/login/", {"username": "tech1", "password": "motdepasse123"}, format="json"
    )
    assert response.status_code == 200
    assert "access" in response.json()


@pytest.mark.django_db
def test_login_with_wrong_password_is_rejected(api_client, technicien):
    response = api_client.post("/api/auth/login/", {"username": "tech1", "password": "mauvais"}, format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_profile_requires_authentication(api_client):
    response = api_client.get("/api/auth/profile/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_profile_returns_current_user(auth_client):
    response = auth_client.get("/api/auth/profile/")
    assert response.status_code == 200
    assert response.json()["username"] == "tech1"
