from datetime import date
from typing import Any

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.qna.models import Question
from apps.qna.models.question_category import QuestionCategory
from apps.users.models import User


class TestChatbotSessionAPI(APITestCase):
    user: User
    other: User
    category: QuestionCategory
    questions: Any
    session_url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="user1@test.com",
            password="pw1234",
            birthday=date(2000, 1, 1),
            is_active=True,
        )
        cls.other = User.objects.create_user(
            email="user2@test.com",
            password="pw1234",
            birthday=date(2000, 1, 2),
            is_active=True,
        )

        cls.category = QuestionCategory.objects.create(
            name="테스트 카테고리",
        )

        cls.questions = [
            Question.objects.create(
                category=cls.category,
                author=cls.user,
                title=f"테스트 질문 {i}",
                content="테스트 내용",
            )
            for i in range(3)
        ]

        cls.session_url = reverse("chatbot-session")

    # -------------------------
    # POST /sessions
    # -------------------------
    def test_create_session_first_time(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.session_url,
            data={
                "question": self.questions[0].id,
                "using_model": "gemini",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            ChatbotSession.objects.filter(
                user=self.user,
                question=self.questions[0],
            ).exists()
        )
        self.assertEqual(response.data["question"], self.questions[0].id)

    def test_create_session_idempotent(self) -> None:
        self.client.force_authenticate(user=self.user)

        self.client.post(
            self.session_url,
            data={"question": self.questions[1].id},
            format="json",
        )

        response = self.client.post(
            self.session_url,
            data={"question": self.questions[1].id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ChatbotSession.objects.filter(
                user=self.user,
                question=self.questions[1],
            ).count(),
            1,
        )

    def test_create_requires_authentication(self) -> None:
        response = self.client.post(
            self.session_url,
            data={"question": self.questions[2].id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
