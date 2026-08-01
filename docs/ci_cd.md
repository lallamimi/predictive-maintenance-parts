# Intégration et livraison continue (C13, C18, C19)

## Déclencheur

Le workflow `.github/workflows/ci.yml` se déclenche sur chaque `push` et chaque `pull_request`, quelle que soit la branche.

## Étapes (4 jobs séquencés par dépendances)

```mermaid
flowchart LR
    A[data-and-ml] --> B[backend-tests]
    A --> C[frontend-build]
    B --> D[docker-build]
    C --> D
```

1. **`data-and-ml`** — rejoue la chaîne complète de données et d'entraînement à chaque exécution (téléchargement du dataset public, génération synthétique, nettoyage, requêtes SQL, entraînement des deux modèles), puis archive les `.pkl` obtenus comme artefact partagé avec les jobs suivants. C'est la preuve que le pipeline C1→C3→C9 est reproductible, pas seulement documenté.
2. **`backend-tests`** — installe les dépendances backend, récupère les modèles entraînés par le job précédent, migre la base (SQLite en CI) et exécute la suite `pytest` complète (29 tests : auth, données, ML, permissions, recommandations).
3. **`frontend-build`** — lint (`oxlint`) puis `npm run build` pour garantir que le frontend compile sans erreur.
4. **`docker-build`** — construit réellement les images Docker backend et frontend, puis démarre un conteneur du backend fraîchement construit et vérifie que `/api/health/` répond (test de fumée). C'est la preuve de packaging/livraison (C19), pas seulement un `Dockerfile` qui n'a jamais été construit.

## Pourquoi rejouer tout le pipeline à chaque fois plutôt que de committer les `.pkl`

Les modèles entraînés ne sont **jamais versionnés** dans Git (gitignorés, voir `.gitignore`) : ils sont un artefact dérivé, reproductible à partir du code et des données. Les regénérer en CI garantit qu'un contributeur qui clone le dépôt obtient exactement la même chaîne fonctionnelle, sans dépendre d'un fichier binaire figé.

## Vérification locale équivalente

```bash
# Pipeline data + ML
pip install -r requirements.txt
python src/collect/download_ai4i.py && python src/collect/generate_synthetic_parts.py
python src/clean/clean_maintenance.py && python src/clean/validate_dataset.py
python src/ml/train_failure_model.py && python src/ml/train_demand_model.py

# Backend
cd src/backend && pip install -r requirements.txt
python manage.py migrate && python -m pytest -v

# Frontend
cd src/frontend && npm ci && npm run lint && npm run build

# Packaging (necessite Docker Desktop demarre)
docker compose build
```

## Limite connue

La vérification `docker compose build` / `docker compose up` en local nécessite que Docker Desktop soit démarré sur la machine — ce n'était pas garanti de façon fiable dans l'environnement de développement utilisé pour ce projet. La vérification de référence est donc le job `docker-build` de la CI (GitHub Actions, runners Linux avec Docker toujours disponible), qui construit réellement les deux images et démarre un conteneur du backend pour vérifier `/api/health/` — voir le badge de statut du dernier run sur l'onglet *Actions* du dépôt.
