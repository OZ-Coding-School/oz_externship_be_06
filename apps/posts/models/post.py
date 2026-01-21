# mypy: ignore-errors

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampModel


class Post(TimeStampModel):
    """
    ERD의 post 테이블: 게시글의 본문 및 기본 정보를 담습니다.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts", null=False, verbose_name="작성자"
    )
    category = models.ForeignKey(
        "posts.PostCategory", on_delete=models.PROTECT, related_name="posts", null=False, verbose_name="카테고리"
    )
    title = models.CharField(max_length=50, null=False, verbose_name="제목")
    content = models.TextField(null=False, verbose_name="내용")
    view_count = models.IntegerField(default=0, null=False, verbose_name="조회수")
    is_visible = models.BooleanField(default=True, verbose_name="공개 여부")
    is_notice = models.BooleanField(default=False, verbose_name="공지사항 여부")

    class Meta:
        db_table = "post"
        verbose_name = "게시글"
        verbose_name_plural = "게시글 목록"

    def __str__(self) -> str:
        return f"[{self.id}] {self.title}"
