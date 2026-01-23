from typing import Any

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.chatbot.models.chatbot_session import ChatbotSession


@transaction.atomic
def create_chatbot_session(
    *,
    user: Any,  # ← 여기 핵심
    question_id: int,
    title: str | None = None,
    using_model: str | None = None,
) -> ChatbotSession:
    try:
        return ChatbotSession.objects.create(
            user=user,
            question_id=question_id,
            title=title or "새 채팅",
            using_model=using_model or "GPT",
        )
    except IntegrityError as exc:
        raise ValidationError("이미 해당 질문에 대한 세션이 존재합니다.") from exc
