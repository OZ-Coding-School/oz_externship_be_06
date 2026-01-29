from typing import Any

from rest_framework import serializers

from apps.chatbot.models.chatbot_session import ChatbotSession


class ChatbotSupportSessionCreateSerializer(serializers.Serializer[Any]):
    title = serializers.CharField(max_length=100)
    using_model = serializers.ChoiceField(choices=ChatbotSession.AIModel.choices)
