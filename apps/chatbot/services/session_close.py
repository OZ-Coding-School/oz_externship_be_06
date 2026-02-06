from __future__ import annotations

from django.db import transaction

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.services.completion_clear import clear_completions
from apps.users.models import User


@transaction.atomic
def close_session(*, user: User, session_id: int) -> None:
    session = ChatbotSession.objects.select_for_update().filter(pk=session_id).first()
    if session is None:
        raise ChatbotSession.DoesNotExist

    if session.user_id != user.id:
        raise PermissionError

    # support: 즉시 초기화
    if session.question_id is None:
        clear_completions(user=user, session_id=session.id)

    # 질문하기: 유예만 시작 (updated_at 갱신)
    session.save(update_fields=["updated_at"])
