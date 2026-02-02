from typing import Any

from rest_framework.exceptions import APIException
from rest_framework import status
from apps.posts.constants.post_const import PostErrorMessage

class PostUnauthorizedException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = PostErrorMessage.UNAUTHORIZED
    default_code = 'unauthorized'

    def __init__(self, detail: Any = None, code: Any = None) -> None:
        if detail is None:
            detail = self.default_detail

        self.detail = {"error_detail": detail}