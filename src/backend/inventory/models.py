from django.db import models


class Fournisseur(models.Model):
    nom = models.CharField(max_length=200)
    fiabilite_score = models.FloatField()
    delai_moyen_livraison_jours = models.PositiveIntegerField()

    class Meta:
        ordering = ["nom"]

    def __str__(self) -> str:
        return self.nom


class PieceRechange(models.Model):
    code_panne_associe = models.CharField(max_length=16)
    nom = models.CharField(max_length=200)
    categorie = models.CharField(max_length=100)
    prix_unitaire = models.FloatField()
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.PROTECT, related_name="pieces")
    stock_actuel = models.PositiveIntegerField()
    seuil_reapprovisionnement = models.PositiveIntegerField()

    class Meta:
        ordering = ["nom"]

    @property
    def sous_le_seuil(self) -> bool:
        return self.stock_actuel < self.seuil_reapprovisionnement

    def __str__(self) -> str:
        return f"{self.nom} ({self.categorie})"
