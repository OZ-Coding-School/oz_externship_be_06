# apps/posts/views/post_category_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from ..models.post_category import PostCategory
from ..serializers.post_category_serializers import PostCategorySerializer

class PostCategoryListView(APIView):
    @extend_schema(
        tags=["posts"], # "Community - Category"에서 "posts"로 변경
        summary="게시글 카테고리 목록 조회",
        description="활성화된 모든 게시글 카테고리 목록을 조회합니다.",
        responses={200: PostCategorySerializer(many=True)}
    )
    def get(self, request):
        # 활성화된 카테고리만 가져옵니다.
        categories = PostCategory.objects.filter(status=True)
        serializer = PostCategorySerializer(categories, many=True)
        return Response(serializer.data)