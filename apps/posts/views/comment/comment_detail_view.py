from typing import Any

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import parsers, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.exceptions.comment_exceptions import (
    CommentForbiddenException,
    CommentNotFoundException,
)
from apps.posts.models.post_comment import PostComment
from apps.posts.permissions.comment_permissions import IsCommentAuthorOrReadOnly
from apps.posts.selectors.comment_selectors import CommentSelector
from apps.posts.serializers.comment_serializers import (
    PostCommentListSerializer,
    PostCommentUpdateSerializer,
)
from apps.posts.services.comment.comment_delete_services import delete_comment
from apps.posts.services.comment.comment_update_services import update_comment


class PostCommentDetailAPIView(APIView):

    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    def get_permissions(self) -> list[Any]:
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def _get_comment(self, post_id: int, comment_id: int) -> PostComment:
        """댓글 조회 및 게시글 일치 여부 확인"""
        comment = CommentSelector.get_comment_by_id(comment_id)
        if comment.post_id != post_id:
            raise CommentNotFoundException()
        return comment

    @extend_schema(
        tags=["posts"],
        summary="커뮤니티 게시글 댓글 상세 조회 API",
        responses={
            200: PostCommentListSerializer,
            404: inline_serializer(
                name="PostCommentDetail404",
                fields={"error_detail": serializers.CharField()},
            ),
        },
    )
    def get(self, request: Request, post_id: int, comment_id: int) -> Response:

        try:
            comment = self._get_comment(post_id, comment_id)
        except CommentNotFoundException:
            return Response(
                {"error_detail": "해당 댓글을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PostCommentListSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["posts"],
        summary="커뮤니티 게시글 댓글 수정 API",
        request=PostCommentUpdateSerializer,
        responses={
            200: inline_serializer(
                name="PostCommentUpdateResponse",
                fields={
                    "id": serializers.IntegerField(),
                    "content": serializers.CharField(),
                    "updated_at": serializers.DateTimeField(),
                },
            ),
            400: inline_serializer(
                name="PostCommentUpdate400",
                fields={"error_detail": serializers.DictField()},
            ),
            401: inline_serializer(
                name="PostCommentUpdate401",
                fields={"error_detail": serializers.CharField()},
            ),
            403: inline_serializer(
                name="PostCommentUpdate403",
                fields={"error_detail": serializers.CharField()},
            ),
            404: inline_serializer(
                name="PostCommentUpdate404",
                fields={"error_detail": serializers.CharField()},
            ),
        },
    )
    def put(self, request: Request, post_id: int, comment_id: int) -> Response:

        try:
            comment = self._get_comment(post_id, comment_id)
        except CommentNotFoundException:
            return Response(
                {"error_detail": "해당 댓글을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 권한 체크: 작성자만 수정 가능
        if comment.author_id != request.user.id:
            return Response(
                {"error_detail": "권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PostCommentUpdateSerializer(
            instance=comment,
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_comment = update_comment(request.user, comment, serializer.validated_data["content"])

        return Response(
            {
                "id": updated_comment.id,
                "content": updated_comment.content,
                "updated_at": updated_comment.updated_at,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["posts"],
        summary="커뮤니티 게시글 댓글 삭제 API",
        responses={
            200: inline_serializer(
                name="PostCommentDelete200",
                fields={"detail": serializers.CharField()},
            ),
            401: inline_serializer(
                name="PostCommentDelete401",
                fields={"error_detail": serializers.CharField()},
            ),
            403: inline_serializer(
                name="PostCommentDelete403",
                fields={"error_detail": serializers.CharField()},
            ),
            404: inline_serializer(
                name="PostCommentDelete404",
                fields={"error_detail": serializers.CharField()},
            ),
        },
    )
    def delete(self, request: Request, post_id: int, comment_id: int) -> Response:
        try:
            comment = self._get_comment(post_id, comment_id)
        except CommentNotFoundException:
            return Response(
                {"error_detail": "해당 댓글을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 권한 체크: 작성자만 삭제 가능
        if comment.author_id != request.user.id:
            return Response(
                {"error_detail": "권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        delete_comment(request.user, comment)

        return Response(
            {"detail": "댓글이 삭제되었습니다."},
            status=status.HTTP_200_OK,
        )
