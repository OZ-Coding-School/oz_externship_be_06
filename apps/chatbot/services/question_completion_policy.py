import re
from datetime import timedelta

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession

# ==============================
# 정책 상수 (Question 전용)
# ==============================

QUESTION_SESSION_TTL = timedelta(hours=3)

MAX_INPUT_LENGTH = 1000

# 탈옥 / 시스템·정책 노출 / 모델 노출 / 내부정보 요청 차단
BLOCKED_PROMPT_KEYWORDS = [
    # 시스템/프롬프트 노출
    "시스템 프롬프트",
    "system prompt",
    "developer message",
    "hidden prompt",
    "prompt reveal",
    "프롬프트 보여줘",
    "프롬프트 공개",
    "너의 지침",
    "너의 규칙",
    "규칙을 보여줘",
    "정책을 보여줘",
    "policy",
    "content policy",
    # 지시 무시/역할 변경
    "지시를 무시",
    "이전 지시 무시",
    "ignore instructions",
    "disregard",
    "override",
    "역할을 바꿔",
    "roleplay",
    "act as",
    "너는 이제",
    # 탈옥 키워드
    "탈옥",
    "jailbreak",
    "prompt injection",
    "dan",
    # 내부 설정/파라미터/키
    "temperature",
    "top_p",
    "system message",
    "api key",
    "secret key",
    "키를 알려줘",
    "토큰",
    # 모델명/벤더 노출 유도
    "모델 뭐야",
    "사용하는 모델",
    "gpt",
    "gemini",
    "claude",
    "llama",
    "openai",
]

# 소설/창작/번역/요약 등 질문하기 도메인 외 (학습 QnA 중심 유지)
BLOCKED_NONQUESTION_KEYWORDS = [
    "소설",
    "시나리오",
    "대본",
    "웹소설",
    "스토리",
    "창작해줘",
    "시 써줘",
    "가사 써줘",
    "번역해줘",
    "번역해줘요",
    "요약해줘",
    "요약해줘요",
    "광고 문구",
    "마케팅 문구",
    "홍보 글",
]

# “완성형 프로그램/서비스 제작” 요청 차단 (예제/부분 코드는 허용)
BLOCKED_BUILD_REQUEST_KEYWORDS = [
    "프로그램 만들어줘",
    "앱 만들어줘",
    "웹 만들어줘",
    "서비스 만들어줘",
    "완성해줘",
    "전체 코드",
    "풀코드",
    "통파일로",
    "프로젝트 통째로",
    "배포까지",
    "운영 가능한",
]

# 고객지원(support) 성격 키워드 (질문하기에서 처리하지 않음)
BLOCKED_SUPPORT_LIKE_KEYWORDS = [
    "출결",
    "결석",
    "지각",
    "출석",
    "과제",
    "제출",
    "계정",
    "로그인",
    "비밀번호",
    "수강 신청",
    "수강신청",
    "결제",
    "환불",
    "운영",
    "관리자",
    "정책",
    "문의",
]

# 공백/기호 섞어서 우회하는 입력 대응용 정규화
_NORMALIZE_RE = re.compile(r"[\s\W_]+", re.UNICODE)


# ==============================
# Policy Entry Point
# ==============================


def validate_user_prompt_policy(
    *,
    session: ChatbotSession,
    content: str,
) -> None:
    """
    질문하기 챗봇 USER 입력 정책 검증

    정책 요약:
    - 질문(question_id) 기반 세션 전용
    - 마지막 USER 질문 기준 3시간 TTL
    - ASSISTANT 응답 중 추가 질문 차단
    - 프롬프트 탈옥/모델 노출/내부정보 요청 차단
    - 고객지원(support) 성격 문의 차단 (support로 유도)
    - 창작/요약/번역 등 질문하기 목적 외 요청 차단
    - 완성형 프로그램/서비스 제작 요청 차단 (예제/부분 코드는 허용)
    """

    _validate_question_session(session=session)
    _validate_question_session_alive(session=session)
    _validate_not_during_assistant_response(session=session)
    _validate_input_content(content=content)
    _validate_prompt_injection(content=content)
    _validate_question_domain(content=content)

    return None


# ==============================
# 세부 정책 함수
# ==============================


def _is_question_session(*, session: ChatbotSession) -> bool:
    return session.question_id is not None


def _validate_question_session(*, session: ChatbotSession) -> None:
    if not _is_question_session(session=session):
        raise ValidationError("질문하기 세션이 아닙니다.")


def _validate_question_session_alive(*, session: ChatbotSession) -> None:
    last_user_completion = (
        ChatbotCompletions.objects.filter(session=session, role=ChatbotCompletions.Role.USER)
        .order_by("-created_at")
        .first()
    )

    if not last_user_completion:
        return

    if last_user_completion.created_at + QUESTION_SESSION_TTL < timezone.now():
        raise ValidationError("이전 대화가 만료되었습니다. 새로 질문해 주세요.")


def _validate_not_during_assistant_response(*, session: ChatbotSession) -> None:
    last_completion = ChatbotCompletions.objects.filter(session=session).order_by("-created_at").first()

    if not last_completion:
        return

    if last_completion.role == ChatbotCompletions.Role.USER:
        raise ValidationError("AI 응답이 완료된 후 다시 질문해 주세요.")


def _validate_input_content(*, content: str) -> None:
    if not content or not content.strip():
        raise ValidationError("질문 내용을 입력해 주세요.")

    if len(content) > MAX_INPUT_LENGTH:
        raise ValidationError("질문은 최대 1000자까지 입력할 수 있습니다.")


def _normalize_text(*, content: str) -> str:
    lowered = content.lower()
    return _NORMALIZE_RE.sub("", lowered)


def _validate_prompt_injection(*, content: str) -> None:
    raw_lower = content.lower()
    normalized = _normalize_text(content=content)

    for keyword in BLOCKED_PROMPT_KEYWORDS:
        k1 = keyword.lower()
        k2 = _NORMALIZE_RE.sub("", k1)
        if k1 in raw_lower or (k2 and k2 in normalized):
            raise ValidationError("해당 요청은 처리할 수 없습니다.")


def _validate_question_domain(*, content: str) -> None:
    raw_lower = content.lower()
    normalized = _normalize_text(content=content)

    for keyword in BLOCKED_SUPPORT_LIKE_KEYWORDS:
        k1 = keyword.lower()
        k2 = _NORMALIZE_RE.sub("", k1)
        if k1 in raw_lower or (k2 and k2 in normalized):
            raise ValidationError("해당 문의는 고객지원 챗봇을 통해 안내받을 수 있습니다.")

    for keyword in BLOCKED_NONQUESTION_KEYWORDS:
        k1 = keyword.lower()
        k2 = _NORMALIZE_RE.sub("", k1)
        if k1 in raw_lower or (k2 and k2 in normalized):
            raise ValidationError("질문하기에서는 학습 질문에 대해서만 답변할 수 있습니다.")

    for keyword in BLOCKED_BUILD_REQUEST_KEYWORDS:
        k1 = keyword.lower()
        k2 = _NORMALIZE_RE.sub("", k1)
        if k1 in raw_lower or (k2 and k2 in normalized):
            raise ValidationError("질문하기에서는 완성형 제작 요청이 아니라 학습 질문 위주로 도와드릴 수 있습니다.")
