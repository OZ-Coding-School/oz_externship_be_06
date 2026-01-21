# mypy: ignore-errors

from django.db import models

from apps.core.models import TimeStampModel


class PostAttachment(TimeStampModel):
    """
    ERD의 post_attachments 테이블: 게시글에 첨부된 일반 파일들을 관리합니다.
    """

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="attachments", verbose_name="게시글")
    file_url = models.CharField(max_length=255, null=False, verbose_name="파일 URL")
    file_name = models.CharField(max_length=50, null=False, verbose_name="파일명")

    class Meta:
        db_table = "post_attachments"
        verbose_name = "게시글 첨부파일"
        verbose_name_plural = "게시글 첨부파일 목록"
