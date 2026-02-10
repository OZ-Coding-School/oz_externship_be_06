from django.core.exceptions import ValidationError

from apps.chatbot.constants.question_prompts import QUESTION_SYSTEM_PROMPT
from apps.chatbot.constants.support_prompts import SUPPORT_FULL_PROMPT
from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.services.completion_answer import generate_completion_answer
from apps.chatbot.services.completion_user_create import create_user_completion
from apps.chatbot.services.question_completion_policy import (
    validate_user_prompt_policy as validate_question_policy,
)
from apps.chatbot.services.support_completion_policy import (
    validate_user_prompt_policy as validate_support_policy,
)


def _is_support_session(*, session: ChatbotSession) -> bool:
    return session.question_id is None


def _validate_policy(*, session: ChatbotSession, content: str) -> None:
    if _is_support_session(session=session):
        validate_support_policy(session=session, content=content)
        return

    validate_question_policy(session=session, content=content)


def _resolve_system_prompt(*, session: ChatbotSession) -> str:
    return SUPPORT_FULL_PROMPT if _is_support_session(session=session) else QUESTION_SYSTEM_PROMPT


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

    _validate_policy(session=session, content=content)

    user_completion = create_user_completion(
        session=session,
        content=content,
    )

    system_prompt = _resolve_system_prompt(session=session)

    generate_completion_answer(
        session=session,
        system_prompt=system_prompt,
    )

    return user_completion
