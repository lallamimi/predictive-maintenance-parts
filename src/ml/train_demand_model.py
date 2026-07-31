"""
Entrainement du modele de prevision de la demande de pieces de rechange
(mission 4 du sujet).

Approche : agregation mensuelle de la consommation par piece, feature
engineering de type serie temporelle (mois, decalage 1 mois, moyenne
glissante 3 mois), regression pour predire la demande du mois suivant.

Limite assumee et documentee : le volume de donnees synthetiques disponible
est faible (~355 interventions sur 5 pieces / ~24 mois), ce qui limite la
robustesse statistique du modele. C'est un choix delibere pour ce projet
fictif plutot qu'une generation de donnees artificiellement massive qui
donnerait une fausse impression de robustesse.

Usage :
    python src/ml/train_demand_model.py
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import OneHotEncoder

BASE_DIR = Path(__file__).resolve().parents[2]
INTERVENTIONS_PATH = BASE_DIR / "data" / "synthetic" / "interventions_pieces.csv"
PIECES_PATH = BASE_DIR / "data" / "synthetic" / "pieces_rechange.csv"
MODELS_DIR = BASE_DIR / "data" / "processed" / "models"


def build_monthly_demand(interventions: pd.DataFrame, pieces: pd.DataFrame) -> pd.DataFrame:
    """Construit une grille complete (piece x mois) avec la demande, en completant
    par des zeros les mois sans intervention (regle metier : absence d'intervention
    = demande nulle, pas une donnee manquante)."""
    interventions = interventions.copy()
    interventions["mois"] = pd.to_datetime(interventions["date_intervention"]).dt.to_period("M")

    demande = interventions.groupby(["piece_id", "mois"])["quantite"].sum().reset_index()
    demande = demande.rename(columns={"quantite": "demande"})

    tous_mois = pd.period_range(interventions["mois"].min(), interventions["mois"].max(), freq="M")
    grille = pd.MultiIndex.from_product([pieces["piece_id"], tous_mois], names=["piece_id", "mois"]).to_frame(index=False)

    complet = grille.merge(demande, on=["piece_id", "mois"], how="left")
    complet["demande"] = complet["demande"].fillna(0)
    complet = complet.merge(pieces[["piece_id", "categorie"]], on="piece_id", how="left")
    complet = complet.sort_values(["piece_id", "mois"]).reset_index(drop=True)
    return complet


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["mois_numero"] = df["mois"].dt.month
    df["lag_1"] = df.groupby("piece_id")["demande"].shift(1)
    df["rolling_mean_3"] = (
        df.groupby("piece_id")["demande"].shift(1).rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
    )
    return df.dropna(subset=["lag_1"])  # premiere observation de chaque piece sans historique


def main() -> None:
    if not INTERVENTIONS_PATH.exists():
        print(f"ERREUR : {INTERVENTIONS_PATH} introuvable. Executez d'abord generate_synthetic_parts.py")
        raise SystemExit(1)

    interventions = pd.read_csv(INTERVENTIONS_PATH)
    pieces = pd.read_csv(PIECES_PATH)

    monthly = build_monthly_demand(interventions, pieces)
    featured = add_features(monthly)
    print(f"Observations (piece x mois) exploitables apres feature engineering : {len(featured)}")

    # Split chronologique (pas aleatoire) : plus realiste pour une serie temporelle -
    # on entraine sur le passe, on teste sur les derniers mois observes.
    featured = featured.sort_values("mois")
    cutoff = featured["mois"].quantile(0.8, interpolation="lower")
    train = featured[featured["mois"] <= cutoff]
    test = featured[featured["mois"] > cutoff]
    print(f"Train : {len(train)} lignes | Test : {len(test)} lignes (coupure : {cutoff})")

    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    cat_train = encoder.fit_transform(train[["categorie"]])
    cat_test = encoder.transform(test[["categorie"]])

    feature_cols = ["mois_numero", "lag_1", "rolling_mean_3"]
    X_train = np.hstack([train[feature_cols].values, cat_train])
    X_test = np.hstack([test[feature_cols].values, cat_test])
    y_train, y_test = train["demande"], test["demande"]

    model = RandomForestRegressor(n_estimators=200, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    if len(test) > 0:
        y_pred = model.predict(X_test)
        print("\n--- Modele de prevision de demande (RandomForestRegressor) ---")
        print(f"MAE  : {mean_absolute_error(y_test, y_pred):.2f} unites")
        print(f"RMSE : {mean_squared_error(y_test, y_pred) ** 0.5:.2f} unites")
    else:
        print("\nPas assez de mois pour un jeu de test distinct - modele entraine sur toutes les donnees.")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "encoder": encoder, "feature_cols": feature_cols}, MODELS_DIR / "demand_model.pkl")
    print(f"Modele sauvegarde : {MODELS_DIR / 'demand_model.pkl'}")


if __name__ == "__main__":
    main()
