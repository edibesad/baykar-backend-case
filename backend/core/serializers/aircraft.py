from rest_framework import serializers
from core.models import Part
from core.models.aircraft import Aircraft


class PartMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ["id", "serial_number", "type"]


class AircraftSerializer(serializers.ModelSerializer):
    wing_serial = serializers.CharField(write_only=True)
    body_serial = serializers.CharField(write_only=True)
    tail_serial = serializers.CharField(write_only=True)
    avionic_serial = serializers.CharField(write_only=True)
    engine_serial = serializers.CharField(write_only=True)

    class Meta:
        model = Aircraft
        fields = [
            "id",
            "serial_number",
            "model",
            "assembled_by",
            "assembled_at",
            "wing_serial",
            "body_serial",
            "tail_serial",
            "avionic_serial",
            "engine_serial",
        ]
        read_only_fields = ["id", "assembled_by", "assembled_at"]

    def validate(self, data):
        from core.models import Part

        # Seri numaralarına göre parçaları bul
        parts = {
            "wing": Part.objects.filter(serial_number=data.get("wing_serial")).first(),
            "body": Part.objects.filter(serial_number=data.get("body_serial")).first(),
            "tail": Part.objects.filter(serial_number=data.get("tail_serial")).first(),
            "avionic": Part.objects.filter(
                serial_number=data.get("avionic_serial")
            ).first(),
            "engine": Part.objects.filter(
                serial_number=data.get("engine_serial")
            ).first(),
        }

        # Parçaları data'ya ekle
        data.update(
            {
                "wing": parts["wing"],
                "body": parts["body"],
                "tail": parts["tail"],
                "avionic": parts["avionic"],
                "engine": parts["engine"],
            }
        )

        return data


class AircraftDetailSerializer(serializers.ModelSerializer):
    wing = PartMinimalSerializer(read_only=True)
    body = PartMinimalSerializer(read_only=True)
    tail = PartMinimalSerializer(read_only=True)
    avionic = PartMinimalSerializer(read_only=True)
    engine = PartMinimalSerializer(read_only=True)
    model = serializers.StringRelatedField()
    assembled_by = serializers.StringRelatedField()

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
        read_only_fields = fields
