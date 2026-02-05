from datetime import date
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.services.completion_answer import generate_completion_answer

User = get_user_model()


class CompletionAnswerTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            birthday=date(1995, 1, 1),
        )
        self.session = ChatbotSession.objects.create(
            user=self.user,
            title="test",
            using_model="gemini-1.5-flash",
        )

    @patch("apps.chatbot.services.completion_answer.genai.GenerativeModel")
    def test_generate_completion_answer_mock(self, mock_model: MagicMock) -> None:
        mock_chat = MagicMock()
        mock_chat.send_message.return_value = [
            MagicMock(text="an"),
            MagicMock(text="swer"),
        ]

        mock_model.return_value.start_chat.return_value = mock_chat

        result_iter = generate_completion_answer(
            session=self.session,
            user_message="hi",
        )

        result = "".join(result_iter)

        self.assertEqual(result, "answer")
