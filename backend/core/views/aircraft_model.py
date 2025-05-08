from core.models.aircraft_model import AircraftModel
from rest_framework import viewsets, permissions
from core.serializers.aircraft_model import AircraftModelSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class AircraftModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing aircraft models.
    """
    queryset = AircraftModel.objects.all()
    serializer_class = AircraftModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Uçak Modellerini Listele",
        operation_description="Sistemdeki tüm uçak modellerini listeler",
        responses={200: AircraftModelSerializer(many=True)},
        tags=["Aircraft Models"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Uçak Model Detayı",
        operation_description="Belirli bir uçak modelinin detaylarını gösterir",
        responses={200: AircraftModelSerializer()},
        tags=["Aircraft Models"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs) 