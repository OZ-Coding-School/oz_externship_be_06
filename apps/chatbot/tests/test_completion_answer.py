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
                        system_prompt="test system prompt",
                    )
                )

    @override_settings(GEMINI_API_KEY="test-api-key")
    @patch("apps.chatbot.services.completion_answer.genai")
    def test_generate_completion_answer_mock(self, mock_genai: Any) -> None:
        # given
        chunk1 = MagicMock()
        chunk1.text = "an"
        chunk2 = MagicMock()
        chunk2.text = "swer"

        mock_response: Iterator[Any] = iter([chunk1, chunk2])

        mock_models = MagicMock()
        mock_models.generate_content_stream.return_value = mock_response

        mock_client = MagicMock()
        mock_client.models = mock_models

        mock_genai.Client.return_value = mock_client

        # when
        result_iter = generate_completion_answer(
            session=self.session,
            system_prompt="test system prompt",
        )
        result = "".join(list(result_iter))

        # then
        self.assertEqual(result, "answer")
        mock_genai.Client.assert_called_once_with(api_key="test-api-key")
        mock_models.generate_content_stream.assert_called_once()
