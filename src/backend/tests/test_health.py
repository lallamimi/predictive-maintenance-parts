import pytest


@pytest.mark.django_db
def test_health_check_ok(api_client):
    response = api_client.get("/api/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["checks"]["database"] is True
