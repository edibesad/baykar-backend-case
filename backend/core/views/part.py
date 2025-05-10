from rest_framework import viewsets, permissions
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.models import Part, AircraftModel, PartType
from core.serializers.part import PartSerializer
from core.permission import IsTeamAuthorizedForPartType
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import (
    Count,
    Q,
    F,
    Value,
    IntegerField,
    Sum,
    Case,
    When,
    OuterRef,
    Subquery,
)
from rest_framework.decorators import action
from itertools import product
from django.db.models.functions import Coalesce
from django.db import connection


class PartViewSet(viewsets.ModelViewSet):
    """
    Parça işlemlerini yöneten viewset.
    Parçaların listelenmesi, detaylarının görüntülenmesi, oluşturulması ve silinmesi işlemlerini yönetir.
    Takım bazlı yetkilendirme sistemi kullanır.
    """

    # Parça verilerini JSON formatına dönüştüren serializer
    serializer_class = PartSerializer

    def get_permissions(self):
        """
        İşlem tipine göre yetkilendirme sınıflarını döndürür.
        Parça oluşturma ve silme işlemi için özel yetkilendirme gerekir.
        """
        if self.action in ["create", "destroy"]:
            return [IsTeamAuthorizedForPartType()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Kullanıcının yetkisine göre parça listesini filtreler.
        - Montaj takımı tüm parçaları görebilir
        - Diğer takımlar sadece kendi yetkili oldukları parçaları görebilir
        - Uçak ID'si ile filtreleme yapılabilir
        """
        user = self.request.user
        personnel = getattr(user, "personnel", None)

        if not personnel or not personnel.team:
            return Part.objects.none()

        # Montaj takımı tüm parçaları görebilir
        if personnel.team.responsibility.lower() == "montaj":
            queryset = Part.objects.all()
        else:
            # Diğer takımlar sadece kendi takımlarına izin verilen parçaları görebilir
            queryset = Part.objects.filter(type__allowed_team=personnel.team)

        # Filter by aircraft_id if provided in query parameters
        aircraft_id = self.request.query_params.get("aircraft_id", None)
        if aircraft_id:
            queryset = queryset.filter(used_in_aircraft_id=aircraft_id)

        return queryset

    def perform_create(self, serializer):
        """
        Yeni parça oluşturulurken üreten personeli ve kullanım durumunu kaydeder.
        """
        personnel = self.request.user.personnel
        serializer.save(produced_by=personnel, used_in_aircraft=None)

    def get_object(self):
        """
        Belirli bir parçayı ID'ye göre getirir.
        Parça bulunamazsa NotFound hatası fırlatır.
        """
        queryset = self.filter_queryset(self.get_queryset())
        pk = self.kwargs.get(self.lookup_field, None)

        try:
            return queryset.get(pk=pk)
        except Part.DoesNotExist:
            raise NotFound("Verilen sorguya uygun bir Parça bulunamadı.")

    @swagger_auto_schema(
        operation_summary="Parçaları Listele",
        operation_description="Tüm üretilmiş parçaların listesini döner. Montaj takımı tüm parçaları görebilirken, diğer takımlar sadece kendilerine ait parçaları görürler.",
        responses={
            200: openapi.Response(
                description="Parçalar başarıyla listelendi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="Toplam kayıt sayısı"
                        ),
                        "data": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description="Parça ID",
                                    ),
                                    "serial_number": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Parça seri numarası",
                                    ),
                                    "type": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER,
                                                description="Parça tipi ID",
                                            ),
                                            "name": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description="Parça tipi adı",
                                            ),
                                            "allowed_team": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description="Yetkili takım",
                                            ),
                                        },
                                    ),
                                    "aircraft_model": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER,
                                                description="Uçak modeli ID",
                                            ),
                                            "name": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description="Uçak modeli adı",
                                            ),
                                        },
                                    ),
                                    "used_in_aircraft": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER,
                                                description="Uçak ID",
                                            ),
                                            "serial_number": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description="Uçak seri numarası",
                                            ),
                                            "model": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description="Uçak modeli adı",
                                            ),
                                        },
                                        nullable=True,
                                    ),
                                    "produced_by": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER,
                                                description="Personel ID",
                                            ),
                                            "full_name": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description="Personel adı",
                                            ),
                                            "team": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description="Personel takımı",
                                            ),
                                        },
                                    ),
                                    "created_at": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format="date-time",
                                        description="Oluşturulma tarihi",
                                    ),
                                },
                            ),
                        ),
                    },
                ),
            )
        },
        manual_parameters=[
            openapi.Parameter(
                "aircraft_id",
                openapi.IN_QUERY,
                description="Belirli bir uçağa ait parçaları filtrelemek için uçak ID'si",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                description="Sayfalama için limit değeri",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "offset",
                openapi.IN_QUERY,
                description="Sayfalama için offset değeri",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
        tags=["Parts"],
    )
    def list(self, request, *args, **kwargs):
        """
        Tüm parçaların listesini getirir.
        Yetkiye ve filtreleme parametrelerine göre sonuçları döndürür.
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Parça Detayı",
        operation_description="Belirli bir parçanın detay bilgisini döner.",
        tags=["Parts"],
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Belirli bir parçanın detaylı bilgilerini getirir.
        Parça ID'si URL'de belirtilmelidir.
        """
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
            required=["serial_number", "type_id", "aircraft_model_id"],
            properties={
                "serial_number": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Parça seri numarası"
                ),
                "type_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Parça türü ID"
                ),
                "aircraft_model_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Uçak modeli ID"
                ),
            },
        ),
        tags=["Parts"],
    )
    def create(self, request, *args, **kwargs):
        """
        Yeni bir parça oluşturur.
        Takım yetkisi ve gerekli alanların doğruluğu kontrol edilir.
        """
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            if "serial_number" in e.detail:
                raise ValidationError(
                    {"details": "Bu seri kodu başka bir parçada kullanılmış"}
                )
            raise e

    @swagger_auto_schema(
        operation_summary="Parça Sil (Geri Dönüşüm)",
        operation_description="Belirli bir parçayı veritabanından kalıcı olarak siler. Eğer parça bir uçakta kullanılıyorsa silinemez.",
        tags=["Parts"],
    )
    def destroy(self, request, *args, **kwargs):
        """
        Bir parçayı siler.
        Parça bir uçakta kullanılıyorsa veya kullanıcının takımı parçanın tipine yetkili değilse silme işlemi yapılamaz.
        """
        instance = self.get_object()

        # Kullanıcının takımının parça tipine yetkisi var mı kontrol et
        user = request.user
        personnel = getattr(user, "personnel", None)

        if not personnel or not personnel.team:
            raise PermissionDenied(
                {"details": "Bu işlem için bir takıma ait olmanız gerekmektedir."}
            )

        if instance.type.allowed_team != personnel.team:
            raise PermissionDenied(
                {
                    "details": "Sadece kendi takımınıza ait parçaları geri dönüşüme yollayabilirsiniz."
                }
            )

        if instance.used_in_aircraft:
            raise ValidationError(
                {
                    "details": f"Bu parça {instance.used_in_aircraft.serial_number} seri numaralı uçakta kullanılıyor."
                }
            )

        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Parça Stok Durumu",
        operation_description="""Parçaların uçak modeline göre stok durumunu listeler. 
        Her uçak modeli için:
        - Parça tipi adı
        - Toplam üretilen parça sayısı
        - Kullanılan parça sayısı
        - Stokta kalan parça sayısı
        
        bilgilerini içeren bir rapor oluşturur.
        """,
        responses={
            200: openapi.Response(
                description="Stok durumu başarıyla getirildi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="Toplam kayıt sayısı"
                        ),
                        "data": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "aircraft_model_name": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Uçak modeli adı",
                                    ),
                                    "parts": openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                "part_type_name": openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    description="Parça tipi adı",
                                                ),
                                                "total_produced": openapi.Schema(
                                                    type=openapi.TYPE_INTEGER,
                                                    description="Toplam üretilen parça sayısı",
                                                ),
                                                "used_count": openapi.Schema(
                                                    type=openapi.TYPE_INTEGER,
                                                    description="Kullanılan parça sayısı",
                                                ),
                                                "stock_count": openapi.Schema(
                                                    type=openapi.TYPE_INTEGER,
                                                    description="Stokta kalan parça sayısı",
                                                ),
                                            },
                                        ),
                                    ),
                                },
                            ),
                        ),
                    },
                ),
            )
        },
        manual_parameters=[
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                description="Sayfalama için limit değeri",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "offset",
                openapi.IN_QUERY,
                description="Sayfalama için offset değeri",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
        tags=["Parts"],
    )
    @action(detail=False, methods=["get"], url_path="stock")
    def stock(self, request):
        """
        Parçaların stok durumunu raporlar.

        Her uçak modeli ve parça tipi için:
        - Toplam üretilen parça sayısı
        - Kullanılan parça sayısı
        - Stokta kalan parça sayısı

        bilgilerini içeren bir rapor oluşturur.
        """
        # Execute raw SQL query
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    acm.id AS aircraft_model_id,
                    acm.name AS aircraft_model_name,
                    pt.id AS part_type_id,
                    pt.name AS part_type_name,
                    COUNT(cp.id) AS total_count,
                    COUNT(cp.used_in_aircraft_id) AS used_count,
                    COUNT(cp.id) - COUNT(cp.used_in_aircraft_id) AS remaining_count
                FROM
                    core_aircraftmodel acm
                CROSS JOIN
                    core_parttype pt
                LEFT JOIN
                    core_part cp ON cp.aircraft_model_id = acm.id AND cp.type_id = pt.id
                GROUP BY
                    acm.id, acm.name, pt.id, pt.name
                ORDER BY
                    acm.id, pt.id
            """
            )
            columns = [col[0] for col in cursor.description]
            stock_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Process data to create the hierarchical response
        result = []
        current_model_id = None
        model_parts = []
        model_name = None

        for item in stock_data:
            # If we've moved to a new aircraft model
            if current_model_id != item["aircraft_model_id"]:
                # Add the previous model to the results (if any)
                if current_model_id is not None:
                    result.append(
                        {"aircraft_model_name": model_name, "parts": model_parts}
                    )

                # Start a new model entry
                current_model_id = item["aircraft_model_id"]
                model_name = item["aircraft_model_name"]
                model_parts = []

            # Add part data to the current model
            model_parts.append(
                {
                    "part_type_name": item["part_type_name"],
                    "total_produced": item["total_count"],
                    "used_count": item["used_count"],
                    "stock_count": item["remaining_count"],
                }
            )

        # Add the last model if we have one
        if current_model_id is not None:
            result.append({"aircraft_model_name": model_name, "parts": model_parts})

        # Apply pagination
        page = self.paginate_queryset(result)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(result)
