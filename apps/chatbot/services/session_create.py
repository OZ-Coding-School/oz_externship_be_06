from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.qna.models import Question
from apps.users.models import User


@transaction.atomic
def create_chatbot_session(
    *,
    user: User,
    question_id: int,
    title: str | None = None,
    using_model: str | None = None,
) -> ChatbotSession:
    # 질문 존재 여부 확인
    if not Question.objects.filter(id=question_id).exists():
        raise ValidationError("존재하지 않는 질문입니다.")

    try:
        return ChatbotSession.objects.create(
            user=user,
            question_id=question_id,
            title=title or "새 채팅",
            using_model=using_model or ChatbotSession.AIModel.GEMINI,
        )
    except IntegrityError as exc:
        # user + question 유니크 제약
        raise ValidationError("이미 해당 질문에 대한 세션이 존재합니다.") from exc
