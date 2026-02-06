from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.services.completion_create import create_user_completion
from apps.qna.models import Question, QuestionCategory

User = get_user_model()


class CreateUserCompletionServiceTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            birthday=date(2000, 1, 1),
        )

        # 필수 FK
        self.category = QuestionCategory.objects.create(name="테스트 카테고리")

        self.question = Question.objects.create(
            category=self.category,
            author=self.user,
            title="테스트 질문",
            content="질문 내용입니다.",
        )

        self.session = ChatbotSession.objects.create(
            user=self.user,
            question=self.question,
            title="테스트 세션",
            using_model="GEMINI",
        )

    def test_create_user_completion_success(self) -> None:
        completion = create_user_completion(
            session=self.session,
            content="테스트 메시지",
        )

        self.assertEqual(completion.session, self.session)
        self.assertEqual(completion.role, ChatbotCompletions.Role.USER)
        self.assertEqual(completion.content, "테스트 메시지")

    def test_create_user_completion_without_session_fail(self) -> None:
        with self.assertRaises(ValidationError):
            create_user_completion(
                session=None,  # type: ignore[arg-type]
                content="메시지",
            )
