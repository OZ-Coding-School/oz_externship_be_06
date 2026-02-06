from __future__ import annotations

from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.users.models import User


def clear_completions(*, user: User, session_id: int) -> None:
    session = ChatbotSession.objects.filter(pk=session_id).first()
    if session is None:
        raise ChatbotSession.DoesNotExist

    if session.user_id != user.id:
        raise PermissionError

    ChatbotCompletions.objects.filter(session_id=session_id).delete()
