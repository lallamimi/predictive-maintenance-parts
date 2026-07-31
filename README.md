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
src/backend/   # API Django (données + modèles IA)
src/frontend/  # Tableaux de bord React
tests/         # Suite de tests (pytest)
```

## Démarrage rapide

Voir [`docs/architecture.md`](docs/architecture.md) pour l'architecture complète et [`docs/cahier_des_charges.md`](docs/cahier_des_charges.md) pour les spécifications fonctionnelles.

```bash
# 1. Collecte des données
python src/collect/download_ai4i.py
python src/collect/generate_synthetic_parts.py

# 2. Nettoyage
python src/clean/clean_maintenance.py

# 3. Backend (à venir)
cd src/backend && pip install -r requirements.txt && python manage.py migrate && python manage.py runserver

# 4. Frontend (à venir)
cd src/frontend && npm install && npm run dev
```

## Suivi du projet

- Référentiel de compétences visé : [`../referentiel_competences.md`](../referentiel_competences.md)
- Suivi agile : voir [`docs/project_management.md`](docs/project_management.md)
- Registre RGPD : [`docs/rgpd.md`](docs/rgpd.md)
