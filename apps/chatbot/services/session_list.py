from django.db.models import QuerySet

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.users.models import User


def get_user_chatbot_sessions(*, user: User) -> QuerySet[ChatbotSession]:
    return ChatbotSession.objects.filter(user=user).select_related("question")
