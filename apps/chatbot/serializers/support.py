from typing import Any

from rest_framework import serializers

from apps.chatbot.models.chatbot_session import ChatbotSession


class ChatbotSupportSessionCreateSerializer(serializers.Serializer[Any]):
    title = serializers.CharField(
        max_length=30,
        allow_blank=False,
    )
    using_model = serializers.ChoiceField(
        choices=ChatbotSession.AIModel.choices,
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if "question" in self.initial_data:
            raise serializers.ValidationError({"question": "서포트 세션에서는 question을 사용할 수 없습니다."})
        return attrs
