from rest_framework import serializers
from core.models import Part


class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = [
            "id",
            "serial_number",
            "type",
            "aircraft_model",
            "used_in_aircraft",
            "produced_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "produced_by"]
