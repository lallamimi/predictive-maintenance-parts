-- Schema relationnel du projet (compatible PostgreSQL et SQLite).
-- En production, ce schema est cree via les migrations Django (voir src/backend/),
-- ce fichier sert de preuve independante de la competence de modelisation SQL (C2/C4)
-- et de base pour la verification locale des requetes d'analyse (analysis_queries.sql).

CREATE TABLE IF NOT EXISTS fournisseurs (
    fournisseur_id              INTEGER PRIMARY KEY,
    nom                         TEXT NOT NULL,
    fiabilite_score             REAL NOT NULL CHECK (fiabilite_score BETWEEN 0 AND 1),
    delai_moyen_livraison_jours INTEGER NOT NULL CHECK (delai_moyen_livraison_jours >= 0)
);

CREATE TABLE IF NOT EXISTS pieces_rechange (
    piece_id                   INTEGER PRIMARY KEY,
    code_panne_associe         TEXT NOT NULL,
    nom                        TEXT NOT NULL,
    categorie                  TEXT NOT NULL,
    prix_unitaire              REAL NOT NULL CHECK (prix_unitaire > 0),
    fournisseur_id             INTEGER NOT NULL REFERENCES fournisseurs(fournisseur_id),
    stock_actuel               INTEGER NOT NULL CHECK (stock_actuel >= 0),
    seuil_reapprovisionnement  INTEGER NOT NULL CHECK (seuil_reapprovisionnement >= 0)
);

CREATE TABLE IF NOT EXISTS interventions_pieces (
    intervention_id     INTEGER PRIMARY KEY,
    reference_ai4i       INTEGER,
    piece_id            INTEGER NOT NULL REFERENCES pieces_rechange(piece_id),
    nom_piece            TEXT NOT NULL,
    quantite             INTEGER NOT NULL CHECK (quantite > 0),
    date_intervention    DATE NOT NULL,
    cout_total           REAL NOT NULL CHECK (cout_total >= 0)
);

CREATE INDEX IF NOT EXISTS idx_pieces_fournisseur ON pieces_rechange (fournisseur_id);
CREATE INDEX IF NOT EXISTS idx_interventions_piece ON interventions_pieces (piece_id);
CREATE INDEX IF NOT EXISTS idx_interventions_date ON interventions_pieces (date_intervention);
