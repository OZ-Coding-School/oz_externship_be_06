from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.services.session_activate import activate_session
from apps.qna.models import Question, QuestionCategory

User = get_user_model()


class TestChatbotSessionActivate(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="user@test.com",
            password="pw1234",
            birthday="2000-01-01",
        )

        self.category = QuestionCategory.objects.create(name="테스트 카테고리")

        self.question = Question.objects.create(
            category=self.category,
            author=self.user,
            title="테스트 질문",
            content="테스트 내용",
        )

    def test_activate_new_session(self) -> None:
        session, created = activate_session(user=self.user, question_id=self.question.id)

        self.assertTrue(created)
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.question, self.question)

    def test_activate_existing_session(self) -> None:
        ChatbotSession.objects.create(
            user=self.user,
            question=self.question,
            title="기존 세션",
            using_model=ChatbotSession.AIModel.GPT,
        )

        session, created = activate_session(user=self.user, question_id=self.question.id)

        self.assertFalse(created)

        existing = ChatbotSession.objects.first()
        assert existing is not None
        self.assertEqual(session.id, existing.id)
