from typing import Any

from django.db import transaction
from rest_framework import status

from apps.qna.constants import ErrorMessages
from apps.qna.exceptions import QnaBaseException
from apps.qna.models import Question, QuestionCategory
from apps.qna.utils.model_types import User


class QuestionCommandService:
    """
    질문 데이터 변경(CUD) 로직 처리 서비스
    """

    @staticmethod
    @transaction.atomic
    def create_question(author: User, data: dict[str, Any]) -> Question:
        """
        새로운 질문 생성

        - Args:
            author (User): 질문 작성자 객체 (User Instance)
            data (dict): title(str), content(str), category_id(int)를 포함한 검증된 데이터

        - Returns:
            Question: 생성된 질문 객체

        """

        category_id = data.pop("category_id")

        try:
            category = QuestionCategory.objects.get(id=category_id)
        except QuestionCategory.DoesNotExist:
            raise QnaBaseException(detail=ErrorMessages.NOT_FOUND_CATEGORY, status_code=status.HTTP_404_NOT_FOUND)

        question = Question.objects.create(author=author, category=category, **data)
        return question
