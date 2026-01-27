from rest_framework.views import exception_handler
from rest_framework.response import Response
from typing import Any, Optional

def post_exception_handler(exc: Exception, context: Any) -> Optional[Response]:
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                response.data = {"error_detail": response.data['detail']}
            else:
                response.data = {"error_detail": response.data}
        elif isinstance(response.data, list):
            response.data = {"error_detail": response.data[0]}

    return response