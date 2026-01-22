from django.conf import settings
from django.db import models

from .cohorts import Cohort
from ...core.models import TimeStampModel


class CohortStudent(TimeStampModel):
    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cohort_students",
        db_column="user_id",
    )

    cohort = models.ForeignKey(
        Cohort,
        on_delete=models.CASCADE,
        related_name="cohort_students",
        db_column="cohort_id",
    )

    class Meta:
        db_table = "cohort_students"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["cohort"]),
        ]
        verbose_name = "코호트 수강생"
        verbose_name_plural = "코호트 수강생들"
