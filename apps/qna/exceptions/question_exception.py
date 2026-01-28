from rest_framework import status
from rest_framework.exceptions import APIException


class QuestionBaseException(APIException):
    """
    QnA 앱의 최상위 예외 클래스 (400 Bad Request)
    DRF 기본 ValidationError 발생: detail = serializers.ValidationError.detail,
    그 외의 예상치 못한 에러: detail = default_detail
    """

    status_code: int = status.HTTP_400_BAD_REQUEST
    default_detail = "질문 처리 중 오류가 발생했습니다."
    default_code = "question_error"


class QuestionPermissionDeniedException(QuestionBaseException):
    """
    권한 부족 예외 (403 Forbidden)
    """

    status_code: int = status.HTTP_403_FORBIDDEN
    default_detail = "해당 질문에 대한 권한이 없습니다."
    default_code = "permission_denied"


class QuestionNotFoundException(QuestionBaseException):
    """
    데이터가 존재하지 않을 때 예외 (404 Not Found)
    """

    status_code: int = status.HTTP_404_NOT_FOUND
    default_detail = "조회 가능한 질문이 존재하지 않습니다."
    default_code = "question_not_found"
