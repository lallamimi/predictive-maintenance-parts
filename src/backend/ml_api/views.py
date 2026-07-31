import logging
from datetime import date

import numpy as np
import pandas as pd
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory.models import PieceRechange
from maintenance.models import InterventionPiece

from .model_registry import ModeleIndisponible, get_demand_model, get_failure_model
from .serializers import PredictDemandInputSerializer, PredictFailureInputSerializer

logger = logging.getLogger("maintenance")


class PredictFailureView(APIView):
    """
    API modele IA (C9) : expose le modele de prediction de panne entraine par
    src/ml/train_failure_model.py.

    POST /api/ml/predict-failure/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PredictFailureInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entree = serializer.validated_data

        try:
            model = get_failure_model()
        except ModeleIndisponible as exc:
            logger.error("predict-failure indisponible : %s", exc)
            return Response({"detail": str(exc)}, status=503)

        X = pd.DataFrame([entree])
        proba = float(model.predict_proba(X)[0][1])
        prediction = bool(proba >= 0.5)

        if proba >= 0.7:
            niveau = "eleve"
        elif proba >= 0.3:
            niveau = "moyen"
        else:
            niveau = "faible"

        logger.info("predict-failure user=%s proba=%.3f", request.user.username, proba)

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
    src/ml/train_demand_model.py.

    POST /api/ml/predict-demand/  body: {"piece_id": <id>}
    Calcule automatiquement les features (mois, lag, moyenne glissante) a partir
    de l'historique reel des interventions en base - l'appelant n'a besoin de
    fournir que l'identifiant de la piece.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PredictDemandInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        piece_id = serializer.validated_data["piece_id"]

        try:
            piece = PieceRechange.objects.get(pk=piece_id)
        except PieceRechange.DoesNotExist:
            return Response({"detail": "Piece introuvable."}, status=404)

        try:
            bundle = get_demand_model()
        except ModeleIndisponible as exc:
            logger.error("predict-demand indisponible : %s", exc)
            return Response({"detail": str(exc)}, status=503)

        historique = (
            InterventionPiece.objects.filter(piece_id=piece_id)
            .values("date_intervention", "quantite")
        )
        df = pd.DataFrame(list(historique))

        if df.empty:
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

        logger.info("predict-demand user=%s piece=%s prevue=%.2f", request.user.username, piece.nom, prediction)

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
