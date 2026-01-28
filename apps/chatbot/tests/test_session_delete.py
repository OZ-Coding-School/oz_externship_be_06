from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.qna.models import Question, QuestionCategory

User = get_user_model()


class ChatbotSessionDeleteAPITest(TestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()

        self.user = User.objects.create_user(
            email="user1@test.com",
            password="password",
            birthday="2000-01-01",
        )
        self.other_user = User.objects.create_user(
            email="user2@test.com",
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

        self.session = ChatbotSession.objects.create(
            user=self.user,
            question_id=self.question.id,
            title="테스트 세션",
            using_model=ChatbotSession.AIModel.GEMINI,
        )

    def test_delete_own_session_success(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = reverse("chatbot-session-delete", args=[self.session.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ChatbotSession.objects.filter(id=self.session.id).exists())

    def test_delete_other_user_session_returns_404(self) -> None:
        self.client.force_authenticate(user=self.other_user)

        url = reverse("chatbot-session-delete", args=[self.session.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(ChatbotSession.objects.filter(id=self.session.id).exists())

    def test_delete_not_found_session_returns_404(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = reverse("chatbot-session-delete", args=[9999])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
