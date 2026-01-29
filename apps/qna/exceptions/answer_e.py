from rest_framework import status

from apps.qna.exceptions.base_e import QnaBaseException
from apps.qna.utils.constants import ErrorMessages


class AnswerPermissionDeniedException(QnaBaseException):
    """
    [403] Forbidden(권한 부족)
    """

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = ErrorMessages.FORBIDDEN_ANSWER_UPDATE
    default_code = "answer_permission_denied"


class AnswerNotFoundException(QnaBaseException):
    """
    [404] Not Found(데이터가 존재하지 않음)
    """

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = ErrorMessages.NOT_FOUND_ANSWER
    default_code = "answer_not_found"


class AdoptedAnswerConflictException(QnaBaseException):
    """
    [409] Conflict(데이터 중복)
    """

    status_code = status.HTTP_409_CONFLICT
    default_detail = ErrorMessages.ALREADY_EXISTS_ADOPTED_ANSWER
    default_code = "answer_already_adopted"
