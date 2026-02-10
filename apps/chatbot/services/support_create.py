from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.users.models import User


def create_support_session(
    *,
    user: User,
    title: str,
    using_model: str,
) -> ChatbotSession:
    return ChatbotSession.objects.create(
        user=user,
        question=None,
        title=title,
        using_model=using_model,
    )
