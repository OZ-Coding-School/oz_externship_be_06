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
        "qna.Question", on_delete=models.CASCADE, related_name="chatbot_sessions", verbose_name="질문 ID"
    )
    title = models.CharField(max_length=30, verbose_name="세션 제목")
    using_model = models.CharField(
        max_length=20,
        choices=AIModel.choices,
        default=AIModel.GEMINI,
        verbose_name="사용 모델",
    )
    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.IDLE,
        verbose_name="세션 상태",
        help_text="AI가 답변 중일 때는 추가 질문을 막기 위한 상태 필드",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="활성화 여부",
        help_text="사용자가 'x'를 누르거나 새로고침하여 세션이 종료되면 False로 변경됩니다.",
    )

    class Meta:
        db_table = "chatbot_session"
        verbose_name = "챗봇 세션"
        verbose_name_plural = "챗봇 세션 목록"

    def __str__(self) -> str:
        return f"[{self.pk}] {self.title} ({self.get_using_model_display()})"
