from django.db import models

from inventory.models import PieceRechange


class LectureCapteur(models.Model):
    """Une ligne de mesure capteur issue du dataset AI4I 2020 (reformule contexte
    automobile), avec les indicateurs de panne associes."""

    reference_ai4i = models.IntegerField(unique=True)
    type_produit = models.CharField(max_length=8)
    temperature_air_k = models.FloatField()
    temperature_process_k = models.FloatField()
    vitesse_rotation_rpm = models.FloatField()
    couple_nm = models.FloatField()
    usure_outil_min = models.FloatField()
    panne = models.BooleanField(default=False)
    panne_twf = models.BooleanField(default=False)
    panne_hdf = models.BooleanField(default=False)
    panne_pwf = models.BooleanField(default=False)
    panne_osf = models.BooleanField(default=False)
    panne_rnf = models.BooleanField(default=False)

    class Meta:
        ordering = ["reference_ai4i"]

    def __str__(self) -> str:
        return f"Lecture #{self.reference_ai4i} (panne={self.panne})"


class InterventionPiece(models.Model):
    """Une intervention de maintenance ayant consomme une piece de rechange."""

    lecture = models.ForeignKey(
        LectureCapteur, on_delete=models.CASCADE, related_name="interventions", null=True, blank=True
    )
    piece = models.ForeignKey(PieceRechange, on_delete=models.PROTECT, related_name="interventions")
    quantite = models.PositiveIntegerField()
    date_intervention = models.DateField()
    cout_total = models.FloatField()

    class Meta:
        ordering = ["-date_intervention"]

    def __str__(self) -> str:
        return f"Intervention {self.date_intervention} - {self.piece.nom} x{self.quantite}"
