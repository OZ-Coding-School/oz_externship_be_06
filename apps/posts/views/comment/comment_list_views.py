from typing import Any, Type

from django.db.models import QuerySet
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
)
from rest_framework import generics, parsers, serializers
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


class PostCommentListAPIView(generics.ListAPIView[PostComment]):
    # 댓글 단일 상세 조회(GET)도 AllowAny가 아니라면, 인증 체크 및 커스텀 예외 적용 필요
    # 만약 상세 조회 API가 별도라면, 해당 view에도 동일하게 적용해야 함
    pagination_class = PostPagination
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]
    permission_classes = [AllowAny]

    def _get_post(self) -> Post:
        post_id = self.kwargs.get("post_id")
        try:
            return Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise CommentNotFoundException()

    def get_queryset(self) -> QuerySet[PostComment]:
        post_id = self.kwargs.get("post_id")
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
        try:
            return super().get(request, *args, **kwargs)
        except CommentNotFoundException as e:
            return Response({"error_detail": str(e.detail)}, status=404)
