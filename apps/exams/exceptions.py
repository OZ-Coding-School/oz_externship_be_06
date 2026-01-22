from __future__ import annotations

from rest_framework.exceptions import APIException


class ErrorDetailException(APIException):
    status_code = 500
    http_status: int

    def __init__(self, detail: str, http_status: int) -> None:
        super().__init__(detail=detail)
        self.http_status = http_status
