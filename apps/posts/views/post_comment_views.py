from typing import Any

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import generics, parsers, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment
from apps.posts.serializers.post_comment import (
    PostCommentCreateSerializer,
    PostCommentListSerializer,
    PostCommentUpdateSerializer,
)


class PostCommentListAPIView(generics.ListAPIView):  # type: ignore[type-arg]
    """
    특정 게시글의 댓글 목록 조회 API

    GET /api/v1/posts/{post_id}/comments

    Query Parameters:
        - page (int, optional): 페이지 번호
        - page_size (int, optional): 페이지당 항목 수
    """

    serializer_class = PostCommentListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self) -> QuerySet[PostComment]:
        """
        특정 게시글의 댓글 목록을 반환합니다.
        """
        post_id = self.kwargs.get("post_id")

        # 게시글 존재 여부 확인
        try:
            Post.objects.get(pk=post_id, is_visible=True)
        except Post.DoesNotExist as e:
            raise NotFound(detail="해당 게시글을 찾을 수 없습니다.") from e

        # 댓글 조회 (작성일 기준 오름차순)
        queryset = (
            PostComment.objects.filter(post_id=post_id)
            .select_related("author")
            .prefetch_related("tags__tagged_user")
            .order_by("created_at")
        )

        return queryset

    @extend_schema(
        operation_id="v1_post_comments_list",
        tags=["Comments"],
        summary="게시글 댓글 목록 조회 API",
        responses={200: PostCommentListSerializer(many=True), 404: {"description": "해당 게시글을 찾을 수 없습니다."}},
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        특정 게시글의 댓글 목록을 페이지네이션하여 반환합니다.
        """
        return super().get(request, *args, **kwargs)


class _EmptyTags:
    def select_related(self, *args: object, **kwargs: object) -> "_EmptyTags":
        return self

    def all(self) -> list[object]:
        return []


class _MockAuthor:
    def __init__(self, id: int = 1, nickname: str = "mock-user", profile_img_url: str | None = None):
        self.id = id
        self.nickname = nickname
        self.profile_img_url = profile_img_url


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
        # Mock comment 객체 생성 (UpdateSerializer의 validate를 통과하기 위해)
        mock_comment = type("Comment", (), {})()
        mock_comment.id = comment_id
        mock_comment.content = "Mock comment"
        mock_comment.author = request.user if hasattr(request, "user") else _MockAuthor()

        serializer = self.serializer_class(instance=mock_comment, data=request.data, context={"request": request})
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
