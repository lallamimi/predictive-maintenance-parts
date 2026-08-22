"""Tests de la couche Donnees (competence C18) : colonnes, types, valeurs
manquantes, formats. Purs, sur des DataFrames synthetiques, aucun fichier requis."""

import pandas as pd

from validate_dataset import REQUIRED_COLUMNS, validate

LIGNE_VALIDE = {
    "reference_ai4i": 1,
    "type_produit": "M",
    "temperature_air_k": 300.0,
    "temperature_process_k": 310.0,
    "vitesse_rotation_rpm": 1500.0,
    "couple_nm": 40.0,
    "usure_outil_min": 100.0,
    "panne": False,
}


def _df(**overrides):
    ligne = {**LIGNE_VALIDE, **overrides}
    return pd.DataFrame([ligne])


def test_dataset_valide_est_reconnu_valide():
    rapport = validate(_df())
    assert rapport["valide"] is True
    assert rapport["colonnes_requises_presentes"] is True
    assert rapport["doublons"] == 0


def test_colonne_manquante_est_detectee():
    df = _df().drop(columns=["couple_nm"])
    rapport = validate(df)
    assert rapport["colonnes_requises_presentes"] is False
    assert "couple_nm" in rapport["colonnes_manquantes"]
    assert rapport["valide"] is False


def test_valeur_manquante_est_comptee():
    df = _df()
    df.loc[0, "usure_outil_min"] = None
    rapport = validate(df)
    assert rapport["valeurs_manquantes_par_colonne"]["usure_outil_min"] == 1


def test_doublon_rend_le_dataset_non_valide():
    df = pd.concat([_df(), _df()], ignore_index=True)
    rapport = validate(df)
    assert rapport["doublons"] == 1
    assert rapport["valide"] is False


def test_valeur_hors_plage_physique_rend_le_dataset_non_valide():
    df = _df(temperature_air_k=-50.0)
    rapport = validate(df)
    assert rapport["plages_hors_bornes"]["temperature_air_k"] == 1
    assert rapport["valide"] is False


def test_toutes_les_colonnes_requises_sont_couvertes_par_le_rapport():
    rapport = validate(_df())
    assert set(rapport["valeurs_manquantes_par_colonne"].keys()) == set(REQUIRED_COLUMNS)
