from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException, NotAuthenticated, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.qna.utils.constants import ErrorMessages


class QnaBaseException(APIException):
    """
    QnA 앱의 최상위 예외 클래스
    """

    status_code: int = status.HTTP_400_BAD_REQUEST
    default_detail = ErrorMessages.INVALID_REQUEST
    default_code = "qna_bad_request"

    def __init__(self, detail: Any = None, code: Any = None):
        if isinstance(detail, dict):
            detail = detail.get("error_detail") or detail.get("detail") or str(detail)
        super().__init__(detail, code)


def qna_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """QnA 앱 예외 처리기"""
    response = exception_handler(exc, context)

    # View 클래스명을 통해 현재 에러가 발생한 도메인이 Question인지 Answer인지 판별
    view = context.get("view")
    view_name = view.__class__.__name__ if view else ""
    is_answer = "Answer" in view_name

    # 401 Unauthorized 처리
    if isinstance(exc, NotAuthenticated):
        msg = ErrorMessages.UNAUTHORIZED_ANSWER_CREATE if is_answer else ErrorMessages.UNAUTHORIZED_QUESTION_CREATE
        return Response({"error_detail": msg.value}, status=status.HTTP_401_UNAUTHORIZED)

    # 403 Forbidden 처리
    elif isinstance(exc, PermissionDenied):
        msg = ErrorMessages.FORBIDDEN_ANSWER_CREATE if is_answer else ErrorMessages.FORBIDDEN_QUESTION_CREATE
        return Response({"error_detail": msg.value}, status=status.HTTP_403_FORBIDDEN)

    # 응답 데이터 규격화 및 메시지 추출
    if response is not None:

        def _extract_msg(data: Any) -> str:
            if isinstance(data, dict):
                # 우선순위: error_detail > detail > 첫 번째 값
                target = data.get("error_detail") or data.get("detail") or next(iter(data.values()), "Unknown Error")
                return _extract_msg(target)
            if isinstance(data, list):
                return _extract_msg(data[0]) if data else "Unknown Error"
            return str(data)

        response.data = {"error_detail": _extract_msg(response.data)}

    return response
