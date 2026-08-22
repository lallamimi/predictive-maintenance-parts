"""
Entrainement du modele de prediction de panne (mission 3 du sujet, competence C9 en amont).

Classification binaire : a partir des mesures capteur, predire si une panne survient
(colonne `panne`, derivee de "Machine failure" du dataset AI4I 2020).

Usage :
    python src/ml/train_failure_model.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
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
METRICS_PATH = BASE_DIR / "docs" / "ml_metrics.json"

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

    # Benchmark de plusieurs algorithmes sur le meme split/preprocessing, pour
    # justifier le choix de XGBoost par des chiffres plutot que par defaut
    # (voir docs/choix_modele_ml.md). XGBoost reste le modele sauvegarde/deploye.
    candidats = {
        "regression_logistique": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "random_forest": RandomForestClassifier(
            n_estimators=300, max_depth=8, class_weight="balanced", random_state=42, n_jobs=-1
        ),
        "xgboost": XGBClassifier(
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
    }

    resultats = {}
    model = None
    print("\n--- Comparaison d'algorithmes (meme split, meme preprocessing) ---")
    for nom, clf in candidats.items():
        pipeline = Pipeline(steps=[("prep", preprocess), ("clf", clf)])
        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1]

        metriques = {
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "f1_score": round(f1_score(y_test, y_pred), 4),
            "roc_auc": round(roc_auc_score(y_test, y_proba), 4),
            "precision": round(precision_score(y_test, y_pred), 4),
            "recall": round(recall_score(y_test, y_pred), 4),
        }
        resultats[nom] = metriques
        print(
            f"{nom:25s} accuracy={metriques['accuracy']:.4f} f1={metriques['f1_score']:.4f} "
            f"roc_auc={metriques['roc_auc']:.4f} precision={metriques['precision']:.4f} recall={metriques['recall']:.4f}"
        )

        if nom == "xgboost":
            model = pipeline  # modele retenu et deploye, voir docs/choix_modele_ml.md pour la justification

    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(
        json.dumps(
            {
                "genere_le": datetime.now(timezone.utc).isoformat(),
                "dataset_lignes": len(df),
                "modele_retenu": "xgboost",
                "resultats": resultats,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nMetriques comparatives sauvegardees : {METRICS_PATH}")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODELS_DIR / "failure_model.pkl")
    print(f"Modele sauvegarde : {MODELS_DIR / 'failure_model.pkl'}")


if __name__ == "__main__":
    main()
