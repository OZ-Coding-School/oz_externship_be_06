from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import AllowAny
from apps.posts.selectors.category_selectors import CategorySelector
from apps.posts.serializers.category_serializers import CategoryListSerializer

class CategoryListView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        summary="카테고리 목록 조회",
        description="커뮤니티 게시글을 작성하거나 필터링할 때 필요한 카테고리(예: 자유게시판, 질문게시판) 목록을 가져옵니다.",
        tags=["posts"]
    )
    def get(self, request: Request) -> Response:
        """
        활성화된 카테고리 목록을 반환하는 API
        데이터가 없는 경우 빈 리스트([])를 반환
        """
        categories = CategorySelector.get_category_list()
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)