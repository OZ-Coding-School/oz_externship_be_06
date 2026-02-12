from __future__ import annotations

from typing import Any

from django.db.models import Prefetch, QuerySet
from rest_framework import status

from apps.qna.constants import SORT_CHOICES, ErrorMessages
from apps.qna.exceptions import QnaBaseException
from apps.qna.models import Answer, Question
from apps.qna.services.base_question_query import BaseQuestionQueryService


class AdminQuestionQueryService(BaseQuestionQueryService):
    """
    - get_question_list: 질문 목록 조회
        _apply_category_filter
        _apply_search_filter
        _apply_status_filter
        _apply_sorting
    - get_question_detail: 질문 상세 조회
    """

    @staticmethod
    def get_question_list(filters: dict[str, Any]) -> QuerySet[Question]:
        """
        검색, 필터링, 정렬 로직을 수행하고 질문 목록을 반환
        - Args:
            filters (dict):
                검색어(search_keyword),
                카테고리(category_id),
                답변상태(answer_status),
                정렬(sort)
        - Returns:
            QuerySet[Question]: 필터링된 질문 QuerySet
            or []: 어떤 값도 필터링 되지 않았을때
        - Raises:
            QnaBaseException: 카테고리 id가 존재하지 않을 경우 (404)
        """
        queryset = Question.objects.select_related("author", "category__parent__parent")

        # 카테고리 필터
        queryset = AdminQuestionQueryService._apply_category_filter(queryset, filters.get("category_id"))
        queryset = AdminQuestionQueryService._apply_search_filter(queryset, filters.get("search_keyword"))
        queryset = AdminQuestionQueryService._apply_status_filter(queryset, filters.get("answer_status"))
        queryset = AdminQuestionQueryService._apply_sorting(queryset, filters.get("sort", SORT_CHOICES[0]))

        return queryset

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
