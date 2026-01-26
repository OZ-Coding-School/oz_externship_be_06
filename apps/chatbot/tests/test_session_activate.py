from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.qna.models import Question, QuestionCategory

User = get_user_model()


class ChatbotSessionActivateAPITest(TestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()

        self.user = User.objects.create_user(
            email="user1@test.com",
            password="password",
            birthday="2000-01-01",
        )

        self.category = QuestionCategory.objects.create(
            name="dummy-category",
        )

        self.question = Question.objects.create(
            author=self.user,
            category=self.category,
            title="dummy",
            content="dummy",
        )

        self.activate_url = reverse("chatbot-session-activate")

    def test_activate_session_creates_new_session(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.activate_url,
            data={"question_id": self.question.id},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["created"])
        self.assertTrue(
            ChatbotSession.objects.filter(
                user=self.user,
                question_id=self.question.id,
            ).exists()
        )

    def test_activate_existing_session_returns_existing(self) -> None:
        self.client.force_authenticate(user=self.user)

        existing_session = ChatbotSession.objects.create(
            user=self.user,
            question_id=self.question.id,
            title="기존 세션",
            using_model=ChatbotSession.AIModel.GEMINI,
        )

        response = self.client.post(
            self.activate_url,
            data={"question_id": self.question.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["created"])
        self.assertEqual(
            response.data["session"]["id"],
            existing_session.id,
        )

    def test_activate_requires_authentication(self) -> None:
        response = self.client.post(
            self.activate_url,
            data={"question_id": self.question.id},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
