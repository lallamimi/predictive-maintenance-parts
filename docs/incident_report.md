# Fiche incident (C21)

## Incident 1 — `load_dataset` ne trouve pas le dataset

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

Ce type d'erreur (calcul manuel de chemin relatif par comptage de `parents[N]`) est facile à introduire et facile à corriger, mais silencieuse si aucun test ne vérifie explicitement le résultat. La tentative de traiter préventivement le même pattern ailleurs dans le projet (`ml_api/model_registry.py`) s'est révélée **incomplète** — voir Incident 2 ci-dessous, où exactement la même classe de bug a quand même provoqué un vrai échec, faute d'avoir traité le symptôme (calcul non conditionné) et pas seulement la valeur numérique.

---

## Incident 2 — le conteneur backend crashe au démarrage (CI `docker-build`)

### Symptôme

Le job CI `docker-build` échouait systématiquement à son étape de test de fumée : les images `backend` et `frontend` se construisaient sans erreur, mais le conteneur backend démarré à partir de l'image fraîchement construite sortait immédiatement, et `/api/health/` ne répondait jamais (timeout après le nombre de tentatives prévu).

### Reproduction

Non reproductible en local en dehors de Docker (`runserver` avec les mêmes variables d'environnement démarrait sans erreur). Reproduit uniquement en construisant et lançant réellement le conteneur :

```bash
docker build -t maintenance-predictive-backend:debug ./src/backend
docker run -d --name debug-backend \
  -e DJANGO_SECRET_KEY=cle-de-test-ci -e DJANGO_DEBUG=0 \
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 -e ML_MODELS_DIR=/app/models \
  -v "$PWD/data/processed/models:/app/models:ro" -p 8000:8000 \
  maintenance-predictive-backend:debug
docker ps -a   # -> Exited (1)
docker logs debug-backend
```

### Diagnostic

`docker logs` a montré un `IndexError: 3` dans `ml_api/model_registry.py`, levé pendant les vérifications système de Django au démarrage (avant même `migrate`) :

```python
_BASE_DIR = Path(__file__).resolve().parents[3]
MODELS_DIR = Path(os.getenv("ML_MODELS_DIR") or (_BASE_DIR / "data" / "processed" / "models"))
```

Cette ligne calculait `_BASE_DIR` **inconditionnellement**, avant même de regarder si `ML_MODELS_DIR` était défini — seule la valeur finale de `MODELS_DIR` dépendait de la variable d'environnement, pas le calcul de `_BASE_DIR` lui-même. Or dans le conteneur, seul `src/backend/` est copié vers `/app/` (voir `Dockerfile`) : depuis `ml_api/model_registry.py`, `/app` n'a que 2 niveaux de parents avant la racine `/`. `.parents[3]` sort donc de la plage disponible et lève `IndexError` — contrairement à `.resolve()` qui, elle, ne lève jamais d'erreur sur un chemin trop court.

**Cause racine** : même famille que l'Incident 1 (calcul de chemin par comptage de `parents[N]`), mais avec une nuance différente et plus dangereuse — ici la variable d'environnement de secours existait bien et était correctement branchée dans `docker-compose.yml` et dans le workflow CI, mais le code ne court-circuitait pas *l'évaluation* du chemin de repli, seulement son *usage final*. Un `or` protège contre une valeur `None`, pas contre une exception levée en calculant l'autre opérande.

### Correction

```diff
-_BASE_DIR = Path(__file__).resolve().parents[3]
-MODELS_DIR = Path(os.getenv("ML_MODELS_DIR") or (_BASE_DIR / "data" / "processed" / "models"))
+def _resolve_models_dir() -> Path:
+    env_value = os.getenv("ML_MODELS_DIR")
+    if env_value:
+        return Path(env_value)
+    base_dir = Path(__file__).resolve().parents[3]
+    return base_dir / "data" / "processed" / "models"
+
+
+MODELS_DIR = _resolve_models_dir()
```

`parents[3]` n'est plus jamais évalué quand `ML_MODELS_DIR` est déjà fourni — exactement le cas en conteneur et en CI.

### Vérification

- Image reconstruite en local, conteneur relancé avec les mêmes variables d'environnement que le smoke test CI : `docker ps -a` montre `Up` (plus de sortie immédiate), `docker logs` ne montre plus de traceback.
- `curl http://localhost:8001/api/health/` → `{"status":"ok","checks":{"database":true,"groq_configured":false}}`.
- Job `docker-build` sur GitHub Actions repassé au vert après le push du correctif (voir [`ci_cd.md`](ci_cd.md)).

### Retour d'expérience

Diagnostiqué en binôme avec le porteur du projet plutôt que documenté comme une limite non résolue : l'accès aux logs du job (via l'API GitHub non authentifiée, faute de connexion navigateur disponible) avait déjà permis de savoir *que* le conteneur ne répondait pas, mais pas *pourquoi* — il a fallu reproduire le conteneur en local (une fois Docker Desktop de nouveau disponible sur la machine) pour obtenir la trace exacte. Leçon durable : un calcul de chemin de repli conditionné par `X or Y` ne protège que si `Y` ne peut pas lever d'exception ; sinon, la condition doit empêcher son *évaluation*, pas seulement ignorer son résultat.

### Extension — le même bug existait dans une deuxième commande

En testant `docker compose up` de bout en bout juste après ce correctif (pour vérifier manuellement que le projet fonctionne réellement en conditions conteneurisées, au-delà du seul `/api/health/` sondé par la CI), `python manage.py load_dataset --reset` a échoué avec exactement la même erreur — `IndexError: 5` cette fois, dans `maintenance/management/commands/load_dataset.py`, sur `BASE_DIR = Path(__file__).resolve().parents[5]`.

C'est la même classe de bug que l'Incident 1 (où `parents[5]` était la valeur *correcte* localement) combinée au même défaut que ci-dessus (calcul non conditionné, invisible pour la CI puisqu'aucune étape n'exécutait `load_dataset` en conteneur avant ce test manuel). Corrigé à l'identique : une fonction `_resolve_data_dir()` qui ne calcule `parents[5]` que si la variable d'environnement `DATA_DIR` est absente, avec `DATA_DIR=/app/data` ajouté au service `backend` de `docker-compose.yml` (et le dossier `data/` monté en lecture seule, comme `data/processed/models/` l'était déjà pour `ML_MODELS_DIR`).

Vérifié en conditions réelles : `docker compose up -d --build`, puis `docker compose exec backend python manage.py load_dataset --reset` → `Import termine : 5 fournisseurs, 5 pieces, 10000 lectures, 355 interventions.` Un compte de test créé via `/api/auth/register/` et une connexion complète au tableau de bord (KPI, prédiction de panne à 99.7 % sur un cas de test, prévision de demande) ont confirmé que la chaîne fonctionne intégralement une fois construite par Docker — pas seulement que `/api/health/` répond.

**Leçon** : corriger un bug dans un fichier ne garantit pas l'absence du même bug ailleurs, même quand on a explicitement identifié le pattern dangereux (voir la note ajoutée à l'Incident 1 après le premier correctif de `model_registry.py`, qui s'est révélée trop optimiste). Un test de bout en bout qui exerce réellement le chemin de code concerné reste plus fiable qu'un raisonnement par analogie sur "où d'autres ce pattern pourrait exister".
