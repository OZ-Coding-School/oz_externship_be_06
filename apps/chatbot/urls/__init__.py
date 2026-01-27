from django.urls import path

from apps.chatbot.views.session import ChatbotSessionAPIView
from apps.chatbot.views.session_activate import ChatbotSessionActivateAPIView
from apps.chatbot.views.session_delete import ChatbotSessionDeleteAPIView

urlpatterns = [
    # 세션 목록 조회 (GET) / 세션 생성 (POST)
    path(
        "sessions/",
        ChatbotSessionAPIView.as_view(),
        name="chatbot-session",
    ),
    # 세션 활성화
    path(
        "sessions/activate/",
        ChatbotSessionActivateAPIView.as_view(),
        name="chatbot-session-activate",
    ),
    # 세션 삭제
    path(
        "sessions/<int:session_id>/",
        ChatbotSessionDeleteAPIView.as_view(),
        name="chatbot-session-delete",
    ),
]
