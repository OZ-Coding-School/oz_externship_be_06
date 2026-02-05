from __future__ import annotations

from typing import Any, Dict, Iterator, List, cast

import google.generativeai as _genai
from django.conf import settings
from django.core.exceptions import ValidationError
from google.generativeai.types import GenerationConfig

from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession

genai = cast(Any, _genai)


def generate_completion_answer(*, session: ChatbotSession, user_message: str) -> Iterator[str]:
    api_key = getattr(settings, "GEMINI_API_KEY", None)
    if not api_key:
        raise ValidationError("Gemini API 키가 설정되지 않았습니다.")

    genai.configure(api_key=api_key)

    # 모델명 정규화 및 매핑 (GEMINI, gemini-2.5-flash 등 예외 처리)
    raw_model = session.using_model.lower() if session.using_model else "gemini"

    if "gpt" in raw_model:
        model_name = "gpt-4o"
    else:
        # 안정성을 위해 gemini-pro로 고정
        model_name = "gemini-2.0-flash"

    # 모델 초기화
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=GenerationConfig(
            temperature=0.7,
            max_output_tokens=1024,
        ),
    )

    # 대화 기록 조회
    history_objs = ChatbotCompletions.objects.filter(session=session).order_by("created_at")
    chat_history: List[Dict[str, Any]] = []

    # 시스템 프롬프트 설정
    system_text = "당신은 오즈 익스턴십 LMS의 서포트 챗봇입니다. 친절하게 답변하세요."
    if session.question_id and session.question:
        system_text = f"다음 질문에 대해 정확하고 간결하게 답변하세요:\n{session.question.content}"

    # 히스토리 주입 (구버전 호환성 확보)
    if not history_objs.exists():
        chat_history.append({"role": "user", "parts": [system_text]})
        chat_history.append({"role": "model", "parts": ["네, 알겠습니다."]})

    for h in history_objs:
        role = "user" if h.role == ChatbotCompletions.Role.USER else "model"
        chat_history.append({"role": role, "parts": [h.content]})

    # 스트리밍 요청
    chat = model.start_chat(history=chat_history)

    try:
        response = chat.send_message(user_message, stream=True)

        for chunk in response:
            if chunk.text:
                yield chunk.text

    except Exception as exc:
        print(f"Gemini API Error: {exc}")
        raise ValidationError("AI 응답 생성에 실패했습니다.") from exc
