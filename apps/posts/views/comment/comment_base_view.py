from typing import Any

from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.exceptions.comment_exceptions import (
    CommentForbiddenException,
    CommentUnauthorizedException,
)


class CommentBaseView(APIView):
    """
    comment 관련 APIView에서 상속해서 인증/권한 예외를 error_detail 포맷으로 변환
    """

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            exc = CommentUnauthorizedException()
        elif isinstance(exc, PermissionDenied):
            exc = CommentForbiddenException()
        return super().handle_exception(exc)
