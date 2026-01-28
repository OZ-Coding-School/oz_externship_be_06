from typing import Any, Optional

from rest_framework.response import Response
from rest_framework.views import exception_handler


def post_exception_handler(exc: Exception, context: Any) -> Optional[Response]:
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(response.data, dict):
            # detail 키가 있다면 error_detail에도 똑같이 복사 (기존 테스트 보존)
            if "detail" in response.data:
                response.data["error_detail"] = response.data["detail"]
            else:
                # 필드 에러(title 등)인 경우 전체를 error_detail로 감쌈
                response.data = {"error_detail": response.data}
        elif isinstance(response.data, list):
            response.data = {"error_detail": response.data[0]}

    return response
