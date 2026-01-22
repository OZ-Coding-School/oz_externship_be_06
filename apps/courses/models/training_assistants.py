from django.conf import settings
from django.db import models

from apps.core.models import TimeStampModel


# 조교
class TrainingAssistant(TimeStampModel):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assisted_cohorts")
    cohort = models.ForeignKey("courses.Cohort", on_delete=models.CASCADE, related_name="training_assistants")

    class Meta:
        db_table = "training_assistants"
        verbose_name = "조교"
        verbose_name_plural = "조교 목록"

    def __str__(self) -> str:
        return f"{self.user.name} - {self.cohort}"
