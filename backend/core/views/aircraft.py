from core.models.aircraft import Aircraft
from core.permission import IsTeamAuthorizedForAircraft
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from core.serializers.aircraft import AircraftSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

expected_types = {
    "wing": "kanat",
    "body": "gövde",
    "tail": "kuyruk",
    "avionic": "aviyonik",
    "engine": "motor",
}


class AircraftViewSet(viewsets.ModelViewSet):
    serializer_class = AircraftSerializer

    def get_permissions(self):
        return [permissions.IsAuthenticated(), IsTeamAuthorizedForAircraft()]

    def get_queryset(self):
        user = self.request.user
        personnel = getattr(user, "personnel", None)

        if not personnel or not personnel.team:
            return Aircraft.objects.none()
        
        if personnel.team.name.lower() != "montaj":
            raise permissions.PermissionDenied("Bu işlem için Montaj takımına ait olmanız gerekmektedir.")

        return Aircraft.objects

    @swagger_auto_schema(
        operation_summary="Yeni Uçak Montajı",
        operation_description="""
Montaj takımı, parçaları birleştirerek yeni bir uçak oluşturur.

Kurallar:
- Parçalar, sadece tanımlı uçak modeli için üretilmiş olmalıdır
- Aynı parça başka uçakta daha önce kullanılmamış olmalıdır
- Her parça doğru türde olmalıdır (örneğin `kanat` alanına `kanat` tipi parça)
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

        for name, part in parts.items():
            if part is None:
                raise ValidationError({name: f"{name.capitalize()} parçası eksik."})

            if part.type.name.lower() != expected_types[name]:
                raise ValidationError(
                    {
                        name: f"{part.serial_number} bir {part.type.name} parçasıdır, {expected_types[name]} bekleniyordu."
                    }
                )

            if part.used_in_aircraft is not None:
                raise ValidationError(
                    {name: f"{part.serial_number} zaten başka uçakta kullanılmış."}
                )

            if part.aircraft_model != model:
                raise ValidationError(
                    {
                        name: f"{part.serial_number} sadece {part.aircraft_model.name} için üretilmiştir."
                    }
                )

        aircraft = serializer.save(assembled_by=personnel)

        for part in parts.values():
            part.used_in_aircraft = aircraft
            part.save()

        return Response(
            self.get_serializer(aircraft).data, status=status.HTTP_201_CREATED
        )
