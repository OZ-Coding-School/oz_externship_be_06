from typing import Any

from django.db import transaction

from apps.qna.exceptions.question_exception import QuestionBaseException
from apps.qna.models import Question, QuestionCategory


class QuestionCommandService:
    """
    질문 데이터 변경(CUD) 로직 처리 서비스
    """

    @staticmethod
    @transaction.atomic
    def create_question(author: Any, data: dict[str, Any]) -> Question:
        """질문 생성 로직"""
        try:
            category_id = data.pop("category_id")
            category = QuestionCategory.objects.get(id=category_id)  # 카테고리 획득
            question = Question.objects.create(author=author, category=category, **data)  # 질문 생성
            return question

        except Exception:  # 발생하는 모든 예외를 최상위 예외인 QuestionBaseException으로 전환
            raise QuestionBaseException(detail="유효하지 않은 질문 등록 요청입니다.")
