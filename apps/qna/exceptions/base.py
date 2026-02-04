from typing import Any, Optional

from rest_framework import status
from rest_framework.exceptions import (
    APIException,
)

from apps.qna.constants import ErrorMessages


class QnaBaseException(APIException):
    """
    QnA 앱의 통합 예외 클래스

    사용 예시:
        raise QnaBaseException(detail="커스텀 에러 메시지", status_code=400)
    """

    status_code: int = status.HTTP_400_BAD_REQUEST
    default_detail: str = ErrorMessages.DEFAULT_400.value
    default_code: str = "qna_error"

    def __init__(
        self,
        detail: Any = None,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
    ):
        if status_code is not None:
            self.status_code = status_code

        if detail is None:
            detail = self.default_detail

        # Enum 객체 체크 및 값 추출
        elif hasattr(detail, "value"):
            detail = detail.value

        # 딕셔너리 형태 체크 및 메시지 추출
        elif isinstance(detail, dict):
            detail = detail.get("error_detail") or detail.get("detail") or str(detail)

        # DRF APIException은 detail 속성 사용
        super().__init__(detail=detail, code=code)
