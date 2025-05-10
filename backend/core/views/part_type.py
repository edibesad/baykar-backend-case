from core.models.part_type import PartType
from rest_framework import viewsets, permissions
from core.serializers.part_type import PartTypeSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response


class PartTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Parça tiplerini görüntülemek için kullanılan viewset.
    Bu viewset sadece okuma işlemlerine izin verir (listeleme ve detay görüntüleme).
    """

    # Tüm parça tiplerini getiren queryset
    queryset = PartType.objects.all()
    # Parça tipi verilerini JSON formatına dönüştüren serializer
    serializer_class = PartTypeSerializer
    # Sadece kimliği doğrulanmış kullanıcıların erişimine izin veren izin sınıfı
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Parça Tiplerini Listele",
        operation_description="Sistemdeki tüm parça tiplerini listeler",
        responses={
            200: openapi.Response(
                description="Başarılı yanıt",
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
                                        description="Parça tipi ID",
                                    ),
                                    "name": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Parça tipi adı",
                                    ),
                                    "allowed_team": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER,
                                                description="Takım ID",
                                            ),
                                            "name": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description="Takım adı",
                                            ),
                                        },
                                    ),
                                },
                            ),
                            description="Parça tipleri listesi",
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
        tags=["Part Types"],
    )
    def list(self, request, *args, **kwargs):
        """
        Tüm parça tiplerini listeler.
        Sayfalama parametreleri (limit ve offset) ile sonuçlar filtrelenebilir.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Sayfalama parametrelerini al
        limit = request.query_params.get("limit")
        offset = request.query_params.get("offset")

        # Limit ve offset değerlerini integer'a çevir
        try:
            limit = int(limit) if limit else None
            offset = int(offset) if offset else 0
        except (TypeError, ValueError):
            limit = None
            offset = 0

        # Veritabanı seviyesinde sayfalama uygula
        if limit is not None:
            queryset = queryset[offset : offset + limit]
        else:
            queryset = queryset[offset:]

        serializer = self.get_serializer(queryset, many=True)
        total_count = self.get_queryset().count()
        return Response({"total": total_count, "data": serializer.data})

    @swagger_auto_schema(
        operation_summary="Parça Tipi Detayı",
        operation_description="Belirli bir parça tipinin detaylarını gösterir",
        responses={
            200: openapi.Response(
                description="Başarılı yanıt",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="Parça tipi ID"
                        ),
                        "name": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Parça tipi adı"
                        ),
                        "allowed_team": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(
                                    type=openapi.TYPE_INTEGER, description="Takım ID"
                                ),
                                "name": openapi.Schema(
                                    type=openapi.TYPE_STRING, description="Takım adı"
                                ),
                            },
                        ),
                    },
                ),
            )
        },
        tags=["Part Types"],
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Belirli bir parça tipinin detaylı bilgilerini getirir.
        Parça tipi ID'si URL'de belirtilmelidir.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
