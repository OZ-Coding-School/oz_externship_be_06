from __future__ import annotations

from typing import Any
from rest_framework import status
from rest_framework.exceptions import APIException


class CoreBaseException(APIException):
    """
    프로젝트 전역에서 사용하는 표준화된 기본 예외 클래스.
    응답 스키마의 {"error_detail": "..."} 형식을 보장하며,
    Enum(ErrorMessages) 및 다양한 입력 형식을 자동으로 처리합니다.
    """

    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail: Any = None, status_code: int | None = None) -> None:
        """
        생성 시 메시지를 명세서 규격인 'error_detail' 키로 래핑하여 주입
        """
        if status_code is not None:
            self.status_code = status_code

        # 메시지 추출 및 가공
        processed_detail = self._parse_detail(detail)

        # DRF APIException은 detail 인자에 딕셔너리가 들어오면 그대로 JSON화 합니다.
        # 모든 응답은 {"error_detail": "..."} 구조를 유지하도록 강제합니다.
        custom_payload = {"error_detail": processed_detail}

        super().__init__(detail=custom_payload)

    def _parse_detail(self, detail: Any) -> str:
        """
        다양한 타입의 detail 입력을 문자열 메시지로 변환합니다.
        """
        if detail is None:
            return "잘못된 요청입니다."

        # Enum 객체(ErrorMessages)인 경우 .value 추출
        if hasattr(detail, "value"):
            return str(detail.value)

        # 딕셔너리인 경우 기존 키(error_detail, detail)에서 추출
        if isinstance(detail, dict):
            return str(detail.get("error_detail") or detail.get("detail") or str(detail))

        # 리스트인 경우 첫 번째 요소 추출
        if isinstance(detail, list) and detail:
            return self._parse_detail(detail[0])

        return str(detail)
