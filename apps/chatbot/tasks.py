from __future__ import annotations

from datetime import timedelta

from celery import shared_task  # type: ignore
from django.conf import settings
from django.utils import timezone

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.services.session_delete import delete_chatbot_session


@shared_task  # type: ignore[misc]
def delete_expired_qna_sessions() -> None:
    deadline = timezone.now() - timedelta(hours=settings.CHATBOT_SESSION_EXPIRE_HOURS)

    sessions = ChatbotSession.objects.select_related("user").filter(
        question__isnull=False,
        updated_at__lt=deadline,
    )

    for session in sessions.iterator():
        delete_chatbot_session(
            user=session.user,
            session_id=session.id,
        )
