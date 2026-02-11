from typing import Any, Type

from django.db.models import QuerySet
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
)
from rest_framework import parsers, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.exceptions.comment_exceptions import CommentNotFoundException
from apps.posts.exceptions.post_exceptions import PostNotFoundException
from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment
from apps.posts.selectors.comment_selectors import CommentSelector
from apps.posts.serializers.comment_serializers import (
    PostCommentCreateSerializer,
    PostCommentListSerializer,
)
from apps.posts.utils.pagination import PostPagination


class PostCommentListAPIView(APIView):

    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    def get_permissions(self) -> list[Any]:
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def _get_post(self) -> Post:
        post_id = self.kwargs.get("post_id")
        try:
            return Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise PostNotFoundException()

    @extend_schema(
        operation_id="v1_post_comments_list",
        tags=["posts"],
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
    def get(self, request: Request, post_id: int) -> Response:
        """댓글 목록 조회 (GET)"""
        try:
            queryset = CommentSelector.get_comments_for_post(post_id)
        except PostNotFoundException:
            return Response(
                {"error_detail": "해당 게시글을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        paginator = PostPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)

        if page is not None:
            serializer = PostCommentListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = PostCommentListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="v1_post_comments_create",
        tags=["posts"],
        summary="커뮤니티 게시글 댓글 작성 API",
        request=PostCommentCreateSerializer,
        responses={
            201: inline_serializer(
                name="PostCommentCreate201",
                fields={"detail": serializers.CharField()},
            ),
            400: inline_serializer(
                name="PostCommentCreate400",
                fields={"error_detail": serializers.DictField()},
            ),
            401: inline_serializer(
                name="PostCommentCreate401",
                fields={"error_detail": serializers.CharField()},
            ),
            404: inline_serializer(
                name="PostCommentCreate404",
                fields={"error_detail": serializers.CharField()},
            ),
        },
    )
    def post(self, request: Request, post_id: int) -> Response:
        try:
            post = self._get_post()
        except PostNotFoundException:
            return Response(
                {"error_detail": "해당 게시글을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PostCommentCreateSerializer(
            data=request.data,
            context={"request": request, "post": post},
        )

        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        return Response(
            {"detail": "댓글이 등록되었습니다."},
            status=status.HTTP_201_CREATED,
        )
