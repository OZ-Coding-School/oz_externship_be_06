from typing import Any, Type

from django.db.models import QuerySet
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
)
from rest_framework import generics, parsers, serializers, status
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.posts.constants.comment_const import CommentErrorMessage
from apps.posts.exceptions.comment_exceptions import CommentNotFoundException
from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment
from apps.posts.selectors.comment_selectors import CommentSelector
from apps.posts.serializers.comment_serializers import PostCommentListSerializer
from apps.posts.utils.pagination import PostPagination
from apps.posts.views.comment.comment_base_view import CommentBaseView


class PostCommentListAPIView(CommentBaseView, generics.ListAPIView[PostComment]):
    """
    댓글 목록 조회 API
    - GET /api/posts/<post_id>/comments/
    - 누구나 접근 가능 (AllowAny)
    - 정상: 200 + 댓글 목록 (pagination)
    - 실패: 404 + error_detail
    - 문서화: drf-spectacular @extend_schema 사용
    """

    pagination_class = PostPagination
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]
    permission_classes = [AllowAny]

    def _get_post(self) -> Post:
        post_id = self.kwargs.get("post_id")
        try:
            return Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            # 게시글이 없을 때 404 반환용 예외
            raise CommentNotFoundException()

    def get_queryset(self) -> QuerySet[PostComment]:
        post_id = self.kwargs.get("post_id")
        # 해당 게시글의 댓글 목록 반환
        return CommentSelector.get_comments_for_post(post_id)

    def get_serializer_class(self) -> Type[serializers.Serializer[PostComment]]:
        return PostCommentListSerializer

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
            404: inline_serializer(name="PostCommentList404", fields={"error_detail": serializers.CharField()}),
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        댓글 목록 조회 (GET)
        - 누구나 접근 가능
        - 게시글이 없으면 404
        - 정상 시 pagination된 댓글 목록 반환
        """
        try:
            return super().get(request, *args, **kwargs)
        except CommentNotFoundException as e:
            # 게시글이 없을 때 404 반환
            return Response(
                {
                    "error_detail": (
                        e.detail["error_detail"]
                        if isinstance(e.detail, dict) and "error_detail" in e.detail
                        else e.detail
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )
