from rest_framework.exceptions import ValidationError

from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession

# ==============================
# 정책 상수 (Support 전용)
# ==============================

# 프롬프트 탈옥 / 시스템·모델 정보 요청 차단 키워드
BLOCKED_PROMPT_KEYWORDS = [
    # 시스템 / 프롬프트 탈옥
    "시스템 프롬프트",
    "system prompt",
    "프롬프트 보여줘",
    "지시를 무시",
    "이전 지시 무시",
    "역할을 바꿔",
    "너의 규칙",
    # 모델 노출
    "너는 gpt",
    "너 gpt야",
    "너는 gemini",
    "너 gemini야",
    "사용하는 모델",
    "모델 뭐야",
]

# support 도메인 외 요청 차단 키워드
BLOCKED_SUPPORT_KEYWORDS = [
    "코드 짜줘",
    "프로그램 만들어줘",
    "소설 써줘",
    "번역해줘",
    "요약해줘",
]


# ==============================
# Policy Entry Point
# ==============================


def validate_user_prompt_policy(
    *,
    session: ChatbotSession,
    content: str,
) -> None:
    """
    Support 챗봇 USER 입력 정책 검증

    정책 요약:
    - support 챗봇 전용
    - 대화창 닫힘(is_closed=True) 즉시 차단
    - ASSISTANT 응답 중 추가 질문 차단
    - 프롬프트 탈옥 시도 차단
    - 고객지원 도메인 외 요청 차단

    ※ 질문하기 챗봇 정책은 포함하지 않는다.
    """

    _validate_support_session_alive(session=session)
    _validate_not_during_assistant_response(session=session)
    _validate_input_content(content=content)
    _validate_prompt_injection(content=content)
    _validate_support_domain(session=session, content=content)

    return None


# ==============================
# 세부 정책 함수
# ==============================


def _is_support_session(*, session: ChatbotSession) -> bool:
    """
    support 세션 여부 판단

    - POST /chatbot/support 로 생성
    - GEMINI 모델 사용 세션을 support 로 간주
    """
    return session.using_model == ChatbotSession.AIModel.GEMINI


def _validate_support_session_alive(*, session: ChatbotSession) -> None:
    """
    support 세션 종료 여부 검증

    - 사용자가 대화창을 닫은 경우(is_closed=True)
      → 즉시 차단
    """
    if not _is_support_session(session=session):
        return

    if hasattr(session, "is_closed") and session.is_closed:
        raise ValidationError("이미 종료된 support 대화입니다.")


def _validate_not_during_assistant_response(*, session: ChatbotSession) -> None:
    """
    ASSISTANT 응답 중 USER 질문 차단

    정책 기준:
    - 마지막 메시지가 USER → AI 응답 진행 중
    - 마지막 메시지가 ASSISTANT → 질문 가능
    """

    last_completion = ChatbotCompletions.objects.filter(session=session).order_by("-created_at").first()

    if not last_completion:
        return

    if last_completion.role == ChatbotCompletions.Role.USER:
        raise ValidationError("AI 응답이 완료된 후 다시 질문해 주세요.")


def _validate_input_content(*, content: str) -> None:
    """
    질문 내용 기본 검증
    """
    if not content or not content.strip():
        raise ValidationError("질문 내용을 입력해 주세요.")

    if len(content) > 1000:
        raise ValidationError("질문이 너무 깁니다. 내용을 줄여 주세요.")


def _validate_prompt_injection(*, content: str) -> None:
    """
    프롬프트 탈옥 / 시스템·모델 정보 요청 차단
    """
    lowered = content.lower()

    for keyword in BLOCKED_PROMPT_KEYWORDS:
        if keyword.lower() in lowered:
            raise ValidationError("해당 요청은 처리할 수 없습니다.")


def _validate_support_domain(*, session: ChatbotSession, content: str) -> None:
    """
    support 챗봇 도메인 제약

    - 고객지원 목적 외 요청 차단
    """
    if not _is_support_session(session=session):
        return

    lowered = content.lower()

    for keyword in BLOCKED_SUPPORT_KEYWORDS:
        if keyword.lower() in lowered:
            raise ValidationError("support 채팅에서는 서비스 이용 관련 문의만 가능합니다.")
