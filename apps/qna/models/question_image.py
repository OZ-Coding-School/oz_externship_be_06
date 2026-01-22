from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampModel
from apps.qna.models.question import Question


class QuestionImage(TimeStampModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="images", verbose_name="질문")
    img_url = models.CharField(max_length=255, verbose_name="이미지 URL")

    class Meta:
        db_table = "question_image"
        verbose_name = "질문 이미지"
        verbose_name_plural = "질문 이미지 목록"

    def __str__(self) -> str:
        return f"{self.question.pk}번 질문의 이미지"
