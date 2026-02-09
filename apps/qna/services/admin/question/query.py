from django.db.models import Prefetch
from rest_framework import status

from apps.qna.constants import ErrorMessages
from apps.qna.exceptions.base import QnaBaseException
from apps.qna.models import Answer, Question


class AdminQuestionQueryService:
    """
    어드민 질문 데이터 조회(Read) 로직 처리 서비스
    """

    @staticmethod
    def get_question_detail(question_id: int) -> Question:
        """
        어드민 질문 상세 정보를 조회 (조회수 증가 없음)

        - Args:
            question_id (int): 조회할 질문의 ID (PK)
        - Returns:
            Question: 상세 정보를 포함한 질문 객체
        - Raises:
            QnaBaseException: 질문이 존재하지 않을 경우 (404)
        """
        try:
            question = (
                Question.objects.select_related("author", "category__parent__parent")
                .prefetch_related(
                    "images",
                    # 질문 작성자 course_generation
                    "author__cohort_students__cohort__course",
                    # 답변 + 답변 작성자 enrollment 관계
                    Prefetch(
                        "answers",
                        queryset=Answer.objects.select_related("author").prefetch_related(
                            "author__cohort_students__cohort__course",
                            "author__assisted_cohorts__cohort__course",
                            "author__coached_courses__course",
                            "author__managed_courses__course",
                        ),
                    ),
                )
                .get(id=question_id)
            )

            return question

        except Question.DoesNotExist:
            raise QnaBaseException(detail=ErrorMessages.NOT_FOUND_QUESTION, status_code=status.HTTP_404_NOT_FOUND)
