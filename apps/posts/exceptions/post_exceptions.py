from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException

from apps.posts.constants.post_const import PostErrorMessage


class PostUnauthorizedException(APIException):
    """
    사용자의 인증 정보가 유효하지 않거나 없는 경우 발생하는 예외입니다. (401 Unauthorized)
    """

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
    default_code = "post_not_found"

    def __init__(self, detail: Any = None, code: Any = None) -> None:
        if detail is None:
            detail = self.default_detail
        self.detail = {"error_detail": detail}


class PostPermissionDeniedException(APIException):
    """
    게시글 수정/삭제 권한이 없는 경우(작성자가 아닌 경우) 발생하는 예외 (403 Forbidden)
    """

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = PostErrorMessage.FORBIDDEN
    default_code = "post_permission_denied"

    def __init__(self, detail: Any = None, code: Any = None) -> None:
        if detail is None:
            detail = self.default_detail
        # 공통 에러 응답 규격인 error_detail 포맷을 유지합니다.
        self.detail = {"error_detail": detail}
