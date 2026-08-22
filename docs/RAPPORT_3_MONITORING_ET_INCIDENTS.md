# RAPPORT 3 : MONITORING APPLICATIF, SUIVI DES MODÈLES ET GESTION DES INCIDENTS TECHNIQUES
## Maintenance Prédictive & Optimisation des Pièces de Rechange Automobile

**Auteur** : Candidate Titre RNCP "Développeur en IA"  
**Établissement** : Simplon / ECE  
**Projet** : `predictive-maintenance-parts`  
**Évaluation** : Bloc 3 — Cas pratique E5 / Épreuve finale (Compétence C11, C20, C21)  
**Format** : Documentation technique de résolution d'incident & monitoring (10 pages maximum)  

---

## TABLE DES MATIÈRES

1. **Monitoring du Modèle d'Intelligence Artificielle (C11)**
   1.1. Métriques de santé, d'usage et de qualité définies  
   1.2. Architecture de stockage et restitution SQL natif  
   1.3. Format des journaux d'inférence (Logs d'exécution)  
   1.4. Endpoint d'agrégation `/api/ml/monitoring/` (Restitution en temps réel)  
   1.5. Seuils d'alerte et politique d'intervention  
2. **Monitoring Applicatif et Surveillance d'Infrastructure (C20)**
   2.1. Journalisation structurée sous Django  
   2.2. Rotation automatisée des fichiers journaux (`logs/app.log`)  
   2.3. Sonde de santé applicative publique (`/api/health/`)  
   2.4. Intégration comme superviseur d'infrastructure Docker & CI/CD  
3. **Fiche d'Incident Technique N°1 — Erreur de Résolution de Chemin lors de l'Importation (C21)**
   3.1. Description du symptôme et environnement de survenance  
   3.2. Procédure de reproduction  
   3.3. Analyse de la cause racine (Diagnostic d'ingénierie)  
   3.4. Solution appliquée et correctif de code  
   3.5. Verrouillage par test automatisé de non-régression  
4. **Fiche d'Incident Technique N°2 — Crash du Conteneur Backend au Démarrage en CI/CD (C21)**
   4.1. Description du symptôme et échec du Smoke Test Docker  
   4.2. Procédure de reproduction sous Docker CLI  
   4.3. Analyse de la cause racine (`IndexError: 3` dans `model_registry.py`)  
   4.4. Correctif d'ingénierie par indirection de variables d'environnement  
   4.5. Extension du bug et correctif sur la commande d'importation  
   4.6. Validation fonctionnelle globale et Retour d'Expérience (REX)  

---

## 1. MONITORING DU MODÈLE D'INTELLIGENCE ARTIFICIELLE (C11)

### 1.1. Métriques de Santé, d'Usage et de Qualité Définies
Afin d'assurer le suivi opérationnel du modèle de prédiction de panne (`predict-failure`) et du modèle de prévision de demande (`predict-demand`), un dispositif de monitoring d'inférence est intégré au backend Django ([`docs/monitoring.md`](file:///d:/predictive-maintenance-parts/docs/monitoring.md)) :

- **Santé système** : Latence de traitement (en ms), taux d'échec (requêtes 400/503), disponibilité.
- **Usage** : Nombre total d'appels par endpoint et fréquence d'utilisation.
- **Qualité & Confiance du modèle** : Probabilité brute calculée par le modèle XGBoost, niveau de risque attribué (`faible`, `moyen`, `élevé`).
- **Données d'entrée** : Journalisation systématique des entrées invalides rejetées (HTTP 400 pour valeurs capteurs hors bornes physiques).

### 1.2. Architecture de Stockage et Restitution SQL Natif
- **Choix d'architecture (Sobriété technique)** : Utilisation d'une table relationnelle dédiée `ModelPredictionLog` dans `src/backend/ml_api/models.py`. 
- **Justification** : Permet des requêtes d'agrégation SQL instantanées sans nécessiter le déploiement d'une stack externe surdimensionnée (Grafana / Prometheus), parfaitement adapté au périmètre du projet.

### 1.3. Format des Journaux d'Inférence (Logs d'Exécution)
Chaque inférence génère une ligne de log structurée :
```text
2026-08-05T06:43:05 | /api/ml/predict-failure/ | 200 | latency_ms=1981.6 | user=admin_test | proba=0.003 | niveau=faible
2026-08-05T06:42:55 | /api/ml/predict-failure/ | 400 | latency_ms=0.40   | user=admin_test | invalid_input (type_produit manquant)
```

### 1.4. Endpoint d'Agrégation `/api/ml/monitoring/` (Restitution en Temps Réel)
Un endpoint REST authentifié (`GET /api/ml/monitoring/`) agrège dynamiquement les métriques pour le tableau de bord :

```json
{
  "par_endpoint": {
    "predict-failure": {
      "nb_appels": 2,
      "nb_echecs": 1,
      "taux_echec_pct": 50.0,
      "latence_moyenne_ms": 991.0
    },
    "predict-demand": {
      "nb_appels": 0,
      "nb_echecs": 0,
      "taux_echec_pct": 0,
      "latence_moyenne_ms": 0
    }
  },
  "derniers_appels": [
    {
      "endpoint": "predict-failure",
      "horodatage": "2026-08-05T06:43:05.825Z",
      "latence_ms": 1981.65,
      "succes": true,
      "resultat_resume": "proba=0.003 niveau=faible"
    }
  ]
}
```

### 1.5. Seuils d'Alerte et Politique d'Intervention
- **Latence moyenne > 1000 ms** ➜ Alerte : Vérification de la charge processeur et optimisation de l'inférence.
- **Taux d'échec > 5 %** ➜ Alerte critique : Consultation des logs d'erreurs et vérification de la présence des fichiers binaires `.pkl`.

---

## 2. MONITORING APPLICATIF ET SURVEILLANCE D'INFRASTRUCTURE (C20)

### 2.1. Journalisation Structurée sous Django
Le backend configure le dictionnaire `LOGGING` dans `config/settings.py` pour capturer l'ensemble des événements applicatifs :
- Loggers spécialisés par domaine métier : `maintenance` (pour les capteurs et interventions) et `inventory` (pour les pièces et stock).

### 2.2. Rotation Automatisée des Fichiers Journaux
Pour éviter la saturation de l'espace disque du serveur ou du conteneur, les journaux sont gérés par un `RotatingFileHandler` :
- Fichier cible : `logs/app.log`
- Taille maximale par fichier : **5 Mo**
- Conservation : **3 fichiers d'archive** (rotation glissante).

### 2.3. Sonde de Santé Applicative Publique (`/api/health/`)
L'endpoint public `GET /api/health/` permet de contrôler la santé de l'application sans authentification :
- **Vérifications exécutées** : Connexion active à la base de données relationnelle et présence des clés de configuration.
- **Codes de réponse HTTP** :
  - `HTTP 200 OK` : Base de données disponible et opérationnelle.
  - `HTTP 503 Service Unavailable` : Défaillance de connexion à la BDD.

### 2.4. Intégration comme Superviseur d'Infrastructure
Cet endpoint `/api/health/` est exploité directement par :
1. La directive `healthcheck` de `docker-compose.yml` pour redémarrer automatiquement le conteneur en cas de défaillance.
2. Le job `docker-build` du pipeline CI/CD GitHub Actions pour valider la livraison.

---

## 3. FICHE D'INCIDENT TECHNIQUE N°1 — ERREUR DE RÉSOLUTION DE CHEMIN LORS DE L'IMPORTATION (C21)

### 3.1. Description du Symptôme
Lors de l'exécution initiale de la commande de chargement des données (`python manage.py load_dataset --reset`), le système levait l'erreur suivante :
```text
ERREUR : dataset_final.csv introuvable. Executez d'abord la chaine de collecte/nettoyage.
```
...alors que le fichier `data/processed/dataset_final.csv` existait bel et bien sur le disque.

### 3.2. Procédure de Reproduction
```bash
cd src/backend
python manage.py load_dataset --reset
# ➜ ERREUR : dataset_final.csv introuvable...
```

### 3.3. Analyse de la Cause Racine (Diagnostic d'Ingénierie)
Dans `maintenance/management/commands/load_dataset.py`, le calcul du dossier racine utilisait :
```python
BASE_DIR = Path(__file__).resolve().parents[4]
```
En décomptant les répertoires parents depuis l'emplacement du script :
- `parents[0]` ➜ `commands/`
- `parents[1]` ➜ `management/`
- `parents[2]` ➜ `maintenance/`
- `parents[3]` ➜ `backend/`
- `parents[4]` ➜ `src/` *(Erreur : pointait vers `src/` au lieu de la racine du projet !)*
- `parents[5]` ➜ `predictive-maintenance-parts/` *(Valeur correcte)*.

`BASE_DIR` cherchait donc le fichier dans `src/data/processed/...` au lieu de `data/processed/...`.

### 3.4. Solution Appliquée et Correctif
Correction de l'index dans `load_dataset.py` :
```diff
- BASE_DIR = Path(__file__).resolve().parents[4]
+ BASE_DIR = Path(__file__).resolve().parents[5]
```

### 3.5. Verrouillage par Test Automatisé de Non-Régression
Pour éviter que cette erreur ne se reproduise, le test unitaire [`src/backend/tests/test_load_dataset_command.py`](file:///d:/predictive-maintenance-parts/src/backend/tests/test_load_dataset_command.py) a été créé. Il vérifie que `BASE_DIR` pointe vers un dossier contenant les répertoires réels `data/`, `src/` et `docs/`.

---

## 4. FICHE D'INCIDENT TECHNIQUE N°2 — CRASH DU CONTENEUR BACKEND AU DÉMARRAGE EN CI/CD (C21)

### 4.1. Description du Symptôme
Le job CI/CD `docker-build` échouait systématiquement lors du test de fumée : le conteneur Backend s'arrêtait immédiatement après son lancement (`Exited (1)`), et l'endpoint `/api/health/` ne répondait jamais.

### 4.2. Procédure de Reproduction sous Docker CLI
```bash
docker build -t backend-debug ./src/backend
docker run -d --name debug-backend \
  -e DJANGO_SECRET_KEY=cle-test -e DJANGO_DEBUG=0 \
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 -e ML_MODELS_DIR=/app/models \
  -v "$PWD/data/processed/models:/app/models:ro" -p 8000:8000 \
  backend-debug
docker ps -a   # ➜ Status: Exited (1)
```

### 4.3. Analyse de la Cause Racine (`IndexError: 3` dans `model_registry.py`)
L'examen des journaux du conteneur (`docker logs debug-backend`) a révélé l'exception suivante :
```python
_BASE_DIR = Path(__file__).resolve().parents[3]
MODELS_DIR = Path(os.getenv("ML_MODELS_DIR") or (_BASE_DIR / "data" / "processed" / "models"))
```
**Cause du crash** : Cette ligne évaluait `_BASE_DIR` de manière **inconditionnelle**, avant d'évaluer la variable d'environnement `ML_MODELS_DIR`. Or, dans le conteneur Docker, seul le dossier `src/backend/` est copié vers la racine `/app/`. Depuis `ml_api/model_registry.py`, `/app` ne possède que 2 niveaux de parents. `.parents[3]` sortait de la plage disponible et levait une exception `IndexError: 3` fatale.

### 4.4. Correctif d'Ingénierie par Indirection de Variables d'Environnement
Réécriture du chargement dans `ml_api/model_registry.py` avec une fonction qui n'évalue `parents[3]` que si la variable d'environnement est absente :

```python
def _resolve_models_dir() -> Path:
    env_value = os.getenv("ML_MODELS_DIR")
    if env_value:
        return Path(env_value)
    base_dir = Path(__file__).resolve().parents[3]
    return base_dir / "data" / "processed" / "models"

MODELS_DIR = _resolve_models_dir()
```

### 4.5. Extension du Bug et Correctif sur la Commande d'Importation
La même vérification a révélé un problème identique sur `load_dataset.py` en conteneur. Une fonction `_resolve_data_dir()` similaire a été implémentée et la variable `DATA_DIR=/app/data` a été ajoutée à `docker-compose.yml`.

### 4.6. Validation Fonctionnelle Globale & REX d'Ingénierie
- Re-build de l'image Docker et exécution du test de fumée ➜ `HTTP 200 OK` obtenu sur `/api/health/`.
- Importation réussie dans le conteneur : `Import termine : 5 fournisseurs, 5 pieces, 10000 lectures, 355 interventions.`
- **Leçon d'Ingénierie (REX)** : Un calcul de chemin de repli du type `os.getenv("X") or calcul()` évalue toujours les deux expressions. Si le calcul peut lever une exception, la condition doit empêcher son évaluation (via un bloc `if/else`), et pas seulement ignorer son résultat.
