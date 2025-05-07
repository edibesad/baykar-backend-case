from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.serializers.auth import CustomTokenObtainPairSerializer


class AuthView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_summary="Kullanıcı Girişi (JWT Token Al)",
        operation_description="""
Bu endpoint kullanıcı adı ve şifre ile giriş yapılmasını sağlar.

Başarılı bir giriş sonrası iki token döner:
- `access`: Kısa ömürlü token (API çağrılarında kullanılır)
- `refresh`: Uzun ömürlü token (access süresi dolduğunda yenilemek için kullanılır)

> **Not:** Swagger üzerinden test ederken "Authorize" butonuna basıp `Bearer <access>` formatında token girmeniz gerekir.
        """,
        tags=["Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Kullanıcı adı"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, format="password", description="Şifre"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="JWT tokenları",
                examples={
                    "application/json": {
                        "access": "ACCESS_TOKEN",
                        "refresh": "REFRESH_TOKEN",
                    }
                },
            ),
            401: openapi.Response(description="Geçersiz kullanıcı adı veya şifre."),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RefreshTokenView(TokenRefreshView):
    @swagger_auto_schema(
        operation_summary="Access Token Yenile (Refresh ile)",
        operation_description="""
Bu endpoint, mevcut bir **refresh token** ile yeni bir **access token** üretir.

- Login olduğunuzda aldığınız `refresh` token'ı burada kullanarak, tekrar şifre girmeye gerek kalmadan `access` token yenileyebilirsiniz.

> **Not:** `access` token süresi dolunca frontend uygulamanız bu endpoint'i çağırarak oturumu güncel tutabilir.
        """,
        tags=["Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Daha önce alınmış refresh token",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Yeni access token üretildi.",
                examples={"application/json": {"access": "YENI_ACCESS_TOKEN"}},
            ),
            401: openapi.Response(
                description="Refresh token geçersiz veya süresi dolmuş."
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        operation_summary="Giriş Yapan Kullanıcının Bilgisi",
        operation_description="""
Bu endpoint, access token ile kimliği doğrulanmış kullanıcının:

- kullanıcı adını
- personel ismini
- ait olduğu takımın adını ve sorumluluğunu

döner.
        """,
        tags=["Authentication"],
        responses={
            200: openapi.Response(
                description="Kullanıcı bilgileri",
                examples={
                    "application/json": {
                        "username": "admin",
                        "full_name": "Ahmet Yılmaz",
                        "team": "Kanat Takımı",
                        "team_responsibility": "kanat",
                    }
                },
            ),
            401: openapi.Response(description="JWT token eksik veya geçersiz."),
        },
    )
    def get(self, request):
        user = request.user
        personnel = user.personnel
        return Response(
            {
                "username": user.username,
                "full_name": personnel.full_name,
                "team": personnel.team.name,
                "team_responsibility": personnel.team.responsibility,
            }
        )
