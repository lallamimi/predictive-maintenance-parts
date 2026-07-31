from rest_framework import serializers

from .models import Fournisseur, PieceRechange


class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = ["id", "nom", "fiabilite_score", "delai_moyen_livraison_jours"]


class PieceRechangeSerializer(serializers.ModelSerializer):
    fournisseur_nom = serializers.CharField(source="fournisseur.nom", read_only=True)
    sous_le_seuil = serializers.BooleanField(read_only=True)

    class Meta:
        model = PieceRechange
        fields = [
            "id",
            "code_panne_associe",
            "nom",
            "categorie",
            "prix_unitaire",
            "fournisseur",
            "fournisseur_nom",
            "stock_actuel",
            "seuil_reapprovisionnement",
            "sous_le_seuil",
        ]
