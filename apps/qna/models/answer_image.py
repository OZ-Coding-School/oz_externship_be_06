from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampModel
from apps.qna.models.answer import Answer


class AnswerImage(TimeStampModel):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="images", verbose_name="답변")
    img_url = models.CharField(max_length=255, verbose_name="이미지 URL")

    class Meta:
        db_table = "answer_image"
        verbose_name = "질문 답변 이미지"
        verbose_name_plural = "질문 답변 이미지 목록"

    def __str__(self) -> str:
        return f"{self.answer.id}번 답변의 이미지"
