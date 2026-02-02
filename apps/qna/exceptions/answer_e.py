from rest_framework import status

from apps.qna.constants import ErrorMessages
from apps.qna.exceptions.base_e import QnaBaseException


class AnswerNotFoundException(QnaBaseException):
    """
    [404] Not Found(데이터가 존재하지 않음)
    """

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = ErrorMessages.DEFAULT_MESSAGE_409
    default_code = "answer_not_found"


class AdoptedAnswerConflictException(QnaBaseException):
    """
    [409] Conflict(데이터 중복)
    """

    status_code = status.HTTP_409_CONFLICT
    default_detail = ErrorMessages.ALREADY_EXISTS_ADOPTED_ANSWER
    default_code = "answer_already_adopted"
