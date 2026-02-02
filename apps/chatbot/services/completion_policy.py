from rest_framework.exceptions import ValidationError

from apps.chatbot.models.chatbot_session import ChatbotSession


def validate_user_prompt_policy(
    *,
    session: ChatbotSession,
) -> None:
    """
    USER 추가 질문 가능 여부 검증 (Policy Layer)

    - 현재는 정책 미적용 (골격)
    - 추후 정책 예시:
      * ASSISTANT 응답 중 질문 차단
      * 질문 빈도/횟수 제한
    - 위반 시 DRF ValidationError 발생 (400 Bad Request)
    """
    # TODO:
    # ASSISTANT 응답 중 질문 차단

    return None
