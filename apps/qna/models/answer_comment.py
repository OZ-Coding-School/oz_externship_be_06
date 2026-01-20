from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampModel
from apps.users.models import User

from .answer import Answer


class AnswerComment(TimeStampModel):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="comments", verbose_name="답변")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answer_comments", verbose_name="작성자")
    content = models.TextField(verbose_name="댓글 내용")

    class Meta:
        db_table = "answer_comments"
        verbose_name = "질문 답변 댓글"
        verbose_name_plural = "질문 답변 댓글 목록"

    def __str__(self) -> str:
        return f"{self.author.nickname}님의 댓글: {self.content[:20]}"
