import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from inventory.models import Fournisseur, PieceRechange

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def technicien(db):
    return User.objects.create_user(username="tech1", password="motdepasse123", role="technicien")


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(username="admin1", password="motdepasse123", role="admin")


@pytest.fixture
def auth_client(api_client, technicien):
    api_client.force_authenticate(user=technicien)
    return api_client


@pytest.fixture
def fournisseur(db):
    return Fournisseur.objects.create(nom="Fournisseur Test", fiabilite_score=0.9, delai_moyen_livraison_jours=5)


@pytest.fixture
def piece(db, fournisseur):
    return PieceRechange.objects.create(
        code_panne_associe="TWF",
        nom="Piece Test",
        categorie="usure",
        prix_unitaire=100.0,
        fournisseur=fournisseur,
        stock_actuel=50,
        seuil_reapprovisionnement=10,
    )
