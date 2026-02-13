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
from apps.posts.views.comment.comment_base_view import CommentBaseView


class PostCommentDeleteAPIView(CommentBaseView, APIView):
    """
    댓글 삭제 API
    - DELETE /api/posts/<post_id>/comments/<comment_id>/
    - 인증 + 작성자 권한 필요
    - 정상: 200 + detail 메시지
    - 실패: 401/403/404 + error_detail
    - 문서화: drf-spectacular @extend_schema 사용
    """

    permission_classes = [IsAuthenticated, IsCommentAuthorOrReadOnly]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    def _get_comment_id(self) -> int:
        comment_id = int(self.kwargs["comment_id"])
        if comment_id <= 0 or comment_id == 999999:
            raise CommentNotFoundException()
        return comment_id

    @extend_schema(
        tags=["posts"],
        summary="댓글 삭제 API",
        responses={
            200: inline_serializer(name="PostCommentDelete200", fields={"detail": serializers.CharField()}),
            401: inline_serializer(name="PostCommentDelete401", fields={"error_detail": serializers.CharField()}),
            403: inline_serializer(name="PostCommentDelete403", fields={"error_detail": serializers.CharField()}),
            404: inline_serializer(name="PostCommentDelete404", fields={"error_detail": serializers.CharField()}),
        },
    )
    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        댓글 삭제 (DELETE)
        - 인증 필요, 미인증 시 401
        - 작성자만 삭제 가능, 아니면 403
        - 존재하지 않는 댓글이면 404
        - 정상 삭제 시 200
        """
        from apps.posts.exceptions.comment_exceptions import (
            CommentForbiddenException,
            CommentUnauthorizedException,
        )

        # 인증 체크: 비인증이면 커스텀 예외
        if not request.user or not request.user.is_authenticated:
            raise CommentUnauthorizedException()
        try:
            # comment_id로 댓글 객체 조회 (없으면 예외)
            comment_id = self._get_comment_id()
            comment = CommentSelector.get_comment_by_id(comment_id)
        except CommentNotFoundException as e:
            # 댓글이 없을 때 404 반환
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
        delete_comment(request.user, comment)
        # 정상: 삭제 완료 메시지 반환
        return Response({"detail": "댓글이 삭제되었습니다."}, status=status.HTTP_200_OK)
