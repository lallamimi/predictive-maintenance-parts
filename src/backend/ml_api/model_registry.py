"""
Chargement paresseux (lazy) des modeles entraines (competence C9).

Les modeles sont entraines par src/ml/train_*.py (hors du backend) et charges
ici en lecture seule - le backend ne re-entraine jamais un modele a la volee.
"""

from __future__ import annotations

import os
from pathlib import Path
from threading import Lock

import joblib

# En local (hors Docker), les modeles vivent a la racine du projet, 3 niveaux
# au-dessus de src/backend/. Dans le conteneur, seul src/backend/ est copie -
# le chemin est alors fourni explicitement via ML_MODELS_DIR (voir
# docker-compose.yml) plutot que recalcule par remontee de dossiers, ce qui
# serait fragile des que la structure de fichiers change entre les deux
# environnements.
#
# INCIDENT (voir docs/incident_report.md) : `parents[3]` etait auparavant
# calcule inconditionnellement au chargement du module, meme quand
# ML_MODELS_DIR suffisait. Or /app (racine du conteneur) n'a que 2 niveaux de
# parents avant `/` : `parents[3]` y leve IndexError des l'import, ce qui
# faisait planter Django au demarrage (avant meme `migrate`). Le calcul est
# maintenant strictement paresseux : jamais execute si ML_MODELS_DIR est fourni.


def _resolve_models_dir() -> Path:
    env_value = os.getenv("ML_MODELS_DIR")
    if env_value:
        return Path(env_value)
    base_dir = Path(__file__).resolve().parents[3]  # .../predictive-maintenance-parts (local uniquement)
    return base_dir / "data" / "processed" / "models"


MODELS_DIR = _resolve_models_dir()

_lock = Lock()
_cache: dict[str, object] = {}


class ModeleIndisponible(Exception):
    pass


def _load(name: str, filename: str):
    with _lock:
        if name not in _cache:
            path = MODELS_DIR / filename
            if not path.exists():
                raise ModeleIndisponible(
                    f"{filename} introuvable dans {MODELS_DIR}. "
                    f"Executez d'abord : python src/ml/train_{name}_model.py"
                )
            _cache[name] = joblib.load(path)
    return _cache[name]


def get_failure_model():
    return _load("failure", "failure_model.pkl")


def get_demand_model():
    return _load("demand", "demand_model.pkl")
