from django.db import models

from apps.core.models import TimeStampModel


class ExamDeployment(TimeStampModel):
    class StatusChoices(models.TextChoices):
        ACTIVATED = "ACTIVATED", "시험 응시 가능"
        DEACTIVATED = "DEACTIVATED", "시험 비활성화"

    cohort = models.ForeignKey(
        "courses.Cohort", on_delete=models.CASCADE, related_name="exam_deployments", verbose_name="기수"
    )
    exam = models.ForeignKey("exams.Exam", on_delete=models.CASCADE, related_name="deployments", verbose_name="시험")

    duration_time = models.PositiveSmallIntegerField(null=False, verbose_name="제한 시간(분)")
    access_code = models.CharField(max_length=64, null=False, verbose_name="접근 코드")
    open_at = models.DateTimeField(null=False, verbose_name="오픈 일시")
    close_at = models.DateTimeField(null=False, verbose_name="마감 일시")
    questions_snapshot_json = models.JSONField(null=False, verbose_name="문항 스냅샷(JSON)")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DEACTIVATED,
        verbose_name="상태",
    )

    def __str__(self) -> str:
        return f"{self.exam.title} - {self.cohort.number}기"

    class Meta:
        db_table = "exam_deployments"
        verbose_name = "시험 배포"
        verbose_name_plural = "시험 배포 목록"
