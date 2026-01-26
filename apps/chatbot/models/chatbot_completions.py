from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampModel


class ChatbotCompletions(TimeStampModel):
    class Role(models.TextChoices):
        USER = "User", "사용자"
        ASSISTANT = "Assistant", "AI챗봇"

    session = models.ForeignKey(
        "chatbot.ChatbotSession", on_delete=models.CASCADE, related_name="chatbot_completions", verbose_name="세션 ID"
    )
    content = models.TextField(verbose_name="메시지 내용")  # ERD상 Message 필드
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        verbose_name="발화주체",
    )

    class Meta:
        db_table = "chatbot_completion"
        verbose_name = "챗봇 메세지"
        verbose_name_plural = "챗봇 메시지 목록"

    def __str__(self) -> str:
        return f"[{self.session.pk}] {self.get_role_display()}: {self.content[:20]}..."
