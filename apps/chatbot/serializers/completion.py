from rest_framework import serializers


class ChatbotCompletionCreateSerializer(serializers.Serializer):  # type: ignore[type-arg]
    message = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=1000,
        error_messages={
            "required": "이 필드는 필수 항목입니다.",
            "blank": "이 필드는 blank일 수 없습니다.",
        },
    )
