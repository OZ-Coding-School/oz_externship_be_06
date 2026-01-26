from typing import Any

from rest_framework import serializers

from apps.chatbot.models.chatbot_session import ChatbotSession


class ChatbotSessionSerializer(serializers.ModelSerializer[Any]):
    """
    챗봇 세션 조회/응답용 Serializer
    """

    class Meta:
        model = ChatbotSession
        fields = [
            "id",
            "user",
            "question",
            "title",
            "using_model",
            "created_at",
            "updated_at",
        ]


class ChatbotSessionCreateSerializer(serializers.Serializer[Any]):
    """
    챗봇 세션 생성용 Serializer
    """

    question_id = serializers.IntegerField(min_value=1)
    title = serializers.CharField(
        max_length=255,
        required=False,
    )
    using_model = serializers.CharField(
        required=False,
        max_length=50,
    )

    def validate_using_model(self, value: str) -> str:
        """
        using_model 값 정규화 및 검증
        - 대소문자 혼용 방지
        """
        normalized = value.lower()

        allowed_models = {
            "gemini",
            "gemini-2.5-flash",
        }

        if normalized not in allowed_models:
            raise serializers.ValidationError("지원하지 않는 모델입니다.")

        return normalized
