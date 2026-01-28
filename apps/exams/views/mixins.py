from __future__ import annotations

from typing import Any

from rest_framework.response import Response
from rest_framework.views import APIView


def _normalize_error_detail(response: Response | None) -> Response | None:
    if response is None:
        return None
    data = getattr(response, "data", None)
    if isinstance(data, dict) and "detail" in data and "error_detail" not in data:
        data["error_detail"] = data.pop("detail")
        response.data = data
    return response


class ExamsExceptionMixin(APIView):
    """Normalize error payloads to use error_detail key."""

    def handle_exception(self, exc: Exception) -> Response:
        response = super().handle_exception(exc)
        normalized = _normalize_error_detail(response)
        # handle_exception expects a Response; normalized is never None here
        return normalized  # type: ignore[return-value]
