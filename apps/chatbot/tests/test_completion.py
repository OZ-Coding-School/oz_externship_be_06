from __future__ import annotations

from datetime import date
from typing import Iterable, cast
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.http import StreamingHttpResponse
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.services.completion_user_create import create_user_completion
from apps.chatbot.services.support_completion_policy import validate_user_prompt_policy
from apps.users.models import User


class ChatbotCompletionTest(TestCase):
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
            using_model=ChatbotSession.AIModel.GEMINI,
        )

    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    # ==========================
    # create_user_completion
    # ==========================

    def test_create_user_completion_success(self) -> None:
        completion = create_user_completion(
            session=self.session,
            content="hi",
        )

        self.assertEqual(completion.session, self.session)
        self.assertEqual(completion.content, "hi")
        self.assertEqual(completion.role, ChatbotCompletions.Role.USER)

    def test_create_user_completion_blank_allowed(self) -> None:
        completion = create_user_completion(
            session=self.session,
            content="",
        )

        self.assertEqual(completion.content, "")
        self.assertEqual(completion.role, ChatbotCompletions.Role.USER)

    def test_create_user_completion_without_session_fail(self) -> None:
        with self.assertRaises(ValidationError):
            create_user_completion(
                session=None,  # type: ignore[arg-type]
                content="hi",
            )

    def test_create_user_completion_multiple_calls(self) -> None:
        first = create_user_completion(session=self.session, content="first")
        second = create_user_completion(session=self.session, content="second")

        self.assertNotEqual(first.id, second.id)
        self.assertEqual(ChatbotCompletions.objects.count(), 2)

    def test_create_user_completion_korean_message(self) -> None:
        completion = create_user_completion(
            session=self.session,
            content="테스트 메시지",
        )

        self.assertEqual(completion.content, "테스트 메시지")
        self.assertEqual(completion.role, ChatbotCompletions.Role.USER)

    # ==========================
    # support policy (smoke)
    # ==========================

    def test_validate_user_prompt_policy_pass(self) -> None:
        # 예외가 발생하지 않으면 성공
        validate_user_prompt_policy(
            session=self.session,
            content="hi",
        )

    # ==========================
    # completion view
    # ==========================

    def test_completion_view_unauthenticated(self) -> None:
        from apps.chatbot.views.completion import ChatbotCompletionCreateAPIView

        request = self.factory.post(
            "/fake/",
            data={"message": "hi"},
            format="json",
        )

        response = ChatbotCompletionCreateAPIView.as_view()(
            request,
            session_id=self.session.id,
        )

        self.assertEqual(response.status_code, 401)

    def test_completion_view_invalid_message(self) -> None:
        from apps.chatbot.views.completion import ChatbotCompletionCreateAPIView

        request = self.factory.post(
            "/fake/",
            data={"message": "   "},
            format="json",
        )
        force_authenticate(request, user=self.user)

        response = ChatbotCompletionCreateAPIView.as_view()(
            request,
            session_id=self.session.id,
        )

        self.assertEqual(response.status_code, 400)

    def test_completion_view_success_streaming(self) -> None:
        from apps.chatbot.views.completion import ChatbotCompletionCreateAPIView

        request = self.factory.post(
            "/fake/",
            data={"message": "hi"},
            format="json",
        )
        force_authenticate(request, user=self.user)

        with (
            patch(
                "apps.chatbot.views.completion.generate_completion_answer",
                return_value=iter(["answer"]),
            ),
            patch(
                "apps.chatbot.views.completion.cache.add",
                return_value=True,
            ),
            patch(
                "apps.chatbot.views.completion.cache.delete",
                return_value=True,
            ),
        ):
            response = ChatbotCompletionCreateAPIView.as_view()(
                request,
                session_id=self.session.id,
            )

            streaming_response = cast(StreamingHttpResponse, response)
            self.assertEqual(streaming_response.status_code, 201)

            content_iter = cast(Iterable[bytes], streaming_response.streaming_content)
            body = b"".join(content_iter)

            self.assertIn(b"[DONE]", body)

        self.assertEqual(
            ChatbotCompletions.objects.filter(session=self.session).count(),
            2,
        )
