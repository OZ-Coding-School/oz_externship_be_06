from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.services.completion_clear import clear_completions


class Command(BaseCommand):
    help = "만료된 질문하기(QnA) 챗봇 세션의 대화 내역을 정리한다."

    def handle(self, *args: Any, **options: Any) -> None:
        deadline = timezone.now() - timedelta(hours=settings.CHATBOT_SESSION_EXPIRE_HOURS)

        sessions = ChatbotSession.objects.filter(
            question__isnull=False,
            updated_at__lt=deadline,
        ).only("id", "user_id")

        for session in sessions.iterator():
            clear_completions(
                user=session.user,
                session_id=session.id,
            )
