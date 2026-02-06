from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.qna.models import Question, QuestionCategory

User = get_user_model()


class ChatbotSessionCloseAPITest(TestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()

        self.user = User.objects.create(
            email="user@test.com",
            birthday="2000-01-01",
            is_active=True,
        )
        self.user.set_password("password")
        self.user.save()

        self.other_user = User.objects.create(
            email="other@test.com",
            birthday="1999-12-31",
            is_active=True,
        )
        self.other_user.set_password("password")
        self.other_user.save()

        self.category = QuestionCategory.objects.create(
            name="test-category",
        )

        self.question = Question.objects.create(
            title="test question",
            content="content",
            author=self.user,
            category=self.category,
        )

        # support 세션
        self.support_session = ChatbotSession.objects.create(
            user=self.user,
            question=None,
            title="support",
            using_model="Gemini",
        )
        ChatbotCompletions.objects.create(
            session=self.support_session,
            content="support prompt",
            role=ChatbotCompletions.Role.USER,
        )

        # 질문하기 세션
        self.qna_session = ChatbotSession.objects.create(
            user=self.user,
            question=self.question,
            title="qna",
            using_model="Gemini",
        )
        ChatbotCompletions.objects.create(
            session=self.qna_session,
            content="qna message",
            role=ChatbotCompletions.Role.USER,
        )

    def test_close_support_session_clears_completions(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = f"/api/v1/chatbot/sessions/{self.support_session.id}/close/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            ChatbotCompletions.objects.filter(session=self.support_session).count(),
            0,
        )

    def test_close_qna_session_does_not_clear_completions(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = f"/api/v1/chatbot/sessions/{self.qna_session.id}/close/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            ChatbotCompletions.objects.filter(session=self.qna_session).count(),
            1,
        )

    def test_close_updates_updated_at(self) -> None:
        self.client.force_authenticate(user=self.user)

        before = self.qna_session.updated_at
        url = f"/api/v1/chatbot/sessions/{self.qna_session.id}/close/"
        self.client.post(url)

        self.qna_session.refresh_from_db()
        self.assertGreater(self.qna_session.updated_at, before)

    def test_close_forbidden(self) -> None:
        self.client.force_authenticate(user=self.other_user)

        url = f"/api/v1/chatbot/sessions/{self.qna_session.id}/close/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_close_not_found(self) -> None:
        self.client.force_authenticate(user=self.user)

        url = "/api/v1/chatbot/sessions/999999/close/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ChatbotSessionExpireAPITest(TestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()

        self.user = User.objects.create(
            email="user@test.com",
            birthday="2000-01-01",
            is_active=True,
        )
        self.user.set_password("password")
        self.user.save()

        self.category = QuestionCategory.objects.create(
            name="expire-category",
        )

        self.question = Question.objects.create(
            title="expire test",
            content="content",
            author=self.user,
            category=self.category,
        )

        self.session = ChatbotSession.objects.create(
            user=self.user,
            question=self.question,
            title="qna",
            using_model="Gemini",
        )
        ChatbotCompletions.objects.create(
            session=self.session,
            content="old message",
            role=ChatbotCompletions.Role.USER,
        )

        ChatbotSession.objects.filter(id=self.session.id).update(
            updated_at=timezone.now() - timedelta(hours=3, minutes=1),
        )

    def test_expire_on_completion_create(self) -> None:
        from apps.chatbot.services.completion_create import create_user_completion

        create_user_completion(
            session=self.session,
            content="new message",
        )

        self.assertEqual(
            ChatbotCompletions.objects.filter(session=self.session).count(),
            1,
        )
        self.assertEqual(
            ChatbotCompletions.objects.filter(
                session=self.session,
                content="new message",
            ).count(),
            1,
        )
