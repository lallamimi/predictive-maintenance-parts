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
| 2024-08 |                  6 |        1760.24 |
| 2024-09 |                 15 |        4520.55 |
| 2024-10 |                 15 |        4894.24 |
| 2024-11 |                 11 |        4946.55 |
| 2024-12 |                 17 |        5370.51 |
| 2025-01 |                 22 |        6235.37 |
| 2025-02 |                 10 |        3380.08 |
| 2025-03 |                 13 |        3469.86 |
| 2025-04 |                 16 |        4816.97 |
| 2025-05 |                 14 |        4358.91 |
| 2025-06 |                 20 |        6724.44 |
| 2025-07 |                 10 |        4575.04 |
| 2025-08 |                 17 |        6512.95 |
| 2025-09 |                 14 |        4628.61 |
| 2025-10 |                 13 |        4689.57 |
| 2025-11 |                 13 |        3816.55 |
| 2025-12 |                 17 |        5578.41 |
| 2026-01 |                 15 |        5690.27 |
| 2026-02 |                 13 |        5013.13 |
| 2026-03 |                 11 |        5457.06 |
| 2026-04 |                 22 |        9061.91 |
| 2026-05 |                 25 |        8749.32 |
| 2026-06 |                 10 |        3773.52 |
| 2026-07 |                 15 |        4912.24 |
| 2026-08 |                  1 |         168.74 |

## 5) Piece la plus consommee par categorie, avec sa part du cout total de sa categorie.

| categorie       | piece                    |   quantite_totale_consommee |   part_cout_categorie_pct |
|:----------------|:-------------------------|----------------------------:|--------------------------:|
| electrique      | Alternateur              |                         147 |                     100   |
| electronique    | Capteur moteur           |                           1 |                     100   |
| refroidissement | Radiateur                |                         173 |                     100   |
| usure           | Courroie de distribution |                         148 |                      69.7 |
| usure           | Disque d'embrayage       |                          72 |                      30.3 |
