from rest_framework import viewsets, permissions
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.models import Part
from core.serializers.part import PartSerializer
from core.permission import IsTeamAuthorizedForPartType
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404


class PartViewSet(viewsets.ModelViewSet):
    serializer_class = PartSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsTeamAuthorizedForPartType()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        personnel = getattr(user, "personnel", None)

        if not personnel or not personnel.team:
            return Part.objects.none()

        return Part.objects.filter(type__allowed_team=personnel.team)

    def perform_create(self, serializer):
        personnel = self.request.user.personnel
        serializer.save(produced_by=personnel, used_in_aircraft=None)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        pk = self.kwargs.get(self.lookup_field, None)

        try:
            return queryset.get(pk=pk)
        except Part.DoesNotExist:
            raise NotFound("Verilen sorguya uygun bir Parça bulunamadı.")

    @swagger_auto_schema(
        operation_summary="Parçaları Listele",
        operation_description="Tüm üretilmiş parçaların listesini döner.",
        tags=["Parts"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Parça Detayı",
        operation_description="Belirli bir parçanın detay bilgisini döner.",
        tags=["Parts"],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Parça Oluştur",
        operation_description="""
Takımınızın yetkili olduğu bir parça türü ile parça üretebilirsiniz.

Eğer takımınız type ile eşleşmiyorsa **403 hatası** döner.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["serial_number", "type", "aircraft_model"],
            properties={
                "serial_number": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Parça seri numarası"
                ),
                "type": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Parça türü ID"
                ),
                "aircraft_model": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Uçak modeli ID"
                ),
            },
        ),
        tags=["Parts"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Parça Sil (Geri Dönüşüm)",
        operation_description="Belirli bir parçayı veritabanından kalıcı olarak siler.",
        tags=["Parts"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
