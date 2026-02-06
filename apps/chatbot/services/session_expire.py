from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.services.completion_clear import clear_completions
from apps.users.models import User


def expire_if_needed(*, user: User, session: ChatbotSession) -> bool:
    # 최신 세션 상태 기준으로 만료 여부 판단
    session.refresh_from_db(fields=["updated_at", "question"])

    # support 세션은 만료 정책 대상이 아님
    if session.question is None:
        return False

    deadline = session.updated_at + timedelta(
        hours=settings.CHATBOT_SESSION_EXPIRE_HOURS,
    )
    if timezone.now() <= deadline:
        return False

    clear_completions(user=user, session_id=session.id)
    return True
