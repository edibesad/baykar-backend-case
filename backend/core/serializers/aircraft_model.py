from rest_framework import serializers
from core.models.aircraft_model import AircraftModel


class AircraftModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AircraftModel
        fields = ["id", "name"]
        read_only_fields = ["id"]
        ref_name = "AircraftModelDetail"
