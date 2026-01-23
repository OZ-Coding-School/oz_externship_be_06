from django.db import models

from apps.core.models import TimeStampModel


class Subject(TimeStampModel):
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="courses", verbose_name="강좌")

    title = models.CharField(max_length=30, null=False, verbose_name="주제 타이틀")
    number_of_days = models.PositiveSmallIntegerField(verbose_name="일수", null=False)
    number_of_hours = models.PositiveSmallIntegerField(verbose_name="시간", null=False)
    thumbnail_img_url = models.CharField(max_length=255, null=True, blank=True, verbose_name="썸네일 URL")
    status = models.BooleanField(default=True, verbose_name="상태", null=False)

    def __str__(self) -> str:
        return self.title

    class Meta:
        db_table = "course_subjects"
        verbose_name = "과목"
        verbose_name_plural = "과목 목록"
