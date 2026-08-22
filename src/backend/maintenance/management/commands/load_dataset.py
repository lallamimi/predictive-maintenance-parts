"""
Commande Django d'import des donnees collectees/nettoyees dans la base (competence C4).

Charge, dans cet ordre (dependances FK) :
    data/synthetic/fournisseurs.csv       -> inventory.Fournisseur
    data/synthetic/pieces_rechange.csv    -> inventory.PieceRechange
    data/processed/dataset_final.csv      -> maintenance.LectureCapteur + InterventionPiece

Usage :
    python manage.py load_dataset
    python manage.py load_dataset --reset   (vide les tables avant import)
"""

import os
from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from inventory.models import Fournisseur, PieceRechange
from maintenance.models import InterventionPiece, LectureCapteur


def _resolve_data_dir() -> Path:
    """cf. ml_api/model_registry.py : meme classe de bug (IndexError sur
    parents[N] evalue sans condition), meme correction (paresseux, pilote
    par variable d'environnement en conteneur ou la structure de dossiers
    est aplatie)."""
    env_value = os.getenv("DATA_DIR")
    if env_value:
        return Path(env_value)
    return Path(__file__).resolve().parents[5] / "data"  # .../predictive-maintenance-parts/data


DATA_DIR = _resolve_data_dir()
SYNTHETIC_DIR = DATA_DIR / "synthetic"
PROCESSED_PATH = DATA_DIR / "processed" / "dataset_final.csv"


class Command(BaseCommand):
    help = "Importe les donnees collectees/nettoyees (fournisseurs, pieces, lectures, interventions)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Vide les tables avant import")

    @transaction.atomic
    def handle(self, *args, **options):
        if not PROCESSED_PATH.exists():
            self.stderr.write(
                "ERREUR : dataset_final.csv introuvable. Executez d'abord la chaine de collecte/nettoyage."
            )
            return

        if options["reset"]:
            InterventionPiece.objects.all().delete()
            LectureCapteur.objects.all().delete()
            PieceRechange.objects.all().delete()
            Fournisseur.objects.all().delete()
            self.stdout.write("Tables videes.")

        n_fournisseurs = self._load_fournisseurs()
        n_pieces = self._load_pieces()
        n_lectures, n_interventions = self._load_lectures_et_interventions()

        self.stdout.write(self.style.SUCCESS(
            f"Import termine : {n_fournisseurs} fournisseurs, {n_pieces} pieces, "
            f"{n_lectures} lectures, {n_interventions} interventions."
        ))

    def _load_fournisseurs(self) -> int:
        df = pd.read_csv(SYNTHETIC_DIR / "fournisseurs.csv")
        count = 0
        for _, row in df.iterrows():
            _, created = Fournisseur.objects.update_or_create(
                id=int(row["fournisseur_id"]),
                defaults={
                    "nom": row["nom"],
                    "fiabilite_score": float(row["fiabilite_score"]),
                    "delai_moyen_livraison_jours": int(row["delai_moyen_livraison_jours"]),
                },
            )
            count += 1
        return count

    def _load_pieces(self) -> int:
        df = pd.read_csv(SYNTHETIC_DIR / "pieces_rechange.csv")
        count = 0
        for _, row in df.iterrows():
            _, created = PieceRechange.objects.update_or_create(
                id=int(row["piece_id"]),
                defaults={
                    "code_panne_associe": row["code_panne_associe"],
                    "nom": row["nom"],
                    "categorie": row["categorie"],
                    "prix_unitaire": float(row["prix_unitaire"]),
                    "fournisseur_id": int(row["fournisseur_id"]),
                    "stock_actuel": int(row["stock_actuel"]),
                    "seuil_reapprovisionnement": int(row["seuil_reapprovisionnement"]),
                },
            )
            count += 1
        return count

    def _load_lectures_et_interventions(self) -> tuple[int, int]:
        df = pd.read_csv(PROCESSED_PATH)

        lectures_uniques = df.drop_duplicates(subset=["reference_ai4i"])
        n_lectures = 0
        for _, row in lectures_uniques.iterrows():
            LectureCapteur.objects.update_or_create(
                reference_ai4i=int(row["reference_ai4i"]),
                defaults={
                    "type_produit": row["type_produit"],
                    "temperature_air_k": float(row["temperature_air_k"]),
                    "temperature_process_k": float(row["temperature_process_k"]),
                    "vitesse_rotation_rpm": float(row["vitesse_rotation_rpm"]),
                    "couple_nm": float(row["couple_nm"]),
                    "usure_outil_min": float(row["usure_outil_min"]),
                    "panne": bool(row["panne"]),
                    "panne_twf": bool(row["panne_twf"]),
                    "panne_hdf": bool(row["panne_hdf"]),
                    "panne_pwf": bool(row["panne_pwf"]),
                    "panne_osf": bool(row["panne_osf"]),
                    "panne_rnf": bool(row["panne_rnf"]),
                },
            )
            n_lectures += 1

        n_interventions = 0
        interventions_df = df.dropna(subset=["piece_id"])
        InterventionPiece.objects.all().delete()  # eviter les doublons si la commande est relancee sans --reset
        for _, row in interventions_df.iterrows():
            lecture = LectureCapteur.objects.get(reference_ai4i=int(row["reference_ai4i"]))
            InterventionPiece.objects.create(
                lecture=lecture,
                piece_id=int(row["piece_id"]),
                quantite=int(row["quantite"]),
                date_intervention=row["date_intervention"],
                cout_total=float(row["cout_total"]),
            )
            n_interventions += 1

        return n_lectures, n_interventions
