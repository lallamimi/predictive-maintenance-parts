# Spécifications des données (C1)

## Sources

| Source | Nature | Accès | Script |
|---|---|---|---|
| AI4I 2020 Predictive Maintenance Dataset | Réelle, publique | UCI Machine Learning Repository (ID 601), package `ucimlrepo` avec repli sur téléchargement CSV direct | `src/collect/download_ai4i.py` |
| Fournisseurs / pièces / interventions | Générée, règles métier documentées | Aucune source publique équivalente (voir justification ci-dessous) | `src/collect/generate_synthetic_parts.py` |

## Contraintes

| Contrainte | AI4I | Synthétique |
|---|---|---|
| Accès | Public, gratuit, sans authentification, licence CC BY 4.0 | N/A (généré localement) |
| Format | CSV, 12 colonnes | CSV, 3 fichiers (`fournisseurs.csv`, `pieces_rechange.csv`, `interventions_pieces.csv`) |
| Fréquence | Ponctuelle, rejouée à chaque exécution de la CI (`.github/workflows/ci.yml`, job `data-and-ml`) | Idem — régénérée à chaque run, seed fixe (`SEED = 42`) pour la reproductibilité |
| Confidentialité | Aucune donnée personnelle — mesures de capteurs industriels | Aucune donnée personnelle — entités commerciales fictives |
| Volumétrie | 10 000 lignes × 12 colonnes | 5 fournisseurs, 5 pièces, 355 interventions |

## Pourquoi une partie générée

Aucun dataset public ne couvre à la fois les pannes machine et la gestion de stock de pièces de rechange automobile. Cette partie est donc simulée selon 3 règles métier explicites (documentées en tête de `generate_synthetic_parts.py`, pas de tirage aléatoire "nu") :

1. **Correspondance mode de panne → pièce consommée** : les 5 modes de panne AI4I (TWF, HDF, PWF, OSF, RNF) sont chacun rattachés à une pièce automobile plausible (ex. TWF → Disque d'embrayage, HDF → Radiateur).
2. **Stock et réapprovisionnement** : les pièces d'usure ont un stock et un seuil plus élevés (consommation plus fréquente) que les pièces électriques/électroniques.
3. **Coût et délai** : chaque pièce est rattachée à un fournisseur (fiabilité, délai moyen) ; le coût d'une intervention = quantité × prix unitaire.

## Pré-requis d'exécution

1. `python src/collect/download_ai4i.py` — doit s'exécuter en premier (produit `data/raw/ai4i2020_raw.csv`)
2. `python src/collect/generate_synthetic_parts.py` — dépend du fichier ci-dessus (modes de panne réels utilisés pour générer les interventions)
3. `python src/clean/clean_maintenance.py` — fusionne les deux
4. `python src/clean/validate_dataset.py` — contrôle qualité du résultat final

Voir [`docs/cleaning_rules.md`](cleaning_rules.md) pour les règles de nettoyage et [`data_dictionary.md`](data_dictionary.md) pour le détail colonne par colonne.
