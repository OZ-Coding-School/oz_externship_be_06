from django.shortcuts import get_object_or_404

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.qna.models import Question
from apps.users.models import User


def create_support_session(
    *,
    user: User,
    title: str,
    using_model: str,
) -> ChatbotSession:
    support_question = get_object_or_404(
        Question,
        title="SYSTEM_SUPPORT",
    )

    return ChatbotSession.objects.create(
        user=user,
        question=support_question,
        title=title,
        using_model=using_model,
    )
