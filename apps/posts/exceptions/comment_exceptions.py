from rest_framework.exceptions import NotAuthenticated, NotFound, PermissionDenied

from apps.posts.constants.comment_const import CommentErrorMessage


class CommentNotFoundException(NotFound):
    """
    댓글이 존재하지 않을 때 발생하는 예외
    """

    default_detail = CommentErrorMessage.COMMENT_NOT_FOUND


class CommentUnauthorizedException(NotAuthenticated):
    """
    댓글 인증(로그인) 필요시 발생하는 예외
    """

    default_detail = CommentErrorMessage.UNAUTHORIZED


class CommentForbiddenException(PermissionDenied):
    """
    댓글에 대한 권한이 없을 때 발생하는 예외
    """

    default_detail = CommentErrorMessage.FORBIDDEN
