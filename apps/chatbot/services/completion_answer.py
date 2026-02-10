from __future__ import annotations

from typing import Any, Dict, Iterator, List, cast

from django.conf import settings
from django.core.exceptions import ValidationError
from google import genai

from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession


def generate_completion_answer(
    *,
    session: ChatbotSession,
    system_prompt: str,
) -> Iterator[str]:
    api_key = getattr(settings, "GEMINI_API_KEY", None)
    if not api_key:
        raise ValidationError("Gemini API 키가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)

    # 모델명 정규화 및 매핑 (GEMINI, gemini-2.5-flash 등 예외 처리)
    raw_model = session.using_model.lower() if session.using_model else "gemini"

    if "gpt" in raw_model:
        model_name = "gpt-4o"
    else:
        # 안정성을 위해 gemini-2.0-flash로 고정
        model_name = "gemini-2.0-flash"

    # 대화 기록 조회
    history_objs = ChatbotCompletions.objects.filter(session=session).order_by("created_at")
    chat_history: List[Dict[str, Any]] = []

    # 시스템 프롬프트 주입 (오케스트레이션 레이어에서 결정됨)
    chat_history.append(
        {
            "role": "user",
            "parts": [system_prompt],
        }
    )
    chat_history.append(
        {
            "role": "model",
            "parts": ["네, 알겠습니다."],
        }
    )

    # 기존 대화 히스토리 주입
    for h in history_objs:
        role = "user" if h.role == ChatbotCompletions.Role.USER else "model"
        chat_history.append(
            {
                "role": role,
                "parts": [h.content],
            }
        )

    # 스트리밍 요청
    try:
        response = client.models.generate_content_stream(
            model=model_name,
            contents=cast(Any, chat_history),
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text

    except Exception as exc:
        print(f"Gemini API Error: {exc}")
        raise ValidationError("AI 응답 생성에 실패했습니다.") from exc
