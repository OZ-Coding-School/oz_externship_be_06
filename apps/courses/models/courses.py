from django.db import models

from apps.core.models import TimeStampModel


class Course(TimeStampModel):
    name = models.CharField(max_length=30, null=False, verbose_name="강좌명")
    tag = models.CharField(max_length=3, null=False, verbose_name="태그")
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name="설명")
    thumbnail_img_url = models.CharField(max_length=255, null=True, blank=True, verbose_name="썸네일 URL")

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = "courses"
        verbose_name = "강좌"
        verbose_name_plural = "강좌 목록"
