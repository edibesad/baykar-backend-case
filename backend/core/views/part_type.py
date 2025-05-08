from core.models.part_type import PartType
from rest_framework import viewsets, permissions
from core.serializers.part_type import PartTypeSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class PartTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing part types.
    """
    queryset = PartType.objects.all()
    serializer_class = PartTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Parça Tiplerini Listele",
        operation_description="Sistemdeki tüm parça tiplerini listeler",
        responses={200: PartTypeSerializer(many=True)},
        tags=["Part Types"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Parça Tipi Detayı",
        operation_description="Belirli bir parça tipinin detaylarını gösterir",
        responses={200: PartTypeSerializer()},
        tags=["Part Types"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs) 