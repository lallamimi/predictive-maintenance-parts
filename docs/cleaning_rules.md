# Règles de nettoyage et validation du dataset (C3)

## Sources fusionnées

- `data/raw/ai4i2020_raw.csv` — AI4I 2020 Predictive Maintenance Dataset, 10 000 lignes brutes (voir C1)
- `data/synthetic/interventions_pieces.csv`, `pieces_rechange.csv` — données générées (voir C1)

## Règles de nettoyage appliquées (`src/clean/clean_maintenance.py`)

1. **Suppression des doublons stricts** — `df.drop_duplicates()` sur l'ensemble des colonnes.
2. **Suppression des lignes physiquement impossibles** — température air/process > 0 K, vitesse de rotation > 0, couple > 0, usure outil ≥ 0. Une valeur négative ou nulle sur ces mesures physiques signale un défaut de capteur, pas une observation exploitable.
3. **Renommage des colonnes en snake_case français** — cohérence avec le reste du projet (modèles Django, API REST, dashboard React).
4. **Fusion avec les interventions/pièces synthétiques** sur `reference_ai4i`, jointure gauche : chaque lecture capteur garde sa ligne même sans intervention associée ; une lecture liée à plusieurs interventions (plusieurs pièces changées pour une même panne) produit plusieurs lignes.

Aucune suppression silencieuse : chaque règle produit un compteur inclus dans le rapport avant/après.

## Rapport avant/après (exécution du 04/08/2026)

| Étape | Valeur |
|---|---|
| Lignes avant nettoyage (AI4I brut) | 10 000 |
| Doublons supprimés | 0 |
| Lignes physiquement invalides supprimées | 0 |
| Lignes après nettoyage (avant fusion) | 10 000 |
| Lignes après fusion avec interventions | 10 025 |
| Colonnes finales | 22 |
| Interventions réelles liées (panne réelle) | 355 |

0 doublon et 0 valeur invalide : attendu, AI4I est un jeu académique déjà propre. Les 25 lignes supplémentaires après fusion viennent de pannes ayant nécessité plusieurs pièces (jointure 1-vers-N) — pas une anomalie. La vraie valeur ajoutée du script est la fusion (règle 4), pas la correction de données déjà saines.

## Validation qualité (`src/clean/validate_dataset.py`)

Contrôles automatisés sur `data/processed/dataset_final.csv` :

- présence des colonnes requises (`reference_ai4i`, `type_produit`, mesures capteur, `panne`)
- doublons
- valeurs manquantes par colonne
- plages de valeurs plausibles par capteur (`RANGE_CHECKS`) : température air/process 250–350 K, vitesse de rotation 0–3000 rpm, couple 0–100 Nm, usure outil 0–300 min
- verdict global `VALIDE` / `NON VALIDE`, sortie non nulle (`SystemExit(1)`) si invalide

**Intégration CI** : ce script s'exécute juste après `clean_maintenance.py` dans le job `data-and-ml` de `.github/workflows/ci.yml` — un dataset invalide bloque la pipeline avant même l'entraînement des modèles, pas seulement un contrôle manuel ponctuel.
