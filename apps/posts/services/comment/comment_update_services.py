from typing import Any

from django.db import transaction

from apps.posts.exceptions.comment_exceptions import CommentForbiddenException
from apps.posts.models.post_comment import PostComment


def update_comment(user: Any, comment: PostComment, content: str) -> PostComment:
    """
    댓글 수정 (작성자만 가능)
    """
    if comment.author != user:
        raise CommentForbiddenException()
    comment.content = content
    comment.save(update_fields=["content", "updated_at"])
    return comment
