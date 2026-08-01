from django.conf import settings
from django.db import models


class ModelPredictionLog(models.Model):
    """Journal de chaque appel aux modeles IA (competence C11 - monitoring du modele)."""

    class Endpoint(models.TextChoices):
        FAILURE = "predict-failure", "Prédiction de panne"
        DEMAND = "predict-demand", "Prévision de demande"

    endpoint = models.CharField(max_length=32, choices=Endpoint.choices)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    horodatage = models.DateTimeField(auto_now_add=True)
    latence_ms = models.FloatField()
    succes = models.BooleanField(default=True)
    resultat_resume = models.CharField(max_length=200, blank=True)
    message_erreur = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["-horodatage"]

    def __str__(self) -> str:
        return f"{self.endpoint} @ {self.horodatage:%Y-%m-%d %H:%M} ({'OK' if self.succes else 'ERREUR'})"
