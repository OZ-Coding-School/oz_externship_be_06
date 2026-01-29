from rest_framework import status

from apps.qna.exceptions.base_e import QnaBaseException
from apps.qna.utils.constants import ErrorMessages


class QuestionPermissionDeniedException(QnaBaseException):
    """
    [403] Forbidden (권한 부족)
    """

    status_code: int = status.HTTP_403_FORBIDDEN
    default_detail = ErrorMessages.FORBIDDEN_QUESTION_CREATE
    default_code = "question_permission_denied"


class QuestionNotFoundException(QnaBaseException):
    """
    [404] Not Found (데이터가 존재하지 않음)
    """

    status_code: int = status.HTTP_404_NOT_FOUND
    default_detail = ErrorMessages.NOT_FOUND_QUESTION
    default_code = "question_not_found"
