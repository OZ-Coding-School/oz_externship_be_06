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
        # 1. 가짜 데이터를 리스트로 준비합니다.
        mock_categories = [
            {"id": 1, "name": "자유게시판"},
            {"id": 2, "name": "질문답변"},
            {"id": 3, "name": "강사님께 질문"},
            {"id": 4, "name": "학생들의 일상"},
        ]

        # 2. 'serializer' 변수를 여기서 확실히 정의합니다.
        serializer = PostCategorySerializer(mock_categories, many=True)

        # 3. 정의된 'serializer'를 사용하여 응답합니다.
        return Response(serializer.data)