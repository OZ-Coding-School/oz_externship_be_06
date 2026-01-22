from django.conf import settings
from django.db import models

from apps.core.models import TimeStampModel


#러닝코치
class LearningCoach(TimeStampModel):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coached_courses")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="learning_coachs")

    class Meta:
        db_table = "learning_coachs"
        verbose_name = "러닝코치"
        verbose_name_plural = "러닝코치 목록"

    def __str__(self) -> str:
        return f"{self.user.name} - {self.course.name}"
