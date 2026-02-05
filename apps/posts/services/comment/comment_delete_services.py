from typing import Any

from apps.posts.exceptions.comment_exceptions import CommentForbiddenException
from apps.posts.models.post_comment import PostComment


def delete_comment(user: Any, comment: PostComment) -> None:
    """
    댓글 삭제 (작성자만 가능)
    """
    if comment.author != user:
        raise CommentForbiddenException()
    comment.delete()
