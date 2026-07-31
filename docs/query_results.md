# Resultats des requetes d'analyse (`analysis_queries.sql`)

Genere automatiquement par `src/sql/run_queries.py` a partir des donnees synthetiques.

## 1) Cout total et nombre d'interventions par piece, du plus couteux au moins couteux.

| piece                    | categorie       |   nb_interventions |   cout_cumule |
|:-------------------------|:----------------|-------------------:|--------------:|
| Radiateur                | refroidissement |                115 |      52825.6  |
| Alternateur              | electrique      |                 95 |      52286.4  |
| Courroie de distribution | usure           |                 98 |      12486.8  |
| Disque d'embrayage       | usure           |                 46 |       5426.64 |
| Capteur moteur           | electronique    |                  1 |         79.66 |

## 2) Delai moyen de livraison par fournisseur, pondere par le nombre de pieces qu'il fournit.

| fournisseur              |   fiabilite_score |   delai_moyen_livraison_jours |   nb_pieces_fournies |
|:-------------------------|------------------:|------------------------------:|---------------------:|
| TransAuto Fournitures    |              0.9  |                             9 |                    0 |
| AutoPieces Ile-de-France |              0.91 |                             8 |                    1 |
| GarageDirect Pro         |              0.93 |                             6 |                    0 |
| MecaStock 92             |              0.88 |                             4 |                    2 |
| PieceRapide SARL         |              0.97 |                             2 |                    2 |

## 3) Pieces actuellement sous leur seuil de reapprovisionnement.

| nom   | categorie   | stock_actuel   | seuil_reapprovisionnement   | deficit   |
|-------|-------------|----------------|-----------------------------|-----------|

## 4) Repartition mensuelle des interventions (tendance temporelle).

| mois    |   nb_interventions |   cout_mensuel |
|:--------|-------------------:|---------------:|
| 2024-08 |                  8 |        2149.96 |
| 2024-09 |                 17 |        5833.63 |
| 2024-10 |                 11 |        3191.44 |
| 2024-11 |                 11 |        4946.55 |
| 2024-12 |                 20 |        5995.34 |
| 2025-01 |                 19 |        5610.54 |
| 2025-02 |                 12 |        3760.8  |
| 2025-03 |                 14 |        3952.95 |
| 2025-04 |                 17 |        5068.39 |
| 2025-05 |                 14 |        4445.18 |
| 2025-06 |                 16 |        5522.94 |
| 2025-07 |                 12 |        5049.13 |
| 2025-08 |                 20 |        7518.78 |
| 2025-09 |                 12 |        4538.83 |
| 2025-10 |                 12 |        4010.81 |
| 2025-11 |                 11 |        3105.17 |
| 2025-12 |                 19 |        6374.16 |
| 2026-01 |                 16 |        5664.96 |
| 2026-02 |                 11 |        4954.07 |
| 2026-03 |                 13 |        5897.12 |
| 2026-04 |                 24 |       10062.3  |
| 2026-05 |                 23 |        7561.95 |
| 2026-06 |                 10 |        3588.47 |
| 2026-07 |                 13 |        4301.54 |

## 5) Piece la plus consommee par categorie, avec sa part du cout total de sa categorie.

| categorie       | piece                    |   quantite_totale_consommee |   part_cout_categorie_pct |
|:----------------|:-------------------------|----------------------------:|--------------------------:|
| electrique      | Alternateur              |                         147 |                     100   |
| electronique    | Capteur moteur           |                           1 |                     100   |
| refroidissement | Radiateur                |                         173 |                     100   |
| usure           | Courroie de distribution |                         148 |                      69.7 |
| usure           | Disque d'embrayage       |                          72 |                      30.3 |
