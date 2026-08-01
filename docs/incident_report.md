# Fiche incident (C21)

## Symptôme

Lors du premier lancement de `python manage.py load_dataset --reset` (tâche C4/C5, backend Django), la commande échouait systématiquement avec le message :

```
ERREUR : dataset_final.csv introuvable. Executez d'abord la chaine de collecte/nettoyage.
```

...alors que `data/processed/dataset_final.csv` **existait bel et bien** sur le disque (généré et vérifié quelques minutes plus tôt par `src/clean/clean_maintenance.py`).

## Reproduction

```bash
cd src/backend
python manage.py load_dataset --reset
# -> ERREUR : dataset_final.csv introuvable...
```

Reproductible à 100 %, indépendamment du contenu des données.

## Diagnostic

Le calcul du chemin racine du projet dans `maintenance/management/commands/load_dataset.py` utilisait :

```python
BASE_DIR = Path(__file__).resolve().parents[4]
```

Le fichier se trouve à `predictive-maintenance-parts/src/backend/maintenance/management/commands/load_dataset.py`. En comptant les niveaux de dossiers parents depuis ce fichier :

| Index `parents[n]` | Dossier atteint |
|---|---|
| `parents[0]` | `commands/` |
| `parents[1]` | `management/` |
| `parents[2]` | `maintenance/` |
| `parents[3]` | `backend/` |
| `parents[4]` | `src/` ← **valeur utilisée par erreur** |
| `parents[5]` | `predictive-maintenance-parts/` ← valeur correcte |

`BASE_DIR` pointait donc vers `src/` et non la racine du projet : `BASE_DIR / "data" / "processed" / "dataset_final.csv"` cherchait un fichier dans `src/data/processed/...`, qui n'existe pas — d'où l'erreur, malgré un fichier bien présent une racine plus haut.

**Cause racine** : erreur de comptage manuelle des niveaux `parents[N]`, aucune vérification automatisée n'existait pour ce calcul de chemin au moment de l'écriture.

## Correction

```diff
- BASE_DIR = Path(__file__).resolve().parents[4]  # .../predictive-maintenance-parts
+ BASE_DIR = Path(__file__).resolve().parents[5]  # .../predictive-maintenance-parts
```

Un seul caractère, mais la cause aurait pu passer inaperçue longtemps sans une vérification explicite — d'où le test de non-régression ajouté (voir ci-dessous), plutôt qu'une simple correction silencieuse.

## Test de non-régression

`src/backend/tests/test_load_dataset_command.py` vérifie explicitement que `BASE_DIR` :
1. se nomme bien `predictive-maintenance-parts` ;
2. contient effectivement les dossiers `data/`, `src/`, `docs/` attendus à la racine du projet.

**Preuve que le test détecte bien la régression** : le bug a été délibérément réintroduit (`parents[4]`) pour vérifier que `pytest tests/test_load_dataset_command.py` échoue bien dans ce cas (2 tests en échec, avec le message `AssertionError: assert 'src' == 'predictive-maintenance-parts'`), avant de restaurer le correctif (`parents[5]`) et de confirmer que la suite complète repasse au vert (31/31 tests). Voir l'historique Git pour la trace de cette vérification.

## Résultat final

```bash
$ python manage.py load_dataset --reset
Tables videes.
Import termine : 5 fournisseurs, 5 pieces, 10000 lectures, 355 interventions.
```

## Retour d'expérience

Ce type d'erreur (calcul manuel de chemin relatif par comptage de `parents[N]`) est facile à introduire et facile à corriger, mais silencieuse si aucun test ne vérifie explicitement le résultat. Leçon appliquée immédiatement au reste du projet : `src/backend/ml_api/model_registry.py` utilise le même pattern de calcul de chemin (`parents[3]`) — corrigé de façon préventive lors de la tâche C18/C19 (ajout d'un chemin explicite via variable d'environnement `ML_MODELS_DIR` pour l'exécution en conteneur Docker, où la structure de dossiers diffère de l'environnement local), avant qu'un incident similaire ne se produise.
