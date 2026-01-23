from django.urls import path

from apps.chatbot.views.session_activate import ChatbotSessionActivateAPIView
from apps.chatbot.views.session_create import ChatbotSessionCreateAPIView

urlpatterns = [
    # 세션 생성
    path(
        "sessions/",
        ChatbotSessionCreateAPIView.as_view(),
        name="chatbot-session-create",
    ),
    # 세션 활성화
    path(
        "sessions/activate/",
        ChatbotSessionActivateAPIView.as_view(),
        name="chatbot-session-activate",
    ),
]
