from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampModel

from apps.qna.models.question import Question


class QuestionAIAnswer(TimeStampModel):
    class AIModel(models.TextChoices):
        GEMINI = "Gemini", "Gemini"
        GPT = "GPT", "GPT"

    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name="ai_answer", verbose_name="질문")
    output = models.TextField(verbose_name="AI 답변 본문")
    using_model = models.CharField(
        max_length=20, choices=AIModel.choices, default=AIModel.GEMINI, verbose_name="사용된 AI 모델"
    )

    class Meta:
        db_table = "question_ai_answer"
        verbose_name = "질문 AI 답변"
        verbose_name_plural = "질문 AI 답변 목록"

    def __str__(self) -> str:
        return f"{self.question.id}번 질문에 대한 AI 답변 ({self.using_model})"
