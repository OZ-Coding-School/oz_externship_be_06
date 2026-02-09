from __future__ import annotations

from datetime import date
from typing import Any, Iterator
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.services.completion_answer import generate_completion_answer
from apps.users.models import User


class CompletionAnswerTest(TestCase):
    user: User
    session: ChatbotSession

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            birthday=date(1995, 1, 1),
        )
        cls.session = ChatbotSession.objects.create(
            user=cls.user,
            title="test_session",
            using_model="gemini-1.5-flash",
        )

    def test_generate_completion_answer_missing_api_key(self) -> None:
        with override_settings(GEMINI_API_KEY=None):
            with self.assertRaises(ValidationError):
                _ = list(
                    generate_completion_answer(
                        session=self.session,
                        user_message="hi",
                    )
                )

    @override_settings(GEMINI_API_KEY="test-api-key")
    @patch("apps.chatbot.services.completion_answer.genai")
    def test_generate_completion_answer_mock(self, mock_genai: Any) -> None:
        chunk1 = MagicMock()
        chunk1.text = "an"
        chunk2 = MagicMock()
        chunk2.text = "swer"

        mock_response: Iterator[Any] = iter([chunk1, chunk2])

        mock_chat = MagicMock()
        mock_chat.send_message.return_value = mock_response

        mock_model = MagicMock()
        mock_model.start_chat.return_value = mock_chat

        mock_genai.GenerativeModel.return_value = mock_model

        result_iter = generate_completion_answer(
            session=self.session,
            user_message="select_related가 뭐야?",
        )
        result = "".join(list(result_iter))

        self.assertEqual(result, "answer")
        mock_genai.configure.assert_called_once()
        mock_genai.GenerativeModel.assert_called_once()
        mock_model.start_chat.assert_called_once()
        mock_chat.send_message.assert_called_once()
