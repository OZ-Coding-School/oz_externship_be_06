from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.qna.models import Question
from apps.users.models import User


@transaction.atomic
def create_or_activate_chatbot_session(
    *,
    user: User,
    question_id: int,
    title: str | None = None,
    using_model: str | None = None,
) -> tuple[ChatbotSession, bool]:
    """
    챗봇 세션 생성 (activate 포함, idempotent)

    - 질문 존재 여부를 검증한다.
    - user + question 기준으로 세션이 있으면 반환하고, 없으면 생성한다.
    - 동시 요청 시 중복 생성을 방지하기 위해 row-level lock을 사용한다.
    """

    # 1. 질문 존재 여부 검증
    if not Question.objects.filter(id=question_id).exists():
        raise ValidationError("존재하지 않는 질문입니다.")

    # 2. 기존 세션 조회 (동시성 제어)
    session = ChatbotSession.objects.select_for_update().filter(user=user, question_id=question_id).first()

    if session:
        return session, False

    try:
        # 3. 세션이 없으면 새로 생성
        session = ChatbotSession.objects.create(
            user=user,
            question_id=question_id,
            title=title or "새 채팅",
            using_model=using_model or ChatbotSession.AIModel.GEMINI,
        )
        return session, True

    except IntegrityError:
        # race condition으로 이미 생성된 경우 재조회
        session = ChatbotSession.objects.get(user=user, question_id=question_id)
        return session, False
