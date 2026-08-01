"""
Test de non-regression pour l'incident documente dans docs/incident_report.md :
`load_dataset.py` calculait un BASE_DIR errone (`parents[4]` au lieu de
`parents[5]`), qui pointait vers src/ au lieu de la racine du projet, rendant
data/processed/dataset_final.csv introuvable meme quand le fichier existait.

Ce test empeche toute regression future de ce calcul de chemin sans avoir
besoin d'executer la commande complete (qui necessite des donnees reelles).
"""

from maintenance.management.commands.load_dataset import BASE_DIR


def test_base_dir_resolves_to_project_root():
    assert BASE_DIR.name == "predictive-maintenance-parts"


def test_base_dir_contains_expected_project_folders():
    assert (BASE_DIR / "data").is_dir()
    assert (BASE_DIR / "src").is_dir()
    assert (BASE_DIR / "docs").is_dir()
