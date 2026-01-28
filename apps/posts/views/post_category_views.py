from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.posts.models.post_category import PostCategory
from apps.posts.serializers.post_category import PostCategorySerializer


@extend_schema(
    operation_id="v1_post_categories_list",
    tags=["Posts"],
    summary="커뮤니티 게시글 카테고리 목록 조회 API",
    responses={200: PostCategorySerializer(many=True)},
)
class PostCategoryListAPIView(generics.ListAPIView):  # type: ignore[type-arg]
    permission_classes = [AllowAny]
    serializer_class = PostCategorySerializer
    pagination_class = None

    def get_queryset(self) -> QuerySet[PostCategory]:
        return PostCategory.objects.filter(status=True).only("id", "name").order_by("id")
