from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.qna.models import Question
from apps.users.models import User


def _validate_question_exists(*, question_id: int) -> None:
    if not Question.objects.filter(id=question_id).exists():
        raise ValidationError("존재하지 않는 질문입니다.")


@transaction.atomic
def create_or_activate_chatbot_session(
    *,
    user: User,
    question_id: int,
    title: str | None = None,
    using_model: str | None = None,
) -> tuple[ChatbotSession, bool]:
    _validate_question_exists(question_id=question_id)

    session = ChatbotSession.objects.select_for_update().filter(user=user, question_id=question_id).first()

    if session:
        return session, False

    try:
        session = ChatbotSession.objects.create(
            user=user,
            question_id=question_id,
            title=title or "새 채팅",
            using_model=using_model or ChatbotSession.AIModel.GEMINI,
        )
        return session, True

    except IntegrityError:
        session = ChatbotSession.objects.get(user=user, question_id=question_id)
        return session, False
