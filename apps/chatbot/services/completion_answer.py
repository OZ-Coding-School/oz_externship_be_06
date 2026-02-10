from __future__ import annotations

from typing import Any, Dict, Iterator, List, cast

from django.conf import settings
from django.core.exceptions import ValidationError
from google import genai

from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession


def _get_genai_client() -> genai.Client:
    api_key = getattr(settings, "GEMINI_API_KEY", None)
    if not api_key:
        raise ValidationError("Gemini API 키가 설정되지 않았습니다.")

    return genai.Client(api_key=api_key)


def _resolve_model_name(*, session: ChatbotSession) -> str:
    raw_model = session.using_model.lower() if session.using_model else "gemini"

    if "gpt" in raw_model:
        return "gpt-4o"

    return "gemini-2.0-flash"


def _build_chat_history(
    *,
    session: ChatbotSession,
    system_prompt: str,
) -> List[Dict[str, Any]]:
    history_objs = ChatbotCompletions.objects.filter(session=session).order_by("created_at")

    chat_history: List[Dict[str, Any]] = [
        {
            "role": "user",
            "parts": [system_prompt],
        },
        {
            "role": "model",
            "parts": ["네, 알겠습니다."],
        },
    ]

    for h in history_objs:
        role = "user" if h.role == ChatbotCompletions.Role.USER else "model"
        chat_history.append(
            {
                "role": role,
                "parts": [h.content],
            }
        )

    return chat_history


def generate_completion_answer(
    *,
    session: ChatbotSession,
    system_prompt: str,
) -> Iterator[str]:
    client = _get_genai_client()
    model_name = _resolve_model_name(session=session)
    chat_history = _build_chat_history(session=session, system_prompt=system_prompt)

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
