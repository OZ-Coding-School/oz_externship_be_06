from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Optional

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import (
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.qna.constants import ErrorMessages
from apps.qna.exceptions import QnaBaseException

logger = logging.getLogger(__name__)

# ==============================================================================
# 에러 메시지 매핑 테이블 (View + Method 조합)
# ==============================================================================
_PERMISSION_ERROR_MAP: dict[tuple[str, str, bool], ErrorMessages] = {
    # ---------- Question -----------
    # 질문 등록
    ("QuestionCreateListAPIView", "POST", True): ErrorMessages.UNAUTHORIZED_QUESTION_CREATE,
    ("QuestionCreateListAPIView", "POST", False): ErrorMessages.FORBIDDEN_QUESTION_CREATE,
    # 질문 수정
    ("QuestionUpdateAPIView", "PUT", True): ErrorMessages.UNAUTHORIZED_QUESTION_UPDATE,
    ("QuestionUpdateAPIView", "PUT", False): ErrorMessages.FORBIDDEN_QUESTION_UPDATE,
    # ---------- Answer -----------
    # AI 답변 생성 및 생성된 답변 조회
    ("AIAnswerGenerateAPIView", "GET", True): ErrorMessages.UNAUTHORIZED_AI_REQUEST,
    # 답변 등록
    ("AnswerCreateAPIView", "POST", True): ErrorMessages.UNAUTHORIZED_ANSWER_CREATE,
    ("AnswerCreateAPIView", "POST", False): ErrorMessages.FORBIDDEN_ANSWER_CREATE,
    # 답변 수정
    ("AnswerUpdateAPIView", "PUT", True): ErrorMessages.UNAUTHORIZED_ANSWER_UPDATE,
    ("AnswerUpdateAPIView", "PUT", False): ErrorMessages.FORBIDDEN_ANSWER_UPDATE,
    # 답변 채택
    ("AnswerAdoptAPIView", "POST", True): ErrorMessages.UNAUTHORIZED_ANSWER_ADOPT,
    ("AnswerAdoptAPIView", "POST", False): ErrorMessages.FORBIDDEN_ANSWER_ADOPT,
    # 답변 댓글 작성
    ("AnswerCommentCreateAPIView", "POST", True): ErrorMessages.UNAUTHORIZED_COMMENT_CREATE,
    ("AnswerCommentCreateAPIView", "POST", False): ErrorMessages.FORBIDDEN_COMMENT_CREATE,
    # ---------- Admin Category -----------
    # 어드민 카테고리 등록
    ("AdminCategoriesAPIView", "POST", True): ErrorMessages.UNAUTHORIZED_ADMIN_CATEGORY_CREATE,
    ("AdminCategoriesAPIView", "POST", False): ErrorMessages.FORBIDDEN_ADMIN_CATEGORY_CREATE,
    # 어드민 카테고리 목록 조회
    ("AdminCategoriesAPIView", "GET", True): ErrorMessages.UNAUTHORIZED_ADMIN_CATEGORY_LIST,
    ("AdminCategoriesAPIView", "GET", False): ErrorMessages.FORBIDDEN_ADMIN_CATEGORY_LIST,
    # 어드민 카테고리 삭제
    ("AdminCategoryDeleteAPIView", "DELETE", True): ErrorMessages.UNAUTHORIZED_ADMIN_CATEGORY_DELETE,
    ("AdminCategoryDeleteAPIView", "DELETE", False): ErrorMessages.FORBIDDEN_ADMIN_CATEGORY_DELETE,
    # ---------- Admin Question -----------
    # 어드민 질문 목록 조회
    ("AdminQuestionListAPIView", "GET", True): ErrorMessages.UNAUTHORIZED_ADMIN_QUESTION_LIST,
    ("AdminQuestionListAPIView", "GET", False): ErrorMessages.FORBIDDEN_ADMIN_QUESTION_LIST,
    # 어드민 질문 상세 조회
    ("AdminQuestionDetailAPIView", "GET", True): ErrorMessages.UNAUTHORIZED_ADMIN_QUESTION_DETAIL,
    ("AdminQuestionDetailAPIView", "GET", False): ErrorMessages.FORBIDDEN_ADMIN_QUESTION_DETAIL,
    # 어드민 질의응답 삭제
    ("AdminQuestionDetailAPIView", "DELETE", True): ErrorMessages.UNAUTHORIZED_ADMIN_QUESTION_DELETE,
    ("AdminQuestionDetailAPIView", "DELETE", False): ErrorMessages.FORBIDDEN_ADMIN_QUESTION_DELETE,
    # ---------- Admin -----------
    # [DELETE] Admin delete answer
    ("AdminAnswerDeleteAPIView", "DELETE", True): ErrorMessages.UNAUTHORIZED_ADMIN_ANSWER_DELETE,
    ("AdminAnswerDeleteAPIView", "DELETE", False): ErrorMessages.FORBIDDEN_ADMIN_ANSWER_DELETE,
}

# 기본 폴백 메시지
_DEFAULT_AUTH_ERROR = ErrorMessages.DEFAULT_401
_DEFAULT_PERM_ERROR = ErrorMessages.DEFAULT_403


def qna_exception_handler(exc: Exception, context: dict[str, Any]) -> Optional[Response]:
    """QnA 앱 예외 처리기 + 로깅 중앙화"""
    request = context.get("request")
    view = context.get("view")
    method = (request.method or "").upper() if request else ""
    view_name = view.__class__.__name__ if view else ""
    user_info = f"User({request.user.pk})" if request and request.user.is_authenticated else "Anonymous"

    # 예외 종류별 응답 생성
    response: Optional[Response] = None

    if isinstance(exc, (NotAuthenticated, PermissionDenied)):
        response = _handle_permission_errors(exc, view_name, method)

    elif isinstance(exc, ObjectDoesNotExist):
        # Django ORM DoesNotExist → 404 또는 400으로 변환
        response = _handle_object_not_found(exc, view)

    else:
        # DRF 기본 핸들러 실행 (ValidationError, QnaBaseException 등 포함)
        response = exception_handler(exc, context)
        if response is not None:
            msg = _extract_custom_msg(exc, response.data, view)
            response.data = {"error_detail": msg}

    # 중앙 로깅 (401, 403, 400, 404, 409, 500 통합)
    if response is not None:
        _log_exception(response.status_code, view_name, method, user_info, exc)
    else:
        # 핸들러가 잡지 못한 치명적 에러 (500)
        logger.error(f"[Critical Error] {view_name} {method} | {user_info} | {str(exc)}", exc_info=True)
        return Response(
            {"error_detail": ErrorMessages.SYSTEM_ERROR.value}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response


def _handle_permission_errors(exc: Exception, view_name: str, method: str) -> Response:
    """권한 에러 발생 시 View 이름과 Method를 조합하여 커스텀 메시지 출력"""
    is_auth_error = isinstance(exc, NotAuthenticated)

    key = (view_name, method, is_auth_error)
    msg = _PERMISSION_ERROR_MAP.get(key)

    # 폴백 메시지 (매핑되지 않은 경우)
    msg_str: str
    if msg is None:
        msg_str = _DEFAULT_AUTH_ERROR.value if is_auth_error else _DEFAULT_PERM_ERROR.value
    else:
        msg_str = msg.value

    status_code = status.HTTP_401_UNAUTHORIZED if is_auth_error else status.HTTP_403_FORBIDDEN
    return Response({"error_detail": msg_str}, status=status_code)


def _handle_object_not_found(exc: Exception, view: Any) -> Response:
    """Django ORM의 DoesNotExist 예외를 400 또는 404로 변환"""
    # 모델명 추출 시도
    model_name = ""
    if hasattr(exc, "model"):
        model_name = exc.model.__name__
    elif hasattr(exc, "__class__") and hasattr(exc.__class__, "__qualname__"):
        # Model.DoesNotExist 형태에서 모델명 추출
        qualname = exc.__class__.__qualname__
        if "." in qualname:
            model_name = qualname.split(".")[0]

    # 모델별 에러 메시지 매핑
    not_found_messages = {
        "Question": ErrorMessages.NOT_FOUND_QUESTION,
        "Answer": ErrorMessages.NOT_FOUND_ANSWER,
        "QuestionCategory": ErrorMessages.NOT_FOUND_ADMIN_CATEGORY,
    }

    error_msg = not_found_messages.get(model_name, ErrorMessages.DEFAULT_404)

    # 입력값으로 인한 DoesNotExist는 400, 리소스 조회는 404
    # View 이름에 Detail이 포함되면 404, 아니면 400 (생성/수정 시 FK 조회 실패)
    view_name = view.__class__.__name__ if view else ""
    if "Detail" in view_name or "List" in view_name:
        return Response({"error_detail": error_msg.value}, status=status.HTTP_404_NOT_FOUND)

    return Response({"error_detail": error_msg.value}, status=status.HTTP_400_BAD_REQUEST)


def _log_exception(status_code: int, view_name: str, method: str, user_info: str, exc: Exception) -> None:
    """상태 코드별 로깅 레벨 분기"""
    log_prefix = f"{view_name} {method} | {user_info}"

    if status_code >= 500:
        logger.error(f"[System Error] {log_prefix} | {str(exc)}", exc_info=True)
    elif status_code == 401:
        logger.info(f"[Auth Required] {status_code} | {log_prefix}")
    elif status_code == 403:
        logger.warning(f"[Permission Denied] {status_code} | {log_prefix} | {str(exc)}")
    elif status_code == 404:
        logger.info(f"[Not Found] {status_code} | {log_prefix} | {str(exc)}")
    elif status_code == 409:
        logger.warning(f"[Conflict] {status_code} | {log_prefix} | {str(exc)}")
    else:
        # 400 Bad Request 등
        logger.warning(f"[Client Error] {status_code} | {log_prefix} | {str(exc)}")


def _extract_custom_msg(exc: Exception, data: Any, view: Any) -> str:
    """
    ValidationError, ObjectDoesNotExist에 메세지가 있다면 추출
    그 외에는 시리얼라이저의 default_error_message 값을 추출
    """
    try:
        # QnaBaseException은 예외 자체의 메시지를 우선 사용
        if isinstance(exc, QnaBaseException):
            return str(exc.detail)

        first_msg = _get_first_message(data)

        status_code = getattr(exc, "status_code", None)
        if status_code == 400 or isinstance(exc, (ValidationError, ObjectDoesNotExist)):
            serializer_class = _get_serializer_class(view)

            if serializer_class:
                custom_msg = getattr(serializer_class, "default_error_message", None)

                if isinstance(data, dict) and "non_field_errors" in data:
                    return first_msg

                if custom_msg:
                    return str(custom_msg.value) if hasattr(custom_msg, "value") else str(custom_msg)

        return first_msg

    except Exception as e:
        # 메시지 추출 실패 시 안전하게 폴백
        logger.warning(f"[Message Extraction Failed] {str(e)}", exc_info=True)
        return _get_first_message(data)


def _get_serializer_class(view: Any) -> Optional[type[Any]]:
    """View에서 현재 요청에 해당하는 Serializer 클래스를 추출"""
    if view is None:
        return None

    # get_serializer_class() 메서드
    if hasattr(view, "get_serializer_class"):
        try:
            result = view.get_serializer_class()
            return result if isinstance(result, type) else None
        except Exception:
            pass

    # serializer_class 또는 serializer_classes 딕셔너리 (메서드별 분기)
    request = getattr(view, "request", None)
    method = request.method.upper() if request else ""

    # serializer_class (singular) 먼저 확인
    if hasattr(view, "serializer_class"):
        classes = getattr(view, "serializer_class")
        if isinstance(classes, dict):
            result = classes.get(method)
            return result if isinstance(result, type) else None

    # serializer_classes (plural) 확인
    if hasattr(view, "serializer_classes"):
        classes = getattr(view, "serializer_classes")
        if isinstance(classes, dict):
            result = classes.get(method)
            return result if isinstance(result, type) else None

    # 단일 serializer_class
    if hasattr(view, "serializer_class"):
        result = view.serializer_class
        return result if isinstance(result, type) else None

    return None


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
