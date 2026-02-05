from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException

from apps.posts.constants.comment_const import CommentErrorMessage


class CommentUnauthorizedException(APIException):
    """
    댓글 인증(로그인) 필요시 발생하는 예외 (401 Unauthorized)
    """

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = CommentErrorMessage.UNAUTHORIZED
    default_code = "unauthorized"

    def __init__(self, detail: Any = None, code: Any = None) -> None:
        if detail is None:
            detail = self.default_detail
        self.detail = {"error_detail": detail}


class CommentNotFoundException(APIException):
    """
    댓글이 존재하지 않을 때 발생하는 예외 (404 Not Found)
    """

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = CommentErrorMessage.COMMENT_NOT_FOUND
    default_code = "comment_not_found"

    def __init__(self, detail: Any = None, code: Any = None) -> None:
        if detail is None:
            detail = self.default_detail
        self.detail = {"error_detail": detail}


class CommentForbiddenException(APIException):
    """
    댓글에 대한 권한이 없을 때 발생하는 예외 (403 Forbidden)
    """

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = CommentErrorMessage.FORBIDDEN
    default_code = "comment_permission_denied"

    def __init__(self, detail: Any = None, code: Any = None) -> None:
        if detail is None:
            detail = self.default_detail
        self.detail = {"error_detail": detail}
