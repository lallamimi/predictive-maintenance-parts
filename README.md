# Maintenance Prédictive & Optimisation des Pièces de Rechange

Projet individuel — Titre RNCP "Développeur en Intelligence Artificielle" (Simplon/ECE).

> **Projet fictif.** Ce projet s'inspire d'un sujet de mission réel (maintenance prédictive automobile) mais n'est **pas** réalisé dans le cadre d'un stage en entreprise : aucune donnée réelle d'entreprise n'est utilisée. Toutes les données sont issues d'un jeu de données public (AI4I 2020 Predictive Maintenance Dataset) reformulé pour un contexte automobile, complété par des données générées synthétiquement (pièces de rechange, fournisseurs, stock) selon des règles métier documentées dans [`docs/`](docs/).

## Objectif

Système d'aide à la décision permettant de :
- prédire les besoins futurs en maintenance et en pièces de rechange à partir de l'historique des interventions ;
- prévoir la demande de pièces de rechange pour optimiser leur disponibilité en stock ;
- suivre des indicateurs de performance (KPI) de maintenance et de gestion des stocks via des tableaux de bord ;
- générer des recommandations en langage naturel (coûts opérationnels, disponibilité des pièces) à l'aide d'un service d'IA générative.

## Stack

- **Backend** : Django 5 + Django REST Framework, PostgreSQL, SimpleJWT, `drf-spectacular` (OpenAPI)
- **Modèles IA** : scikit-learn / XGBoost (prédiction de panne, prévision de demande), SHAP (explicabilité)
- **Service IA tiers** : Groq (Llama 3.3) pour la génération de recommandations en langage naturel — voir [`docs/benchmark_ia.md`](docs/benchmark_ia.md)
- **Frontend** : React 19 + Vite, Recharts / Plotly pour les tableaux de bord
- **Qualité** : pytest, GitHub Actions (CI/CD), Docker / docker-compose

## Structure du projet

```
docs/          # Cahier des charges, architecture, RGPD, veille, benchmark IA, monitoring, incidents
data/          # raw (source publique), synthetic (généré), processed (nettoyé) — raw/synthetic gitignorés
src/collect/   # Scripts de collecte (source publique + génération synthétique) — C1
src/sql/       # Schéma et requêtes d'analyse — C2
src/clean/     # Nettoyage et validation du dataset — C3
src/ml/        # Entraînement des modèles et explicabilité — C9-C13
src/backend/   # API Django (données + modèles IA) — tests dans src/backend/tests/
src/frontend/  # Tableaux de bord React
```

## Démarrage rapide

Voir [`docs/architecture.md`](docs/architecture.md) pour l'architecture complète et [`docs/cahier_des_charges.md`](docs/cahier_des_charges.md) pour les spécifications fonctionnelles.

### Option A — Docker Compose (le plus simple)

```bash
cp .env.example .env   # a la racine ; laisser GROQ_API_KEY vide desactive juste les recommandations IA
docker compose up -d --build

# Charger des donnees de demonstration dans la base (une fois les conteneurs "healthy")
docker compose exec backend python manage.py load_dataset --reset

# Creer un compte de test (role: technicien | gestionnaire_stock | admin)
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@test.local","password":"DemoTest1234!","role":"admin"}'

# Exemple d'appel a l'API de donnees (avec le token "access" retourne ci-dessus)
curl http://localhost:8000/api/data/pieces/ -H "Authorization: Bearer <access_token>"
```

- Frontend : http://localhost:8080 (se connecter avec le compte créé ci-dessus)
- API : http://localhost:8000/api/ — doc interactive sur http://localhost:8000/api/docs/
- Santé : http://localhost:8000/api/health/

### Option B — En local, sans Docker (utile en développement, hot-reload)

```bash
# 1. Collecte + nettoyage des données (une seule fois, ou si data/processed est vide)
pip install -r requirements.txt
python src/collect/download_ai4i.py
python src/collect/generate_synthetic_parts.py
python src/clean/clean_maintenance.py
python src/ml/train_failure_model.py
python src/ml/train_demand_model.py

# 2. Backend
cd src/backend
python -m venv .venv && .venv/Scripts/activate  # ou source .venv/bin/activate sous Linux/Mac
pip install -r requirements.txt
cp .env.example .env   # DATABASE_URL vide -> SQLite local
python manage.py migrate
python manage.py load_dataset --reset
python manage.py runserver

# 3. Frontend (autre terminal)
cd src/frontend
npm install
npm run dev   # http://localhost:5173
```

Dans les deux cas, aucun compte n'existe par défaut : il faut en créer un via `/api/auth/register/` (ou `python manage.py createsuperuser` pour l'admin Django `/admin/`).

## Tests

**51 tests au total**, répartis sur 3 suites, toutes exécutées automatiquement à chaque push (`.github/workflows/ci.yml`) :

**Backend (41 tests, pytest)** — santé applicative, authentification, API données, API modèle IA, règles de décision métier (seuils de risque), permissions par rôle, recommandations, commande d'import (non-régression) :
```bash
cd src/backend
python -m venv .venv && .venv/Scripts/activate   # ou source .venv/bin/activate sous Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python -m pytest -v --cov=. --cov-report=term-missing   # rapport de couverture
ruff check . --select=F,E9                                # lint (job backend-tests de la CI)
```

**Données (6 tests, pytest, racine du dépôt)** — validation du dataset : colonnes requises, valeurs manquantes, doublons, plages physiques :
```bash
pip install -r requirements.txt   # a la racine
python -m pytest tests/ -v
```

**Frontend (4 tests, Vitest + Testing Library)** — rendu, appel API, gestion d'erreur, validation de formulaire :
```bash
cd src/frontend
npm ci
npm test
```

## Limites et perspectives

Phase A (preuve minimale sur l'ensemble des compétences visées) terminée. Limites actuelles, assumées :

- Pas d'audit d'accessibilité WCAG formel
- Pas d'audit de sécurité OWASP complet (rate limiting absent)
- Pas de déploiement en pré-production réelle (local + CI uniquement)
- Suivi de projet individuel : pas de rituels d'équipe au sens strict

Voir [`docs/project_management.md`](docs/project_management.md) pour la suite envisagée (Phase B).

## Suivi du projet

- Référentiel de compétences visé : [`../referentiel_competences.md`](../referentiel_competences.md)
- Suivi agile : voir [`docs/project_management.md`](docs/project_management.md)
- Registre RGPD : [`docs/rgpd.md`](docs/rgpd.md)
- Modèle de données : [`docs/mcd_mpd.md`](docs/mcd_mpd.md)
