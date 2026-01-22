from typing import Any

from django.db import transaction

from apps.qna.exceptions.question_exception import QuestionBaseException
from apps.qna.models import Question, QuestionCategory, QuestionImage


class QuestionService:
    @staticmethod
    @transaction.atomic
    def create_question(author: Any, data: dict[str, Any]) -> Question:
        """
        질문 생성 및 리소스 연결 로직
        """
        try:
            category_id = data.pop("category_id")
            image_ids = data.pop("image_ids", [])

            # 카테고리 획득
            category = QuestionCategory.objects.get(id=category_id)

            # 질문 생성
            question = Question.objects.create(author=author, category=category, **data)

            # 이미지 연관 관계 업데이트
            if image_ids:
                QuestionImage.objects.filter(id__in=image_ids, question__isnull=True).update(question=question)

            return question

        except Exception as e:
            # 발생하는 모든 예외를 최상위 예외인 QuestionBaseException으로 전환합니다.
            raise QuestionBaseException(detail=f"질문 등록 중 오류가 발생했습니다: {str(e)}")
