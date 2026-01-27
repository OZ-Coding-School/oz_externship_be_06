from django.db.models import QuerySet

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.users.models import User


def get_user_chatbot_sessions(*, user: User) -> QuerySet[ChatbotSession]:
    """
    사용자 기준 챗봇 세션 목록 조회
    - Cursor Pagination 대응을 위해 정렬 포함
    """
    return ChatbotSession.objects.filter(user=user).select_related("question").order_by("-created_at")
