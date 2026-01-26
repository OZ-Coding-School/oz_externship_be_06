from typing import Any

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.serializers.session import ChatbotSessionSerializer
from apps.core.utils.pagination import ChatbotSessionCursorPagination


@extend_schema(
    tags=["chatbot"],
    summary="챗봇 세션 목록 조회",
    description="사용자의 챗봇 세션 목록을 조회합니다. (Cursor Pagination 적용)",
)
class ChatbotSessionListAPIView(generics.ListAPIView[Any]):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatbotSessionSerializer
    pagination_class = ChatbotSessionCursorPagination

    def get_queryset(self) -> QuerySet[ChatbotSession]:
        user_id = self.request.user.id
        assert user_id is not None

        return ChatbotSession.objects.filter(user_id=user_id).select_related("question")
