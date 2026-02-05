from django.db.models import QuerySet

from apps.posts.models.post_comment import PostComment


def list_comments(post_id: int) -> QuerySet[PostComment]:
    """
    특정 게시글의 댓글 목록 반환
    """
    return PostComment.objects.filter(post_id=post_id).order_by("-created_at")
