from typing import Any

from rest_framework import serializers

from apps.chatbot.models.chatbot_session import ChatbotSession


class ChatbotSessionSerializer(serializers.ModelSerializer[Any]):
    class Meta:
        model = ChatbotSession
        fields = [
            "id",
            "user",
            "question",
            "title",
            "using_model",
            "status",
            "created_at",
            "updated_at",
        ]
