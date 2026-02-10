from django.urls import path

from apps.chatbot.views.completion import ChatbotCompletionCreateAPIView
from apps.chatbot.views.session import ChatbotSessionAPIView
from apps.chatbot.views.session_delete import ChatbotSessionDeleteAPIView
from apps.chatbot.views.support import ChatbotSupportSessionCreateAPIView

urlpatterns = [
    # 세션 조회 (GET) / 세션 생성 (POST)
    path(
        "sessions/",
        ChatbotSessionAPIView.as_view(),
        name="chatbot-session",
    ),
    # 세션 삭제 (명시적 삭제)
    path(
        "sessions/<int:session_id>/",
        ChatbotSessionDeleteAPIView.as_view(),
        name="chatbot-session-delete",
    ),
    # 챗봇 응답 생성 (POST, SSE)
    path(
        "sessions/<int:session_id>/completions",
        ChatbotCompletionCreateAPIView.as_view(),
        name="chatbot-completions",
    ),
    # 시스템 챗봇 세션 생성 (Support)
    path(
        "support",
        ChatbotSupportSessionCreateAPIView.as_view(),
        name="chatbot-support-session",
    ),
]
