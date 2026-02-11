from __future__ import annotations

from django.db.models import Count, Q, QuerySet
from rest_framework import status

from apps.qna.constants import ANSWER_STATUS_CHOICES, SORT_CHOICES, ErrorMessages
from apps.qna.exceptions import QnaBaseException
from apps.qna.models import Question, QuestionCategory


class BaseQuestionQueryService:
    """
    질문 목록 조회를 위한 공통 로직을 제공하는 베이스 서비스
    QuestionQueryService와 AdminQuestionQueryService에서 상속하여 사용
    """

    @staticmethod
    def _apply_category_filter(queryset: QuerySet[Question], category_id: int | None) -> QuerySet[Question]:
        """
        카테고리 ID로 질문 필터링
        - Args:
            queryset (QuerySet[Question]): 필터링할 질문 QuerySet
            category_id (int | None): 카테고리 ID (None일 경우 필터링 안함)
        - Returns:
            QuerySet[Question]: 필터링된 질문 QuerySet
        - Raises:
            QnaBaseException(404): 카테고리가 존재하지 않을 경우
        """
        if not category_id:
            return queryset

        # DB에 존재하지 않는 카테고리일 경우만 404 발생
        if not QuestionCategory.objects.filter(id=category_id).exists():
            raise QnaBaseException(detail=ErrorMessages.NOT_FOUND_CATEGORY, status_code=status.HTTP_404_NOT_FOUND)

        return queryset.filter(category_id=category_id)

    @staticmethod
    def _apply_search_filter(queryset: QuerySet[Question], keyword: str | None) -> QuerySet[Question]:
        """
        검색 키워드로 질문 필터링 (제목 또는 내용에서 검색)
        - Args:
            queryset (QuerySet[Question]): 필터링할 질문 QuerySet
            keyword (str | None): 검색 키워드 (None일 경우 필터링 안함)
        - Returns:
            QuerySet[Question]: 필터링된 질문 QuerySet
        """
        if not keyword:
            return queryset
        return queryset.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword))

    @staticmethod
    def _apply_status_filter(queryset: QuerySet[Question], answer_status: str | None) -> QuerySet[Question]:
        """
        답변 상태에 따른 필터링 (성능 최적화 적용)
        - Args:
            queryset (QuerySet[Question]): 필터링할 질문 QuerySet
            answer_status (str | None): 답변 상태 ('waiting', 'answered', None)
        - Returns:
            QuerySet[Question]: 필터링된 질문 QuerySet
        """

        # waiting
        if answer_status == ANSWER_STATUS_CHOICES[0]:
            # Count를 구하는 것보다 역참조 존재 여부를 체크하는 것이 훨씬 빠름
            return queryset.filter(answers__isnull=True)

        # answered
        if answer_status == ANSWER_STATUS_CHOICES[1]:
            # 답변이 하나라도 있는 경우 (Distinct를 통한 중복 방지)
            return queryset.filter(answers__isnull=False).distinct()

        return queryset

    @staticmethod
    def _apply_sorting(queryset: QuerySet[Question], sort: str) -> QuerySet[Question]:
        """
        정렬 전략 분리
        - Args:
            queryset (QuerySet[Question]): 정렬할 질문 QuerySet
            sort (str): 정렬 방식 ('latest', 'oldest', 'most_views')
        - Returns:
            QuerySet[Question]: 정렬된 질문 QuerySet (답변 개수 annotate 포함)
        """
        # 정렬 시 created_at과 id를 같이 사용하여 페이징 시 정렬 보장 (Stable Sort)
        sort_map = {
            SORT_CHOICES[0]: ["-created_at", "-id"],  # "latest"
            SORT_CHOICES[1]: ["created_at", "id"],  # "oldest"
            SORT_CHOICES[2]: ["-view_count", "-created_at"],  # "most_views"
        }

        order_by = sort_map.get(sort, sort_map[SORT_CHOICES[0]])

        # 목록 조회 시점에 답변 개수가 필요하다면 여기서만 annotate (지연 연산)
        return queryset.annotate(answer_count=Count("answers")).order_by(*order_by)
