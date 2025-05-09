from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Özel details formatını uygula
        if isinstance(exc, ValidationError) and "details" in response.data:
            # Eğer details bir liste ise, ilk öğeyi al (genellikle tek öğe vardır)
            if isinstance(response.data["details"], list) and response.data["details"]:
                response.data["details"] = response.data["details"][0]
    
    return response 

class CustomPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100
    
    def get_paginated_response(self, data):
        return Response({
            'total': self.count,
            'data': data
        }) 