from django.core.exceptions import ValidationError

from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession


def create_user_completion(
    *,
    session: ChatbotSession,
    content: str,
) -> ChatbotCompletions:
    """
    USER 메시지 저장 로직
    - ChatbotCompletions 모델 기준
    - validation / 질문 제한 정책은 상위 레이어에서 처리
    """

    if session is None:
        raise ValidationError("챗봇 세션이 존재하지 않습니다.")

    return ChatbotCompletions.objects.create(
        session=session,
        content=content,
        role=ChatbotCompletions.Role.USER,  # "User"
    )
