from drf_spectacular.utils import extend_schema
from rest_framework import parsers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.serializers.post_comment import (
    PostCommentCreateSerializer,
    PostCommentListSerializer,
    PostCommentUpdateSerializer,
)


class _EmptyTags:
    def select_related(self, *args: object, **kwargs: object) -> list[object]:
        return []


class _MockAuthor:
    def __init__(self, id: int = 1, nickname: str = "mock-user", profile_img_url: str | None = None):
        self.id = id
        self.nickname = nickname
        self.profile_img_url = profile_img_url


from rest_framework.request import Request


class PostCommentListCreateAPIView(APIView):
    """댓글 목록 조회 및 생성 (mock 응답)"""

    serializer_class = PostCommentCreateSerializer
    permission_classes = [AllowAny]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    @extend_schema(tags=["Comments"], summary="댓글 등록 API")
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="v1_post_comments_list",
        tags=["Comments"],
        summary="게시글 댓글 전체 목록 조회 API",
        responses={200: PostCommentListSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        mock_data = []
        for i in range(1, 11):
            obj = type("Comment", (), {})()
            obj.id = i
            obj.content = f"Mock comment {i}"
            obj.author = _MockAuthor(id=i, nickname=f"user{i}")
            obj.tags = _EmptyTags()
            obj.created_at = None
            obj.updated_at = None
            mock_data.append(obj)

        serializer = PostCommentListSerializer(mock_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostCommentRetrieveUpdateDestroyAPIView(APIView):
    """댓글 상세 조회 / 수정 / 삭제 (mock 응답)"""

    serializer_class = PostCommentUpdateSerializer
    permission_classes = [AllowAny]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    @extend_schema(tags=["Comments"], summary="댓글 상세 조회 API")
    def get(self, request: Request, comment_id: int) -> Response:
        obj = type("Comment", (), {})()
        obj.id = comment_id
        obj.content = "Mock comment"
        obj.author = _MockAuthor()
        obj.tags = _EmptyTags()
        obj.created_at = None
        obj.updated_at = None
        return Response(PostCommentListSerializer(obj).data, status=status.HTTP_200_OK)

    @extend_schema(tags=["Comments"], summary="댓글 수정 API")
    def put(self, request: Request, comment_id: int) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = type("Comment", (), {})()
        obj.id = comment_id
        obj.content = serializer.validated_data.get("content", "Mock comment")
        obj.author = _MockAuthor()
        obj.tags = _EmptyTags()
        obj.created_at = None
        obj.updated_at = None
        return Response(PostCommentListSerializer(obj).data, status=status.HTTP_200_OK)

    @extend_schema(tags=["Comments"], summary="댓글 삭제 API")
    def delete(self, request: Request, comment_id: int) -> Response:
        return Response(status=status.HTTP_204_NO_CONTENT)
