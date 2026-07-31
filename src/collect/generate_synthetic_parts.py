"""
Generation synthetique des donnees "pieces de rechange" du projet.

Aucun dataset public ne couvre a la fois les pannes machine ET la gestion de
stock de pieces de rechange automobile : cette partie est donc simulee,
selon des regles metier explicites et documentees ci-dessous (pas de tirage
aleatoire "nu" sans justification).

Regle metier n#1 - correspondance mode de panne -> piece consommee
(reprend les 5 modes de panne du dataset AI4I 2020, reformules pour un
contexte automobile) :

    TWF (Tool Wear Failure)       -> Disque d'embrayage   (piece d'usure)
    HDF (Heat Dissipation Failure)-> Radiateur             (dissipation thermique)
    PWF (Power Failure)           -> Alternateur           (defaut de puissance)
    OSF (Overstrain Failure)      -> Courroie de distribution (surcharge mecanique)
    RNF (Random Failure)          -> Capteur moteur        (panne aleatoire, non correlee)

Regle metier n#2 - stock et reapprovisionnement :
    stock_actuel et seuil_reapprovisionnement sont tires de lois realistes
    par categorie de piece (les pieces d'usure ont un seuil plus eleve car
    consommees plus souvent).

Regle metier n#3 - cout et delai :
    chaque piece est rattachee a un fournisseur (fiabilite_score, delai
    moyen de livraison) ; le cout d'une intervention = quantite * prix
    unitaire de la piece.

Pre-requis : avoir execute au prealable `download_ai4i.py` (pour disposer
des identifiants d'intervention et des modes de panne).

Usage :
    python src/collect/generate_synthetic_parts.py
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = BASE_DIR / "data" / "raw" / "ai4i2020_raw.csv"
DEFAULT_OUTPUT_DIR = BASE_DIR / "data" / "synthetic"

# Regle metier n#1 : correspondance mode de panne -> categorie de piece
FAILURE_TO_PART = {
    "TWF": {"nom": "Disque d'embrayage", "categorie": "usure", "prix_min": 60, "prix_max": 180},
    "HDF": {"nom": "Radiateur", "categorie": "refroidissement", "prix_min": 120, "prix_max": 320},
    "PWF": {"nom": "Alternateur", "categorie": "electrique", "prix_min": 150, "prix_max": 400},
    "OSF": {"nom": "Courroie de distribution", "categorie": "usure", "prix_min": 40, "prix_max": 120},
    "RNF": {"nom": "Capteur moteur", "categorie": "electronique", "prix_min": 30, "prix_max": 90},
}

FOURNISSEUR_NOMS = ["AutoPieces Ile-de-France", "GarageDirect Pro", "MecaStock 92", "PieceRapide SARL", "TransAuto Fournitures"]


def generate_fournisseurs(rng: np.random.Generator) -> pd.DataFrame:
    """Genere la table des fournisseurs (fiabilite + delai de livraison)."""
    rows = []
    for i, nom in enumerate(FOURNISSEUR_NOMS, start=1):
        rows.append(
            {
                "fournisseur_id": i,
                "nom": nom,
                "fiabilite_score": round(float(rng.uniform(0.65, 0.98)), 2),
                "delai_moyen_livraison_jours": int(rng.integers(2, 12)),
            }
        )
    return pd.DataFrame(rows)


def generate_pieces_rechange(rng: np.random.Generator, fournisseurs: pd.DataFrame) -> pd.DataFrame:
    """Genere la table des pieces de rechange, une par mode de panne (regle n#1),
    avec stock/seuil selon la regle n#2."""
    rows = []
    for i, (code, info) in enumerate(FAILURE_TO_PART.items(), start=1):
        fournisseur_id = int(rng.choice(fournisseurs["fournisseur_id"]))
        is_usure = info["categorie"] == "usure"
        rows.append(
            {
                "piece_id": i,
                "code_panne_associe": code,
                "nom": info["nom"],
                "categorie": info["categorie"],
                "prix_unitaire": round(float(rng.uniform(info["prix_min"], info["prix_max"])), 2),
                "fournisseur_id": fournisseur_id,
                # regle n#2 : pieces d'usure -> stock et seuil plus eleves (consommation frequente)
                "stock_actuel": int(rng.integers(30, 80)) if is_usure else int(rng.integers(5, 25)),
                "seuil_reapprovisionnement": int(rng.integers(15, 30)) if is_usure else int(rng.integers(3, 10)),
            }
        )
    return pd.DataFrame(rows)


def generate_interventions_pieces(
    rng: np.random.Generator, ai4i: pd.DataFrame, pieces: pd.DataFrame
) -> pd.DataFrame:
    """Pour chaque panne du dataset AI4I (Machine failure == 1), determine la
    piece consommee via la regle n#1, une quantite et une date d'intervention,
    puis calcule le cout (regle n#3)."""
    failure_cols = list(FAILURE_TO_PART.keys())
    missing = [c for c in failure_cols + ["Machine failure"] if c not in ai4i.columns]
    if missing:
        raise ValueError(
            f"Colonnes manquantes dans le dataset AI4I : {missing}. "
            "Avez-vous bien execute download_ai4i.py au prealable ?"
        )

    # Le package ucimlrepo ne renvoie pas de colonne d'identifiant (UDI/UID) :
    # on utilise l'index de ligne du dataset source comme reference stable.
    id_col = next((c for c in ("UDI", "UID") if c in ai4i.columns), None)

    pannes = ai4i[ai4i["Machine failure"] == 1].copy()
    today = datetime.now()
    rows = []
    intervention_id = 1

    for idx, panne in pannes.iterrows():
        modes_actifs = [c for c in failure_cols if panne.get(c, 0) == 1]
        if not modes_actifs:
            continue  # panne generique sans mode identifie : pas de piece rattachee
        for code in modes_actifs:
            piece = pieces[pieces["code_panne_associe"] == code].iloc[0]
            quantite = int(rng.integers(1, 3))
            jours_dans_le_passe = int(rng.integers(0, 730))  # sur les 2 dernieres annees
            rows.append(
                {
                    "intervention_id": intervention_id,
                    "reference_ai4i": panne[id_col] if id_col else idx,
                    "piece_id": int(piece["piece_id"]),
                    "nom_piece": piece["nom"],
                    "quantite": quantite,
                    "date_intervention": (today - timedelta(days=jours_dans_le_passe)).strftime("%Y-%m-%d"),
                    "cout_total": round(quantite * float(piece["prix_unitaire"]), 2),
                }
            )
            intervention_id += 1

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Genere les donnees synthetiques pieces/fournisseurs/interventions.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="CSV AI4I source (issu de download_ai4i.py)")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Dossier de sortie")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERREUR : {args.input} introuvable. Executez d'abord : python src/collect/download_ai4i.py")
        raise SystemExit(1)

    rng = np.random.default_rng(SEED)
    ai4i = pd.read_csv(args.input)

    fournisseurs = generate_fournisseurs(rng)
    pieces = generate_pieces_rechange(rng, fournisseurs)
    interventions = generate_interventions_pieces(rng, ai4i, pieces)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    fournisseurs.to_csv(args.output_dir / "fournisseurs.csv", index=False)
    pieces.to_csv(args.output_dir / "pieces_rechange.csv", index=False)
    interventions.to_csv(args.output_dir / "interventions_pieces.csv", index=False)

    print("Generation terminee :")
    print(f"  - fournisseurs.csv       : {len(fournisseurs)} lignes")
    print(f"  - pieces_rechange.csv    : {len(pieces)} lignes")
    print(f"  - interventions_pieces.csv : {len(interventions)} lignes (pannes AI4I -> pieces consommees)")


if __name__ == "__main__":
    main()
