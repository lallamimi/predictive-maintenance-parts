"""Journalisation applicative de chaque requete HTTP (competence C20).

Distinct de ml_api.ModelPredictionLog (competence C11, specifique aux deux
endpoints de prediction) : ce middleware couvre TOUTE l'application (auth,
donnees, recommandations, health...), pas seulement les modeles IA.

Format aligne sur l'exemple du referentiel :
    <horodatage> | <methode> <chemin> | <statut> | latency_ms=<X> | user=<username|anon>
"""

import logging
import time

logger = logging.getLogger("maintenance")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        debut = time.perf_counter()
        response = self.get_response(request)
        latence_ms = (time.perf_counter() - debut) * 1000

        user = getattr(request, "user", None)
        username = user.username if user and user.is_authenticated else "anon"

        niveau = logger.warning if response.status_code >= 500 else logger.info
        niveau(
            "%s %s | %s | latency_ms=%.1f | user=%s",
            request.method,
            request.path,
            response.status_code,
            latence_ms,
            username,
        )

        return response
