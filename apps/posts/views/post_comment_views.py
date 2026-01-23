from typing import Any

from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, parsers, serializers, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
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


class PostCommentPagination(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "page_size"
    page_size = 10
    max_page_size = 100


class PostCommentListCreateAPIView(generics.ListCreateAPIView):  # type: ignore[type-arg]
    """댓글 목록 조회(GET) / 생성(POST)
    - 명세: /posts/{post_id}/comments/
    - GET: AllowAny + pagination(count/next/previous/results)
    - POST: IsAuthenticated + {detail: "..."}
    """

    pagination_class = PostCommentPagination
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def _get_post(self) -> Post:
        post_id = self.kwargs.get("post_id")
        try:
            return Post.objects.get(pk=post_id, is_visible=True)
        except Post.DoesNotExist as e:
            raise NotFound(detail="해당 게시글을 찾을 수 없습니다.") from e

    def get_queryset(self):
        post = self._get_post()
        return (
            PostComment.objects.filter(post=post)
            .select_related("author")
            .prefetch_related("tags__tagged_user")
            .order_by("created_at")
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PostCommentListSerializer
        return PostCommentCreateSerializer

    def get_serializer_context(self) -> dict[str, Any]:
        ctx = super().get_serializer_context()
        if self.request.method == "POST":
            ctx["post"] = self._get_post()
        return ctx

    def perform_create(self, serializer: PostCommentCreateSerializer) -> None:
        # DB에 실제 생성
        post = self._get_post()
        serializer.save(author=self.request.user, post=post)

    @extend_schema(
        operation_id="v1_post_comments_list",
        tags=["Comments"],
        summary="커뮤니티 게시글 댓글 목록 조회 API",
        responses={
            200: inline_serializer(
                name="PostCommentListPaginatedResponse",
                fields={
                    "count": serializers.IntegerField(),
                    "next": serializers.CharField(allow_null=True),
                    "previous": serializers.CharField(allow_null=True),
                    "results": PostCommentListSerializer(many=True),
                },
            ),
            404: inline_serializer(
                name="PostCommentList404",
                fields={"error_detail": serializers.CharField()},
            ),
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # *args/**kwargs 꼭 필요: post_id 들어와도 TypeError 안 나게
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Comments"],
        summary="커뮤니티 게시글 댓글 작성 API",
        request=PostCommentCreateSerializer,
        responses={
            201: inline_serializer(name="PostCommentCreate201", fields={"detail": serializers.CharField()}),
            400: inline_serializer(name="PostCommentCreate400", fields={"error_detail": serializers.DictField()}),
            401: inline_serializer(name="PostCommentCreate401", fields={"error_detail": serializers.CharField()}),
            404: inline_serializer(name="PostCommentCreate404", fields={"error_detail": serializers.CharField()}),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        super().post(request, *args, **kwargs)
        return Response({"detail": "댓글이 등록되었습니다."}, status=status.HTTP_201_CREATED)


class PostCommentRetrieveUpdateDestroyAPIView(APIView):
    """댓글 상세 조회 / 수정 / 삭제 (mock 응답 유지)
    - 명세: /posts/{post_id}/comments/{comment_id}/
    """

    serializer_class = PostCommentUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    def _get_comment(self) -> PostComment:
        post_id = int(self.kwargs["post_id"])
        comment_id = int(self.kwargs["comment_id"])

        if comment_id <= 0:
            raise NotFound(detail="해당 댓글을 찾을 수 없습니다.")

        try:
            return (
                PostComment.objects.select_related("author")
                .prefetch_related("tags__tagged_user")
                .get(pk=comment_id, post_id=post_id)
            )
        except PostComment.DoesNotExist as e:
            raise NotFound(detail="해당 댓글을 찾을 수 없습니다.") from e

    @extend_schema(tags=["Comments"], summary="댓글 상세 조회 API")
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        comment = self._get_comment()
        return Response(PostCommentListSerializer(comment).data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Comments"],
        summary="댓글 수정 API",
        responses={
            200: inline_serializer(
                name="PostCommentUpdateResponse",
                fields={
                    "id": serializers.IntegerField(),
                    "content": serializers.CharField(),
                    "updated_at": serializers.DateTimeField(),
                },
            ),
            400: inline_serializer(name="PostCommentUpdate400", fields={"error_detail": serializers.DictField()}),
            401: inline_serializer(name="PostCommentUpdate401", fields={"error_detail": serializers.CharField()}),
            403: inline_serializer(name="PostCommentUpdate403", fields={"error_detail": serializers.CharField()}),
            404: inline_serializer(name="PostCommentUpdate404", fields={"error_detail": serializers.CharField()}),
        },
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        comment = self._get_comment()
        if comment.author_id != request.user.id:
            raise PermissionDenied()

        # validate는 기존 serializer 로직 재사용
        mock_comment = type("Comment", (), {})()
        mock_comment.id = comment.id
        mock_comment.content = comment.content
        mock_comment.author = comment.author

        serializer = self.serializer_class(instance=mock_comment, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        return Response(
            {"id": comment.id, "content": serializer.validated_data["content"], "updated_at": timezone.now()},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Comments"],
        summary="댓글 삭제 API",
        responses={
            200: inline_serializer(name="PostCommentDelete200", fields={"detail": serializers.CharField()}),
            401: inline_serializer(name="PostCommentDelete401", fields={"error_detail": serializers.CharField()}),
            403: inline_serializer(name="PostCommentDelete403", fields={"error_detail": serializers.CharField()}),
            404: inline_serializer(name="PostCommentDelete404", fields={"error_detail": serializers.CharField()}),
        },
    )
    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        comment = self._get_comment()
        if comment.author_id != request.user.id:
            raise PermissionDenied()
        return Response({"detail": "댓글이 삭제되었습니다."}, status=status.HTTP_200_OK)
