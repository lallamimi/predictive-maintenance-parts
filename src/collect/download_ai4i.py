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
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pandas as pd

DIRECT_CSV_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00601/ai4i2020.csv"
BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = BASE_DIR / "data" / "raw" / "ai4i2020_raw.csv"
LOG_FILE = BASE_DIR / "logs" / "collecte.log"

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Console + fichier logs/collecte.log (rotation 5 Mo x 3), meme convention que le logging Django (C20)."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3),
        ],
    )


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
        logger.info("[1/2] Tentative via le package ucimlrepo...")
        df = fetch_via_ucimlrepo()
        logger.info("OK : %d lignes recuperees via ucimlrepo.", len(df))
    except ImportError:
        logger.warning("ucimlrepo n'est pas installe (pip install ucimlrepo). Repli sur le CSV direct.")
    except Exception as exc:  # noqa: BLE001 - on veut logguer puis basculer sur le repli
        logger.warning("Echec ucimlrepo (%r). Repli sur le CSV direct.", exc)

    if df is None:
        try:
            logger.info("[2/2] Tentative de telechargement direct du CSV UCI...")
            df = fetch_via_direct_csv()
            logger.info("OK : %d lignes recuperees via telechargement direct.", len(df))
        except Exception as exc:  # noqa: BLE001
            logger.error("Echec du telechargement direct (%r).", exc)
            logger.error("ERREUR : aucune des deux methodes de collecte n'a fonctionne.")
            logger.error("Solution manuelle : telecharger le CSV depuis")
            logger.error("  https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset")
            logger.error("  et le placer dans : %s", output_path)
            sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Donnees sauvegardees : %s", output_path)
    logger.info("Lignes : %d | Colonnes : %d", len(df), len(df.columns))
    logger.info("Colonnes : %s", list(df.columns))
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
    setup_logging()
    download(args.output)


if __name__ == "__main__":
    main()
