from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.contrib import admin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.utils import swagger_auto_schema


schema_view = get_schema_view(
   openapi.Info(
      title="API Dokümantasyonu",
      default_version='v1',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

token_obtain_schema = swagger_auto_schema(
    method='post',
    operation_description="Kullanıcı girişi (JWT token al)",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
        },
    ),
    responses={
        200: openapi.Response(
            description='Token başarıyla alındı',
            examples={
                'application/json': {
                    'access': 'eyJ0eXAiOiJKV1QiLCJh...',
                    'refresh': 'eyJ0eXAiOiJKV1QiLCJh...'
                }
            }
        )
    }
)(TokenObtainPairView.as_view())


urlpatterns = [
   path('api/token/', token_obtain_schema, name='token_obtain_pair'),
   path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('admin/', admin.site.urls),
]
