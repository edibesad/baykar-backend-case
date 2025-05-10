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

# Loglama için logger tanımlaması
logger = logging.getLogger(__name__)

# Tam bir uçak için gerekli olan parça tipleri ve miktarları
REQUIRED_PART_TYPES = {
    "kanat": 1,
    "gövde": 1,
    "kuyruk": 1,
    "aviyonik": 1,
}


@swagger_auto_schema(
    tags=["Aircraft"],
    operation_summary="Uçak İşlemleri",
    operation_description="Uçak montajı ve detaylarını görüntüleme işlemleri. Sadece Montaj takımı üyeleri erişebilir.",
)
class AircraftViewSet(viewsets.ModelViewSet):
    """
    Uçak işlemleri için kullanılan viewset.
    Bu viewset uçakların listelenmesi, detaylarının görüntülenmesi ve yeni uçak montajı işlemlerini yönetir.
    Sadece montaj takımı üyeleri erişebilir.
    """

    # Uçak verilerini JSON formatına dönüştüren serializer
    serializer_class = AircraftSerializer
    # Kimlik doğrulama ve montaj takımı yetkisi kontrolü
    permission_classes = [permissions.IsAuthenticated, IsTeamAuthorizedForAircraft]

    def get_queryset(self):
        """
        Tüm uçakları getiren queryset.
        """
        user = self.request.user
        return Aircraft.objects.all()

    def get_serializer_class(self):
        """
        İşlem tipine göre uygun serializer'ı döndürür.
        Detay görüntüleme için AircraftDetailSerializer, diğer işlemler için AircraftSerializer kullanılır.
        """
        if self.action == "retrieve":
            return AircraftDetailSerializer
        return self.serializer_class

    @swagger_auto_schema(
        operation_summary="Uçak Listesi",
        operation_description="Tüm uçakların listesini getirir. Sadece Montaj takımı üyeleri erişebilir.",
        responses={200: AircraftDetailSerializer(many=True)},
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
        tags=["Aircraft"],
    )
    def list(self, request, *args, **kwargs):
        """
        Tüm uçakların listesini getirir.
        Sayfalama parametreleri (limit ve offset) ile sonuçlar filtrelenebilir.
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Uçak Detaylarını Getir",
        operation_description="Belirtilen ID'ye sahip uçağın detaylarını getirir. Sadece Montaj takımı üyeleri erişebilir.",
        responses={200: AircraftDetailSerializer},
        tags=["Aircraft"],
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Belirli bir uçağın detaylı bilgilerini getirir.
        Uçak ID'si URL'de belirtilmelidir.
        """
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
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["serial_number", "model_id", "parts"],
            properties={
                "serial_number": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Uçak seri numarası"
                ),
                "model_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Uçak modeli ID"
                ),
                "parts": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description="Bu uçak ile ilişkilendirilecek parçaların seri numaralarının listesi",
                ),
            },
        ),
        responses={201: AircraftSerializer},
        tags=["Aircraft"],
    )
    def create(self, request, *args, **kwargs):
        """
        Yeni bir uçak montajı yapar.

        İşlem adımları:
        1. Gelen verileri doğrular
        2. Parçaların uygunluğunu kontrol eder
        3. Gerekli parça tiplerinin varlığını kontrol eder
        4. Parçaların başka uçaklarda kullanılmadığını kontrol eder
        5. Parçaların doğru uçak modeli için üretildiğini kontrol eder
        6. Yeni uçağı oluşturur ve parçaları ilişkilendirir
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        personnel = request.user.personnel
        model = serializer.validated_data["model"]

        # Serializer'dan parça nesnelerini al
        parts = getattr(serializer, "parts_objects", [])

        # Parça listesinin boş olup olmadığını kontrol et
        if not parts:
            logger.error(
                "Validation error: Uçak montajı için parça listesi boş olamaz."
            )
            raise ValidationError(
                {"details": "Uçak montajı için parça listesi boş olamaz."}
            )

        # Parçaları tiplerine göre grupla
        part_types = {}
        for part in parts:
            type_name = part.type.name.lower()
            if type_name not in part_types:
                part_types[type_name] = []
            part_types[type_name].append(part)

        # Gerekli parça tiplerinin varlığını kontrol et
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

        # Her parçayı doğrula
        for part in parts:
            # Parçanın başka uçakta kullanılıp kullanılmadığını kontrol et
            if part.used_in_aircraft is not None:
                error_msg = f"{part.serial_number} seri numaralı parça zaten başka uçakta kullanılmış."
                logger.error(f"Validation error: {error_msg}")
                raise ValidationError({"details": error_msg})

            # Parçanın doğru uçak modeli için üretilip üretilmediğini kontrol et
            if part.aircraft_model != model:
                error_msg = f"{part.serial_number} seri numaralı parça {model.name} modeli için üretilmemiş."
                logger.error(f"Validation error: {error_msg}")
                raise ValidationError({"details": error_msg})

        # Uçağı oluştur
        aircraft = serializer.save(assembled_by=personnel)

        # Parçaları yeni uçakla ilişkilendir
        for part in parts:
            part.used_in_aircraft = aircraft
            part.save()

        return Response(
            self.get_serializer(aircraft).data, status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        operation_summary="Uçak Sil",
        operation_description="Belirtilen ID'ye sahip uçağı siler. Sadece Montaj takımı üyeleri erişebilir.",
        responses={204: "Uçak başarıyla silindi"},
        tags=["Aircraft"],
    )
    def destroy(self, request, *args, **kwargs):
        """
        Belirli bir uçağı siler.
        İlişkili parçaların used_in_aircraft alanı otomatik olarak NULL olarak ayarlanır.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
