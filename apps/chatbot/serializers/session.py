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
        allow_blank=True,
    )
    using_model = serializers.CharField(
        required=False,
        max_length=50,
    )
