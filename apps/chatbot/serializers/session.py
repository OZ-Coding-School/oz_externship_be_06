from typing import Any

from rest_framework import serializers

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.qna.models import Question


class ChatbotSessionCreateSerializer(serializers.Serializer[Any]):
    """
    챗봇 세션 생성용 Serializer
    """

    question = serializers.IntegerField(min_value=1)
    title = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    using_model = serializers.CharField(
        required=False,
        max_length=50,
    )

    def validate_question(self, value: int) -> int:
        if not Question.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 질문입니다.")
        return value

    def validate_using_model(self, value: str) -> str:
        valid_choices = ChatbotSession.AIModel.values
        choice_map = {choice.lower(): choice for choice in valid_choices}

        normalized_input = value.lower()

        if normalized_input not in choice_map:
            allowed = ", ".join(valid_choices)
            raise serializers.ValidationError(f"지원하지 않는 모델입니다. (가능한 모델: {allowed})")

        return choice_map[normalized_input]


class ChatbotSessionSerializer(serializers.ModelSerializer[Any]):
    """
    챗봇 세션 응답 Serializer
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
