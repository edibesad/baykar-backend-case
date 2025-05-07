from rest_framework import serializers
from core.models import Part
from core.models.aircraft import Aircraft


class PartMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ["id", "serial_number", "type"]


class AircraftSerializer(serializers.ModelSerializer):
    wing = serializers.PrimaryKeyRelatedField(
        queryset=Part.objects.all(), write_only=True
    )
    body = serializers.PrimaryKeyRelatedField(
        queryset=Part.objects.all(), write_only=True
    )
    tail = serializers.PrimaryKeyRelatedField(
        queryset=Part.objects.all(), write_only=True
    )
    avionic = serializers.PrimaryKeyRelatedField(
        queryset=Part.objects.all(), write_only=True
    )
    engine = serializers.PrimaryKeyRelatedField(
        queryset=Part.objects.all(), write_only=True
    )

    class Meta:
        model = Aircraft
        fields = [
            "id",
            "serial_number",
            "model",
            "assembled_by",
            "assembled_at",
            "wing",
            "body",
            "tail",
            "avionic",
            "engine",
        ]
        read_only_fields = ["id", "assembled_by", "assembled_at"]
