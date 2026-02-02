from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.services.completion_create import create_user_completion

User = get_user_model()


class CreateUserCompletionServiceTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            birthday=date(2000, 1, 1),
        )

        self.session = ChatbotSession.objects.create(
            user=self.user,
            question_id=1,
            title="테스트 세션",
            using_model="GEMINI",
        )
