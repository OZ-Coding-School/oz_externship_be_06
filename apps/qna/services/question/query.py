from typing import Any

from django.db import transaction
from django.db.models import Count, F, Q, QuerySet
from rest_framework import status

from apps.qna.constants import ErrorMessages
from apps.qna.exceptions.base import QnaBaseException
from apps.qna.models import Question, QuestionCategory


class QuestionQueryService:
    """
    질문 데이터 조회(Read) 로직 처리 서비스
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
            QnaBaseException: 조건에 맞는 질문이 하나도 없을 경우 (404)
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
    def _apply_category_filter(queryset: QuerySet[Question], category_id: int | None) -> QuerySet[Question]:
        if not category_id:
            return queryset

        # DB에 존재하지 않는 카테고리일 경우만 404 발생
        if not QuestionCategory.objects.filter(id=category_id).exists():
            raise QnaBaseException(detail=ErrorMessages.NOT_FOUND_QUESTION, status_code=status.HTTP_404_NOT_FOUND)

        return queryset.filter(category_id=category_id)

    @staticmethod
    def _apply_search_filter(queryset: QuerySet[Question], keyword: str | None) -> QuerySet[Question]:
        if not keyword:
            return queryset
        return queryset.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword))

    @staticmethod
    def _apply_status_filter(queryset: QuerySet[Question], answer_status: str | None) -> QuerySet[Question]:
        """답변 상태에 따른 필터링 (성능 최적화 적용)"""
        if answer_status == "waiting":
            # Count를 구하는 것보다 역참조 존재 여부를 체크하는 것이 훨씬 빠름
            return queryset.filter(answers__isnull=True)

        if answer_status == "answered":
            # 답변이 하나라도 있는 경우 (Distinct를 통한 중복 방지)
            return queryset.filter(answers__isnull=False).distinct()

        return queryset

    @staticmethod
    def _apply_sorting(queryset: QuerySet[Question], sort: str) -> QuerySet[Question]:
        """정렬 전략 분리"""
        # 정렬 시 created_at과 id를 같이 사용하여 페이징 시 정렬 보장 (Stable Sort)
        sort_map = {
            "latest": ["-created_at", "-id"],
            "oldest": ["created_at", "id"],
            "most_views": ["-view_count", "-created_at"],
        }

        order_by = sort_map.get(sort, sort_map["latest"])

        # 목록 조회 시점에 답변 개수가 필요하다면 여기서만 annotate (지연 연산)
        return queryset.annotate(answer_count=Count("answers")).order_by(*order_by)

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
            QnaBaseException: 질문이 존재하지 않을 경우 (404)
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

    @staticmethod
    def get_question_category_tree() -> QuerySet[QuestionCategory]:
        """전체 카테고리를 계층 구조(Tree)로 조회하기 위해 최상위 카테고리 목록을 반환"""
        return (
            QuestionCategory.objects.filter(parent__isnull=True)
            .prefetch_related("subcategories__subcategories")
            .order_by("name")
        )
