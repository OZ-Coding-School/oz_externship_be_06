from django.core.exceptions import ValidationError

from apps.chatbot.constants.question_prompts import QUESTION_SYSTEM_PROMPT
from apps.chatbot.constants.support_prompts import SUPPORT_FULL_PROMPT
from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.services.completion_answer import generate_completion_answer
from apps.chatbot.services.question_completion_policy import (
    validate_user_prompt_policy as validate_question_policy,
)
from apps.chatbot.services.support_completion_policy import (
    validate_user_prompt_policy as validate_support_policy,
)


def create_completion(
    *,
    session: ChatbotSession,
    content: str,
) -> ChatbotCompletions:
    """
    챗봇 USER 입력 → 정책 검증 → AI 응답 생성 오케스트레이션
    """

    if session is None:
        raise ValidationError("챗봇 세션이 존재하지 않습니다.")

    # 세션 타입 판단
    is_support = session.question_id is None

    # 정책 검증
    if is_support:
        validate_support_policy(session=session, content=content)
    else:
        validate_question_policy(session=session, content=content)

    # USER 메시지 저장
    user_completion = ChatbotCompletions.objects.create(
        session=session,
        content=content,
        role=ChatbotCompletions.Role.USER,
    )

    # SYSTEM 프롬프트 선택
    system_prompt = SUPPORT_FULL_PROMPT if is_support else QUESTION_SYSTEM_PROMPT

    # AI 응답 생성
    generate_completion_answer(
        session=session,
        system_prompt=system_prompt,
    )

    return user_completion
