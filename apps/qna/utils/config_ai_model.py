import logging
import os
import google.generativeai as genai

logger = logging.getLogger("django")


class AIModelConfig:
    """
    AI 모델 설정 및 매핑 상수
    - using_model: DB에 저장되는 모델 타입 (Gemini, GPT)
    - model_name: 실제 API 호출에 사용되는 세부 모델명
    """

    # 모델 타입 → 세부 모델명 매핑
    MODEL_NAME_MAP: dict[str, str] = {
        "Gemini": "gemini-2.0-flash",
        "GPT": "gpt-4o",
    }

    # 기본 모델 타입
    DEFAULT_MODEL_TYPE = "Gemini"

    # API 요청 타임아웃 (초)
    REQUEST_TIMEOUT = 30

    _is_gemini_configured = False

    @classmethod
    def ensure_gemini_configured(cls) -> None:
        """Gemini API 설정 초기화"""
        if cls._is_gemini_configured:
            return

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
            raise ValueError("AI 서비스 설정이 올바르지 않습니다.")

        genai.configure(api_key=api_key)
        cls._is_gemini_configured = True

    @classmethod
    def get_model_name(cls, model_type: str) -> str:
        """
        모델 타입에 해당하는 세부 모델명을 반환합니다.

        Args:
            model_type: 모델 타입 (Gemini 또는 GPT)

        Returns:
            str: 세부 모델명 (gemini-2.0-flash 또는 gpt-4o)

        Raises:
            ValueError: 지원하지 않는 모델 타입인 경우
        """
        if model_type not in cls.MODEL_NAME_MAP:
            raise ValueError(f"지원하지 않는 AI 모델입니다: {model_type}")
        return cls.MODEL_NAME_MAP[model_type]
