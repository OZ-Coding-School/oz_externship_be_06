from typing import Any

from django.db.models import QuerySet

from apps.qna.constants import CATEGORY_LABELS
from apps.qna.models import QuestionCategory


class AdminCategoryQueryService:
    """
    어드민 카테고리 조회 서비스
    """

    @staticmethod
    def get_category_list(data: dict[str, Any]) -> QuerySet[QuestionCategory]:
        """필터 조건에 맞는 카테고리 목록을 조회"""
        # depth 프로퍼티 계산 및 필터링을 위해 parent 관계를 미리 로드
        queryset = QuestionCategory.objects.select_related("parent", "parent__parent").prefetch_related("subcategories")

        # 검색어 필터
        search_keyword = data.get("search_keyword")
        if search_keyword:
            queryset = queryset.filter(name__icontains=search_keyword)

        # 카테고리 타입 필터
        category_type = data.get("category_type")
        if category_type == CATEGORY_LABELS[0]:
            queryset = queryset.filter(parent__isnull=True)
        elif category_type == CATEGORY_LABELS[1]:
            queryset = queryset.filter(parent__isnull=False, parent__parent__isnull=True)
        elif category_type == CATEGORY_LABELS[2]:
            queryset = queryset.filter(parent__parent__isnull=False)

        # 정렬 (최신순)
        return queryset.order_by("-created_at")
