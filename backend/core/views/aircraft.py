from core.models.aircraft import Aircraft
from core.models.part import Part
from core.models.part_type import PartType
from core.permission import IsTeamAuthorizedForAircraft
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from core.serializers.aircraft import AircraftSerializer, AircraftDetailSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)

# Required part types for a complete aircraft
REQUIRED_PART_TYPES = {
    "kanat": 1,  # wing
    "gövde": 1,  # body
    "kuyruk": 1,  # tail
    "aviyonik": 1,  # avionic
    "motor": 1,  # engine
}


@swagger_auto_schema(
    tags=["Aircraft"],
    operation_summary="Uçak İşlemleri",
    operation_description="Uçak montajı ve detaylarını görüntüleme işlemleri. Sadece Montaj takımı üyeleri erişebilir.",
)
class AircraftViewSet(viewsets.ModelViewSet):
    serializer_class = AircraftSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeamAuthorizedForAircraft]

    def get_queryset(self):
        user = self.request.user
        return Aircraft.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AircraftDetailSerializer
        return self.serializer_class

    @swagger_auto_schema(
        operation_summary="Uçak Listesi",
        operation_description="Tüm uçakların listesini getirir. Sadece Montaj takımı üyeleri erişebilir.",
        responses={200: AircraftDetailSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Sayfalama için limit değeri",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'offset',
                openapi.IN_QUERY,
                description="Sayfalama için offset değeri",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        tags=["Aircraft"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Uçak Detaylarını Getir",
        operation_description="Belirtilen ID'ye sahip uçağın detaylarını getirir. Sadece Montaj takımı üyeleri erişebilir.",
        responses={200: AircraftDetailSerializer},
        tags=["Aircraft"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Yeni Uçak Montajı",
        operation_description="""
Montaj takımı, parçaları birleştirerek yeni bir uçak oluşturur.

Kurallar:
- Parçalar, sadece tanımlı uçak modeli için üretilmiş olmalıdır
- Aynı parça başka uçakta daha önce kullanılmamış olmalıdır
- Parça seri kodları geçerli olmalıdır
        """,
        responses={201: AircraftSerializer},
        tags=["Aircraft"],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        personnel = request.user.personnel
        model = serializer.validated_data["model"]
        
        # Get part objects from the serializer
        parts = getattr(serializer, 'parts_objects', [])
        
        # Check if any parts are provided
        if not parts:
            logger.error("Validation error: Uçak montajı için parça listesi boş olamaz.")
            raise ValidationError({"details": "Uçak montajı için parça listesi boş olamaz."})
        
        # Group parts by type
        part_types = {}
        for part in parts:
            type_name = part.type.name.lower()
            if type_name not in part_types:
                part_types[type_name] = []
            part_types[type_name].append(part)
        
        # Check for required part types
        for type_name, required_count in REQUIRED_PART_TYPES.items():
            count = len(part_types.get(type_name, []))
            if count < required_count:
                error_msg = f"En az {required_count} adet {type_name} parçası gerekli. {count} adet mevcut."
                logger.error(f"Validation error: {error_msg}")
                raise ValidationError({"details": error_msg})
            elif count > required_count:
                error_msg = f"En fazla {required_count} adet {type_name} parçası kullanılabilir. {count} adet belirtilmiş."
                logger.error(f"Validation error: {error_msg}")
                raise ValidationError({"details": error_msg})
        
        # Validate each part
        for part in parts:
            # Check if part is already used in another aircraft
            if part.used_in_aircraft is not None:
                error_msg = f"{part.serial_number} seri numaralı parça zaten başka uçakta kullanılmış."
                logger.error(f"Validation error: {error_msg}")
                raise ValidationError({"details": error_msg})
                
            # Check if part is for the correct aircraft model
            if part.aircraft_model != model:
                error_msg = f"{part.serial_number} seri numaralı parça {model.name} modeli için üretilmemiş."
                logger.error(f"Validation error: {error_msg}")
                raise ValidationError({"details": error_msg})

        # Create aircraft
        aircraft = serializer.save(assembled_by=personnel)
        
        # Associate parts with the new aircraft
        for part in parts:
            part.used_in_aircraft = aircraft
            part.save()

        return Response(
            self.get_serializer(aircraft).data, status=status.HTTP_201_CREATED
        )
