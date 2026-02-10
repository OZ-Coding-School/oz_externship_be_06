from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.users.models import User


def create_support_session(
    *,
    user: User,
    title: str,
    using_model: str,
) -> ChatbotSession:
    """고객지원(support) 전용 챗봇 세션 생성"""

    return ChatbotSession.objects.create(
        user=user,
        question=None,
        title=title,
        using_model=using_model,
    )
