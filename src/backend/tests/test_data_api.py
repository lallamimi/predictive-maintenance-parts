import pytest


@pytest.mark.django_db
def test_pieces_list_requires_authentication(api_client):
    response = api_client.get("/api/data/pieces/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_pieces_list_returns_created_piece(auth_client, piece):
    response = auth_client.get("/api/data/pieces/")
    assert response.status_code == 200
    noms = [p["nom"] for p in response.json()["results"]]
    assert "Piece Test" in noms


@pytest.mark.django_db
def test_piece_sous_seuil_flag(auth_client, piece):
    response = auth_client.get("/api/data/pieces/")
    resultat = response.json()["results"][0]
    assert resultat["sous_le_seuil"] is False  # stock=50 > seuil=10


@pytest.mark.django_db
def test_pieces_sous_seuil_endpoint_filters_correctly(auth_client, fournisseur):
    from inventory.models import PieceRechange

    PieceRechange.objects.create(
        code_panne_associe="HDF",
        nom="Piece en rupture",
        categorie="refroidissement",
        prix_unitaire=50.0,
        fournisseur=fournisseur,
        stock_actuel=2,
        seuil_reapprovisionnement=10,
    )
    response = auth_client.get("/api/data/pieces/sous_seuil/")
    assert response.status_code == 200
    noms = [p["nom"] for p in response.json()]
    assert "Piece en rupture" in noms


@pytest.mark.django_db
def test_kpi_endpoint_returns_expected_keys(auth_client):
    response = auth_client.get("/api/data/interventions/kpi/")
    assert response.status_code == 200
    data = response.json()
    for key in ["nb_lectures_total", "nb_pannes", "taux_panne_pct", "nb_interventions", "cout_total_interventions"]:
        assert key in data
