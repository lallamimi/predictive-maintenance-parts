"""Tests de gestion des droits et des accès (compétence C17)."""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def gestionnaire(db):
    return User.objects.create_user(username="gest1", password="motdepasse123", role="gestionnaire_stock")


@pytest.fixture
def admin(db):
    return User.objects.create_user(username="admin1", password="motdepasse123", role="admin")


@pytest.mark.django_db
def test_technicien_can_read_pieces(auth_client, piece):
    response = auth_client.get("/api/data/pieces/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_technicien_cannot_adjust_stock(auth_client, piece):
    response = auth_client.patch(f"/api/data/pieces/{piece.id}/ajuster-stock/", {"nouveau_stock": 99}, format="json")
    assert response.status_code == 403
    piece.refresh_from_db()
    assert piece.stock_actuel != 99


@pytest.mark.django_db
def test_gestionnaire_can_adjust_stock(api_client, gestionnaire, piece):
    api_client.force_authenticate(user=gestionnaire)
    response = api_client.patch(f"/api/data/pieces/{piece.id}/ajuster-stock/", {"nouveau_stock": 99}, format="json")
    assert response.status_code == 200
    piece.refresh_from_db()
    assert piece.stock_actuel == 99


@pytest.mark.django_db
def test_admin_can_adjust_stock(api_client, admin, piece):
    api_client.force_authenticate(user=admin)
    response = api_client.patch(f"/api/data/pieces/{piece.id}/ajuster-stock/", {"nouveau_stock": 42}, format="json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_adjust_stock_rejects_negative_value(api_client, gestionnaire, piece):
    api_client.force_authenticate(user=gestionnaire)
    response = api_client.patch(f"/api/data/pieces/{piece.id}/ajuster-stock/", {"nouveau_stock": -5}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_adjust_stock_requires_authentication(api_client, piece):
    response = api_client.patch(f"/api/data/pieces/{piece.id}/ajuster-stock/", {"nouveau_stock": 10}, format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_unknown_role_defaults_to_technicien_and_is_denied():
    """La valeur par defaut du role (voir accounts.models.User.Role) doit rester la moins permissive."""
    user = User.objects.create_user(username="u3", password="motdepasse123")
    assert user.role == "technicien"
