from typing import Any

from django.db import transaction

from apps.posts.exceptions.comment_exceptions import CommentForbiddenException
from apps.posts.models.post_comment import PostComment


@transaction.atomic
def delete_comment(user: Any, comment: PostComment) -> None:
    """
    댓글 삭제 (작성자만 가능)

    @transaction.atomic:
    - 댓글 삭제와 관련된 모든 DB 작업을 하나의 트랜잭션으로 묶음
    - 에러 발생 시 자동 롤백하여 데이터 일관성 보장
    - 향후 연관된 태그, 알림 등의 삭제 작업 추가 시에도 안전성 유지
    """
    if comment.author != user:
        raise CommentForbiddenException()
    comment.delete()
