from __future__ import annotations

from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.constants import ErrorMessages
from apps.exams.exceptions import ErrorDetailException


def _normalize_error_detail(response: Response) -> Response:
    if response.status_code == 401:
        response.data = {"error_detail": ErrorMessages.UNAUTHORIZED.value}
        return response

    data = getattr(response, "data", None)
    if isinstance(data, dict) and "detail" in data and "error_detail" not in data:
        data["error_detail"] = data.pop("detail")
        response.data = data
    return response


class ExamsExceptionMixin(APIView):
    """에러 응답의 키를 error_detail로 통일."""

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            return Response({"error_detail": ErrorMessages.UNAUTHORIZED.value}, status=401)

        if isinstance(exc, ErrorDetailException):
            return Response({"error_detail": str(exc.detail)}, status=exc.http_status)

        response = super().handle_exception(exc)
        return _normalize_error_detail(response)
