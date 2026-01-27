from rest_framework import serializers

from apps.qna.models import Question, QuestionCategory
from apps.qna.serializers.base import QnaValidationMixin


class QuestionCreateSerializer(QnaValidationMixin, serializers.ModelSerializer[Question]):
    """
    질문 등록 시리얼라이저
    """

    category_id = serializers.IntegerField(required=True, help_text="카테고리 ID (소분류)")
    default_error_message = "유효하지 않은 질문 등록 요청입니다."

    def validate_category_id(self, value: int) -> int:
        if not QuestionCategory.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 카테고리입니다.")
        return value

    class Meta:
        model = Question
        fields = ["title", "content", "category_id"]
