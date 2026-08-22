"""
Test de non-regression pour deux incidents documentes dans docs/incident_report.md :
1. `load_dataset.py` calculait un BASE_DIR errone (`parents[4]` au lieu de
   `parents[5]`), qui pointait vers src/ au lieu de la racine du projet, rendant
   data/processed/dataset_final.csv introuvable meme quand le fichier existait.
2. Ce meme calcul, fait sans condition au chargement du module, levait
   IndexError a l'interieur du conteneur Docker (structure de dossiers
   aplatie) - corrige en le rendant paresseux, pilote par la variable
   d'environnement DATA_DIR quand elle est definie (voir docker-compose.yml).

Ce test empeche toute regression future de ce calcul de chemin sans avoir
besoin d'executer la commande complete (qui necessite des donnees reelles).
"""

from maintenance.management.commands.load_dataset import DATA_DIR


def test_data_dir_resolves_to_project_data_folder():
    assert DATA_DIR.name == "data"
    assert DATA_DIR.parent.name == "predictive-maintenance-parts"


def test_data_dir_contains_expected_project_folders():
    assert DATA_DIR.is_dir()
    assert (DATA_DIR.parent / "src").is_dir()
    assert (DATA_DIR.parent / "docs").is_dir()
