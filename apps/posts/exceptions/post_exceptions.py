from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException

from apps.posts.constants.post_const import PostErrorMessage


class PostUnauthorizedException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = PostErrorMessage.UNAUTHORIZED
    default_code = "unauthorized"

    def __init__(self, detail: Any = None, code: Any = None) -> None:
        if detail is None:
            detail = self.default_detail

        self.detail = {"error_detail": detail}

class PostNotFoundException(APIException):
    """
    게시글을 찾을 수 없을 때 발생하는 예외
    """

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = PostErrorMessage.POST_NOT_FOUND
    default_code = 'post_not_found'

    def __init__(self, detail: Any = None, code: Any = None) -> None:
        if detail is None:
            detail = self.default_detail
        self.detail = {"error_detail": detail}