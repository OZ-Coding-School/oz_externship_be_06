# mypy: ignore-errors

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampModel


class PostComment(TimeStampModel):
    """
    ERD의 post_comment 테이블: 게시글에 달린 댓글을 관리합니다.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_comments", verbose_name="작성자"
    )
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="comments", verbose_name="게시글")
    content = models.CharField(max_length=300, null=False, verbose_name="내용")

    class Meta:
        db_table = "post_comment"
        verbose_name = "게시글 댓글"
        verbose_name_plural = "게시글 댓글 목록"

    def __str__(self) -> str:
        return f"{self.author.nickname}의 댓글: {self.content[:20]}"
