from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.qna.models import Question

User = get_user_model()


class TestChatbotSessionList(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="user1@test.com",
            password="pw1234",
            birthday=date(2000, 1, 1),
        )
        self.other = User.objects.create_user(
            email="user2@test.com",
            password="pw1234",
            birthday=date(2000, 1, 2),
        )

        self.question = Question.objects.create(
            title="테스트 질문",
            content="테스트 내용",
        )

        ChatbotSession.objects.bulk_create(
            [
                ChatbotSession(
                    user=self.user,
                    question=self.question,
                    title=f"title-{i}",
                    using_model=ChatbotSession.AIModel.GPT,
                )
                for i in range(12)
            ]
        )

        ChatbotSession.objects.bulk_create(
            [
                ChatbotSession(
                    user=self.other,
                    question=self.question,
                    title=f"other-{i}",
                    using_model=ChatbotSession.AIModel.GPT,
                )
                for i in range(3)
            ]
        )

    def test_list_only_my_sessions_and_pagination(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("chatbot-session-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])
        self.assertTrue(all(item["user"] == self.user.id for item in response.data["results"]))
