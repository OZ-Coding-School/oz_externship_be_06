from rest_framework import status

from apps.qna.constants import ErrorMessages
from apps.qna.exceptions.base_e import QnaBaseException


class QuestionNotFoundException(QnaBaseException):
    """
    [404] Not Found (데이터가 존재하지 않음)
    """

    status_code: int = status.HTTP_404_NOT_FOUND
    default_detail = ErrorMessages.NOT_FOUND_QUESTION
    default_code = "question_not_found"
