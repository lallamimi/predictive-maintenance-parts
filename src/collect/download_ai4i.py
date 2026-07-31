"""
Collecte automatisee du jeu de donnees public AI4I 2020 Predictive Maintenance Dataset.

Source : UCI Machine Learning Repository, dataset id=601
DOI    : https://doi.org/10.24432/C5HS5C
Licence: CC BY 4.0
Page   : https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset

Le dataset est reformule pour le contexte "vehicule/piece automobile" du projet :
il s'agit d'un jeu de donnees synthetique mais realiste de pannes industrielles
(10 000 lignes), reutilise ici comme proxy des interventions de maintenance
vehicule (vitesse de rotation / couple ~ capteurs moteur-transmission).

Strategie de collecte (deux methodes, avec repli automatique) :
  1. Package officiel `ucimlrepo` (methode recommandee par UCI)
  2. Telechargement direct du CSV si `ucimlrepo` est indisponible ou echoue

Usage :
    python src/collect/download_ai4i.py
    python src/collect/download_ai4i.py --output data/raw/mon_fichier.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

DIRECT_CSV_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00601/ai4i2020.csv"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / "data" / "raw" / "ai4i2020_raw.csv"


def fetch_via_ucimlrepo() -> pd.DataFrame:
    """Methode 1 : package officiel UCI (pip install ucimlrepo)."""
    from ucimlrepo import fetch_ucirepo  # import local : dependance optionnelle

    dataset = fetch_ucirepo(id=601)
    features = dataset.data.features
    targets = dataset.data.targets
    return pd.concat([features, targets], axis=1)


def fetch_via_direct_csv(url: str = DIRECT_CSV_URL) -> pd.DataFrame:
    """Methode 2 (repli) : telechargement direct du CSV UCI."""
    return pd.read_csv(url)


def download(output_path: Path) -> pd.DataFrame:
    """Collecte les donnees en essayant successivement les deux sources,
    avec gestion d'erreurs explicite a chaque etape (exigence C1)."""
    df: pd.DataFrame | None = None

    try:
        print("[1/2] Tentative via le package ucimlrepo...")
        df = fetch_via_ucimlrepo()
        print(f"      OK : {len(df)} lignes recuperees via ucimlrepo.")
    except ImportError:
        print("      ucimlrepo n'est pas installe (pip install ucimlrepo). Repli sur le CSV direct.")
    except Exception as exc:  # noqa: BLE001 - on veut logguer puis basculer sur le repli
        print(f"      Echec ucimlrepo ({exc!r}). Repli sur le CSV direct.")

    if df is None:
        try:
            print("[2/2] Tentative de telechargement direct du CSV UCI...")
            df = fetch_via_direct_csv()
            print(f"      OK : {len(df)} lignes recuperees via telechargement direct.")
        except Exception as exc:  # noqa: BLE001
            print(f"      Echec du telechargement direct ({exc!r}).")
            print("ERREUR : aucune des deux methodes de collecte n'a fonctionne.")
            print("Solution manuelle : telecharger le CSV depuis")
            print("  https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset")
            print(f"  et le placer dans : {output_path}")
            sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\nDonnees sauvegardees : {output_path}")
    print(f"Lignes : {len(df)} | Colonnes : {len(df.columns)}")
    print(f"Colonnes : {list(df.columns)}")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Collecte le dataset AI4I 2020 Predictive Maintenance.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Chemin du fichier CSV de sortie (defaut : data/raw/ai4i2020_raw.csv)",
    )
    args = parser.parse_args()
    download(args.output)


if __name__ == "__main__":
    main()
