from __future__ import annotations

from rest_framework.exceptions import APIException
from rest_framework import status


class CoreBaseException(APIException):
    """
    core용 기본 예외 클래스
    """
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail: str, status_code: int | None = None) -> None:
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail=detail)