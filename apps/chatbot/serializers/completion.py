from typing import Any

from rest_framework import serializers

from apps.chatbot.models.chatbot_completions import ChatbotCompletions


class ChatbotCompletionCreateSerializer(serializers.Serializer[Any]):
    message = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=1000,
        error_messages={
            "required": "이 필드는 필수 항목입니다.",
            "blank": "이 필드는 공란일 수 없습니다.",
        },
    )


class ChatbotCompletionListSerializer(serializers.ModelSerializer[ChatbotCompletions]):
    message = serializers.CharField(source="content")

    class Meta:
        model = ChatbotCompletions
        fields = ["id", "message", "role", "created_at"]
