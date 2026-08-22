# Maintenance Prédictive & Optimisation des Pièces de Rechange

Projet individuel de maintenance prédictive et d’optimisation des stocks de pièces automobiles.

Cette plateforme illustre un cas d’usage industriel complet : exploiter des données capteurs, entraîner des modèles de Machine Learning, exposer les prédictions via une API REST sécurisée et restituer les indicateurs dans un tableau de bord React.

L’objectif est d’aider à anticiper les défaillances machines, prioriser les interventions et ajuster les stocks de pièces de rechange à partir d’indicateurs exploitables.

## Aperçu

Cette application couvre une chaîne complète :

```text
Données capteurs
      ↓
Préparation & validation
      ↓
Modèles ML : XGBoost / RandomForest
      ↓
API Django REST sécurisée JWT
      ↓
Dashboard React : KPI, prédictions, recommandations
      ↓
CI/CD Docker + tests automatisés
```

## Fonctionnalités

- Collecte et préparation d’un dataset de maintenance prédictive automobile.
- Analyse SQL métier : coûts, interventions, pièces critiques, fournisseurs.
- Base relationnelle avec PostgreSQL / SQLite selon l’environnement.
- API REST documentée avec OpenAPI / Swagger.
- Authentification JWT avec gestion des rôles.
- Prédiction de panne machine à partir de mesures capteur.
- Prévision de demande en pièces de rechange.
- Recommandations en langage naturel via Groq Llama 3.3.
- Monitoring des prédictions et journalisation applicative.
- Dashboard React 19 avec KPI, graphiques et formulaires métiers.
- Pipeline CI/CD GitHub Actions avec tests, build frontend et packaging Docker.

## Stack technique

| Couche | Technologies |
|---|---|
| Backend | Django 5, Django REST Framework, SimpleJWT |
| Base de données | PostgreSQL, SQLite |
| Machine Learning | pandas, scikit-learn, XGBoost, SHAP |
| IA générative | Groq API, Llama 3.3 |
| Frontend | React 19, Vite, Recharts, Plotly |
| Qualité | pytest, Vitest, Testing Library, ruff, eslint |
| DevOps | Docker, docker-compose, GitHub Actions |

## Architecture du projet

```text
docs/          Documentation technique, architecture, RGPD, monitoring, CI/CD
data/          Données brutes, intermédiaires et préparées
src/collect/   Collecte et préparation initiale des données
src/sql/       Schéma SQL et requêtes d’analyse métier
src/clean/     Nettoyage, validation et normalisation du dataset
src/ml/        Entraînement, métriques et explicabilité des modèles
src/backend/   API Django REST, authentification, modèles IA, monitoring
src/frontend/  Interface React, dashboard, formulaires et tests frontend
tests/         Tests de validation des données
```

## Modèles IA

Deux modèles principaux sont utilisés :

- **XGBoost** pour la prédiction de défaillance machine.
- **RandomForest** pour la prévision de demande en pièces.

Le choix du modèle de panne est justifié par une comparaison chiffrée entre plusieurs algorithmes :

| Modèle | Accuracy | F1 Score | ROC-AUC | Recall |
|---|---:|---:|---:|---:|
| Régression logistique | 0.8252 | 0.2373 | 0.8836 | 0.8000 |
| Random Forest | 0.9700 | 0.6193 | 0.9670 | 0.7176 |
| XGBoost | 0.9692 | 0.6516 | 0.9730 | 0.8471 |

Les métriques sont conservées dans [`docs/ml_metrics.json`](docs/ml_metrics.json) et la justification détaillée est disponible dans [`docs/choix_modele_ml.md`](docs/choix_modele_ml.md).

## API principale

| Endpoint | Rôle |
|---|---|
| `GET /api/health/` | Santé applicative |
| `POST /api/auth/login/` | Authentification JWT |
| `GET /api/data/pieces/` | Catalogue des pièces |
| `GET /api/data/interventions/kpi/` | KPI de maintenance |
| `POST /api/ml/predict-failure/` | Prédiction de panne |
| `POST /api/ml/predict-demand/` | Prévision de demande |
| `GET /api/ml/monitoring/` | Monitoring des modèles |
| `GET /api/recommendations/` | Recommandations IA |

Documentation interactive :

```text
http://localhost:8000/api/docs/
```

## Démarrage avec Docker

```bash
cp .env.example .env
docker compose up -d --build
```

Charger les données dans la base :

```bash
docker compose exec backend python manage.py load_dataset --reset
```

Créer un compte de test :

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@test.local","password":"DemoTest1234!","role":"admin"}'
```

Accès :

```text
Frontend : http://localhost:8080
API      : http://localhost:8000/api/
Swagger  : http://localhost:8000/api/docs/
Health   : http://localhost:8000/api/health/
```

## Démarrage local

### Backend

```bash
cd src/backend
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py load_dataset --reset
python manage.py runserver
```

### Frontend

```bash
cd src/frontend
npm install
npm run dev
```

Frontend local :

```text
http://localhost:5173
```

## Tests

Le projet dispose de **51 tests automatisés**.

| Suite | Nombre | Périmètre |
|---|---:|---|
| Données | 6 | Structure, valeurs manquantes, doublons, bornes physiques |
| Backend | 41 | Auth, API, permissions, ML, monitoring, recommandations |
| Frontend | 4 | Formulaire, appel API, affichage résultat, erreurs |

### Tests backend

```bash
cd src/backend
python -m pytest -v --cov=. --cov-report=term-missing
ruff check . --select=F,E9
```

### Tests données

```bash
python -m pytest tests/ -v
```

### Tests frontend

```bash
cd src/frontend
npm test
```

## CI/CD

Le workflow GitHub Actions exécute automatiquement :

```text
1. Pipeline données + entraînement des modèles
2. Lint + tests + build frontend
3. Tests backend avec couverture
4. Packaging Docker + smoke test applicatif
```

Le pipeline vérifie notamment :

- la préparation des données ;
- l’entraînement des modèles ;
- les tests automatisés ;
- le build React ;
- la construction Docker ;
- le démarrage réel du backend via `/api/health/`.

## Monitoring

Le projet inclut une supervision applicative légère :

- endpoint public `GET /api/health/` ;
- journalisation Django dans `logs/app.log` ;
- rotation automatique des logs ;
- table `ModelPredictionLog` pour tracer les inférences ;
- endpoint `GET /api/ml/monitoring/` pour agréger les appels modèle.

## Sécurité

- Authentification JWT.
- Endpoints métier protégés.
- Permissions par rôle : `technicien`, `gestionnaire_stock`, `admin`.
- Mots de passe hachés.
- Variables sensibles chargées via `.env`.
- Aucune clé API versionnée.

## Documentation utile

| Document | Description |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | Architecture technique |
| [`docs/ci_cd.md`](docs/ci_cd.md) | Pipeline CI/CD |
| [`docs/monitoring.md`](docs/monitoring.md) | Logs, santé applicative, monitoring |
| [`docs/incident_report.md`](docs/incident_report.md) | Incident technique et résolution |
| [`docs/mcd_mpd.md`](docs/mcd_mpd.md) | Modèle de données |
| [`docs/rgpd.md`](docs/rgpd.md) | Registre et démarche RGPD |
| [`docs/choix_modele_ml.md`](docs/choix_modele_ml.md) | Choix du modèle ML |
| [`docs/benchmark_ia.md`](docs/benchmark_ia.md) | Benchmark du service IA |

## Perspectives

Améliorations possibles :

- déploiement cloud en pré-production ;
- suivi avancé du data drift ;
- monitoring modèle plus détaillé ;
- audit de sécurité applicative ;
- audit d’accessibilité avec utilisateurs finaux.
