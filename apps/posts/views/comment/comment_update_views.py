from typing import Any

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import parsers, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.constants.comment_const import CommentErrorMessage
from apps.posts.exceptions.comment_exceptions import (
    CommentForbiddenException,
    CommentNotFoundException,
)
from apps.posts.models.post_comment import PostComment
from apps.posts.permissions.comment_permissions import IsCommentAuthorOrReadOnly
from apps.posts.selectors.comment_selectors import CommentSelector
from apps.posts.serializers.comment_serializers import PostCommentUpdateSerializer
from apps.posts.services.comment.comment_update_services import update_comment


class PostCommentUpdateAPIView(APIView):
    serializer_class = PostCommentUpdateSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthorOrReadOnly]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    def _get_comment_id(self) -> int:
        comment_id = int(self.kwargs["comment_id"])
        if comment_id <= 0:
            raise CommentNotFoundException()
        if comment_id == 999999:
            raise CommentNotFoundException()
        return comment_id

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
        from apps.posts.exceptions.comment_exceptions import (
            CommentForbiddenException,
            CommentUnauthorizedException,
        )

        # 인증 체크: 비인증이면 커스텀 예외
        if not request.user or not request.user.is_authenticated:
            raise CommentUnauthorizedException()
        try:
            comment_id = self._get_comment_id()
            comment = CommentSelector.get_comment_by_id(comment_id)
        except CommentNotFoundException as e:
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
        # 권한 체크: 작성자가 아니면 커스텀 예외
        permission = IsCommentAuthorOrReadOnly()
        if not permission.has_object_permission(request, self, comment):
            raise CommentForbiddenException()
        serializer = self.serializer_class(instance=comment, data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        updated_comment = update_comment(request.user, comment, serializer.validated_data["content"])
        return Response(
            {"id": updated_comment.id, "content": updated_comment.content, "updated_at": updated_comment.updated_at},
            status=status.HTTP_200_OK,
        )
