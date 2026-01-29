from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.qna.models import Question

User = get_user_model()


class ChatbotSupportSessionCreateAPITest(TestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()

        self.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            birthday="1995-01-01",
        )

        category_model = Question._meta.get_field("category").remote_field.model
        self.category = category_model.objects.create(name="SYSTEM")  # type: ignore[attr-defined]

        self.support_question = Question.objects.create(
            title="SYSTEM_SUPPORT",
            author=self.user,
            category=self.category,
        )

    def test_create_support_session_success(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = reverse("chatbot-support-session")
        payload = {
            "title": "수강 관련 문의",
            "using_model": ChatbotSession.AIModel.GEMINI,
        }

        response: Any = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], payload["title"])
        self.assertEqual(response.data["using_model"], payload["using_model"])
        self.assertEqual(response.data["user"], self.user.id)

        self.assertTrue(
            ChatbotSession.objects.filter(
                user=self.user,
                title=payload["title"],
                using_model=payload["using_model"],
                question=self.support_question,
            ).exists()
        )

    def test_create_support_session_unauthorized(self) -> None:
        url = reverse("chatbot-support-session")
        payload = {
            "title": "문의",
            "using_model": ChatbotSession.AIModel.GEMINI,
        }

        response: Any = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_support_session_invalid_model(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = reverse("chatbot-support-session")
        payload = {
            "title": "문의",
            "using_model": "jarvis-v1",
        }

        response: Any = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("using_model", response.data)
