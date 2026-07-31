from rest_framework import serializers


class PredictFailureInputSerializer(serializers.Serializer):
    temperature_air_k = serializers.FloatField(min_value=250, max_value=350)
    temperature_process_k = serializers.FloatField(min_value=250, max_value=350)
    vitesse_rotation_rpm = serializers.FloatField(min_value=0, max_value=5000)
    couple_nm = serializers.FloatField(min_value=0, max_value=150)
    usure_outil_min = serializers.FloatField(min_value=0, max_value=300)
    type_produit = serializers.ChoiceField(choices=["L", "M", "H"])


class PredictDemandInputSerializer(serializers.Serializer):
    piece_id = serializers.IntegerField(min_value=1)
