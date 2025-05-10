from rest_framework import serializers
from core.models.personnel import Personnel


class PersonnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personnel
        fields = ["id", "full_name", "team"]
        ref_name = "AircraftPersonnelSerializer"
