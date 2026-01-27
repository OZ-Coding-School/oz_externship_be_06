from rest_framework import serializers

from apps.qna.models import Question
from apps.qna.serializers.base import QnAVersionedValidationMixin


class QuestionCreateSerializer(QnAVersionedValidationMixin, serializers.ModelSerializer[Question]):
    """
    질문 등록 시리얼라이저
    """

    category_id = serializers.IntegerField(required=True, help_text="카테고리 ID (소분류)")

    class Meta:
        model = Question
        fields = ["title", "content", "category_id"]
