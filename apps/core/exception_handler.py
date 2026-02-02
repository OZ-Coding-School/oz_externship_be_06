from __future__ import annotations

from typing import Any

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    request = context.get("request")
    path = getattr(request, "path", "") if request else ""

    if path.endswith("/api/v1/admin/analytics/withdrawals/trends"):
        detail = response.data.get("detail", "")
        if isinstance(detail, dict):
            detail = detail.get("error_detail") or detail.get("detail") or str(detail)
        response.data = {"error_detail": str(detail)}

    return response
