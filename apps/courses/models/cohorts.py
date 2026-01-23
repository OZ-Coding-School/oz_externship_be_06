from django.db import models

from apps.core.models import TimeStampModel


class Cohort(TimeStampModel):
    class StatusChoices(models.TextChoices):
        PREPARING = "PREPARING", "모집중"
        IN_PROGRESS = "IN_PROGRESS", "진행중"
        FINISHED = "FINISHED", "종료"

    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="cohorts", verbose_name="강좌")

    number = models.PositiveSmallIntegerField(verbose_name="기수", null=False)
    max_student = models.PositiveSmallIntegerField(verbose_name="최대 학생 수", null=False)
    start_date = models.DateField(verbose_name="시작일", null=False)
    end_date = models.DateField(verbose_name="종료일", null=False)

    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.PREPARING, verbose_name="상태"
    )

    def __str__(self) -> str:
        return f"{self.course.name} - {self.number}기"

    class Meta:
        db_table = "course_cohorts"
        verbose_name = "기수"
        verbose_name_plural = "기수 목록"
