from rest_framework import serializers

from .models import InterventionPiece, LectureCapteur


class LectureCapteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = LectureCapteur
        fields = [
            "id",
            "reference_ai4i",
            "type_produit",
            "temperature_air_k",
            "temperature_process_k",
            "vitesse_rotation_rpm",
            "couple_nm",
            "usure_outil_min",
            "panne",
            "panne_twf",
            "panne_hdf",
            "panne_pwf",
            "panne_osf",
            "panne_rnf",
        ]


class InterventionPieceSerializer(serializers.ModelSerializer):
    nom_piece = serializers.CharField(source="piece.nom", read_only=True)

    class Meta:
        model = InterventionPiece
        fields = ["id", "lecture", "piece", "nom_piece", "quantite", "date_intervention", "cout_total"]
