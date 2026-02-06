from typing import Any

from django.db.models import Count, Q, QuerySet
from rest_framework import status

from apps.qna.constants import ANSWER_STATUS_CHOICES, SORT_CHOICES, ErrorMessages
from apps.qna.exceptions import QnaBaseException
from apps.qna.models import Question, QuestionCategory


class AdminQuestionQueryService:
    """
    어드민 질의응답 조회 서비스
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
        queryset = AdminQuestionQueryService._apply_status_filter(
            queryset, filters.get("answer_status", ANSWER_STATUS_CHOICES[0])
        )
        queryset = AdminQuestionQueryService._apply_sorting(queryset, filters.get("sort", SORT_CHOICES[0]))

        return queryset

    @staticmethod
    def _apply_category_filter(queryset: QuerySet[Question], category_id: int | None) -> QuerySet[Question]:
        if not category_id:
            return queryset

        # DB에 존재하지 않는 카테고리일 경우만 404 발생
        if not QuestionCategory.objects.filter(id=category_id).exists():
            raise QnaBaseException(detail=ErrorMessages.NOT_FOUND_CATEGORY, status_code=status.HTTP_404_NOT_FOUND)

        return queryset.filter(category_id=category_id)

    @staticmethod
    def _apply_search_filter(queryset: QuerySet[Question], keyword: str | None) -> QuerySet[Question]:
        if not keyword:
            return queryset
        return queryset.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword))

    @staticmethod
    def _apply_status_filter(queryset: QuerySet[Question], answer_status: str) -> QuerySet[Question]:
        """답변 상태에 따른 필터링 (성능 최적화 적용)"""
        # waiting
        if answer_status == ANSWER_STATUS_CHOICES[0]:
            return queryset.filter(answers__isnull=True)

        # answered
        if answer_status == ANSWER_STATUS_CHOICES[1]:
            # 답변이 하나라도 있는 경우 (Distinct를 통한 중복 방지)
            return queryset.filter(answers__isnull=False).distinct()

        return queryset

    @staticmethod
    def _apply_sorting(queryset: QuerySet[Question], sort: str) -> QuerySet[Question]:
        """정렬 전략 분리"""
        # 정렬 시 created_at과 id를 같이 사용하여 페이징 시 정렬 보장 (Stable Sort)
        sort_map = {
            SORT_CHOICES[0]: ["-created_at", "-id"],  # "latest"
            SORT_CHOICES[1]: ["created_at", "id"],  # "oldest"
            SORT_CHOICES[2]: ["-view_count", "-created_at"],  # "most_views"
        }
        order_by = sort_map.get(sort, sort_map[SORT_CHOICES[0]])

        # 목록 조회 시점에 답변 개수가 필요하다면 여기서만 annotate (지연 연산)
        return queryset.order_by(*order_by)
