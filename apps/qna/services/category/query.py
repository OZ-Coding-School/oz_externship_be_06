
from django.db.models import QuerySet

from apps.qna.models import  QuestionCategory


class CategoryQueryService:
    """
    카테고리 조회(Read) 로직 처리 서비스
    """

    @staticmethod
    def get_category_tree() -> QuerySet[QuestionCategory]:
        """전체 카테고리를 계층 구조(Tree)로 조회하기 위해 최상위 카테고리 목록을 반환"""
        return (
            QuestionCategory.objects.filter(parent__isnull=True)
            .prefetch_related("subcategories__subcategories")
            .order_by("name")
        )