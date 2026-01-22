from django.db import models


class Exam(models.Model):
    title = models.CharField(max_length=50, null=False, verbose_name="시험 제목")
    thumbnail_img_url = models.CharField(max_length=255, null=False, verbose_name="썸네일 URL")
    subject = models.ForeignKey(
        "courses.Subject",
        on_delete=models.CASCADE,
        related_name="exams",
        verbose_name="과목",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    def __str__(self) -> str:
        return self.title

    class Meta:
        db_table = "exams"
        verbose_name = "시험"
        verbose_name_plural = "시험 목록"
