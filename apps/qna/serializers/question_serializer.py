from typing import Any, cast

from rest_framework import serializers

from apps.qna.models import Question
from apps.qna.serializers.question_base import QnAVersionedValidationMixin


class QuestionCreateSerializer(QnAVersionedValidationMixin, serializers.ModelSerializer[Question]):
    category_id = serializers.IntegerField(required=True, help_text="카테고리 ID (소분류)")

    class Meta:
        model = Question
        fields = ["title", "content", "category_id"]


class QuestionCreateResponseSerializer(QnAVersionedValidationMixin, serializers.Serializer[Any]):
    message = serializers.CharField(default="질문이 성공적으로 등록되었습니다.")
    question_id = serializers.IntegerField(source="id")
