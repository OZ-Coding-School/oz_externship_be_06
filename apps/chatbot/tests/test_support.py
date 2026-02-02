from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.chatbot.models.chatbot_session import ChatbotSession

User = get_user_model()


class ChatbotSupportSessionCreateAPITest(TestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()

        self.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            birthday="1995-01-01",
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
        self.assertIsNone(response.data["question"])

        self.assertTrue(
            ChatbotSession.objects.filter(
                user=self.user,
                title=payload["title"],
                using_model=payload["using_model"],
                question__isnull=True,
            ).exists()
        )
