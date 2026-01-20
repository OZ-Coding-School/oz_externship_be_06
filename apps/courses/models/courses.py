from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=30, null=False, verbose_name="강좌명")
    tag = models.CharField(max_length=3, null=False, verbose_name="태그")
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name="설명")
    thumbnail_img_url = models.CharField(max_length=255, null=True, blank=True, verbose_name="썸네일 URL")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'courses'
        verbose_name = "강좌"
        verbose_name_plural = "강좌 목록"