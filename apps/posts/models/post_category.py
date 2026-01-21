from django.conf import settings
from django.db import models

from apps.core.models import TimeStampModel


class PostCategory(TimeStampModel):
    """
    ERD의 post_category 테이블: 게시글의 카테고리를 관리합니다.
    """

    name = models.CharField(max_length=20, null=False, verbose_name="카테고리명")
    status = models.BooleanField(default=True, verbose_name="활성 상태")

    class Meta:
        db_table = "post_category"
        verbose_name = "게시글 카테고리"
        verbose_name_plural = "게시글 카테고리 목록"

    def __str__(self) -> str:
        return self.name
