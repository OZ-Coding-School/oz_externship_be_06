from __future__ import annotations

from django.db import transaction
from rest_framework import status

from apps.qna.constants import ErrorMessages
from apps.qna.exceptions import QnaBaseException
from apps.qna.models import AnswerComment, Question


class AdminQuestionCommandService:
    """
    - delete_question: 질의응답 삭제
    """

    @staticmethod
    @transaction.atomic
    def delete_question(question_id: int) -> dict[str, int]:
        """
        질문과 관련된 답변, 댓글을 모두 삭제

        - Args:
            question_id (int): 삭제할 질문의 PK
        - Returns:
            dict: question_id, deleted_answer_count, deleted_comment_count
        - Raises:
            QnaBaseException: 질문이 존재하지 않을 경우 (404)
        """
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise QnaBaseException(
                detail=ErrorMessages.NOT_FOUND_ADMIN_QUESTION,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # 삭제 전 카운트 (CASCADE 삭제 전에 집계)
        answer_count = question.answers.count()
        comment_count = AnswerComment.objects.filter(answer__question=question).count()

        # 질문 삭제 (CASCADE: Answer, AnswerComment, QuestionImage, AnswerImage, QuestionAIAnswer)
        question.delete()

        return {
            "question_id": question_id,
            "deleted_answer_count": answer_count,
            "deleted_comment_count": comment_count,
        }
