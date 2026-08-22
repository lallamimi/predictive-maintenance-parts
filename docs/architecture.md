# Architecture technique (C15)

## Vue d'ensemble

```mermaid
flowchart TD
    A[Dataset public AI4I 2020] -->|download_ai4i.py| B[data/raw]
    A2[Règles métier pannes/pièces] -->|generate_synthetic_parts.py| C[data/synthetic]
    B --> D[clean_maintenance.py]
    C --> D
    D --> E[data/processed/dataset_final.csv]
    E --> F[train_failure_model.py]
    E --> G[train_demand_model.py]
    F --> H[(data/processed/models/*.pkl)]
    G --> H

    E -->|load_dataset.py| I[(PostgreSQL / SQLite)]
    I --> J[API données /api/data/]
    H --> K[API modèle /api/ml/]
    J --> L[React — Dashboard]
    K --> L
    M[Groq LLM] <--> N[API recommandations /api/recommendations/]
    I --> N
    L --> N
```

## Justification des choix techniques

| Choix | Raison |
|---|---|
| **Django + DRF** | Écosystème mature pour l'authentification (JWT), l'ORM et la génération de documentation OpenAPI (`drf-spectacular`) — cohérent avec les compétences C4/C5/C9. |
| **Deux espaces d'API distincts** (`/api/data/` vs `/api/ml/`) | Le référentiel RNCP distingue explicitement C5 (mise à disposition des données) et C9 (exposition d'un modèle IA) — la séparation rend chaque compétence démontrable isolément. |
| **PostgreSQL (SQLite en local)** | PostgreSQL pour la robustesse en environnement conteneurisé (`docker-compose.yml`), SQLite comme repli zéro-configuration pour le développement rapide — bascule automatique via `DATABASE_URL`. |
| **React 19 + Vite** | Démarrage rapide, écosystème large, cohérent avec les compétences déjà démontrées sur les projets précédents analysés pour cet examen. |
| **scikit-learn / XGBoost pour les modèles maison** | Modèles interprétables (SHAP), légers, adaptés au volume de données du projet — pas besoin de deep learning pour ce périmètre. |
| **Groq pour les recommandations en langage naturel** | Voir `docs/benchmark_ia.md` — gratuit, latence faible, API compatible OpenAI (portabilité). |
| **Modèles chargés en lecture seule par le backend** (`ml_api/model_registry.py`) | Sépare clairement l'entraînement (hors ligne, `src/ml/`) de l'inférence (API), pattern MLOps standard qui évite de ré-entraîner un modèle à chaque requête. |

## Dépendances et services externes

| Catégorie | Dépendance | Rôle |
|---|---|---|
| Backend | Django 5, Django REST Framework, `djangorestframework-simplejwt`, `drf-spectacular` | API, auth JWT, doc OpenAPI |
| Base de données | PostgreSQL 16 (prod/Docker), SQLite (local/CI) | Stockage relationnel |
| ML | scikit-learn, XGBoost, SHAP, pandas, joblib | Entraînement et explicabilité des modèles |
| Frontend | React 19, Vite, Recharts, `lucide-react` | Interface, graphiques, icônes |
| Service externe | Groq API (Llama 3.3 70B) | Recommandations en langage naturel — voir `docs/benchmark_ia.md` et `docs/service_ia.md` ; **optionnel** (repli par règles si absent) |
| Qualité | pytest, pytest-cov, ruff (backend), Vitest, Testing Library (frontend) | Tests et lint |
| Infrastructure | Docker, Docker Compose, GitHub Actions | Packaging et CI/CD |

Liste exhaustive et versionnée dans `requirements.txt` (racine + `src/backend/`) et `src/frontend/package.json`.

## Flux de données

1. **Collecte** (`src/collect/`) : dataset public + génération synthétique documentée.
2. **Nettoyage** (`src/clean/`) : fusion, validation, dataset final versionné dans son format (pas les données elles-mêmes, gitignorées).
3. **Stockage** (`load_dataset.py`) : import en base relationnelle.
4. **Entraînement** (`src/ml/`) : modèles sauvegardés en `.pkl`, hors du backend.
5. **Exposition** : deux APIs REST distinctes, authentifiées par JWT.
6. **Restitution** : dashboard React consommant les deux APIs + les recommandations IA.

## Diagramme de flux applicatif (requête utilisateur)

```mermaid
flowchart LR
    U[Utilisateur] --> I[Interface React]
    I -->|POST /api/ml/predict-failure/| A[API Django]
    A --> M[Modèle chargé en cache]
    M --> A
    A --> B[(PostgreSQL / SQLite)]
    A -->|journalisation| B
    A --> I
    I --> U
```

Répond aux trois questions du référentiel : la donnée entre par l'interface (formulaire de mesures capteur), elle est transformée/exposée par l'API Django (validation, appel modèle, journalisation en base), et le modèle IA intervient entre la validation de l'entrée et la construction de la réponse JSON.

## Preuve de concept

**Niveau atteint : Bon** (flux documenté, testé, avec gestion d'erreurs — cf. grille du référentiel : Minimal / Correct / **Bon** / Excellent).

Le flux ci-dessus est **fonctionnel de bout en bout en environnement local** (vérifié : collecte réelle du dataset UCI, entraînement réel des deux modèles, API testée par requêtes HTTP réelles, interface testée par interactions réelles dans un navigateur — voir l'historique de commits pour le détail de chaque vérification).

**Conclusion : continuer.** Rien ne justifie de corriger l'approche ou de réduire le périmètre — les 21 compétences ont une preuve fonctionnelle. Le seul écart avec le niveau "Excellent" est l'absence de déploiement en pré-production distant (Render/Railway), volontairement classé en Phase B, non bloquant pour la démonstration des compétences visées.

## Diagrammes complémentaires

- Modèle de données : voir les migrations Django (`src/backend/*/migrations/0001_initial.py`) qui font foi de MPD, et `docs/mcd_mpd.md` pour une version lisible.
