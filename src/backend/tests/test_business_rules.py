"""Tests de la couche Metier (competence C18) : calcul, regle de decision,
seuil, mapping resultat. Purs, sans base de donnees ni modele ML charge."""

import pytest

from ml_api.business_rules import niveau_risque, panne_predite


@pytest.mark.parametrize(
    "proba,attendu",
    [
        (0.0, False),
        (0.49, False),
        (0.5, True),
        (0.99, True),
    ],
)
def test_panne_predite_seuil(proba, attendu):
    assert panne_predite(proba) is attendu


@pytest.mark.parametrize(
    "proba,attendu",
    [
        (0.0, "faible"),
        (0.29, "faible"),
        (0.3, "moyen"),
        (0.69, "moyen"),
        (0.7, "eleve"),
        (1.0, "eleve"),
    ],
)
def test_niveau_risque_seuils(proba, attendu):
    assert niveau_risque(proba) == attendu
