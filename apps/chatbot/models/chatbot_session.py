from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampModel


class ChatbotSession(TimeStampModel):
    class AIModel(models.TextChoices):
        GEMINI = "Gemini", "Gemini"
        GPT = "GPT", "GPT"

    class SessionStatus(models.TextChoices):
        IDLE = "IDLE", "질문 대기 중"
        RESPONDING = "RESPONDING", "답변 생성 중"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chatbot_sessions", verbose_name="사용자 ID"
    )
    question = models.ForeignKey(
        "qna.Question", blank=True, on_delete=models.CASCADE, related_name="chatbot_sessions", verbose_name="질문 ID"
    )
    title = models.CharField(max_length=30, verbose_name="세션 제목")
    using_model = models.CharField(
        max_length=20,
        choices=AIModel.choices,
        default=AIModel.GEMINI,
        verbose_name="사용 모델",
    )

    class Meta:
        db_table = "chatbot_session"
        verbose_name = "챗봇 세션"
        verbose_name_plural = "챗봇 세션 목록"

        constraints = [models.UniqueConstraint(fields=["user", "question"], name="unique_user_question_session")]

    def __str__(self) -> str:
        return f"[{self.pk}] {self.title} ({self.get_using_model_display()})"
