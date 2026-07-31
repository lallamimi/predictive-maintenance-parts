"""
Nettoyage et fusion des donnees (competence C3).

Entrees :
    data/raw/ai4i2020_raw.csv            (issu de download_ai4i.py)
    data/synthetic/interventions_pieces.csv, pieces_rechange.csv (issus de generate_synthetic_parts.py)

Regles de nettoyage appliquees (documentees, pas de suppression silencieuse) :
    1. Suppression des doublons stricts.
    2. Suppression des lignes physiquement impossibles (temperatures negatives en Kelvin,
       vitesse de rotation <= 0, couple <= 0).
    3. Renommage des colonnes en snake_case francais, pour coherence avec le reste du projet.
    4. Fusion avec les interventions/pieces synthetiques sur l'index (reference_ai4i) pour
       obtenir un jeu de donnees final "capteurs + panne + piece consommee".

Sortie :
    data/processed/dataset_final.csv
    Rapport avant/apres affiche en console.

Usage :
    python src/clean/clean_maintenance.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_PATH = BASE_DIR / "data" / "raw" / "ai4i2020_raw.csv"
SYNTHETIC_DIR = BASE_DIR / "data" / "synthetic"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "dataset_final.csv"

RENAME_MAP = {
    "Type": "type_produit",
    "Air temperature": "temperature_air_k",
    "Process temperature": "temperature_process_k",
    "Rotational speed": "vitesse_rotation_rpm",
    "Torque": "couple_nm",
    "Tool wear": "usure_outil_min",
    "Machine failure": "panne",
    "TWF": "panne_twf",
    "HDF": "panne_hdf",
    "PWF": "panne_pwf",
    "OSF": "panne_osf",
    "RNF": "panne_rnf",
}


def clean_ai4i(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    report = {"lignes_avant": len(df)}

    df = df.drop_duplicates()
    report["doublons_supprimes"] = report["lignes_avant"] - len(df)

    mask_valide = (
        (df["Air temperature"] > 0)
        & (df["Process temperature"] > 0)
        & (df["Rotational speed"] > 0)
        & (df["Torque"] > 0)
        & (df["Tool wear"] >= 0)
    )
    report["lignes_invalides_supprimees"] = int((~mask_valide).sum())
    df = df.loc[mask_valide].copy()

    df = df.rename(columns=RENAME_MAP)
    df.index.name = "reference_ai4i"
    df = df.reset_index()

    report["lignes_apres"] = len(df)
    return df, report


def merge_with_interventions(ai4i_clean: pd.DataFrame) -> pd.DataFrame:
    interventions = pd.read_csv(SYNTHETIC_DIR / "interventions_pieces.csv")
    pieces = pd.read_csv(SYNTHETIC_DIR / "pieces_rechange.csv")

    interventions_enrichies = interventions.merge(
        pieces[["piece_id", "categorie", "prix_unitaire", "fournisseur_id"]],
        on="piece_id",
        how="left",
    )

    fusion = ai4i_clean.merge(
        interventions_enrichies,
        on="reference_ai4i",
        how="left",
        suffixes=("", "_intervention"),
    )
    return fusion


def main() -> None:
    if not RAW_PATH.exists():
        print(f"ERREUR : {RAW_PATH} introuvable. Executez d'abord : python src/collect/download_ai4i.py")
        raise SystemExit(1)

    raw = pd.read_csv(RAW_PATH)
    clean, report = clean_ai4i(raw)
    final = merge_with_interventions(clean)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(OUTPUT_PATH, index=False)

    print("=== Rapport de nettoyage (avant / apres) ===")
    print(f"Lignes avant nettoyage       : {report['lignes_avant']}")
    print(f"Doublons supprimes           : {report['doublons_supprimes']}")
    print(f"Lignes physiquement invalides supprimees : {report['lignes_invalides_supprimees']}")
    print(f"Lignes apres nettoyage       : {report['lignes_apres']}")
    print(f"Colonnes finales ({len(final.columns)}) : {list(final.columns)}")
    print(f"Lignes avec intervention associee (panne reelle) : {final['intervention_id'].notna().sum()}")
    print(f"\nDataset final sauvegarde : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
