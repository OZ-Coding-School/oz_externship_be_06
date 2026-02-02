import logging
from typing import Any

from django.db import transaction

from apps.qna.constants import ErrorMessages
from apps.qna.exceptions.base_e import QnaBaseException
from apps.qna.models import Question, QuestionCategory, QuestionImage
from apps.qna.utils.content_parser import ContentParser
from apps.qna.utils.model_types import User

logger = logging.getLogger(__name__)


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
        category = QuestionCategory.objects.get(id=category_id)  # 카테고리 획득
        question = Question.objects.create(author=author, category=category, **data)  # 질문 생성
        return question
