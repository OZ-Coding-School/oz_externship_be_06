from django.urls import path

from apps.chatbot.views.session_activate import ChatbotSessionActivateAPIView
from apps.chatbot.views.session_create import ChatbotSessionCreateAPIView
from apps.chatbot.views.session_list import ChatbotSessionListAPIView

urlpatterns = [
    path(
        "sessions/",
        ChatbotSessionCreateAPIView.as_view(),
        name="chatbot-session-create",
    ),
    path(
        "sessions/activate/",
        ChatbotSessionActivateAPIView.as_view(),
        name="chatbot-session-activate",
    ),
    path(
        "sessions/list/",
        ChatbotSessionListAPIView.as_view(),
        name="chatbot-session-list",
    ),
]
