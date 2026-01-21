# mypy: ignore-errors

from django.db import models
from apps.core.models import TimeStampModel

class PostImage(TimeStampModel):
    """
    ERD의 post_images 테이블: 게시글에 첨부된 이미지들을 관리합니다.
    """

    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="게시글"
    )
    img_url = models.TextField(null=False, verbose_name="이미지 URL")

    class Meta:
        db_table = "post_images"
        verbose_name = "게시글 이미지"
        verbose_name_plural = "게시글 이미지 목록"