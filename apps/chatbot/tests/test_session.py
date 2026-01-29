from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.qna.models import Question
from apps.qna.models.question_category import QuestionCategory

User = get_user_model()


class TestChatbotSessionAPI(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="user1@test.com",
            password="pw1234",
            birthday=date(2000, 1, 1),
            is_active=True,
        )
        self.other = User.objects.create_user(
            email="user2@test.com",
            password="pw1234",
            birthday=date(2000, 1, 2),
            is_active=True,
        )

        self.category = QuestionCategory.objects.create(
            name="테스트 카테고리",
        )

        self.questions = [
            Question.objects.create(
                category=self.category,
                author=self.user,
                title=f"테스트 질문 {i}",
                content="테스트 내용",
            )
            for i in range(15)
        ]

        # user 세션 12개
        ChatbotSession.objects.bulk_create(
            [
                ChatbotSession(
                    user=self.user,
                    question=self.questions[i],
                    title=f"title-{i}",
                    using_model=ChatbotSession.AIModel.GEMINI,
                )
                for i in range(12)
            ]
        )

        # other user 세션 3개
        ChatbotSession.objects.bulk_create(
            [
                ChatbotSession(
                    user=self.other,
                    question=self.questions[i],
                    title=f"other-{i}",
                    using_model=ChatbotSession.AIModel.GEMINI,
                )
                for i in range(3)
            ]
        )

        self.session_url = reverse("chatbot-session")

    # -------------------------
    # GET /sessions
    # -------------------------
    def test_list_only_my_sessions_and_pagination(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.session_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])
        self.assertTrue(all(item["user"] == self.user.id for item in response.data["results"]))

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

        # 첫 요청
        self.client.post(
            self.session_url,
            data={"question": self.questions[1].id},
            format="json",
        )

        # 같은 질문으로 재요청
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
