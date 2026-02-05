from typing import Any

from apps.posts.exceptions.comment_exceptions import CommentForbiddenException
from apps.posts.models.post_comment import PostComment


def delete_comment(user: Any, comment: PostComment) -> None:
    # 댓글을 삭제하는 함수입니다. 작성자만 삭제할 수 있습니다.
    if comment.author != user:
        raise CommentForbiddenException()
    comment.delete()
