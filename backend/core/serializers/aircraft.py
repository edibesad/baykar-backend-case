from rest_framework import serializers
from core.models import Part
from core.models.aircraft import Aircraft
from django.db import transaction
from core.serializers.aircraft_model import AircraftModelSerializer
from core.models.personnel import Personnel


class PartMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ["id", "serial_number", "type"]


class PersonnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personnel
        fields = ["id", "full_name", "team"]
        ref_name = "AircraftPersonnelSerializer"


class AircraftSerializer(serializers.ModelSerializer):
    parts = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="Bu uçak ile ilişkilendirilecek parçaların seri numaralarının listesi"
    )
    model = AircraftModelSerializer(read_only=True)
    model_id = serializers.PrimaryKeyRelatedField(
        source='model', 
        queryset=Aircraft._meta.get_field('model').related_model.objects.all(),
        write_only=True
    )
    assembled_by = PersonnelSerializer(read_only=True)

    class Meta:
        model = Aircraft
        fields = [
            "id",
            "serial_number",
            "model",
            "model_id",
            "assembled_by",
            "assembled_at",
            "parts",
        ]
        read_only_fields = ["id", "assembled_by", "assembled_at"]

    def validate(self, data):
        # Verilerden parçalar listesini çıkar ancak doğrulanmış son verilerde tutma
        part_serial_numbers = data.pop('parts', [])
        
        # Create metodunda kullanmak için parça nesnelerini sakla
        if part_serial_numbers:
            self.parts_objects = Part.objects.filter(serial_number__in=part_serial_numbers)
            # Tüm istenen parçaların bulunup bulunmadığını kontrol et
            found_serials = self.parts_objects.values_list('serial_number', flat=True)
            if len(self.parts_objects) != len(part_serial_numbers):
                missing_serials = [serial for serial in part_serial_numbers if serial not in found_serials]
                error_msg = f"{', '.join(missing_serials)} seri numaralı parçalar bulunamadı"
                raise serializers.ValidationError({"details": error_msg})
            
            # Parçaların uygun uçak modeline ait olup olmadığını kontrol et
            aircraft_model = data.get('model')
            if aircraft_model:
                incompatible_parts = self.parts_objects.exclude(aircraft_model=aircraft_model)
                if incompatible_parts.exists():
                    incompatible_serials = list(incompatible_parts.values_list('serial_number', flat=True))
                    error_msg = f"{', '.join(incompatible_serials)} seri numaralı parçalar uçak modeliyle uyumlu değil. Bu parçalar farklı bir uçak modeli için üretilmiş."
                    raise serializers.ValidationError({"details": error_msg})
        else:
            self.parts_objects = []
            
        return data
        
    def create(self, validated_data):
        # Transaction kullanarak uçak ve parçalarını oluştur
        # Herhangi bir hata durumunda tüm işlemler geri alınacak
        with transaction.atomic():
            # Parçalar olmadan uçak örneğini oluştur
            aircraft = Aircraft.objects.create(**validated_data)
            
            # Parçaları uçağa ekle
            if hasattr(self, 'parts_objects') and self.parts_objects:
                for part in self.parts_objects:
                    aircraft.parts.add(part)
            
            return aircraft


class AircraftDetailSerializer(serializers.ModelSerializer):
    parts = PartMinimalSerializer(many=True, read_only=True)
    model = AircraftModelSerializer(read_only=True)
    assembled_by = PersonnelSerializer(read_only=True)

    class Meta:
        model = Aircraft
        fields = [
            "id",
            "serial_number",
            "model",
            "assembled_by",
            "assembled_at",
            "parts",
        ]
        read_only_fields = fields
