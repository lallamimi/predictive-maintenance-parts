"""
Explicabilite du modele de prediction de panne via SHAP.

Usage :
    python src/ml/explain.py --reference 42
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
import shap

BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_DIR / "data" / "processed" / "dataset_final.csv"
MODEL_PATH = BASE_DIR / "data" / "processed" / "models" / "failure_model.pkl"

FEATURES_NUM = [
    "temperature_air_k",
    "temperature_process_k",
    "vitesse_rotation_rpm",
    "couple_nm",
    "usure_outil_min",
]
FEATURE_CAT = "type_produit"


def explain_one(reference_ai4i: int) -> None:
    if not MODEL_PATH.exists():
        print(f"ERREUR : {MODEL_PATH} introuvable. Executez d'abord train_failure_model.py")
        raise SystemExit(1)

    model = joblib.load(MODEL_PATH)
    df = pd.read_csv(DATASET_PATH).drop_duplicates(subset=["reference_ai4i"])

    ligne = df[df["reference_ai4i"] == reference_ai4i]
    if ligne.empty:
        print(f"reference_ai4i={reference_ai4i} introuvable.")
        raise SystemExit(1)

    X = ligne[FEATURES_NUM + [FEATURE_CAT]]

    prep = model.named_steps["prep"]
    clf = model.named_steps["clf"]

    X_transformed = prep.transform(X)
    feature_names = list(prep.get_feature_names_out())

    explainer = shap.TreeExplainer(clf)
    shap_values = explainer.shap_values(X_transformed)

    contributions = pd.DataFrame({"feature": feature_names, "shap_value": shap_values[0]})
    contributions["abs_val"] = contributions["shap_value"].abs()
    contributions = contributions.sort_values("abs_val", ascending=False)

    proba = model.predict_proba(X)[0][1]

    print(f"Reference AI4I #{reference_ai4i} - probabilite de panne predite : {proba:.2%}\n")
    print("Contributions SHAP (du plus au moins influent) :")
    for _, row in contributions.head(10).iterrows():
        signe = "+" if row["shap_value"] >= 0 else ""
        print(f"  {row['feature']:35s} {signe}{row['shap_value']:.4f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Explique une prediction du modele de panne via SHAP.")
    parser.add_argument("--reference", type=int, default=None, help="reference_ai4i a expliquer")
    args = parser.parse_args()

    if args.reference is None:
        df = pd.read_csv(DATASET_PATH).drop_duplicates(subset=["reference_ai4i"])
        pannes = df[df["panne"] == 1]
        args.reference = int(pannes.iloc[0]["reference_ai4i"]) if not pannes.empty else int(df.iloc[0]["reference_ai4i"])
        print(f"Aucune reference fournie, utilisation de reference_ai4i={args.reference} a titre d'exemple.\n")

    explain_one(args.reference)


if __name__ == "__main__":
    main()
