from django.core.exceptions import ValidationError

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.users.models import User


def delete_chatbot_session(
    *,
    user: User,
    session_id: int,
) -> None:
    session = ChatbotSession.objects.filter(
        pk=session_id,
        user=user,
    ).first()

    if session is None:
        raise ValidationError("존재하지 않거나 접근 권한이 없는 세션입니다.")

    session.delete()
