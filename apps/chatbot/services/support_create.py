from apps.chatbot.constants.support_prompts import SUPPORT_SYSTEM_PROMPT
from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.users.models import User


def create_support_session(
    *,
    user: User,
    title: str,
    using_model: str,
) -> ChatbotSession:
    """고객지원(support) 전용 챗봇 세션 생성"""

    # support 세션 생성 (question=None으로 유형 구분)
    session = ChatbotSession.objects.create(
        user=user,
        question=None,
        title=title,
        using_model=using_model,
    )

    # SYSTEM 프롬프트 1회 저장
    ChatbotCompletions.objects.create(
        session=session,
        role=ChatbotCompletions.Role.USER,
        content=SUPPORT_SYSTEM_PROMPT,
    )

    return session
