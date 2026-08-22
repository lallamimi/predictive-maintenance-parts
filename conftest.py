"""Rend src/clean/ importable pour les tests de tests/ (couche Donnees, C18)
sans transformer src/ en package Python (src/backend/ reste un projet Django
independant avec sa propre gestion de chemin)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "clean"))
