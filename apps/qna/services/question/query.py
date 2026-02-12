from __future__ import annotations

from typing import Any

from django.db import transaction
from django.db.models import F, QuerySet
from rest_framework import status

from apps.qna.constants import ErrorMessages
from apps.qna.exceptions import QnaBaseException
from apps.qna.models import Question
from apps.qna.services.base_question_query import BaseQuestionQueryService

# ==============================================================================
# QuestionQueryService
#   - get_question_list: 질문 목록 조회
#   - get_question_detail: 질문 상세 조회
# ==============================================================================


class QuestionQueryService(BaseQuestionQueryService):
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
        - Raises:
            QnaBaseException(404): 조건에 맞는 질문이 하나도 없을 경우
        """

        # QuerySet 구성
        queryset = Question.objects.select_related("author", "category__parent__parent")

        # 필터링 및 정렬
        queryset = QuestionQueryService._apply_category_filter(queryset, filters.get("category_id"))
        queryset = QuestionQueryService._apply_search_filter(queryset, filters.get("search_keyword"))
        queryset = QuestionQueryService._apply_status_filter(queryset, filters.get("answer_status"))
        queryset = QuestionQueryService._apply_sorting(queryset, filters.get("sort", "latest"))

        return queryset

    @staticmethod
    @transaction.atomic
    def get_question_detail(question_id: int) -> Question:
        """
        질문 상세 정보를 조회하고 조회수를 1 증가
        - Args:
            question_id (int): 조회할 질문의 ID (PK)
        - Returns:
            Question: 상세 정보를 포함한 질문 객체
                Author,
                Category,
                Answers,
                Comments
        - Raises:
            QnaBaseException(404): 질문이 존재하지 않을 경우
        """

        try:
            # 조회수 증가
            Question.objects.filter(id=question_id).update(view_count=F("view_count") + 1)

            # 질문 조회 및 관련 데이터 로딩
            question = (
                Question.objects.select_related("author", "category__parent__parent")
                .prefetch_related("images", "answers__author", "answers__comments__author")
                .get(id=question_id)
            )

            return question

        except Question.DoesNotExist:
            raise QnaBaseException(detail=ErrorMessages.NOT_FOUND_QUESTION, status_code=status.HTTP_404_NOT_FOUND)
