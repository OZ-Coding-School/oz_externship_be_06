from typing import Any

from django.db import transaction

from apps.posts.exceptions.comment_exceptions import CommentForbiddenException
from apps.posts.models.post_comment import PostComment


@transaction.atomic
def update_comment(user: Any, comment: PostComment, content: str) -> PostComment:
    """
    댓글 수정 (작성자만 가능)

    @transaction.atomic:
    - 댓글 수정과 관련된 모든 DB 작업을 하나의 트랜잭션으로 묶음
    - 에러 발생 시 자동 롤백하여 데이터 일관성 보장
    """
    if comment.author != user:
        raise CommentForbiddenException()
    comment.content = content
    comment.save(update_fields=["content", "updated_at"])
    return comment
