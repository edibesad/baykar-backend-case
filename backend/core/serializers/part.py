from rest_framework import serializers
from core.models import Part, PartType, AircraftModel, Personnel, Aircraft


class PartTypeSerializer(serializers.ModelSerializer):
    allowed_team = serializers.StringRelatedField()

    class Meta:
        model = PartType
        fields = ['id', 'name', 'allowed_team']


class AircraftModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AircraftModel
        fields = ['id', 'name']


class PersonnelSerializer(serializers.ModelSerializer):
    team = serializers.StringRelatedField()

    class Meta:
        model = Personnel
        fields = ['id', 'full_name', 'team']
        ref_name = "PartPersonnelSerializer"


class AircraftMinimalSerializer(serializers.ModelSerializer):
    model = serializers.StringRelatedField()

    class Meta:
        model = Aircraft
        fields = ['id', 'serial_number', 'model']


class PartSerializer(serializers.ModelSerializer):
    type = PartTypeSerializer(read_only=True)
    aircraft_model = AircraftModelSerializer(read_only=True)
    produced_by = PersonnelSerializer(read_only=True)
    used_in_aircraft = AircraftMinimalSerializer(read_only=True)
    
    # Adding these fields for write operations since the nested serializers are read-only
    type_id = serializers.PrimaryKeyRelatedField(
        source='type', write_only=True, queryset=PartType.objects.all()
    )
    aircraft_model_id = serializers.PrimaryKeyRelatedField(
        source='aircraft_model', write_only=True, queryset=AircraftModel.objects.all()
    )

    class Meta:
        model = Part
        fields = [
            "id",
            "serial_number",
            "type", "type_id",
            "aircraft_model", "aircraft_model_id",
            "used_in_aircraft",
            "produced_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "produced_by"]
