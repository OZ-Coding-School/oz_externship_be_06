from django.core.exceptions import ValidationError

from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession


def create_user_completion(
    *,
    session: ChatbotSession,
    content: str,
) -> ChatbotCompletions:
    """
    사용자 메시지를 저장한다.
    """

    if session is None:
        raise ValidationError("챗봇 세션이 존재하지 않습니다.")

    return ChatbotCompletions.objects.create(
        session=session,
        content=content,
        role=ChatbotCompletions.Role.USER,
    )
