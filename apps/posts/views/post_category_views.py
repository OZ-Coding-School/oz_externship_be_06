from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.post_category import PostCategory
from ..serializers.post_category_serializers import PostCategorySerializer


class PostCategoryListView(APIView):
    @extend_schema(
        tags=["posts"],
        summary="게시글 카테고리 목록 조회",
        description="활성화된 모든 게시글 카테고리 목록을 조회합니다.",
        responses={200: PostCategorySerializer(many=True)},
    )
    def handle_exception(self, exc: Exception) -> Response:
        response = super().handle_exception(exc)
        if isinstance(response.data, dict):
            detail = response.data.get("detail", response.data)
            response.data = {"error_detail": detail}
        return response

    def get(self, request: Request) -> Response:
        categories = PostCategory.objects.filter(status=True)
        serializer = PostCategorySerializer(categories, many=True)
        return Response(serializer.data)
