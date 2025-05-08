from core.models.aircraft import Aircraft
from core.permission import IsTeamAuthorizedForAircraft
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from core.serializers.aircraft import AircraftSerializer, AircraftDetailSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)

expected_types = {
    "wing": "kanat",
    "body": "gövde",
    "tail": "kuyruk",
    "avionic": "aviyonik",
    "engine": "motor",
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
- Her parça doğru türde olmalıdır (örneğin `kanat` alanına `kanat` tipi parça)
- Parça seri numaraları geçerli olmalıdır
        """,
        responses={201: AircraftSerializer},
        tags=["Aircraft"],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        personnel = request.user.personnel
        model = serializer.validated_data["model"]

        parts = {
            "wing": serializer.validated_data.get("wing"),
            "body": serializer.validated_data.get("body"),
            "tail": serializer.validated_data.get("tail"),
            "avionic": serializer.validated_data.get("avionic"),
            "engine": serializer.validated_data.get("engine"),
        }

        errors = {}
        for name, part in parts.items():
            if part is None:
                serial = request.data.get(f"{name}_serial", "")
                errors[name] = f"{serial} seri numaralı {name} parçası bulunamadı."
                continue

            if part.type.name.lower() != expected_types[name]:
                errors[name] = (
                    f"{part.serial_number} bir {part.type.name} parçasıdır, {expected_types[name]} bekleniyordu."
                )
                continue

            if part.used_in_aircraft is not None:
                errors[name] = f"{part.serial_number} zaten başka uçakta kullanılmış."
                continue

            if part.aircraft_model != model:
                errors[name] = (
                    f"{part.serial_number} sadece {part.aircraft_model.name} için üretilmiştir."
                )
                continue

        if errors:
            logger.error(f"Validation errors during aircraft creation: {errors}")
            raise ValidationError(errors)

        aircraft = serializer.save(assembled_by=personnel)

        for part in parts.values():
            part.used_in_aircraft = aircraft
            part.save()

        return Response(
            self.get_serializer(aircraft).data, status=status.HTTP_201_CREATED
        )
