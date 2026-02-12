from __future__ import annotations

from django.db import transaction
from rest_framework import status

from apps.qna.constants import ErrorMessages
from apps.qna.exceptions import QnaBaseException
from apps.qna.models.answer import Answer


class AdminAnswerCommandService:
    """
    - delete_answer: 답변 삭제
    """

    @classmethod
    @transaction.atomic
    def delete_answer(cls, answer_id: int) -> dict[str, int]:
        """
        답변 삭제
        - Args:
            answer_id (int): 삭제할 답변 ID
        - Returns:
            dict: answer_id, deleted_comment_count
        - Raises:
            QnaBaseException: 답변이 존재하지 않을 경우 (404)
        """
        try:
            answer = Answer.objects.get(id=answer_id)
        except Answer.DoesNotExist:
            raise QnaBaseException(
                detail=ErrorMessages.NOT_FOUND_ADMIN_ANSWER,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # 삭제 전 카운트 (CASCADE 삭제 전에 집계)
        comment_count = answer.comments.count()

        # 답변 삭제 (CASCADE: AnswerComment)
        answer.delete()

        return {
            "answer_id": answer_id,
            "deleted_comment_count": comment_count,
        }
