"""Regles de decision metier, isolees du modele et de la vue (competence C18,
couche "Metier" : calcul, regle de decision, seuil, mapping resultat).

Extrait de PredictFailureView pour etre testable sans modele ML charge.
"""

from __future__ import annotations

SEUIL_PANNE = 0.5
SEUIL_RISQUE_ELEVE = 0.7
SEUIL_RISQUE_MOYEN = 0.3


def panne_predite(proba: float) -> bool:
    return proba >= SEUIL_PANNE


def niveau_risque(proba: float) -> str:
    if proba >= SEUIL_RISQUE_ELEVE:
        return "eleve"
    if proba >= SEUIL_RISQUE_MOYEN:
        return "moyen"
    return "faible"
