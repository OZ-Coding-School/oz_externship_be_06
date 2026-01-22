from rest_framework import status
from rest_framework.exceptions import APIException


class QuestionBaseException(APIException):
    """QnA 앱의 최상위 예외 클래스 (400 Bad Request)"""

    status_code: int = status.HTTP_400_BAD_REQUEST
    default_detail = "질문 처리 중 오류가 발생했습니다."
    default_code = "question_error"


class QuestionPermissionDeniedException(QuestionBaseException):
    """권한 부족 예외 (403 Forbidden)"""

    status_code: int = status.HTTP_403_FORBIDDEN
    default_detail = "해당 질문에 대한 권한이 없습니다."
    default_code = "permission_denied"


class QuestionAuthenticationRequiredException(QuestionBaseException):
    """인증 필요 예외 (401 Unauthorized)"""

    status_code: int = status.HTTP_401_UNAUTHORIZED
    default_detail = "인증 정보가 유효하지 않습니다."
    default_code = "authentication_failed"
