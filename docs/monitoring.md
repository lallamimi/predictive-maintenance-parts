# Monitoring (C11 — modèle, C20 — application)

## Monitoring du modèle IA (C11)

**Ce qui est mesuré** : chaque appel à `/api/ml/predict-failure/` et `/api/ml/predict-demand/` est journalisé dans `ml_api.ModelPredictionLog` (voir `src/backend/ml_api/models.py`) :

| Métrique | Description |
|---|---|
| `latence_ms` | Temps de traitement de la requête (chargement modèle exclu, mis en cache) |
| `succes` | Faux si le modèle est indisponible ou l'entrée invalide |
| `resultat_resume` | Résumé de la prédiction (proba, niveau de risque / pièce, demande prévue) |
| `message_erreur` | Cause de l'échec le cas échéant |

**Restitution** : `GET /api/ml/monitoring/` (authentifié) agrège, par endpoint : nombre d'appels, taux d'échec, latence moyenne, et les 10 derniers appels. Consommable directement par un futur widget du tableau de bord (Phase B).

**Outil choisi et pourquoi** : une table Postgres/SQLite dédiée plutôt qu'un simple fichier de log — permet des agrégations SQL immédiates et une restitution dans le dashboard React existant (Recharts déjà en dépendance), sans ajouter d'outil externe (Prometheus/Grafana) disproportionné pour ce volume.

**Seuils d'alerte définis** (à surveiller manuellement en Phase A, à automatiser en Phase B) :

| Métrique | Seuil | Action |
|---|---|---|
| Latence moyenne | > 1000 ms | Vérifier la charge serveur / taille du modèle |
| Taux d'échec | > 5 % | Consulter `message_erreur`, vérifier que les `.pkl` sont bien présents |
| `predict-demand` sans historique | fréquent | Signale une pièce mal alimentée en données synthétiques |

## Monitoring applicatif (C20)

**Journalisation de chaque requête HTTP** : `config.middleware.RequestLoggingMiddleware` (voir `src/backend/config/middleware.py`), enregistré en dernier dans `MIDDLEWARE`. Contrairement à `ml_api.ModelPredictionLog` (C11, limité aux deux endpoints de prédiction), ce middleware couvre **toute l'application** — authentification, données, recommandations, health check compris. Format aligné sur l'exemple du référentiel :
```
<horodatage> | <méthode> <chemin> | <statut> | latency_ms=<X> | user=<username|anon>
```
Niveau `WARNING` si le statut renvoyé est ≥ 500, `INFO` sinon. Exemple réel capturé (07/08/2026) :
```
GET /api/health/ | 200 | latency_ms=1.3 | user=anon
GET /api/data/pieces/ | 200 | latency_ms=34.8 | user=jury_c20
```

**Journalisation Django** : configuration `LOGGING` dans `config/settings.py` — sortie console + fichier `logs/app.log` (rotation 5 Mo × 3, non versionné). Loggers dédiés `maintenance` et `inventory` en plus du logger `django` standard — c'est ce logger `maintenance` que réutilise le middleware ci-dessus.

**Endpoint de santé** : `GET /api/health/` (public, sans authentification) vérifie la connexion base de données et si `GROQ_API_KEY` est configurée. Retourne `503` si la base de données est inaccessible.

**Utilisation prévue** : ce endpoint est le point d'entrée naturel pour un futur superviseur externe (UptimeRobot, healthcheck Docker — voir `docker-compose.yml`).
