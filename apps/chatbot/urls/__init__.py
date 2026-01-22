from django.urls import path

from apps.chatbot.views.session_activate import (
    ChatbotSessionActivateAPIView,
)

urlpatterns = [
    path(
        "activate/",
        ChatbotSessionActivateAPIView.as_view(),
        name="chatbot-session-activate",
    ),
]
