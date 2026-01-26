from django.urls import path

from apps.chatbot.views.session_activate import ChatbotSessionActivateAPIView
from apps.chatbot.views.session_create import ChatbotSessionCreateAPIView
from apps.chatbot.views.session_delete import ChatbotSessionDeleteAPIView
from apps.chatbot.views.session_list import ChatbotSessionListAPIView

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
    # 세션 목록 조회
    path(
        "sessions/list/",
        ChatbotSessionListAPIView.as_view(),
        name="chatbot-session-list",
    ),
    # 세션 삭제
    path(
        "sessions/<int:session_id>/",
        ChatbotSessionDeleteAPIView.as_view(),
        name="chatbot-session-delete",
    ),
]
