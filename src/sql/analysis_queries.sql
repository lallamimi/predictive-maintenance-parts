-- Requetes d'analyse documentees (competence C2).
-- Executees et verifiees via src/sql/run_queries.py, resultats dans docs/query_results.md.

-- 1) Cout total et nombre d'interventions par piece, du plus couteux au moins couteux.
--    Objectif : identifier les pieces qui pesent le plus sur le budget maintenance.
SELECT
    p.nom AS piece,
    p.categorie,
    COUNT(ip.intervention_id) AS nb_interventions,
    SUM(ip.cout_total) AS cout_cumule
FROM interventions_pieces ip
JOIN pieces_rechange p ON p.piece_id = ip.piece_id
GROUP BY p.nom, p.categorie
ORDER BY cout_cumule DESC;

-- 2) Delai moyen de livraison par fournisseur, pondere par le nombre de pieces qu'il fournit.
--    Objectif : identifier les fournisseurs a risque (delai long) sur des pieces critiques.
SELECT
    f.nom AS fournisseur,
    f.fiabilite_score,
    f.delai_moyen_livraison_jours,
    COUNT(p.piece_id) AS nb_pieces_fournies
FROM fournisseurs f
LEFT JOIN pieces_rechange p ON p.fournisseur_id = f.fournisseur_id
GROUP BY f.nom, f.fiabilite_score, f.delai_moyen_livraison_jours
ORDER BY f.delai_moyen_livraison_jours DESC;

-- 3) Pieces actuellement sous leur seuil de reapprovisionnement.
--    Objectif : liste d'alerte stock (utilisee par le dashboard et les recommandations IA).
SELECT
    nom,
    categorie,
    stock_actuel,
    seuil_reapprovisionnement,
    (seuil_reapprovisionnement - stock_actuel) AS deficit
FROM pieces_rechange
WHERE stock_actuel < seuil_reapprovisionnement
ORDER BY deficit DESC;

-- 4) Repartition mensuelle des interventions (tendance temporelle).
--    Objectif : identifier une saisonnalite ou une derive du taux de panne.
SELECT
    strftime('%Y-%m', date_intervention) AS mois,
    COUNT(*) AS nb_interventions,
    SUM(cout_total) AS cout_mensuel
FROM interventions_pieces
GROUP BY mois
ORDER BY mois;

-- 5) Piece la plus consommee par categorie, avec sa part du cout total de sa categorie.
--    Objectif : prioriser les categories de pieces a surveiller de pres.
SELECT
    p.categorie,
    p.nom AS piece,
    SUM(ip.quantite) AS quantite_totale_consommee,
    ROUND(100.0 * SUM(ip.cout_total) / (
        SELECT SUM(ip2.cout_total)
        FROM interventions_pieces ip2
        JOIN pieces_rechange p2 ON p2.piece_id = ip2.piece_id
        WHERE p2.categorie = p.categorie
    ), 1) AS part_cout_categorie_pct
FROM interventions_pieces ip
JOIN pieces_rechange p ON p.piece_id = ip.piece_id
GROUP BY p.categorie, p.nom
ORDER BY p.categorie, quantite_totale_consommee DESC;
