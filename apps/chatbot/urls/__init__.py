from django.urls import path

from apps.chatbot.views.session import ChatbotSessionAPIView
from apps.chatbot.views.session_delete import ChatbotSessionDeleteAPIView

urlpatterns = [
    # 세션 목록 조회 (GET) / 세션 생성 (POST, activate 포함)
    path(
        "sessions/",
        ChatbotSessionAPIView.as_view(),
        name="chatbot-session",
    ),
    # 세션 삭제
    path(
        "sessions/<int:session_id>/",
        ChatbotSessionDeleteAPIView.as_view(),
        name="chatbot-session-delete",
    ),
]
