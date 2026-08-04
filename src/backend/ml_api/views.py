import logging
import time
from datetime import date

import numpy as np
import pandas as pd
from django.db.models import Avg
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory.models import PieceRechange
from maintenance.models import InterventionPiece

from .model_registry import ModeleIndisponible, get_demand_model, get_failure_model
from .models import ModelPredictionLog
from .serializers import PredictDemandInputSerializer, PredictFailureInputSerializer

logger = logging.getLogger("maintenance")


def _log_prediction(endpoint, user, latence_ms, succes, resultat_resume="", message_erreur=""):
    """Persiste un appel de prediction (competence C11). Ne doit jamais faire
    echouer la requete principale : toute erreur ici est seulement journalisee."""
    try:
        ModelPredictionLog.objects.create(
            endpoint=endpoint,
            utilisateur=user if user and user.is_authenticated else None,
            latence_ms=latence_ms,
            succes=succes,
            resultat_resume=resultat_resume[:200],
            message_erreur=message_erreur[:500],
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Echec de journalisation de prediction : %s", exc)


class PredictFailureView(APIView):
    """
    API modele IA (C9) : expose le modele de prediction de panne entraine par
    src/ml/train_failure_model.py. Chaque appel est chronometre et journalise (C11).

    POST /api/ml/predict-failure/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        debut = time.perf_counter()
        serializer = PredictFailureInputSerializer(data=request.data)
        if not serializer.is_valid():
            latence = (time.perf_counter() - debut) * 1000
            _log_prediction(
                ModelPredictionLog.Endpoint.FAILURE, request.user, latence, False, message_erreur=str(serializer.errors)
            )
            return Response(serializer.errors, status=400)
        entree = serializer.validated_data

        try:
            model = get_failure_model()
        except ModeleIndisponible as exc:
            latence = (time.perf_counter() - debut) * 1000
            _log_prediction(ModelPredictionLog.Endpoint.FAILURE, request.user, latence, False, message_erreur=str(exc))
            logger.error("predict-failure indisponible : %s", exc)
            return Response({"detail": "Modele de prediction de panne indisponible pour le moment."}, status=503)

        X = pd.DataFrame([entree])
        proba = float(model.predict_proba(X)[0][1])
        prediction = bool(proba >= 0.5)

        if proba >= 0.7:
            niveau = "eleve"
        elif proba >= 0.3:
            niveau = "moyen"
        else:
            niveau = "faible"

        latence = (time.perf_counter() - debut) * 1000
        _log_prediction(
            ModelPredictionLog.Endpoint.FAILURE,
            request.user,
            latence,
            True,
            resultat_resume=f"proba={proba:.3f} niveau={niveau}",
        )
        logger.info("predict-failure user=%s proba=%.3f latence=%.1fms", request.user.username, proba, latence)

        return Response(
            {
                "panne_predite": prediction,
                "probabilite": round(proba, 4),
                "niveau_risque": niveau,
                "modele_version": "xgboost-v1",
            }
        )


class PredictDemandView(APIView):
    """
    API modele IA (C9) : expose le modele de prevision de demande entraine par
    src/ml/train_demand_model.py. Chaque appel est chronometre et journalise (C11).

    POST /api/ml/predict-demand/  body: {"piece_id": <id>}
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        debut = time.perf_counter()
        serializer = PredictDemandInputSerializer(data=request.data)
        if not serializer.is_valid():
            latence = (time.perf_counter() - debut) * 1000
            _log_prediction(
                ModelPredictionLog.Endpoint.DEMAND, request.user, latence, False, message_erreur=str(serializer.errors)
            )
            return Response(serializer.errors, status=400)
        piece_id = serializer.validated_data["piece_id"]

        try:
            piece = PieceRechange.objects.get(pk=piece_id)
        except PieceRechange.DoesNotExist:
            latence = (time.perf_counter() - debut) * 1000
            _log_prediction(
                ModelPredictionLog.Endpoint.DEMAND, request.user, latence, False, message_erreur="piece introuvable"
            )
            return Response({"detail": "Piece introuvable."}, status=404)

        try:
            bundle = get_demand_model()
        except ModeleIndisponible as exc:
            latence = (time.perf_counter() - debut) * 1000
            _log_prediction(ModelPredictionLog.Endpoint.DEMAND, request.user, latence, False, message_erreur=str(exc))
            logger.error("predict-demand indisponible : %s", exc)
            return Response({"detail": "Modele de prevision de demande indisponible pour le moment."}, status=503)

        historique = InterventionPiece.objects.filter(piece_id=piece_id).values("date_intervention", "quantite")
        df = pd.DataFrame(list(historique))

        if df.empty:
            latence = (time.perf_counter() - debut) * 1000
            _log_prediction(
                ModelPredictionLog.Endpoint.DEMAND, request.user, latence, True, resultat_resume="aucun historique"
            )
            return Response(
                {
                    "piece_id": piece_id,
                    "nom_piece": piece.nom,
                    "demande_prevue": 0.0,
                    "avertissement": "Aucun historique d'intervention pour cette piece : prevision non fiable.",
                }
            )

        df["mois"] = pd.to_datetime(df["date_intervention"]).dt.to_period("M")
        demande_mensuelle = df.groupby("mois")["quantite"].sum().sort_index()

        lag_1 = float(demande_mensuelle.iloc[-1])
        rolling_mean_3 = float(demande_mensuelle.tail(3).mean())
        mois_prochain = (date.today().month % 12) + 1

        model = bundle["model"]
        encoder = bundle["encoder"]
        cat_encoded = encoder.transform(pd.DataFrame([[piece.categorie]], columns=["categorie"]))
        X = np.hstack([[[mois_prochain, lag_1, rolling_mean_3]], cat_encoded])

        prediction = float(model.predict(X)[0])
        latence = (time.perf_counter() - debut) * 1000

        _log_prediction(
            ModelPredictionLog.Endpoint.DEMAND,
            request.user,
            latence,
            True,
            resultat_resume=f"piece={piece.nom} prevue={prediction:.1f}",
        )
        logger.info(
            "predict-demand user=%s piece=%s prevue=%.2f latence=%.1fms",
            request.user.username,
            piece.nom,
            prediction,
            latence,
        )

        return Response(
            {
                "piece_id": piece_id,
                "nom_piece": piece.nom,
                "demande_prevue": round(max(prediction, 0), 1),
                "features_utilisees": {
                    "mois_numero": mois_prochain,
                    "lag_1": lag_1,
                    "rolling_mean_3": round(rolling_mean_3, 2),
                },
                "modele_version": "random-forest-v1",
            }
        )


class ModelMonitoringView(APIView):
    """
    Restitution des metriques de monitoring du modele (competence C11).

    GET /api/ml/monitoring/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = {}
        for endpoint, _ in ModelPredictionLog.Endpoint.choices:
            qs = ModelPredictionLog.objects.filter(endpoint=endpoint)
            total = qs.count()
            echecs = qs.filter(succes=False).count()
            stats[endpoint] = {
                "nb_appels": total,
                "nb_echecs": echecs,
                "taux_echec_pct": round(100 * echecs / total, 2) if total else 0,
                "latence_moyenne_ms": round(qs.aggregate(avg=Avg("latence_ms"))["avg"] or 0, 1),
            }

        derniers = list(
            ModelPredictionLog.objects.all()[:10].values(
                "endpoint", "horodatage", "latence_ms", "succes", "resultat_resume"
            )
        )

        return Response({"par_endpoint": stats, "derniers_appels": derniers})
