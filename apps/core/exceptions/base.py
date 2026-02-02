from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class CoreBaseException(APIException):
    """
    core용 기본 예외 클래스
    """

    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail: str, status_code: int | None = None) -> None:
        if status_code is not None:
            self.status_code = status_code

        custom_detail = {"error_detail": detail}
        super().__init__(detail=custom_detail)
