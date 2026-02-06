from django.core.exceptions import ValidationError

from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.services.session_expire import expire_if_needed


def create_user_completion(
    *,
    session: ChatbotSession,
    content: str,
) -> ChatbotCompletions:
    """
    USER 메시지 저장 로직

    - 일반 사용자 입력을 ChatbotCompletions로 저장한다.
    - support 세션의 SYSTEM 프롬프트는 이 로직을 타지 않는다.
    - 입력 validation 및 질문 제한 정책은 상위 레이어에서 처리한다.
    """

    if session is None:
        raise ValidationError("챗봇 세션이 존재하지 않습니다.")

    # 만료 세션 정리
    expire_if_needed(user=session.user, session=session)

    return ChatbotCompletions.objects.create(
        session=session,
        content=content,
        role=ChatbotCompletions.Role.USER,
    )
