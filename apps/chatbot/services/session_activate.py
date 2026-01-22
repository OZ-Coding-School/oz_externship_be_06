from typing import Any, Tuple

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.chatbot.models.chatbot_session import ChatbotSession


@transaction.atomic
def activate_session(*, user: Any, question_id: int) -> Tuple[ChatbotSession, bool]:
    """
    채팅 진입 시 세션 활성화
    - user + question 기준 idempotent
    - 응답 중(RESPONDING) 세션은 진입 차단
    """

    session = ChatbotSession.objects.select_for_update().filter(user=user, question_id=question_id).first()

    if session:
        # Django model field (mypy 미지원)
        if session.status == ChatbotSession.SessionStatus.RESPONDING:  # type: ignore[attr-defined]
            raise ValidationError("이미 응답이 진행 중인 세션입니다.")
        return session, False

    try:
        session = ChatbotSession.objects.create(
            user=user,
            question_id=question_id,
            title="새 채팅",
            using_model=ChatbotSession.UsingModel.GPT,  # type: ignore[attr-defined]
            status=ChatbotSession.SessionStatus.IDLE,  # type: ignore[misc]
        )
        return session, True

    except IntegrityError:
        session = ChatbotSession.objects.get(user=user, question_id=question_id)
        if session.status == ChatbotSession.SessionStatus.RESPONDING:  # type: ignore[attr-defined]
            raise ValidationError("이미 응답이 진행 중인 세션입니다.")
        return session, False
