from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException, NotAuthenticated, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import exception_handler


class QuestionBaseException(APIException):
    """
    QnA 앱의 최상위 예외 클래스 (400 Bad Request)
    에러 메시지는 명세서에 따라 발생 시점(Service/Serializer)에서 주입
    """

    status_code: int = status.HTTP_400_BAD_REQUEST
    default_detail = {"error_detail": "유효하지 않은 질문 요청입니다."}
    default_code = "question_bad_request"

    def __init__(self, detail: Any = None, code: Any = None):
        # 만약 detail이 딕셔너리로 들어오면 메시지만 추출하여 문자열로 저장
        if isinstance(detail, dict):
            detail = detail.get("error_detail") or detail.get("detail") or str(detail)
        super().__init__(detail, code)


class QuestionPermissionDeniedException(QuestionBaseException):
    """
    권한 부족 예외 (403 Forbidden)
    """

    status_code: int = status.HTTP_403_FORBIDDEN
    default_detail = {"error_detail": "질문 등록 권한이 없습니다."}
    default_code = "question_permission_denied"


class QuestionNotFoundException(QuestionBaseException):
    """
    데이터가 존재하지 않을 때 예외 (404 Not Found)
    """

    status_code: int = status.HTTP_404_NOT_FOUND
    default_detail = {"error_detail": "해당 질문을 찾을 수 없습니다."}
    default_code = "question_not_found"


def qna_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """QnA 앱 예외 처리기"""
    response = exception_handler(exc, context)

    if isinstance(exc, NotAuthenticated):
        return Response(
            {"error_detail": "로그인한 수강생만 질문을 등록할 수 있습니다."}, status=status.HTTP_401_UNAUTHORIZED
        )

    if isinstance(exc, PermissionDenied):
        return Response({"error_detail": "질문 등록 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    # 모든 응답 데이터 규격을 {"error_detail": str} 로 통일
    if response is not None:
        if isinstance(response.data, dict):
            # 기존 'detail'이나 'error_detail'에서 순수 메시지만 추출
            raw_msg = response.data.get("error_detail") or response.data.get("detail") or str(response.data)

            # 만약 DRF 기본 에러(딕셔너리 리스트 등)가 넘어온 경우 첫 번째 메시지만 획득
            if isinstance(raw_msg, dict):
                first_key = next(iter(raw_msg))
                val = raw_msg[first_key]
                raw_msg = val[0] if isinstance(val, list) else val
            elif isinstance(raw_msg, list):
                raw_msg = raw_msg[0]

            response.data = {"error_detail": str(raw_msg)}
        else:
            response.data = {"error_detail": str(response.data)}

    return response
