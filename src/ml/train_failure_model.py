"""
Entrainement du modele de prediction de panne (mission 3 du sujet, competence C9 en amont).

Classification binaire : a partir des mesures capteur, predire si une panne survient
(colonne `panne`, derivee de "Machine failure" du dataset AI4I 2020).

Usage :
    python src/ml/train_failure_model.py
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_DIR / "data" / "processed" / "dataset_final.csv"
MODELS_DIR = BASE_DIR / "data" / "processed" / "models"

FEATURES_NUM = [
    "temperature_air_k",
    "temperature_process_k",
    "vitesse_rotation_rpm",
    "couple_nm",
    "usure_outil_min",
]
FEATURE_CAT = "type_produit"
TARGET = "panne"


def main() -> None:
    if not DATASET_PATH.exists():
        print(f"ERREUR : {DATASET_PATH} introuvable. Executez d'abord src/clean/clean_maintenance.py")
        raise SystemExit(1)

    df = pd.read_csv(DATASET_PATH)
    # Une ligne par lecture capteur (le dataset_final contient des doublons de lecture
    # quand une meme panne a consomme plusieurs pieces - non pertinent pour ce modele).
    df = df.drop_duplicates(subset=["reference_ai4i"]).copy()
    print(f"Lignes uniques pour l'entrainement : {len(df)}")

    X = df[FEATURES_NUM + [FEATURE_CAT]]
    y = df[TARGET].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    preprocess = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), FEATURES_NUM),
            ("cat", OneHotEncoder(handle_unknown="ignore"), [FEATURE_CAT]),
        ]
    )

    pos = int(y_train.sum())
    neg = int((1 - y_train).sum())
    scale_pos_weight = neg / max(pos, 1)
    print(f"scale_pos_weight={scale_pos_weight:.2f} (neg={neg}, pos={pos})")

    model = Pipeline(
        steps=[
            ("prep", preprocess),
            (
                "clf",
                XGBClassifier(
                    n_estimators=300,
                    learning_rate=0.05,
                    max_depth=4,
                    subsample=0.9,
                    colsample_bytree=0.9,
                    scale_pos_weight=scale_pos_weight,
                    random_state=42,
                    eval_metric="logloss",
                    n_jobs=-1,
                ),
            ),
        ]
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print("\n--- Modele de prediction de panne (XGBoost) ---")
    print(f"Accuracy  : {accuracy_score(y_test, y_pred):.4f}")
    print(f"F1 Score  : {f1_score(y_test, y_pred):.4f}")
    print(f"ROC-AUC   : {roc_auc_score(y_test, y_proba):.4f}")
    print(f"Precision : {precision_score(y_test, y_pred):.4f}")
    print(f"Recall    : {recall_score(y_test, y_pred):.4f}")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODELS_DIR / "failure_model.pkl")
    print(f"\nModele sauvegarde : {MODELS_DIR / 'failure_model.pkl'}")


if __name__ == "__main__":
    main()
