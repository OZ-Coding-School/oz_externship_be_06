from typing import TYPE_CHECKING, cast

from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response

if TYPE_CHECKING:
    from rest_framework.response import Response

from apps.posts.exceptions.comment_exceptions import (
    CommentForbiddenException,
    CommentUnauthorizedException,
)


class CommentExceptionHandlerMixin:
    """
    [Mixin] 댓글 관련 View에서 발생하는 인증/권한 예외를 커스텀으로 반환
    - APIView를 상속받지 않습니다.
    - 필요한 View 클래스에 첫 인자로 추가해서 사용합니다.
    """

    def handle_exception(self, exc: Exception) -> Response:
        # 1. 인증 예외 반환 (401)
        if isinstance(exc, NotAuthenticated):
            exc = CommentForbiddenException()

        # 2. 권한 예외 반환 (403)
        elif isinstance(exc, PermissionDenied):
            exc = CommentUnauthorizedException()

        # 3. 부모 (APIView)의 handel_exception 호출
        return cast("Response", super().handle_exception(exc))  # type: ignore[misc]
