from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampModel


class StudentEnrollmentRequest(TimeStampModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "대기"
        APPROVED = "APPROVED", "승인"
        REJECTED = "REJECTED", "거절"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollment_requests",
    )
    cohort = models.ForeignKey(
        "courses.Cohort",
        on_delete=models.CASCADE,
        related_name="enrollment_requests",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "student_enrollment_requests"

    def __str__(self) -> str:
        return f"{self.user} - {self.cohort} ({self.get_status_display()})"
