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
        """인증된 사용자가 정상적으로 support 세션을 생성한다."""
        self.client.force_authenticate(user=self.user)

        url = reverse("chatbot-support-session")
        payload = {
            "title": "수강 관련 문의",
            "using_model": "gemini",
        }

        response: Any = self.client.post(url, payload, format="json")

        # response 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], payload["title"])
        self.assertEqual(response.data["using_model"], payload["using_model"])
        self.assertEqual(response.data["user"], self.user.id)

        # DB 저장 검증
        self.assertTrue(
            ChatbotSession.objects.filter(
                user=self.user,
                title=payload["title"],
                using_model=payload["using_model"],
            ).exists()
        )

    def test_create_support_session_unauthorized(self) -> None:
        """인증되지 않은 사용자는 support 세션을 생성할 수 없다."""
        url = reverse("chatbot-support-session")
        payload = {
            "title": "문의",
            "using_model": "gemini",
        }

        response: Any = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_support_session_invalid_model(self) -> None:
        """지원하지 않는 모델명이 들어오면 400 에러를 반환한다."""
        self.client.force_authenticate(user=self.user)

        url = reverse("chatbot-support-session")
        payload = {
            "title": "문의",
            "using_model": "jarvis-v1",
        }

        response: Any = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("using_model", response.data)
