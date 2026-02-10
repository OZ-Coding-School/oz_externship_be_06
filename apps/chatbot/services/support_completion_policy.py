from rest_framework.exceptions import ValidationError

from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession

BLOCKED_PROMPT_KEYWORDS = [
    "시스템 프롬프트",
    "system prompt",
    "developer message",
    "hidden prompt",
    "프롬프트 보여줘",
    "프롬프트 공개",
    "너의 규칙",
    "너의 지침",
    "정책을 보여줘",
    "prompt",
    "지시를 무시",
    "이전 지시 무시",
    "ignore instructions",
    "override",
    "역할을 바꿔",
    "roleplay",
    "act as",
    "너는 이제",
    "탈옥",
    "jailbreak",
    "prompt injection",
    "dan",
    "api key",
    "secret key",
    "키를 알려줘",
    "토큰",
    "temperature",
    "top_p",
    "gpt",
    "gemini",
    "claude",
    "llama",
    "사용하는 모델",
    "모델 뭐야",
]

BLOCKED_SUPPORT_KEYWORDS = [
    "코드 짜줘",
    "프로그램 만들어줘",
    "앱 만들어줘",
    "웹 만들어줘",
    "알고리즘",
    "구현해줘",
    "소설 써줘",
    "시 써줘",
    "대본 써줘",
    "번역해줘",
    "요약해줘",
    "왜 그런지",
    "개념 설명",
    "문제 풀어줘",
    "로직 설명",
]


def validate_user_prompt_policy(
    *,
    session: ChatbotSession,
    content: str,
) -> None:
    _validate_support_session_alive(session=session)
    _validate_not_during_assistant_response(session=session)
    _validate_input_content(content=content)
    _validate_prompt_injection(content=content)
    _validate_support_domain(session=session, content=content)


def _is_support_session(*, session: ChatbotSession) -> bool:
    return session.question_id is None


def _validate_support_session_alive(*, session: ChatbotSession) -> None:
    if not _is_support_session(session=session):
        return

    if hasattr(session, "is_closed") and session.is_closed:
        raise ValidationError("이미 종료된 support 대화입니다.")


def _validate_not_during_assistant_response(*, session: ChatbotSession) -> None:
    last_completion = ChatbotCompletions.objects.filter(session=session).order_by("-created_at").first()

    if not last_completion:
        return

    if last_completion.role == ChatbotCompletions.Role.USER:
        raise ValidationError("AI 응답이 완료된 후 다시 질문해 주세요.")


def _validate_input_content(*, content: str) -> None:
    if not content or not content.strip():
        raise ValidationError("질문 내용을 입력해 주세요.")

    if len(content) > 1000:
        raise ValidationError("질문이 너무 깁니다. 내용을 줄여 주세요.")


def _validate_prompt_injection(*, content: str) -> None:
    lowered = content.lower()

    for keyword in BLOCKED_PROMPT_KEYWORDS:
        if keyword.lower() in lowered:
            raise ValidationError("해당 요청은 처리할 수 없습니다.")


def _validate_support_domain(*, session: ChatbotSession, content: str) -> None:
    if not _is_support_session(session=session):
        return

    lowered = content.lower()

    for keyword in BLOCKED_SUPPORT_KEYWORDS:
        if keyword.lower() in lowered:
            raise ValidationError("support 채팅에서는 서비스 이용 관련 문의만 가능합니다.")
