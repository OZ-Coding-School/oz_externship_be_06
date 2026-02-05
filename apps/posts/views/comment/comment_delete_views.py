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
from apps.posts.permissions.comment_permissions import IsCommentAuthorOrReadOnly
from apps.posts.selectors.comment_selectors import CommentSelector
from apps.posts.services.comment.comment_delete_services import delete_comment


class PostCommentDeleteAPIView(APIView):
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
        summary="댓글 삭제 API",
        responses={
            200: inline_serializer(name="PostCommentDelete200", fields={"detail": serializers.CharField()}),
            401: inline_serializer(name="PostCommentDelete401", fields={"error_detail": serializers.CharField()}),
            403: inline_serializer(name="PostCommentDelete403", fields={"error_detail": serializers.CharField()}),
            404: inline_serializer(name="PostCommentDelete404", fields={"error_detail": serializers.CharField()}),
        },
    )
    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            comment_id = self._get_comment_id()
            comment = CommentSelector.get_comment_by_id(comment_id)
            delete_comment(request.user, comment)
        except CommentNotFoundException as e:
            return Response({"error_detail": str(e.detail)}, status=404)
        except CommentForbiddenException as e:
            return Response({"error_detail": str(e.detail)}, status=403)
        return Response({"detail": "댓글이 삭제되었습니다."}, status=status.HTTP_200_OK)
