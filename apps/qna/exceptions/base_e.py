import logging
from enum import Enum
from typing import Any, Optional

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.qna.constants import ErrorMessages

logger = logging.getLogger("apps.qna.exceptions")


class QnaBaseException(APIException):
    """
    QnA 앱의 최상위 예외 클래스
    """

    status_code: int = status.HTTP_400_BAD_REQUEST
    default_detail: str | ErrorMessages = ErrorMessages.DEFAULT_400.value
    default_code = "qna_bad_request"

    def __init__(self, detail: Any = None, code: Any = None):
        if detail is None:
            detail = self.default_detail

        # Enum 객체 체크 및 값 추출
        if hasattr(detail, "value"):
            detail = detail.value

        # 딕셔너리 형태 체크 및 메시지 추출
        if isinstance(detail, dict):
            detail = detail.get("error_detail") or detail.get("detail") or str(detail)

        super().__init__(detail, code)


def qna_exception_handler(exc: Exception, context: dict[str, Any]) -> Optional[Response]:
    """QnA 앱 예외 처리기 + 로깅"""
    # 기본 정보 추출
    request = context.get("request")
    view = context.get("view")
    method = request.method.upper() if request else ""
    view_name = view.__class__.__name__ if view else ""
    user_info = f"User({request.user.pk})" if request and request.user.is_authenticated else "Anonymous"

    # 예외 종류별 응답 생성
    response: Optional[Response]
    if isinstance(exc, (NotAuthenticated, PermissionDenied)):
        response = _handle_permission_errors(exc, view_name, method)
    else:
        # DRF 기본 핸들러 실행 (ValidationError 등 포함)
        response = exception_handler(exc, context)

    # 3. 중앙 로깅 (401, 403, 400, 404, 409, 500 통합)
    if response is not None:
        if response.status_code >= 500:
            logger.error(f"[System Error] {view_name} {method} | {user_info} | {str(exc)}", exc_info=True)
        else:
            logger.warning(f"[Business Error] {response.status_code} | {view_name} {method} | {user_info} | {str(exc)}")
    else:
        # 핸들러가 잡지 못한 치명적 에러 (500)
        logger.error(f"[Critical Error] {view_name} {method} | {user_info} | {str(exc)}", exc_info=True)
        return Response(
            {"error_detail": ErrorMessages.SYSTEM_ERROR.value}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # 최종 메시지 가공 (Serializer의 default_error_message 있으면 자동 활용)
    msg = _extract_custom_msg(exc, response.data, view)
    response.data = {"error_detail": msg}
    return response


def _handle_permission_errors(exc: Exception, view_name: str, method: str) -> Response:
    """권한 에러 발생 시 View 이름과 Method를 조합하여 커스텀 메시지 출력"""
    is_auth_error = isinstance(exc, NotAuthenticated)

    if "Question" in view_name:
        if method == "POST":
            msg = (
                ErrorMessages.UNAUTHORIZED_QUESTION_CREATE if is_auth_error else ErrorMessages.FORBIDDEN_QUESTION_CREATE
            )

        elif method == "PUT":
            msg = (
                ErrorMessages.UNAUTHORIZED_QUESTION_UPDATE if is_auth_error else ErrorMessages.FORBIDDEN_QUESTION_UPDATE
            )

    elif "Answer" in view_name:
        if method == "POST":
            if "Create" in view_name:
                msg = (
                    ErrorMessages.UNAUTHORIZED_ANSWER_CREATE if is_auth_error else ErrorMessages.FORBIDDEN_ANSWER_CREATE
                )
            elif "Adopt" in view_name:
                msg = ErrorMessages.UNAUTHORIZED_ANSWER_ADOPT if is_auth_error else ErrorMessages.FORBIDDEN_ANSWER_ADOPT
            elif "Comment" in view_name:
                msg = (
                    ErrorMessages.UNAUTHORIZED_COMMENT_CREATE
                    if is_auth_error
                    else ErrorMessages.FORBIDDEN_COMMENT_CREATE
                )

        elif method == "GET":
            msg = ErrorMessages.UNAUTHORIZED_AI_REQUEST if is_auth_error else ErrorMessages.FORBIDDEN_AI_REQUEST

        elif method == "PUT":
            msg = ErrorMessages.UNAUTHORIZED_ANSWER_UPDATE if is_auth_error else ErrorMessages.FORBIDDEN_ANSWER_UPDATE

    status_code = status.HTTP_401_UNAUTHORIZED if is_auth_error else status.HTTP_403_FORBIDDEN
    return Response({"error_detail": msg.value}, status=status_code)


def _extract_custom_msg(exc: Exception, data: Any, view: Any) -> str:
    """
    시리얼라이저의 default_error_message 설정을 자동으로 반영합니다.
    """
    status_code = getattr(exc, "status_code", None)

    # [수정] ObjectDoesNotExist 예외가 발생한 경우도 400 Bad Request 상황으로 간주합니다.
    is_not_found_input = isinstance(exc, ObjectDoesNotExist)

    if status_code == 400 or isinstance(exc, ValidationError) or is_not_found_input:
        serializer_class = None

        if hasattr(view, "get_serializer_class"):
            try:
                serializer_class = view.get_serializer_class()
            except Exception:
                pass

        if not serializer_class and hasattr(view, "serializer_classes"):
            request = getattr(view, "request", None)
            method = request.method.upper() if request else ""
            classes = getattr(view, "serializer_classes")
            if isinstance(classes, dict):
                serializer_class = classes.get(method)

        if not serializer_class and hasattr(view, "serializer_class"):
            serializer_class = view.serializer_class

        if serializer_class:
            custom_msg = getattr(serializer_class, "default_error_message", None)
            if custom_msg:
                return str(custom_msg.value) if isinstance(custom_msg, Enum) else str(custom_msg)
    return _get_first_message(data)


def _get_first_message(data: Any) -> str:
    """데이터 구조를 파싱하여 첫 번째 에러 문자열을 반환"""
    if isinstance(data, dict):
        if not data:
            return "Unknown Error"
        inner_data = data.get("error_detail") or data.get("detail") or next(iter(data.values()))
        return _get_first_message(inner_data)

    if isinstance(data, list):
        return _get_first_message(data[0]) if data else "Unknown Error"

    if isinstance(data, Enum):
        return str(data.value)

    return str(data)
