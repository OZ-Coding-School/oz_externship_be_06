from django.db.models import QuerySet

from apps.posts.models.post_category import PostCategory


class CategorySelector:
    @staticmethod
    def get_category_list() -> QuerySet[PostCategory]:
        """
        활성화된 모든 카테고리 목록을 ID 순으로 가져옵니다.
        """

        return PostCategory.objects.filter(status=True).order_by("id")
