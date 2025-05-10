from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Giriş yapılmamış (token yok veya geçersiz)
        if isinstance(exc, NotAuthenticated):
            response.data = {"detail": "Kimlik doğrulama bilgileri sağlanmadı."}

        # Kullanıcı adı veya şifre yanlış
        elif isinstance(exc, AuthenticationFailed):
            response.data = {"detail": "Kullanıcı adı veya şifre hatalı."}

        # Validasyon hatalarını sadeleştir
        elif isinstance(exc, ValidationError):
            if isinstance(response.data, dict):
                # Tüm alanlardaki ilk hatayı al
                for key, value in response.data.items():
                    if isinstance(value, list) and value:
                        response.data = {"details": value[0]}
                    elif isinstance(value, str):
                        response.data = {"details": value}

    return response


class CustomPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "limit"
    offset_query_param = "offset"
    max_limit = 100

    def get_paginated_response(self, data):
        return Response({"total": self.count, "data": data})
