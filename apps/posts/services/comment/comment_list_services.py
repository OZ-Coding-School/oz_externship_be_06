from django.db.models import QuerySet

from apps.posts.models.post_comment import PostComment


def list_comments(post_id: int) -> QuerySet[PostComment]:
    # 특정 게시글의 댓글 목록을 반환합니다. post_id(게시글 PK)를 기준으로 최신순 정렬합니다.
    return PostComment.objects.filter(post_id=post_id).order_by("-created_at")
