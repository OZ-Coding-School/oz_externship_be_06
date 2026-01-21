# mypy: ignore-errors

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampModel


class PostLike(TimeStampModel):
    """
    ERD의 post_likes 테이블: 게시글에 대한 사용자의 좋아요 상태를 관리합니다.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_likes", verbose_name="사용자"
    )

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="likes", verbose_name="게시글")

    is_liked = models.BooleanField(default=True, verbose_name="좋아요 여부")

    class Meta:
        db_table = "post_likes"
        verbose_name = "게시글 좋아요"
        verbose_name_plural = "게시글 좋아요 목록"
        unique_together = ("user", "post")

    def __str__(self) -> str:
        status = "좋아요" if self.is_liked else "취소"
        return f"{self.user.nickname} - {self.post.title} ({status})"
