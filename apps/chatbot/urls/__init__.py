from django.urls import path

from apps.chatbot.views.session import ChatbotSessionAPIView
from apps.chatbot.views.session_delete import ChatbotSessionDeleteAPIView
from apps.chatbot.views.support import ChatbotSupportSessionCreateAPIView

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
    # 시스템 챗봇 세션 생성 (플로팅 버튼 진입)
    path(
        "support",
        ChatbotSupportSessionCreateAPIView.as_view(),
        name="chatbot-support-session",
    ),
]
