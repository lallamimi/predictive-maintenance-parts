"""
Tests de l'API exposant les modeles IA (competence C12).

Necessitent que les modeles entraines existent (data/processed/models/*.pkl) -
executer au prealable la chaine complete : collecte -> nettoyage -> entrainement
(voir README.md ou docs/ci_cd.md). C'est la meme chaine que celle jouee par la CI.
"""

import pytest

from ml_api.model_registry import MODELS_DIR

MODELS_AVAILABLE = (MODELS_DIR / "failure_model.pkl").exists() and (MODELS_DIR / "demand_model.pkl").exists()

pytestmark = pytest.mark.skipif(
    not MODELS_AVAILABLE,
    reason="Modeles non entraines : executez src/ml/train_failure_model.py et train_demand_model.py",
)

VALID_FAILURE_PAYLOAD = {
    "temperature_air_k": 300,
    "temperature_process_k": 310,
    "vitesse_rotation_rpm": 1500,
    "couple_nm": 40,
    "usure_outil_min": 100,
    "type_produit": "M",
}


@pytest.mark.django_db
def test_predict_failure_requires_authentication(api_client):
    response = api_client.post("/api/ml/predict-failure/", VALID_FAILURE_PAYLOAD, format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_predict_failure_with_valid_input(auth_client):
    response = auth_client.post("/api/ml/predict-failure/", VALID_FAILURE_PAYLOAD, format="json")
    assert response.status_code == 200
    data = response.json()
    assert "panne_predite" in data
    assert 0 <= data["probabilite"] <= 1
    assert data["niveau_risque"] in {"faible", "moyen", "eleve"}


@pytest.mark.django_db
def test_predict_failure_rejects_out_of_range_input(auth_client):
    payload = {**VALID_FAILURE_PAYLOAD, "temperature_air_k": 9999}
    response = auth_client.post("/api/ml/predict-failure/", payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_predict_failure_rejects_missing_field(auth_client):
    payload = dict(VALID_FAILURE_PAYLOAD)
    del payload["couple_nm"]
    response = auth_client.post("/api/ml/predict-failure/", payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_predict_failure_logs_prediction(auth_client):
    from ml_api.models import ModelPredictionLog

    count_before = ModelPredictionLog.objects.count()
    auth_client.post("/api/ml/predict-failure/", VALID_FAILURE_PAYLOAD, format="json")
    assert ModelPredictionLog.objects.count() == count_before + 1


@pytest.mark.django_db
def test_predict_demand_with_unknown_piece_returns_404(auth_client):
    response = auth_client.post("/api/ml/predict-demand/", {"piece_id": 999999}, format="json")
    assert response.status_code == 404


@pytest.mark.django_db
def test_predict_demand_without_history_returns_zero(auth_client, piece):
    response = auth_client.post("/api/ml/predict-demand/", {"piece_id": piece.id}, format="json")
    assert response.status_code == 200
    data = response.json()
    assert data["demande_prevue"] == 0.0
    assert "avertissement" in data


@pytest.mark.django_db
def test_monitoring_endpoint_reports_calls(auth_client):
    auth_client.post("/api/ml/predict-failure/", VALID_FAILURE_PAYLOAD, format="json")
    response = auth_client.get("/api/ml/monitoring/")
    assert response.status_code == 200
    data = response.json()
    assert data["par_endpoint"]["predict-failure"]["nb_appels"] >= 1
