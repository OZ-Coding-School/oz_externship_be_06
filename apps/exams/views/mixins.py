from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.constants import ErrorMessages


def _normalize_error_detail(response: Response) -> Response:
    data = getattr(response, "data", None)
    if isinstance(data, dict):
        if response.status_code == 401:
            data["error_detail"] = ErrorMessages.UNAUTHORIZED.value
        elif "detail" in data and "error_detail" not in data:
            data["error_detail"] = data.pop("detail")
        response.data = data
    return response


class ExamsExceptionMixin(APIView):
    """에러 응답의 키를 error_detail로 통일."""

    def handle_exception(self, exc: Exception) -> Response:
        response = super().handle_exception(exc)
        return _normalize_error_detail(response)
