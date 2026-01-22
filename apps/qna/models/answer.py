from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampModel
from apps.users.models import User

from apps.qna.models.question import Question


class Answer(TimeStampModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers", verbose_name="질문")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers", verbose_name="작성자")
    content = models.TextField(verbose_name="답변 내용")
    is_adopted = models.BooleanField(default=False, verbose_name="채택 여부")

    class Meta:
        db_table = "answer"
        verbose_name = "질문 답변"
        verbose_name_plural = "질문 답변 목록"

    def __str__(self) -> str:
        return f"[{self.question.title}]에 대한 {self.author.nickname}님의 답변"
