"""
Validation qualite du dataset final (competence C3 - controle qualite).

Verifie : nombre de lignes, valeurs manquantes par colonne, doublons,
presence des colonnes requises, coherence des plages de valeurs.

Usage :
    python src/clean/validate_dataset.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_DIR / "data" / "processed" / "dataset_final.csv"
REQUIRED_COLUMNS = [
    "reference_ai4i",
    "type_produit",
    "temperature_air_k",
    "temperature_process_k",
    "vitesse_rotation_rpm",
    "couple_nm",
    "usure_outil_min",
    "panne",
]

RANGE_CHECKS = {
    "temperature_air_k": (250, 350),       # Kelvin, plage plausible capteur moteur
    "temperature_process_k": (250, 350),
    "vitesse_rotation_rpm": (0, 3000),
    "couple_nm": (0, 100),
    "usure_outil_min": (0, 300),
}


def validate(df: pd.DataFrame) -> dict:
    report = {
        "n_lignes": len(df),
        "n_colonnes": len(df.columns),
        "colonnes_requises_presentes": all(c in df.columns for c in REQUIRED_COLUMNS),
        "colonnes_manquantes": [c for c in REQUIRED_COLUMNS if c not in df.columns],
        "doublons": int(df.duplicated().sum()),
        "valeurs_manquantes_par_colonne": {
            c: int(df[c].isna().sum()) for c in REQUIRED_COLUMNS if c in df.columns
        },
        "plages_hors_bornes": {},
    }

    for col, (low, high) in RANGE_CHECKS.items():
        if col in df.columns:
            hors_bornes = int(((df[col] < low) | (df[col] > high)).sum())
            report["plages_hors_bornes"][col] = hors_bornes

    report["valide"] = (
        report["colonnes_requises_presentes"]
        and report["doublons"] == 0
        and all(v == 0 for v in report["plages_hors_bornes"].values())
    )
    return report


def main() -> None:
    if not DATASET_PATH.exists():
        print(f"ERREUR : {DATASET_PATH} introuvable. Executez d'abord : python src/clean/clean_maintenance.py")
        raise SystemExit(1)

    df = pd.read_csv(DATASET_PATH)
    report = validate(df)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    print()
    print("RESULTAT :", "VALIDE" if report["valide"] else "NON VALIDE")

    if not report["valide"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
