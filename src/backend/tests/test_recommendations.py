import pytest


@pytest.mark.django_db
def test_recommendations_requires_authentication(api_client):
    response = api_client.get("/api/recommendations/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_recommendations_falls_back_without_groq_key(auth_client, settings):
    settings.GROQ_API_KEY = ""  # simule l'absence de cle (cas par defaut de ce projet)
    response = auth_client.get("/api/recommendations/")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "repli_regles"
    assert "recommandation" in data and len(data["recommandation"]) > 0
