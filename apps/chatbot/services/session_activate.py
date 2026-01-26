from typing import Any, Tuple

from django.db import IntegrityError, transaction

from apps.chatbot.models.chatbot_session import ChatbotSession


@transaction.atomic
def activate_session(*, user: Any, question_id: int) -> Tuple[ChatbotSession, bool]:
    """
    챗봇 세션 활성화

    - user + question 기준으로 세션을 idempotent 하게 생성/반환한다.
    - 동시 요청 시 중복 생성을 방지하기 위해 row-level lock을 사용한다.
    - ChatbotSession 모델에 status 필드가 없으므로 상태 기반 분기는 수행하지 않는다.
    """

    # 기존 세션이 있으면 그대로 반환 (동시성 제어를 위해 select_for_update 사용)
    session = ChatbotSession.objects.select_for_update().filter(user=user, question_id=question_id).first()

    if session:
        return session, False

    try:
        # 세션이 없으면 새로 생성
        session = ChatbotSession.objects.create(
            user=user,
            question_id=question_id,
            title="새 채팅",
            using_model=ChatbotSession.AIModel.GPT,
        )
        return session, True

    except IntegrityError:
        # race condition으로 이미 생성된 경우 재조회하여 반환
        session = ChatbotSession.objects.get(user=user, question_id=question_id)
        return session, False
