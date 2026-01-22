from django.conf import settings
from django.db import models

from apps.core.models import TimeStampModel


#운매
class OperationManager(TimeStampModel):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="managed_courses")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="operation_managers")

    class Meta:
        db_table = "operation_managers"
        verbose_name = "운영매니저"
        verbose_name_plural = "운영매니저 목록"

    def __str__(self) -> str:
        return f"{self.user.name} - {self.course.name}"
