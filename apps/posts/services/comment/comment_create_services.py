from typing import Any

from django.db import transaction

from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment


@transaction.atomic
def create_comment(author: Any, post: Post, content: str) -> PostComment:
    """
    댓글 생성

    @transaction.atomic:
    - 댓글 생성과 관련된 모든 DB 작업을 하나의 트랜잭션으로 묶음
    - 에러 발생 시 자동 롤백하여 데이터 일관성 보장
    - 향후 알림, 통계 업데이트 등 추가 작업 시에도 안전성 유지
    """
    return PostComment.objects.create(author=author, post=post, content=content)
