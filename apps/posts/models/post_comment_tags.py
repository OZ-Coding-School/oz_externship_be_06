# mypy: ignore-errors

from django.db import models
from django.conf import settings
from apps.core.models import TimeStampModel

class PostCommentTag(TimeStampModel):
    """
    ERD의 post_comment_tags 테이블: 댓글 내에서 언급(태그)된 사용자를 관리합니다.
    """

    tagged_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comment_tags",
        verbose_name="태그된 사용자"
    )

    comment = models.ForeignKey(
        "posts.PostComment",
        on_delete=models.CASCADE,
        related_name="tags",
        verbose_name="댓글"
    )

    class Meta:
        db_table = "post_comment_tags"
        verbose_name = "댓글 태그"
        verbose_name_plural = "댓글 태그 목록"

    def __str__(self):
        return f"{self.comment_id}번 댓글 - {self.tagged_user.nickname} 태그"