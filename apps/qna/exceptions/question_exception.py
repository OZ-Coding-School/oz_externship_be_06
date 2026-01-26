from rest_framework import status
from rest_framework.exceptions import APIException


class QuestionBaseException(APIException):
    """
    QnA 앱의 최상위 예외 클래스 (400 Bad Request)
    DRF 기본 ValidationError 발생은 serializer에서 처리하고,
    그 외의 예상치 못한 에러를 위한 예외처리 클래스
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
