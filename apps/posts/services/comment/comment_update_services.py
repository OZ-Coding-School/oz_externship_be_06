from typing import Any

from django.db import transaction

from apps.posts.exceptions.comment_exceptions import CommentForbiddenException
from apps.posts.models.post_comment import PostComment


def update_comment(user: Any, comment: PostComment, content: str) -> PostComment:
    # 댓글을 수정하는 함수입니다. 작성자만 수정할 수 있습니다.
    if comment.author != user:
        raise CommentForbiddenException()
    comment.content = content
    comment.save(update_fields=["content", "updated_at"])
    return comment
