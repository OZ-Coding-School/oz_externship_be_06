from typing import Any

from django.db import transaction

from apps.qna.exceptions.question_exception import QuestionBaseException
from apps.qna.models import Question, QuestionCategory


class QuestionService:
    @staticmethod
    @transaction.atomic
    def create_question(author: Any, data: dict[str, Any]) -> Question:
        """
        질문 생성 로직
        """
        try:
            category_id = data.pop("category_id")

            # 카테고리 획득
            category = QuestionCategory.objects.get(id=category_id)

            # 질문 생성
            question = Question.objects.create(author=author, category=category, **data)

            return question

        except Exception as e:
            # 발생하는 모든 예외를 최상위 예외인 QuestionBaseException으로 전환합니다.
            raise QuestionBaseException(detail=f"질문 등록 중 오류가 발생했습니다: {str(e)}")
