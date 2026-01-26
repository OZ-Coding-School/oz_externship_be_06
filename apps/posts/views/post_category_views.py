from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from ..serializers.post_category_serializers import PostCategorySerializer

class PostCategoryListView(APIView):
    # Swagger에서 'Community - Category' 그룹으로 표시됩니다.
    @extend_schema(
        tags=["Community - Category"],
        summary="카테고리 목록 조회",
        responses={200: PostCategorySerializer(many=True)}
    )

    def get(self, request):
        mock_categories = [
            {"id": 1, "name": "자유게시판"},
            {"id": 2, "name": "질문답변"},
        ]

        serializer = PostCategorySerializer(mock_categories, many=True)
        return Response(serializer.data)