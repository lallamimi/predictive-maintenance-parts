# Dictionnaire de données (C1/C3)

## 1. Données brutes AI4I (`data/raw/ai4i2020_raw.csv`)

Noms de colonnes originaux du dataset UCI (avant nettoyage/renommage).

| Colonne | Type | Description | Domaine |
|---|---|---|---|
| `Type` | catégorielle | Qualité/gamme de la machine | `L` (low), `M` (medium), `H` (high) |
| `Air temperature` | numérique | Température de l'air ambiant | Kelvin, ~295–305 |
| `Process temperature` | numérique | Température du procédé | Kelvin, ~305–314 |
| `Rotational speed` | numérique | Vitesse de rotation | tr/min (rpm) |
| `Torque` | numérique | Couple mécanique | Newton-mètre (Nm) |
| `Tool wear` | numérique | Usure cumulée de l'outil | minutes |
| `Machine failure` | booléen (0/1) | Panne machine détectée (cible principale) | 0 ou 1 |
| `TWF` | booléen (0/1) | Tool Wear Failure — panne par usure d'outil | 0 ou 1 |
| `HDF` | booléen (0/1) | Heat Dissipation Failure — panne de dissipation thermique | 0 ou 1 |
| `PWF` | booléen (0/1) | Power Failure — panne de puissance | 0 ou 1 |
| `OSF` | booléen (0/1) | Overstrain Failure — panne de surcharge mécanique | 0 ou 1 |
| `RNF` | booléen (0/1) | Random Failure — panne aléatoire, non corrélée aux mesures | 0 ou 1 |

## 2. Données synthétiques (`data/synthetic/`)

### `fournisseurs.csv`

| Colonne | Type | Description |
|---|---|---|
| `fournisseur_id` | entier | Identifiant unique |
| `nom` | texte | Nom de l'entreprise (fictive) |
| `fiabilite_score` | numérique | Score de fiabilité, entre 0.65 et 0.98 |
| `delai_moyen_livraison_jours` | entier | Délai moyen de livraison, entre 2 et 12 jours |

### `pieces_rechange.csv`

| Colonne | Type | Description |
|---|---|---|
| `piece_id` | entier | Identifiant unique |
| `code_panne_associe` | texte | Mode de panne AI4I rattaché (TWF/HDF/PWF/OSF/RNF) |
| `nom` | texte | Nom de la pièce (ex. Radiateur, Alternateur) |
| `categorie` | catégorielle | `usure`, `refroidissement`, `electrique`, `electronique` |
| `prix_unitaire` | numérique | Prix en euros, selon fourchette par catégorie |
| `fournisseur_id` | entier | Référence vers `fournisseurs.csv` |
| `stock_actuel` | entier | Quantité en stock (30–80 pour pièces d'usure, 5–25 sinon) |
| `seuil_reapprovisionnement` | entier | Seuil d'alerte stock (15–30 pour pièces d'usure, 3–10 sinon) |

### `interventions_pieces.csv`

| Colonne | Type | Description |
|---|---|---|
| `intervention_id` | entier | Identifiant unique, séquentiel |
| `reference_ai4i` | entier | Référence vers la ligne AI4I à l'origine de l'intervention |
| `piece_id` | entier | Référence vers `pieces_rechange.csv` |
| `nom_piece` | texte | Nom de la pièce consommée (dénormalisé pour lisibilité) |
| `quantite` | entier | Quantité consommée (1 ou 2) |
| `date_intervention` | date (`AAAA-MM-JJ`) | Date de l'intervention, tirée dans les 2 dernières années |
| `cout_total` | numérique | `quantite × prix_unitaire` de la pièce |

## 3. Dataset final fusionné (`data/processed/dataset_final.csv`)

Produit par `src/clean/clean_maintenance.py` — 22 colonnes, fusion des deux sources ci-dessus (jointure gauche sur `reference_ai4i`).

| Colonne | Origine | Description |
|---|---|---|
| `reference_ai4i` | AI4I (index) | Identifiant de la lecture capteur, clé de fusion |
| `type_produit` | AI4I `Type` | Gamme machine (L/M/H) |
| `temperature_air_k` | AI4I `Air temperature` | Température air, Kelvin |
| `temperature_process_k` | AI4I `Process temperature` | Température procédé, Kelvin |
| `vitesse_rotation_rpm` | AI4I `Rotational speed` | Vitesse de rotation, tr/min |
| `couple_nm` | AI4I `Torque` | Couple, Nm |
| `usure_outil_min` | AI4I `Tool wear` | Usure outil, minutes |
| `panne` | AI4I `Machine failure` | Panne détectée (cible du modèle de prédiction) |
| `panne_twf`, `panne_hdf`, `panne_pwf`, `panne_osf`, `panne_rnf` | AI4I `TWF/HDF/PWF/OSF/RNF` | Modes de panne détaillés |
| `intervention_id` | synthétique | Intervention associée (vide si pas de panne exploitée) |
| `piece_id`, `nom_piece`, `categorie`, `prix_unitaire`, `fournisseur_id` | synthétique (`pieces_rechange.csv`) | Détail de la pièce consommée |
| `quantite`, `date_intervention`, `cout_total` | synthétique (`interventions_pieces.csv`) | Détail de l'intervention |

**Plages de valeurs plausibles contrôlées** (`src/clean/validate_dataset.py`, `RANGE_CHECKS`) : température air/process 250–350 K, vitesse de rotation 0–3000 rpm, couple 0–100 Nm, usure outil 0–300 min.
