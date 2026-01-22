from typing import Any

from rest_framework import serializers

from apps.qna.models import Question


class ChatbotActivateSerializer(serializers.Serializer[Any]):
    question_id = serializers.IntegerField()

    def validate_question_id(self, value: int) -> int:
        if not Question.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 질문입니다.")
        return value
