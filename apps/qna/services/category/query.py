from __future__ import annotations

from django.db.models import QuerySet

from apps.qna.models import QuestionCategory

# ==============================================================================
# CategoryQueryService
#   - get_question_list: 카테고리 계층 구조 조회
# ==============================================================================


class CategoryQueryService:
    """
    - get_question_list: 카테고리 계층 구조 조회
    """

    @staticmethod
    def get_category_tree() -> QuerySet[QuestionCategory]:
        """
        전체 카테고리를 계층 구조(Tree)로 조회하기 위해 최상위 카테고리 목록을 반환
        - Args:
            없음
        - Returns:
            QuerySet[QuestionCategory]: 최상위 카테고리 QuerySet (하위 카테고리 prefetch 포함)
        """

        return (
            QuestionCategory.objects.filter(parent__isnull=True)
            .prefetch_related("subcategories__subcategories")
            .order_by("name")
        )
