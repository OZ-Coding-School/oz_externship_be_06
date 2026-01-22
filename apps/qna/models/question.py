from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampModel
from apps.users.models import User

from apps.qna.models.question_category import QuestionCategory


class Question(TimeStampModel):
    category = models.ForeignKey(
        QuestionCategory, on_delete=models.PROTECT, related_name="questions", verbose_name="카테고리"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions", verbose_name="작성자")
    title = models.CharField(max_length=50, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    view_count = models.PositiveIntegerField(default=0, verbose_name="조회수")

    is_ai_answered = models.BooleanField(default=False, verbose_name="AI 답변 여부")
    is_staff_answered = models.BooleanField(default=False, verbose_name="운영진 답변 여부")

    class Meta:
        db_table = "question"
        verbose_name = "질문"
        verbose_name_plural = "질문 목록"

    def __str__(self) -> str:
        return f"[{self.pk}] {self.title}"
