from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from ..serializers.post_serializers import PostSerializer

# 클래스 전체를 'Community - Post' 그룹으로 묶습니다.
@extend_schema(tags=["Community - Post"])
class PostViewSet(viewsets.ViewSet):
    # Swagger가 입력 데이터 형식을 알 수 있도록 시리얼라이저를 등록합니다.
    serializer_class = PostSerializer

    @extend_schema(summary="게시글 목록 조회")
    def list(self, request):
        mock_posts = [
            {
                "id": 1,
                "title": "Mock 데이터 테스트입니다.",
                "content": "내용입니다.",
            }
        ]
        # 여기서 'serializer' 변수를 정의해야 'Unresolved reference' 오류가 안 납니다.
        serializer = PostSerializer(mock_posts, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="게시글 상세 조회",
        parameters=[
            # {id} 부분이 숫자(int)임을 Swagger에 알려줍니다.
            OpenApiParameter(name='pk', type=int, location=OpenApiParameter.PATH)
        ]
    )
    def retrieve(self, request, pk=None):
        mock_post = {
            "id": int(pk),
            "category_name": "자유게시판",
            "author_name": "코딩파트너",
            "title": f"{pk}번 게시글 상세 조회",
            "content": "상세 내용입니다.",
            "view_count": 11,
            "is_notice": False,
            "created_at": timezone.now()
        }
        # 여기서도 'serializer'를 새로 정의합니다.
        serializer = PostSerializer(mock_post)
        return Response(serializer.data)

    @extend_schema(summary="게시글 작성")
    def create(self, request):
        return Response({"message": "게시글이 작성되었습니다. (Mock)"}, status=status.HTTP_201_CREATED)

    @extend_schema(summary="게시글 수정")
    def update(self, request, pk=None):
        return Response({"message": f"{pk}번 게시글이 수정되었습니다. (Mock)"})

    @extend_schema(summary="게시글 삭제")
    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_204_NO_CONTENT)